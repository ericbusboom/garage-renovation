# Exposed loft joist / W-beam connection study

**Date:** 2026-09-21  
**Status:** architectural concept — not for construction

This study applies the current `loft-span-study` geometry to the exposed floor:

- three east-west rolled beams over the 23 ft 5 1/2 in span;
- 2x8 DF-L joists at 16 in o.c., spanning about 7 ft 7 in between beams;
- W12x16 at the project's 40 psf live-load reading (W16x26 if the floor is instead
  required to carry the 125 psf storage reading);
- W12x16 dimensions used in the drawing: `d = 12.0`, `bf = 3.99`, `tw = 0.220`,
  `tf = 0.265 in`.

## Recommended visual direction

Use a **flush tucked joist on an engineered steel seat**. Each joist terminates at
the W-shape web; the joist on the other side is a separate aligned piece. A shallow
top cope clears the top flange, while a continuous or intermittent steel ledger/seat
inside the web pocket carries gravity. Small side clips provide the positive attachment,
uplift and rotation restraint. Painted wood hides nearly all of it; the steel beam reads
as one dark line crossing a regular field of wood cells.

For a W12x16, the theoretical flange projection beyond the web is about 1.885 in and
the flange is 0.265 in thick. The concept therefore needs roughly a 5/16 in deep by
1 7/8 in long cope plus fit and root-fillet clearance. These are layout dimensions,
not an approved connection detail. The seat, welds or bolts, end shear, beam-web local
strength, lateral restraint, tolerances and erection sequence all need engineering.

This is preferable to relying on the lower flange: a 7.25 in joist seated on the lower
flange would finish roughly 4.5 in below the W12 top.

## Other connection families

1. **Top nailer + listed top-flange hanger.** The most conventional route. Bolt a wood
   nailer to the steel beam and use a listed hanger suited to the nailer/steel condition.
   It is easy to inspect, but either raises the floor plane or leaves more connector
   visible. A blackened or dark powder-coated hanger can make the repetition intentional.

2. **Weldable top-flange hanger.** Several Simpson top-flange families have weldable
   variants. This avoids a wood nailer, but every weld and hanger is visible and must be
   specified for the actual load, steel and uplift condition.

3. **Concealed knife plate / proprietary connector.** This gives the purest wood-only
   appearance, but the small products still generally need timber thicker than a single
   1.5 in 2x8. Rothoblaas ALUMIDI's US data recommends at least 3 1/8 in timber width;
   SHERPA's steel/concrete series is likewise aimed at engineered timber. This becomes
   realistic if the joists change to doubled members, LVL or glulam, not ordinary single
   2x8s.

4. **Exposed architectural clip.** A custom bent plate or side clip in blackened steel
   or bronze can be attractive if every fastener line is disciplined. It is less quiet,
   but more honest and easier to inspect than a faux-concealed detail.

## The service floor

The proposed layered floor is sound in concept, with one important refinement:

1. exposed 2x8 joists;
2. 1/2 in A-grade plywood as the visible ceiling plane;
3. sleepers aligned over the joists;
4. wiring, drivers and junction boxes in the service cavity;
5. 23/32 in T&G structural subfloor above;
6. finish floor.

Use **2x3 sleepers on edge** when possible, giving a 2.5 in service cavity. That is much
friendlier to low-profile fixtures, conduit and junction boxes than a flat 2x4's 1.5 in
cavity. The final diaphragm/load path must be designed so the upper subfloor is properly
fastened through the sleepers to the framing.

If the cavity must remain 1.5 in, ordinary cable is too close to fasteners from one face
or the other. NEC 300.4(A)(1) uses 1 1/4 in edge clearance, or steel protection where
that cannot be maintained. A deliberate EMT layout is the cleanest minimal-depth answer.
Keep all junction boxes accessible through removable lights or planned access panels;
do not bury them between the two decks.

## Simpler alternative: close the joists from below

The east lean-to makes a raised service floor optional. It can serve as a hidden
distribution spine running north-south. Branch one circuit or conduit into each bay
between W-beams, then distribute within that bay through centered holes in the joists.
This is a particularly clean plan because no cable needs to cross a W-shape web.

Use ordinary listed hangers on an engineered wood nailer or a hanger specifically
listed for the steel/nailer condition. A thin furring layer below the joists can clear
hanger seats, create a continuous fastening plane, and isolate the ceiling finish from
small framing irregularities. Drywall, veneer plywood with expressed reveals, or T&G
wood can then close the joist cavities. The W12 remains exposed roughly 4 3/4 in below
the ceiling because it is 12 in deep while a 2x8 is only 7 1/4 in deep.

For sawn 2x8s, the IRC-style boring limits are a maximum hole diameter of one-third
the joist depth (2.42 in for a 7.25 in joist) and at least 2 in between a hole and the
top, bottom, another hole or a notch. A roughly 3/4-1 in wiring hole centered vertically
is comfortably inside that geometric envelope. Put longitudinal cable runs on a joist
side, not sandwiched between the joist top and subfloor, and preserve required protection
from finish fasteners. Engineered wood products require their manufacturer's hole chart
or a specific engineered design instead of these sawn-lumber rules.

## The shallow arch

Do **not** field-cut a shallow arch out of the bottom of the already-sized 2x8. That
removes the tension edge near midspan, where bending demand is largest. The concern is
especially sharp under the 125 psf storage interpretation: the current span study puts
the uncut 2x8 at DCR 0.96.

If the arch is worth the extra craft, start with a deeper engineered member—nominal
2x10, LVL or glulam—and engineer a smooth routed/tapered profile that preserves at least
the required net depth at midspan. Avoid a square re-entrant corner. A shop-cut glulam
or LVL also pairs naturally with a proprietary concealed connector.

## Sources consulted

- American Wood Council, *2018 NDS*, section 4.4.3: end notches no deeper than one
  quarter of member depth; interior notches limited and prohibited in the middle third:
  <https://awc.org/wp-content/uploads/2021/10/AWC_NDS2018-withCommentary_20200827_AWCWebsite_Chapter04.pdf>
- Simpson Strong-Tie, top-flange hanger options for steel frames with nailers and
  weldable applications:
  <https://www2.strongtie.com/products/strongframe/resources/hangers.asp>
- Simpson Strong-Tie, hanger option matrix (concealed flanges, nailer and weldability
  options):
  <https://www.strongtie.com/products/connectors/wood-construction-connectors/technical-notes/hanger-options-matrix>
- Rothoblaas ALUMIDI, concealed hangers for timber/steel connections and US NDS data:
  <https://www.rothoblaas.com/products/fastening/brackets-and-plates/concealed-connections/alumidi>
- SHERPA CS connectors, concealed systems for wood to steel/concrete:
  <https://tie-in-timber.sherpa-connector.com/en/onlineshop/cs-connectors/>
- NFPA material quoting NEC 300.4(A)(1), including 1 1/4 in edge clearance and steel
  protection where it cannot be maintained:
  <https://docinfofiles.nfpa.org/files/AboutTheCodes/70/70_A2022_NEC_P03_FD_PIResponses.pdf>
- ICC code text for sawn-joist drilling: holes no larger than one-third the member
  depth and at least 2 in from the top, bottom, other holes and notches:
  <https://codes.iccsafe.org/content/FLRC2014/chapter-5-floors>
- AISC Engineering Journal, design aids for engineered web openings in W-shapes. This
  is why electrical openings in the steel should be designed, not improvised in the field:
  <https://ej.aisc.org/index.php/engj/article/view/1293>

## Outputs

- `joist-hanger-options.png` — review image
- `joist-hanger-options.pdf` — printable sheet
- `joist-hanger-options.svg` — editable vector sheet
- `closed-ceiling-electrical-option.png` — direct-ceiling review image
- `closed-ceiling-electrical-option.pdf` — printable direct-ceiling sheet
- `closed-ceiling-electrical-option.svg` — editable direct-ceiling vector sheet
- `draw.py` — regenerates both sheets in PNG, PDF and SVG
