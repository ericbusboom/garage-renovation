# Garage reconstruction — initial geometric model

Open `garage-viewer.html` in a browser to rotate the model offline. Drag to orbit,
scroll to zoom, or choose an elevation. Hide the roof to inspect the interior.
Roof rise and ridge length edits affect the preview only, not the saved CAD files.

## Files and editing

- `garage.FCStd`: native FreeCAD document. Wall and opening geometry retains
  editable Part boxes and boolean cuts. It includes saved object visibility,
  colors, and an isometric camera. Close an already-open older copy and reopen
  this file to load the corrected display settings. Expand an opening cut in the tree to
  edit the underlying cutter's Length, Width, Height, or Placement in the Data
  panel. Select a roof or group and press Space to toggle visibility.
- `garage-existing.step`: existing garage as CAD geometry in millimetres.
- `proposal-concept.step`: the proposed structure, separate from the existing
  building, with assumed heights. No foundations, connections or bracing inferred.
- `garage-existing.dae`: named meshes, metres, Z up, for COLLADA import.
- `garage-existing.obj`: named meshes, metres, Z up. Set import units to metres.
- `parameters.json`: editable measurements in inches. This is the regeneration
  source, including roof geometry. The Dimensions object in FreeCAD records
  values; it is not an automatically linked parameter controller.
- `build_model.py`: FreeCAD generator. The hip roof is a closed envelope rather
  than an assembly of rafters or measured roof layers. Regenerate it after
  changing roof parameters; it has no embedded Python callback dependency.
- `plan_structure.json`: proposed beams/posts extracted from SVG at 6 units/inch.
- `scene.json`: geometry used by the browser preview.
- `validation.json`: FreeCAD shape validity and volume checks.

On this Mac, regenerate CAD after editing parameters with:

```sh
cd /Volumes/Proj/proj/CAD/garage
PYTHONPATH=/Applications/FreeCAD.app/Contents/Resources/lib /Applications/FreeCAD.app/Contents/Resources/bin/python model/build_model.py
```

Alternatively run this in FreeCAD's Python console (View → Panels → Python console):

```python
path = '/Volumes/Proj/proj/CAD/garage/model/build_model.py'
exec(compile(open(path).read(), path, 'exec'), {'__file__': path})
```

The generator saves fresh CAD and scene files. To refresh the standalone and
inline browser files, run `python3 model/build_viewer.py` afterward.
Keep copies of manually edited CAD before regenerating because regeneration
replaces the generated outputs.

## Coordinate system

Top of the source plan is south; bottom is north; left is east; right is west.
CAD uses X east, Y north, Z up. Origin is the outside southwest corner at floor
level. Opening offsets in the input retain the drawing convention: horizontal
offsets measured from the east end, side-window offsets measured from the south.

## Confirmed and extracted dimensions

- East–west width: 20 ft 9½ in (249.5 in), retained from SVG.
- North–south wall length: 20 ft 9 in (249 in), user confirmed.
- All windows: sill 4 ft (48 in), height 2 ft (24 in), user confirmed.
- Walls: 8 ft 2½ in (98.5 in), user specified.
- Roof rise above walls: 5 ft (60 in), user specified.
- Total peak height: 13 ft 2½ in (158.5 in).
- Ridge: 18 in, centered, running north–south, user specified.
- South entry: 32 in wide, 106 in from the east outer edge.
- South window: 28 in wide, 179.5 in from east outer edge, from SVG position.
- West windows: 28.5 and 28.75 in wide, offsets 73 and 153.25 in from south.
- North garage door: 165 in wide, offset 28.25 in from east outer edge.
- Wall thicknesses from SVG: east/south 6 in, west 7.5 in, north 8 in.

## Unresolved dimensions and assumptions

1. **North–south wall length is 249 in (20 ft 9 in), confirmed by the user.**
   The 23 ft 10¼ in annotation belongs to different features and does not conflict
   with the wall dimension. This correction supersedes the earlier interpretation
   of the SVG drawing scale. The east–west width remains 249.5 in from the SVG;
   it has not been newly confirmed. Opening offsets and frame XY positions are
   preserved from the source plan.
2. The south wall segment labels do not exactly close: 106 + 32 + 40.75 + 28 + 42
   = 248.75 in, 0.75 in short of the overall width. The SVG's window position
   (179.5 in) was used; that leaves 41.5 in between openings and 42 in at the end.
3. Entry height 80 in and garage door height 84 in remain placeholders. Window
   sills are 48 in above floor datum and window heights are 24 in, both confirmed
   by the user; window heads are therefore 72 in above the floor.
4. Roof overhang is set to zero because it is unknown. Roof is an exterior
   massing envelope with a flat underside at wall height, not measured material
   thickness. No gutters, fascia, rafters, vents or ceiling assembly inferred.
5. Floor is a zero-thickness reference surface; slab thickness and condition
   are not represented.
6. Frame plan positions and plan widths match the SVG. Beams are provisionally
   8 in deep, with bottoms 170.5 in above the floor (12 in above the roof peak).
   Posts run from floor datum to that elevation. These values are illustrative.
   Apparent disconnected members and offsets are preserved, not designed away.
7. Roof Profile.svg/png describes the uncommitted proposed roof and was not used
   as the existing-roof geometry; the user's description controls that geometry.

This is a measured-plan reconstruction with explicit placeholders, suitable for
design discussion and further editing. No structural sizing, load capacity,
foundation design, or construction suitability has been established.

## Validation

The FCStd archive is also checked for saved GUI view providers, visible existing
geometry, a hidden proposal group, and a saved camera.

FreeCAD checks every exported object's geometry with `Shape.isValid()`. Existing
walls are real boolean openings; roof is a valid closed solid. STEP round-trip,
native reopen, units, roof bounds, and mesh indices are checked separately.
COLLADA has not been tested in SketchUp on this machine.

FreeCAD supports editable solids and STEP exchange:
https://www.freecad.org/features.php
SketchUp documents COLLADA import:
https://help.sketchup.com/en/sketchup/importing-and-exporting-collada-files
