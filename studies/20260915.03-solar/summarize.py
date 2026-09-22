import json,math,calendar,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent;d=json.loads((p.parent/'optimization/exposed-frame/cad-mesh.json').read_text());end=122.7624491117621-8;full=exposed=0
for o in d['objects']:
 if o['material']!='pv':continue
 v=o['vertices'];dx=max(t[0] for t in v)-min(t[0] for t in v);a=min(t[1] for t in v);b=max(t[1] for t in v);full+=dx*(b-a)/math.cos(math.pi/6)/144;exposed+=dx*max(0,min(b,end)-a)/math.cos(math.pi/6)/144
j=json.loads((p/'pvgis-8kw.json').read_text());m=j['outputs']['monthly']['fixed'];annual=j['outputs']['totals']['fixed']['E_y'];summary=dict(gross_slope_ft2=419.317708333,exposed_gross_slope_ft2=281.5*(end+63)/math.cos(math.pi/6)/144,drawn_panel_surface_ft2=full,exposed_drawn_panel_surface_ft2=exposed,estimated_capacity_kw=[7,8],annual_energy_kwh=[annual*7/8,annual],basis='PVGIS 5.2 NSRDB; approximate ZIP92109 location32.80,-117.24; south30deg; building-integrated cSi;14% losses; no horizon shading;2005–2015 radiation data. Module layout and non-generating infill not finalized. Cap overlap removed from area, not simulated as shading.');(p/'summary.json').write_text(json.dumps(summary,indent=2));print(summary)
with (p/'monthly-production.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['month','8kW_kWh_month','7kW_kWh_month','8kW_kWh_day']);w.writerows((calendar.month_abbr[r['month']],r['E_m'],round(r['E_m']*7/8,1),r['E_d']) for r in m)
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False});fig,ax=plt.subplots(figsize=(10,4));ax.bar(range(12),[r['E_m'] for r in m],color='#247d89',width=.65);ax.set_xticks(range(12),[calendar.month_abbr[i] for i in range(1,13)]);ax.set_ylabel('Energy produced (kWh/month)');ax.set_ylim(0,1450);ax.set_title('San Diego garage • 8 kW solar scenario',loc='left',fontsize=17,weight='bold')
for i,r in enumerate(m):ax.text(i,r['E_m']+25,str(round(r['E_m']/10)*10),ha='center',fontsize=9)
fig.text(.08,.025,'12,919 kWh/year • South-facing 30° • No shade • Building-integrated mounting • PVGIS estimate',fontsize=10);fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(p/'monthly-production.png',dpi=170)
