import json
from run_analysis import analyze,P,FEModel3D
out=[]
for name,kw in [('sources_baseline',{}),('sources_without_S3',{'remove':['S3']}),('sources_base_pinned',{'base_pinned':True}),('sources_web_pinned',{'web_pinned':True})]:
 r=analyze(name,diagnostic=True,**kw);out.append(r)
 (P/'s2-investigation.json').write_text(json.dumps(out,indent=2,default=lambda x:float(x)))
 print(name,r['status'],{k:{s:round(v,1) for s,v in r0['reactions_lb'].items() if s in ['S2','S3','N2']} for k,r0 in r.get('results',{}).items()},flush=True)
# Independent flat, continuous three-support beam with no overhang.
# Uniform 1 lb/in on entire 316-inch length, pinned vertical supports at 0,63,316.
m=FEModel3D();m.add_material('S',29e6,29e6/2.6,.3,0);m.add_section('S',10,100,100,1)
for name,x in [('A',0),('B',63),('C',316)]:m.add_node(name,x,0,0);m.def_support(name,name=='A',True,True,name=='A',False,False)
m.add_member('AB','A','B','S','S');m.add_member('BC','B','C','S','S')
for k in ['AB','BC']:m.add_member_dist_load(k,'FY',-1,-1,case='U')
m.add_load_combo('U',{'U':1});m.analyze_linear()
r={n:v.RxnFY['U'] for n,v in m.nodes.items()};print('Flat continuous beam reactions',r,flush=True)
(P/'s2-independent-beam.json').write_text(json.dumps({'description':'Flat constant-EI beam, 63-inch and 253-inch spans, no overhang, uniform 1 lb/in. Not garage model; demonstrates possible reaction sign.', 'reactions_lb':r},indent=2))
