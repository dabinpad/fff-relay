#!/usr/bin/env python3
"""FFF 2026-2027 scenarios: per-Red OPTIMISED Blue lineups + a 'Random' (naive similar-pace)
scenario for BOTH teams. 10 sub-teams → points [11,9,8,...,2,0]. Verifies the naive
construction reproduces the user's example trios (Oyster+GoG+AK ; DB+Penny+Apoon)."""
import itertools
from fractions import Fraction as F

def t(mmss): m,s=mmss.split(':'); return (int(m)*60+int(s))*5
OUR={'TT':'4:05','WL':'4:15','Cai':'4:30','CM':'4:45','CP':'4:50','9J':'5:00',
     'LW':'5:45','DB':'5:45','SLK':'5:45','Penny':'5:45','Apoon':'6:00'}
RED={'LC':'4:15','SIN':'4:15','Sandro':'4:15','FL':'4:20','KTY':'4:45','LP':'5:12',
     'LS':'5:15','Oyster':'5:20','5K':'5:25','GoG':'5:45','AK':'6:45'}
OUR={k:t(v) for k,v in OUR.items()}; RED={k:t(v) for k,v in RED.items()}
PTS=[11,9,8,7,6,5,4,3,2,0]

def pair_t(a,b,R): return F(R[a]+R[b])
def trio_t(tri,R): ms=sorted(tri,key=lambda x:R[x]); return F(R[ms[0]])+F(R[ms[1]]+R[ms[2]],2)
def make(lineup,R,side):
    out=[]
    for g in lineup:
        if len(g)==2: out.append((pair_t(g[0],g[1],R),'pair',side,tuple(g)))
        else: out.append((trio_t(g,R),'trio',side,tuple(g)))
    return out
def score(our_teams,red_teams):
    rows=sorted(our_teams+red_teams,key=lambda r:r[0]); n=len(rows); raw=[None]*n; i=0
    while i<n:
        j=i
        while j<n and rows[j][0]==rows[i][0]: j+=1
        grp=[PTS[k] if k<len(PTS) else 0 for k in range(i,j)]; avg=F(sum(grp),j-i)
        for k in range(i,j): raw[k]=avg
        i=j
    op=rp=ot=rt=F(0)
    for idx,r in enumerate(rows):
        if r[2]=='our': op+=raw[idx]; ot+=r[0]
        else: rp+=raw[idx]; rt+=r[0]
    win='our' if (op>rp or (op==rp and ot<rt)) else ('opp' if (rp>op or (rp==op and rt<ot)) else 'tie')
    return op,rp,ot,rt,win
def matchings(items):
    items=list(items)
    if not items: yield []; return
    a=items[0]
    for i in range(1,len(items)):
        b=items[i]; rem=items[1:i]+items[i+1:]
        for m in matchings(rem): yield [(a,b)]+m
def partitions(R):
    names=list(R.keys())
    for tri in itertools.combinations(names,3):
        rest=[x for x in names if x not in tri]
        for pm in matchings(rest): yield [list(tri)]+[list(p) for p in pm]
def best_response(red_teams,R_my):
    best=None
    for part in partitions(R_my):
        ours=make(part,R_my,'our')
        op,rp,ot,rt,win=score(ours,red_teams)
        key=(op-rp,-ot)
        if best is None or key>best[0]: best=(key,part,(op,rp,win))
    return best
def fmt(x): x=float(x); return str(int(x)) if x==int(x) else f"{x:.1f}"
def show(part,R):
    out=[]
    for g in part:
        if len(g)==3: ms=sorted(g,key=lambda x:R[x]); out.append(f"({ms[0]}*+{ms[1]}+{ms[2]})trio")
        else: out.append('+'.join(g))
    return ' · '.join(out)

# ---- naive 'Random' construction: sort by pace; pairs (1,2)(3,4)(5,6)(7,9); trio (8,10,11) ----
def naive(R):
    n=sorted(R, key=lambda x:R[x])   # stable: ties keep dict order
    pairs=[[n[0],n[1]],[n[2],n[3]],[n[4],n[5]],[n[6],n[8]]]
    trio=[n[7],n[9],n[10]]
    return pairs+[trio]

print("="*72); print("VERIFY naive() reproduces the user's example trios"); print("="*72)
red_rand=naive(RED); our_rand=naive(OUR)
print("  RED naive :",show(red_rand,RED))
print("  OUR naive :",show(our_rand,OUR))
red_trio=[g for g in red_rand if len(g)==3][0]; our_trio=[g for g in our_rand if len(g)==3][0]
print(f"  Red trio = {set(red_trio)} == {{Oyster,GoG,AK}} ? {set(red_trio)==set(['Oyster','GoG','AK'])}")
print(f"  Our trio = {set(our_trio)} == {{DB,Penny,Apoon}} ? {set(our_trio)==set(['DB','Penny','Apoon'])}")

print("\n"+"="*72); print("RANDOM scenario — both teams naive (similar-pace grouping)"); print("="*72)
op,rp,ot,rt,win=score(make(our_rand,OUR,'our'),make(red_rand,RED,'opp'))
print(f"  Blue {fmt(op)} : {fmt(rp)} Red   ({'BLUE WINS' if win=='our' else 'RED wins' if win=='opp' else 'TIE'})")
print(f"  OUR: {show(our_rand,OUR)}")
print(f"  RED: {show(red_rand,RED)}")

RED_LINEUPS={
 'optimal':[['LC','SIN'],['Sandro','FL'],['LP','LS'],['Oyster','5K'],['KTY','GoG','AK']],
 'balanced':[['LC','LP'],['SIN','LS'],['Sandro','Oyster'],['FL','5K'],['KTY','GoG','AK']],
 'stacked':[['LC','SIN'],['Sandro','FL'],['KTY','LP'],['LS','Oyster'],['5K','GoG','AK']],
 'spread':[['LC','GoG'],['SIN','5K'],['Sandro','Oyster'],['FL','LS'],['KTY','LP','AK']],
}
print("\n"+"="*72); print("Per-Red OPTIMISED Blue best responses (new points [11,9,...,0])"); print("="*72)
for name,red in RED_LINEUPS.items():
    redT=make(red,RED,'opp')
    bkey,part,(op,rp,win)=best_response(redT,OUR)
    print(f"\n### Red '{name}'  ->  Blue {fmt(op)} : {fmt(rp)} Red   ({'BLUE WINS' if win=='our' else 'RED wins' if win=='opp' else 'TIE'})")
    print(f"  RED:  {show(red,RED)}")
    print(f"  OUR (best response): {show(part,OUR)}")
