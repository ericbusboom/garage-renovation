# Candidate 8 — garage structural study

**Recommendation:** carry forward this braced steel scheme as the next design candidate. It supports the studied loft and roof without assigning vertical capacity to the old walls or slab. It is not a permitted or fabrication-ready design, and is not a proven global cost minimum.

## Main choices

- Remove W2; retain the other nine ground columns. Strengthen TW diagonals to compensate.
- B2: W8×24. T1 future suspended floor beam: W6×15. T-SO: W6×15.
- TE upper chord: HSS 6×6×1/4. TE lower chord: HSS 4×4×1/2, centerline raised from 115 to 118 in to clear old rafters while retaining the floor and roof elevations.
- TE webs: HSS 3×3×1/4. Most other webs remain HSS 2×2×1/8. TW diagonals: HSS 3×3×1/8.
- TW lower chord: HSS 4×4×1/4; upper: HSS 4×4×5/16. The heavier bottom chord avoids relying on the future loft for its roof-first lateral restraint.
- Typical posts: HSS 4×4×1/4. W4 and N2: HSS 4×4×3/8. N1/U-W retains its 6×6×1/4 candidate section. The CSV records all remaining sections.
- Add 16 diagonal bracing members: four lower perimeter bays, two upper-wall bays and two roof-plane bays. The north lower braces move 4 in north for eave clearance; their offset connections need design.

## What the computations establish

Primary steel: 9,408 lb, plus a separate assumed 10% connection dead-weight reserve of 941 lb. This includes primary beams, trusses, posts and the explicit new braces. Secondary roof framing is included only as part of the roof assembly weight allowance. Earlier lighter gravity-only candidates omitted this bracing and are not equivalent completed designs.

Maximum screened member ratio: 0.82 in the completed stage and 0.84 in the roof-first stage. Values below 1 pass the implemented checks; they are not safety factors or proof of every limit state. The additional full-length lower-chord buckling check gives 0.87 for roof-first construction. Upper chords and trolley rails still require designed lateral/torsional restraint at no more than 72 in.

Maximum main floor-support movement under dead, storage-band and roof live loads: 0.58 in. B2 live-only deflection relative to its moving supports: 0.35 in versus a 256.25/360 = 0.71 in comparison. Midspan B2 hoist-case relative deflection: 0.61 in. These are steel-support results, not plywood or joist deflections.

The 10 psf equivalent horizontal-force test gives 0.34 in in the east–west direction and 0.11 in north–south. Roof-first results are 0.34 and 0.11 in. Pinned-base tests give 0.35 and 0.12 in, so these results no longer depend strongly on fixed bases. Tests in both directions at twice the lateral force are included in member checks.

These lateral loads are diagnostic roof-level horizontal forces derived from 10/20 psf times a projected rectangle, not a code wind-pressure distribution. They are not San Diego wind or seismic design loads. The completed candidate uses P–Delta analysis; release/base sensitivities use separate cases. Global force balance, linear moment balance, a closed-form beam benchmark and an axial-force sign check were used. Explicit offset links use finite high stiffness, with a lower-stiffness sensitivity. Coordinates are rounded to 0.001 in to avoid spurious microscopic elements.

## Loads and lightweight envelope

The loft is 275.64 ft². Uniform 40 psf live load is 11,026 lb. The storage case raises 36-in bands along the north and east edges to 75 psf. One 200-lb machine case is also applied over the general floor load. The hoist is 1,000 lb rated, with 25% assumed impact plus 100 lb assumed equipment weight, tested at three trolley positions on each rail. One hoist operates at a time. The separate exterior jib crane, landing ledge and a 1,000-lb concentrated load on plywood are not approved by this trolley analysis.

Dead-load ledger for the candidate:

- Primary steel plus connection allowance: 10,349 lb.
- Loft joists/deck allowance: 3,308 lb (12 psf).
- Roof assembly allowance: 6,058 lb (9.5 psf main sloped surface; 6.6 psf cap).
- Lightweight wall allowance: 2,329 lb (4 psf gross wall surface).

A representative REC module weighs 50 lb over 22.4 ft², about 2.23 psf ([manufacturer data](https://www.recgroup.com/sites/default/files/2025-04/Web_DS_REC%20Alpha%20Pure-RX_EN%20US_042025.pdf)). Metl-Span lists roughly 2.1–3.2 psf for the shown 2-in insulated metal-panel configurations ([panel weights](https://metlspan.com/wp-content/uploads/2022/11/PSF-Panel-Weights_2019.pdf)). These support retaining a lightweight assembly: solar above waterproof metal, foam insulation and metal interior skin. The remaining roof allowance covers secondary framing, fasteners, flashings and reserve. Product attachment, ventilation and the complete roof fire/waterproofing assembly remain to be specified.

The 125 psf storage sensitivity does NOT pass: maximum screened ratio 1.47. The owner’s 40 psf target is not a determination of the legally applicable occupancy load. Confirm that classification under [San Diego's adopted codes](https://www.sandiego.gov/development-services/codes-regulations) before treating these sizes as the design basis. Existing walls do not justify reducing the required load or safety factors.

## Foundations and existing walls

Uplift remains a structural design issue that can be addressed with an engineered load path through connections, anchors, reinforced foundations and soil. It has not been eliminated by assumption. In the service40 case S2 is +0.05 kip and SW0 is -2.95 kip. Bracing redistributes forces. The reaction CSV includes the larger lateral-test demands; those are not final foundation design loads.

No footing dimensions have been approved. The old estimated 18-in by 36-in piers cannot be assumed adequate for uplift, overturning or soil bearing. New connections to the old walls must account for actual stiffness and differential movement; a rigid connection can transfer weight into an old wall even when its capacity is not credited in calculations. Do not use the previous 20 years of performance as a quantified reserve capacity.

## Build-around-existing check

The candidate is saved separately as Garage-Candidate-8.FCStd. The original Proposed-Garage.FCStd remains unchanged. CAD was reopened and all 121 candidate steel solids validated. The existing roof is unclad in that model; field clearances and cladding thickness still matter.

TE now clears the modeled old roof framing by a minimum of 0.35 in. This does not include old roof cladding or erection tolerance; field measurement is required before accepting roof-first clearance.

Remaining modeled intersections involve: BR-E-ground-2, N1 / U-W, N2, S3. See candidate8-clearance-check.json for each existing component. These require planned local openings or adjustment before erection; do not cut loaded existing framing based on this model. Roof-first means the complete tested braced frame and secondary roof restraint are installed, not that any partially erected sequence is stable.

The braced bays must be reviewed against windows, the covered walkway, the outbuilding and access. The main north garage-door opening is left clear. Upper north bracing may affect the adjacent window treatment.

## Secondary framing and remaining design

For the modeled approximately 109-in joist span at 16-in centers, a 1.5×7.25-in wood joist needs approximately 1,093 psi adjusted bending strength and 1.06 million psi modulus to meet the simple 75 psf live + 12 psf dead checks used here. This is a demand specification; species/grade, adjustments, hangers, bearing and plywood point-load capacity still need selection.

At a trial 48-in spacing and 256.25-in span, an E–W roof purlin needs roughly I = 12.1 in⁴ for the provisional roof-live L/240 comparison, and elastic section modulus at least 2.7 in³ for the stated factored gravity load. These are lower-bound property targets, not a cold-formed section design. A supplier/AISI check must include local/distortional buckling, continuity, uplift and bracing. Roof fasteners alone are not an automatically adequate diaphragm.

Still needed before fabrication: actual joint and HSS face checks; welds/bolts/gussets; member torsion/warping and complete applicable code interaction checks; rail flange/wheel contact and hoist side loads; site wind/seismic load cases and combinations; foundation/soil design; fire and property-line requirements; and erection-stage sequencing. A California structural engineer should verify and complete that design.

## Cost and reproducibility

This is the best-performing candidate tested in this study, not proof of the cheapest possible structure. W2 removal requires stronger TW diagonals; its earlier net steel saving was only about 150 lb, so avoided foundation work is the main potential benefit. Whether welding or bolting is cheaper depends on the connection details and shop/erection quotes. A hybrid with shop-fabricated truss sections and site connections is a pricing option, not an established winner.

Files include the Python model, stock catalog, geometry, load basis, member checks and every case reaction. Run candidate8.py with PyNiteFEA 3.0.0 after installing requirements.txt to repeat this candidate from the supplied prior selection input. Change design-basis.json for loads, re-export geometry when CAD changes, and compare all cases before accepting a revision. The historical trials have different scope/assumptions; candidate8 results are the current reference.

Compression uses the AISC E3 column curve; W bending screening includes lateral-torsional buckling with Cb=1. Axial/biaxial demands are combined conservatively with elastic capacities. These partial checks are not an automatic AISC compliance engine. [AISC specification formula reference](https://www.aisc.org/globalassets/aisc/publications/standards/a360-16-spec-and-commentary_march-2021.pdf), [Atlas HSS section properties](https://www.atlastube.com/wp-content/uploads/2018/04/A500-Square-Current.pdf), [PyNite analysis API](https://pynite.readthedocs.io/en/latest/FEModel3D.html).
