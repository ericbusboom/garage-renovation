# Nezha 4P4C to Qwiic adapter — revision A

A 44 × 24 mm passive adapter with a 4P4C receptacle, a four-position 0.1-inch male header in the middle, and a top-entry Qwiic receptacle. All components are surface mounted; all routing is on the front copper. Two 3.00 mm non-plated holes accept heat-staked enclosure posts. Designed 2026-10-05.

**Status:** prototype CAD and manufacturing exports complete. KiCad reports zero electrical-rule violations, board-rule violations, unconnected items, and schematic/layout mismatches. The saved CAD and exported schematic netlist also match the independent pin table. No physical prototype or machine toolpath has been tested. This study is separate from the garage project's controlled structural drawings.

## Files

- [Editable KiCad project](design/nezha-qwiic.kicad_pro), [schematic](design/nezha-qwiic.kicad_sch), and [PCB](design/nezha-qwiic.kicad_pcb)
- [Schematic PDF](exports/schematic.pdf) and [board drawing PDF](exports/board.pdf), viewed from the component side
- [Scalable board preview](exports/board-review.svg)
- [Fabrication ZIP](exports/nezha-qwiic-revA-fabrication.zip) and [Carvera milling-input ZIP](exports/nezha-qwiic-revA-milling-inputs.zip)
- [Parts list](parts.csv), [wiring table](wiring.csv), and [validation results](checks/validation.json)

The ZIP packages and raster previews are generated files excluded from Git; their unpacked source files are retained. A working copy and the installed EDA tools are on Buzzkill at `/home/ros/projects/nezha-qwiic`.

## Wiring and assembly

| Signal | Nezha cable color | J1 contact | J2 male header | J3 Qwiic contact | Qwiic wire |
| --- | --- | --- | --- | --- | --- |
| GND | Black | 1 | 1 | 1 | Black |
| 3.3 V | Red | 2 | 2 | 2 | Red |
| SDA | Yellow | 4 | 3 | 3 | Blue |
| SCL | Green | 3 | 4 | 4 | Yellow |

The user confirmed 3.3 V sensor power and clarified the plug colors: latch-side left-to-right yellow–green–red–black; contact-side black–red–green–yellow. The drawing convention is plug nose away and cable toward the viewer. The selected Kycon jack's front view has the latch below the contacts, with contact 1 at the left and contact 4 at the right. Its PCB top-view solder-pad order is reversed, as shown in the manufacturer drawing.

J2 has one straight row of four male pins at 2.54 mm pitch. Its SMT solder tails alternate sides; this is not a two-row header. With J1 on the left in the board preview, J2 runs from GND at the top through 3V3 and SDA to SCL at the bottom. The header is a tap into the four lines and needs no removable shunts.

**Fit R1, an insulated-body 1206 zero-ohm resistor.** It carries SCL over the SDA trace to make the crossing possible with one copper layer. Do not replace it with a solder blob or a bare conductor touching the board. The board adds no pull-ups, regulator, or level conversion.

Before first power, plug in the actual unpowered cable and check continuity from each cable color to the labeled J2 pin, including the wiring of both cable ends. Check for shorts between adjacent signals and between 3V3 and GND. This confirms the physical plug orientation and assembly against the CAD assumptions.

## Selected parts and footprint sources

| Ref | Part | Notes and source |
| --- | --- | --- |
| J1 | Kycon GMX-SMT4-N-44 | Right-angle, latch-down 4P4C SMT jack; `-TR` changes packaging. Custom footprint from [Kycon drawing](https://www.kycon.com/Pub_Eng_Draw/GMX-SMT4-N-44.pdf), revision A8. |
| J2 | Samtec TSM-104-01-L-SV | Four-position vertical male SMT header, no alignment-pin or locking-clip options. Custom footprint from [Samtec recommended land pattern](https://suddendocs.samtec.com/prints/tsm-1xx-xx-xx-sv-xx-xxx-xx-footprint.pdf), revision D. |
| J3 | JST BM04B-SRSS-TB(LF)(SN) | Top-entry, 1 mm SH connector. Use **BM04B**, not the horizontal SM04B version. [JST SH drawing](https://www.jst-mfg.com/product/pdf/eng/eSH.pdf). |
| R1 | 1206 zero-ohm resistor | Insulated ceramic body required for the trace crossing. |
| H1, H2 | Board features | 3.00 mm NPTH; no purchased metal fastener required. |

The JST and resistor footprints derive from KiCad library version 9.0.7, under the [KiCad library license](https://www.kicad.org/libraries/license/); the installed package's [attribution and license text](design/KICAD-LIBRARY-COPYRIGHT.txt) are retained. The JST mechanical mounting pads have been given blank pad numbers; their geometry is retained. Custom symbols and footprints are included with the project. Qwiic's power, signal order, and cable colors follow [SparkFun's Qwiic specification](https://www.sparkfun.com/qwiic).

## Mechanical dimensions

- Finished board: 44.00 × 24.00 mm rectangle, nominal thickness 1.60 mm.
- Hole diameter: 3.00 mm, non-plated. Centers are (4.00, 3.00) and (40.00, 21.00) mm, measured from the upper-left board corner with X right and Y down in the component-side drawing.
- A nominal 5 mm diameter head area is kept clear around each hole; match the enclosure's post length and melted head to the actual board thickness.
- J1 opening faces left; the body is approximately 11.5 mm high. J2's pin row is at X = 29.50 mm, with Y = 8.19, 10.73, 13.27, 15.81 mm. J3 is top entry; allow clearance for its cable above the board.

The rendered PDF is a review drawing. Use CAD or Gerber geometry for machining and check print scaling before using a paper template.

## Outsourced fabrication

The fabrication ZIP includes front and blank back copper, masks, top silkscreen, paste, outline, non-plated drill file, and order notes. A conventional two-layer order works, with all routing on the front and no back copper. Suggested prototype specification: FR-4, 1.6 mm, 1 oz copper, two 3.00 mm NPTH, top solder mask and silkscreen. A fabricator can alternatively quote a single-copper-layer board from the same geometry. No fabrication order has been placed.

## Carvera milling

The milling ZIP contains front copper and board outline as RS-274X Gerbers, the NPTH Excellon file, and CAM notes. The milling Gerbers omit X2 and netlist attributes and aperture macros, and rendered successfully in gerbv with no diagnostics.

Use copper-up stock. All files share the upper-left board origin: exported X = 0…44 mm and Y = 0…−24 mm. Do not mirror this component-side artwork or independently reposition the drill and outline files. The outline is the finished perimeter, not a cutter-center path.

Tracks are 0.40 mm wide; the design-rule minimum copper clearance is 0.30 mm. The Qwiic pads have 0.40 mm gaps. Choose an isolation tool with effective cutting width comfortably below the smallest gap; a 0.20 mm effective width leaves margin. Actual cutter shape, runout, cutting depth, and stock flatness determine what the machine can achieve. Review the toolpath and cut a coupon before the first board.

[Makera CAM](https://www.makera.com/pages/makera-cam) accepts Gerbers and provides Windows and macOS downloads; run it on the machine-control workstation. Stock size, copper thickness, tool inventory, and fixturing are still needed to choose cutting parameters and panel spacing. No machine-specific G-code is included. Panelization is the next manufacturing step after prototype fit and continuity are confirmed.

## Buzzkill tools and regeneration

Passwordless SSH and sudo were verified at `ros@buzzkill.local` (Ubuntu 26.04 LTS). Installed from the host's Ubuntu repositories: KiCad 9.0.8; symbols, footprints, and 3D libraries 9.0.7; ngspice 45.2; gerbv 2.10.0; Xvfb; and librsvg rendering tools. A passive adapter needs connectivity and clearance checks; no circuit simulation is needed for this design.

From `/home/ros/projects/nezha-qwiic`:

```sh
python3 scripts/build_adapter.py > checks/geometry.json
bash scripts/export_adapter.sh
python3 scripts/package_adapter.py
```

The build script overwrites the generated schematic, PCB, project settings, and local libraries. After manual CAD edits, run only export and packaging to preserve those edits. Export runs KiCad ERC and DRC with schematic parity, then independently checks pad nets, the schematic netlist, the header pitch, front-only tracks, and the actual exported drill locations. Packaging records checksums in `exports/SHA256SUMS.txt`.
