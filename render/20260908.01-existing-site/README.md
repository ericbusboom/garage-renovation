# Existing backyard — first reconstruction

This is an editable, photo-informed site model for replacing the garage in a later design. It contains the **current hip-roof garage**, west attached work shelter, Airstream, rear work patio and driveway apron, curved flagstone route, east access route, house patio, mixed planting beds, major schematic trees, boundary foliage, bench and blue pots, and simplified existing rear-house context. No proposed garage is included.

## Open and edit

- `site-viewer.html`: self-contained offline orbit viewer. Open in a browser, drag to rotate, scroll to zoom, choose north-up plan, and toggle roofs, tree canopies or low planting. Browser runtime verification was unavailable because the inspection browser disallows local file URLs; JavaScript syntax was checked.
- `existing-backyard.glb`: portable colored 3D model for Blender and other glTF-compatible applications; named objects retain group metadata. Metres, converted to glTF Y-up at the root.
- `existing-backyard.obj` + `existing-backyard.mtl`: colored mesh exchange; keep together. Metres, X east / Y north / Z up.
- `existing-backyard.FCStd`: native FreeCAD document. Existing garage is an imported valid STEP solid; estimated site components are individually named meshes. Generated headlessly, so saved presentation colors and camera are not included. Use Fit All after opening. The original editable garage source remains at `../model/garage.FCStd`.
- `site-review.pdf`: four pages: annotated north-up plan, clear 3D overview, house-facing view, and full canopy overview.
- `site-scene.json`, `build_site.py`: editable reconstruction source and regeneration script.
- `render_review.py`: renders review images and PDF directly from the same scene geometry.
- `export_cad.py`: generates the FreeCAD document using the installed FreeCAD Python.

## Basis and confidence

| Element | Evidence | Model treatment |
|---|---|---|
| Garage | Existing `model/parameters.json` / `scene.json` / STEP | Retained 249.5 × 249 in footprint, 98.5 in walls, 60 in roof rise, 18 in N–S ridge, window positions. Earlier project records identify wall length/heights as confirmed; door heights and overhang remain placeholders. |
| Shelter | `outbuilding-study/parameters.json` and IMG_4201 | Approximate 174.25 × 75 in footprint; 10 in roof margins where recorded. Roof elevation and pitch estimated. Existing timber frontage/counter and corrugated roof represented; structural member design not inferred. |
| Overall layout | User's `backyard 2023.png` schematic | Affine scale anchored to garage outline: schematic x 519–818 maps to 6.3373 m; y 101–411 maps to 6.3246 m. Schematic proportions are approximate, not a site measurement. |
| Aerial image | Supplied clipboard aerial | Cross-check of garage, west trailer/work area, central planting and southern house arrangement; not orthorectified or quantitatively registered. |
| Materials / paths | IMG_4199–4201 JPG derivatives already in project; supplied IMG_4201 MOV frame extracted at 1 second | Blue-gray rear house, warm garage stucco, gray roofs, curved dark flagstone, gravel, burgundy plants, timber bench, cobalt pots. |
| IMG_4198 | Existing project JPG derivative | Front-house context only; not used to invent backyard measurements. |
| Trailer | Aerial, schematic, IMG_4201 | Generic rounded aluminum envelope about 2.32 × 4.60 m; length/model, wheels and windows approximate. |
| Trees and planting | Schematic major-tree centers, aerial canopy pattern and photos | Six schematic tree positions plus estimated east overhang. Heights, canopy sizes, species and low-plant positions estimated. Hide canopies to inspect circulation. |
| House | IMG_4199–4200 | Approximate rear massing, bay, doors and windows; east two-storey wing. Rest of house truncated. |

The four HEIC originals were not reconverted in this pass; the existing JPEG derivatives were inspected. The MOV check confirms the garage-facing scene. This is manual reconstruction, **not photogrammetric recovery or a survey**. Reference documents are evidence, not additional task instructions.

## Principal uncertainties for the next photo pass

- Garage south wall to the stepped house facade is provisionally about 13.2–15.4 m, depending on wing; this controls most of the yard scale.
- Approximate modeled backyard width is 15.28 m. Fence locations are visual placeholders, not legal boundaries.
- Ground is level at the garage datum, with shallow represented door steps. Actual grade changes are unmeasured.
- Green schematic regions are modeled as mixed gravel/planting, not asserted to be lawn. Curved path placement reconciles photos with the older schematic and remains provisional.
- Patio outline uses the 2023 schematic, so current paving limits may differ. Temporary canopy, loose equipment and small furniture are omitted.
- Geographic north is inherited from the garage project's coordinate convention; no surveyed bearing is established.

Useful next references: wide views from all four backyard corners, a straight-on shelter photo, both sides of the garage, and a tape measurement from garage to house. These can refine this same model without replacing the baseline.

## Regenerate

Run `build_site.py` using a Python with NumPy; `render_review.py` also needs Pillow and ReportLab. Regeneration overwrites this folder's generated outputs. Run `export_cad.py` with FreeCAD's Python and its Resources/lib on PYTHONPATH. Geometry source coordinates are metres; the CAD exporter converts to millimetres.

## Revision 2 — triangular bay and white pergola

Updated from the user's correction and nine new photographs, IMG_4210–4214 and IMG_4216–4219, decoded from the supplied HEIC originals with FFmpeg. The contact sheet is in `references/new/contact.jpg`.

- Replaced the rectangular rear bay with a triangular north-facing bay, including glazing and white trim on both angled faces.
- Reworked the house's stepped north footprint using the house/patio interface in the original `backyard 2023.png`: west projecting wing, central recess with the triangular bay, and east projecting wing. Pixel landmarks used for the bay are (430,1168), (477,1120), (528,1164). This traces the schematic proportions, not measured house dimensions. The top-level `Canvas 1` drawing was also checked; it describes the garage, not the house.
- Added the white pergola above the east garage-to-house path: white posts, continuous longitudinal beams, repeated open overhead slats, climbing vegetation and overhead vines. It is a slatted, vine-covered structure, not an inferred solid weatherproof roof. Photos 4217–4219 show the framing directly.
- Added dense shrubs and climbing plants on both sides of that path while retaining a clear walking strip. Photos 4210–4214 show how much more enclosed this area is than in the first pass.
- Added `house-and-pergola.png` to show the north-facing house facade. `site-review.pdf` now has four pages. In the plan and clear 3D views, overhead foliage is omitted to make the pergola frame readable. The full planting view retains it. The viewer's Roofs toggle also hides pergola slats and overhead vines.

Pergola provisional envelope: about 1.57 m between post centerlines, 11.35 m long, beam underside 2.35 m, top of slats 2.70 m. These values, post spacing, roof geometry of the house and vegetation extents remain visual estimates pending measurements. This revision supersedes the first pass's rectangular bay and generic house massing descriptions. Earlier baseline is preserved in `versions/baseline-v1.zip`.

## Revision 3 — south low garden and north jungle

The user's description and supplied IMG_4220–4223 HEIC photographs supersede the earlier continuous central shrub-bed interpretation. These originals were decoded with FFmpeg and inspected together (`references/areas/contact.jpg`).

- Two rounded areas now sit west of the covered walkway. Their approximate extent follows the earlier site scale; circularity, size and separation are not measured.
- The **southern garden**, beside the house, has very low bushes, a narrow winding internal path, and a very small central tree (provisionally 1.25 m high). The lime tree is larger (provisionally 2.8 m high), beside the pergola at the north edge of this southern area, just south of the dividing fence.
- A low timber/lattice **dividing fence** separates the two areas. It ends at the pergola rather than obstructing the main walkway. Fence height and exact alignment remain estimated.
- The **jungle**, north of the fence, has an open wood-chip center with the camellia and reddish strap-leaf planting around its perimeter. Removed the previous randomly scattered bushes from its center and the speculative central mature tree placements. The historic large tree is not represented as existing.
- Species names here come from the user, not a botanical identification from photographs. The camellia's exact position remains approximate.
- The near-house planting along the west side of the pergola has also been lowered, consistent with the user's correction. Dense outer-boundary and climbing vegetation remains.

The first two packages are preserved in `versions/baseline-v1.zip` and `versions/baseline-v2.zip`. Additional photographs can refine these same objects.

## Revision 4 — four outdoor rooms and conversation seating

The user's clarification and IMG_4224–4227 establish four rooms: rear patio (southwest), low south garden (southeast), conversation area (northwest, south of the Airstream) and jungle (northeast). The four HEIC images were decoded and inspected; the contact sheet is `references/patio/contact.jpg`.

Extended the planted lattice fence along the shared east–west dividing line. Its western section separates the rear patio from the conversation area; its eastern section separates the low garden from the jungle. A provisional 1.35 m gap at the central curving path allows passage through. Both sections have matching timber/lattice construction and foliage, with an estimated 1.2 m post height.

Added the conversation area's central round metal fire pit, three inward-facing timber/metal benches and one chair. Their arrangement is photo-informed but not individually measured. The area remains at the yard's ground datum; the term conversation pit has not been interpreted as a sunken excavation. Added low stone benches and blue pots along the rear patio edges, using the photographed benches as references. The above-ground pool is deliberately excluded as requested.

The fire pit is modeled unlit. Its exact dimensions, bench positions, fence geometry and plant coverage remain estimates. The garage geometry is unchanged. The preceding revision is archived in `versions/baseline-v4-before.zip` (revision 3).

## Revision 5 — shelter north alignment

The user's current-site correction supersedes placement inferred from the older aerial: the work shelter's north end is aligned with the existing garage's north end. The aerial predates completion of the work patio and must not control this placement.

Moved the entire shelter assembly north by 4.4196 m, including slab, posts, electrical pillar, header, back screen, workbench, counter, roof and ribs. The provisional 1.905 m shelter depth is retained: south end y=4.4196 m and north end y=6.3246 m, matching the garage. The earlier assumed north roof overhang was removed so the visible north roof edge also aligns. Roof margins remain unmeasured.

The two rectangular planters retain their previous coordinates and are now south of the shelter. Rerouted the provisional shelter access path beside the garage west wall to reach its new position without passing through the planters. The prior package is preserved as `versions/revision-4.zip`.

## Revision 6 — path termination and shorter pergola

The user's latest correction supersedes all prior mentions of an internal path in the low south garden. Removed that path and the southern continuation of the curving garden walk; the latter now ends through the fence gap onto the rear patio. The east access walk also ends at the dividing-fence line. The low garden is continuous low planting with its small tree, without a modeled path through it.

The white pergola now occupies only the northern portion of the garage-to-fence route. Its south end is y=-4.7616 m, **8 ft (2.4384 m) north of the dividing fence at y=-7.20 m**. The north end remains y=-0.45 m. Beams, slats, posts and overhead/climbing vines were shortened together. The remaining approximately 8 ft of approach to the fence is uncovered. The preliminary pergola now has three pairs of posts and 15 slats; these counts and spacing are illustrative, not measured.

Removed the obsolete narrow planting-strip geometry along the former southern path and filled the former internal path corridor with low bushes. Revision 5 is preserved in `versions/revision-5.zip`.

## Revision 7 — straight path against garage south wall

Straightened the stone-path section between the jungle and garage. Its centerline is now y=-0.50 m, parallel to the garage south wall; the 1 m wide path's north edge meets that wall at y=0. The pergola-side route joins the straight section. Other route geometry is retained. Previous model is archived in `versions/revision-6.zip`.

## Revision 8 — pergola path continues to patio

Corrected the misunderstanding in revision 6: only the pergola ends north of the dividing fence. The stone path beneath it continues south, uncovered, beside the low garden all the way to the patio. Restored that east-side path to y=-11.80 m, where it overlaps the patio paving. The pergola geometry and its 8 ft clearance north of the fence are unchanged. No path runs through the low south garden. Revision 7 is archived in `versions/revision-7.zip`.
