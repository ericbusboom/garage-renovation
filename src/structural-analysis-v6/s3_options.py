"""Bounded alternatives for S3; preserve ground-floor clearance."""
import copy
import s3_removal_study as T
import completion as C

def option(name):
    f,spec=T.reconstruct()
    if name.startswith('intended-'):
        for c in ['W1','W2']:T.CS.cut_ground_floor(f,c,112.5)
    T.CS.cut_ground_floor(f,'S3',112.5)
    if 'beam' in name:
        f.section_of['R-W1']=T.section('W14X22')
    if 'strut' in name:
        C._add_member(f,'S3.transfer','EF@-6','@211.5,3,147.355','HSS3X3X1/4',3,3,'Bracing',
                      note='Study: overhead diagonal transfers S3 upper joint to E-S3 at east wall')
    if 'stiff' in name:
        f.section_of['BR-W-2']=T.section('HSS3X3X3/16')
    return f,spec

if __name__=='__main__':
    for name in ['beam-stiff','strut-stiff','intended-beam-stiff','intended-strut-stiff']:
        f,spec=option(name);T.solve(name,f,spec)
