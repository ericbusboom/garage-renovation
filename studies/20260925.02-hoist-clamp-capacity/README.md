# Hoist from beam clamps on the loft floor beams

2026-09-25. Owner question: a trolley runway hung from beam clamps on the bottom
flange of the loft beams BWI, B-1, B-1A and B-2 (all W12x16). What hoisted load is safe?

`clamp_capacity.py` builds the current frame (`lean_to_rafters.build()`), adds a unit
hoist at every joist node along the four beams (1,000 lb rated → 1,250 lb vertical
with 25 % impact + 100 lb lateral across the beam, as `loads.HOIST`), and bisects the
factored multiplier (1.2D + 1.6L + 0.5Lr + 1.6H) against the AISC check of every steel
member. It assumes the trolley sits directly under one clamp, so one clamp takes the
whole load. It runs twice: floor beams continuous through their joints (the project
model) and floor-beam ends pinned (the unsized connections could be shear tabs).
Results: `clamp_capacity.json`. Runtime about 3 minutes.

## Rated hoist capacity at one clamp, lower of the two end conditions (lb)

| Beam | Worst spot | Loft at 100 psf (design) | Loft at 40 psf | Loft empty |
|---|---|---:|---:|---:|
| B-1A (y=128) | midspan, x≈115 | **1,030** | 4,000 | 6,000 |
| B-2 (y=185) | midspan, x≈150 | **1,210** | 5,300 | 7,400 |
| BWI (x=3.75) | at B-1 (y=71) | **1,370** | 5,100 | 7,600 |
| B-1 (y=71) | west end, x≈12 | **1,680** | 6,000 | 7,300 |

Near the column ends the numbers are 2-5 times higher. With a full design floor
load the frame is already near capacity (max DCR 0.89-0.92, E.top governing the
frame, and BWI/B-1A/B-2 at 0.6-0.84), so the hoist gets whatever is left.

## Checks not in the frame model

- **Bottom-flange local bending at the clamp.** W12x16 flange is 3.99 in. wide by
  0.265 in. thick. With the jaw 1/4 in. in from the tip, the moment arm to the
  web fillet is about 1.25 in.; effective length ≈ jaw width + 2 × arm ≈ 4 in.
  Yield-line capacity ≈ 5.1 kip factored for two jaws → about 2,500 lb rated;
  elastic (no permanent set) ≈ 1,700 lb rated. Caps a single clamp near 1 ton
  whatever the loft load.
- Beam-end connections (unsized), fatigue under repeated hoisting, torsion from the
  load hanging 6 in. below the beam axis, the clamps, runway beam and trolley
  themselves.
- A runway cantilevered past its end clamp puts more than the hoisted load on that
  clamp; the table assumes the trolley stays between clamps.

Service deflection is small: about 0.11 in. per 1,000 lb at B-1A midspan.
