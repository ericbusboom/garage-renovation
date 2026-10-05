# Nezha 4P4C to Qwiic adapter

Status: requirements and tooling prepared on 2026-10-05. Physical 4P4C contact assignment and source voltage remain unverified. This directory contains no fabrication-ready PCB or machine program.

## Requested construction

- Small passive adapter: female 4P4C handset jack, four-position header physically in the middle, and a Qwiic receptacle at the opposite end.
- One copper side and surface-mount components, intended for Makera Carvera milling and outsourced fabrication.
- Two nominal 3.0 mm non-plated holes for plastic heat-staked rivets. Hole positions and clearance for the melted heads will be set with the enclosure layout.
- Start with one board; arrange multiple copies into a milling panel after the prototype and stock dimensions are checked.
- Proposed middle header: vertical male, 2.54 mm pitch; awaiting user preference. Proposed header order is GND, 3V3, SDA, SCL.

The header is an electrical tap: each of its pins shares one net with both other connectors. No removable shunts are needed to maintain continuity.

## Signal mapping

| Net | Nezha cable color, from user notes | Middle header, proposed | Qwiic contact | Qwiic wire |
| --- | --- | --- | --- | --- |
| GND | Black | 1 | 1 | Black |
| 3V3 | Red, voltage to confirm | 2 | 2 | Red |
| SDA | Yellow / signal 1 | 3 | 3 | Blue |
| SCL | Green / signal 2 | 4 | 4 | Yellow |

Qwiic is a 1 mm JST-SH interface with 3.3 V power and logic. SparkFun documents its [pinout, colors, and connector part number](https://www.sparkfun.com/qwiic). The Nezha color associations above are user-supplied observations, not verified manufacturer contact numbers. `wiring.csv` deliberately leaves the jack contact column empty.

The reported latch-side order was yellow–green–red–black; its reversal is black–red–green–yellow. The separately reported bottom view was black–red–yellow–green. Before assigning a footprint, resolve that discrepancy and map the actual cable into the chosen jack's numbered solder terminals. Check both cable ends; do not assume a handset cable is wired straight through.

ELECFREAKS' [Nezha V2/Pro page](https://wiki.elecfreaks.com/en/microbit/expansion-board/nezha-v2/) specifies 3.3 V sensor power, but its title and SKU table disagree. Its [older Inventor's Kit V2 page](https://wiki.elecfreaks.com/en/microbit/building-blocks/nezha-inventors-kit-v2/product-description/) specifies 3.4 V sensor power. Identify the board and measure red-to-black voltage before deciding the passive connection is suitable for the intended Qwiic device. A 5 V source would require power regulation and assessment of I2C level shifting.

## Candidate components

| Ref | Candidate | Selection status |
| --- | --- | --- |
| J1 | [Amphenol 73306-111LF](https://www.amphenol-cs.com/product/73306111lf.html) | Manufacturer lists a 4P4C, right-angle, surface-mount receptacle. Candidate only; drawing, mating orientation, pad numbering, and footprint need verification. |
| J2 | [Samtec TSM-104-01-L-SV](https://www.samtec.com/products/tsm-104-01-l-sv) | Four-pin 2.54 mm vertical SMT male header, pending preference and land-pattern check. |
| J3 | [JST SM04B-SRSS-TB(LF)(SN)](https://www.jst-mfg.com/product/pdf/eng/eSH.pdf) | Standard right-angle Qwiic receptacle; KiCad footprint is installed. |
| H1, H2 | 3.0 mm NPTH | Actual 3.0 mm holes, not a generic M3 clearance-hole footprint. |

The installed JST footprint uses 0.6 mm-wide signal pads on 1.0 mm centers, leaving 0.4 mm gaps. Choose the isolation tool and cutting depth to fit with margin, then check a test coupon. Keep generous trace widths and spacing elsewhere. Avoid vias for the milled version; if the confirmed pin order forces an impractical crossing, revise placement or provide an explicitly documented SMT zero-ohm bridge. Do not add pull-ups automatically; check those already present on the bus.

## Buzzkill tooling

Passwordless SSH and `sudo -n` verified as `ros@buzzkill.local`; hostname is `buzzkill`. Host runs Ubuntu 26.04 LTS. Installed from its configured Ubuntu repositories:

| Tool | Installed version | Purpose |
| --- | --- | --- |
| KiCad | 9.0.8 | Schematic capture, PCB layout, rule checks, Gerber and drill exports |
| KiCad symbols, footprints, 3D packages | 9.0.7 | Component libraries |
| ngspice | 45.2 | Optional circuit simulation |
| gerbv | 2.10.0 package | Independent Gerber viewing |
| Xvfb | Ubuntu package | Headless viewer checks |

KiCad's Python PCB interface also imports successfully. A passive connector adapter primarily needs connectivity, footprint, and clearance checks rather than SPICE analysis.

The installed StickHub example was used solely to verify schematic PDF, Gerber, and separate plated/non-plated Excellon drill exports. A standalone simulator check returned 3.3 V as expected. These are tool checks, not validation of the proposed adapter.

The gerbv package reports unsupported X2 attributes on KiCad's default exports. A second export using `--no-x2 --no-netlist --disable-aperture-macros` rendered successfully with no viewer diagnostics. Package audit completed without errors. Temporary verification outputs are on Buzzkill at `/tmp/nezha-eda-check.CF89eQ`; they are disposable example files, not adapter fabrication files.

## Manufacturing workflow

Keep one editable KiCad design as the source. Run electrical and board design-rule checks after completing the schematic and routing, then compare the exported nets and footprint pad numbers to the measured cable mapping.

- **Outsourced boards:** export Gerber layers, board outline, separate non-plated drills, and an assembly drawing/BOM. Specify nominal board thickness and copper weight after component and stock review. A fabricator may supply a standard two-layer board with all routing on the front; do not assume a single-sided order from the artwork alone.
- **Carvera:** export front copper and outline as RS-274X Gerbers without X2/netlist attributes or aperture macros if required by the CAM importer, plus millimeter Excellon drills using the same origin. Review orientation, isolation, drills, and perimeter toolpaths in CAM. Put tabs/bridges and panel spacing in the panel/CAM design after stock size, cutter, and fixturing are known.

[Makera CAM](https://www.makera.com/pages/makera-cam) imports Gerbers, but its official download page lists Windows and macOS, not Linux. Use it on the machine-control workstation with exports from Buzzkill. No machine-specific G-code has been generated and no machine motion has been commanded.

Next needed inputs: cable orientation/contact mapping, exact Nezha model and voltage, and middle-header preference. Stock dimensions and cutting-tool details can wait until panelization.
