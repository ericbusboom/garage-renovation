# Revised structural scheme — cabinet frames and piled columns

## Design basis
All specified exterior columns and beams are structural in intent. Exterior columns are reported on approximately18-inch diameter,36-inch-deep concrete pilings. Piling strength and rotational restraint are not established by those approximate dimensions.

Cabinet side frames P1–P4 are now explicitly included as proposed structural support locations. Existing verticals are reported2×1-inch,11-gauge steel. Replacement/strengthening is allowed, particularly atP2/P3, while preserving the1-inch dimension at door openings. The full cabinet side frame is interpreted as30in front-to-back and98.5in high. Local foundation work is permitted in the cabinet strip; no new columns or pilings in the open garage floor. No extra gravity support is assigned to existing walls in this baseline.

Target: at most10in overall beam depth provisionally; user originally said10in web. This is not a selected section or verified capacity. Beam depth changes from the old8in assumption will also affect the loft-floor/roof relationship unless framing is recessed or elevations adjusted.

## Revised geometry
- P1–P4 centers remain y56,105,154,203in from the exterior south face. East-wall cabinet location and the inside-face interpretation of49.5in remain assumptions.
- Garage-door opening: global x56.25 to221.25in. Trial6in jamb posts at x53.25 and224.25 lie just outside that opening, at north beam y253. These are opening-jamb locations, not literal building corners.
- North beam extends to garage east edge x249.5. It has an overhang beyond its northeast post, requiring a cantilever check.
- All four west posts retained at x−32. Original south supports at x148.5 and211.5 are restored.
- Longitudinal cabinet beam moved to x224.25, aligning with NE jamb post. This is11in inside the cabinet front and19in from its rear, within the30in-deep side frames. This replaces the preceding1.75in mismatch observation.
- South end of that relocated beam transfers through the south header: it is12.75in east of the original south post at211.5. This offset requires a header/cantilever/connection check; it is not a direct column bearing.
- New cross-beam bearing-line span:256.25in =21ft4.25in, if continuous from west row to cabinet beam. Any splices/extensions require design.

## Can only P2 and P3 be replaced?
Potentially, if the LONGITUDINAL beam and connections are designed to carry loads to them and the piled end supports. But simply making P2/P3 stronger does not ensure that load avoids P1/P4. The beam lands closer to P1/P4, and actual sharing depends on beam continuity, post/foundation stiffness, fit-up and settlement.

All four cabinet frames plus end supports give longitudinal segments77.25,49,49,49,50in. With P2/P3 and the two ends as the primary capacity-assured supports, those spans become126.25,49,99in. The latter is a sensitivity case to investigate a two-frame retrofit, not an instruction to remove or disengage P1/P4. If the existing frames remain in contact, their resulting loads must still be checked.

### Continuous-beam sensitivity — NOT actual building reactions
An equal-EI continuous rail was solved with point loads of1000lb at EACH cross-beam intersection (y69.75,185). Supports were vertically rigid, rotation free, no settlement; beam self-weight and all other loads omitted. Upward support reactions positive:

| Support | All four cabinet frames engaged | P2/P3 plus ends, sensitivity only |
|---|---:|---:|
|South header support y−21.25|−38lb|165lb|
|P1 y56|781lb|not credited in this sensitivity|
|P2 y105|245lb|932lb|
|P3 y154|348lb|687lb|
|P4 y203|744lb|not credited in this sensitivity|
|North jamb support y253|−80lb|216lb|

The all-frame case puts most of these normalized loads intoP1/P4. Negative end reactions mean this ideal model demands hold-down at those supports for this isolated load case; without tension-capable connections contact can lift off, requiring a different analysis. Gravity dead loads may change the sign. Do not apply these numbers as footing or post design loads. Equilibrium checks on force and moment pass in the calculation script.

## The10-inch depth target
The cross-beams, not just the north–south rail, merit attention. Cabinet supports reduce the rail's span lengths but do not reduce the approximately21ft4.25in width crossed by the transverse beams. A deeper cabinet frame cannot make that cross-span disappear.

For an illustrative floor framing arrangement spanning north–south between the transverse beams, the south interior beam has8.59375ft tributary width. The table assumes a simply supported steel cross-beam, E=29,000,000psi, with uniform area load converted to line load and deflection limited toL/360 under the ENTIRE illustrative load. It excludes beam self-weight, roof reactions, point loads, continuity, cantilevers, vibration and lateral stability. L/360 is an exploratory criterion, not the established governing code combination.

| Illustrative area load | Line load | Each end reaction | Maximum moment | Required bending inertia for that deflection target |
|---|---:|---:|---:|---:|
|50psf|430plf|4.59kip|24.49kip-ft|97.4in⁴|
|75psf|645plf|6.88kip|36.74kip-ft|146.1in⁴|
|100psf|859plf|9.18kip|48.98kip-ft|194.8in⁴|

These are alternative hypothetical loads, not prescribed floor loading and not cumulative. They identify stiffness to investigate; they do not establish a beam size. The actual supported floor and roof framing must be defined first. Width/flange thickness or a purpose-designed shallow built-up member can be explored within a10in envelope; stronger steel alone does not appreciably improve elastic stiffness. All candidates require strength, lateral-torsional buckling, shear, bearing, connection and serviceability checks. A nominal W10 label is not a guarantee of10in outside depth: use actual section dimensions.

## The1-inch-wide cabinet-frame constraint
The30in front-to-back depth provides room for a braced side frame and a top load-transfer member. Keep the one-inch door-gap dimension, but treat its out-of-plane stability as a separate problem. An X brace in the30in-deep side plane does not by itself brace the one-inch-thick frame against buckling toward the neighboring cabinet bay. Engineered inter-frame restraint/diaphragm connections can be explored without using the old walls for extra gravity load.

The cabinet top chord must transfer the beam reaction to the frame's legs; it cannot be assumed adequate just because it is connected to them. The illustrated X braces and top beam seat are conceptual, not a fabrication scheme. Connections, weld access, tolerances, corrosion, existing damage and local tube-wall effects must be checked. Do not assume ordinary I-sections fit within a1in door-gap envelope.

11 gauge is a reported description, not a verified tube wall thickness or material specification. We have not assigned an allowable capacity to existingP1–P4 or specified replacement thicknesses.

## Foundations and next engineering step
The useful scheme to develop is: all exterior piled columns retained, north jamb posts added, cabinet rail moved into the side frames, allP1–P4 included, with a sensitivity check for upgrading onlyP2/P3 and adding foundations in the cabinet strip. Foundation locations must account for front/rear frame reactions and overturning, not just the visible front upright. The slab cannot be credited as a footing without verification.

Before selecting10in-deep members: establish floor use/storage loads, actual roof/PV weights and load paths, joist directions, beam materials/grades, section thickness/orientation, connections/restraint, slab/soil/pile information and wind/seismic/uplift requirements. Have a licensed structural engineer verify the complete scheme and any selective foundation work. No need to assume added gravity capacity from the old walls for this investigation.

## Primary references
- [AISC Shapes Database](https://www.aisc.org/aisc/publications/steel-construction-manual/aisc-shapes-database-v160/) — actual dimensions and section properties for candidate member screening.
- [Steel Tube Institute: Effects of Slender Elements in HSS Compression Members](https://steeltubeinstitute.org/resources/effects-of-slender-elements-in-hss-compression-members/) — local and member buckling considerations.
- [Steel Tube Institute: HSS Brace-to-Column Connections](https://steeltubeinstitute.org/resources/hss-reference-guide-no-5-hss-brace-to-hss-column-connections/) — connection design is part of the bracing system.

This supersedes the earlier assumption that cabinet frames are excluded from the proposed support scheme. Inclusion as design support locations does not certify the present frames' capacities.
