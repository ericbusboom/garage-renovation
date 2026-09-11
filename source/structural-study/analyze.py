"""Preliminary gravity screening, inches/lb/psi. Not a complete building design.
Run: MPLCONFIGDIR=/private/tmp/garage-mpl /Applications/FreeCAD.app/Contents/Resources/bin/python structural-study/analyze.py
"""
from pathlib import Path
import json, csv
import numpy as np
from scipy.linalg import solve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
OUT=Path(__file__).parent
E=29e6
SHEAR_GA=None
# Per manufacturer Nucor-Yamato structural shapes catalog: name,d,Ix,Sx,weight
STEEL=[('W8x18',8.14,61.9,15.2,18),('W8x24',7.93,82.7,20.9,24),('W8x40',8.25,146,35.5,40),('W10x33',9.73,171,35,33),('W10x39',9.92,209,42.1,39),('W10x49',9.98,272,54.6,49)]

def beam(a,b,supports,udls=(),points=(),EI=E*209,step=4):
    breaks=sorted(set([a,b,*supports,*[v for lo,hi,q in udls for v in [lo,hi]],*[p for p,f in points]]))
    x=np.array(sorted(set(v for lo,hi in zip(breaks[:-1],breaks[1:]) for v in np.linspace(lo,hi,max(2,int(np.ceil((hi-lo)/step))+1)))))
    n=len(x); K=np.zeros((2*n,2*n)); F=np.zeros(2*n); elems=[]
    for i,(lo,hi) in enumerate(zip(x[:-1],x[1:])):
        l=hi-lo; q=sum(q for aa,bb,q in udls if aa<=(lo+hi)/2<=bb)
        phi=12*EI/(SHEAR_GA*l*l) if SHEAR_GA else 0
        k=EI/(l**3*(1+phi))*np.array([[12,6*l,-12,6*l],[6*l,(4+phi)*l*l,-6*l,(2-phi)*l*l],[-12,-6*l,12,-6*l],[6*l,(2-phi)*l*l,-6*l,(4+phi)*l*l]])
        f=q*np.array([l/2,l*l/12,l/2,-l*l/12]); ix=np.arange(2*i,2*i+4)
        K[np.ix_(ix,ix)]+=k; F[ix]+=f; elems.append((ix,k,f,q,l))
    for p,f in points:F[2*np.argmin(abs(x-p))]+=f
    fixed=[2*np.argmin(abs(x-p)) for p in supports]; free=np.setdiff1d(np.arange(2*n),fixed)
    u=np.zeros(2*n);u[free]=solve(K[np.ix_(free,free)],F[free],assume_a='pos')
    reactions=-(K@u-F)[fixed]
    moments=[];shears=[]
    for ix,k,f,q,l in elems:
        end=k@u[ix]-f
        # Internal section actions with downward-positive loading.
        s=np.linspace(0,l,9); moments.extend(end[1]-end[0]*s-q*s*s/2);shears.extend(-end[0]-q*s)
    load=sum(q*(hi-lo) for lo,hi,q in udls)+sum(f for p,f in points)
    lm=sum(q*(hi-lo)*(hi+lo)/2 for lo,hi,q in udls)+sum(f*p for p,f in points)
    assert abs(sum(reactions)-load)<max(.01,abs(load)*1e-7)
    assert abs(np.dot(reactions,supports)-lm)<max(.1,abs(lm)*1e-7)
    return dict(M=max(abs(np.array(moments))),V=max(abs(np.array(shears))),delta=max(abs(u[::2])),R=dict(zip(map(str,supports),map(float,reactions))),x=x.tolist(),u=u[::2].tolist(),load=load)

def tests():
    L=240;q=10;EI=E*209
    r=beam(0,L,[0,L],[(0,L,q)],EI=EI)
    assert abs(r['M']-q*L**2/8)<.01
    assert abs(r['delta']/(5*q*L**4/(384*EI))-1)<1e-6
    r=beam(0,L,[0,L],points=[(L/2,1000)],EI=EI)
    assert abs(r['delta']/(1000*L**3/(48*EI))-1)<1e-6
    r=beam(0,120,[0,120],[(60,120,10)])
    assert abs(r['R']['0']-150)<.01 and abs(r['R']['120']-450)<.01
    r=beam(0,144,[0,120],[(120,144,10)])
    assert r['R']['0']<0
    return 'PASS: uniform beam, central point, partial loading, overhang, force/moment balance in every solve'

Y=[-21.25,69.75,185.,253.]; W=249.5
# Simply supported secondary joists/rafters in N-S direction; exact influence integrals.
def share(y0,y1,load0,load1,q):
    lo=max(y0,load0);hi=min(y1,load1)
    if hi<=lo:return 0.,0.
    right=q*((hi-y0)**2-(lo-y0)**2)/(2*(y1-y0)); return q*(hi-lo)-right,right

def tributary(start,end):
    r=np.zeros(4)
    for i in range(3):
        l,h=share(Y[i],Y[i+1],start,end,1);r[i]+=l;r[i+1]+=h
    # Short edge extensions carried by end-span joists, including opposite reaction reduction.
    if start<Y[0]:
        total=Y[0]-start;c=(start+Y[0])/2;t=(c-Y[0])/(Y[1]-Y[0]);r[0]+=total*(1-t);r[1]+=total*t
    if end>Y[-1]:
        total=end-Y[-1];c=(end+Y[-1])/2;t=(c-Y[-2])/(Y[-1]-Y[-2]);r[-2]+=total*(1-t);r[-1]+=total*t
    assert abs(sum(r)-(end-start))<1e-8
    return r
TF=tributary(72,255);TR=tributary(-23.25,271); TN=tributary(219,255); TB=tributary(177,255)
# Floor 12 psf dead, roof 15 psf dead on horizontal projected area incl upper envelope budget.
# Roof maintenance 20 psf unreduced, all cases include in full as screening envelope.

def crossloads(i,kind,case):
    z=[]
    if kind=='D':
        z=[(0,W,(12*TF[i]+15*TR[i])/144)]
        if TB[i]:z.append((-32,0,15*TB[i]/144)) # white balcony dead
    elif kind=='L':
        q=125 if case=='storage125' else 40
        z=[(0,W,q*TF[i]/144)]
        if case=='storage_bands':
            # 36-inch N/W/E bands at125, center40, no double counting corners.
            z += [(0,36,85*TF[i]/144),(W-36,W,85*TF[i]/144),(36,W-36,85*TN[i]/144)]
        if TB[i]:z.append((-32,0,60*TB[i]/144))
    else:z=[(0,W,20*TR[i]/144)]
    return [v for v in z if abs(v[2])>1e-10]

# Sequential simply seated cross members -> continuous cabinet rail -> end headers.
# West beam intersections are directly above four exterior posts.
def system(case,kind,weight=39,frames=True):
    sw=weight/12 if kind=='D' else 0
    out={};eastpoints=[];westreactions={}
    for i in (1,2):
        ud=crossloads(i,kind,case)+[(-32,W,sw)]
        pp=[(96.125,1000)] if case=='patch1000' and kind=='L' and i==2 else []
        r=beam(-32,W,[-32,224.25],ud,pp);out[f'B{i}']=r
        eastpoints.append((Y[i],r['R']['224.25']));westreactions[f'W{i}']=r['R']['-32']
    sup=[Y[0],56.,105.,154.,203.,Y[-1]] if frames else [Y[0],105.,154.,Y[-1]]
    rail=beam(Y[0],Y[-1],sup,[(Y[0],Y[-1],sw)],eastpoints);out['E-rail']=rail
    for i,name,supports in [(0,'S-header',[-32,148.5,211.5]),(3,'N-header',[-32,53.25,224.25])]:
        # Header extended to east roof/floor edge; rail at224.25 requires south seat cantilever.
        ud=crossloads(i,kind,case)+[(-32,W,sw)]
        r=beam(-32,W,supports,ud,[(224.25,rail['R'][str(Y[i])])]);out[name]=r
        for j,(p,val) in enumerate(r['R'].items()):westreactions[name+':'+p]=val
    # West longitudinal beam remains structural; intersections carry load directly into posts.
    wr=beam(Y[0],Y[-1],Y,[(Y[0],Y[-1],sw)]);out['W-rail']=wr
    out['columns']=westreactions
    return out

CAND=[]
for n,d,I,S,wt in STEEL:CAND.append(dict(name=n,d=d,I=I,S=S,E=29e6,weight=wt,Fb=50000/1.67,material='steel'))
for b in [5.25,7.]:
    for d in [9.5,11.875,14,16,18,20]:
        CAND.append(dict(name=f'LVL {b:g} x {d:g}',d=d,I=b*d**3/12,S=b*d*d/6,E=2e6,weight=b*d/144*41,Fb=2600*min(1,(12/d)**.136)*.9,material='LVL'))
SPAN={'B1':256.25,'B2':256.25,'E-rail':77.25,'S-header':180.5,'N-header':171.,'W-rail':115.25}

def main():
    global SHEAR_GA
    validation=tests(); results={}; table=[]
    for case in ['occupied40','storage_bands','storage125','patch1000']:
        SHEAR_GA=None
        D=system(case,'D');L=system(case,'L');R=system(case,'R')
        # Use directly combined load solves to retain moment/reaction signs. Superposition of displacement exact.
        results[case]={'D':D,'L':L,'R':R}
        for c in CAND:
            # All members same weight in each screening variant; sensitivities use same rail EI.
            SHEAR_GA=E*209*12/(19.2*c['d']**2) if c['material']=='LVL' else None
            dc=system(case,'D',c['weight'])
            lc=system(case,'L') if SHEAR_GA else L
            rc=system(case,'R') if SHEAR_GA else R
            for name in SPAN:
                # Scalar maxima addition conservatively envelopes differing peak locations/signs.
                m=dc[name]['M']+lc[name]['M']+rc[name]['M'];v=dc[name]['V']+lc[name]['V']+rc[name]['V']
                scale=E*209/(c['E']*c['I']);dl=lc[name]['delta']*scale;dt=(dc[name]['delta']+lc[name]['delta']+rc[name]['delta'])*scale
                creep=(1.5*(dc[name]['delta']+lc[name]['delta'])+rc[name]['delta'])*scale if c['material']=='LVL' else dt
                flex=m/(c['S']*c['Fb']); shear=1.5*v/(float(c['name'].split()[1])*c['d']*285) if c['material']=='LVL' else None
                ok=flex<=1 and dl<=SPAN[name]/360 and dt<=SPAN[name]/240 and (c['material']=='steel' or (creep<=SPAN[name]/240 and shear<=1))
                table.append(dict(case=case,member=name,candidate=c['name'],depth=c['d'],M_kipft=m/12000,V_kip=v/1000,live_deflection_in=dl,total_deflection_in=dt,wood_sustained_screen_in=creep,flexural_screen_ratio=flex,shear_screen_ratio=shear,passes_limited_screen=bool(ok)))
    SHEAR_GA=None
    results['P2_P3_only']={k:system('storage_bands',k,frames=False) for k in ['D','L','R']}
    (OUT/'results.json').write_text(json.dumps(results,indent=2));(OUT/'candidates.json').write_text(json.dumps(CAND,indent=2))
    with (OUT/'beam-options.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=table[0].keys());w.writeheader();w.writerows(table)
    notes={'validation':validation,'floor_area_sf':W*(255-72)/144,'roof_area_projected_sf':W*(271+23.25)/144,'floor_tributaries_inches':TF.tolist(),'roof_tributaries_inches':TR.tolist()}
    (OUT/'basis.json').write_text(json.dumps(notes,indent=2))
    print(notes)
    for case in ['occupied40','storage_bands','storage125','patch1000']:
        print('\n',case)
        for n in SPAN:
            steel=[r['candidate'] for r in table if r['case']==case and r['member']==n and r['candidate'].startswith('W') and r['passes_limited_screen']]
            wood=[r['candidate'] for r in table if r['case']==case and r['member']==n and r['candidate'].startswith('LVL') and r['passes_limited_screen']]
            print(n,steel,wood[:4])
    # Review figure: plan and B2 option depth/deflection comparisons.
    fig=plt.figure(figsize=(15,10),facecolor='white');ax=fig.add_subplot(121)
    ax.add_patch(Rectangle((0,0),W,249,fill=False,lw=4,edgecolor='#929ba3'))
    ax.add_patch(Rectangle((0,72),W,183,color='#dce9ee'))
    ax.add_patch(Rectangle((0,0),W,72,color='#fff2d7'))
    ax.add_patch(Rectangle((213.25,55.5),30,148,color='#dcbda4',alpha=.8))
    for y in Y:ax.plot([-32,W],[y,y],color='#305e77',lw=3)
    ax.plot([224.25]*2,[Y[0],Y[-1]],color='#9b583b',lw=4);ax.plot([-32]*2,[Y[0],Y[-1]],color='#305e77',lw=3)
    for j,y in enumerate([56,105,154,203],1):ax.plot([213.25,243.25],[y,y],color='#713d27',lw=2);ax.text(254,y,f'P{j}',va='center',fontsize=10)
    for x,y in [(-32,y) for y in Y]+[(148.5,Y[0]),(211.5,Y[0]),(53.25,Y[-1]),(224.25,Y[-1])]:ax.add_patch(Rectangle((x-2,y-2),4,4,color='black'))
    ax.text(108,34,'OPEN BELOW\nFirst 6 ft — no loft floor',ha='center',va='center',fontsize=11)
    ax.text(104,131,'LOFT FLOOR\n317 sq ft gross',ha='center',fontsize=12)
    ax.text(70,190,'B2 — 21 ft 4¼ in support span',fontsize=10,color='#305e77')
    ax.text(70,75,'B1',fontsize=11,color='#305e77');ax.text(88,270,'NORTH / GARAGE DOOR',ha='center',fontsize=10)
    ax.set(xlim=(-50,280),ylim=(-42,287),aspect='equal');ax.axis('off');ax.set_title('Support plan · roof removed',loc='left',fontsize=15)
    ax2=fig.add_subplot(222)
    picks=['W8x40','W10x39','W10x49','LVL 7 x 9.5','LVL 7 x 16','LVL 7 x 18','LVL 7 x 20']
    vals=[next(r for r in table if r['case']=='storage_bands' and r['member']=='B2' and r['candidate']==p) for p in picks]
    ax2.barh(picks,[r['total_deflection_in'] for r in vals],color=['#35657c' if p.startswith('W') else '#ab764b' for p in picks]);ax2.axvline(256.25/240,color='#b84545',ls='--',label='L/240 screen');ax2.invert_yaxis();ax2.set_xlabel('Immediate total deflection (inches)');ax2.legend(fontsize=8);ax2.set_title('B2 · heavier storage along three walls',fontsize=13)
    ax3=fig.add_subplot(224);ax3.axis('off')
    lines=['GRAVITY SCREEN — NOT A CONSTRUCTION SCHEDULE','','Floor: 12 psf dead + 40 psf live in center', 'Storage bands: 125 psf in 3-ft north/east/west strips','Roof: 15 psf dead + 20 psf maintenance, plan area','Balcony: 15 psf dead + 60 psf live','Steel beam self-weight added separately','','All exterior posts and P1–P4 credited as support sites.','Cabinet-frame capacities and foundations not established.','Roof loads require steel transfer framing to beam lines.','Steel buckling, connections, wind/seismic not checked.','LVL plots omit creep; selection screen includes it.']
    ax3.text(0,1,'\n'.join(lines),va='top',fontsize=10,linespacing=1.65)
    fig.suptitle('Garage loft · steel versus laminated-wood beam study',fontsize=20,x=.06,ha='left');fig.subplots_adjust(left=.04,right=.97,top=.91,bottom=.05,wspace=.45,hspace=.45)
    fig.savefig(OUT/'beam-comparison.png',dpi=160);fig.savefig(OUT/'beam-comparison.pdf');plt.close(fig)
if __name__=='__main__':main()
