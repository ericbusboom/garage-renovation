# TN door mini-truss correction

TN over-door mini-truss correction

The bottom chord/header now runs level between the support axes.
Four equal 25.5-inch panels span 102 inches (8 ft 6 in) between those axes.
Chord axes are at 207 and 224.25 inches above datum: 17.25 inches apart.
These are structural centerline dimensions, not the clear finished door opening.

All mini-truss diagonals and verticals now terminate exactly on chord nodes.
The east upper jamb reaches the upper chord. The short sloping header-end
connection that caused the visible uptick has been removed.

N1 / U-W is 3.5 inches north of the TN plane. Its connection is an explicit
out-of-plane centroid offset, not a gap or an upward-sloping header end.
The right jamb remains above the loft; no ground post was added in the door.

TE, TW and TS physical geometry and section choices are unchanged.
Both stages and the final second-order whole-frame analysis were rerun.
Connections, welds, bolts, foundations, roof-brace crossings and site/code
requirements remain preliminary. These are analytical centerline drawings.

Open Corrected-TN-Door-Truss.pdf, TN-door-detail.png, or TN-interactive.html. complete.network.json and roof_first.network.json contain the globally solved networks with all applied loads and supports. verify_and_draw.py replays these networks; make_geometry.py and solve.py require the parent project and previous clean-layout geometry.
