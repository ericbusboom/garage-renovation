# Renovated garage — structural iteration 1

**Status: preliminary conditional model, not a fabrication design.** The original garage is hidden in the separate renovation CAD group. No column has been removed from the CAD baseline. No load capacity is credited to the original walls or slab.

## Load basis

The 1,000 lb rated hoist is modeled as a 1,350 lb vertical point action: 1,000 × 1.25 assumed impact + 100 lb assumed hoist/trolley weight. It is tested separately on B2 and the future T1 floor beam at quarter, middle and three-quarter span; simultaneous hoists are not assumed. Real trolley travel limits, local flange bending, side loads and crane-post action remain to be checked.

The 275.64 ft² loft uses 40 psf live load (11,026 lb), a 30 psf use case, and 75 psf local bands at the north and east edges. The 125 psf case is a sensitivity only; applicable occupancy and code minimum are not yet determined. A 200 lb machine is also tested in addition to the 40 psf case. The joists and plywood still need local load checks.

Dead-load allowances: floor 12 psf excluding primary steel; sloped roof 9.5 psf of surface; cap 6.6 psf of surface; insulated metal walls 4 psf. Candidate primary steel self-weight is computed from member lengths. These assembly allowances require a manufacturer/material takeoff. Roof live load is a provisional 20 psf plan-area case. A 20 psf uplift sensitivity is not a site wind design.

## First comparison

| Layout | Primary steel (lb) | Total floor movement (in) | Largest hold-down (kip) |
|---|---:|---:|---:|
| All columns | 10,135 | 0.664 | 11.4 |
| Remove W2 | 9,935 | 0.670 | 11.7 |
| Remove W3 | 9,902 | 0.844 | 12.0 |
| Remove both | 9,702 | 0.997 | 13.0 |

Movement is absolute displacement of the main floor-support members under dead + floor live + roof live loads. It is not joist or deck deflection, and it is not directly interchangeable with a span-relative L/360 criterion.

W2 removal is the better candidate for further study of the two intermediate west columns: floor displacement changes little, while W3 removal increases it appreciably. This does not establish that W2 can be removed. All cases show large east-side compression/hold-down demands. Removing both also transfers about 11 kip of hold-down demand to SW0.

Hoist cases: peak modeled floor-support displacement is 0.691 in with all columns, 0.695 in without W2, 0.861 in without W3 and 0.978 in without both. These cases include dead load, 40 psf floor live load and one hoist; the 20 psf roof live case is separate.

## Modeling and checks

CAD centerlines and explicitly identified connection offsets feed a 3D PyNite frame model. Roof load is provisionally carried east–west to TE and TW. Steel beams and trusses share load through the modeled joints; each truss is not assigned the entire building load. The future T1 floor beam and hangers are active in this final-stage analysis. The roof-first construction stage has not yet been checked.

Candidate sections are HSS 6×6×1/4 chords, HSS 2×2×1/8 webs, HSS 4×4×1/4 typical posts and W8×31 floor beams. They are stiffness-study candidates, not optimized selections. This roughly 10,100 lb steel baseline is not claimed to meet the minimum-weight goal.

A simply supported beam benchmark reproduces its closed-form deflection. Linear cases check global force and moment balance. Sensitivity runs change web-end bending releases, base fixity and numerical offset-link stiffness; a P–Delta baseline is also included. Convergence and force balance verify solver behavior, not connection realism. Open rectangular truss bays still rely on frame action and need actual joint design.

## Cost optimization and next design gate

Use cost-inputs.json for quantity comparisons and editable rates. Rates are deliberately blank until quotes or stated planning assumptions are supplied. Removing a post saves its steel and potentially one footing, but added reinforcement, hold-downs and connection work can exceed that saving. Compare shop welding with site bolting against site welding after detailing comparable joints.

The next design iteration must resolve the TE/S2/S3 load path and foundation hold-downs, member buckling and lateral restraint, connection capacities, the lateral system, roof seams, hoist flange checks and temporary erection bracing. Only then should stock sections be reduced and cost-ranked as feasible candidates. A California structural engineer needs to review these items before fabrication.

## Reproduce

Install the packages in requirements.txt, then run `python run_analysis.py` and `python make_report.py` from this directory. Edit design-basis.json for the exposed load inputs. Geometry and connectivity come from cad-analytical-members.json; geometry changes require a fresh CAD export. See results.json for every load case and assumption.

## References

- [San Diego adopted codes](https://www.sandiego.gov/development-services/codes-regulations): establish governing requirements before final design.
- [PyNite stability documentation](https://pynite.readthedocs.io/en/latest/stability.html): solver stability is distinct from structural design adequacy.
- [AISC cost guidance](https://www.aisc.org/architecture-center/resources/the-steel-advantage/cost/): fabrication and erection matter alongside material weight.
- [Steel Tube Institute: fabricator considerations](https://steeltubeinstitute.org/resources/fabricator-wishes-knew-hss/): connection detailing and fabrication affect economical HSS designs.
