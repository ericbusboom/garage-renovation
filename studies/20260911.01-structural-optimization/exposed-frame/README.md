# Exposed steel / inside metal panels

The native FreeCAD model uses all 88 selected members from the fixed-geometry weight-sizing study. The corrected north wall remains coplanar at y=253 in. W2 stays removed. Steel centerlines and selected section properties are unchanged; this is an architectural enclosure/rendering update, not another structural solve.

## Open

- `Garage-Exposed-Steel.FCStd`: native FreeCAD solid model.
- `Garage-Exposed-Steel.step`: exchange solids for other CAD programs.
- `Garage-Exposed-Steel.blend`: editable Blender scene, two cameras, materials and lighting.
- `01-southwest.png`, `02-northwest.png`: Cycles renders built from the exact CAD tessellation.

The project lives at `/proj/garage/optimization/exposed-frame` on Buzzkill, shared here as `/Volumes/Proj/Buzzkill-Proj/garage/optimization/exposed-frame`. A local working copy is under `/Volumes/Proj/proj/CAD/garage/optimization/exposed-frame`.

## Arrangement

The FreeCAD groups separate columns, each truss, bracing, future loft steel, floor/joists, interior metal panels, doors/windows, balcony, solar roof, hip roof cap and existing lower garage. Hide `InteriorMetalPanels` to inspect the framing alone. Hide `ExistingGarage` for the new assembly. The existing garage roof is omitted from this finished-renovation view.

Panels are light gray, nominal 2-in insulated infill for visualization, mounted inside the steel: west exterior panel face x=-28.5 in (east of TW), east face x=220.75 in (west of TE), north face y=249 in (south of TN). South upper infill is behind TS. Vertical panel joints are 24 in apart with small expressed seams. Panel attachments and weatherproof transitions are not detailed. No diaphragm or bracing credit is inferred from their presence.

The steel is dark painted metal. West balcony glazing is recessed, with white balcony floor and the frame exposed at the outer edge. North loading-door and adjacent window openings are retained in the infill. Lower walls/openings come from the measured existing FreeCAD model. Window/door leaves are illustrative infill, not purchased units.

The rear cap retains its referenced footprint, white 8-in fascia zone, soffit and 18-in hip rise. Roof reference lines describe the underside; the rendered metal skin lies above the fascia zone. The main 30-degree roof retains flush solar/glass panels and a metal weather skin; no elevated PV rack is added. Edge fascia encloses the reserved secondary roof zone. The secondary roof frame is not fabricated/detailed in this model.

## Editing and validation

Each steel member is a named native solid with member ID, stock section and source centerline metadata. HSS profiles use the selected nominal wall thickness; square corners and untrimmed member ends are simplifications. Changing a text property alone does not regenerate the shape: edit the JSON/generator and rebuild to keep geometry and metadata synchronized, or edit the native solid in CAD.

`cad-validation.json` records solid validity and selected steel weight; `reopen-validation.json` checks the saved model reopens, all section labels and lengths match the study, and solids are visible. `cad-mesh.json` is the same model triangulated for Blender, in inches. Blender converts to metres and adds only small bevel highlights/material finishes.

The selected steel remains a preliminary sizing candidate. Joints, crossing-brace offsets, cuts, fasteners, foundations and required lateral restraint are not fabrication-designed. This model does not revise or validate the prior structural load assumptions.

## Rebuild on Buzzkill

```sh
QT_QPA_PLATFORM=offscreen FONTCONFIG_FILE=/etc/fonts/fonts.conf /opt/freecad-1.1.3/usr/bin/python /proj/garage/optimization/exposed-frame/build_cad.py
QT_QPA_PLATFORM=offscreen FONTCONFIG_FILE=/etc/fonts/fonts.conf /opt/freecad-1.1.3/usr/bin/python /proj/garage/optimization/exposed-frame/check_cad.py
blender -b -t 16 --python /proj/garage/optimization/exposed-frame/render_blender.py
```

The CAD generator requires the measured `/proj/garage/Existing-Garage.FCStd` for the lower walls. Rendering requires only `cad-mesh.json` and `render_blender.py`; the saved Blender file is self-contained.
