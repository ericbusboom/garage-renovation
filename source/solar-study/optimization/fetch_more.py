import concurrent.futures,requests,pathlib,json
D=pathlib.Path(__file__).parent/'data'
b=dict(lat=32.8,lon=-117.24,peakpower=1,loss=14,mountingplace='building',outputformat='json',usehorizon=0,raddatabase='PVGIS-NSRDB')
jobs=[(a,0) for a in [11,12,13,14,16,17]]+[(15,a) for a in [-60,-30,30,60]]
def f(x):
 a,z=x;p=D/f'pv-{a}-az{z}.json'
 if not p.exists():
  r=requests.get('https://re.jrc.ec.europa.eu/api/v5_2/PVcalc',params=dict(b,angle=a,aspect=z),timeout=180);r.raise_for_status();p.write_text(r.text)
 j=json.loads(p.read_text());return a,z,j['outputs']['monthly']['fixed'][7]['E_m']
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:
 for r in e.map(f,jobs):print(r,flush=True)
