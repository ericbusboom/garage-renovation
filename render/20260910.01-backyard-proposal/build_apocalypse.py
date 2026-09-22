"""Hellscape variant: exposed-frame garage in the apocalypse.
Opens the exposed-frame backyard scene, replaces sky/lighting with
volcanic-nuclear hellscape: lava, mushroom clouds, embers, fire sky."""
import bpy, bmesh, json, math, random
from pathlib import Path
from mathutils import Vector, Euler, Color

R = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R / 'backyard-proposed-exposed-frame.blend'))
s = bpy.context.scene
random.seed(666)

# ═══════════════════════════════════════════════════════════════════════
# 1. NUKE THE LIGHTING — replace daylight with fire/volcanic
# ═══════════════════════════════════════════════════════════════════════

# Remove existing lights
for o in list(bpy.data.objects):
    if o.type == 'LIGHT':
        bpy.data.objects.remove(o, do_unlink=True)

# Delete old lighting collection
for c in list(bpy.data.collections):
    if c.name == 'Lighting':
        bpy.data.collections.remove(c)

col_light = bpy.data.collections.new('Hellscape Lighting')
s.collection.children.link(col_light)

def light(name, ptype, pos, color, energy, size=0, angle=0):
    bpy.ops.object.light_add(type=ptype, location=pos)
    o = bpy.context.object
    o.name = 'HELL / ' + name
    o.data.color = color
    o.data.energy = energy
    if size:
        if ptype == 'AREA':
            o.data.size = size
        else:
            o.data.shadow_soft_size = size
    if angle:
        o.data.angle = angle
    for c in list(o.users_collection):
        c.objects.unlink(o)
    col_light.objects.link(o)
    return o

# Main apocalyptic sun — low, blood-red, harsh shadows
light('Dying Sun', 'SUN', (-30, -40, 4), (1.0, 0.25, 0.08), 12.0, angle=0.3)

# Lava glow from below — large warm area lights pointing up
light('Lava Glow East', 'AREA', (5, -3, -0.3), (1.0, 0.35, 0.05), 400, size=10)
light('Lava Glow West', 'AREA', (-6, -3, -0.3), (1.0, 0.3, 0.04), 350, size=10)
light('Lava Glow North', 'AREA', (0, 18, -0.3), (0.9, 0.25, 0.03), 300, size=12)

# Nuclear flash from the distance — extremely bright, blue-white
light('Nuclear Flash SE', 'POINT', (40, -60, 8), (0.8, 0.85, 1.0), 80000, size=5)
light('Nuclear Flash NW', 'POINT', (-30, 50, 6), (0.75, 0.8, 1.0), 60000, size=4)

# Area fire lights for atmosphere
for i, ((x, y, z), (r, g, b), e) in enumerate([
    ((-3, 8, 1.2), (1.0, 0.2, 0.02), 120),
    ((5, 5, 0.8), (1.0, 0.3, 0.04), 100),
    ((-4, -8, 1.0), (0.95, 0.25, 0.03), 140),
    ((2, -6, 0.6), (1.0, 0.35, 0.05), 110),
]):
    light(f'Fire glow {i}', 'POINT', (x, y, z), (r, g, b), e, size=3)

# ═══════════════════════════════════════════════════════════════════════
# 2. VOLUMETRIC HELLSCAPE SKY
# ═══════════════════════════════════════════════════════════════════════

world = s.world
world.use_nodes = True
ns = world.node_tree.nodes
ls = world.node_tree.links
ns.clear()

# Sky gradient: deep red horizon → dark smoky orange → black
sky_grad = ns.new('ShaderNodeTexGradient')
sky_grad.gradient_type = 'SPHERICAL'
map_range = ns.new('ShaderNodeMapRange')
map_range.inputs['From Min'].default_value = 0.0
map_range.inputs['From Max'].default_value = 1.0
map_range.inputs['To Min'].default_value = -0.3
map_range.inputs['To Max'].default_value = 1.0
ls.new(sky_grad.outputs['Color'], map_range.inputs['Value'])

color_ramp = ns.new('ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].color = (0.02, 0.0, 0.0, 1)    # black zenith
el = color_ramp.color_ramp.elements.new(0.25)
el.color = (0.15, 0.02, 0.0, 1)    # dark red
el = color_ramp.color_ramp.elements.new(0.55)
el.color = (0.45, 0.08, 0.0, 1)    # fire orange mid-sky
el = color_ramp.color_ramp.elements.new(0.8)
el.color = (0.7, 0.2, 0.02, 1)     # bright fire horizon
color_ramp.color_ramp.elements[1].color = (0.85, 0.35, 0.05, 1)  # intense horizon
ls.new(map_range.outputs['Result'], color_ramp.inputs['Fac'])

# Add turbulent smoke/noise to the sky
sky_noise = ns.new('ShaderNodeTexNoise')
sky_noise.inputs['Scale'].default_value = 3.0
sky_noise.inputs['Detail'].default_value = 6.0
sky_noise.inputs['Roughness'].default_value = 0.7
sky_noise.inputs['Distortion'].default_value = 0.3

noise_mix = ns.new('ShaderNodeMix')
noise_mix.data_type = 'RGBA'
noise_mix.inputs[0].default_value = 0.65
ls.new(color_ramp.outputs['Color'], noise_mix.inputs[6])  # A
ls.new(sky_noise.outputs['Color'], noise_mix.inputs[7])   # B

# Darker noise for cloud silhouettes
noise_dark = ns.new('ShaderNodeValToRGB')
noise_dark.color_ramp.elements[0].color = (0.01, 0.0, 0.0, 1)
noise_dark.color_ramp.elements[1].color = (0.08, 0.01, 0.0, 1)
ls.new(sky_noise.outputs['Fac'], noise_dark.inputs['Fac'])

sky_final = ns.new('ShaderNodeMix')
sky_final.data_type = 'RGBA'
sky_final.inputs[0].default_value = 0.4
ls.new(noise_mix.outputs[2], sky_final.inputs[6])   # Result
ls.new(noise_dark.outputs['Color'], sky_final.inputs[7])

bg = ns.new('ShaderNodeBackground')
bg.inputs['Strength'].default_value = 0.8
ls.new(sky_final.outputs[2], bg.inputs['Color'])

out = ns.new('ShaderNodeOutputWorld')
ls.new(bg.outputs[0], out.inputs[0])

# ═══════════════════════════════════════════════════════════════════════
# 3. MUSHROOM CLOUDS — volumetric spheres
# ═══════════════════════════════════════════════════════════════════════

def mushroom_cloud(name, location, scale=1.0, brightness=1.0):
    """Create a volumetric mushroom cloud using stacked spheres."""
    x, y, z = location
    col = bpy.data.collections.new('HELL / ' + name)
    s.collection.children.link(col)
    
    # Stem — tall cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.8*scale, depth=6*scale,
        location=(x, y, z + 3*scale))
    stem = bpy.context.object
    stem.name = name + ' stem'
    for c in list(stem.users_collection):
        c.objects.unlink(stem)
    col.objects.link(stem)
    
    # Cap — large sphere squashed
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32, ring_count=16, radius=4*scale,
        location=(x, y, z + 6*scale))
    cap = bpy.context.object
    cap.name = name + ' cap'
    cap.scale = (1, 1, 0.5)
    for c in list(cap.users_collection):
        c.objects.unlink(cap)
    col.objects.link(cap)
    
    # Inner core — brighter
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=8, radius=1.8*scale,
        location=(x, y, z + 5.5*scale))
    core = bpy.context.object
    core.name = name + ' core'
    core.scale = (1, 1, 0.45)
    for c in list(core.users_collection):
        c.objects.unlink(core)
    col.objects.link(core)
    
    # Ring at base of cap
    bpy.ops.mesh.primitive_torus_add(
        major_radius=3.5*scale, minor_radius=0.6*scale,
        location=(x, y, z + 4.5*scale))
    ring = bpy.context.object
    ring.name = name + ' ring'
    for c in list(ring.users_collection):
        c.objects.unlink(ring)
    col.objects.link(ring)
    
    # Materials
    mat_stem = bpy.data.materials.new('MUSHROOM stem ' + name)
    mat_stem.use_nodes = True
    ns = mat_stem.node_tree.nodes
    ls = mat_stem.node_tree.links
    ns.clear()
    emit_stem = ns.new('ShaderNodeEmission')
    emit_stem.inputs['Color'].default_value = (0.25*brightness, 0.15*brightness, 0.08*brightness, 1)
    emit_stem.inputs['Strength'].default_value = 1.5*brightness
    vol_stem = ns.new('ShaderNodeVolumePrincipled')
    vol_stem.inputs['Color'].default_value = (0.6*brightness, 0.35*brightness, 0.15*brightness, 1)
    vol_stem.inputs['Density'].default_value = 0.08
    vol_stem.inputs['Anisotropy'].default_value = 0.5
    out_stem = ns.new('ShaderNodeOutputMaterial')
    ls.new(emit_stem.outputs[0], out_stem.inputs[0])
    # Volume output
    ls.new(vol_stem.outputs[0], out_stem.inputs[1])
    
    mat_cap = bpy.data.materials.new('MUSHROOM cap ' + name)
    mat_cap.use_nodes = True
    ns = mat_cap.node_tree.nodes
    ls = mat_cap.node_tree.links
    ns.clear()
    emit_cap = ns.new('ShaderNodeEmission')
    emit_cap.inputs['Color'].default_value = (0.5*brightness, 0.3*brightness, 0.12*brightness, 1)
    emit_cap.inputs['Strength'].default_value = 2.0*brightness
    vol_cap = ns.new('ShaderNodeVolumePrincipled')
    vol_cap.inputs['Color'].default_value = (0.8*brightness, 0.5*brightness, 0.2*brightness, 1)
    vol_cap.inputs['Density'].default_value = 0.04
    vol_cap.inputs['Anisotropy'].default_value = 0.7
    out_cap = ns.new('ShaderNodeOutputMaterial')
    ls.new(emit_cap.outputs[0], out_cap.inputs[0])
    ls.new(vol_cap.outputs[0], out_cap.inputs[1])
    
    mat_core = bpy.data.materials.new('MUSHROOM core ' + name)
    mat_core.use_nodes = True
    ns = mat_core.node_tree.nodes
    ls = mat_core.node_tree.links
    ns.clear()
    emit_core = ns.new('ShaderNodeEmission')
    emit_core.inputs['Color'].default_value = (0.9*brightness, 0.7*brightness, 0.4*brightness, 1)
    emit_core.inputs['Strength'].default_value = 5.0*brightness
    vol_core = ns.new('ShaderNodeVolumePrincipled')
    vol_core.inputs['Color'].default_value = (1.0*brightness, 0.8*brightness, 0.5*brightness, 1)
    vol_core.inputs['Density'].default_value = 0.12
    vol_core.inputs['Anisotropy'].default_value = 0.8
    out_core = ns.new('ShaderNodeOutputMaterial')
    ls.new(emit_core.outputs[0], out_core.inputs[0])
    ls.new(vol_core.outputs[0], out_core.inputs[1])
    
    mat_ring = bpy.data.materials.new('MUSHROOM ring ' + name)
    mat_ring.use_nodes = True
    ns = mat_ring.node_tree.nodes
    ls = mat_ring.node_tree.links
    ns.clear()
    emit_ring = ns.new('ShaderNodeEmission')
    emit_ring.inputs['Color'].default_value = (0.6*brightness, 0.4*brightness, 0.2*brightness, 1)
    emit_ring.inputs['Strength'].default_value = 3.0*brightness
    vol_ring = ns.new('ShaderNodeVolumePrincipled')
    vol_ring.inputs['Color'].default_value = (0.7*brightness, 0.45*brightness, 0.25*brightness, 1)
    vol_ring.inputs['Density'].default_value = 0.06
    vol_ring.inputs['Anisotropy'].default_value = 0.6
    out_ring = ns.new('ShaderNodeOutputMaterial')
    ls.new(emit_ring.outputs[0], out_ring.inputs[0])
    ls.new(vol_ring.outputs[0], out_ring.inputs[1])
    
    stem.data.materials.append(mat_stem)
    cap.data.materials.append(mat_cap)
    core.data.materials.append(mat_core)
    ring.data.materials.append(mat_ring)
    
    return col

# Three mushroom clouds, placed to read in both ortho and perspective views
mushroom_cloud('SE blast', (16, -11, 1.0), scale=1.3, brightness=0.85)
mushroom_cloud('NW blast', (-15, 9, 0.8), scale=1.5, brightness=0.75)
mushroom_cloud('Far north blast', (4, 17, 0.5), scale=1.1, brightness=0.6)

# Two more distant ones for depth
mushroom_cloud('Far SE blast', (26, -20, 2.0), scale=2.2, brightness=0.5)
mushroom_cloud('Far W blast', (-24, -14, 1.5), scale=1.8, brightness=0.55)

# ═══════════════════════════════════════════════════════════════════════
# 4. LAVA FLOWS — emissive cracked planes
# ═══════════════════════════════════════════════════════════════════════

lavas = bpy.data.collections.new('HELL / Lava Flows')
s.collection.children.link(lavas)

def lava_flow(name, location, size_x, size_y, energy=1.0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=location)
    o = bpy.context.object
    o.name = 'LAVA / ' + name
    o.scale = (size_x, size_y, 1)
    for c in list(o.users_collection):
        c.objects.unlink(o)
    lavas.objects.link(o)
    
    # Lava material with cracks and glow
    mat = bpy.data.materials.new('LAVA / ' + name)
    mat.use_nodes = True
    ns = mat.node_tree.nodes
    ls = mat.node_tree.links
    ns.clear()
    
    # Voronoi for cracked crust effect
    voronoi = ns.new('ShaderNodeTexVoronoi')
    voronoi.inputs['Scale'].default_value = 2.5
    voronoi.inputs['Detail'].default_value = 4.0
    voronoi.inputs['Roughness'].default_value = 0.4
    voronoi.feature = 'DISTANCE_TO_EDGE'
    
    # Noise for surface variation
    noise = ns.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 8.0
    noise.inputs['Detail'].default_value = 5.0
    noise.inputs['Roughness'].default_value = 0.6
    
    # Mix noise into voronoi cracks (both float outputs)
    mix_vn = ns.new('ShaderNodeMix')
    mix_vn.data_type = 'FLOAT'
    mix_vn.inputs[0].default_value = 0.3
    ls.new(voronoi.outputs['Distance'], mix_vn.inputs[1])  # A
    ls.new(noise.outputs['Fac'], mix_vn.inputs[2])          # B
    
    # Crack threshold: narrow cracks = bright lava, wide areas = dark crust
    crack_ramp = ns.new('ShaderNodeValToRGB')
    crack_ramp.color_ramp.elements[0].color = (1.0, 0.6, 0.08, 1)  # bright lava in cracks
    el = crack_ramp.color_ramp.elements.new(0.08)
    el.color = (0.95, 0.4, 0.05, 1)
    el = crack_ramp.color_ramp.elements.new(0.2)
    el.color = (0.5, 0.15, 0.0, 1)    # cooling edge
    el = crack_ramp.color_ramp.elements.new(0.5)
    el.color = (0.08, 0.03, 0.01, 1)  # dark crust
    crack_ramp.color_ramp.elements[1].color = (0.02, 0.01, 0.0, 1)  # coldest crust
    ls.new(mix_vn.outputs[0], crack_ramp.inputs['Fac'])
    
    # Emission from the hot cracks
    emit = ns.new('ShaderNodeEmission')
    emit.inputs['Strength'].default_value = 8.0 * energy
    ls.new(crack_ramp.outputs['Color'], emit.inputs['Color'])
    
    # PBR for the crust
    pbr = ns.new('ShaderNodeBsdfPrincipled')
    pbr.inputs['Base Color'].default_value = (0.03, 0.01, 0.0, 1)
    pbr.inputs['Roughness'].default_value = 0.85
    pbr.inputs['Emission Color'].default_value = (0.0, 0.0, 0.0, 1)
    pbr.inputs['Emission Strength'].default_value = 0.0
    
    # Shader mix: emission for cracks, PBR for crust
    shader_mix = ns.new('ShaderNodeMixShader')
    ls.new(pbr.outputs[0], shader_mix.inputs[1])
    ls.new(emit.outputs[0], shader_mix.inputs[2])
    ls.new(crack_ramp.outputs['Alpha'], shader_mix.inputs[0])
    
    out = ns.new('ShaderNodeOutputMaterial')
    ls.new(shader_mix.outputs[0], out.inputs[0])
    
    o.data.materials.append(mat)
    return o

# Lava flows around the scene
lava_flow('South field', (-2, -10, -0.05), 20, 12, 1.2)
lava_flow('East approach', (10, 2, -0.05), 8, 18, 1.0)
lava_flow('North distant', (0, 22, -0.05), 16, 8, 0.8)
lava_flow('West pocket', (-8, -2, -0.05), 6, 10, 0.9)

# ═══════════════════════════════════════════════════════════════════════
# 5. ASH AND EMBER PARTICLES
# ═══════════════════════════════════════════════════════════════════════

def particle_field(name, count, size, velocity_factor=1.0):
    """Volumetric particle emitter for floating ash/embers."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.02)
    particle = bpy.context.object
    particle.name = 'PARTICLE / ' + name + ' source'
    particle.location = (0, 0, 6)
    particle.scale = (30, 30, 15)
    
    # Hide the source mesh
    particle.hide_render = True
    
    col = bpy.data.collections.new('HELL / ' + name)
    s.collection.children.link(col)
    for c in list(particle.users_collection):
        c.objects.unlink(particle)
    col.objects.link(particle)
    
    # Ember material
    mat = bpy.data.materials.new('EMBER / ' + name)
    mat.use_nodes = True
    ns = mat.node_tree.nodes
    ls = mat.node_tree.links
    ns.clear()
    emit = ns.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = (1.0, 0.5, 0.08, 1)
    emit.inputs['Strength'].default_value = 3.0
    out_vol = ns.new('ShaderNodeOutputMaterial')
    ls.new(emit.outputs[0], out_vol.inputs[0])
    particle.data.materials.append(mat)
    
    # Particle system
    ps = particle.modifiers.new('Embers', 'PARTICLE_SYSTEM')
    psys = ps.particle_system
    psys.name = name
    pset = psys.settings
    pset.name = 'Ember settings ' + name
    pset.count = count
    pset.frame_start = 1
    pset.frame_end = 60
    pset.lifetime = 200
    pset.emit_from = 'VOLUME'
    pset.distribution = 'RAND'
    pset.physics_type = 'NEWTON'
    pset.particle_size = size
    pset.mass = 0.001
    pset.normal_factor = 0.5 * velocity_factor
    pset.factor_random = 1.2
    
    # Turbulence
    pset.effector_weights.gravity = 0.02
    tex = bpy.data.textures.new('Turbulence ' + name, 'CLOUDS')
    tex.noise_scale = 1.5
    tex.noise_depth = 4
    pset.active_texture = tex
    # Texture influence on particles (defaults apply)
    
    # Render as object
    pset.render_type = 'OBJECT'
    
    # Create tiny glowing cube for each ember
    bpy.ops.mesh.primitive_cube_add(size=0.02)
    ember_obj = bpy.context.object
    ember_obj.name = 'Ember instance ' + name
    ember_obj.hide_render = False
    emb_mat = bpy.data.materials.new('EMBER glow ' + name)
    emb_mat.use_nodes = True
    ens = emb_mat.node_tree.nodes
    els = emb_mat.node_tree.links
    ens.clear()
    eemit = ens.new('ShaderNodeEmission')
    eemit.inputs['Color'].default_value = (1.0, 0.45, 0.05, 1)
    eemit.inputs['Strength'].default_value = 4.0
    eout = ens.new('ShaderNodeOutputMaterial')
    els.new(eemit.outputs[0], eout.inputs[0])
    ember_obj.data.materials.append(emb_mat)
    for c in list(ember_obj.users_collection):
        c.objects.unlink(ember_obj)
    col.objects.link(ember_obj)
    
    pset.instance_object = ember_obj
    try:
        pset.use_scale_duplicates = True
    except AttributeError:
        pass
    
    return particle, psys

# Ash floating in the air (large, dark)
ash, _ = particle_field('Floating Ash', 800, 0.08, 0.3)
# Glowing embers (small, bright)
particle_field('Fire Embers', 1200, 0.03, 0.7)

# ═══════════════════════════════════════════════════════════════════════
# 6. VOLUMETRIC SMOKE/FOG — atmospheric haze
# ═══════════════════════════════════════════════════════════════════════

# Add a giant cube with volume scatter for atmospheric smoke
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
fog = bpy.context.object
fog.name = 'HELL / Atmospheric Fog'
fog.scale = (60, 60, 1)
fog.hide_render = False
col_fog = bpy.data.collections.new('HELL / Atmosphere')
s.collection.children.link(col_fog)
for c in list(fog.users_collection):
    c.objects.unlink(fog)
col_fog.objects.link(fog)

fog_mat = bpy.data.materials.new('Volcanic Fog')
fog_mat.use_nodes = True
ns = fog_mat.node_tree.nodes
ls = fog_mat.node_tree.links
ns.clear()

# Dense volume scatter in warm tones
vol_scatter = ns.new('ShaderNodeVolumeScatter')
vol_scatter.inputs['Color'].default_value = (0.4, 0.2, 0.08, 1)
vol_scatter.inputs['Density'].default_value = 0.006

vol_absorb = ns.new('ShaderNodeVolumeAbsorption')
vol_absorb.inputs['Color'].default_value = (0.1, 0.05, 0.02, 1)
vol_absorb.inputs['Density'].default_value = 0.0015

vol_mix = ns.new('ShaderNodeAddShader')
ls.new(vol_scatter.outputs[0], vol_mix.inputs[0])
ls.new(vol_absorb.outputs[0], vol_mix.inputs[1])

out_vol = ns.new('ShaderNodeOutputMaterial')
ls.new(vol_mix.outputs[0], out_vol.inputs[0])

fog.data.materials.append(fog_mat)

# ═══════════════════════════════════════════════════════════════════════
# 7. RENDER SETTINGS — higher samples for volumetrics
# ═══════════════════════════════════════════════════════════════════════

s.render.engine = 'CYCLES'
s.cycles.device = 'CPU'
s.cycles.samples = 128
s.cycles.use_denoising = True
s.cycles.adaptive_threshold = 0.03
# Enable volume bounces
s.cycles.max_bounces = 12
s.cycles.volume_bounces = 4
s.cycles.transparent_max_bounces = 8
# Light sampling for many lights
s.cycles.use_light_tree = True

s.render.resolution_x = 1800
s.render.resolution_y = 1350
s.render.resolution_percentage = 100

s['scene'] = 'NUCLEAR-VOLCANIC HELLSCAPE: Exposed-frame garage endures the apocalypse.'
s['features'] = 'Volumetric mushroom clouds, lava flows, ember particles, atmospheric fog, fire sky, nuclear flash lighting.'

# Set frame so ember/ash particles have time to disperse
s.frame_set(80)

# ═══════════════════════════════════════════════════════════════════════
# 8. SAVE AND RENDER
# ═══════════════════════════════════════════════════════════════════════

bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(R / 'backyard-apocalypse.blend'))

# Cameras from the existing scene
cameras = [
    ('01 / Whole backyard', '01-apocalypse-overview'),
    ('PROPOSED / Patio to garage', '02-apocalypse-patio'),
    ('PROPOSED / Elevated southwest', '03-apocalypse-elevated'),
    ('EXPOSED / Southwest exterior', '04-apocalypse-southwest'),
    ('EXPOSED / Northwest exterior', '05-apocalypse-northwest'),
]

for cam_name, file_name in cameras:
    cam = bpy.data.objects.get(cam_name)
    if cam:
        s.camera = cam
        s.render.filepath = str(R / (file_name + '.png'))
        bpy.ops.render.render(write_still=True)
        print('DONE ' + file_name, flush=True)
    else:
        print('MISSING CAMERA: ' + cam_name, flush=True)

print('APOCALYPSE RENDER COMPLETE', flush=True)