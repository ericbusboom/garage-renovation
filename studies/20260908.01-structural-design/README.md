# Garage loft — preliminary beam options, 7 September 2026

This is a reproducible gravity-load screening study for the garage in ZIP 92109. Its purpose is to identify useful steel and laminated-wood candidates, not to issue a construction or purchasing schedule. A California-licensed structural engineer must complete the building load path, stability, connections, foundations and applicable code checks before construction. No new gravity support is assigned to the existing garage walls or weak slab.

## Result to develop

For the two long cross-garage members, develop **W10×39 steel** as the initial architectural candidate and **W10×49** as the stiffer, heavier alternative. Their catalog depths are 9.92 and 9.98 inches. These fit a nominal ten-inch envelope; manufacturing tolerances, seats, fire protection, decking and connections need additional allowance. A W10 designation alone does not ensure a depth below ten inches.

If laminated wood is preferred, the occupied-loft case points toward a **7 × 16 inch LVL** rear cross-beam, increasing to **7 × 18 inches** for the three-wall storage-band case and **7 × 20 inches** for the full 125 psf storage sensitivity. The 7-inch width means four 1¾-inch plies, connected and loaded as an engineered assembly; it is not a single off-the-shelf solid section. These are 2.0E–2600Fb grade candidates, not interchangeable with arbitrary glulam. Product availability, ply connections, bearing and restraint still require verification. A 7 × 9½ inch LVL is much too flexible for the long span in this model.

The shorter rail and header spans warrant smaller candidates. W8×18/W8×24 and approximately 5¼ × 9½ inch LVL are worth developing for the storage-band case, conditional on all P1–P4 support locations having the required stiffness and strength. For the full uniform storage case, the cabinet rail's wood candidate increases to approximately 5¼ × 11⅞ inches. The CSV contains all candidates, not just the preferred ones. Do not use these short-span choices for a scheme that bypasses P1/P4 without reanalysis.

## Geometry and proposed load path

Dimensions are inches, origin at southwest exterior garage corner; X east, Y north. Garage width 249.5, original length 249. Upper north edge 255; first 72 inches measured from the exterior south face have no loft floor. Gross modeled loft area is 317.07 square feet; clear area is smaller. Exterior columns are represented as 4-inch-square steel support locations; HSS wall thickness is not selected. Footings are assumed capable of providing the required support, without crediting the old slab.

Cross-beam lines: Y = −21.25, 69.75 (B1), 185 (B2), 253. B1/B2 have support centers X = −32 and 224.25, a 256.25-inch / 21 ft 4¼ inch span. Cabinet rail at X224.25 bears on P1–P4 at Y56/105/154/203. All four west posts are retained. South header supports X−32/148.5/211.5; north header supports X−32/53.25/224.25. Retaining the previously drawn jamb-post centers with 4-inch posts leaves a small clearance at the door jambs.

**An explicit analysis addition:** transverse beams extend to X249.5, making a 25.25-inch cantilever beyond the cabinet rail. This carries the floor/roof edge without loading the old east wall. The previous support drawing established the rail and north extension but did not establish this extension for every transverse member. Treat these new extensions as part of the proposed structural scheme, not as surveyed existing beams. South rail connection is 12.75 inches beyond the south support at X211.5.

Floor joists run north–south between B1/B2/north header; their longest support span is 115.25 inches. The roof is assumed to deliver load to these same four transverse lines through new steel upper framing. Roof rafters/hip collectors, their elevations and transfers have **not** been designed. Changing their direction or introducing concentrated hip/truss reactions changes these beam results. The model distributes roof gravity over the plan footprint, including north cap overhang, rather than resolving individual hip rafters. Upper side-wall weight is a budget allowance, not a measured takeoff. Roof projection west of the garage, steep east slope and irregular cap geometry need a final surface takeoff; this is not a guaranteed upper-bound roof weight.

White balcony: modeled 32-inch width west of the garage and 78-inch north–south length, with load delivered to transverse members. Existing outbuilding is not assigned new building load. The west longitudinal member remains structural, but its transverse intersections lie directly over posts, so little additional vertical bending appears there in this chosen load path. That does not establish its lateral/collector role or connection requirements.

## Loads and research

San Diego identifies the 2025 California Building Standards Code as effective for projects submitted from January 1, 2026. The occupancy classification remains unresolved: an intensively used storage loft should not automatically be treated as an uninhabitable attic. The 40 psf occupied-floor and 125 psf storage cases below are comparison benchmarks, not a determination of the legally required classification. Model-code residential tables distinguish limited-storage attics, habitable attics and other residential areas; IBC storage-warehouse tables use 125 psf for light storage, with heavier loads required where anticipated. The mixed-band case is our proposed loading scenario, not a prescribed code category.

- Floor dead: **12 psf**, an estimated allowance for wood joists, plywood, blocking and light finishes; primary beam self-weight is separate. No masonry partitions, screed or heavy finishes included.
- Roof dead: **15 psf of horizontal projected area**, a preliminary allowance including roof framing and light upper envelope. Metl-Span lists **2.65 psf for a 3-inch CFR panel**; Viridian lists **12.8 kg/m² ≈ 2.62 psf** for an example integrated PV assembly. At 30°, those two layers together correspond to about **6.1 psf of horizontal area** before framing, trim and other components. Products are weight references, not a compatible or approved specified assembly. Foam core is already included in the insulated metal panel weight.
- Roof variable gravity: **20 psf unreduced** maintenance/live-load allowance over projected area. Snow, rain/ponding and downward wind are not established by this allowance. No claim of zero snow follows from ZIP code alone.
- Balcony: **15 psf dead + 60 psf live** as a trial allowance. Guard and door-opening loads are separate and unmodeled.
- Steel self-weight: actual catalog pounds per foot for each trial. Wood self-weight: assumed 41 pcf. In each candidate run, all primary members use that candidate's weight, so mixed schedules need their own final run.

Floor live cases:

1. **Occupied40:** 40 psf over all loft floor; about 12,683 lb, excluding floor dead load.
2. **Storage bands:** 125 psf within 3 feet of the north, east and west edges, 40 elsewhere. Corners counted once. This represents storage concentrated around the walls.
3. **Storage125:** 125 psf over the entire loft; about 39,634 lb, a substantially heavier sensitivity than the owner's estimated contents.
4. **Patch1000:** Occupied40 plus a 1,000-lb point at B2 midspan to screen that beam. This does not envelope every possible patch position or certify the plywood.

The owner's 2,000 lb of contents equals 6.3 psf averaged over gross floor area. Movable contents are normally **live load**, even if left in place for a long time. Long duration matters for wood creep; it does not make a low average an adequate substitute for the floor design load.

## Solver and acceptance screens

Custom Python finite elements using NumPy/SciPy: linear beam bending with downward displacement and rotation at each node. Steel uses Euler–Bernoulli bending; LVL includes Timoshenko shear flexibility calibrated to the ESR-1387 bending-plus-shear expression (effective shear rigidity EA/19.2). Results are service-level gravity comparisons, not full LRFD or ASD load-combination envelopes.

Secondary joist/rafter reactions are integrated for partial coverage and overhangs. Cross beams are simply seated onto rails/posts; cabinet rail and headers are continuous over their supports. The calculation transfers cross-beam reactions into the cabinet rail and then rail-end forces into the headers. Supports are vertically rigid; differential settlement, cabinet compression, rail deflection imposed on cross members, joint slip and lateral sway are omitted. Thus displayed beam deflections are relative to assumed stationary bearings, not total building movement. Continuous rail reactions assume equal EI along the rail and positive/tension-capable engagement at every listed support.

For each member, maxima from dead, floor/balcony live and roof live are added in absolute magnitude. This conservatively combines different peak locations for those cases; it does **not** envelope alternate live-load patterns on continuous beams or arbitrary shelf/patch positions. Both floor and roof live are included fully and simultaneously; no live-load reduction is taken.

Screening limits: floor-live L/360 and total immediate L/240, using longest support span. These are study criteria, not the final assembly-specific code limits. LVL also receives a sustained-load sensitivity of 1.5 × (dead + floor/balcony live) + roof live, compared with L/240. This assumes all floor live could remain stored; actual creep and moisture/duration requirements need final verification. LVL bending screen uses 2600 psi × min[1,(12/depth)^0.136] × 0.9; shear uses 285 psi. No increase for short load duration is taken. Steel elastic bending stress is screened against Fy/1.67 with assumed Fy50 ksi. Steel lateral-torsional buckling, shear, flange/web local effects and connection capacity are **not** established by that bending-stress ratio.

A `passes_limited_screen` value in the CSV means only these numerical checks pass. It is not a design approval.

## Cabinet frames, columns and foundations

For the **storage-band case**, with W10×39 self-weight and rigid engagement at all P1–P4, calculated service gravity frame reactions are approximately:

| Frame | Reaction |
|---|---:|
| P1 | 7,209 lb |
| P2 | 1,981 lb |
| P3 | 4,540 lb |
| P4 | 8,920 lb |

For full 125 psf storage they rise to about 10,020 / 2,671 / 6,547 / 12,847 lb. These are reactions at a complete frame plane, not each upright. A simply supported 30-inch top chord with a load 11 inches from the front would divide its reaction approximately 63% front / 37% rear; actual bracing and connections alter that distribution.

The existing 2×1-inch uprights cannot be certified from gauge alone. For illustration, an ideal sharp-corner 2×1 tube with an assumed 0.120-inch wall, unbraced over 98.5 inches, has only about **3,017 lb Euler weak-axis buckling load** with pinned ends. Euler load is an ideal instability ceiling, not allowable capacity. It is already below some calculated individual-leg demands. Bracing the 30-inch frame plane does not automatically restrain this weak direction. An engineered replacement, inter-frame restraint and proper foundations are necessary design subjects.

A sensitivity model crediting only P2/P3 and the end supports gives about **7,693 and 9,569 lb** on P2/P3 in the storage-band case. It does not prove existing P1/P4 become unloaded: stiffness, fit-up and deliberate isolation/transfer details govern actual sharing. The one-inch door-face constraint remains unchanged.

The all-frame storage-band model demands rail-end hold-down reactions of about **240 lb south and 870 lb north**, even in this combined gravity case. Full uniform storage increases them to about 380/1,290 lb. These are uplift actions at the rail/header connection, not necessarily uplift of the entire exterior column. Without tension-capable connections, support contact can open and the continuous-beam assumptions change. Some exterior support reactions also become slightly negative in the full-storage case; wind will introduce additional uplift cases.

The largest modeled exterior compression reaction is about **8.2 kip** for storage bands and **11.6 kip** for full storage, before the small west-rail self-weight contribution and column self-weight. Four-inch HSS is a family of sections, not a capacity: wall thickness, grade, effective length, bracing, bending and base restraint are still required to select the posts. Foundations must support the frame-leg and exterior-column demands plus overturning/uplift; neither the old slab nor the reported 18-inch piles are certified by this analysis.

## The 1,000-lb square-foot load

For one joist spanning 115.25 inches and taking the entire 1,000 lb at midspan, the **patch alone** produces 28,812.5 lb-in moment and 500 lb at each end, before any distributed floor load. At an assumed wood E of 1.6 million psi, bending-only stiffness of 62.26 in⁴ is required just for patch-only L/360. The plywood's panel bending, punching/local bearing, actual feet/contact area and distribution into adjacent joists have not been checked. This load needs a designated reinforced storage location or a designed load-spreading assembly; a main-beam pass does not make ordinary plywood adequate.

## Verification and files

`analyze.py` generates `results.json`, `candidates.json`, `beam-options.csv`, `basis.json`, and the comparison PNG/PDF. `check_details.py` independently checks the local load demands and transfer equilibrium. Validation passed for uniform simple-span load, central point load, partial distributed loading, cantilever uplift, force/moment equilibrium on every beam, global load transfer balance, mesh refinement and wood shear deflection against the manufacturer's expression.

Run from the project directory:

```sh
MPLCONFIGDIR=/private/tmp/garage-mpl /Applications/FreeCAD.app/Contents/Resources/bin/python structural-study/analyze.py
MPLCONFIGDIR=/private/tmp/garage-mpl /Applications/FreeCAD.app/Contents/Resources/bin/python structural-study/check_details.py
```

No FreeCAD model was changed. The next structural model must resolve the actual roof/upper wall framing, cabinet-frame construction, lateral system, support stiffness and load patterns before this can become a final beam schedule.

## Primary sources

- [City of San Diego — codes and regulations](https://www.sandiego.gov/development-services/codes-regulations): current code cycle.
- [ICC — IRC 2021 Chapter 3](https://codes.iccsafe.org/content/IRC2021P1/chapter-3-building-planning): residential load benchmarks; not claimed as current local adoption.
- [ICC — IBC structural design table, Massachusetts 2021 edition](https://codes.iccsafe.org/content/MAIBC2021P1/chapter-16-structural-design): 125 psf light storage benchmark, not local jurisdiction determination.
- [Nucor-Yamato structural shapes catalog](https://nucoryamato.com/staticdata/catalog.pdf): actual W-section geometry, Ix, Sx and weight, pages 34–37.
- [ICC-ES ESR-1387](https://cdn-v2.icc-es.org/wp-content/uploads/report-directory/ESR-1387.pdf): LVL material properties, depth factors and shear deflection expression.
- [Metl-Span CFR architectural design guide](https://www.metlspan.com/wp-content/uploads/2022/11/CFRRoofArchitecturalDesignGuide.pdf): panel self-weight, PDF page 16.
- [Viridian Clearline Fusion PV16 M10 datasheet](https://www.viridiansolar.com/no/assets/files/Clearline-fusion-PV16-M10-Data-Sheet.pdf): example integrated solar module weight.
