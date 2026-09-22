import s3_removal_study as T
import s3_options as O

def final_frame(intended=False):
    f,s=O.option(('intended-' if intended else '')+'beam-stiff')
    # Two adjacent 2x8s, equal sharing, combined b=3 in and unchanged depth.
    f.section_of['shelf SH joist 15']=T.S.sawn_lumber('double 2x8 DF-L No.2',3.0,7.25)
    return f,s

if __name__=='__main__':
    f,s=final_frame();T.solve('s3-clear-floor-pdelta',f,s,second_order=True)
    f,s=final_frame(True);T.solve('w1-w2-s3-clear-floor-pdelta',f,s,second_order=True)
