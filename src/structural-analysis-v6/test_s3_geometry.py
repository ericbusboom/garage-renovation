"""Regressions for raised-floor column deletion and load-plane placement."""
import copy
import unittest
import s3_removal_study as T
import surfaces
from types import SimpleNamespace

class RaisedFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.frame,cls.spec=T.reconstruct()
    def test_load_planes_follow_roof_and_floor(self):
        ss=surfaces.build_surfaces(self.frame,self.spec['parameters'])
        self.assertAlmostEqual(ss['solar_roof'].origin[2],120.25)
        self.assertAlmostEqual(ss['solar_roof'].slope_deg,30,places=3)
        self.assertAlmostEqual(ss['upper_roof'].origin[2],233.25)
        for s in ss.values():
            if s.kind=='floor':self.assertAlmostEqual(s.origin[2],112.5)
        for m,i,j in self.frame.segments:
            if m.startswith('RS @'):
                for n in [i,j]:self.assertLess(abs(ss['solar_roof'].offset(self.frame.xyz(n))),1e-5)
    def test_wrong_cut_height_rejected(self):
        f=copy.deepcopy(self.frame)
        with self.assertRaises(ValueError): T.CS.cut_ground_floor(f,'S3',104.5)
        self.assertEqual(f.segments,self.frame.segments)
    def test_raised_columns_really_removed(self):
        f=copy.deepcopy(self.frame)
        for m in ['W1','W2','S3']:
            note=T.CS.cut_ground_floor(f,m,112.5)
            self.assertEqual(note['segments_cut'],1)
            self.assertNotIn(m+'.base',f.nodes)
            self.assertTrue(all(min(f.xyz(i)[2],f.xyz(j)[2])>=112.5 for mm,i,j in f.segments if mm==m))
        T.clean(f)
        model,index=T.F.build(f)
        for n in ['W1.base','W2.base','S3.base']:self.assertNotIn(n,model.nodes)
    def test_reaction_envelope_signs(self):
        node=SimpleNamespace(name='base', support_DY=True,
            RxnFY={'gravity':12000.,'wind':-1500.},
            RxnFX={'gravity':0.,'wind':300.}, RxnFZ={'gravity':0.,'wind':400.})
        r=T.A._reactions(SimpleNamespace(nodes={'base':node}),['gravity','wind'])['base']
        self.assertEqual(r['max_compression'],12000.)
        self.assertEqual(r['max_uplift'],1500.)
        self.assertEqual(r['max_shear'],500.)

if __name__=='__main__':unittest.main()
