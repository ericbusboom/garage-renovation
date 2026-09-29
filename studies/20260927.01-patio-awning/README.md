# Patio awning

Awning (tarp) over the work patio beside the outbuilding (storage + parked trailer).

- `draw_plan.py` → `patio-plan.svg` / `.png`: Eric's sketch `data/images/patio.svg` redrawn with rounded dimensions and numbered posts.
- Orientation: drawn as Eric sees it from the house — **page up is south**, page right is west. The P2–P3–P4 fence is the west property line; P1 and the electrical pillar are on the east side.
- Script frame: inches, x = page right, y = page up, origin at P1 centre.
- Posts (railroad ties): all four tops at 7'-0" (2026-09-29). History: P1/P2 6'-0" and P3/P4 6'-10" as found; all to 6'-10" to clear cabinets; all to 7'-0".
- P2–P3 and P3–P4 are 8'-0" clear between faces (set for 8 ft stringers), so centres are 8'-8" apart. P4 is 4'-10" past the pillar line (derived, assumes 8" post depth).
- Airstream: inside the fence, 18" off it, front 2'-8" (32") beyond the patio edge at the pillar end, 8 ft wide, 2 ft corner radii; length not given.
- Tie points at 101" (8'-5") high on the fence-side face of the pillar: T1 at its south (page-top) corner, T2 at its north corner. Cables T2–P4 (to P4's south face), T1–P3, T2–P1, T2–P2. `draw_plan.py` prints each cable's plan clearance to the Airstream; T2–P4 crosses the trailer's front corner in plan (~5"), but at 7'-0"–7'-3" high (straight line, no sag) it passes over the rounded roof corner; Eric confirms on site that it just clears from the 101" tie.

## Awning concepts (`awning.py` → `awning-2-membrane.png`, `awning-3-junctions.png`, `awning.json`)

Run: `archive/.venv/bin/python studies/20260927.01-patio-awning/awning.py` (a few seconds). Shared geometry is in `patio_site.py`.

- **2 — fabric with sewn edge cables.** Six-corner sheet T1-P4-P3-P2-P1-T2, clamped straight to the pillar face T2–T1. Force-density form-find; each edge cable tuned to sag 10 % of its chord (circular arcs, cable tension = fabric prestress × radius). The T1–P4 edge grazes the Airstream's front corner at about 7'-1" high. With all posts at 6'-10" the fabric is nearly flat near P2 (min slope 1.2°, ~8 % under 3°), a ponding risk.
- **3 — three-way cable junctions.** Node A (T1, P3, P4) at 36" off the fence on the patio front line gives tensions 1.15 : 1 : 1 and clears the trailer by 10" in plan. P1–P2 cable pulled by T2 at one mid-span node (3a) or two (3b); T3–P1 separate. A 3-way cable node must lie in the plane of its three anchors, so the node heights come from equilibrium, not choice. The closer the P1–P2 junction is held to the line, the harder that cable works (≈1.7× the T2 leg at 24", 2.4× at 12", 4.6× at 6"). Two T2 legs spread tensions worse (2.4 vs 1.7) than one.
- Prestress only; no wind, rain or self weight yet.

## Which post to drop for drainage (`sweep_post.py` → `sweep_p4.json`, `awning-2-membrane-p4-70.png`)

With all posts at 6'-10" the flat zone is by P2. P3 can't come down (electrical connection beside it). Lowering P4 makes the flat zone bigger (fabric under 3°: 8 % at 6'-10" → 17 % with P4 at 5'-10"). Raising P3 barely helps (6 % at 8'-10"). Dropping P2 fixes it (0.1 % with P2 at 6'-2"), if the cabinets allow. The Airstream skim is not a constraint: Eric can move the trailer back.

## Where it pools (`ponding.py` → `awning-4-ponding.png`, `ponding.json`)

Drainage by steepest descent on the mesh. Ponding: 0.1" rain film as load, re-solve at fixed force density, fill dips to spill level, add the water, repeat. Linear force density, so a "runaway" means the pocket keeps deepening, not a literal depth.

- All posts 6'-10": the unloaded fabric has no dip, but under rain a slack sheet (8 lb/ft) pockets about 3'-8" in from the fence and 4'-10" in from the P1–P2 edge, in the flat zone near P2, and the pocket keeps deepening. A firm sheet (20 lb/ft) holds only a trace (0.1").
- P2 at 6'-2": no pond at either tension; the low point is the P2 corner.
- About 40 % of the roof sheds off the fence edge P2–P3, 37–40 % off the north edge P1–P2, and 16–19 % off P3–P4. Nothing meaningful comes off the pillar side.

### Update 2026-09-29: all posts raised to 7'-0"

Figures and JSON above are regenerated at 7'-0". With only 17" of fall from the pillar ties (8'-5") the fabric is flatter (11 % under 3°, median slope 5.7°), and now even a firm 20 lb/ft sheet pockets under rain, near (145, 42): about 2'-5" in from the fence and 3'-6" in from the P1–P2 edge. Dropping P2 to 6'-6" (6" below the rest) stops ponding at both tensions; 6'-8" or 6'-10" only fixes the firm case. The comparison panel uses P2 at 6'-4".
- `setback-research.md`: San Diego code research on how close the awning can be to the property line (2026-09-29).

## Tarp on parallel cables from the roof edge (`tarp_cables.py` → `tarp-cables.png`, `tarp_cables.json`)

2026-09-29. Roof edge over the pillar: x = 24 (11" past the pillar's west face), y = 64 to 160 (10" past its south end, 8 ft long). R1 south end, R2 middle, R3 north end. Cables run due west from R1–R3 to clips N1–N3 on a fence cable P4–P3–P2. For parallel cables the clips sit at the R points' y. The fence cable then acts as a string with point loads: the bow off the fence is d = M/H, so the tension along the fence, H, sets how far the clips pull in. For a 6" bow, H ≈ 4–5 × the R-cable tension. R2 is only 8" from P3's line, so tying R2 straight to P3 (option B) is 3° off parallel and saves a clip. R height is assumed at 8'-5" (not yet given); it moves node heights, not the plan answer.

### Tarp choice (2026-09-29)

Tarp spans 8 ft between the R1 and R3 cables (woven through edge grommets) and runs east–west from the roof edge (x = 24) to at least 2'-6" off the fence: 10 ft maximum. A **cut-size 8 × 10 tarp** finishes about 7'-6" × 9'-6". The 6" shortfall in width pinches the edge cables toward R2, which puts a little tension in the tarp, and the 9'-6" length ends about 3 ft off the fence. Candidates found 2026-09-29 (sale prices, check before buying): Tarp Supply 18 oz flame-retardant vinyl-coated polyester, Forest Green, NFPA 701 / CA State Fire Marshal, waterproof, grommets every 24", ~$94, made to order; Tarp Supply 15 oz green polyester canvas, exact 8 × 10, water-resistant only, no fire-retardant rating, ~$90; TarpsPlus 15 oz green waterproof polyester canvas, ~$158, made to order.
