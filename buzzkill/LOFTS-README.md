# Existing loft reconstruction — south boundary framing revision 004

EXISTING-LOFTS-004 supersedes the previous provisional platform bounds. Existing-Garage.FCStd contains the three revised lofts, with the prior walls and globally clipped roof unchanged. Proposed-Garage.FCStd is unchanged. The backup directory in lofts-agent-result.json preserves the earlier loft reconstruction and exports.

Dimensions below use core outside coordinates (X east, Y north); owner measurements originate at the INSIDE southwest corner, x=6,y=6 inches. All floor joist bottoms remain98.5 inches, tops104 inches, and0.75-inch deck tops104.75 inches. Wall cores remain6 inches. Roof rafters retain the global98.5-inch underside cut with no roof relayout.

## South platform

The measured west start is explicitly **69 inches from the inside west wall**, hence **x=75**. This is not rounded to the surveyed third roof station at70 inches. The owner clarified that the platform stops after five support positions. Interpreting this as four approximately24-inch bays gives96-inch width and east edge **x=171**, not the inside east wall. The free/north edge support is **47 inches from the inside south wall**, hence **y=53**. Deck bounds are x75..171,y6..53 inches:96 inches wide and47 inches deep.

The north/free-edge and south/wall-side boundary joists each comprise three full-width plies spanning **x3..246.5** on the east/west wall tops. The southern triple assembly replaces the former single board as an explicit interpretation of “between two joists.” Its Y extent is6..10.5; the north assembly remains y48.5..53. N–S crossmembers stay under the narrow deck, shortened to y10.5..48.5 between the two assemblies; there are five cross-framing positions with approximately24-inch spacing and an adjusted final bay to keep all timber inside the deck edges. Two wood hangers follow the actual deck edges at assumed12-inch insets (bottom x87 and159). The left hanger now targets the extant SouthNear4 roof member; the right now targets SouthFar4. Their positions, slopes and stitch plates are schematic connections, not newly measured construction details. Attachment points are checked against the unchanged roof shapes.

## Main platform

The first support is measured **72 inches from the inside south wall**, giving center y78. The five main assemblies retain prior relative spacings provisionally: **y78,102,126,151,175**. This shifts the whole main framing/deck14 inches north. The four later centers remain unmeasured.

Each assembly retains three1.5×5.5-inch on-edge plies. End faces remain provisionally at wall midlines x3 and246.5. The central deck remains x54..195.5, leaving48 inches open from each inside east/west wall. Revised deck Y extents are75.75..177.25, spanning the four bays and end assembly edges. Bolted construction is described without inventing bolt locations. These shifted references no longer assert exact alignment with the unchanged modeled roof.

## North platform

The west bound aligns with the garage-door west jamb, **x56.25**. The owner confirmed that the east end is25 inches **WEST of the east jamb**, inside the opening: east jamb x221.25 gives **x196.25**. The platform is140 inches wide. Its29-inch depth remains y214..243.

Single-ply edge and cross framing follow the narrower platform. Two schematic thin metal straps follow its bounds with assumed12-inch insets (bottom x68.25 and184.25), targeting existing NorthNear3 and NorthFar3 roof members. Strap sections/count and precise connections remain assumptions.

## Survey differences preserved explicitly

The three measured south-side N–S roof station offsets from the inside west wall are17.5,46,70 inches (17.5, then28.5, then24). These convert to core X23.5,52,76. The unchanged model has X16,40,64 for the corresponding initial stations: differences7.5,12,12 inches. The measured south second support at core Y53 differs from modeled second station Y40; main first support at core Y78 differs from modeled third station Y64. These discrepancies are recorded in lofts-parameters.json and lofts-revision-input.json. They do not authorize a full roof relayout.

## Files and editing

SouthLoft, MiddleLoft and NorthLoft are separate native groups with individually toggleable Deck objects. LoftParameters under Dimensions exposes measured bounds, provisional offsets and section inputs as inch-valued expressions. Major width/spacing changes require regeneration to update member counts. No external Python proxy is needed to open/edit the file.

loft-generator.py rebuilds the revised native lofts when run with **--replace-lofts** after verifying a backup. It reads the revision survey file and records it with the model. Existing-Garage-lofts.step and visible-mesh-lofts.json include walls, roof and lofts. visible-mesh-lofts-only.json includes only the revised loft geometry. Older roof-only exports remain unchanged.

Validation checks native reopen, visible geometry, deck toggles, joist/deck elevations, measured bounds, all five main centers, actual roof anchor containment, restored parameter edits, prior61 wall/roof solids unchanged, global roof datum preserved, and Proposed unchanged. Unknown reclaimed horizontal floorboards remain documented but unmodeled. Connection intersections and fastenings are schematic; no structural capacity or exact joinery claim is made.

Revision003 changes only the south loft geometry. Middle/north lofts and all existing wall/roof solids are compared geometrically with the pre-revision file and preserved. The narrow deck, crossmembers, hangers and plates remain within x75..171. Revision004 intentionally extends the six boundary joist plies to x3..246.5. South decking and hangers are verified geometrically unchanged.

Revision004 changes only south boundary framing and the crossmember lengths needed to fit between it. Deck x75..171,y6..53 and its69-inch inside-west offset are unchanged. Both full-width boundary assemblies have joist bottoms98.5 inches and tops104 inches, on the existing wall-top level. North and middle lofts remain unchanged. Full-width bearing/joinery details remain schematic.
