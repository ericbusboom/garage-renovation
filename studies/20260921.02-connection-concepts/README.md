# Connection concept and model audit

**Status:** preliminary discussion basis; no connection is designed or approved for fabrication.

## What the current analysis actually assumes

The current lean-to/continuous-east-post model contains 127 physical members, 334 geometric nodes, 11 supports, and 38 short analytical links used to transfer load across offsets.

- 54 wood joists, 22 steel rafters, and 6 steel braces are pin-ended: 82 members and 164 released member ends.
- Two steel door-post heads and four support locations along `BE.upper` are explicitly released in addition to the group rules.
- All 11 modeled foundations are pinned bases: translation is restrained and rotation is free.
- Every other connected analytical member end transfers moment. This is a modeling assumption, not evidence that a weld, end plate, or moment connection has been designed.
- No bolt quantity, screw quantity, weld size, plate thickness, hole type, edge distance, block shear, local HSS wall, flange, anchor, or base-plate check exists.

The cost model counts 109 fitted steel ends and prices them as roughly 55 field-bolted connection locations. It also allows shop fitting and welding at steel ends and shop-welded end plates on 13 W-shape pieces. These are estimating allowances, not a connection schedule.

## A practical connection split

### Shop-welded lateral modules

The current explicit designation starts with two ground-to-floor longitudinal moment frames:

- west `BW` line: `BW`, `SW0`, `W1`, `W2`, `W3`, and `W4`;
- east `BE` line: `BE`, `E-S2`, `E-S3`, and `E-N2`.

These are the red members in the viewer. They are a design intent that still requires connection and foundation engineering; the red color does not mean their joints have already been checked. Use shop welding to make transportable frame modules where those lines need continuity, with deliberate field splices selected to suit erection and shipping.

The upper roof and clerestory members are not automatically included in those moment frames. Most are amber in the viewer because the solver presently transfers moment through them even though their lateral role has not been selected. Each amber end must be released, assigned to a braced bay, or deliberately designed as part of a moment-resisting frame.

Do not assume every intersection in these panels must be a full-strength moment weld. Diagonals can still terminate on shop-welded gusset plates with pinned analytical behavior. Chord-to-column or chord-splice locations that provide frame stiffness need explicit moment-connection design.

### Field-bolted simple connections

- Wood joists: proprietary hangers or designed ledgers/hangers; simple ends.
- Steel rafters: seated or shear-tab connections with positive uplift restraint and rotational freedom.
- Braces: bolted gusset plates, detailed so brace work lines meet at the joint.
- `BE.upper`: bolted simple shear/seat connections at its four supports, matching the existing releases.
- Door-post heads: bolted clip or knife plates that restrain translation while allowing the modeled rotation.
- Column bases: base plates and anchor rods designed as nominally pinned bases unless the lateral design deliberately changes them.

### Field splices between welded modules

Use bolted flange/web plates or end plates at deliberate shipping and erection breaks. These can be simple or moment-resisting, but the analysis must match the selected behavior. A connection should not be called “slip” if the structure relies on it to hold geometry: use a simple rotational connection, a bearing-type bolted joint, or a slip-critical joint as the actual load path requires. Slotted holes are useful for erection tolerance only where their allowed movement cannot create a mechanism or unload a brace.

## The main structural consequence

The current reduced-bracing model assumes moment continuity at all joints that are not explicitly released. Converting those remaining joints wholesale to simple bolted connections would remove stiffness that the H/414 drift result depends on. Before detailing, choose and model the lateral system explicitly:

1. identify the welded/moment-resisting frame planes;
2. keep gravity infill, rafters, joists, and brace gussets simple where possible;
3. place field splices to make the welded modules transportable and erectable;
4. rerun strength, drift, second-order, and pre-demolition stability with those releases;
5. design plates, bolts, welds, anchors, and HSS local reinforcement from the resulting connection forces.

The present force results support treating `BW` as an active lateral member: it is wind-governed under the `WX-.ni` combination, with about 137 kip-in of major-axis moment and a 0.515 checked ratio. The east `BE` beam is gravity-governed at 0.608, while its three designated posts are governed by earthquake or gravity combinations. That means the east red frame is an intentional stability/redundancy choice, not a classification inferred from `BE`'s governing load case.

There are 29 amber members. Until a released-joint rerun passes, the reported H/414 drift belongs to the current partly implicit rigid-joint model; it is not proof that the two red frames alone provide that stiffness.

The preferred fabrication direction is therefore **a small number of shop-welded lateral modules with many field-bolted simple attachments**, rather than welding the whole building together in the field or treating every joint as free to rotate.
