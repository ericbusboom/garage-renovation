# Ground-supported truss views

TN now has one horizontal top chord at 224.25 in (18 ft 8 1/4 in) above datum.
The hip-cap roof remains separate; its roof load allowance is retained.
N1 / U-W is the existing full-height ground column beside the loading door.
The upper east jamb bears on TN; no ground column is added in the garage opening.

Columns appear in multiple wall views but occur ONCE in the global model.
Shared posts carry combined actions; reactions are not arbitrarily divided in half.
T1 is supported by TE and TW, not by new ground columns beneath T1.
All wall images are native PyNite views filtered from the solved global model.
They are not independently solved frames with invented supports at cut edges.

Model assumptions: fixed bases, moment-connected frame members and offset links.
The nine foundations, connections and site wind/seismic loads still need design.
This is a preliminary analytical model, not a construction-ready design.

Open Grounded-Truss-Walls.pdf or the interactive HTML views.
complete.network.json and roof_first.network.json contain the entire unique global network, real ground supports, applied loads and reference displacements/reactions.
Run verify_and_draw.py with the parent requirements-lock-macos.txt runtime to replay and render. update_and_solve.py requires the parent project solver and catalog.

column-reactions.csv contains global linear reactions; global-complete-PDelta.json contains the second-order analysis and partial member screens. All results are preliminary.
