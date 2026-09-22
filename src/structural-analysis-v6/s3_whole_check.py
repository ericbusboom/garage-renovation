import s3_removal_study as T
from s3_followup import whole

def whole_option():
    f,s=whole()
    for m in ['N2','W1','E-S3','E-N2']:
        f.section_of[m]=T.section('HSS6X6X1/4')
    f.section_of['shelf SH joist 15']=T.S.sawn_lumber('double 2x8 DF-L No.2',3,7.25)
    return f,s

if __name__=='__main__':
    f,s=whole_option();T.solve('whole-s3-pdelta',f,s,second_order=True)
