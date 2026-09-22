"""Geometry option: mirror west primary side onto east primary roof line."""
import copy,json,math
import trim_roof_bracing as T
import owner_revisions as OR
import completion as C
OUT=T.OUT/'mirrored-east'
OUT.mkdir(exist_ok=True)

def build():
 f,s,g=T.build([])
 # Remove old east primary side. Outer east support line stays at x=247.5.
 for m in ['BE.upper','S3','E.clerestory','E.clerestory.lower','E.W3','E.W3.lower','N2','E.slope','E.top']:
  OR._drop(f,m)
 # Reuse all common roof/floor intersections; mirrored x=-34 becomes211.5.
 mapping={};pairs={}
 members={'W1':'S3','W2':'E.W2','W3':'E.W3','W4':'N2','BW':'BE.mirror','W.slope':'E.slope','W.top':'E.top','W.rear.brace':'E.rear.brace','BR-W-2':'BR-E-2'}
 for src in members:
  for m,i,j in list(f.segments):
   if m!=src:continue
   for n in (i,j):
    if n in mapping:continue
    v=f.nodes[n];xyz=(177.5-v['x'],v['y'],v['z'])
    match=next((k for k,q in f.nodes.items() if math.dist((q['x'],q['y'],q['z']),xyz)<1e-6),None)
    if match is None:
     # Insert floor intersections into cross-beams where needed.
     if abs(xyz[2]-112.5)<1e-6:
      for beam in ['B-SO','B-S','B-1','B-1A','B-2','B-N']:
       try:match=C._split(f,beam,xyz,'MIRROR.'+n);break
       except ValueError:pass
     if match is None:
      match='MIRROR.'+n
      f.nodes[match]=dict(x=xyz[0],y=xyz[1],z=xyz[2],support=v.get('support',False),members=[])
    f.nodes[match]['support']=v.get('support',False) or f.nodes[match].get('support',False)
    mapping[n]=match
 for src,dst in members.items():
  f.members[dst]=copy.deepcopy(f.members[src]);f.members[dst]['source_name']=dst
  f.section_of[dst]=f.section_of[src]
  for m,i,j in list(f.segments):
   if m==src:f.segments.append((dst,mapping[i],mapping[j]))
  f.unbraced_length_overrides[dst]=T.B.W.D.T.A.unbraced_lengths(f).get(src,f.member_length(src))
 # Preserve east slope seat links by coordinate reuse; loft/header intersections
 # all reuse existing nodes. Clean only after replacement members are present.
 T.B.W.D.T.clean(f)
 assert 'BE.upper' not in f.members
 for src,dst in members.items():assert abs(f.member_length(src)-f.member_length(dst))<1e-5
 info=dict(status='Geometry option; lean-to support decision pending; not analyzed',mirrored_members=members,new_ground_post=[211.5,185,0],primary_east_x=211.5,outer_east_x=247.5,unresolved_loads=f.extra_loads)
 return f,s,info
if __name__=='__main__':
 f,s,g=build()
 (OUT/'mirrored-east-geometry.json').write_text(json.dumps(dict(**g,nodes=f.nodes,segments=f.segments,sections={m:v.name for m,v in f.section_of.items()}),indent=2))
 print(json.dumps(g,indent=2))
