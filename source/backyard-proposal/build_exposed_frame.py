"""Backyard scene with exposed-frame garage (dark steel outside, metal panels inside).
Opens backyard-existing.blend, removes garage_roof, inserts exposed-frame geometry,
and renders from the same three cameras as the hip-cap proposal."""
import bpy, bmesh, json, hashlib
from pathlib import Path
from mathutils import Vector

R = Path(__file__).resolve().parent
# cad-mesh.json lives on Buzzkill share
CAD_MESH = Path('/proj/garage/optimization/exposed-frame/cad-mesh.json')

bpy.ops.wm.open_mainfile(filepath=str(R / 'backyard-existing.blend'))
s = bpy.context.scene

# Remove existing garage roof (keep lower walls, shelter, whole backyard)
removed = []
for c in list(bpy.data.collections):
    if c.name == 'garage_roof':
        for o in list(c.objects):
            removed.append(o.name)
            bpy.data.objects.remove(o, do_unlink=True)

# ── Materials (same as exposed-frame render_blender.py) ──────────────────

def linear(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

def hex_to_rgb(hx):
    return tuple(linear(int(hx[i:i+2], 16) / 255) for i in [0, 2, 4]) + (1,)

colors = {
    'steel':  ('354247', 0.48, 0.34),
    'panel':  ('b6c0c2', 0.30, 0.42),
    'trim':   ('ecebe4', 0.08, 0.38),
    'roof':   ('606d70', 0.52, 0.40),
    'pv':     ('243d50', 0.62, 0.18),
    'glass':  ('526f78', 0.35, 0.16),
    'wood':   ('aa865c', 0.00, 0.62),
    'stucco': ('b7b9b3', 0.00, 0.83),
    'slab':   ('a6a7a2', 0.00, 0.84),
}

mats = {}
for key, (hx, metal, rough) in colors.items():
    m = bpy.data.materials.new('EXPOSED / ' + key)
    m.use_nodes = True
    n = m.node_tree.nodes
    p = n.get('Principled BSDF')
    p.inputs['Base Color'].default_value = hex_to_rgb(hx)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    if key in ['pv', 'glass']:
        p.inputs['Coat Weight'].default_value = 0.5
    if key in ['stucco', 'panel', 'steel']:
        tex = n.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 180 if key != 'stucco' else 80
        b = n.new('ShaderNodeBump')
        b.inputs['Distance'].default_value = 0.00035 if key != 'stucco' else 0.003
        b.inputs['Strength'].default_value = 0.2
        m.node_tree.links.new(tex.outputs['Fac'], b.inputs['Height'])
        m.node_tree.links.new(b.outputs['Normal'], p.inputs['Normal'])
    mats[key] = m

# ── Load & convert exposed-frame mesh (inches → metres) ──────────────────

j = json.loads(CAD_MESH.read_text())
INCHES_TO_METRES = 0.0254

cols = {}
added = 0
for o in j['objects']:
    # Skip existing garage — backyard scene already has it with photo textures
    if o['group'] == 'ExistingGarage':
        continue
    g = 'EXPOSED / ' + o['group']
    if g not in cols:
        cols[g] = bpy.data.collections.new(g)
        s.collection.children.link(cols[g])

    verts = [[v * INCHES_TO_METRES for v in p] for p in o['vertices']]
    m = bpy.data.meshes.new(o['name'])
    m.from_pydata(verts, [], o['triangles'])
    m.update()

    bm = bmesh.new()
    bm.from_mesh(m)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(m)
    bm.free()

    ob = bpy.data.objects.new('EXPOSED / ' + o['name'], m)
    cols[g].objects.link(ob)
    mat = mats.get(o['material'])
    if mat:
        ob.data.materials.append(mat)
    added += 1

    # Bevel for edge highlights on steel, trim, panel, wood
    if o['material'] in ['steel', 'trim', 'panel', 'wood']:
        mod = ob.modifiers.new('Small edge highlight', 'BEVEL')
        mod.width = 0.00065
        mod.segments = 2
        mod.affect = 'EDGES'

# ── Cameras (reuse existing backyard cameras, add proposal-specific) ─────

def cam(name, pos, target, lens=35, ortho=None):
    bpy.ops.object.camera_add(location=pos)
    c = bpy.context.object
    c.name = name
    c.rotation_euler = (Vector(target) - c.location).to_track_quat('-Z', 'Y').to_euler()
    c.data.lens = lens
    if ortho:
        c.data.type = 'ORTHO'
        c.data.ortho_scale = ortho
    return c

cameras = [
    (bpy.data.objects['01 / Whole backyard'], '01-proposed-backyard-overview'),
    (cam('PROPOSED / Patio to garage', (-6.3, -12, 3.8), (0.7, 1.6, 3.1), 26), '02-proposed-patio-to-garage'),
    (cam('PROPOSED / Elevated southwest', (-10, 0, 12), (1, 2, 2.5), 26), '03-proposed-garage-context'),
]

# Also add the two close-up cameras from the original exposed-frame renders
cam('EXPOSED / Southwest exterior', (-11 * 0.3048, -13 * 0.3048, 9 * 0.3048),
    (2 * 0.3048, 1.8 * 0.3048, 3 * 0.3048), 48)
cam('EXPOSED / Northwest exterior', (-10.5 * 0.3048, 17 * 0.3048, 8.5 * 0.3048),
    (2.1 * 0.3048, 3.6 * 0.3048, 3.2 * 0.3048), 48)

# ── Render settings ──────────────────────────────────────────────────────

s.render.engine = 'CYCLES'
s.cycles.device = 'CPU'
s.cycles.samples = 80
s.cycles.use_denoising = True
s.cycles.adaptive_threshold = 0.035
s.render.resolution_x = 1800
s.render.resolution_y = 1350
s.render.resolution_percentage = 100

s['proposal_basis'] = (
    'Exposed-frame garage (dark steel outside, light gray metal panels inside) '
    'inserted into Backyard-Blender-Package.zip baseline. '
    'Shared metre coordinates; original garage roof removed; '
    'lower walls and all site context retained.'
)
s['steel_weight_lb'] = 5289.8
s['member_count'] = 88

bpy.ops.file.pack_all()
s.camera = cameras[0][0]
bpy.ops.wm.save_as_mainfile(filepath=str(R / 'backyard-proposed-exposed-frame.blend'))

report = {
    'source': 'Backyard-Blender-Package.zip',
    'garage_source': str(CAD_MESH),
    'source_blend_sha256': hashlib.sha256((R / 'backyard-existing.blend').read_bytes()).hexdigest(),
    'removed': removed,
    'added_objects': added,
    'transform': 'inches → metres (×0.0254); X east / Y north / Z up',
    'retained': 'all baseline objects except garage_roof',
    'cameras': [c.name for c, _ in cameras],
}
(R / 'exposed-frame-validation.json').write_text(json.dumps(report, indent=2))

for c, n in cameras:
    s.camera = c
    s.render.filepath = str(R / (n + '.png'))
    bpy.ops.render.render(write_still=True)
    print('DONE ' + n, flush=True)

# Also render close-ups
for cn, fn in [('EXPOSED / Southwest exterior', '04-exposed-southwest.png'),
               ('EXPOSED / Northwest exterior', '05-exposed-northwest.png')]:
    c = bpy.data.objects.get(cn)
    if c:
        s.camera = c
        s.render.filepath = str(R / fn)
        bpy.ops.render.render(write_still=True)
        print('DONE ' + fn, flush=True)