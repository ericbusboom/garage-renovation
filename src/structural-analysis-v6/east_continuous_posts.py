"""Continuous east posts with a smaller lean-to support beam."""
import json,sys
import trim_roof_bracing as T
import completion as C
import owner_revisions as OR
OUT=T.OUT/'continuous-east-posts'
OUT.mkdir(exist_ok=True)
def build(section='W6X8.5', simple=False, reinforced=False):
 f,s,g=T.build([])
 pairs=[('E.clerestory','E.clerestory.lower','B-1'),('E.W3','E.W3.lower','B-2')]
 for upper,lower,beam in pairs:
  assert f.section_of[upper].name==f.section_of[lower].name
  f.segments=[(upper if m==lower else m,i,j) for m,i,j in f.segments]
  f.members.pop(lower);f.section_of.pop(lower)
  f.members[upper]['section_status']='Continuous post from loft beam to roof top; no splice at lean-to beam'
 T.B.W.D.T.clean(f)
 oldsec=f.section_of['BE.upper'];newsec=T.B.W.D.T.section(section)
 # Keep the lean-to bearing top at its established elevation. The smaller
 # section axis rises, with separate beam joints along the continuous posts.
 ends=sorted({n for m,i,j in f.segments if m=='BE.upper' for n in(i,j)},key=lambda n:f.xyz(n)[1])
 xyz=[f.xyz(n) for n in ends]
 OR._drop(f,'BE.upper')
 posts=['S3','E.clerestory','E.W3','N2'];newnodes=[]
 for post,p in zip(posts,xyz):
  target=(p[0],p[1],p[2]+(oldsec.d-newsec.d)/2)
  newnodes.append(C._split(f,post,target,'BE.small@'+str(p[1])))
 for i,j in zip(newnodes,newnodes[1:]):
  if 'BE.upper' not in f.members:C._add_member(f,'BE.upper',i,j,section,newsec.b,newsec.d,'Beams',note='Smaller lean-to support beam; original top bearing elevation retained')
  else:f.segments.append(('BE.upper',i,j))
 if simple:
  for upper,lower,beam in pairs:f.section_of[upper]=T.B.W.D.T.section('HSS5X5X1/4')
  f.pinned_ends.extend(('BE.upper',n) for n in newnodes)
 # Full post height used conservatively; no lateral support credited merely
 # because the small lean-to beam intersects it.
 for upper,lower,beam in pairs:f.unbraced_length_overrides[upper]=f.member_length(upper)
 if reinforced:
  f.section_of['E.top']=T.B.W.D.T.section('HSS4X4X1/4')
  f.section_of['BE']=T.B.W.D.T.section('W14X22')
 T.B.W.D.T.clean(f)
 for upper,lower,beam in pairs:
  assert lower not in f.members
  nodes={n for m,i,j in f.segments if m==upper for n in(i,j)}
  bottom=min(nodes,key=lambda n:f.xyz(n)[2])
  assert beam in f.nodes[bottom]['members'],(upper,beam,f.nodes[bottom])
  assert min(f.xyz(n)[2] for n in nodes)==112.5 and max(f.xyz(n)[2] for n in nodes)==236.75
 assert len([v for v in f.extra_loads if v[0]=='BE.upper'])==2
 return f,s,dict(section=section,simple_spans=simple,reinforced=reinforced,posts=[p[0] for p in pairs],post_section=f.section_of['E.W3'].name,post_height=124.25,beam_axis_raise=(oldsec.d-newsec.d)/2,lean_to_loads=f.extra_loads)
def run(section,simple=False,reinforced=False):
 f,s,g=build(section,simple,reinforced);tag=section.lower().replace('.','p').replace('/','-')+('-simple' if simple else '')+('-reinforced' if reinforced else '')
 T.B.W.D.T.OUT=OUT
 r=T.B.W.D.T.solve(tag,f,s,second_order=True)
 (OUT/(tag+'-geometry.json')).write_text(json.dumps(dict(**g,nodes=f.nodes,segments=f.segments,sections={m:v.name for m,v in f.section_of.items()}),indent=2))
 return r
if __name__=='__main__':run(sys.argv[1] if len(sys.argv)>1 else 'W6X8.5',len(sys.argv)>2 and sys.argv[2]=='simple',len(sys.argv)>3 and sys.argv[3]=='reinforced')
