"""Print the base backyard's collections with object bounds (metres)."""
import bpy, sys
from mathutils import Vector
path = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.open_mainfile(filepath=path)
def walk(c, d=0):
    print('  ' * d + f'[{c.name}] {len(c.objects)} objects')
    for o in c.objects:
        if o.type != 'MESH':
            print('  ' * d + f'   - {o.name} ({o.type})'); continue
        bb = [o.matrix_world @ Vector(b) for b in o.bound_box]
        lo = [min(v[i] for v in bb) for i in range(3)]; hi = [max(v[i] for v in bb) for i in range(3)]
        print('  ' * d + f'   - {o.name}: x {lo[0]:.2f}..{hi[0]:.2f} y {lo[1]:.2f}..{hi[1]:.2f} z {lo[2]:.2f}..{hi[2]:.2f} faces {len(o.data.polygons)}')
    for ch in c.children:
        walk(ch, d + 1)
walk(bpy.context.scene.collection)
