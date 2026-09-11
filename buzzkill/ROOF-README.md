# Existing roof framing prototype

Existing-Garage.FCStd now contains the existing walls plus a roof framing prototype. Proposed-Garage.FCStd remains the independent walls-only starting copy, byte-for-byte unchanged. Timestamped backups under backups/ preserve both original FCStd files; roof-validation.json records their hashes and backup path. Existing-Garage.step and visible-mesh.json remain the prior walls-only exports; use Existing-Garage-roof.step and visible-mesh-roof.json for the roof-inclusive model.

## Explicit assumptions awaiting owner confirmation

The owner confirmed **1.5-inch framing thickness and ON EDGE orientation**. All reclaimed stock is modeled as flat rectangular **1.5 × 5.5 inch boards ON EDGE**, including hips and ridge. The owner also has 5-inch boards, but their locations are unknown, so none are assigned arbitrarily. Soffit thickness is a **0.75 inch placeholder**. No tongue-and-groove profile is invented. This is a useful editable geometry prototype, not structural analysis or an exact joinery model.

## Roof and eave layout

The centered north–south ridge is 18 inches long, with its upper edge at wall height + approximately 60 inches. Four hips connect eave corners to the corresponding ridge ends. Soffit projects 3.5 inches from the outer stucco face, top at wall-top height. The 0.75-inch fascia sits beyond the soffit; its bottom aligns with the soffit underside, and its 3.5-inch height extends upward. Eave framing upper edges meet fascia top. Roof slopes follow these elevations and runs; hips are not forced to 45-degree plan angles. Bearing elevations and pitch are exposed in roof-parameters.json and the roof spreadsheet.

All 40 jack-rafter tails and four hip tails have native parametric horizontal underside cuts at soffit top (98.5 inches) across their entire footprints, including over the walls and hip corners; this global datum supersedes the earlier eave-only cuts. Ends are also trimmed at fascia inside faces to prevent fascia penetration. The roof upper slope and ridge remain unchanged; the outer eave profile stays represented by fascia and the hidden covering reference. Contact at soffit top is allowed; no positive clearance gap is invented. Lateral intersections at hips/ridge may overlap; other joints, birdsmouths, notches and bearings remain unresolved. No precise fit or capacity is claimed. The eave alignment follows upper-edge datums, not a fabricated seat detail.

Rafters begin 16 inches from each core wall corner and continue at 24-inch stations from both ends. Central residual bays are 25.5 inches on north/south and 25 inches on east/west. With this exact pattern the 18-inch ridge lies between adjacent stations: there are **40 jack rafters, four hips and one ridge board; no common rafter station lands on the ridge**. The separate Common and jack rafters group preserves the intended organizational role. Adding central common rafters requires a layout decision rather than an invented station.

## Editing and visibility

Soffit, Fascia, Hip rafters, Ridge, and Common and jack rafters are independent groups. Source stock and trim cutters are hidden; final native intersections are visible. All stock uses native Part::Box, Part::Common and tail Part::Cut features within native App::Part placements, with spreadsheet expressions; no external Python proxy is needed to reopen/edit. Edit Roof dimensions — ASSUMPTIONS under Dimensions. The global stock dimensions and roof rise update native member geometry. Individual member start/end vectors, runs, pitch and yaw are inspectable in its matching native axis-dimensions object under Dimensions (the member assembly links to it). The fixed five-station-per-end topology requires regeneration for substantial layout changes.

There is **no roof sheet/cladding**. Cover edge — hidden reference only contains a plan perimeter one inch beyond fascia. This static native wire is a footprint reference, not a sloped roof surface, and must be regenerated for footprint changes.

Saved GUI view providers and isometric camera are verified through native reopen. Offscreen OpenGL is unavailable, so the parent should render visible-mesh-roof.json for a preview. Its vertices are in millimeters and include global placements. roof-validation.json records shape validity, expression edit/restore, preserved walls, unchanged Proposed hash, and STEP checks.

The generator imports the included roof_tail_tools.py solely during construction; opening/editing the FCStd requires no external Python code. correct-roof-tails.py records the earlier eave correction; correct-global-roof-datum.py records the superseding global underside correction.

Run roof-generator.py using the bundled /opt/freecad-1.1.3/usr/bin/python with QT_QPA_PLATFORM=offscreen. It refuses to add a duplicate roof. Review assumptions before generating another model, and regenerate from a backed-up walls-only Existing file in a separate directory. The generator exits explicitly after verification to avoid the bundled GUI interpreter teardown crash.

## Tail correction validation

Request RAFTER-SOFFIT-CLEARANCE-002 checks each of the 44 corrected members against all four soffit solids and all four fascia solids, with common volume below 0.0001 mm³ per pair. It also checks single-solid validity, native reopen visibility, unchanged walls/eave components/ridge, and a framing-thickness expression edit restored to 1.5 inches. See roof-validation.json for actual intersections, clearances and removed volumes, and roof-agent-result.json for result status. A timestamped pre-correction backup preserves the prior model and exports.

## Global underside datum — owner correction

RAFTER-GLOBAL-DATUM-003 requires every jack and hip rafter to have no material below Z = 98.5 inches (2501.9 mm), including the portions over walls. Native horizontal Part::Box cutters cover complete members in their correctly transformed App::Part frames; final Part::Cut outputs remain editable. No rafters were shifted inward. Original section thickness remains 1.5 inches, on edge, with 5.5-inch nominal depth away from the underside cuts. Upper roof envelopes, ridge, walls, soffit and fascia are preserved. Validation checks global minimum Z within 0.000001 mm, below-plane volume below 0.0001 mm³, soffit/fascia collision volumes, native reopen visibility and a restored thickness edit.
