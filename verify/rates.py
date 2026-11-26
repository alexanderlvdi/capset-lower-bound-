#!/usr/bin/env python3
"""Exact recomputation of the node rates (eta_b, B_b), b in {144,182,183,252,641}, from the two rule tables
of Lu's Appendix C (matching.tsv, reader_rows.tsv: Lu's supplement, shipped UNMODIFIED in appendix_c_data/ and
pinned by SHA-256 below) following the formulas of Lu Sec. C.1-C.5 (integer weights with D = 2^176, exact
Fractions).  Own code; none of Lu's code is used or run.  stdlib only.
usage: python3 -I rates.py cert.json [cert2.json ...]   (exit 0 iff every node_rates entry equals the recomputation exactly)
Also importable: verify_node_rates(node_rates_dict_from_json) -> bool (prints PASS/FAIL lines)."""
import sys, csv, time, os, hashlib, json
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from itertools import combinations
from math import comb, prod
DATA=os.path.join(os.path.dirname(os.path.abspath(__file__)),'appendix_c_data')+os.sep
UNIT=2**176; CELL=2**80; SIZES=(144,182,183,252,641); MODES=('same','upper','lower')
def recs(name):
    with open(DATA+name,encoding='ascii',newline='') as f:
        yield from csv.DictReader(f,delimiter='\t')
def as_rows(mask):
    while mask:
        bit=mask&-mask; yield bit.bit_length(); mask^=bit
def table_data():
    match=defaultdict(dict)
    for r in recs('matching.tsv'):
        match[int(r['m']),int(r['width'])][int(r['mask_hex'],16)]=int(r['target'])
    readers={m:{} for m in MODES}
    for r in recs('reader_rows.tsv'):
        readers[r['mode']][(int(r['leg']),int(r['profile_mask_hex'],16))]=tuple(map(int,r['read_rows'].split(',')))
    return dict(match),readers
@cache
def gauss(a,e):
    if not a or not e: return UNIT,UNIT
    if a>e: return gauss(e,a)
    lo,hi=gauss(a-1,e); x,y=gauss(a,e-1)
    return lo+(x>>a), hi+((y+(1<<a)-1)>>a)
def omega_const(m,w,table):
    avg=Fraction()
    for p,a in table.items():
        rank=0; ch=Fraction(1)
        for bit in range(w):
            fail=Fraction(1,2**(m-rank))
            if p&(1<<bit): ch*=1-fail; rank+=1
            else: ch*=fail
        fd=a-(p&((1<<a)-1)).bit_count(); avg+=ch/2**fd
    return (1-Fraction(1,2**(m+1)))*avg
def one_zero_price(rule,eta):
    short=[0]*15; spill=[0]*8
    for mask,a in rule.items():
        rows=tuple(as_rows(mask)); i=len(rows); v=a-sum(p<a for p in rows)
        delta=sum(rows)-i*(i+1)//2+v+(7-i)*(15-i); weight=UNIT>>delta
        spill[7-i]+=weight
        if i==7:
            for length in range(max(a,rows[-1]),15): short[length]+=weight
    @cache
    def window(length):
        if length<15: return short[length]
        return sum(weight*gauss(t,length-15-t)[0]//UNIT for t,weight in enumerate(spill) if 15+t<=length)
    @cache
    def price(b,s):
        if s<7:
            fail=Fraction(2**(s+1)-1,2**b); return (eta-fail)/(1-fail)
        c,d=s-7,b-s; total=0
        for j in range((min(d,21) if c else 0)+1):
            pre=gauss(c-1,j)[0] if c else UNIT
            total+=(pre*window(7+d-j)//UNIT)>>(9*j)
        return Fraction(total*2**d,gauss(s,d)[1]*(2**d-1))
    return price
def shapes(prefix=(),displacement=0,previous=0):
    if len(prefix)==16: yield prefix,displacement; return
    slots=16-len(prefix)
    for v in range(previous,min(16,(30-displacement)//slots)+1):
        yield from shapes(prefix+(len(prefix)+1+v,),displacement+v,v)
def linear_reducer(columns):
    pivots={}
    for v in columns:
        while v and v.bit_length() in pivots: v^=pivots[v.bit_length()]
        if v: pivots[v.bit_length()]=v
    ordered=sorted(pivots,reverse=True)
    def reduce(v):
        for i in ordered:
            if v&(1<<(i-1)): v^=pivots[i]
        return v
    return len(pivots),reduce
def cell_histograms(rule,readers,maxorder):
    @cache
    def target(rows):
        anchor=rows[-8] if len(rows)>=8 else 0
        mask=sum(1<<(r-anchor-1) for r in rows[-7:] if r<=anchor+15)
        return anchor+rule[mask] if mask in rule else 0
    @cache
    def requests(rows,top):
        reqs=[]
        if top:
            for e in rows:
                q=tuple(r for r in rows if r!=e)
                possible=[r for r in q if r<e and target(tuple(t for t in q if t!=r))==r]
                if possible:
                    d,=possible; reqs.append((q,e,len(rows)-rows.index(e),len(rows)-rows.index(d)))
        else:
            for a in range(1,rows[-1]+16):
                if a in rows: continue
                q=tuple(sorted(rows+(a,))); d=target(q)
                if d>a: reqs.append((q,a,a-sum(p<a for p in rows),d-sum(p<d for p in rows)))
        return reqs
    hist={mode:Counter() for mode in MODES}; nf=Counter()
    for rows,delta in shapes():
        dual=tuple(33-p for p in range(32,0,-1) if p not in rows)
        for mode in MODES:
            legs=((rows,True),(rows,False)) if mode=='same' else ((rows,mode=='upper'),(dual,mode=='upper'))
            bits,rhs,failures={},0,[]
            for leg,(profile,top) in enumerate(legs):
                for q,r,j,h in requests(profile,top):
                    key=(leg,sum(1<<(v-1) for v in q)); rr=readers[mode][key]
                    if rr==(r,): continue
                    eq=1<<len(failures); failures.append((leg,j,h))
                    if r not in rr: rhs|=eq
                    for read in rr:
                        p,f=(r,read) if top else (read,r)
                        if p<f:
                            if leg and mode!='same': p,f=33-f,33-p
                            bits[p,f]=bits.get((p,f),0)^eq
            rank,reduce=linear_reducer(bits.values()); syndrome=reduce(rhs)
            units=[reduce(1<<i) for i in range(len(failures))]
            nf[len(failures)]+=1
            for order in range(maxorder+1):
                for indices in combinations(range(len(failures)),order):
                    residue=syndrome
                    for i in indices: residue^=units[i]
                    if residue: continue
                    names=tuple(sorted(failures[i] for i in indices))
                    hist[mode][names]+=CELL>>(delta+rank)
    return hist,nf
@cache
def bin_coefficients(spec):
    H=max(h for _,h in spec); assert len({j for j,h in spec})==len(spec)
    weights={2**H-sum(2**(H-j) for j,h in spec):1}
    for j,h in spec:
        bins=2**(h-j-1); counts=Counter()
        for v in range(bins+1):
            factor=(-1)**(bins-v)*comb(bins,v)*2**v
            for a,c in weights.items(): counts[a+v*2**(H-h)]+=factor*c
        weights={a:c for a,c in counts.items() if c}
    return H,weights
@cache
def avoid(n,spec):
    spec=tuple(sorted((j,h) for j,h in spec if h<=n))
    if not spec: return UNIT
    H,coeff=bin_coefficients(spec)
    allp=2**(H*n); good=sum(c*a**n for a,c in coeff.items()); full=prod(2**n-2**i for i in range(H))
    return max(0,(good-allp+full)*UNIT//full)
def legp(n,keys):
    """lower bound on Pr(no forbidden pair for all keys on one leg)"""
    if not keys: return UNIT
    singles=[avoid(n,((j,h),)) for j,h in keys]
    if len(keys)==1: return singles[0]
    best=max(0,sum(singles)-(len(keys)-1)*UNIT)
    best=max(best,avoid(n,tuple(keys)))
    return best
def make_mass(hist):
    @cache
    def mass(mode,dims):
        total=0
        for spec,cell in hist[mode].items():
            k0=[(j,h) for l,j,h in spec if l==0]; k1=[(j,h) for l,j,h in spec if l==1]
            p=legp(dims[0],k0)*legp(dims[1],k1)//UNIT
            total+=p*cell
        return total
    return mass
def table_prices(mass,price_one,sizes=SIZES):
    def joint(b,k):
        t=b-k
        if min(k,t)<9: return [[0,0],[0,0]]
        g=gauss(k,t)[1]
        if min(k,t)<16:
            a=comb(b,k)*(UNIT**2//g); return [[a,a],[a,a]]
        modes=[[('same',(k,t)),('upper',(k,t))],[('lower',(t,k)),('same',(t,k))]]
        return [[comb(b,k)*(mass(mode,dims)*UNIT//(CELL*g)) for mode,dims in row] for row in modes]
    for b in sizes:
        total_old=total_new=0
        for start in range(3):
            heights=range(start,b,3); states=None
            for h in heights:
                vertices=[comb(b-1,h)*int(price_one(b,s)*UNIT) for s in (h,b-1-h)]
                if states is None: states=[(0,v) for v in vertices]
                else:
                    edge=joint(b,h-1)
                    states=[max((old+edge[i][d],new+vertices[d]) for i,(old,new) in enumerate(states)) for d in (0,1)]
            old,new=max(states); total_old+=old; total_new+=new
        yield b,Fraction(total_new,UNIT*2**(b-1)),Fraction(total_old,UNIT*2**b)

PINS={'matching.tsv':'992d2411f04680aa866428c5f8817b3d23f82b048e1414ce0676acc713ba27f2','reader_rows.tsv':'72e2339aad7f04ec715a93d5dabff904c2438091a51cf76869370045af66addd'}
# Lu Table 2 (floor(1e12*eta_b), floor(1e12*B_b)) as printed in the paper
TABLE2={144:(313436531305,328092514121),182:(313436531305,328035264355),183:(313436531305,328032524173),
        252:(313436531305,327984670844),641:(313436531305,327904358794)}
_CACHE=[]
def recompute():
    if _CACHE: return _CACHE[0]
    for n,h in PINS.items():
        assert hashlib.sha256(open(DATA+n,'rb').read()).hexdigest()==h, 'appendix_c_data/'+n+' does not match its pinned SHA-256'
    tables,readers=table_data()
    assert tuple(len(tables[k]) for k in ((2,6),(3,7),(5,10),(7,15)))==(22,61,586,15828), 'matching table sizes differ from Lu C.1'
    const=omega_const(7,15,tables[7,15]); po=one_zero_price(tables[7,15],const)
    hist,nf=cell_histograms(tables[7,15],readers,2)          # at most two failed keys (Lu C.5)
    assert tuple(len(hist[m]) for m in MODES)==(671,611,645), 'bin counts differ from Lu C.5 (671, 611, 645)'
    mass=make_mass(hist)
    out={b:(eta,B) for b,eta,B in table_prices(mass,po)}
    _CACHE.append(out); return out
def verify_node_rates(nr_json, quiet=False):
    """nr_json: {'144':[eta_str,B_str],...} exact rationals from a certificate."""
    rec=recompute(); ok=True
    for b in SIZES:
        eta=Fraction(nr_json[str(b)][0]); B=Fraction(nr_json[str(b)][1])
        e,Bb=rec[b]
        c1=(eta==e and B==Bb); c2=((eta*10**12)//1,(B*10**12)//1)==TABLE2[b]
        ok=ok and c1 and c2
        if not quiet:
            print(('PASS' if c1 else 'FAIL'),'node rate b=%d: eta_b and B_b equal the exact recomputation from Lu App. C tables'%b)
            print(('PASS' if c2 else 'FAIL'),'node rate b=%d: floors %s equal Lu Table 2'%(b,TABLE2[b]),flush=True)
    return ok
if __name__=='__main__':
    ok=True
    for fn in sys.argv[1:]:
        ok=verify_node_rates(json.load(open(fn))['node_rates']) and ok
    print('RESULT','PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
