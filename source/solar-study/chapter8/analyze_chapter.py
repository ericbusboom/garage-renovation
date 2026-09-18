"""Chapter 8 extension. Reuses the prior dispatch definitions with isolated outputs."""
from pathlib import Path
import json, math, hashlib
ROOT=Path(__file__).resolve().parents[2]
WORK=Path(__file__).resolve().parent
OUT=WORK/'results'; OUT.mkdir(parents=True,exist_ok=True)
old=ROOT/'solar-study/optimization/analyze.py'
source=old.read_text().split('rows=[];runs={}')[0]
source=source.replace("OUT=D/'results'", "OUT=pathlib.Path("+repr(str(OUT))+ ")")
scope={'__file__':str(old)}
exec(compile(source,str(old),'exec'),scope)
np=scope['np']; pd=scope['pd']
for a in [35,40]: scope['pv'][a]=scope['hourly_pv'](a)
angles=[]; monthly=[]; geom=[]; systems=[]; audit=[]
W=281.5/12; L=325/W; run30=L*math.cos(math.radians(30)); depth=249/12; floor=9+8/12; cap=floor+8
for a in [30,35,40]:
    v=scope['pvs'][a]
    angles.append(dict(tilt=a,annual_per_kw=v.sum(),winter_DJF_per_kw=v[[11,0,1]].sum(),summer_JJA_per_kw=v[[5,6,7]].sum(),july_per_kw=v[6],august_per_kw=v[7],kw_for_1200_august=1200/v[7],kw_for_average_1kw=8760/v.sum()))
    for m in range(12): monthly.append(dict(month=m+1,tilt=a,kwh_per_kw=v[m],six_kw_kwh=6*v[m],modeled_load_kwh=scope['loadnormal'][m]))
    for mode in ['fixed_325_sqft','fixed_plan_run']:
        rad=math.radians(a); run=L*math.cos(rad) if mode=='fixed_325_sqft' else run30
        area=W*run/math.cos(rad); rise=run*math.tan(rad); end=run-63/12
        sixstart=(floor+6-9)/math.tan(rad)-63/12
        eightstart=(floor+8-9)/math.tan(rad)-63/12
        # The cap envelope reaches 8 ft at its front; roof build-up not yet deducted.
        sixstart=min(sixstart,end); eightstart=min(eightstart,end)
        geom.append(dict(mode=mode,tilt=a,width_ft=W,solar_area_sqft=area,plan_run_ft=run,rise_ft=rise,slope_top_ft=9+rise,clerestory_inches=(cap-9-rise)*12,cap_depth_within_walls_ft=depth-end,cap_area_sqft=W*(depth-end),cap_area_to_roof_edge_sqft=W*(253/12-end),envelope_6ft_area_sqft=W*(depth-max(0,sixstart)),envelope_8ft_area_sqft=W*(depth-max(0,eightstart)),capacity_22pct_90pct_kw=area*.09290304*.22*.90))
    for k,b in [(4,0),(5,0),(6,0),(5,13.5),(5.64,13.5),(6,13.5),(6.5,13.5),(7,13.5),(8,13.5),(6,27)]:
        r=scope['dispatch'](k,b,a); bill=scope['bill'](r); fin=scope['finance'](k,b,scope['nosolar']-bill)
        residual=r['pv'].sum()+r['imports'].sum()-r['load'].sum()-r['exports'].sum()-r['charge'].sum()+r['discharge'].sum()
        assert abs(residual)<1e-5
        systems.append(dict(tilt=a,solar_kw=k,battery_kwh=b,annual_pv_kwh=r['pv'].sum(),imports_kwh=r['imports'].sum(),exports_kwh=r['exports'].sum(),battery_discharge_kwh=r['discharge'].sum(),annual_bill=bill,first_year_saving=scope['nosolar']-bill,**fin))
        audit.append(dict(tilt=a,solar_kw=k,battery_kwh=b,energy_residual_kwh=residual))
        if k==6 and b==13.5:
            pd.DataFrame(r,index=scope['idx']).to_csv(OUT/f'hourly-6kw-{a}deg.csv.gz',index_label='local_time')
    print('Completed tilt',a,flush=True)
for name,rows in [('angle-comparison',angles),('monthly-angle-production',monthly),('roof-geometry',geom),('system-comparison',systems),('energy-balance-checks',audit)]:
    pd.DataFrame(rows).to_csv(OUT/(name+'.csv'),index=False)
(OUT/'summary.json').write_text(json.dumps({'angles':angles,'geometry':geom,'baseline_bill':scope['nosolar'],'annual_load':float(scope['loadnormal'].sum()),'legacy_engine_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'maximum_balance_residual_kwh':max(abs(x['energy_residual_kwh']) for x in audit)},indent=2))
print(json.dumps(angles,indent=2))
