# Backyard — Blender rendering package

This package builds the **existing** backyard from corrected site revision 8, using six materials extracted from the owner's photographs. It is separate from `blender-render/garage-site.blend`, which used the proposed garage.

## Main outputs

- `backyard-existing.blend` — native Blender scene with packed textures, named collections and four cameras.
- `01-backyard-overview.png` — whole-yard view.
- `02-patio-toward-garage.png` — view toward the garage from the patio.
- `03-conversation-area.png` — fire pit and seating.
- `04-house-and-gardens.png` — house-facing context.
- `Backyard-Existing-Conditions.pdf` — formal illustrated record of the model basis and limitations.
- `BACKYARD-EXISTING-CONDITIONS.md` — editable written record.
- `textures/` — original surface crops, repeating color atlases, approximate bump/roughness maps, and crop manifest.
- `site-scene.json` — frozen geometry input from site revision 8.

## Regeneration

On Blender 5.0.1:

```sh
blender -b -t 12 --python build_backyard.py
blender -b -t 12 --python render_final.py
```

The first command builds the scene and renders two smaller previews. The final-render script applies the reviewed exposure and soft conversation-area fill. The second opens the saved scene and renders the four final views at 1800 × 1350, 80 Cycles samples with denoising. The image textures are packed into the blend file. Separate texture files are retained to make material edits straightforward.

To re-extract maps on the original Mac, run `extract_textures.py` with Python, Pillow and NumPy. The script resolves source photographs from the existing project. Source photographs are not embedded wholesale in this package; the selected surface crops are included. `textures/manifest.json` records original source paths and pixel coordinates.

`build_report.py` requires ReportLab. It creates the illustrated PDF from the Markdown record and final images.

## Scope

The owner-confirmed layout corrections take precedence over the older aerial: north-aligned work shelter with planters south; four rooms separated by a planted fence with a gap; open jungle center; no path within the low south garden; pergola ends 8 ft north of the fence while its path continues to the patio; no above-ground pool. Garage geometry is inherited from the existing measured model. All other dimensions and most vertical detail remain estimates.

Vegetation detail is procedural geometry within the approximate plant envelopes, not reconstructed individual leaves. Surface color is cropped from actual photos; bump and roughness are estimates, not scanned PBR. Some photographic lighting and repetition remain visible. This is a visualization baseline, not a survey or construction model.

Remote build directory: `/home/ros/garage-render/existing-backyard-20260908` on `ros@buzzkill`.
