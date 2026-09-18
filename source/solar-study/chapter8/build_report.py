"""Build the curated Chapter 8 PDF, Markdown, figures, data and source archive."""
from pathlib import Path
import os, json, math, shutil, csv, hashlib, zipfile, html, re
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/garage-solar-mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[2]; WORK=Path(__file__).resolve().parent; R=WORK/'results'
C=ROOT/'report/08-solar-electrical-and-energy'; F=C/'figures'; DATA=C/'data'; HIST=C/'historical'
for p in [C,F,DATA,HIST]: p.mkdir(parents=True,exist_ok=True)
OLD=ROOT/'solar-study/optimization/results'
s=json.loads((R/'summary.json').read_text()); prior=json.loads((OLD/'summary.json').read_text())
a=pd.read_csv(R/'angle-comparison.csv'); g=pd.read_csv(R/'roof-geometry.csv'); sy=pd.read_csv(R/'system-comparison.csv')
mo=pd.read_csv(R/'monthly-angle-production.csv'); ml=pd.read_csv(OLD/'monthly.csv'); bills=pd.read_csv(ROOT/'solar-study/bills/power-bills-2026.csv')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'white'})
cs=['#167D9A','#C78727','#803F8C']; names=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def save(fig,name):
    fig.tight_layout(); fig.savefig(F/(name+'.png'),dpi=180,bbox_inches='tight'); fig.savefig(F/(name+'.pdf'),bbox_inches='tight'); plt.close(fig)
fig,ax=plt.subplots(figsize=(10,4.8))
ax.bar(range(12),ml.modeled_use_kwh,color='#dce3e7',label='Modeled normal-year household use')
for t,c in zip([30,35,40],cs): ax.plot(range(12),mo[mo.tilt==t].six_kw_kwh,'o-',color=c,label=f'6 kW at {t}°')
ax.set(xticks=range(12),xticklabels=names,ylabel='kWh per month',title='Same 6 kW array: tilt shifts energy toward winter');ax.legend(ncol=2,fontsize=9);ax.grid(axis='y',alpha=.2);save(fig,'seasonal-production')
fig,ax=plt.subplots(1,2,figsize=(10,4))
for j,(col,title) in enumerate([('winter_DJF_per_kw','Winter: December–February'),('summer_JJA_per_kw','Summer: June–August')]):
    vals=a[col].values*6; ax[j].bar(['30°','35°','40°'],vals,color=cs)
    for k,v in enumerate(vals): ax[j].text(k,v+15,f'{v:,.0f} kWh\n{(v/vals[0]-1)*100:+.1f}%',ha='center',fontsize=9)
    ax[j].set(title=title,ylim=(0,max(vals)*1.23),ylabel='Season total for 6 kW')
save(fig,'seasonal-tradeoff')
fig,axes=plt.subplots(3,1,figsize=(11,10),sharex=True)
for ax,(t,c) in zip(axes,zip([30,35,40],cs)):
    r=g[(g['mode']=='fixed_325_sqft')&(g.tilt==t)].iloc[0]; end=r.plan_run_ft-5.25; floor=9+8/12; eave=floor+8
    ax.plot([-5.25,end],[9,r.slope_top_ft],lw=4,color=c)
    ax.plot([end,end],[r.slope_top_ft,eave],lw=2,color='#B74F36')
    ax.plot([end,(end+20.75)/2,21.083],[eave,eave+1.5,eave],lw=2,color='#334655')
    ax.plot([0,20.75],[floor,floor],color='#647789');ax.plot([0,0],[0,9],color='#999');ax.plot([20.75,20.75],[0,eave],color='#999')
    ax.plot([-5.25,-5.25],[0,9],color='#999');ax.axhline(eave,color='#aaa',ls=':',lw=.8)
    ax.fill_between([end,20.75],floor,eave,alpha=.1,color=c)
    ax.text(-4.9,18.6,f'{t}° / 325 ft²',color=c,weight='bold',fontsize=12)
    ax.text(-4.9,16.3,f'Run {r.plan_run_ft:.2f} ft\nRise {r.rise_ft:.2f} ft',fontsize=10)
    ax.text(11,12.7,f'Gross cap plan {r.cap_area_sqft:.0f} ft²\nDepth {r.cap_depth_within_walls_ft:.2f} ft',fontsize=10)
    ax.annotate(f'Slope top {r.slope_top_ft:.2f} ft\nClerestory {r.clerestory_inches:.1f} in',xy=(end,r.slope_top_ft),xytext=(end+2,20.5),arrowprops=dict(arrowstyle='-',color='#777'),fontsize=9)
    ax.set(ylim=(7.6,23),ylabel='Height above study grade (ft)');ax.grid(alpha=.15)
axes[-1].set(xlabel='South ← distance from existing south wall (ft) → North',xlim=(-6,23))
fig.suptitle('West sections — fixed solar area, fixed 17 ft 8 in cap eave',y=1.01,fontsize=15,weight='bold');save(fig,'west-sections')
fig,ax=plt.subplots(1,2,figsize=(11,4.6))
for mode,style,label in [('fixed_325_sqft','-','Keep 325 ft² solar face'),('fixed_plan_run','--','Keep 12 ft horizontal run')]:
    q=g[g['mode']==mode];ax[0].plot(q.tilt,q.solar_area_sqft,'o'+style,label=label);ax[1].plot(q.tilt,q.clerestory_inches,'o'+style,label=label)
ax[0].set(ylabel='Gross solar face (ft²)',xlabel='Pitch (degrees)',title='Panel area versus roof footprint');ax[1].set(ylabel='Clerestory rise (inches)',xlabel='Pitch (degrees)',title='Window space disappears as the slope rises');ax[1].axhline(0,color='#b44',lw=1)
for x in ax:x.set_xticks([30,35,40]);x.legend(fontsize=8);x.grid(alpha=.2)
save(fig,'geometry-tradeoff')
fig,ax=plt.subplots(figsize=(10,5.5)); W=281.5; H=325/(281.5/12)*12
ax.add_patch(Rectangle((0,0),W,H,facecolor='#e5eaee',edgecolor='#31475a',lw=2))
pw=68.;ph=47.4;gap=.5;startx=(W-4*pw-3*gap)/2;starty=(H-3*ph-2*gap)/2
for row in range(3):
 for col in range(4):
    x=startx+col*(pw+gap);y=starty+row*(ph+gap);ax.add_patch(Rectangle((x,y),pw,ph,facecolor='#183e58',edgecolor='white'));ax.text(x+pw/2,y+ph/2,'470 W',color='white',ha='center',va='center')
ax.set(xlim=(-10,W+10),ylim=(-10,H+10),aspect='equal',xlabel='East–west distance on roof (inches)',ylabel='Distance along solar slope (inches)',title='Illustrative physical fit: 12 × 470 W = 5.64 kW')
save(fig,'module-layout')
fig,ax=plt.subplots(figsize=(10,4.8))
for b,c in [(0,cs[0]),(13.5,cs[1]),(27,cs[2])]:
    q=sy[(sy.tilt==30)&(sy.battery_kwh==b)];ax.plot(q.solar_kw,q.annual_bill,'o-',color=c,label=f'{b:g} kWh battery')
ax.axvspan(6,8.1,color='#e9e9e9',alpha=.5,label='Above approximate 325 ft² capacity at 22%, 90% coverage')
ax.set(xlabel='Solar nameplate (kW DC)',ylabel='Modeled annual utility bill ($)',title='One battery captures most of the modeled bill benefit');ax.legend(fontsize=8);ax.grid(alpha=.2);save(fig,'battery-sizing')
fig,axes=plt.subplots(2,1,figsize=(10,6),sharex=True)
h=pd.read_csv(R/'hourly-6kw-35deg.csv.gz');h['time']=pd.to_datetime(h.local_time,utc=True).dt.tz_convert('America/Los_Angeles');h['month']=h.time.dt.month;h['hour']=h.time.dt.hour
for ax,m,title in [(axes[0],1,'January average day'),(axes[1],8,'August average day')]:
    q=h[h.month==m].groupby('hour').mean(numeric_only=True)
    for col,c in [('pv','#c58b27'),('load','#273f4d'),('charge','#39a293'),('discharge','#8b5bb0')]:ax.plot(q.index,q[col],label=col,color=c)
    ax.set(title=title,ylabel='Average kW');ax.grid(alpha=.2);ax.legend(ncol=4,fontsize=8)
axes[-1].set(xlabel='Local hour');save(fig,'battery-operation')

# Controlled source copies and complete historic gallery.
legacy=[]
for src in sorted((ROOT/'solar-study').glob('*.png'))+sorted(OLD.glob('*.png')):
    dest=F/('historical-'+src.name);shutil.copy2(src,dest);legacy.append((src,dest))
for src in [ROOT/'roof-options/south-post-solar-clerestory.png',ROOT/'roof-options/west-elevation-roof-options.png']:
    dest=F/('historical-'+src.name);shutil.copy2(src,dest);legacy.append((src,dest))
for src in list(OLD.glob('*.pdf'))+[ROOT/'roof-options/south-post-solar-clerestory.pdf',ROOT/'roof-options/west-elevation-roof-options.pdf']:
    shutil.copy2(src,HIST/src.name)
for src in R.glob('*.csv'):shutil.copy2(src,DATA/src.name)
for src in [ROOT/'solar-study/bills/power-bills-2026.csv',OLD/'monthly.csv',OLD/'sensitivity.csv',OLD/'sun-geometry.csv',OLD/'azimuth.csv']:
    shutil.copy2(src,DATA/('prior-'+src.name if src.name in ['monthly.csv','sensitivity.csv','azimuth.csv'] else src.name))

styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyC',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=8,textColor=colors.HexColor('#263b49')))
styles.add(ParagraphStyle(name='SmallC',parent=styles['BodyC'],fontSize=8,leading=11))
styles.add(ParagraphStyle(name='HeadingC',fontName='Helvetica-Bold',fontSize=20,leading=24,spaceAfter=15,textColor=colors.HexColor('#173e55')))
styles.add(ParagraphStyle(name='CallC',parent=styles['BodyC'],fontName='Helvetica-Bold',fontSize=12,leading=17,backColor=colors.HexColor('#edf5f4'),borderPadding=10,spaceBefore=8,spaceAfter=15))
story=[];md=[];page_titles=[]
def p(text,style='BodyC'):
    story.append(Paragraph(text,styles[style]));markdown=text.replace('<b>','**').replace('</b>','**');markdown=re.sub(r'<link href="([^"]+)"[^>]*>(.*?)</link>',r'[\2](\1)',markdown);md.append(markdown+'\n')
def page(title):
    if story:story.append(PageBreak())
    page_titles.append(title);story.append(Paragraph(title,styles['HeadingC']));md.append('\n## '+title+'\n')
def table(rows,widths=None):
    if widths is None:widths=[492/len(rows[0])]*len(rows[0])
    cells=[[Paragraph(html.escape(str(x)),styles['SmallC']) for x in row] for row in rows]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dce9ed')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f4f6f7')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),1,colors.HexColor('#597988'))]));story.extend([t,Spacer(1,10)])
    md.append('| '+' | '.join(str(x) for x in rows[0])+' |\n| '+' | '.join('---' for _ in rows[0])+' |\n'+'\n'.join('| '+' | '.join(str(x) for x in row)+' |' for row in rows[1:])+'\n')
def image(name,caption,maxh=290):
    path=F/(name+'.png');w,h=ImageReader(str(path)).getSize();scale=min(492/w,maxh/h);story.append(Image(str(path),width=w*scale,height=h*scale));p(caption,'SmallC');md.append(f'![{caption}](figures/{path.name})\n')
def money(x):return f'${x:,.0f}'
def row(k,b,t=30):return sy[(sy.solar_kw==k)&(sy.battery_kwh==b)&(sy.tilt==t)].iloc[0]

page('08 / Solar, battery and roof design')
p('1370 Wilbur Avenue • Pacific Beach, San Diego, CA 92109','SmallC')
p('SOL-001 • Revision 1 • 15 September 2026 • Draft design-development report','SmallC')
p('Plan around approximately <b>5.6–6.0 kW of solar and one 13.5 kWh battery</b>. Develop the <b>35° roof option</b>: it shifts energy toward winter and gains loft envelope with almost no annual generation penalty. Confirm panel fit and clerestory height before selecting the roof.','CallC')
image('seasonal-production','Typical-year production from cached PVGIS data; household load inferred from six bills.',285)
p('The current 325 ft² solar face is smaller than the 401 ft² face used in earlier energy studies. This chapter corrects that mismatch, retains the historical work with labels, and adds 30°/35°/40° generation, battery-dispatch and geometric comparisons.')
p('This is a planning recommendation for owner review. The array layout, approved roofing system, electrical design, utility provider, site shade, permitting envelope and contractor prices remain to be resolved.')

page('Reading guide and evidence status')
table([['Part','What it establishes'],['1. Demand and solar resource','Six bills; weather model; sunlight and seasonal production.'],['2. Roof area and tilt','325 ft² current concept; physical panel fit; 30°/35°/40° tradeoffs.'],['3. Storage and economics','Battery operation; system-size comparison; cost and tariff sensitivity.'],['4. Design coordination','Integrated roof details; next design decisions; source register.'],['Appendix / historical figures','All recovered solar charts plus related roof studies, labeled with their limitations.']],[145,347])
p('The report contains new calculations and curated historical material. New calculations use the same cached solar/weather inputs and financial framework as the earlier study, allowing changes caused by pitch to be isolated. Historical charts and PDFs are evidence of prior analysis; their older roof-area assumptions do not govern the current concept.')
p('kW is power: the rate of production or use. kWh is energy accumulated over time. A 6 kW solar array is its DC nameplate rating under test conditions. It does not supply 6 kW continuously. One average kW across a year means 8,760 kWh/year.')
p('The data folder supplies bill inputs, monthly production, geometry, system comparisons, sun geometry and validation tables. The accompanying analysis archive preserves the original reports, source data, scripts and hourly runs. Editable report text is supplied as Markdown.')

page('1 / Household demand')
table([['2026 bill','Reported kWh','Reported cost']]+[[r.month,str(r.usage_kwh),money(r.reported_bill_usd)] for _,r in bills.iterrows()],[150,150,192])
p('February is treated as a month without air conditioning: 768 / 28 = <b>27.43 kWh/day</b>, or <b>1.14 kW continuously</b>. The earlier recollection of 24 kWh/day was approximate. Calendar month lengths substitute for actual billing dates.')
p('The retained change-point model is daily kWh = 27.43 + 1.53 × max(monthly mean temperature − 63.57°F, 0). Normal weather gives about <b>11,096 kWh/year</b>, including roughly 10,011 kWh of base consumption and 1,085 kWh of cooling. The warmer 2016–2025 weather average gives about 11,335 kWh/year.')
p('The six-point fit has about 56 kWh/month root-mean-square error. April is below the assumed fixed base; this exposes billing-period and usage variability. The inferred base/cooling split is provisional, not a measured end-use breakdown. Obtain 12 months of bills and interval data before ordering equipment.')
p('The historical bill relationship is about $15.15/month + $0.3765/kWh, giving $4,360/year at modeled normal use. The tariff simulation uses a separate bundled SDG&E EV-TOU-5 baseline of $4,303/year. These are different estimation methods, not two simultaneous charges.')

page('2 / Sun, weather and energy basis')
p('PVGIS 5.2 calculations use approximate location 32.80°N, 117.24°W, south-facing crystalline-silicon modules, building-integrated mounting, 14% user system losses, and NSRDB radiation data for 2005–2015. Cloud variability is already reflected in irradiance. Do not subtract an additional cloud percentage. Building mounting includes temperature effects; the 14% input is not the model’s entire loss budget. [1]')
p('No horizon or local shading is included, following the owner’s sunny-site description. A measured horizon, nearby trees, the clerestory, fascia/cap projection, and future vegetation still need checking. The cap overlap in the older area calculation was removed geometrically; its shadow was not simulated.')
sun=pd.read_csv(OLD/'sun-geometry.csv')
table([['Mid-month','Sunrise','Sunset','Daylight','Noon elevation']]+[[r.month,r.sunrise,r.sunset,f'{r.daylight_hours:.1f} h',f'{r.noon_elevation:.1f}°'] for _,r in sun.iloc[[0,2,5,6,7,8,11]].iterrows()])
p('Azimuth is compass bearing: south is 180°. The retained azimuth study found small August gains for southwest orientation at 15°, but that changes the roof direction and does not justify reorienting this design. Its numerical table remains in the supporting data.')
p('Weather inputs use ERA5 via Open-Meteo, with 1991–2020 normals and a 2016–2025 comparison. They describe regional coastal climate rather than a sensor on this roof. [2]')

page('3 / How much roof do we have?')
table([['Geometry generation','Solar face','Use in this chapter'],['Earlier exposed-frame design','419.3 ft² gross; 401.3 ft² after cap overlap','Historical 7–8 kW studies only.'],['Current south-post / clerestory concept','325 ft² gross sloped face','Primary design comparison; full width 23 ft 5½ in.'],['Current 30° plan projection','281.5 ft²','About 12 ft run; starts 5 ft 3 in south of existing wall.']],[155,142,195])
p('The old drawing calls 325 ft² an “active solar plane.” That label overstates what is available to generating modules. Here, 325 ft² is <b>gross roof face</b>, including panel gaps, edge treatments, non-generating glass, and any required access clearances.')
table([['System','Module area at 22%','Gross face at 90% coverage'],['5.64 kW',f'{5.64/.22/.09290304:.0f} ft²',f'{5.64/.22/.09290304/.9:.0f} ft²'],['6.00 kW',f'{6/.22/.09290304:.0f} ft²',f'{6/.22/.09290304/.9:.0f} ft²'],['7.00 kW',f'{7/.22/.09290304:.0f} ft²',f'{7/.22/.09290304/.9:.0f} ft²']])
p('At 22% module efficiency, 325 ft² accommodates 5.31 kW at 80% coverage, 5.65 kW at 85%, or 5.98 kW at 90%. At 23% and 90%, it reaches 6.25 kW. These are area budgets, not proven module layouts. Equation: kW = roof ft² × 0.09290304 × module efficiency × coverage.')
p('Roof dormers, balconies and non-generating infill reduce this budget; surrounding shadows can cost additional energy. A 6 kW array leaves little discretionary roof area in the 325 ft² version.')

page('4 / A physical module fit check')
image('module-layout','Slope-face view, inches, schematic. North is upslope; east/west orientation is not material to this fit test.',310)
p('A current REC Alpha Pure-RX example is 470 W and about 68.0 × 47.4 in. (22.4 ft²), with maximum module efficiency about 22.6%. Twelve modules in a four-by-three landscape grid give <b>5.64 kW</b> and about <b>269 ft²</b> of modules. This is an example for checking scale, not a product selection. [3]')
p('With illustrative half-inch gaps, the grid occupies 273.5 × 143.2 in. The roof is 281.5 × 166.3 in. That leaves only about 4 in. on each east/west edge and 11.5 in. at each upslope/down-slope edge if centered. Required fire access, roof edges, clamps and waterproofing may invalidate this layout.')
p('Adding a thirteenth module cannot be justified merely from remaining square feet; it needs a real packing layout. Sixteen of these modules do not fit the 325 ft² face. At a fixed 12-ft run, even 40° gives only about 188 in. slope length, short of four 47.4-in. rows plus gaps.')
p('Recommendation: request layouts in the 5.6–6.0 kW range using approved roof/module assemblies; price alternatives before changing the building around a nominal panel-area target.')

page('5 / Pitch: annual and seasonal generation')
image('seasonal-tradeoff','Fixed 6 kW nameplate; winter = December–February; summer = June–August.',250)
table([['Pitch','Annual 6 kW','Winter 6 kW','Summer 6 kW','August 6 kW']]+[[f'{r.tilt:.0f}°',f'{r.annual_per_kw*6:,.0f}',f'{r.winter_DJF_per_kw*6:,.0f}',f'{r.summer_JJA_per_kw*6:,.0f}',f'{r.august_per_kw*6:,.0f}'] for _,r in a.iterrows()])
p('Relative to 30°, 35° changes annual energy by −0.01%, increases winter energy 3.26%, and decreases summer energy 2.85%. At 40°, annual energy changes −0.58%, winter rises 5.86%, and summer falls 6.14%. The near-identical annual output of 30° and 35° is far below weather and model uncertainty.')
p('For 6 kW, the winter gains are about 69 kWh at 35° and 124 kWh at 40°. They are useful but modest. Steeper pitch does not create seasonal energy storage; the battery still shifts hours, not summer into winter.')
p('The earlier 20° comparison gave about 1,587 kWh per installed kW annually, versus 1,615 at 30°: about 1.7% less. It required about 5.52 kW to average 1 kW over the year, versus 5.42 kW at 30°. Its smaller sloped area over a fixed footprint further reduced available capacity.')
p('The hourly bill model shows only about $9/year more utility cost at 35° and $27/year at 40° for the same 6 kW and one battery. Treat differences this small as economically indistinguishable; choose among these pitches mainly for architecture, height and buildability.')

page('6 / Monthly output and sizing targets')
table([['Month','Modeled use','6 kW / 30°','6 kW / 35°','6 kW / 40°']]+[[names[i],f'{ml.iloc[i].modeled_use_kwh:,.0f}']+[f'{mo[(mo.month==i+1)&(mo.tilt==t)].six_kw_kwh.iloc[0]:,.0f}' for t in [30,35,40]] for i in range(12)])
table([['Pitch','kW for 1,200 kWh in August','kW for average 1 kW annually']]+[[f'{r.tilt:.0f}°',f'{r.kw_for_1200_august:.2f}',f'{r.kw_for_average_1kw:.2f}'] for _,r in a.iterrows()])
p('All production and use above are kWh/month. The owner’s final summer target was 1,200 kWh in August. At 30° it requires about 8.01 kW; at 40° about 8.39 kW. At 22% efficiency and 90% coverage these need roughly 435–456 ft², exceeding the 325 ft² concept. Size for useful annual savings unless the summer target becomes a firm requirement.')
p('A 5.64 kW array produces about 9,108 kWh/year at 30° or 9,106 at 35°; 6 kW produces about 9,689. This is 82–87% of modeled annual household consumption before storage losses, not equivalent grid independence.')

page('7 / West elevations: loft and clerestory')
image('west-sections','Schematic envelope sections, not construction drawings. Full east–west width is used for gross area; roof/truss thickness and side slopes are not deducted.',515)
p('These sections retain the newer study’s 9-ft low eave, 9-ft-8-in loft floor top, 17-ft-8-in cap eave, and 18-in cap rise. They do not alter the CAD model or establish zoning compliance. At 40°, the solar top passes above the retained cap eave; a positive clerestory needs a raised cap.','SmallC')

page('8 / Two different ways to steepen the roof')
table([['Keep 325 ft²','30°','35°','40°'],['Horizontal run (ft)']+[f'{x:.2f}' for x in g[g['mode']=='fixed_325_sqft'].plan_run_ft],['Solar rise (ft)']+[f'{x:.2f}' for x in g[g['mode']=='fixed_325_sqft'].rise_ft],['Gross cap plan (ft²)']+[f'{x:.0f}' for x in g[g['mode']=='fixed_325_sqft'].cap_area_sqft],['Clerestory at fixed cap (in)']+[f'{x:.1f}' for x in g[g['mode']=='fixed_325_sqft'].clerestory_inches]])
p('With the same sloped face, 35° moves the cap about 7.8 in. south, increasing gross cap plan area by 15.2 ft². At 40° it moves 16.6 in. south, gaining 32.5 ft². The cap areas are 328.5, 343.7 and 361.0 ft². These use the full 23-ft-5½-in roof width and the existing north-wall station; they are <b>not net usable interior loft area</b>. Side slopes, walls, stairs, voids and structure must be deducted.')
p('The 20.9-in clerestory at 30° shrinks to 8.6 in. at 35° and becomes a 2.9-in downward step at 40°. To preserve the original window band, raise the cap 12.2 in. at 35° or 23.7 in. at 40°. The cap ridge then becomes approximately 20.19 ft or 21.14 ft above the study grade, before any new assembly allowance.')
table([['Keep 12-ft run','30°','35°','40°'],['Gross solar face (ft²)']+[f'{x:.1f}' for x in g[g['mode']=='fixed_plan_run'].solar_area_sqft],['Area-based kW at 22%, 90%']+[f'{x:.2f}' for x in g[g['mode']=='fixed_plan_run'].capacity_22pct_90pct_kw],['Solar top above grade (ft)']+[f'{x:.2f}' for x in g[g['mode']=='fixed_plan_run'].slope_top_ft]])
p('At fixed footprint, steeper pitch provides more solar area and headroom under the slope, but no extra cap footprint. Preserving the clerestory requires cap raises of 17.7 in. at 35° or 37.7 in. at 40°. Greater PV capacity is only possible if additional modules physically fit. The 20.75-ft north–south wall length is the roof-study input; Chapter 3 records a conflicting model dimension that must be reconciled.')

page('9 / Geometry tradeoff and recommended pitch')
image('geometry-tradeoff','The dotted alternative keeps the roof transition at the same plan position; the solid alternative keeps generating-face area constant.',270)
p('<b>Develop 35° with approximately 325 ft² of solar face.</b> It preserves annual production, improves winter production, and gains a modest amount of tall loft envelope. Keep 30° as the height-constrained fallback. Use 40° if the extra loft space is worth the cap/clerestory redesign, rather than for the small energy gain alone.','CallC')
p('If preserving the current 20.9-in window band is important, study an approximately 12.2-in cap raise at 35°. If height cannot increase, redesign the clerestory with its roughly 8.6-in remaining gross band; actual glazing will be smaller after framing and flashings.')
p('No numerical net-floor-area gain is claimed here. The full roof width includes areas outside the garage footprint, and the loft’s side slopes and structural depths remain unsettled. The new geometry CSV retains gross headroom-envelope calculations solely as coordination data.')

page('10 / Why one battery is the useful starting point')
image('battery-operation','Synthetic average days for 6 kW / 35° / one 13.5 kWh battery. Dispatch assumes perfect knowledge of the modeled year; actual control will differ.',310)
p('The model uses 13.5 kWh nominal energy, a 10% reserve, 90% round-trip efficiency, and a conservative 5 kW charge/discharge limit. It permits solar-only charging and discharge to serve the building; no grid arbitrage or battery export. Tesla’s current 13.5 kWh Powerwall is one example of this capacity class, not the specified product. [4]')
p('At 6 kW / 35°, battery discharge is about 3,531 kWh/year. The modeled building still imports about 3,020 kWh/year and exports about 1,219 kWh/year. Annual energy balancing is not enough to eliminate imports because production and consumption occur at different hours.')
p('A 12.15 kWh operating window divided by the 1.14 kW base load is about 10.6 hours before further operating losses or restrictions. Air conditioning and machinery shorten backup time. A battery does not provide backup by itself: transfer/islanding hardware, circuit selection and inverter starting capacity must be designed.')

page('11 / Capacity and battery comparison')
image('battery-sizing','Planning tariff model at 30°. Gray region exceeds the current approximate area budget; it is retained to show the economic trend.',280)
table([['System at 30°','Installed allowance','Utility / year','Saving / year']]+[[f'{k:g} kW + {b:g} kWh',money(row(k,b).upfront),money(row(k,b).annual_bill),money(row(k,b).first_year_saving)] for k,b in [(4,0),(6,0),(5.64,13.5),(6,13.5),(7,13.5),(6,27)]],[145,115,112,120])
p('Moving from 6 kW alone to 6 kW plus one battery adds a $14,250 installed allowance and saves about $1,610/year in this model. Moving to a second battery adds about $11,750 but saves only another $165/year. A second battery is therefore a backup-duration choice, not the preferred bill-saving choice under these assumptions.')
p('The numerical optimum is shallow: 5.64, 6 and 6.5 kW plus one battery are close financially. Panel layout, real quotes and actual interval demand should choose the final number, not a tiny modeled difference.')

page('12 / Installed cost and lifecycle value')
table([['6 kW + one battery cost basis','Allowance'],['Conventional PV hardware/install at $2.56/W','$15,360'],['13.5 kWh battery and controls','$14,250'],['Electrical allowance','$2,500'],['Custom integrated-looking roof increment','$7,500'],['Total central allowance','$39,610']],[350,142])
p('These are retained planning allowances, not current contractor quotes. They exclude the garage structure and main roof construction, major service upgrades beyond the allowance, and any unpriced integrated-roof certification or fabrication. Obtain separate bids for the waterproof roof, active PV, matching infill, electrical work and battery to avoid double counting.')
p('The prior $2.56/W regional benchmark is preserved as an assumption rather than a verified market offer. A ±20% total-installed-cost range gives roughly $31,700–$47,500 for the central system. The cost of a bespoke solar skin could vary more than this range.')
p('At 30°, the central model gives about $3,465 first-year bill savings and roughly 11.4 years simple payback. With a 25-year horizon, 5% real discount rate, 0.5% annual savings degradation, maintenance of 0.5% of PV cost, and year-15 inverter/battery replacement, levelized net savings are only about $58/year; 25-year NPV is about $815. At 35°, they are about $49/year and $692. This is approximately break-even within uncertainty.')
p('If the $7,500 custom finish would be built regardless of solar, allocating it to the building budget improves the 30° solar investment’s levelized net benefit to about $590/year. This changes cost allocation, not the total cash required. A higher custom premium, more expensive replacement battery, cheaper future electricity or less consumption can reverse the result.')
p('No federal homeowner tax credit is deducted: current IRS guidance excludes residential clean-energy property placed in service after December 31, 2025. Business ownership and other tax provisions are outside this homeowner model. [5]')

page('13 / Export credits, tariffs and incentives')
p('SDG&E’s Solar Billing Plan values imported and exported energy by time. Residential customers use EV-TOU-5; evening imports from 4–9 p.m. make stored solar valuable. Export credits appear on the bill. A CCA customer must use its generation provider’s rules as well as SDG&E delivery charges. [6]')
p('The analysis retains bundled rates effective August 1, 2026: about 80.2 cents/kWh summer peak, 49.6 cents off-peak and 13.1 cents super off-peak; winter values are about 52.4, 46.6 and 12.3 cents. It includes $0.79343/day base service charge. Current weekday 10 a.m.–2 p.m. super-off-peak treatment is held across the planning year. [7, 8]')
p('The cached “Current 2026” export file contains NBT00 records although its README describes NBT26. That unresolved vintage mismatch is retained explicitly. The model approximates separate generation/delivery credit buckets, non-bypassable charges and annual surplus adjustment; it is not a full utility billing engine. [9]')
p('Annual net-surplus energy is repriced at net-surplus compensation rather than keeping the ordinary hourly export value. The prior model used 1.702 cents/kWh for that settlement. This is a historical assumption, not a guaranteed future rate. Whether a remaining balance is paid or carried forward depends on the applicable utility/CCA settlement rules; it must be confirmed before treating exports as cash income. [10]')
p('San Diego Community Power currently advertises $350/kWh for market-rate customers installing new solar plus battery: $4,725 for 13.5 kWh if eligible. Enrollment, approved equipment/installer, dispatch participation, available funds and service-provider eligibility must be checked. Keeping the upfront rebate requires at least five years in the program. No rebate or performance incentive is included in the central model. [11]')
p('Because provider, tariff and export vintage remain unconfirmed, dollar figures should be used to compare concepts. The narrow lifecycle margin is not sufficient evidence for a purchase decision.')

page('14 / Integrated roof and electrical scope')
p('The desired appearance is a continuous glossy solar face. Standard PV modules must remain intact; odd triangular areas can use compatible non-generating panels. Those pieces add no electrical capacity and need their own wind, impact, fire, drainage and attachment design.')
p('A concealed waterproof layer can be visually simple, but it must be durable, code-compliant and repairable. Ordinary rack-mounted modules do not automatically form an approved waterproof roof. Select either a tested integrated system or a coordinated weatherproof roof with compatible PV attachment, drainage and ventilation. Keep roof and solar costs separate in bids.')
p('The clerestory/cap projection requires a shadow check on the upper module row. Roof pathways, setbacks, access to junctions, module replacement and firefighter requirements may reduce the 325 ft² allocation. City IB-301 describes PV/ESS electrical submittals and the building-review requirements for structural modifications. [12]')
table([['Next design deliverable','Required content'],['Final array plan','Exact modules, dimensions, strings, setbacks/pathways, active/inactive infill, shading.'],['Electrical one-line','Service rating, inverter/ESS, circuit protection, conductors, grounding, disconnects and rapid shutdown.'],['Battery location and backup','Impact protection, clearances, transfer equipment, critical circuits and loads.'],['Roof details','Waterproof layer, flashings, drainage, ventilation, attachment and replacement access.'],['Commercial scope','Separate waterproof roof, PV, infill, battery, electrical and utility work prices.']],[155,337])

page('Sensitivity / How strong is the cost conclusion?')
sens=pd.read_csv(OLD/'sensitivity.csv')
table([['Retained scenario','Selected kW / battery kWh','Net benefit per year']]+[[r.scenario,f'{r.solar_kw:g} / {r.battery_kwh:g}',money(r.annual_net_saving)] for _,r in sens.iterrows()],[246,132,114])
p('Historical sweep: 30° and the prior summer-optimal pitch; older 401 ft² area constraint. Dollar values retain prior inputs. Some selected sizes exceed the current 325 ft² layout budget. These rows show how uncertainty changes the decision; they are not current installation quotes. New 30°/35°/40° cases are in the current system-comparison data.','SmallC')

page('15 / Recommendation and remaining decisions')
p('<b>Carry 5.6–6.0 kW DC and one 13.5 kWh battery into design development.</b> Compare 35° with the 30° fallback. The illustrated twelve-module 5.64 kW layout is a realistic scale check; its clearances still need professional layout review.','CallC')
p('Keep the 325 ft² face as the current area budget. If more capacity is wanted, enlarge the roof or identify a different approved module arrangement. The 8 kW summer-target system belongs to a larger roof concept; neither 35° nor 40° makes it fit within an unchanged 325 ft² face.')
p('Before selecting 35°, decide whether to raise the cap approximately one foot to preserve the window band. Coordinate that height with Chapter 3 setbacks, the survey, side-roof geometry, overhead utilities and structural depth. Keep all existing and proposed datums explicit.')
p('Before selecting equipment, obtain interval demand, full bills including the generation provider, a shade study, electrical-service information, fire-access layout and at least comparable contractor quotes. Test the design with a non-ideal battery controller and the actual tariff/credit rules. Re-run the financial analysis after those inputs are known.')
p('The 30 new system simulations pass annual energy balance with residual below 0.00000001 kWh. Monthly PV is normalized to the cached PVGIS totals. These checks establish internal numerical consistency; they do not validate the assumed household profile, legal roof envelope, product layout or future prices.')

page('16 / Methods and reproducibility')
p('The extension imports the definition portion of the earlier analysis into an isolated output directory and runs identical 30°/35°/40° cases. It preserves the original bill fit, PVGIS monthly totals, hourly TMY solar shapes, load timing, tariff model, battery reserve/power/efficiency and financial assumptions. No old result files are overwritten.')
p('Hourly solar shape uses pvlib irradiance transposition and temperature response, then scales each month to the official cached PVGIS energy estimate. Linear programming chooses solar charging and load-serving discharge over the year with cyclic battery state. Perfect foresight and idealized dispatch make this an optimistic operational comparison; the financial objective also simplifies credit caps.')
p('Roof calculations use width W = 281.5/12 ft, gross sloped face A = 325 ft², low eave 9 ft, floor top 9 + 8/12 ft, existing wall length 249/12 ft, and south-post offset 63/12 ft. For fixed face: slope length = A/W; run = length × cos(pitch); rise = length × sin(pitch). For fixed run: area = W × run / cos(pitch).')
p('Gross cap area uses W × (existing north-wall station − slope-end station). It is a roof-plan coordination quantity, not measured usable floor. Clear headroom must subtract roof and structure depths, and net floor must exclude side strips, openings, stairs and any undecked areas.')
p('The prior solar datasets use 2005–2015 radiation, so results describe that climatology, not a 2026 weather forecast. Annual differences of less than 1% between pitches should not be interpreted more precisely than the input data supports.')
p('The source archive preserves all recovered solar analysis code, raw cached inputs, CSV/JSON results, hourly audit files, original PDFs and diagrams, plus the relevant roof-option sources. It excludes software environments, cache files, logs and redundant downloaded ZIP containers. A file inventory records SHA-256 checksums.')

sources=[
('1','European Commission PVGIS','https://re.jrc.ec.europa.eu/pvg_tools/en/','Cached 5.2 NSRDB monthly outputs and TMY; building-integrated c-Si, 14% user losses.'),
('2','Open-Meteo historical weather API','https://open-meteo.com/en/docs/historical-weather-api','Retained ERA5 inputs and normal/recent temperature analysis.'),
('3','REC Alpha Pure-RX US datasheet','https://www.recgroup.com/sites/default/files/2026-03/DS_Alpha_Pure-RX_UL%20DC.pdf','470 W example; 68.0 × 47.4 in.; about 22.6% efficiency.'),
('4','Tesla Powerwall 3 US datasheet','https://energylibrary.tesla.com/docs/Public/EnergyStorage/Powerwall/3/Datasheet/en-us/Powerwall-3-Datasheet.pdf','13.5 kWh example; actual power ratings vary by configuration.'),
('5','IRS Residential Clean Energy Credit','https://www.irs.gov/credits-deductions/residential-clean-energy-credit','No homeowner credit for property placed in service after 2025.'),
('6','SDG&E Solar Billing Plan','https://www.sdge.com/solar/solar-billing-plan','Residential EV-TOU-5 and hourly export credits; CCA rules may differ.'),
('7','SDG&E Total Electric Rates','https://www.sdge.com/total-electric-rates','Cached August 1, 2026 bundled EV-TOU-5 table.'),
('8','SDG&E Extended Super Off-Peak Hours','https://www.sdge.com/fil/node/33521','Year-round weekday 10 a.m.–2 p.m. off-peak extension.'),
('9','SDG&E export pricing','https://www.sdge.com/solar/solar-billing-plan/export-pricing','2026 download and unresolved NBT00/NBT26 labeling.'),
('10','SDG&E Understanding Your Solar Bill','https://www.sdge.com/fil/node/25491','Annual surplus repricing and credit adjustment.'),
('11','Community Power Solar Battery Savings','https://sdcommunitypower.org/solar-battery-savings/','Conditional new-system rebate and enrollment terms.'),
('12','City of San Diego IB-301','https://www.sandiego.gov/development-services/forms-publications/information-bulletins/301','PV/ESS permitting and structural-work review.')]
for n in range(2):
 page(f'17 / Sources and supporting documents — {n+1}')
 for ident,title,url,note in sources[n*6:(n+1)*6]:
    p(f'[{ident}] <b>{title}</b>','BodyC');p(f'<link href="{html.escape(url)}" color="#167D9A">{html.escape(url)}</link>','SmallC');p(note,'SmallC')
 p('Official regulatory/product pages checked 15 September 2026 where cited. The retained cost allowances are not quotes. The model’s cached source records and acquisition URLs are preserved in the analysis archive.','SmallC')

legacy_notes={
'monthly-production.png':'Early 7–8 kW production illustration based on the older, larger solar face. Current 325 ft² roof capacity is lower.',
'bill-by-system.png':'Historical 30° battery comparison; curve retained for traceability. Current face cannot automatically fit the larger systems.',
'system-economics.png':'Historical capacity sweep with 401 ft² area gate. Replaced for roof-fit decisions by the current 325 ft² comparison.',
'monthly-energy-and-cost.png':'Historical demand backfill and 7 kW comparison; monthly bills precede full credit settlement.',
'temperature-fit.png':'Retained six-bill temperature fit and climate comparison. Calendar billing approximation remains provisional.',
'roof-angle-and-fit.png':'Historical fixed-footprint angle study using the older 401 ft² face. Do not use its area limit for the current roof.',
'south-post-solar-clerestory.png':'Current roof-study source. Its “active solar plane” label is reinterpreted here as gross face; cap projection/shading and usable module area remain unresolved.',
'west-elevation-roof-options.png':'Earlier massing alternatives retained to explain the design path; not the selected envelope.'}
for i,(src,dest) in enumerate(legacy,1):
 page(f'Appendix / Historical figure {i:02d}')
 p(src.name,'SmallC');image(dest.stem,legacy_notes.get(src.name,'Historical solar study.'),530)

def footer(can,doc):
    can.saveState();can.setStrokeColor(colors.HexColor('#c7d6dd'));can.line(54,42,558,42);can.setFont('Helvetica',8);can.setFillColor(colors.HexColor('#557080'));can.drawString(54,28,'SOL-001 • Rev 1 • Draft • 15 September 2026');can.drawRightString(558,28,str(doc.page));can.restoreState()
doc=SimpleDocTemplate(str(C/'solar-energy-report.pdf'),pagesize=(612,792),leftMargin=60,rightMargin=60,topMargin=48,bottomMargin=55,title='Chapter 8 — Solar, battery and roof design',author='Garage project design-development study')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(C/'solar-energy-report.md').write_text('# Chapter 8 — Solar, battery and roof design\n\nSOL-001 / Revision 1 / 2026-09-15 / draft\n\n'+'\n'.join(md))
(WORK/'page-titles.json').write_text(json.dumps(page_titles,indent=2))

# Auditable source set, including previous analyses and the current extension.
files=[]
for src in (ROOT/'solar-study').rglob('*'):
    if not src.is_file() or any(x.startswith('.') or x=='__pycache__' for x in src.relative_to(ROOT/'solar-study').parts):continue
    if src.suffix in ['.py','.json','.csv','.png','.pdf','.md','.txt','.gz'] and src.name not in ['analysis.log','environment-install.log']:files.append(src)
for src in (ROOT/'roof-options').glob('*'):
    if src.suffix in ['.py','.pdf','.png','.svg','.md']:files.append(src)
inventory=[]
with zipfile.ZipFile(C/'solar-analysis-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for src in sorted(set(files)):
    rel=str(src.relative_to(ROOT));z.write(src,rel);inventory.append([rel,src.stat().st_size,hashlib.sha256(src.read_bytes()).hexdigest()])
with (C/'source-inventory.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['source_path','bytes','sha256']);w.writerows(inventory)
print('Wrote report,',len(page_titles),'intended pages;',len(inventory),'source artifacts')
