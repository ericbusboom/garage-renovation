
## Garage: weight, load paths and steel framing

<b>Review study, not construction sizing.</b> This calculation establishes a conditional gravity-load baseline and tests practical member families. It does not establish a final safe structure or a global minimum-weight design. Existing walls, cabinets and slab receive no added gravity credit.

Your two-stage plan is useful with one correction: equilibrium alone cannot determine how redundant supports share load. Assuming all beams infinitely rigid does not resolve that sharing. This study first assigns tributary loads, then uses finite beam, truss and column stiffness to calculate reactions and member forces.

Finding | Result
Permanent construction weight | 20,443 lb, including 10% primary connection allowance
Primary steel plus connection allowance | 9,233 lb
Occupied service case | 44,734 lb total downward load
Heavy perimeter-storage service case | 55,747 lb total; N2 about 14,999 lb
B2 depth target | An 8-inch HSS candidate survives the selected gravity screen; it is not a final member selection.
Main unresolved issue | Connections, lateral bracing and real load transfer govern whether these results are achievable.
Stored contents remain live load even when left in place. The stated 2,000 lb of contents is not used as a substitute for floor design live load. A 1,000 lb concentrated item is a separate local floor problem.

Simple changes did not deliver a lighter frame: the triangulated trial weighs 9,263 lb, and triangulation with B2/B3 shear seats weighs 9,955 lb, versus 9,233 lb baseline. These are bounded-search comparisons, not proof that triangulation cannot help.


## What I would resolve next

Detail the south load path and connect S1 deliberately; choose a real lateral bracing system; locate the heavy storage bearing points; then redesign the truss panel layout and joints together. Repeat the section search after those decisions. Do not buy the candidate sections from this report.


## Geometry and load routing

All architectural beam and truss bottom lines are at 98.5 inches above nominal ground. The analytical lines idealize those architectural lines as member centerlines; actual centroid offsets and connection eccentricities still need detailing. The main roof rises 30 degrees from T-SO; the rear cap has the restored low hip. The cap surface weight is included, but its rafters and collectors are not explicitly modeled.

Item | Analytical geometry / assumption
Main loft | 18 ft 8-1/4 in east-west by 15 ft 3 in north-south; 284.98 sq ft. South edge 72 in north of south wall.
Floor joists | North-south, supported at T1 (69.75 in), B2 (185 in) and B3 (249 in). North deck edge 255 in.
Roof purlins | East-west onto T-W and T-E, with the east overhang carried by cantilever reaction factors. This choice strongly affects truss demand.
T-E / T-W | Longitudinal trusses. Roof loads enter their upper lines; floor loads enter through transverse framing.
T-S / T1 | Open-bay baseline modeled with rigid frame joints, not pin-jointed rectangular trusses.
T-N | Full upper north wall truss with the door opening. B3 remains the floor-level north beam.
T-SO | A beam despite its historical name. Its south support transfer is not a construction detail.
Columns | All nine shown columns included, with S3 assumed active. S1 has no connection to upper framing and therefore carries only its own weight.
Foundations | Fixed bases initially assumed. Existing footing dimensions and soil capacity are not verified. No foundation sizing is claimed.
Upper wall loads are placed on the perimeter framing. The east wall load includes its offset from T-E. Roof overhang effects are included through reaction factors and equivalent moments. The small balcony north overhang is clamped to the last support station; this and the roof-cap load smearing require refinement. Existing shelter capacity is excluded.


## Permanent weight budget

Component | Weight, lb
loft deck + secondary joists (9 psf) | 2,565
solar-slope assembly (9.5 psf actual surface) | 3,975
hip-cap assembly (6.6 psf actual surface) | 1,581
upper panel walls/girts (4 psf gross) | 2,681
balcony deck and guards | 408
Primary steel + 10% connection allowance | 9,233
TOTAL | 20,443
The solar-slope budget is 9.5 psf of actual surface: approximately 2.4 PV, 2.6 metal/foam panel, 1.0 waterproofing/details and 3.5 secondary framing. Cap budget is 6.6 psf of actual surface. These are allowances, not a selected tested roof system. The manufacturer panel reference is steel-faced; the desired aluminum-faced assembly must be priced and weighed separately.

Measured roof surfaces in the model total 418.43 sq ft of solar slope and 239.58 sq ft of hip cap. Their intersecting takeoff is retained conservatively. Wall weight uses gross area with no opening deductions. Primary connection weight is an allowance, with no connection stiffness or capacity established.


## Load cases

Service case | Total load, lb | Max vertical movement, in
occupied | 44,734 | 0.488
storage bands | 55,747 | 0.644
full125 | 68,958 | 1.102
patch1000 | 45,734 | 0.558
Occupied = D + 40 psf floor live + 20 psf projected roof live. Storage bands = 125 psf in 36-inch north/east/west strips, 40 psf elsewhere, plus D and roof live. Full125 applies 125 psf everywhere. Patch1000 adds 1,000 lb directly at B2 midspan to the occupied case. Balcony live allowance is 60 psf.

Strength search cases are 1.2D + 1.6 band-load + 0.5 roof-live, and 1.2D + band-load + 1.6 roof-live. These are selected study combinations, not an exhaustive code envelope. Full125 and patch1000 are service sensitivity checks, not fully strength-qualified design cases. The 0.75-inch maximum movement search limit is a study tolerance, not a member-specific code deflection check.


## Column reactions: perimeter storage case

Column | With S3, lb | Without S3, lb
W1 | 2,424 | 2,453
W2 | 9,975 | 9,963
W3 | 1,840 | 1,839
W4 | 5,203 | 5,162
S1 | 85 | 85
S2 | 4,996 | 12,815
N1 | 7,640 | 7,680
N2 | 14,999 | 15,664
S3 | 8,585 | 0
These are service vertical base reactions. S1 contributes only its own 85 lb: including a column in the model does not connect it to the roof. Removing S3 moves S2 from about 5,000 to 12,800 lb. The CSV includes column shears and base moments for every case; footing demand cannot be reduced to axial load alone.


## Candidate sections from the bounded search

<b>Analytical trial sections only.</b> A500 Grade C square HSS, Fy = 50 ksi. Dimensions are outside size and nominal wall thickness in inches. Catalogue properties are from Atlas Tube. These sections have not passed connection, lateral stability, foundation or full code checks.

Member family | Trial square HSS
B-WO:beam | 3x3x0.188
B2:beam | 8x8x0.313
B3:beam | 6x6x0.375
O2:beam | 6x6x0.375
O3:beam | 2x2x0.188
T-E:chord | 6x6x0.25
T-E:web | 3x3x0.125
T-N:chord | 4x4x0.188
T-N:web | 3x3x0.125
T-S:chord | 2x2x0.125
T-S:web | 2x2x0.125
T-SO:beam | 8x8x0.313
T-W:chord | 6x6x0.25
T-W:web | 3x3x0.188
T1:chord | 5x5x0.188
T1:web | 2x2x0.125
columns | 4x4x0.188
The result is not uniformly thin tubing: T-E and T-W use 6-inch chords, while the transverse T1 uses 5-inch chords. Their stiffness and frame action matter. The very light T-S result depends on the assumed east-west roof spanning direction and must not be generalized to a different roof layout.

All columns were screened as 4 x 4 x 0.188. This does not establish that 4-inch posts are adequate: the first-order base restraint and lateral system remain assumptions, and second-order effects are omitted. W-sections, rectangular HSS, cold-formed members and timber trusses were not optimized in this search.


## Sensitivity and member-force checks

Model variation | Storage movement, in | Y lateral movement, in
Baseline | 0.644 | 0.918
column bending stiffness 25% | 0.663 | 1.745
truss bending/torsion stiffness 25% | 1.046 | 2.583
pinned column bases | 0.651 | 1.957
without optional S3 | 0.648 | 1.015
The lateral runs use an arbitrary 20 psf gross-area pressure for sensitivity only. They are not San Diego design wind pressures. Uplift uses an equally diagnostic 20 psf case. No wind or seismic adequacy conclusion follows from them. Reduced truss stiffness increases movement substantially, showing why real joints cannot be left unspecified.

Group | Compression, kip | Bending, kip-ft | Max screen ratio
T-S | 1.03 | 0.51 | 0.280
T1 | 8.10 | 16.46 | 0.890
T-W | 5.47 | 12.95 | 0.718
T-E | 10.97 | 3.54 | 0.856
T-N | 10.09 | 8.14 | 0.698
B2 | 0.00 | 27.22 | 0.340
B3 | 0.06 | 14.43 | 0.292
T-SO | 0.00 | 8.22 | 0.138
Values are independent maxima anywhere in each group, not simultaneous forces on a single member. Full axial tension, shear, torsion and case-by-case envelopes are in member-group-demands.csv. The ratio is an internal screening metric, not an AISC certification.

Screening uses the AISC E3 column curve, elastic bending yield, a conservative linear axial/biaxial interaction and an approximate shear/torsion screen. K = 1 and chord brace spacing at most 72 inches are assumed. Those brace points must be provided and designed. End-connection local yielding, punching, welds, bolts, gussets and tube-face flexibility are not checked.


## The 1,000 lb item: floor framing

Simple joist check: span 115.25 inches, spacing 16 inches, 9 psf dead plus 40 psf live, with the entire 1,000 lb placed at midspan of one joist. This is deliberately localized; load spreading through the plywood has not been established.

Member | Live movement, in | Bending demand
wood 1.5 x 7.25 in; E=1.6e6 assumed | 0.552 | 2,881 psi
wood 1.5 x 9.25 in; E=1.6e6 assumed | 0.266 | 1,770 psi
HSS3x3x0.125 | 0.816 | 31,808 psi
HSS3x3x0.188 | 0.590 | 23,081 psi
HSS4x4x0.188 | 0.234 | 12,171 psi
L/360 here is 0.320 inch. A single 2x8 fails that movement screen. A 2x10 meets this one deflection screen but still needs a species/grade and adjusted bending capacity of about 1,770 psi. HSS 4x4x0.188 also meets this isolated movement screen, at about 9.42 lb/ft versus an assumed 3.37 lb/ft for the wood 2x10. Neither is a complete floor design.

For low weight, the present comparison favors investigating wood or engineered-wood joists with a deliberately reinforced storage pad. Steel cold-formed joists may be competitive but need a separate local/distortional-buckling design. The plywood must be checked for the actual contact footprint; placing a heavy item above a primary support is much more useful than averaging it over the loft.


## Secondary roof framing

An isolated square-HSS purlin screen at 4 ft spacing over 18 ft 8-1/4 in gives HSS 5x5x0.25 as the lightest listed candidate meeting the selected L/240 and elastic stress screens, at 15.62 lb/ft. This is already roughly 3.9 psf on projected area. A lighter roof therefore needs efficient purlin profiles or a shorter effective span; thin cladding alone does not make the roof light. Cold-formed Z/C purlins and their restraint details were not designed here.


## Reproducibility, limits and engineering handoff

Python model: 438 nodes and 541 frame elements; six degrees of freedom per node, Euler-Bernoulli bending, axial stiffness and Saint-Venant torsion. E = 29,000 ksi. Tests verify cantilever bending, axial extension, torsion and simply supported point-load bending. Each run checks force and moment equilibrium and free-degree residuals. The shear-seat option uses statically condensed end releases.

Run frame_solver tests, then study.py for the baseline, then extra_checks.py. The two variant directories retain their own results and analytical geometries. Use TRUSS_OPTION=triangulated for the triangulated variant; add SHEAR_SEATS=1 for the shear-seat variant. Frozen source geometry is included in inputs/. make_report.py uses saved results and ReportLab; plot_report.py uses Matplotlib. NumPy and SciPy are required for analysis.

The section search selects from a finite square-HSS catalogue, updates self-weight after changes, and downsizes member families while meeting selected strength and movement screens. It is a local search with grouped sections, not a mathematical minimum. Model equilibrium does not verify that the assumed physical load path or joints can be built.

Before final sizing, a California licensed structural engineer needs to establish occupancy and storage design loads; site wind/exposure and seismic parameters; lateral system and diaphragm forces; second-order stability; actual joint stiffness, gussets and welds; beam seats and eccentricities; member-specific deflection and floor vibration; roof collectors and purlins; snow/rain/ponding and uplift cases; column baseplates/anchors; and footing soil, bearing and overturning capacity. The existing wall/slab reserve has intentionally not been presumed.


## Primary references

<link href="https://www.sandiego.gov/development-services/codes-regulations" color="#126080">San Diego current codes</link>

<link href="https://www.sandiego.gov/development-services/forms-publications/information-bulletins/140" color="#126080">San Diego residential addition/remodel guidance</link>

<link href="https://www.atlastube.com/wp-content/uploads/2018/04/A500-Square-Current.pdf" color="#126080">Atlas A500 square HSS catalogue</link>

<link href="https://www.canadiansolar.com/wp-content/uploads/sites/3/2026/01/CS-Datasheet-TOPHiKu6_All-Black_CS6.1-54TM-H_v1.4C25_F23_D2_TX.pdf" color="#126080">Canadian Solar module dimensions and weight</link>

<link href="https://metlspan.com/wp-content/uploads/2022/11/PSF-Panel-Weights_2019.pdf" color="#126080">Metl-Span panel weight reference</link>

<link href="https://www.aisc.org/globalassets/aisc/publications/standards/a360-16w-rev-june-2019.pdf" color="#126080">AISC 360-16 with revisions: E3 formula reference</link>

<link href="https://steeltubeinstitute.org/hss-tools/" color="#126080">Steel Tube Institute section and availability resources</link>

Sources inform this screen; they do not establish compliance with the currently adopted 2025 California codes. The 40/125 psf scenarios are explicit study assumptions pending use classification, and manufacturer weights do not certify the proposed integrated solar roof assembly.
