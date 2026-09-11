# S2 reaction audit

The bottom chord is horizontal. There is no unsupported end overhang needed to generate this reaction. My earlier seesaw/cantilever explanation was incomplete: the relevant mechanism in this model is a continuous, three-support frame with strongly unequal adjacent spans.

## What was checked

- S2 at y=-63 in, S3 at y=0, N2 at y=253 in. The bottom chord is at z=115 in along its whole length.
- S2 connects to TE bottom chord, TE top chord and T-SO. S3 connects to both TE chords and TS. N2 connects to both TE chords and TN with an explicit 4-inch north offset.
- The model assumes continuity through S3 and connections capable of transmitting the modeled forces. Those details were not yet engineered.
- Load directions use global vertical FY, with CAD height mapped to solver Y. Reaction signs and global force/moment equilibrium were checked.
- Gravity loads were run separately. S2 contribution (lb): {'Dsteel': -1313.7, 'Dfloor': -1173.4, 'Droof': -1301.7, 'Dwall': -510.0, 'L40': -3911.3, 'R20': -3229.8}.
- Sum: -11,439.9 lb at S2, reproducing the prior service40 result.
- Removing S3 as a diagnostic, while retaining the remaining geometry and loads apart from its own weight, changes S2 to 9,667.3 lb downward bearing. This is not a proposal to remove S3 and no CAD columns were removed.
- Releasing column-base rotations or web-end bending leaves the uplift present. Those releases do not interrupt the continuous chords through S3.

## Independent check

A completely flat, constant-stiffness beam on three supports, with 63-inch and 253-inch spans and no overhang, also develops an upward-pull demand at its first support under uniform downward loading. At 1 lb/in, the classical three-moment equation gives reactions -71.752, 286.963, 100.789 lb. The independent PyNite beam reproduces those numbers to better than 1e-8 lb.

For two separate simply supported spans instead, the same loads give 31.5, 158 and 126.5 lb: all downward-bearing loads on the foundations. This is a different connection/continuity arrangement, not a solver setting to change merely to remove an undesirable result.

## Conclusion

I did not find a flipped load, sloping bottom chord, or required cantilever that explains away the reaction. The reaction is reproducible within the continuous-frame assumption. Its magnitude is not established for the intended construction until the TE/S3 connection arrangement is settled. Treat the 11.4 kip as a conditional analytical result, not a footing design requirement.

The next meaningful comparison is a deliberately detailed TE arrangement that either preserves continuity through S3 or divides the structural action into independent spans. Releasing an individual web or column base is not equivalent to that change.

Solver API conventions checked against [PyNite documentation](https://pynite.readthedocs.io/en/latest/FEModel3D.html). All numerical results above are calculations in this project, not values from that documentation.
