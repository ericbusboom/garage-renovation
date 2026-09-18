"""Reproducible preliminary solar study. Cached sources; assumptions in report.md."""
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/garage-solar-mpl')
import json,calendar,pathlib
import numpy as np,pandas as pd,pvlib
from scipy.optimize import linprog
from scipy.sparse import diags,hstack,lil_matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
D=pathlib.Path(__file__).parent; DATA=D/'data'; OUT=D/'results';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.titleweight':'bold'})
months=np.arange(1,13);days=np.array([calendar.monthrange(2026,int(m))[1] for m in months]);names=[calendar.month_abbr[m] for m in months]
bills=pd.read_csv(D.parent/'bills/power-bills-2026.csv');bills['m']=pd.to_datetime(bills.month).dt.month
w=pd.DataFrame(json.load(open(DATA/'weather.json'))['daily']);w['date']=pd.to_datetime(w.time);w['year']=w.date.dt.year;w['m']=w.date.dt.month
wm=w.groupby(['year','m']).temperature_2m_mean.mean().unstack();normal=wm.loc[1991:2020].mean().values;recent=wm.loc[2016:2025].mean().values;actual=wm.loc[2026].values
base=768/28; ix=bills.m.values-1; observed=bills.usage_kwh.values
# Simple change-point y = b + m*x: monthly mean temperature above fitted cooling balance.
# February is fixed baseline, with no cooling; calendar month billing approximation.
fits=[]
for balance in np.arange(actual[1],72,.01):
 x=np.maximum(actual[ix]-balance,0)*days[ix];y=observed-base*days[ix]
 beta=max(0,np.dot(x,y)/np.dot(x,x));pred=base*days[ix]+beta*x
 fits.append((np.mean((pred-observed)**2),balance,beta))
rmse2,balance,beta=min(fits)
def monthly_load(temp,basemult=1,coolmult=1):return base*basemult*days+beta*coolmult*np.maximum(temp-balance,0)*days
loadnormal=monthly_load(normal);loadrecent=monthly_load(recent);predobs=monthly_load(np.nan_to_num(actual,nan=balance))
bills['temperature_F']=actual[ix];bills['model_kwh']=predobs[ix];bills['residual_kwh']=observed-predobs[ix];bills.to_csv(OUT/'bill-fit.csv',index=False)
bill_slope,bill_intercept=np.polyfit(observed,bills.reported_bill_usd,1)
# PVGIS direct monthly results, including cloud climatology and building mounting temperature effects.
pvs={a:np.array([r['E_m'] for r in json.load(open(DATA/f'pv-{a}.json'))['outputs']['monthly']['fixed']]) for a in range(0,46,5)}
for a in [11,12,13,14,16,17]:
 p=DATA/f'pv-{a}-az0.json'
 if p.exists():pvs[a]=np.array([r['E_m'] for r in json.load(open(p))['outputs']['monthly']['fixed']])
best=max(pvs,key=lambda a:pvs[a][7]);targetkw=1200/pvs[best][7]
area30=401.2594749;planarea=area30*np.cos(np.deg2rad(30));packing=.90;eff=.22
angle_rows=[]
for a,v in sorted(pvs.items()):
 area=planarea/np.cos(np.deg2rad(a));kw=1200/v[7]
 angle_rows.append(dict(tilt_deg=a,july_kwh_per_kw=v[6],august_kwh_per_kw=v[7],annual_kwh_per_kw=v.sum(),target_kw=kw,active_module_sqft=kw/eff/.092903,roof_sqft_at_90pct_coverage=kw/eff/.092903/packing,existing_envelope_sqft=area,capacity_kw_at_22pct_90pct=area*.092903*eff*packing))
angles=pd.DataFrame(angle_rows);angles.to_csv(OUT/'tilt-and-area.csv',index=False)
az=[]
for z in [-60,-30,0,30,60]:
 p=DATA/f'pv-15-az{z}.json' if z else DATA/'pv-15.json'
 if p.exists():
  j=json.load(open(p));v=np.array([r['E_m'] for r in j['outputs']['monthly']['fixed']]);az.append(dict(compass_azimuth=180+z,tilt=15,august_kwh_per_kw=v[7],annual_kwh_per_kw=v.sum()))
pd.DataFrame(az).to_csv(OUT/'azimuth.csv',index=False)
# Synthetic hourly weather and production shape from official PVGIS TMY.
tmy=pd.DataFrame(json.load(open(DATA/'tmy.json'))['outputs']['tmy_hourly']);tmy.index=pd.to_datetime(tmy['time(UTC)'],format='%Y%m%d:%H%M').dt.strftime('%m%d%H')
idx=pd.date_range('2026-01-01','2027-01-01',inclusive='left',freq='h',tz='America/Los_Angeles'); n=len(idx);mon=idx.month.values;hour=idx.hour.values
wx=tmy.loc[idx.tz_convert('UTC').strftime('%m%d%H')].copy();wx.index=idx
pos=pvlib.solarposition.get_solarposition(idx,32.8,-117.24)
# Isotropic diffuse used only for hourly shape; official PVGIS fixes each monthly total.
def hourly_pv(a):
 poa=pvlib.irradiance.get_total_irradiance(a,180,pos.apparent_zenith,pos.azimuth,wx['Gb(n)'],wx['G(h)'],wx['Gd(h)'])['poa_global'].clip(lower=0)
 cell=pvlib.temperature.faiman(poa,wx.T2m,wx.WS10m)
 raw=np.maximum(0,np.asarray(poa)/1000*(1-.0035*(np.asarray(cell)-25)))
 for m in months:
  mask=mon==m;raw[mask]*=pvs[a][m-1]/raw[mask].sum()
 return raw
pv={a:hourly_pv(a) for a in [best,20,30]}
def hourly_load(monthly,baseline=base,lag=2):
 temp=wx.T2m.values*1.8+32;shape=np.maximum(np.roll(temp,lag)-balance,0)+.05
 out=np.zeros(n)
 for m in months:
  mask=mon==m;fixed=baseline*days[m-1];out[mask]=fixed/mask.sum()+max(0,monthly[m-1]-fixed)*shape[mask]/shape[mask].sum()
 return out
load=hourly_load(loadnormal)
# 2026 SDG&E bundled residential EV-TOU-5. Latest rates held constant in real dollars.
exports=pd.read_csv(DATA/'exports/Current Year NBT Pricing Upload MIDAS.csv')
# SDG&E's file readme describes NBT26, but the current download contains only
# NBT00 records. Use the records actually published and preserve the rate name
# in the summary so this cannot silently masquerade as a locked vintage.
export_rate_name='NBT26' if (exports.RateName=='NBT26').any() else 'NBT00'
exports=exports[exports.RateName.eq(export_rate_name)].copy();exports['timestamp']=pd.to_datetime(exports.DateStart+' '+exports.TimeStart,utc=True,format='mixed');exports=exports[exports.timestamp.isin(idx.tz_convert('UTC'))]
exports['component']=np.where(exports.RIN.str.contains('USCA-XXSD'),'generation','delivery')
e=exports.pivot(index='timestamp',columns='component',values='Value').reindex(idx.tz_convert('UTC'));assert len(e)==8760 and not e.isna().any().any()
egen=e.generation.to_numpy();edel=e.delivery.to_numpy()
holidays=pd.to_datetime(['2026-01-01','2026-02-16','2026-05-25','2026-07-04','2026-09-07','2026-11-11','2026-11-26','2026-12-25'])
weekend=(idx.dayofweek>=5)|np.isin(idx.tz_localize(None).normalize(),holidays)
superoff=((hour<6)|((hour>=10)&(hour<14))| (weekend&(hour<14)))
peak=(hour>=16)&(hour<21);summer=(mon>=6)&(mon<=10)
gen=np.where(summer,np.where(peak,.48396,np.where(superoff,.08385,.17818)),np.where(peak,.20574,np.where(superoff,.07627,.14757)))
udc=np.where(superoff,.04114,.31218);nonnet=.021 # conservative approximation PPP + wildfire/DWR nonbypassable components
retail=gen+udc+.00591;delivery=retail-gen-nonnet
fixed=365*.79343
# Optimize solar-only charging, no battery export or grid charging. Cyclic annual SOC.
eta=np.sqrt(.90)
B=diags([np.ones(n),-np.ones(n-1)],[0,-1],format='lil');B[0,n-1]=-1
A=hstack([-eta*diags(np.ones(n)),diags(np.ones(n))/eta,B.tocsr()],format='csr')
cache={}
def dispatch(k,b,tilt=30,loadarr=None,pvscale=1,batfade=1):
 L=load if loadarr is None else loadarr;P=pv[tilt]*k*pvscale
 excess=np.maximum(P-L,0);deficit=np.maximum(L-P,0)
 if b:
  bounds=np.vstack([np.column_stack([np.zeros(n),np.minimum(excess,5)]),np.column_stack([np.zeros(n),np.minimum(deficit,5)]),np.column_stack([np.zeros(n),np.full(n,b*.9*batfade)])])
  sol=linprog(np.r_[egen+edel,-retail,np.full(n,1e-9)],A_eq=A,b_eq=np.zeros(n),bounds=bounds,method='highs')
  if not sol.success:raise RuntimeError(sol.message)
  c=sol.x[:n];d=sol.x[n:2*n];soc=sol.x[2*n:];I=deficit-d;E=excess-c
  assert np.max(abs(A@sol.x))<1e-5
 else:c=d=soc=np.zeros(n);I=deficit;E=excess
 assert abs(P.sum()+I.sum()-L.sum()-E.sum()-(c.sum()-d.sum()))<1e-5
 return dict(imports=I,exports=E,charge=c,discharge=d,soc=soc,pv=P,load=L)
def bill(r,ratefactor=1,exportfactor=1):
 I=r['imports'];E=r['exports'];surplus=max(0,E.sum()-I.sum())
 genbill=max(0,np.dot(I,gen)*ratefactor-np.dot(E,egen)*exportfactor+surplus*.08672*exportfactor)
 delbill=max(0,np.dot(I,delivery)*ratefactor-np.dot(E,edel)*exportfactor+surplus*.02329*exportfactor)
 return fixed+I.sum()*nonnet*ratefactor+genbill+delbill-surplus*.01702
nosolar=bill(dispatch(0,0));billcal=(bill_intercept+bill_slope*loadnormal).sum()
# Annual equivalent cost of 25-year discounted cash flows; no utility escalation beyond inflation.
def finance(k,b,savings,premium=7500,rebate=False,costfactor=1,discount=.05,batrepl=.60):
 solar=k*2560;bat={0:0,13.5:14250,27:26000}[b];initial=(solar+bat+premium+2500)*costfactor-(min(10000,b*350) if rebate else 0)
 if k==0 and b==0:return dict(upfront=0,annual_equipment=0,annual_net_saving=0,npv=0)
 df=np.array([(1+discount)**-y for y in range(1,26)]);annuity=df.sum()
 replacement=((2000+(bat*batrepl))/(1+discount)**15)*costfactor
 maintenance=.005*solar*costfactor
 pvsavings=np.sum(df*savings*.995**np.arange(25))
 equipment=(initial+replacement+maintenance*annuity)/annuity
 return dict(upfront=initial,annual_equipment=equipment,annual_net_saving=pvsavings/annuity-equipment,npv=pvsavings-initial-replacement-maintenance*annuity)
rows=[];runs={}
# Coarse capacity sweep at current 30-degree geometry; refine around winning sizes later.
for tilt in [30,best]:
 for b in [0,13.5,27]:
  for k in np.arange(2,8.51,.5):
   r=dispatch(float(k),b,tilt);runs[(tilt,float(k),b)]=r;cost=bill(r);fin=finance(k,b,nosolar-cost)
   maxkw=planarea/np.cos(np.deg2rad(tilt))*.092903*.22*.9
   rows.append(dict(tilt=tilt,solar_kw=k,battery_kwh=b,annual_solar_kwh=r['pv'].sum(),august_kwh=r['pv'][mon==8].sum(),annual_import_kwh=r['imports'].sum(),annual_export_kwh=r['exports'].sum(),annual_bill=cost,first_year_saving=nosolar-cost,roof_fits_22pct_90pct=k<=maxkw,**fin))
  print('Finished',tilt,b,flush=True)
results=pd.DataFrame(rows);results.to_csv(OUT/'system-comparison.csv',index=False)
bestrow=results[results.roof_fits_22pct_90pct].sort_values('annual_net_saving',ascending=False).iloc[0]
# Financial sensitivities evaluated for every design, with identical operating assumptions.
sens=[]
for label,args in [('Custom roof, central',{}),('Conventional installation',{'premium':0}),('Custom premium $15,000',{'premium':15000}),('Installed cost -20%',{'costfactor':.8}),('Installed cost +20%',{'costfactor':1.2}),('Discount rate 3%',{'discount':.03}),('Discount rate 8%',{'discount':.08}),('Conditional SDCP rebate',{'rebate':True}),('Battery replacement full price',{'batrepl':1})]:
 ranked=[]
 for _,row in results[results.roof_fits_22pct_90pct].iterrows():
  f=finance(row.solar_kw,row.battery_kwh,row.first_year_saving,**args);ranked.append(dict(scenario=label,tilt=row.tilt,solar_kw=row.solar_kw,battery_kwh=row.battery_kwh,**f))
 sens.append(max(ranked,key=lambda x:x['annual_net_saving']))
# Operational uncertainties re-simulated for a practical shortlist.
short=[(30,4.,0),(30,5.,0),(30,6.,13.5),(30,7.,13.5),(30,7.,27),(best,7.,13.5)]
for label,kwargs,rf,ef in [('Recent 2016-25 climate',{'loadarr':hourly_load(loadrecent)},1,1),('Cooling +50%',{'loadarr':hourly_load(monthly_load(normal,coolmult=1.5))},1,1),('Base computers -20%',{'loadarr':hourly_load(monthly_load(normal,basemult=.8),base*.8)},1,1),('Base computers +20%',{'loadarr':hourly_load(monthly_load(normal,basemult=1.2),base*1.2)},1,1),('PV weather -10%',{'pvscale':.9},1,1),('PV weather +10%',{'pvscale':1.1},1,1),('Battery usable capacity -20%',{'batfade':.8},1,1),('Import rates -20%',{},.8,1),('Import rates +20%',{},1.2,1),('Export credits halved',{},1,.5),('AC delayed four hours',{'loadarr':hourly_load(loadnormal,lag=4)},1,1)]:
  ranked=[]
  for t,k,b in short:
   r=dispatch(k,b,t,**kwargs);ns=bill(dispatch(0,0,t,loadarr=kwargs.get('loadarr')),rf,ef);saving=ns-bill(r,rf,ef);ranked.append(dict(scenario=label,tilt=t,solar_kw=k,battery_kwh=b,**finance(k,b,saving)))
  sens.append(max(ranked,key=lambda x:x['annual_net_saving']))
pd.DataFrame(sens).to_csv(OUT/'sensitivity.csv',index=False)
# Representative monthly table and hourly audit file for practical 7 kW + one battery.
chosen=runs[(30,7.,13.5)]; monthly=[]
for m in months:
 mask=mon==m;I=chosen['imports'][mask];E=chosen['exports'][mask]
 monthly.append(dict(month=names[m-1],normal_temperature_F=normal[m-1],recent_temperature_F=recent[m-1],temperature_2026_F=actual[m-1] if m<=8 else np.nan,base_kwh=base*days[m-1],modeled_use_kwh=loadnormal[m-1],modeled_current_bill_usd=bill_intercept+bill_slope*loadnormal[m-1],target_array_kwh=pvs[best][m-1]*targetkw,seven_kw_30deg_kwh=chosen['pv'][mask].sum(),grid_import_kwh=I.sum(),grid_export_kwh=E.sum(),solar_bill_before_credit_bank_trueup=days[m-1]*.79343+I.sum()*nonnet+max(0,np.dot(I,gen[mask])-np.dot(E,egen[mask]))+max(0,np.dot(I,delivery[mask])-np.dot(E,edel[mask]))))
monthly=pd.DataFrame(monthly);monthly.to_csv(OUT/'monthly.csv',index=False)
h=pd.DataFrame(chosen,index=idx);h['import_rate']=retail;h['export_generation_rate']=egen;h['export_delivery_rate']=edel;h.to_csv(OUT/'hourly-7kw-one-battery.csv.gz',compression='gzip',index_label='local_time')
sun=[]
for m in months:
 dt=pd.DatetimeIndex([pd.Timestamp(2026,int(m),15,tz='America/Los_Angeles')]);s=pvlib.solarposition.sun_rise_set_transit_spa(dt,32.8,-117.24).iloc[0]
 p=pvlib.solarposition.get_solarposition(pd.DatetimeIndex([s.sunrise,s.sunset,s.transit]),32.8,-117.24)
 sun.append(dict(month=names[m-1],sunrise=s.sunrise.strftime('%H:%M %Z'),sunset=s.sunset.strftime('%H:%M %Z'),daylight_hours=(s.sunset-s.sunrise).total_seconds()/3600,sunrise_azimuth=p.azimuth.iloc[0],sunset_azimuth=p.azimuth.iloc[1],noon_elevation=p.apparent_elevation.iloc[2]))
pd.DataFrame(sun).to_csv(OUT/'sun-geometry.csv',index=False)
summary=dict(base_kwh_day=base,base_continuous_kw=base/24,balance_temperature_F=balance,cooling_slope_kwh_per_day_per_F=beta,fit_rmse_kwh=np.sqrt(rmse2),annual_normal_kwh=loadnormal.sum(),annual_recent_kwh=loadrecent.sum(),normal_august_kwh=loadnormal[7],august_2026_temperature=actual[7],august_normal_temperature=normal[7],bill_fit_fixed=bill_intercept,bill_fit_marginal=bill_slope,annual_bill_calibrated=billcal,annual_bill_EVTOU5=nosolar,export_rate_name=export_rate_name,best_south_tilt=best,target_kw=targetkw,target_annual_kwh=pvs[best].sum()*targetkw,target_july_kwh=pvs[best][6]*targetkw,best_candidate=bestrow.to_dict(),seven_kw_one_battery=results[(results.tilt==30)&(results.solar_kw==7)&(results.battery_kwh==13.5)].iloc[0].to_dict(),azimuth=az,sensitivities=sens,sun=sun)
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,default=lambda o:bool(o) if isinstance(o,np.bool_) else float(o)))
# Presentation charts.
pdf=PdfPages(OUT/'Solar-Analysis-Charts.pdf')
def save(fig,name):
 fig.tight_layout();fig.savefig(OUT/(name+'.png'),dpi=170,bbox_inches='tight');pdf.savefig(fig,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(2,1,figsize=(12,9),gridspec_kw={'height_ratios':[1.3,1]})
a=ax[0];a.bar(months,base*days,color='#a7b9c9',label='Steady base load');a.bar(months,loadnormal-base*days,bottom=base*days,color='#de8c52',label='Cooling in a normal year');a.plot(months,pvs[best]*targetkw,'o-',color='#2d916e',lw=2.5,label=f'{targetkw:.2f} kW at {best}°: August target');a.plot(months,pvs[30]*7,'--',color='#4f6cb2',lw=2,label='7 kW at current 30° roof');a.scatter(bills.m,bills.usage_kwh,s=70,color='#222',marker='D',label='Your six 2026 bills',zorder=5);a.set(xticks=months,xticklabels=names,ylabel='Energy (kWh/month)',title='Your base load dominates the year; cooling drives the summer increase');a.legend(ncol=2,fontsize=9);a.set_ylim(0,1650);a.grid(axis='y',alpha=.2)
a=ax[1];a.plot(months,monthly.modeled_current_bill_usd,'o-',color='#222',label='Current bill relationship × normal-year use');a.scatter(bills.m,bills.reported_bill_usd,color='#222',marker='D');a.plot(months,monthly.solar_bill_before_credit_bank_trueup,'o-',color='#2d916e',label='7 kW + 13.5 kWh battery: estimated utility charges');a.set(xticks=months,xticklabels=names,ylabel='Utility bill ($/month)',title='Utility charges only — equipment cost is compared separately');a.legend(fontsize=9);a.grid(axis='y',alpha=.2)
fig.text(.02,-.005,'Forecast, not measured interval data. Solar case uses bundled SDG&E EV-TOU-5; monthly values precede credit banking/true-up.\nNormal weather: 1991–2020 ERA5. Solar: PVGIS NSRDB 2005–2015. No gas charges or climate credits modeled.',fontsize=9,color='#555');save(fig,'monthly-energy-and-cost')
fig,ax=plt.subplots(1,2,figsize=(12,5));a=ax[0];xx=np.linspace(54,80,200);a.plot(xx,base+beta*np.maximum(xx-balance,0),color='#2d916e',lw=2,label='Fitted base + cooling');a.scatter(actual[ix],observed/days[ix],s=70,color='#222');
for m,t,u in zip(bills.m,actual[ix],observed/days[ix]):a.annotate(names[m-1],(t,u),xytext=(5,5),textcoords='offset points')
a.set(xlabel='Mean monthly outdoor temperature (°F)',ylabel='Household energy (kWh/day)',title=f'Fit: {base:.2f} + {beta:.2f} × max(T − {balance:.1f}, 0)');a.legend();a.grid(alpha=.2)
a=ax[1];a.plot(months,normal,'o-',label='1991–2020 normal');a.plot(months,recent,'--',label='2016–2025 average');a.plot(months[:8],actual[:8],'o-',label='2026 January–August');a.set(xticks=months,xticklabels=names,ylabel='Monthly mean temperature (°F)',title='Coastal San Diego weather');a.legend();a.grid(alpha=.2);save(fig,'temperature-fit')
fig,ax=plt.subplots(1,2,figsize=(12,5));a=ax[0];x=angles.tilt_deg;a.plot(x,angles.august_kwh_per_kw,'o-',label='August');a.plot(x,angles.july_kwh_per_kw,'o-',label='July');a.set(xlabel='Roof tilt (degrees)',ylabel='kWh per installed kW per month',title='Summer production per panel');a.legend();a.grid(alpha=.2)
a=ax[1];a.plot(x,angles.roof_sqft_at_90pct_coverage,label='Roof area needed for 1,200 kWh in August',lw=2);a.plot(x,angles.existing_envelope_sqft,label='Area over existing roof footprint',lw=2);a.set(xlabel='Roof tilt (degrees)',ylabel='Sloped area (sq ft)',title='22% modules, 90% generating panel coverage');a.legend(fontsize=8);a.grid(alpha=.2);save(fig,'roof-angle-and-fit')
fig,ax=plt.subplots(figsize=(12,6));r=results[results.tilt==30]
for b,c in [(0,'#547aa5'),(13.5,'#26866e'),(27,'#c28446')]:
 q=r[r.battery_kwh==b];ax.plot(q.solar_kw,q.annual_net_saving/12,'o-',color=c,label=f'{b:g} kWh battery')
ax.axhline(0,color='#555',lw=1);ax.axvspan(7.38,8.5,color='#ddd',alpha=.4,label='Beyond 90% roof coverage at 22% efficiency');ax.set(xlabel='Solar system (kW DC)',ylabel='Net saving after amortized equipment ($/month)',title='Financial comparison — current 30° roof, custom solar finish');ax.legend();ax.grid(alpha=.2);fig.text(.02,-.02,'25 years, 5% real discount, 0.5% annual savings degradation; battery/inverter replacement in year 15.\nIncludes $7,500 custom-roof allowance + $2,500 electrical allowance; no rebate. Utility tariff and hourly household profile provisional.',fontsize=9);save(fig,'system-economics')
pdf.close()
print(json.dumps(summary,indent=2,default=lambda o:bool(o) if isinstance(o,np.bool_) else float(o)),flush=True)
