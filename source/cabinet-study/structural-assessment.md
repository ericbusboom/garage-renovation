# Cabinet / beam support assessment — preliminary

## Conclusion
The cabinet steel frame could potentially be incorporated into an engineered support system. These photos and outside dimensions do not establish an allowable support load. For beam selection, give the existing cabinets **no verified structural credit yet**; this is not a claim that their physical capacity is zero. A licensed structural engineer needs to verify the members, connections, bracing and foundations before new building loads are applied.

The weak slab identified at the start of this project is a central issue: cabinet legs concentrate load into small areas. A frame capable of carrying a load is not sufficient if its base, slab or soil cannot carry the reaction. New dedicated posts and designed foundations integrated into the cabinet layout are a candidate solution. Their locations and foundation design require site review.

Being attached to or partly supported by the existing roof joists is not evidence that the cabinets can support replacement beams. Determine which existing connections carry gravity loads and which provide lateral restraint. The proposed load path cannot loop from the new beam through a cabinet back into the roof it is meant to support.

## Provisional geometry
- Cabinet run assumed on EAST wall; this has not been confirmed.
- Six doors interpreted as three 48-inch paired openings, with four 1-inch upright faces: total run 148 inches.
- 49.5 inches assumed measured from inside south-wall face. With 6-inch south wall, first upright begins at y55.5; upright centers y56,105,154,203, measured from south outside face.
- East wall6 + pegboard0.25 + cabinet30 puts cabinet front at x213.25, measured east from west exterior face. The stated quarter-inch is treated as pegboard thickness, not an additional air gap.
- Original Canvas cross-beam centers y69.75 and185. East longitudinal beam center x211.5: transverse offset to cabinet face1.75in. Actual upright section orientation, bearing width and joints must be measured.
- Current west row at x−32. Trial bearing-line span to east rail is243.5in (20ft3.5in). Original internal cross-members require designed extension/connections to that moved west row; dashed lines show intent only. This is not a fabrication length.

## What the layout reveals
Both interior cross-beams land between cabinet uprights. A continuous transfer beam/header is required unless supports are deliberately relocated or added. For a SIMPLY SUPPORTED 49-inch header bay with a single downward point load P:

| Beam y | Distances from adjacent post centers | South-post share | North-post share | Peak header moment |
|---|---|---|---|---|
|69.75in|13.75in and35.25in|0.719P|0.281P|9.892P lb-in if P is lb|
|185in|31in and18in|0.367P|0.633P|11.388P lb-in if P is lb|

These are idealized demand relations, not proof that the cabinet top rail is suitable. A continuous rail will have different moment/reaction distributions; cabinet dead load, contents and other beam loads are additional. Neither division assumes four posts share a beam reaction equally. The door leaves, hinges, pegboard and unverified wood infill are not counted as structural bracing.

## Beam-depth analysis: what can be computed now
For a simply supported beam between the trial bearing lines, L=20.2917ft, with uniform line load w:
- End reaction R=wL/2.
- Maximum bending moment M=wL²/8.
- Elastic midspan deflection δ=5wL⁴/(384EI), using consistent units.

For EACH100lb/ft of line load, the demands are1,014.6lb per end and5,146.9lb-ft maximum moment. This is a normalization, **not a proposed design load**. Convert actual area loads to line loads using the tributary floor/roof width, then include beam self-weight, concentrated loads and appropriate load combinations. Roof and floor framing directions must be established first.

No beam depth is selected: material/grade, actual loading, support conditions, lateral restraint and deflection criteria are unknown. A larger beam depth may improve stiffness but does not establish bearing, connection or foundation capacity. An east-side cabinet support primarily provides an end support; it does not halve the across-garage span.

## Information needed for a capacity calculation
1. Confirm cabinet wall, the49.5in reference face, and whether48in is each pair or each leaf.
2. Measure frame section: closed tube vs angle/channel, 1x2 orientation, wall thickness, steel grade/condition, full post height and effective unbraced lengths.
3. Record top rails, welds/bolts, beam seats/cap plates, rear members, base plates/anchors and how the frame reaches the ground. Identify gravity support from existing joists.
4. Investigate slab thickness/reinforcement/condition and any independent footings; establish soil/foundation capacity.
5. Establish proposed beam material/grade, joist direction, supported floor/roof area, floor use/storage loads, roof/PV weight, wind/seismic/uplift loads and serviceability criteria.

Checks then include beam flexure/shear/deflection; transfer-header flexure and local bearing; column buckling and eccentric loading; connection strength; lateral stability; slab/footing/soil reactions. Local building requirements and the completed load path must be reviewed by the project engineer.

## References
- [AISC — Stability of Slender Section HSS Columns](https://www.aisc.org/education/continuingeducation/education-archives/stability-of-slender-section-hss-columns/): wall slenderness, member length and local/global buckling affect column capacity.
- [Steel Tube Institute — HSS Limit States in Cap Plate Connections](https://steeltubeinstitute.org/resources/hss-limit-states-cap-plate-connections/): concentrated loads require local HSS wall checks; a member's axial capacity alone is insufficient.
- [FEMA — Structural design criteria](https://www.fema.gov/pdf/plan/prevent/rms/453/fema453_ch2.pdf): continuous structural load paths.

No existing cabinet, joist, beam or slab has been certified by this desk study. The plan and demand equations are for developing the design and identifying the required checks.
