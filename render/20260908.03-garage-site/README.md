# Garage Blender render

Source: `source/garage-model.json`, extracted from the supplied garage-render-package.zip. Coordinates and architectural geometry are preserved in metres. The supplied README describes the design basis and unresolved details.

`build_scene.py` builds a native Blender scene with named objects grouped into collections, procedural surface bump, bevel highlights, glass and panel materials, a soft daylight environment and warm sun, and southwest/northwest perspective cameras. Internal conceptual trusses are retained but hidden for exterior rendering, matching the source exterior-view visibility. The presentation ground is illustrative, not a surveyed site.

Generated with Blender 5.0.1 on ros@buzzkill in /home/ros/garage-render. Cycles detected only the Ryzen CPU; GPU rendering was not available in this installation. Renders use 128 samples, adaptive sampling and denoising at 1600 × 1200 pixels.

Rebuild on that host:

    cd /home/ros/garage-render
    blender -b -t 12 --python build_scene.py

The saved garage.blend contains both cameras and all procedural materials, with no external texture dependencies. Geometry and material choices remain editable. The original package is preserved separately.
