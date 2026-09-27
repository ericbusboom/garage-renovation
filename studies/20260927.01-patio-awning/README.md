# Patio awning

Awning (tarp) over the work patio beside the outbuilding (storage + parked trailer).

- `draw_plan.py` → `patio-plan.svg` / `.png`: Eric's sketch `data/images/patio.svg` redrawn with rounded dimensions and numbered posts.
- Orientation: drawn as Eric sees it from the house — **page up is south**, page right is west. The P2–P3–P4 fence is the west property line; P1 and the electrical pillar are on the east side.
- Script frame: inches, x = page right, y = page up, origin at P1 centre.
- Posts (railroad ties): all four tops at 6'-10" (P1 and P2 raised from 6'-0" on 2026-09-27 to clear cabinets; may go higher).
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
