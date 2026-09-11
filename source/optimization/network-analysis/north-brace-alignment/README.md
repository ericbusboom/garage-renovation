# North brace alignment

North ground-brace alignment correction

Both X-braces between W4 and N1 / U-W were offset 4 inches north of
the column axes. All four brace endpoints now coincide with those axes.
The analytical offset links at those four connections are eliminated.
Attachment heights remain at 6 inches and 115 inches above datum.

W4 is at north-coordinate 253 inches; N1 is at 252.5 inches. The braces
follow the plane between those columns, including that half-inch difference.
The TN truss above remains in its existing plane at north-coordinate 249 inches.
Its short connections to the posts are separate from this ground-brace correction.

The corrected over-door mini-truss and every other physical member are unchanged.
Both construction stages and the final second-order analysis were rerun.
The whole-frame network contains each column and brace once.

These are structural centerlines. Gussets, brace crossing clearance, bolts,
welds and foundations remain to be detailed; this is not a fabrication drawing.

Open North-Brace-Alignment.pdf, TN-door-detail.png, or TN-interactive.html. complete.network.json and roof_first.network.json contain the globally solved networks with all applied loads and supports. verify_and_draw.py replays these networks; make_geometry.py and solve.py require the parent project and previous clean-layout geometry.
