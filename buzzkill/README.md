# Garage — existing walls only

- **Existing-Garage.FCStd** is the existing garage wall model.
- **Proposed-Garage.FCStd** is an independent editable starting copy of the same existing walls. No proposed design is modeled yet; changes to one file do not update the other.
- Neither file has a roof, slab, framing, columns, door leaves or glazing. Openings are actual holes.

Open either FCStd in FreeCAD. The saved view is isometric and fitted to the eight visible wall/stucco outputs. Walls, Exterior stucco and Dimensions are separate groups. Intermediate solids and opening cutters are hidden. The east wall has no openings, so its final output is a native box; other final wall outputs are native cuts.

Edit the labeled inch-valued cells in Dimensions → Dimensions — editable inches, then recompute. All geometry uses native Part::Box/Part::Cut objects and spreadsheet expressions, with no external Python proxy or generator dependency after opening. Width and length are the OUTSIDE faces of the 6-inch core. The separate 0.5-inch stucco is outboard. X points east, Y north, Z up. South/north offsets are measured from east; west offsets from south. Shared corners use non-overlapping butt joints. No construction assemblies beyond these layers are implied.

The supplied parameters define a 249.5 × 249 inch core footprint and 98.5 inch height. Windows have 48 inch sills and 24 inch heights. Entry height is 80 inches; garage opening height is 86 inches.

`validation.json` records valid solids, opening locations and dimensions, empty opening intersections, analytical net volumes, no overlapping layers, visible GUI providers, saved cameras and successful native reopen checks for both documents. The Width alias was temporarily increased by one inch to verify wall/opening expression updates, then restored before saving. `Existing-Garage.step` is an exchange export, not the parametric source. `visible-mesh.json` contains per-object vertices, triangle indices and colors in millimeters for preview rendering.

The offscreen Qt backend does not support OpenGL screenshots here. Native view providers and stored cameras are checked; visual appearance in a hardware-rendered GUI was not inspected. The mesh is supplied for preview. The bundled GUI Python crashes during interpreter teardown; after writing and verifying all outputs, the generator explicitly exits without that teardown.

To regenerate, use a NEW directory containing copies of generator.py, existing-parameters.json and this README (the script refuses to overwrite existing model/result outputs), then run:

```sh
QT_QPA_PLATFORM=offscreen FONTCONFIG_FILE=/etc/fonts/fonts.conf /opt/freecad-1.1.3/usr/bin/python /path/to/new/directory/generator.py
```

`agent-result.json` is the machine-readable result for request EXISTING-GARAGE-WALLS-001. File retrieval is the temporary remote communication workaround; it does not repair app response retrieval.
