# Revised concept: deep perimeter trusses, shallow B2

User's new requirement supersedes the all-members ten-inch limit: only B2 has an eight-inch overall structural-depth target. South, east, west and north framing may use deep trusses, provisionally 24 inches. B1 and B-N are explicitly trusses (latest user revision). Their existing drawing IDs are retained. B-N remains the north floor-edge truss, separate from raised north-wall truss T-N. Its depth and chord elevation must be coordinated around both the loft and ground-floor garage-door openings; no chord location is approved by this plan change. Cabinets remain nonstructural. Keep the proposed east-wall column at Y126 provisionally; no calculation yet establishes that perimeter trusses eliminate it.

## Framing arrangement to develop

- Southernmost beam is a storage truss. It is distinct from B1 at the south edge of the loft. Rectangular cabinet bays can be incorporated, with diagonals in selected end bays and moment-resisting rectangular bays where access is needed. Cabinet weights must be added to the south truss load case; previous study did not include them. Existing south support locations make this a multi-support member, so diagonal locations must follow the analyzed shear distribution rather than appearance alone.
- East-wall truss replaces the former cabinet-bearing rail, centered over the new independent steel support. It can use conventional triangular web bays where openings do not matter. New footing and connections remain required.
- Add a west-wall truss at X0. It cannot bear on the old wall by assumption. Retain the exterior post row at X−32 and design transverse transfer members/outriggers for the 32-inch offset. Alternatively new independently founded posts at the wall line would be a different scheme. No exterior post is removed or declared nonstructural. West loft doors/balcony must remain unobstructed; final chord elevation and door portals need coordinated elevations.
- B2 spans between X0 and X246.5: 246.5 inches, or 20 ft 6½ in. This is a shorter support span than the last 23 ft 2½ in scheme, conditional on the new west-wall truss and its foundations/transfer framing being effective bearings.
- North raised truss sits over the seven-foot loft door, with jamb posts/side framing. If the underside of the roof structure is ten feet above the loft floor, there are 36 inches above a nominal seven-foot door: a 24-inch truss concept can fit with nominal space for a rough opening and connections. Nine feet leaves exactly 24 inches above the door with no such allowance. These dimensions refer to roof underside, not outside roof height.
- The north floor-edge member is still required: raising a roof truss over the door does not automatically support the floor below it. Develop a floor collector and jamb/side-frame or hanger load path that also clears the ground-floor garage door. Do not insert a truss chord or diagonal across either door opening.

## B2 numerical screen

Reproducible script `truss_revision.py`; output `truss-revision-B2.json`. This is a local member study, not a solved complete truss system. It retains the previous 12 psf floor dead, 40 psf center live and 125 psf three-foot perimeter storage bands; also evaluates 125 psf throughout. Two roof cases are included: prior roof loads retained on B2, and roof gravity bypassing B2 into new perimeter trusses. The latter requires explicit roof secondary-framing design. Balcony loads go to its separate exterior support framing. No composite action or fixed-end restraint is credited. Vertical bearings assumed immovable, omitting truss/connection deflection and settlement.

For storage bands:

| B2 alternative | Actual depth | Floor-only immediate deflection | Previous roof load also on B2 |
|---|---:|---:|---:|
| W8×31 | 8.00 in | 0.681 in | 1.008 in |
| Fabricated I: 8 in deep × 12 in flange width, ½ in flanges, ⅜ in web | 8.00 in | 0.431 in | 0.631 in |
| Fabricated I: 8 in deep × 12 in flange width, ⅝ in flanges, ⅜ in web | 8.00 in | 0.368 in | 0.536 in |

Fabricated sections are ideal rectangular-plate geometries for stiffness exploration, not weld/shop specifications. For reference L/240 is 1.027 inches and L/360 is 0.685 inches. W8×31 live deflection is 0.527 inches with the storage bands, but about 1.198 inches with 125 psf throughout; the latter fails the study's L/360 criterion. A fabricated 8×12 section with ⅝-inch flanges gives about 0.615 inches live deflection in that heavier case. Rolled W8×40 is 8.25 inches deep and therefore not eligible for the new strict depth limit.

These values omit steel shear deformation, connection slip, vibration, truss-bearing deflection, lateral-torsional buckling, local buckling, welds, bearing and lateral loads. They are not final strength or serviceability approval. W8×31 is a candidate for further study with roof gravity bypassing it; a wider fabricated eight-inch beam offers useful stiffness reserve. Do not assume truss-bearing deflection fits inside the remaining serviceability allowance.

## Truss engineering

A series of rectangular openings is not a stable pin-jointed truss. It needs Vierendeel/frame action and appropriately stiff moment connections, or additional triangulation. End diagonals alone do not make all interior joints suitable as pins. Roof, floor and storage reactions should meet designed panel points where possible; otherwise chord bending must be included. Connections, compression-chord bracing, load reversal and the three-dimensional lateral system need design. The existing posts' four-inch width does not establish bending or connection capacity.

Sources: [Nucor-Yamato section catalog](https://nucoryamato.com/staticdata/catalog.pdf), [Steel Tube Institute on rectangular HSS moment connections and Vierendeel systems](https://steeltubeinstitute.org/resources/square-rectangular-hss-hss-moment-connections/).

Architecture/model files are not yet changed: door-height/roof-cap changes and truss elevations remain a proposed revision. The prior full gravity analysis is retained as a record of its older assumptions, not a final analysis of this new scheme.
