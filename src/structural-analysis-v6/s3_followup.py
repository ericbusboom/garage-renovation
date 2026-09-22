import copy
import s3_removal_study as T
import s3_options as O

def whole():
    f,spec=T.reconstruct();T.OR._drop(f,'S3')
    for m,sec in {'BE':'W14X22','R-W1':'W14X22','RS @ 170.58':'HSS3X3X1/8','BR-W-2':'HSS3X3X3/16',
                  'E.clerestory.lower':'HSS4X4X1/4','E.W3.lower':'HSS4X4X1/4',
                  'E.clerestory':'HSS4X4X1/4','E.W3':'HSS4X4X1/4'}.items():f.section_of[m]=T.section(sec)
    return f,spec

if __name__=='__main__':
    f,s=O.option('beam');T.solve('beam-only',f,s)
    f,s=O.option('beam-stiff');T.solve('beam-stiff-pdelta',f,s,second_order=True)
    f,s=whole();T.solve('whole-s3-strengthened',f,s)
