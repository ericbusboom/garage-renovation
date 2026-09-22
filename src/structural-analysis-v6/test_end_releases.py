import unittest
from pathlib import Path
import frame as F
import sections as S
class EndReleaseTests(unittest.TestCase):
 def test_both_explicit_pins_survive(self):
  f=F.Frame(path=Path('test'),version='test',nodes={'a':dict(x=0,y=0,z=0,support=True),'b':dict(x=120,y=0,z=0,support=True)},segments=[('beam','a','b')],members={'beam':dict(group='Beams',material='steel')},section_of={'beam':S.get('W12X16')},pinned_ends=[('beam','a'),('beam','b')])
  model,index=F.build(f);flags=model.members[index['beam'][0]].Releases
  self.assertTrue(all(flags[k] for k in (4,5,10,11)))
 def test_single_element_brace_has_two_pinned_ends(self):
  f=F.Frame(path=Path('test'),version='test',nodes={'a':dict(x=0,y=0,z=0,support=True),'b':dict(x=120,y=0,z=120,support=True)},segments=[('brace','a','b')],members={'brace':dict(group='Bracing',material='steel')},section_of={'brace':S.hss_square(3,.25)})
  model,index=F.build(f);flags=model.members[index['brace'][0]].Releases
  self.assertTrue(all(flags[k] for k in (4,5,9,10,11)))
if __name__=='__main__':unittest.main()
