# Roof-first construction study

9 September 2026, corrected roof revision. Concept planning for keeping the existing garage usable between construction operations. No existing design files or post coordinates have been changed. This is not an erection plan or structural approval.

## Corrected existing roof — latest user instruction

The original `Canvas 1.svg` has labels of 23 ft 10¼ in and 20 ft 9½ in. For this requested redraw, use a provisional north–south wall length of 286.25 inches and east–west width of 249.5 inches. The original long dimension extends beyond the drawn wall endpoints; applying it to the wall footprint is a working assumption, not a newly verified survey.

Walls are 98.5 inches high. Four triangular roof planes meet at one central point, 58 inches above the walls, at Z156.5 inches (13 ft ½ in). There is no ridge segment. `existing-roof-parameters.json` controls this study; older CAD/site models have not been regenerated.

The unchanged proposed frame at Y253 now lies 33.25 inches SOUTH of the provisional north wall. The earlier north-first exterior-column sequence is therefore conditional on revising or confirming the layout. Do not use the previous four-inch north clearance or 48.4-inch T1 clearance. The updated T1 geometric gap is about 56.4 inches. Full-depth truss conflicts remain. The proposed north roof extent also needs reconciliation before claiming full roof coverage.

`existing-garage-corrected.png/pdf/svg` shows the full roof in plan, 3D and elevations. `roof-clearance.png/pdf` has been regenerated with the corrected geometry. Off-center slices through a pyramid have flat-topped section profiles; these are not a flat top or ridge in the physical roof.

## Finding

A new, independently supported roof above the existing garage is a plausible direction. The current full-depth truss scheme cannot be erected intact around the retained roof. Roof surface clearance and framing clearance are different constraints.

The preferred alternative to develop is a permanent roof-only frame on independent foundations, with the loft floor and conflicting lower framing installed after the old roof is removed. It must support the roof and resist lateral loads without T1's present lower chord/web system, the future floor diaphragm, or the old building. Simply omitting parts of the currently analyzed trusses would invalidate their load paths.

## Drawing basis and conflicts

Basis: `existing-roof-parameters.json` and the latest user correction for the existing pyramid roof; `structural-analysis-v5/inputs/framing-member-register.json`, its model basis, and `geometry_builder.py` for proposed geometry. The original model's high illustrative proposed beam elevation is superseded. Revision 5 investigates B2 alternatives and omits B3; its copied register still contains B3, so that register is not a final member schedule. This study does not choose a B2 alternative.

- Old walls: Z98.5 inches; central peak: Z156.5 inches. Existing roof has four triangular faces and no ridge segment. Overhang is unknown and modeled as zero; actual rafters, ties, ceiling joists, sheathing thickness and projecting details are not surveyed framing.
- New roof underside: Z106.5 at Y−63, rising at 30 degrees to Z227.25, then level in the reference underside profile. The upper hip cap is separate from this underside clearance check.
- T1 at Y69.75: old roof surface reaches Z126.766; new roof underside Z183.143. Approximately 56.4 inches of geometric space is available at the tightest cross-sectional location. This is before new member depth, connections, deflection and working clearance. The present T1 lower chord at Z98.5 and its webs occupy the old roof envelope.
- T-E at X224.25 is 25.25 inches inside the east wall. S2 and N2 can be outside the south and north walls while the member joining them still crosses the old roof. A roof-level longitudinal girder between exterior end supports could be studied; an exterior east support row is another alternative, subject to site space and access. Neither is sized here.
- T-W at X0 is above the existing west wall, whereas W1–W4 lie at X−32. Using full-height west posts directly for roof support changes the current transfer arrangement and needs a new load-path design. Unknown eaves and the adjacent shelter must be checked.
- North posts W4/N1/N2 at Y253 lie 33.25 inches inside the provisional north exterior wall at Y286.25. Post widths, base plates, actual eaves and foundation excavation can overlap existing construction. Moving outward is an alternative, not an assumed relocation.
- W1/S1/S2 remain at Y−21.25 while T-SO is at Y−63: 41.75 inches of offset. The outer beam needs real support or a designed transfer; the existing documents leave this unresolved. S3 is optional at the south-wall line, not an unobstructed exterior post.
- T-S occupies the south wall/eave line. It may require a local eave/connection modification or redesign; zero-overhang geometry cannot establish installation clearance.
- B2 and future floor framing at the wall-top/loft elevation should be deferred where they conflict with existing roof framing. No ability to slide beams through the existing attic is assumed.

## Sequence to develop

1. **Survey and settle the roof-only scheme.** Record real roof/eave edges, gutters, utilities, footing edges, boundaries, shelter obstructions, door travel and crane access. Check both final member locations and the space required to rotate, lift and connect them. Model all retained roof framing and future removal routes.
2. **Build independent foundations in accessible groups.** Resolve the north clearance, east support strategy and south offset before locating foundations. Design excavation around existing footings and maintain the garage approaches. Do not assign building, crane, shoring or brace-anchor loads to the weak slab without separate verification.
3. **Start a stable exterior bay.** After resolving the revised north-wall position, the north/west corner is a candidate staging area: W4/N1/N2 with W3 and a west return, provided door and shelter access allow. This is a planning priority, not a lifting order. An engineered combination of columns, connecting members and bracing must stabilize each erection stage in both directions. A lone north frame does not establish a stable three-dimensional system.
4. **Extend exterior framing south.** Work through W2 and the southern supports in connected, braced increments, with corresponding east/end roof supports. Full-height columns can reduce later splices, but their erection and long-term unsupported lengths must be checked. Column length is set by actual bearing elevations and foundation detail, not an arbitrary 20- or 30-foot stock length.
5. **Erect the complete roof-only support system.** Install members whose entire physical envelope and lifting path clear the old roof. Roof-level beams/rafters or shallower trusses replace the current dependence on conflicting full-depth T1/T-E members during this stage. Include the permanent lateral system or engineered long-duration bracing. Neither old roof nor future loft is credited as restraint.
6. **Complete roofing and drainage.** Install the specified deck/purlins, bracing, roof covering, flashings and gutters. Roof covering is not automatically a structural diaphragm. Design the open-sided stage for its actual wind exposure and uplift. Allow ventilation/drainage between roofs and retain an access/removal route for the old roof.
7. **Pause with both roofs present.** This is the useful long-duration milestone: new roof structurally complete and weather-managed, garage operational below. Review inspections, corrosion protection, drainage and bracing retention for the actual duration. Keep daily access routes clear.
8. **Remove the old roof under the new one.** Schedule garage closures during overhead work. Establish protection and a demolition sequence that preserves old-wall stability, since roof ties and diaphragms may restrain those walls. Remove manageable sections through the planned route; do not assume old members can be craned vertically through the completed roof.
9. **Install the loft and deferred framing.** Use the revised final design. If temporary supports were used, transfer loads under an engineered procedure before releasing them; fitting a member into place does not automatically transfer existing roof load to it.

## Alternatives

**Permanent roof-first structure:** best fit to the owner's goal of long pauses and minimal interior disruption. It may require different member sizes, more exterior supports, a higher roof or revised upper-wall/floor framing. Preserve the current roof profile only if the remaining structural and working envelope proves sufficient.

**Temporary independent support followed by load transfer:** can preserve more of the final full-depth truss design, but requires two structural states, temporary works and a controlled transfer. More complicated for a multiyear build.

**Local roof openings with temporary weather closures:** may reduce redesign but relaxes the strict goal of retaining the whole old roof until the new one is complete. It still requires checking how cuts affect rafters and wall restraint.

## Engineering basis for staging

The previous gravity studies do not verify a roof-only construction stage or tall columns without the completed frame. Each long-duration stopping point needs its own stability and load-path checks. OSHA requires structural stability throughout steel erection and addresses installation and removal of plumbing-up equipment: https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.754 . AISC discusses the engineering of staged stability and temporary bracing: https://learning.aisc.org/local/catalog/view/product.php?productid=2030 . These sources support the staging principle; they do not establish this project's member or foundation capacities.

The accompanying section figure is a geometric screen, not a fabrication drawing. Gray shading marks the old roof envelope, not solid material. Orange lines illustrate truss chords/verticals; omitted diagonals and connection volumes can add conflicts. No member sizing is implied by drawn line thickness.
