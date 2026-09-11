# Whole north-wall alignment

Entire north-wall frame aligned

TN chords, webs, door header and jambs, north braces, W4, N1 and N2
now occupy one plane at north-coordinate 253 inches.
TN moved 4 inches north; N1 moved 0.5 inch north to align with W4/N2.
All 36 internal north-wall connections now have coincident member axes.

The east-end vertical and diagonals now terminate at actual chord nodes.
The upper door jamb meets the bottom chord directly.
The five-inch height difference between TE and TN bottom chords is carried
by the real N2 column segment; the redundant offset link was removed.
Columns retain their existing extensions above the top chord.

TE, TW and TS member geometry is unchanged. TE/TW rear connections now
meet TN at their ends. Floor load distribution uses the actual TN support
station (253 inches) with the same loaded floor area and load intensities.

Both stages and final second-order analysis were rerun. The revised global
network has been replayed independently across 70 load combinations.

These are analytical centerlines, not fabrication details. Connection hardware,
foundations, roof-brace crossing details and full code checks remain unresolved.

Open Aligned-North-Wall.pdf, TN-door-detail.png, or TN-interactive.html. complete.network.json and roof_first.network.json contain the globally solved networks with all applied loads and supports. verify_and_draw.py replays these networks; make_geometry.py and solve.py require the parent project and previous clean-layout geometry.
