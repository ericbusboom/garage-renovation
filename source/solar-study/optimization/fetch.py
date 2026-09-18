import requests,json,concurrent.futures,pathlib,re,urllib.parse
D=pathlib.Path(__file__).parent/'data'
def get(name,url,params=None):
 p=D/name
 if p.exists(): return name+' cached'
 r=requests.get(url,params=params,timeout=180);r.raise_for_status();p.write_bytes(r.content);return name+' saved'
base=dict(lat=32.8,lon=-117.24,peakpower=1,loss=14,aspect=0,mountingplace='building',outputformat='json',usehorizon=0,raddatabase='PVGIS-NSRDB')
jobs=[(f'pv-{a}.json','https://re.jrc.ec.europa.eu/api/v5_2/PVcalc',dict(base,angle=a)) for a in range(0,46,5)]
jobs += [('weather.json','https://archive-api.open-meteo.com/v1/archive',dict(latitude=32.8,longitude=-117.24,start_date='1991-01-01',end_date='2026-08-31',daily='temperature_2m_mean',temperature_unit='fahrenheit',timezone='America/Los_Angeles',models='era5')),('tmy.json','https://re.jrc.ec.europa.eu/api/v5_2/tmy',dict(lat=32.8,lon=-117.24,outputformat='json',usehorizon=0,raddatabase='PVGIS-NSRDB'))]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for r in ex.map(lambda x:get(*x),jobs): print(r,flush=True)
for name,url,pattern in [('tariff','https://www.sdge.com/total-electric-rates',r'8/1/26.*?Current, Schedule EV-TOU-5$'),('exports','https://www.sdge.com/solar/solar-billing-plan/export-pricing',r'Current 2026 Export Pricing')]:
 h=requests.get(url,timeout=60).text
 for href,body in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',h,re.S):
  label=re.sub('<[^>]+>','',body).strip()
  if re.search(pattern,label):
   u=urllib.parse.urljoin(url,href);print(name,label,u,flush=True);get(name+('.pdf' if name=='tariff' else '.zip'),u);(D/(name+'-url.txt')).write_text(u);break
