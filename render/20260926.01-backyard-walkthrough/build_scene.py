"""Current building, outer-walls look, in the reviewed existing backyard.

blender -b -t 16 --python build_scene.py -- <backyard-existing.blend>

Inputs: ``building-mesh.json`` (written by
``src/structural-analysis-v6/lean_to_report.py``: the same meshes the HTML frame
viewer draws with its outer walls, roofs and inner walls on) and the reviewed
existing backyard. Both use the existing garage's outside south-west corner as
origin, x east, y north, z up; the building is converted from inches to metres
and nothing is moved.

Outputs, beside this script:
  backyard-walkthrough.blend  editable scene
  backyard-walkthrough.glb    browser copy (lighter foliage, 1024 px textures)
  walkmap.json                where a person can stand: 0.1 m cells, blocked where
                              anything between 18 in. and head height is in the way
  validation.json             what was removed, clipped and added
"""
import bpy, bmesh, json, sys, math, hashlib
from pathlib import Path
from mathutils import Vector

R = Path(__file__).resolve().parent
BASE = Path(sys.argv[sys.argv.index('--') + 1])
IN = 0.0254
STEP_LIMIT = 18 * IN          # anything taller than this is an obstacle
HEAD = 72 * IN                # the HTML walkthrough's 6 ft head point
CELL = 0.10

bpy.ops.wm.open_mainfile(filepath=str(BASE))
scene = bpy.context.scene
report = dict(removed=[], clipped=[], added=0)

# ---------------------------------------------------------------- the old garage
# The building mesh carries its own existing walls (drawn in the new-wall grey,
# openings cut) and its own roofs, so the photographic garage walls and the old
# hip roof go. The floor datum stays: it is the garage floor.
for name in ('garage', 'garage_roof'):
    col = bpy.data.collections.get(name)
    for o in list(col.objects) if col else []:
        if o.name.startswith('Floor datum'):
            continue
        report['removed'].append(o.name)
        bpy.data.objects.remove(o, do_unlink=True)

# Owner, 2026-09-27: the shelter's brown timber header and back screen go; the
# clip below bent them to wrong lines and angles. The green roof and the grey
# pillar that holds it up stay.
for name in ('Shelter timber front header', 'Shelter back screen'):
    o = bpy.data.objects.get(name)
    if o:
        report['removed'].append(o.name)
        bpy.data.objects.remove(o, do_unlink=True)

# ------------------------------------------------ what the new footprint displaces
mesh = json.loads((R / 'building-mesh.json').read_text())
xs = [v[0] * IN for o in mesh['objects'] if o['group'] in ('frame', 'outer')
      for v in o['vertices']]
ys = [v[1] * IN for o in mesh['objects'] if o['group'] in ('frame', 'outer')
      for v in o['vertices']]
FX0, FX1, FY0, FY1 = min(xs) - 0.03, max(xs) + 0.03, min(ys) - 0.03, max(ys) + 0.03
report['footprint_m'] = [FX0, FX1, FY0, FY1]
KEEP = {'ground', 'Context', 'context', 'paths', 'boundary', 'Lighting', 'Cameras',
        'Collection'}
KEEP_NAMES = ('East overhanging canopy', 'East mature tree trunk',
              'Surrounding ground', 'Floor datum')

def world_bounds(o):
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return ([min(v[i] for v in bb) for i in range(3)],
            [max(v[i] for v in bb) for i in range(3)])

for col in bpy.data.collections:
    if col.name in KEEP:
        continue
    for o in list(col.objects):
        if o.type != 'MESH' or o.name.startswith(KEEP_NAMES):
            continue
        lo, hi = world_bounds(o)
        ox = min(hi[0], FX1) - max(lo[0], FX0)
        oy = min(hi[1], FY1) - max(lo[1], FY0)
        if ox <= 0 or oy <= 0:
            continue
        cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
        if FX0 < cx < FX1 and FY0 < cy < FY1:
            report['removed'].append(o.name)
            bpy.data.objects.remove(o, do_unlink=True)
            continue
        # Straddles the footprint: push the vertices inside it back out across
        # the nearer side (the pergola beams stop short of the porch, the
        # shelter roof stops at the west addition).
        axis = 0 if ox < oy else 1
        lo_b, hi_b = (FX0, FX1) if axis == 0 else (FY0, FY1)
        side = lo_b if (cx if axis == 0 else cy) < lo_b else hi_b
        if o.data.users > 1:
            o.data = o.data.copy()
        mw, inv = o.matrix_world, o.matrix_world.inverted()
        for v in o.data.vertices:
            w = mw @ v.co
            if FX0 < w.x < FX1 and FY0 < w.y < FY1:
                w[axis] = side
                v.co = inv @ w
        report['clipped'].append(o.name)

# ----------------------------------------------------------------- the building
def linear(c):
    return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4

def rgb(hexcolor):
    h = hexcolor.lstrip('#')
    return tuple(linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))

ROLE = {  # (metallic, roughness) by what the colour is for
    '#f4f4f1': (0.25, 0.45), '#141618': (0.4, 0.18), '#4a4f55': (0.5, 0.42),
    '#fbfbf9': (0.0, 0.5), '#8fa9c2': (0.3, 0.4),
}
mats = {}

def material(color, opacity, vertex=False):
    key = (color, round(opacity, 3), vertex)
    if key in mats:
        return mats[key]
    m = bpy.data.materials.new(f'BUILDING / {"mural" if vertex else color} {opacity:g}')
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes.get('Principled BSDF')
    metal, rough = ROLE.get(color, (0.0, 0.6))
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    if vertex:
        ca = nt.nodes.new('ShaderNodeVertexColor')
        ca.layer_name = 'Col'
        nt.links.new(ca.outputs['Color'], p.inputs['Base Color'])
        p.inputs['Roughness'].default_value = 0.85
    else:
        p.inputs['Base Color'].default_value = rgb(color or '#9aa3ab') + (1,)
    if opacity < 0.999:
        p.inputs['Alpha'].default_value = opacity
        p.inputs['Roughness'].default_value = 0.05
        p.inputs['IOR'].default_value = 1.0          # no refraction: near-clear sheet
        m.surface_render_method = 'BLENDED'
    mats[key] = m
    return m

# The building's grey wall panels (and the existing walls drawn in that grey)
# take the house's own stucco material, so they are the same grey as the house.
# The texture is mapped at the house's texel density: UVs are world metres
# projected on each face's dominant axis, scaled to match.
WALL_GREY = '#d3d6d9'
stucco = bpy.data.materials['PHOTO / house_stucco']
uv_area = world_area = 0.0
for o in bpy.data.collections['house'].objects:
    if o.type != 'MESH' or stucco.name not in [m.name for m in o.data.materials if m]:
        continue
    uvl = o.data.uv_layers.active
    sc = o.matrix_world.to_scale()
    for p in o.data.polygons:
        if o.data.materials[p.material_index] != stucco or uvl is None:
            continue
        uv = [uvl.data[k].uv for k in p.loop_indices]
        a2 = 0.0
        for k in range(1, len(uv) - 1):
            a2 += abs((uv[k].x - uv[0].x) * (uv[k + 1].y - uv[0].y)
                      - (uv[k + 1].x - uv[0].x) * (uv[k].y - uv[0].y)) / 2
        uv_area += a2
        world_area += p.area * abs(sc.x * sc.y * sc.z) ** (2 / 3)
UV_PER_M = math.sqrt(uv_area / world_area) if world_area else 1.0
report['stucco_uv_per_m'] = UV_PER_M

def planar_uvs(me):
    uvl = me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        n = p.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        for k in p.loop_indices:
            co = me.vertices[me.loops[k].vertex_index].co
            uvl.data[k].uv = (co[a] * UV_PER_M, co[b] * UV_PER_M)

cols = {}
for e in mesh['objects']:
    g = 'BUILDING / ' + e['group']
    if g not in cols:
        cols[g] = bpy.data.collections.new(g)
        scene.collection.children.link(cols[g])
    me = bpy.data.meshes.new(e['name'])
    me.from_pydata([[c * IN for c in v] for v in e['vertices']], [], e['triangles'])
    me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me); bm.free()
    vertex = bool(e.get('vertexcolor'))
    if vertex:
        attr = me.color_attributes.new('Col', 'BYTE_COLOR', 'POINT')
        for k, c in enumerate(e['vertexcolor']):
            attr.data[k].color = rgb(c) + (1,)
    if e['group'] == 'outer' and e['color'] == WALL_GREY:
        planar_uvs(me)
        me.materials.append(stucco)
    else:
        me.materials.append(material(e['color'], e['opacity'], vertex))
    ob = bpy.data.objects.new('BUILDING / ' + e['name'], me)
    cols[g].objects.link(ob)
    report['added'] += 1

scene['basis'] = ('Outer-walls look of viz/latest/lean-to-frame-3d.html in the '
                  'reviewed existing backyard; shared origin, no transform.')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(R / 'backyard-walkthrough.blend'))
print('BLEND_READY', flush=True)

# ---------------------------------------------------------------- the walk map
# Rays go straight down from head height on a 3 x 3 pattern in every cell. A
# cell is blocked if any ray meets something higher than 18 in.; otherwise the
# highest hit is the floor there. Shrubs are sparse leaf cards that rays slip
# between, so any ground-rooted plant also blocks its (slightly shrunk) outline.
# One BVH over every mesh in world coordinates; scene.ray_cast is far slower.
from mathutils.bvhtree import BVHTree
dg = bpy.context.evaluated_depsgraph_get()
def tree(objects):
    verts, polys = [], []
    for o in objects:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = o.matrix_world
        base = len(verts)
        verts.extend(mw @ v.co for v in me.vertices)
        polys.extend([base + k for k in p.vertices] for p in me.polygons)
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys, all_triangles=False), len(polys)
meshes = [o for o in scene.objects if o.type == 'MESH' and not o.hide_render
          and o.name != 'Surrounding ground']
bvh, polys = tree(meshes)
# The building's meshes are all closed solids, so a downward ray whose first
# hit faces down started inside one. (Leaf cards are open; they stay out.)
solid, _ = tree([o for o in meshes if o.name.startswith('BUILDING /')])
print('BVH_READY', polys, flush=True)
ground = [o for o in scene.objects if o.name == 'Approximate backyard extent'][0]
GX0, GY0, _ = world_bounds(ground)[0]
GX1, GY1, _ = world_bounds(ground)[1]
nx, ny = int((GX1 - GX0) / CELL), int((GY1 - GY0) / CELL)
blocked = [[False] * nx for _ in range(ny)]
floor = [[0.0] * nx for _ in range(ny)]
subs = [(-1 / 3, -1 / 3), (0, -1 / 3), (1 / 3, -1 / 3), (-1 / 3, 0), (0, 0),
        (1 / 3, 0), (-1 / 3, 1 / 3), (0, 1 / 3), (1 / 3, 1 / 3)]
down = Vector((0, 0, -1))
up = Vector((0, 0, 1))
for j in range(ny):
    for i in range(nx):
        cx, cy = GX0 + (i + .5) * CELL, GY0 + (j + .5) * CELL
        top, inside = -1.0, False
        for sx, sy in subs:
            px, py = cx + sx * CELL, cy + sy * CELL
            # Down from head height. A hit on a face that points away from the
            # ray's start means the start is inside a solid (a wall, a post).
            loc, nrm, *_ = bvh.ray_cast(Vector((px, py, HEAD)), down)
            if loc is not None:
                top = max(top, loc.z)
                inside |= nrm.z < 0
            # Up from just over the step limit: anything below head height is
            # in the way, even if the down ray started inside it.
            loc, nrm, *_ = bvh.ray_cast(Vector((px, py, STEP_LIMIT + .01)), up)
            if loc is not None and loc.z < HEAD:
                inside = True
            # Inside a building solid? Tested on the building alone: in the full
            # tree a wall's bottom face ties with the slab it stands on.
            loc, nrm, *_ = solid.ray_cast(Vector((px, py, HEAD)), down)
            if loc is not None and nrm.z < 0 and loc.z <= STEP_LIMIT:
                inside = True
        if top > STEP_LIMIT or inside:
            blocked[j][i] = True
        else:
            floor[j][i] = round(max(top, 0.0), 3)
for o in scene.objects:
    if o.type != 'MESH' or 'detailed leaves' not in o.name:
        continue
    lo, hi = world_bounds(o)
    if lo[2] > STEP_LIMIT or hi[2] < STEP_LIMIT:
        continue                                  # canopies overhead, ground covers
    sx, sy = (hi[0] - lo[0]) * .15, (hi[1] - lo[1]) * .15
    for j in range(max(0, int((lo[1] + sy - GY0) / CELL)), min(ny, int((hi[1] - sy - GY0) / CELL) + 1)):
        for i in range(max(0, int((lo[0] + sx - GX0) / CELL)), min(nx, int((hi[0] - sx - GX0) / CELL) + 1)):
            blocked[j][i] = True
# The yard's edge is a wall.
for j in range(ny):
    blocked[j][0] = blocked[j][nx - 1] = True
for i in range(nx):
    blocked[0][i] = blocked[ny - 1][i] = True
walkmap = dict(cell=CELL, x0=GX0, y0=GY0, nx=nx, ny=ny, head=HEAD, step=STEP_LIMIT,
               footprint=[FX0, FX1, FY0, FY1],
               rows=[''.join('#' if b else '.' for b in row) for row in blocked],
               floor=[[round(v, 2) for v in row] for row in floor])
(R / 'walkmap.json').write_text(json.dumps(walkmap))
report['walkmap'] = dict(nx=nx, ny=ny, walkable=sum(r.count('.') for r in walkmap['rows']))
print('WALKMAP_READY', flush=True)

# ------------------------------------------------------------- the browser copy
for ob in list(bpy.data.objects):
    if ob.type != 'MESH':
        continue
    if len(ob.data.polygons) > 1000 and any(m and m.name.startswith('Leaf ') for m in ob.data.materials):
        old = ob.data
        faces = [p for p in old.polygons if (p.index // 4) % 4 == 0]
        used = sorted({v for p in faces for v in p.vertices})
        mapping = {v: i for i, v in enumerate(used)}
        me = bpy.data.meshes.new(old.name + ' web')
        me.from_pydata([old.vertices[i].co for i in used], [], [[mapping[i] for i in p.vertices] for p in faces])
        me.update()
        for m in old.materials:
            me.materials.append(m)
        for p, q in zip(me.polygons, faces):
            p.material_index = q.material_index
        ob.data = me
for im in bpy.data.images:
    if im.type == 'IMAGE' and max(im.size) > 1024:
        r = 1024 / max(im.size)
        im.scale(max(1, int(im.size[0] * r)), max(1, int(im.size[1] * r)))
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
    if ob.type == 'MESH' and not ob.hide_render and ob.name != 'Surrounding ground':
        ob.hide_set(False); ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R / 'backyard-walkthrough.glb'), export_format='GLB',
                          use_selection=True, export_apply=True, export_cameras=False,
                          export_lights=False, export_yup=True)
report['building_mesh_sha256'] = hashlib.sha256((R / 'building-mesh.json').read_bytes()).hexdigest()
report['baseline_sha256'] = hashlib.sha256(BASE.read_bytes()).hexdigest()
(R / 'validation.json').write_text(json.dumps(report, indent=2))
print('GLB_READY', flush=True)
