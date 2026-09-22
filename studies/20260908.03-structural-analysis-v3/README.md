
## Truss-by-truss design and calculation review

<b>Revision 3: connected model with W-section trolley rails.</b> This package gives an explicit candidate geometry and member schedule for T-S, T1, T-E, T-W and T-N. It traces loads from the framing plan into each truss, records the controlling member checks, and tests lighter alternatives. It remains a preliminary first-order gravity design study, not a fabrication or construction design.

The model has a feasible local result under its selected screens: <b>7,495 lb</b> of primary steel plus a 10% connection-weight allowance, a highest strength screening ratio of <b>0.899</b>, and a largest service vertical movement of <b>0.730 inch</b>. This is approximately 1,738 lb (19%) below the prior 9,233 lb HSS study. Separating upper and lower chords, changing B2 end behavior and using W rails all changed this comparison; the savings cannot be attributed to one change alone.

Truss | Lower chord | Upper chord(s) | Webs / posts
T-S | HSS 2 x 2 x 1/8 | HSS 2 x 2 x 1/8 | HSS 2 x 2 x 1/8
T1 | W8X24 | HSS 2 x 2 x 1/8 | HSS 2.5 x 2.5 x 1/8
T-E | HSS 6 x 6 x 1/4 | HSS 2.5 x 2.5 x 1/8 | HSS 2.5 x 2.5 x 1/8
T-W | HSS 6 x 6 x 1/4 | HSS 6 x 6 x 1/4 | HSS 3 x 3 x 3/16
T-N | HSS 4 x 4 x 3/16 | HSS 3 x 3 x 3/16 | HSS 3 x 3 x 1/8
<b>B2 is W8X31, 8.00 inches actual depth. T1 remains a full truss with a W8X24 bottom chord, 7.93 inches deep.</b> W8X24 means nominal 8-inch depth and 24 lb/ft; the 24 is not a wall thickness. Both rails need actual trolley flange compatibility and local wheel-load checks before any lifting rating can be assigned.

The small T-S members are at the bottom of the tested catalogue, not proven absolute minima. Their low demand depends on roof purlins spanning east-west to T-W/T-E. Wind, facade detailing and connection fabrication can set substantially larger minimum sizes. All schedules in this report are conditional candidates.


### What this delivers, and what remains

Delivered: truss geometry with member IDs, load-path actions, trial sizes, compression/bending screens, moving-hoist gravity cases and a recorded lighter-section search. Remaining: site lateral loads and stability, bracing design, joint design, trolley local flange effects, cap collectors, column bases and foundations. These unresolved checks can invalidate the light sections shown here.


## 1. Top-down load path

Blue horizontal members are beams. Each colored perimeter line represents the full-height truss on its individual elevation sheet. No added gravity bearing is assigned to the existing walls, slab or cabinets. S1 is modeled but still has no upper-frame connection. S3 is assumed present.


## 2. Loads enter once, then transfer between members

Roof purlins are assumed to span east-west onto T-W and T-E. Floor joists span north-south onto T1, B2 and B3. The connected stiffness model then redistributes the reactions through the trusses, transfer beams and columns. A load transferred from B2 into T-E is not added again as building weight.

Group | Direct service load, lb | Sum of vertical actions from connected frame, lb
T-S | 566 | 566
T1 | 7,416 | 7,416
B2 | 11,856 | 11,856
B3 | 7,530 | 7,530
T-E | 11,609 | 11,609
T-W | 11,209 | 11,209
T-N | 2,072 | 2,072
Direct load includes the assigned roof/floor/wall load and the member group self-weight, for D + perimeter-storage live load + roof live load. Positive connection action is upward on the named group. Connection actions can include both upward and downward forces at different joints. The equality above is a group equilibrium check, not a statement that each truss carries the entire building.


### Load cases and trolley assumptions

The inherited floor is 284.98 sq ft, with 125 psf live load in 36-inch north/east/west storage bands and 40 psf elsewhere. Roof live load is 20 psf on horizontal projection. Dead allowances are 9 psf floor, 9.5 psf actual solar roof surface, 6.6 psf cap surface, 4 psf gross upper walls, and the balcony/guard allowances from revision 2. The new frame self-weight is recalculated for every trial.

A single operating trolley is tested on either B2 or T1 at nine positions, from x = 0 to 224.25 inches. Each position adds 1,350 lb downward: the confirmed 1,000 lb lifted load, a provisional 25% dynamic increment, and an assumed 100 lb trolley/hoist. This is a sampled position envelope, not a continuous moving-load proof. The actual equipment weight, wheel spacing, flange contact and dynamic requirements must replace these assumptions. Simultaneous use of two hoists is not included.

Service = D + storage + roof live, with and without each trolley position. Strength = 1.2D + 1.6 storage + 0.5 roof live, with trolley gravity factored 1.6; also 1.2D + storage + 1.6 roof live without trolley. These are selected study combinations, not the full legal design envelope. Full-area 125 psf and lateral cases from revision 2 are not requalified by this revision.


### Movement criterion

The search holds maximum absolute vertical movement at any model node to 0.75 inch. This is a study-wide tolerance, not an L/360 certification for every beam or a hoist manufacturer alignment limit. Maximum movement with the trolley is 0.730 inch; the no-trolley storage case is 0.726 inch. Member-relative deflection, floor vibration and machinery tolerances still need review.


## 3. How the member sizes are found

Each truss is kept as a complete connected assembly. Upper chords, lower chords and webs are sized as separate families, while the global model retains their common nodes. Changing a family changes both stiffness and self-weight, so the entire frame is solved again after every trial. The geometry itself is held fixed; this run is a section search, not a truss-topology optimization.

Start with the earlier feasible HSS study, replace B2 and the T1 lower chord with real W-section candidates, and release B2 end bending rotations to represent shear seats. B2 end torsion remains restrained and needs a real detail.

Increase families that fail the selected combined-force screen. Then test every lighter catalogue section in each family and accept the first one that keeps the whole frame within the strength and movement screens.

Repeat complete sweeps until no family can be reduced. Three sweeps were run; the final sweep accepted zero reductions. This is a coordinate-wise local stopping point. Simultaneous section swaps, different bracing or different panel geometry can produce a different result.


### Strength calculations used

Steel E = 29,000 ksi and specified Fy = 50 ksi. Compression uses r = sqrt(Imin/A), Fe = pi²E/(KL/r)², and Fcr = Fy(0.658)^(Fy/Fe) when Fy/Fe ≤ 2.25, otherwise 0.877Fe. Available compression Pc = 0.9 Fcr A; gross-section tensile yield Pt = 0.9 Fy A. Net-section fracture and connection rupture are not checked.

HSS elastic bending screens use 0.9 Fy S about each axis. W major-axis bending additionally uses AISC F2 lateral-torsional buckling with Cb = 1.0, capped at elastic yield. Slightly noncompact W flanges are conservatively capped at 0.9 × 0.7 Fy S rather than credited with plastic capacity. This is deliberately a screening implementation, not every AISC limit state.

Combined metric = max(Ncompression/Pc, Ntension/Pt) + |Mmajor|/Mc-major + |Mminor|/Mc-minor. A separate approximate shear-plus-torsion ratio is checked, and the larger value controls. The search limit is 0.90. This conservative linear metric is not a full AISC H1/H3 code check. All force values are first-order; no second-order stability reduction has been included.

<b>Required restraint assumptions:</b> K = 1; chords and W members have effective lateral/torsional brace spacing at most 72 inches, limited by their original member length; web members use their original full length; columns use 98.5 inches. Numerical subdivisions never shorten the assumed buckling length. Those brace points and their force/stiffness requirements have not been designed. W torsion uses Saint-Venant stiffness only; restrained warping and flange distortion remain unresolved.

Closed-form solver tests cover cantilever bending, axial extension, torsion, simple-span point loading, end releases, and distinct strong/weak W-section axes. Load-path recovery checks each member group equilibrium. These verify the calculation implementation at this level, not the physical assumptions.


## T-S — geometry and load transfer

Overall analytical span 246.50 in; maximum depth above wall-top line 44.37 in. Physical member IDs match the force table. Member lengths are analytical centerline lengths, not cut lengths. Joints, offsets and weld gaps remain to be detailed.

Role | Candidate | Governing screen | Case
lower | HSS 2 x 2 x 1/8 | 0.212 | strength T1@2/8
upper | HSS 2 x 2 x 1/8 | 0.244 | strength T1@2/8
web | HSS 2 x 2 x 1/8 | 0.272 | strength T1@2/8
The bottom arrows show only vertical interaction with adjacent framing in the no-trolley service case. Distributed direct loads are summarized in the title. Horizontal actions and joint moments also exist; connection-actions.csv contains all six components. A connection cannot be designed from the vertical arrows alone.


## T-S — member force and capacity checks

ID / role | Length in | Comp. / tens. kip | Major / minor M kip-ft | Ratio
M001 / lower | 246.5 | 0.09 / 0.00 | 0.36 / 0.02 | 0.212
M002 / upper | 246.5 | 0.25 / 0.00 | 0.40 / 0.02 | 0.244
M003 / web | 44.4 | 0.77 / 0.00 | 0.03 / 0.11 | 0.101
M004 / web | 44.4 | 0.00 / 0.08 | 0.00 / 0.08 | 0.045
M005 / web | 44.4 | 0.00 / 0.03 | 0.00 / 0.21 | 0.115
M006 / web | 44.4 | 0.00 / 0.03 | 0.00 / 0.37 | 0.205
M007 / web | 44.4 | 0.00 / 0.05 | 0.00 / 0.49 | 0.272
M008 / web | 44.4 | 0.00 / 0.18 | 0.02 / 0.24 | 0.152
M009 / web | 44.4 | 0.00 / 0.11 | 0.04 / 0.07 | 0.059
M010 / web | 60.5 | 0.15 / 0.00 | 0.08 / 0.01 | 0.057
M011 / web | 60.5 | 0.67 / 0.00 | 0.04 / 0.05 | 0.082
Each row reports the controlling sampled load case and finite-element segment within that physical member. Axial and moment components conservatively take the larger end value within that segment; they are not a single connection force vector. The CSV records the governing case, effective buckling length, capacities, shear and torsion for every row.


### Worked check: governing member in this truss

M007: HSS 2 x 2 x 1/8; governing case strength T1@2/8. Assumed effective buckling length 44.4 in. Available compression 29.47 kip, tensile yield 37.80 kip, major bending 1.82 kip-ft, minor bending 1.82 kip-ft.

Axial term = 0.001; major-bending term = 0.001; minor-bending term = 0.270. Sum = 0.272. Separate shear/torsion screen = 0.022. Governing metric = 0.272, against the study target 0.900. This conditional screen does not include joint capacity or second-order effects.


## T-S — why not make it lighter?

Family | Lighter trial | Saved lb | Global ratio | Global movement in
Each row changes only that family and then re-solves the entire connected building. The illustrated trial is the next lighter catalogue entry by weight; the full search also tested other lighter entries. A ratio above 0.900 or movement above 0.750 inch rejects the trial. A rejection can be caused by a different member because stiffness changes redistribute loads.

A missing role is already at the lightest candidate in the tested catalogue. That is a catalogue floor, not proof of a physical minimum and not a fabrication recommendation.

Selected T-S weight including 10% connection allowance: 258 lb.


### Connection actions to carry forward

Node | Connected group(s) | Vertical lb | Moment magnitude kip-ft
0 | T-W | +612 | 0.22
11 | S3, T-E | +56 | 0.18
13 | T-W | -500 | 0.02
24 | T-E | +40 | 0.14
36 | T-E | +358 | 0.07
These are service connection actions, included to expose the assumed transfer path. They are not a factored connection design schedule. The moment magnitude is for orientation only; connection design must use the signed component vectors and all governing combinations. Welds, gussets, bolts, HSS face yielding and local distortions remain unqualified.


## T1 — geometry and load transfer

Overall analytical span 224.25 in; maximum depth above wall-top line 84.64 in. Physical member IDs match the force table. Member lengths are analytical centerline lengths, not cut lengths. Joints, offsets and weld gaps remain to be detailed.

Role | Candidate | Governing screen | Case
lower | W8X24 | 0.446 | strength T1@0/8
upper | HSS 2 x 2 x 1/8 | 0.496 | strength T1@4/8
web | HSS 2.5 x 2.5 x 1/8 | 0.633 | strength T1@3/8
The bottom arrows show only vertical interaction with adjacent framing in the no-trolley service case. Distributed direct loads are summarized in the title. Horizontal actions and joint moments also exist; connection-actions.csv contains all six components. A connection cannot be designed from the vertical arrows alone.

T1 retains its full 84.64-inch truss depth. The W8X24 is only the lower chord/trolley rail. Open middle bays require moment-resisting joints; their lower chord is not assumed to act alone as a full-span simply supported beam.


## T1 — member force and capacity checks

ID / role | Length in | Comp. / tens. kip | Major / minor M kip-ft | Ratio
M012 / lower | 224.2 | 0.00 / 4.28 | 33.70 / 0.06 | 0.446
M013 / upper | 224.2 | 4.90 / 0.00 | 0.44 / 0.01 | 0.496
M014 / web | 84.6 | 1.74 / 0.00 | 0.02 / 0.40 | 0.204
M015 / web | 84.6 | 0.00 / 10.98 | 0.00 / 0.06 | 0.249
M016 / web | 84.6 | 0.00 / 0.12 | 0.00 / 0.27 | 0.094
M017 / web | 84.6 | 0.04 / 0.00 | 0.00 / 0.53 | 0.179
M018 / web | 84.6 | 0.00 / 0.05 | 0.00 / 0.62 | 0.208
M019 / web | 84.6 | 0.00 / 10.24 | 0.00 / 0.37 | 0.336
M020 / web | 84.6 | 0.00 / 1.70 | 0.01 / 0.15 | 0.089
M021 / web | 92.5 | 12.07 / 0.00 | 0.02 / 0.41 | 0.633
M022 / web | 92.5 | 11.51 / 0.00 | 0.03 / 0.17 | 0.534
Each row reports the controlling sampled load case and finite-element segment within that physical member. Axial and moment components conservatively take the larger end value within that segment; they are not a single connection force vector. The CSV records the governing case, effective buckling length, capacities, shear and torsion for every row.


### Worked check: governing member in this truss

M021: HSS 2.5 x 2.5 x 1/8; governing case strength T1@3/8. Assumed effective buckling length 92.5 in. Available compression 24.61 kip, tensile yield 48.15 kip, major bending 2.99 kip-ft, minor bending 2.99 kip-ft.

Axial term = 0.490; major-bending term = 0.007; minor-bending term = 0.136. Sum = 0.633. Separate shear/torsion screen = 0.006. Governing metric = 0.633, against the study target 0.900. This conditional screen does not include joint capacity or second-order effects.


## T1 — why not make it lighter?

Family | Lighter trial | Saved lb | Global ratio | Global movement in
lower | W6X20 | 82.2 | 0.919 | 0.732
web | HSS 2 x 2 x 1/8 | 60.6 | 1.024 | 0.731
Each row changes only that family and then re-solves the entire connected building. The illustrated trial is the next lighter catalogue entry by weight; the full search also tested other lighter entries. A ratio above 0.900 or movement above 0.750 inch rejects the trial. A rejection can be caused by a different member because stiffness changes redistribute loads.

A missing role is already at the lightest candidate in the tested catalogue. That is a catalogue floor, not proof of a physical minimum and not a fabrication recommendation.

Selected T1 weight including 10% connection allowance: 834 lb.


### Connection actions to carry forward

Node | Connected group(s) | Vertical lb | Moment magnitude kip-ft
38 | O2, T-W | +3,277 | 27.10
50 | T-E | +4,289 | 1.05
51 | T-W | -1,095 | 0.08
63 | T-E | +944 | 0.06
These are service connection actions, included to expose the assumed transfer path. They are not a factored connection design schedule. The moment magnitude is for orientation only; connection design must use the signed component vectors and all governing combinations. Welds, gussets, bolts, HSS face yielding and local distortions remain unqualified.


## T-E — geometry and load transfer

Overall analytical span 316.00 in; maximum depth above wall-top line 128.75 in. Physical member IDs match the force table. Member lengths are analytical centerline lengths, not cut lengths. Joints, offsets and weld gaps remain to be detailed.

Role | Candidate | Governing screen | Case
lower | HSS 6 x 6 x 1/4 | 0.784 | strength B2@0/8
upper | HSS 2.5 x 2.5 x 1/8 | 0.664 | strength roof
web | HSS 2.5 x 2.5 x 1/8 | 0.708 | strength T1@8/8
The bottom arrows show only vertical interaction with adjacent framing in the no-trolley service case. Distributed direct loads are summarized in the title. Horizontal actions and joint moments also exist; connection-actions.csv contains all six components. A connection cannot be designed from the vertical arrows alone.


## T-E — member force and capacity checks

ID / role | Length in | Comp. / tens. kip | Major / minor M kip-ft | Ratio
M047 / lower | 316.0 | 0.05 / 0.00 | 1.86 / 0.43 | 0.784
M048 / upper | 48.2 | 0.00 / 0.13 | 0.46 / 0.03 | 0.168
M049 / web | 52.7 | 0.00 / 1.19 | 0.11 / 0.04 | 0.072
M050 / upper | 24.5 | 0.00 / 1.23 | 0.52 / 0.03 | 0.206
M051 / web | 49.2 | 3.46 / 0.00 | 0.33 / 0.04 | 0.210
M052 / upper | 80.5 | 1.71 / 0.00 | 1.43 / 0.06 | 0.549
M053 / web | 109.7 | 12.65 / 0.00 | 0.07 / 0.03 | 0.708
M054 / upper | 65.0 | 9.97 / 0.00 | 1.03 / 0.10 | 0.664
M055 / web | 129.9 | 0.00 / 4.13 | 0.10 / 0.02 | 0.128
M056 / upper | 23.3 | 8.65 / 0.00 | 0.31 / 0.06 | 0.312
M057 / web | 130.3 | 0.00 / 3.76 | 0.10 / 0.06 | 0.131
M058 / upper | 38.9 | 6.47 / 0.00 | 0.73 / 0.04 | 0.408
M059 / web | 134.5 | 0.00 / 2.22 | 0.05 / 0.07 | 0.086
M060 / upper | 68.0 | 5.78 / 0.00 | 1.26 / 0.01 | 0.597
M061 / web | 145.6 | 0.00 / 14.21 | 0.07 / 0.20 | 0.386
M062 / web | 8.0 | 0.98 / 0.00 | 0.35 / 0.02 | 0.142
M063 / web | 32.1 | 1.33 / 0.00 | 0.17 / 0.06 | 0.108
M064 / web | 44.4 | 0.28 / 0.00 | 0.49 / 0.24 | 0.251
M065 / web | 84.6 | 0.00 / 1.70 | 0.01 / 0.15 | 0.089
M066 / web | 117.1 | 3.34 / 0.00 | 0.18 / 0.08 | 0.288
M067 / web | 128.8 | 0.83 / 0.00 | 0.08 / 0.05 | 0.106
M068 / web | 128.8 | 4.75 / 0.00 | 0.03 / 0.11 | 0.394
M069 / web | 128.8 | 4.52 / 0.00 | 0.18 / 0.56 | 0.580
Each row reports the controlling sampled load case and finite-element segment within that physical member. Axial and moment components conservatively take the larger end value within that segment; they are not a single connection force vector. The CSV records the governing case, effective buckling length, capacities, shear and torsion for every row.


### Worked check: governing member in this truss

M047: HSS 6 x 6 x 1/4; governing case strength B2@0/8. Assumed effective buckling length 72.0 in. Available compression 219.98 kip, tensile yield 235.80 kip, major bending 35.74 kip-ft, minor bending 35.74 kip-ft.

Axial term = 0.000; major-bending term = 0.052; minor-bending term = 0.012. Sum = 0.064. Separate shear/torsion screen = 0.784. Governing metric = 0.784, against the study target 0.900. This conditional screen does not include joint capacity or second-order effects.


## T-E — why not make it lighter?

Family | Lighter trial | Saved lb | Global ratio | Global movement in
lower | HSS 4 x 4 x 3/8 | 50.7 | 1.160 | 0.767
upper | HSS 2 x 2 x 1/8 | 27.1 | 1.019 | 0.731
web | HSS 2 x 2 x 1/8 | 111.0 | 1.370 | 0.733
Each row changes only that family and then re-solves the entire connected building. The illustrated trial is the next lighter catalogue entry by weight; the full search also tested other lighter entries. A ratio above 0.900 or movement above 0.750 inch rejects the trial. A rejection can be caused by a different member because stiffness changes redistribute loads.

Selected T-E weight including 10% connection allowance: 1,185 lb.


### Connection actions to carry forward

Node | Connected group(s) | Vertical lb | Moment magnitude kip-ft
11 | S3, T-S | +9,764 | 0.70
24 | T-S | -40 | 0.14
36 | T-S | -358 | 0.07
50 | T1 | -4,289 | 1.05
63 | T1 | -944 | 0.06
175 | T-SO | -47 | 0.16
177 | S2 | +2,821 | 0.56
185 | B2 | -5,928 | 0.00
188 | B3 | -3,846 | 10.42
189 | N2, T-N | +7,842 | 8.44
229 | T-N | +6,012 | 0.54
256 | T-N | +11 | 0.14
257 | T-N | +612 | 0.03
These are service connection actions, included to expose the assumed transfer path. They are not a factored connection design schedule. The moment magnitude is for orientation only; connection design must use the signed component vectors and all governing combinations. Welds, gussets, bolts, HSS face yielding and local distortions remain unqualified.


## T-W — geometry and load transfer

Overall analytical span 316.00 in; maximum depth above wall-top line 128.75 in. Physical member IDs match the force table. Member lengths are analytical centerline lengths, not cut lengths. Joints, offsets and weld gaps remain to be detailed.

Role | Candidate | Governing screen | Case
lower | HSS 6 x 6 x 1/4 | 0.778 | strength B2@0/8
upper | HSS 6 x 6 x 1/4 | 0.334 | strength B2@0/8
web | HSS 3 x 3 x 3/16 | 0.609 | strength B2@0/8
The bottom arrows show only vertical interaction with adjacent framing in the no-trolley service case. Distributed direct loads are summarized in the title. Horizontal actions and joint moments also exist; connection-actions.csv contains all six components. A connection cannot be designed from the vertical arrows alone.

The rear opening is deliberately untriangulated. Its frame action helps explain why T-W retains a much larger upper chord than T-E. Do not add diagonals through the balcony/door opening without an architectural revision.


## T-W — member force and capacity checks

ID / role | Length in | Comp. / tens. kip | Major / minor M kip-ft | Ratio
M023 / lower | 316.0 | 0.00 / 0.64 | 3.36 / 0.53 | 0.778
M024 / upper | 48.2 | 0.00 / 0.45 | 0.56 / 0.22 | 0.024
M025 / web | 52.7 | 0.00 / 0.77 | 0.03 / 0.12 | 0.033
M026 / upper | 24.5 | 0.00 / 1.45 | 0.37 / 0.26 | 0.024
M027 / web | 49.2 | 0.00 / 1.45 | 0.05 / 0.29 | 0.071
M028 / upper | 80.5 | 0.00 / 2.75 | 2.38 / 0.83 | 0.101
M029 / web | 109.7 | 0.00 / 2.92 | 0.03 / 0.16 | 0.067
M030 / upper | 88.2 | 0.00 / 3.55 | 2.54 / 0.73 | 0.107
M031 / web | 149.7 | 9.20 / 0.00 | 0.06 / 0.47 | 0.456
M032 / upper | 38.9 | 2.17 / 0.00 | 9.90 / 1.16 | 0.319
M033 / web | 134.5 | 0.00 / 2.20 | 0.05 / 0.60 | 0.132
M034 / upper | 1.0 | 1.40 / 0.00 | 10.63 / 1.10 | 0.334
M035 / upper | 60.0 | 1.40 / 0.00 | 10.44 / 1.07 | 0.328
M036 / upper | 7.0 | 0.61 / 0.00 | 3.71 / 0.46 | 0.119
M037 / web | 8.0 | 0.50 / 0.00 | 0.20 / 0.34 | 0.093
M038 / web | 32.1 | 1.13 / 0.00 | 0.13 / 0.42 | 0.103
M039 / web | 44.4 | 1.72 / 0.00 | 0.13 / 0.56 | 0.135
M040 / web | 84.6 | 3.07 / 0.00 | 0.06 / 0.98 | 0.223
M041 / web | 128.8 | 0.00 / 1.30 | 0.20 / 0.70 | 0.160
M042 / web | 128.8 | 0.00 / 1.57 | 0.50 / 0.94 | 0.252
M043 / web | 128.8 | 0.00 / 1.76 | 1.25 / 0.93 | 0.376
M044 / web | 128.8 | 0.00 / 3.16 | 2.00 / 0.98 | 0.522
M045 / web | 128.8 | 4.26 / 0.00 | 2.37 / 0.60 | 0.609
M046 / web | 60.0 | 0.00 / 0.34 | 1.86 / 0.01 | 0.309
Each row reports the controlling sampled load case and finite-element segment within that physical member. Axial and moment components conservatively take the larger end value within that segment; they are not a single connection force vector. The CSV records the governing case, effective buckling length, capacities, shear and torsion for every row.


### Worked check: governing member in this truss

M023: HSS 6 x 6 x 1/4; governing case strength B2@0/8. Assumed effective buckling length 72.0 in. Available compression 219.98 kip, tensile yield 235.80 kip, major bending 35.74 kip-ft, minor bending 35.74 kip-ft.

Axial term = 0.003; major-bending term = 0.094; minor-bending term = 0.015. Sum = 0.112. Separate shear/torsion screen = 0.778. Governing metric = 0.778, against the study target 0.900. This conditional screen does not include joint capacity or second-order effects.


## T-W — why not make it lighter?

Family | Lighter trial | Saved lb | Global ratio | Global movement in
lower | HSS 4 x 4 x 3/8 | 50.7 | 1.110 | 0.756
upper | HSS 4 x 4 x 3/8 | 55.9 | 1.013 | 0.732
web | HSS 2.5 x 2.5 x 3/16 | 160.6 | 0.934 | 0.742
Each row changes only that family and then re-solves the entire connected building. The illustrated trial is the next lighter catalogue entry by weight; the full search also tested other lighter entries. A ratio above 0.900 or movement above 0.750 inch rejects the trial. A rejection can be caused by a different member because stiffness changes redistribute loads.

Selected T-W weight including 10% connection allowance: 2,020 lb.


### Connection actions to carry forward

Node | Connected group(s) | Vertical lb | Moment magnitude kip-ft
0 | T-S | -612 | 0.22
13 | T-S | +500 | 0.02
38 | O2, T1 | +9,190 | 2.58
51 | T1 | +1,095 | 0.08
91 | T-SO | +89 | 0.32
101 | B2, O3 | -4,211 | 2.33
106 | B3 | -3,683 | 9.23
107 | T-N | +374 | 8.28
145 | T-N | +1,970 | 0.88
171 | T-N | +2,322 | 0.29
172 | T-N | +4,174 | 0.18
These are service connection actions, included to expose the assumed transfer path. They are not a factored connection design schedule. The moment magnitude is for orientation only; connection design must use the signed component vectors and all governing combinations. Welds, gussets, bolts, HSS face yielding and local distortions remain unqualified.


## T-N — geometry and load transfer

Overall analytical span 281.50 in; maximum depth above wall-top line 128.75 in. Physical member IDs match the force table. Member lengths are analytical centerline lengths, not cut lengths. Joints, offsets and weld gaps remain to be detailed.

Role | Candidate | Governing screen | Case
lower | HSS 4 x 4 x 3/16 | 0.662 | strength B2@0/8
upper | HSS 3 x 3 x 3/16 | 0.436 | strength B2@0/8
web | HSS 3 x 3 x 1/8 | 0.523 | strength B2@8/8
The bottom arrows show only vertical interaction with adjacent framing in the no-trolley service case. Distributed direct loads are summarized in the title. Horizontal actions and joint moments also exist; connection-actions.csv contains all six components. A connection cannot be designed from the vertical arrows alone.

The door interrupts triangulation below the upper band. The middle horizontal line and upper band are both in the upper-chord family. Portal-frame joint action around the opening has not been fabricated or verified.


## T-N — member force and capacity checks

ID / role | Length in | Comp. / tens. kip | Major / minor M kip-ft | Ratio
M070 / lower | 281.5 | 0.03 / 0.00 | 7.67 / 0.04 | 0.662
M071 / upper | 281.5 | 6.10 / 0.00 | 0.42 / 0.97 | 0.436
M072 / upper | 281.5 | 0.00 / 9.60 | 0.82 / 0.29 | 0.292
M073 / web | 128.8 | 7.62 / 0.00 | 0.63 / 0.07 | 0.474
M074 / web | 128.8 | 5.79 / 0.00 | 0.35 / 0.45 | 0.420
M075 / web | 128.8 | 2.08 / 0.00 | 0.18 / 0.21 | 0.173
M076 / web | 128.8 | 0.00 / 1.43 | 0.10 / 0.15 | 0.080
M077 / web | 128.8 | 5.49 / 0.00 | 0.32 / 1.00 | 0.523
M078 / web | 128.8 | 3.36 / 0.00 | 0.08 / 0.21 | 0.205
M079 / web | 24.0 | 0.38 / 0.00 | 0.29 / 0.43 | 0.168
M080 / web | 42.6 | 10.77 / 0.00 | 0.51 / 0.47 | 0.424
M081 / web | 24.0 | 0.00 / 2.94 | 0.77 / 0.45 | 0.324
M082 / web | 42.6 | 9.44 / 0.00 | 0.05 / 0.53 | 0.307
M083 / web | 24.0 | 0.00 / 1.21 | 0.13 / 0.72 | 0.211
M084 / web | 42.6 | 0.00 / 4.89 | 0.52 / 0.07 | 0.215
M085 / web | 24.0 | 1.39 / 0.00 | 0.05 / 0.14 | 0.067
M086 / web | 42.6 | 0.00 / 3.13 | 0.12 / 0.08 | 0.099
M087 / web | 24.0 | 0.24 / 0.00 | 0.03 / 0.21 | 0.057
M088 / web | 42.6 | 0.90 / 0.00 | 0.18 / 0.03 | 0.065
M089 / web | 24.0 | 0.00 / 0.09 | 0.01 / 0.02 | 0.009
M090 / web | 42.6 | 0.00 / 0.65 | 0.01 / 0.01 | 0.016
M091 / web | 24.0 | 0.00 / 0.06 | 0.01 / 0.02 | 0.008
M092 / web | 42.6 | 0.74 / 0.00 | 0.09 / 0.05 | 0.046
M093 / web | 24.0 | 0.29 / 0.00 | 0.15 / 0.13 | 0.067
M094 / web | 42.6 | 4.19 / 0.00 | 0.31 / 0.08 | 0.166
M095 / web | 32.0 | 0.15 / 0.00 | 0.08 / 0.01 | 0.022
Each row reports the controlling sampled load case and finite-element segment within that physical member. Axial and moment components conservatively take the larger end value within that segment; they are not a single connection force vector. The CSV records the governing case, effective buckling length, capacities, shear and torsion for every row.


### Worked check: governing member in this truss

M070: HSS 4 x 4 x 3/16; governing case strength B2@0/8. Assumed effective buckling length 72.0 in. Available compression 99.18 kip, tensile yield 116.10 kip, major bending 11.66 kip-ft, minor bending 11.66 kip-ft.

Axial term = 0.000; major-bending term = 0.658; minor-bending term = 0.004. Sum = 0.662. Separate shear/torsion screen = 0.187. Governing metric = 0.662, against the study target 0.900. This conditional screen does not include joint capacity or second-order effects.


## T-N — why not make it lighter?

Family | Lighter trial | Saved lb | Global ratio | Global movement in
lower | HSS 3 x 3 x 1/4 | 15.7 | 0.860 | 0.811
upper | HSS 2.5 x 2.5 x 3/16 | 66.1 | 0.909 | 0.733
web | HSS 2 x 2 x 3/16 | 52.7 | 1.017 | 0.740
Each row changes only that family and then re-solves the entire connected building. The illustrated trial is the next lighter catalogue entry by weight; the full search also tested other lighter entries. A ratio above 0.900 or movement above 0.750 inch rejects the trial. A rejection can be caused by a different member because stiffness changes redistribute loads.

Selected T-N weight including 10% connection allowance: 1,180 lb.


### Connection actions to carry forward

Node | Connected group(s) | Vertical lb | Moment magnitude kip-ft
107 | T-W | -374 | 8.28
145 | T-W | -1,970 | 0.88
171 | T-W | -2,322 | 0.29
172 | T-W | -4,174 | 0.18
189 | N2, T-E | +6,856 | 6.39
229 | T-E | -6,012 | 0.54
256 | T-E | -11 | 0.14
257 | T-E | -612 | 0.03
258 | B-WO, W4 | +3,719 | 0.22
262 | N1 | +6,973 | 0.64
These are service connection actions, included to expose the assumed transfer path. They are not a factored connection design schedule. The moment magnitude is for orientation only; connection design must use the signed component vectors and all governing combinations. Welds, gussets, bolts, HSS face yielding and local distortions remain unqualified.


## B2 and the trolley rails

Rail | Candidate | Actual depth | Screen ratio
B2 | W8X31 | 8.00 in | 0.606
T1 lower chord | W8X24 | 7.93 in | 0.446
B2 is a beam and T1 is a truss. B2 uses end bending releases to model shear seats; torsional restraint remains assumed. T1 lower chord remains connected to its posts, diagonal end bays and upper chord. The rest of T1 participates in carrying the trolley and floor loads.

Nine loaded positions were checked on each rail, one trolley at a time. The position label @3/8 means three-eighths of the way from the west end. Moving load is applied on the rail centerline for vertical global analysis. Wheel spacing, unequal wheel loads, longitudinal acceleration, lateral force, flange-local bending, web tension and restrained warping are not resolved by that idealization.

<b>No 1,000 lb lifting rating is established by these results.</b> The actual trolley specification is needed to check flange fit, wheel contact and the relevant hoist standard/dynamic factors. Both the full building load and the moving load must be retained in the final checks. Bolted splices, end stops and stiffeners must preserve trolley travel.


### Whole-frame reactions remain important

Column | Service storage reaction, lb
W1 | 249
W2 | 12,648
W3 | 2,260
W4 | 4,116
S1 | 85
S2 | 2,906
N1 | 7,058
N2 | 14,783
S3 | 9,905
These revised reactions supersede the earlier values only for this conditional configuration. Columns remain 4 x 4 x 3/16 HSS trial members. Axial capacity alone does not establish column or footing adequacy. The assumed rigid bases and bracing have not been verified.


## Remaining engineering and reproducibility

The geometry still contains architectural-line approximations at joints, rather than fully detailed section-centroid offsets. Upper HSS chord sizes as small as 2 inches may be impractical when connected to the much larger lower chords. Cost, weld access, tube-face capacity and required bracing can make a heavier but simpler truss preferable.

This revision does not optimize geometry, connection weight or purlin profiles. Roof purlin routing is assumed, and the hip-cap rafters and collectors are represented only by loads. The frame is not a complete lateral-force-resisting system. Wind, seismic, rain/ponding, second-order effects, diaphragm actions, uplift connections and foundation capacity must be checked before members are finalized.

The recorded stopping point is local and conditional. It answers “what lighter members survive these explicit gravity screens in this connected model?” It does not answer “what is the lightest safe building?” That latter answer requires the unresolved physical details and site design loads.


### Files and commands

engineer.py builds the revised connected model, performs the grouped section search and writes results.json. geometry_builder.py preserves the prior geometry and load routing. frame_solver.py now distinguishes W-section strong and weak axes. Run verify.py for benchmarks; run engineer.py, then detail.py for member IDs, CSVs and figures; run report.py with ReportLab to produce this document. NumPy, SciPy and Matplotlib are needed for the calculation/figures.

Inputs are frozen under inputs/. The prior HSS starting selection is stored as baseline-selection.json. Physical member lengths and coordinates are in physical-members.json; individual demand/capacity data are in member-checks.csv; signed service joint actions are in connection-actions.csv; the complete section-search history and lighter trials are in results.json. The source ZIP includes the AISC catalogue download used for the W data.


### Primary references

<link href="https://www.aisc.org/aisc/publications/steel-construction-manual/aisc-shapes-database-v160/" color="#176986">AISC Shapes Database v16.0</link>

<link href="https://cloud.aisc.org/biggie_bin/aisc-shapes-database-v160-2.xlsx" color="#176986">Official AISC spreadsheet downloaded for this study</link>

<link href="https://www.atlastube.com/wp-content/uploads/2018/04/A500-Square-Current.pdf" color="#176986">Atlas square HSS properties</link>

<link href="https://www.aisc.org/globalassets/aisc/publications/standards/a360-16w-rev-june-2019.pdf" color="#176986">AISC specification formula reference, E3 and F2</link>

<link href="https://www.aisc.org/globalassets/modern-steel/steel-interchange/2005/2005v02_si_web.pdf" color="#176986">AISC discussion of bottom-flange loading and hoist impact</link>

<link href="https://www.sandiego.gov/development-services/codes-regulations" color="#176986">San Diego adopted codes</link>

The cited formula reference and diagnostic load assumptions do not establish compliance with the currently adopted California code. A licensed structural engineer must reconcile the final design basis, details and applicable standards before construction.
