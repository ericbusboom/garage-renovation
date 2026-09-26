"""Outer walls, doors and roofs for the solid viewer's "Outer walls" view.

The walls are thin panels set on the *inside* of the steel: each panel's inside
face is flush with the inside face of the posts on its line, and it is
``WALL_T`` thick outward from there, so the 5 in. posts, the beams and every
brace stand proud of the skin on the outside. The existing garage walls that
stay on the outside of the building are drawn in the same colour.

Every section carries a position code: the face it is on (N, S, E, W), L for
the ground storey (slab to the loft beams, z 0-112.5) or U for the loft storey
(loft beams to the roof), and a number counted west to east on the north and
south faces and south to north on the east and west faces. NL2 is the second
section on the lower north face. Doors are numbered in the same sequence and
say so in their hover.

Roofs: the solar slope is black; the hipped cap over the flat top, the
lean-to and the flat roof over the shed are dark grey; the cap's soffit and
fascia are white. The garage-door jamb post ``NJ`` is drawn here too. It is not
in the frame model and carries nothing: pinned top and bottom, removable, and
there only so the two door leaves have something to close against.
"""
from __future__ import annotations

import plotly.graph_objects as go

import cabinets as CB
import existing as EX
import frame as framemod

WALL_T = 2.0                 # panel thickness, outward from the steel's inside face
POST_HALF = 2.5              # HSS5X5 posts: inside face is 2.5 in. off the line
WALL = '#d3d6d9'             # light grey panels
DOOR = '#8fa9c2'             # door leaves, blue-grey so they read as doors
GLASS = '#a9c8da'            # clerestory glazing
BEAM = '#f4f4f1'             # frame colour in this view
SOLAR = '#141618'            # black solar roof
ROOF = '#4a4f55'             # dark grey metal roof
TRIM = '#fbfbf9'             # soffit and fascia

HIP_RISE = 18.0              # eave to ridge
SOFFIT = 4.0                 # soffit width beyond the outside of the steel
FASCIA = 4.0                 # fascia depth
FASCIA_T = 1.0
ROOF_T = 1.5

JAMB = dict(name='NJ', b=2.0, d=5.0, section='HSS5X2X1/8 (conceptual)')

LOFT_Z = 112.5               # loft beam centreline: the storey split


def _pt(frame, member):
    return CB._base_point(frame, member)


def _top(frame, member):
    """Top of steel of a horizontal member."""
    return CB._ends(frame, member)[0][2] + frame.section_of[member].d / 2.0


def geometry(frame: framemod.Frame) -> dict:
    """The lines the walls and roofs are set out from, all read from the frame."""
    (ya, za), (yb, zb) = [(p[1], p[2]) for p in CB._ends(frame, 'W.slope')]
    k = (zb - za) / (yb - ya)
    lift = 1.8                   # HSS3 slope chord: half depth measured vertically
    roof_base = max(_top(frame, m) for m in ('R-W3', 'R-W4', 'E.top', 'W.top'))
    be_upper = CB._ends(frame, 'BE.upper')
    hx = be_upper[0][0] + frame.section_of['BE.upper'].b / 2.0
    lx = CB._ends(frame, 'BE')[0][0] + frame.section_of['BE'].b / 2.0
    ht = max(p[2] for p in be_upper) + frame.section_of['BE.upper'].d / 2.0
    lt = _top(frame, 'BE')
    g = dict(
        west=CB._ends(frame, 'BW')[0][0], east_upper=be_upper[0][0], east=lx - frame.section_of['BE'].b / 2.0,
        south=CB._ends(frame, 'B-SO')[0][1], north=CB._ends(frame, 'B-N')[0][1],
        clerestory=yb, eave_y=ya,
        slope=lambda y: za + k * (y - ya) + lift,     # underside of the solar roof
        slope_k=k, roof_base=roof_base,
        lean_hx=hx, lean_lx=lx, lean_ht=ht, lean_lt=lt,
        lean=lambda x: ht + (lt - ht) * (x - hx) / (lx - hx),
    )
    n1, n2 = _pt(frame, 'N1'), _pt(frame, 'N2')
    g['jamb_x'] = (n1[0] + n2[0]) / 2.0
    return g


# --------------------------------------------------------------------------
# the wall schedule
# --------------------------------------------------------------------------

def _panel(axis, t0, t1, pts):
    """A convex (along, z) polygon in a plane of constant ``axis``, t0..t1 thick."""
    if axis == 'x':                       # wall runs north-south
        poly = [(t0, a, z) for a, z in pts]
        off = (t1 - t0, 0.0, 0.0)
    else:                                 # wall runs east-west
        poly = [(a, t0, z) for a, z in pts]
        off = (0.0, t1 - t0, 0.0)
    return CB._slab(poly, off)


def _rect(a0, a1, z0, z1):
    return [(a0, z0), (a1, z0), (a1, z1), (a0, z1)]


def _under(a0, a1, z0, top):
    """A panel from z0 up to a sloping top line ``top(along)``."""
    return [(a0, z0), (a1, z0), (a1, top(a1)), (a0, top(a0))]


def _outside(inner, sign):
    """Thickness range of a panel whose inside face is ``inner``; sign +1 = outward is +axis."""
    return (inner, inner + WALL_T) if sign > 0 else (inner - WALL_T, inner)


def _existing(side, a0, a1, c0, c1, top):
    """An existing wall, openings cut, topped up with new infill to ``top``."""
    verts, faces = [], []
    EX._pierced(verts, faces, side, a0, a1, c0, c1, side in ('south', 'north'))
    if side in ('south', 'north'):
        EX._box(verts, faces, a0, a1, c0, c1, EX.WALL_TOP, top)
    else:
        EX._box(verts, faces, c0, c1, a0, a1, EX.WALL_TOP, top)
    leaves = []
    for o0, o1, z0, z1 in EX.openings(side):
        if a0 - 1e-6 < o0 and o1 < a1 + 1e-6:
            leaves.append((o0, o1, z0, z1))
    return verts, faces, leaves


def sections(frame: framemod.Frame) -> list[dict]:
    """Every outer wall, door and glazing section, with its position code."""
    g = geometry(frame)
    X = lambda m: _pt(frame, m)[0]
    Y = lambda m: _pt(frame, m)[1]
    west, north, south = g['west'], g['north'], g['south']
    east_up, east = g['east_upper'], g['east']
    top = g['roof_base']
    slope = g['slope']
    lean = g['lean']
    w3y = CB._ends(frame, 'W3')[0][1]
    w1y = CB._ends(frame, 'W1')[0][1]
    s3y = CB._ends(frame, 'S3')[0][1]
    nm2 = CB._ends(frame, 'N-M2')[0][0]
    nm = CB._ends(frame, 'N-M')[0][0]
    n1, n2, en2 = X('N1'), X('N2'), X('E-N2')
    bx0, bx1, by0, _ = CB._shed_bounds(frame)
    be_top = _top(frame, 'BE')
    jx = g['jamb_x']

    # Inside faces of each line.
    wi = west + POST_HALF                          # west line, inside is +x
    ni = north - POST_HALF                         # north line, inside is -y
    eu_i = east_up - POST_HALF                     # upper east line, inside is -x
    ei = east - POST_HALF                          # outer east line, inside is -x
    shed_s = by0 + CB.SHED_WALL_T                  # shed faces, where its equipment is set out
    shed_e = bx1 - CB.SHED_WALL_T
    lean_s = s3y + POST_HALF                       # lean-to south end, inside is +y

    out = []
    def add(code, where, kind, axis, trange, pts, note=''):
        out.append(dict(code=code, where=where, kind=kind, axis=axis,
                        t=trange, pts=pts, note=note))

    # ---- west face (south to north)
    add('WL1', 'existing west wall, y 0 → W3', 'existing', 'x',
        (0.0, EX.THICK['west']), None,
        note=('west', 0.0, w3y, 0.0, EX.THICK['west']))
    add('WL2', 'W3 → W4', 'wall', 'x', _outside(wi, -1),
        _rect(w3y, north, 0.0, LOFT_Z))
    add('WU1', 'SW0 → W1, under the solar slope', 'wall', 'x', _outside(wi, -1),
        _under(south, w1y, LOFT_Z, slope))
    add('WU2', 'W1 → W2, under the solar slope', 'wall', 'x', _outside(wi, -1),
        _under(w1y, g['clerestory'], LOFT_Z, slope))
    add('WU3', 'W2 → W3', 'wall', 'x', _outside(wi, -1),
        _rect(g['clerestory'], w3y, LOFT_Z, top))
    add('WU4', 'W3 → W4, behind W.rear.brace', 'wall', 'x', _outside(wi, -1),
        _rect(w3y, north, LOFT_Z, top))

    # ---- north face (west to east)
    ny = _outside(ni, +1)
    door_y = (ni, ni + WALL_T - 0.5)
    add('NL1', 'W4 → N1, behind BR-N', 'wall', 'y', ny, _rect(west, n1, 0.0, LOFT_Z))
    add('NL2', 'garage door, west leaf · N1 → NJ', 'door', 'y', door_y,
        _rect(n1 + POST_HALF, jx - JAMB['b'] / 2, 0.0, _soffit_bn(frame)))
    add('NL3', 'garage door, east leaf · NJ → N2', 'door', 'y', door_y,
        _rect(jx + JAMB['b'] / 2, n2 - POST_HALF, 0.0, _soffit_bn(frame)))
    add('NL4', 'N2 → E-N2', 'wall', 'y', ny, _rect(n2, en2, 0.0, be_top))
    add('NU1', 'W4 → N-M2', 'wall', 'y', ny, _rect(west, nm2, LOFT_Z, top))
    add('NU2', 'loft loading door · N-M2 → N-M', 'door', 'y', door_y,
        _rect(nm2 + 1.5, nm - 1.5, CB.floor_top(frame), top))
    add('NU3', 'N-M → N2, behind BR-NU-1', 'wall', 'y', ny, _rect(nm, n2, LOFT_Z, top))
    add('NU4', 'lean-to north end · N2 → E-N2', 'wall', 'y', ny,
        _under(east_up, ei, LOFT_Z, lean))

    # ---- east face (south to north)
    add('EL1', 'shed east wall · E-S2 → existing building', 'wall', 'x',
        _outside(shed_e, +1), _rect(by0, 0.0, 0.0, be_top))
    add('EL2', 'existing east wall', 'existing', 'x', None, None,
        note=('east', 0.0, EX.L, EX.W - EX.THICK['east'], EX.W))
    add('EL3', 'E-N2 → existing building', 'wall', 'x', _outside(ei, +1),
        _rect(EX.L, north, 0.0, be_top))
    add('EU1', 'upper east line, south of S3, under the solar slope', 'wall', 'x',
        _outside(eu_i, +1), _under(south, s3y, LOFT_Z, slope))
    add('EU2', 'S3 → E.clerestory, under the solar slope', 'wall', 'x',
        _outside(eu_i, +1), _under(s3y, g['clerestory'], LOFT_Z, slope))
    add('EU3', 'E.clerestory → E.W3', 'wall', 'x', _outside(eu_i, +1),
        _rect(g['clerestory'], w3y, LOFT_Z, top))
    add('EU4', 'E.W3 → N2', 'wall', 'x', _outside(eu_i, +1),
        _rect(w3y, north, LOFT_Z, top))

    # ---- south face (west to east)
    add('SL1', 'W3 → existing west wall', 'wall', 'y', _outside(w3y + POST_HALF, -1),
        _rect(west, 0.0, 0.0, LOFT_Z))
    add('SL2', 'existing south wall', 'existing', 'y', None, None,
        note=('south', 0.0, EX.W, 0.0, EX.THICK['south']))
    add('SL3', 'shed south wall · S1 → E-S2', 'wall', 'y', _outside(shed_s, -1),
        _rect(bx0, bx1, 0.0, be_top))
    add('SU1', 'solar eave strip over B-SO · SW0 → upper east line', 'wall', 'y',
        _outside(south + POST_HALF, -1),
        _rect(west, east_up, LOFT_Z, slope(south + POST_HALF - WALL_T)))
    mull = sorted(CB._ends(frame, f'CT.mullion.{i}')[0][0] for i in range(1, 6))
    stops = [west] + mull + [east_up]
    cy = g['clerestory'] + 1.25
    for i, (a, b) in enumerate(zip(stops, stops[1:])):
        add(f'SU{i + 2}', f'clerestory glazing · x {a:g} → {b:g}', 'glass', 'y',
            (cy, cy + 1.0), _rect(a, b, g['slope'](g['clerestory']) - 2.0, top))
    add(f'SU{len(stops) + 1}', 'lean-to south end · S3 → E-S3', 'wall', 'y',
        _outside(lean_s, -1), _under(east_up, ei, LOFT_Z, lean))
    return out


def _soffit_bn(frame):
    return CB._soffit(frame, 'B-N')


# --------------------------------------------------------------------------
# traces
# --------------------------------------------------------------------------

KIND_TEXT = dict(wall='new wall panel', door='door', glass='clerestory glazing',
                 existing='existing garage wall (retained)')
KIND_COLOR = dict(wall=WALL, door=DOOR, glass=GLASS, existing=WALL)
FACE = dict(N='north', S='south', E='east', W='west')
LEVEL = dict(L='lower', U='upper')


def _trace(verts, faces, color, name, hover, opacity=1.0):
    return go.Mesh3d(
        x=[v[0] for v in verts], y=[v[1] for v in verts], z=[v[2] for v in verts],
        i=[f[0] for f in faces], j=[f[1] for f in faces], k=[f[2] for f in faces],
        color=color, opacity=opacity, flatshading=True,
        lighting=dict(ambient=0.7, diffuse=0.75, specular=0.05, roughness=0.95),
        lightposition=dict(x=-8000, y=-12000, z=16000),
        name=name, hovertemplate=hover + '<extra></extra>', showlegend=False,
        visible=False)


def _hover(s):
    code = s['code']
    head = f'<b>{code}</b> · {FACE[code[0]]} {LEVEL[code[1]]} {code[2:]}'
    kind = KIND_TEXT[s['kind']]
    if s['kind'] == 'door':
        kind = '<b>DOOR</b>'
    lines = [head, s['where'], kind]
    if s['kind'] == 'wall':
        lines.append(f'{WALL_T:g} in. panel, inside face flush with the steel')
    if s['kind'] == 'existing':
        lines.append(f'openings cut; new infill above z = {EX.WALL_TOP:g}')
    if s.get('pts'):
        zs = [p[1] for p in s['pts']]
        al = [p[0] for p in s['pts']]
        lines.append(f'{"y" if s["axis"] == "x" else "x"} {min(al):g} → {max(al):g}'
                     f' · z {min(zs):.1f} → {max(zs):.1f}')
    return '<br>'.join(lines)


def wall_traces(frame: framemod.Frame) -> tuple[list, list[dict]]:
    rows = sections(frame)
    be_top = _top(frame, 'BE')
    out = []
    for s in rows:
        if s['kind'] == 'existing':
            side, a0, a1, c0, c1 = s['note']
            v, f, leaves = _existing(side, a0, a1, c0, c1,
                                     LOFT_Z if side != 'east' else be_top)
            out.append(_trace(v, f, WALL, s['code'], _hover(s)))
            for o0, o1, z0, z1 in leaves:
                lv, lf = [], []
                mid0, mid1 = c0 + 1.0, c1 - 1.0
                if side in ('south', 'north'):
                    EX._box(lv, lf, o0, o1, mid0, mid1, z0, z1)
                else:
                    EX._box(lv, lf, mid0, mid1, o0, o1, z0, z1)
                is_door = z0 < 1.0
                out.append(_trace(lv, lf, DOOR if is_door else GLASS,
                                  f'{s["code"]} opening',
                                  f'<b>{s["code"]}</b> · existing '
                                  f'{"door" if is_door else "window"}<br>'
                                  f'{o0:g} → {o1:g} · z {z0:g} → {z1:g}',
                                  opacity=1.0 if is_door else 0.6))
            continue
        v, f = _panel(s['axis'], *s['t'], s['pts'])
        out.append(_trace(v, f, KIND_COLOR[s['kind']], s['code'], _hover(s),
                          opacity=0.55 if s['kind'] == 'glass' else 1.0))
    return out, rows


def roof_traces(frame: framemod.Frame) -> list:
    g = geometry(frame)
    out = []
    # Solar slope: one black slab on the rafter tops, outside of steel to outside.
    x0, x1 = g['west'] - POST_HALF, g['east_upper'] + POST_HALF
    y0, y1 = g['south'] - POST_HALF, g['clerestory']
    s = g['slope']
    v, f = CB._slab([(x0, y0, s(y0)), (x1, y0, s(y0)), (x1, y1, s(y1)), (x0, y1, s(y1))],
                    (0.0, 0.0, ROOF_T))
    out.append(_trace(v, f, SOLAR, 'solar roof',
                      '<b>Solar roof</b><br>south slope, flush panels on the rafters'
                      f'<br>y {y0:g} → {y1:g}'))

    # Hipped cap over the flat top. Outside of steel, then the soffit, then the
    # fascia; the roof starts at the fascia top and rises HIP_RISE to the ridge.
    ox0, ox1 = g['west'] - POST_HALF, g['east_upper'] + POST_HALF
    oy0, oy1 = g['clerestory'] - POST_HALF, g['north'] + POST_HALF
    fx0, fx1 = ox0 - SOFFIT, ox1 + SOFFIT              # fascia inside faces
    fy0, fy1 = oy0 - SOFFIT, oy1 + SOFFIT
    X0, X1, Y0, Y1 = fx0 - FASCIA_T, fx1 + FASCIA_T, fy0 - FASCIA_T, fy1 + FASCIA_T
    zb = g['roof_base']
    ze = zb + FASCIA
    zr = ze + HIP_RISE
    half = min(X1 - X0, Y1 - Y0) / 2.0
    if X1 - X0 >= Y1 - Y0:
        ry = (Y0 + Y1) / 2.0
        r0, r1 = (X0 + half, ry), (X1 - half, ry)
    else:
        rx = (X0 + X1) / 2.0
        r0, r1 = (rx, Y0 + half), (rx, Y1 - half)
    R0, R1 = (*r0, zr), (*r1, zr)
    planes = [
        ('south', [(X0, Y0, ze), (X1, Y0, ze), R1, R0]),
        ('north', [(X1, Y1, ze), (X0, Y1, ze), R0, R1]),
        ('west', [(X0, Y1, ze), (X0, Y0, ze), R0]),
        ('east', [(X1, Y0, ze), (X1, Y1, ze), R1]),
    ]
    for name, poly in planes:
        v, f = CB._slab(poly, (0.0, 0.0, ROOF_T))
        out.append(_trace(v, f, ROOF, f'hip roof {name}',
                          f'<b>Hipped roof — {name} plane</b><br>{HIP_RISE:g} in. rise '
                          f'over {half:.0f} in. · eave z {ze:g} · ridge z {zr:g}'))
    ring = [
        ('south', (fx0, fx1, fy0 - FASCIA_T, fy0), (fx0, fx1, fy0, oy0)),
        ('north', (fx0, fx1, fy1, fy1 + FASCIA_T), (fx0, fx1, oy1, fy1)),
        ('west', (fx0 - FASCIA_T, fx0, Y0, Y1), (fx0, ox0, fy0, fy1)),
        ('east', (fx1, fx1 + FASCIA_T, Y0, Y1), (ox1, fx1, fy0, fy1)),
    ]
    for name, fb, sb in ring:
        v, f = CB._box(*fb, zb, ze)
        out.append(_trace(v, f, TRIM, f'fascia {name}',
                          f'<b>Fascia — {name}</b><br>{FASCIA:g} in. deep · white'))
        v, f = CB._box(*sb, zb, zb + 0.75)
        out.append(_trace(v, f, TRIM, f'soffit {name}',
                          f'<b>Soffit — {name}</b><br>{SOFFIT:g} in. beyond the steel · white'))

    # Lean-to: dark grey sheet on the rafter tops, BE.upper to the outer BE edge.
    ly0, ly1 = 0.0, g['north'] + POST_HALF
    hx, lx = g['lean_hx'], g['lean_lx']
    v, f = CB._slab([(hx, ly0, g['lean'](hx)), (lx, ly0, g['lean'](lx)),
                     (lx, ly1, g['lean'](lx)), (hx, ly1, g['lean'](hx))],
                    (0.0, 0.0, 1.2))
    out.append(_trace(v, f, ROOF, 'lean-to roof',
                      '<b>Lean-to roof</b><br>metal sheet on the LT rafters'))
    # Over the shed, east of the solar slope, nothing is framed. A flat sheet at
    # beam top closes it so the view reads as a building; it is an assumption.
    sy0 = g['south'] - POST_HALF
    zs = _top(frame, 'BE')
    v, f = CB._box(g['east_upper'] - POST_HALF + WALL_T, lx, sy0, ly0 + 3.0, zs, zs + 1.2)
    out.append(_trace(v, f, ROOF, 'shed roof',
                      '<b>Shed roof, east of the solar slope</b><br>flat sheet at BE top'
                      '<br><i>assumed; no roof framing is modelled here</i>'))
    return out


def jamb_trace(frame: framemod.Frame):
    """The non-structural garage-door jamb post midway between N1 and N2."""
    g = geometry(frame)
    x, y = g['jamb_x'], g['north']
    z1 = _soffit_bn(frame)
    v, f = CB._box(x - JAMB['b'] / 2, x + JAMB['b'] / 2,
                   y - JAMB['d'] / 2, y + JAMB['d'] / 2, 0.0, z1)
    return go.Mesh3d(
        x=[p[0] for p in v], y=[p[1] for p in v], z=[p[2] for p in v],
        i=[q[0] for q in f], j=[q[1] for q in f], k=[q[2] for q in f],
        color='#87919d', flatshading=True, opacity=1.0, name='NJ',
        lighting=dict(ambient=0.62, diffuse=0.85, specular=0.12, roughness=0.9),
        lightposition=dict(x=-8000, y=-12000, z=16000), showlegend=False,
        hovertemplate=(f'<b>NJ</b> · garage-door jamb post<br>{JAMB["section"]}'
                       f'<br>{JAMB["b"]:g} wide × {JAMB["d"]:g} deep in. · x = {x:g}, '
                       f'midway N1–N2<br>z 0 → {z1:g}, pinned top and bottom'
                       '<br><b>not structural</b> — removable, not in the analysis'
                       '<extra></extra>'))


def html(frame: framemod.Frame, rows: list[dict]) -> str:
    g = geometry(frame)
    body = ''.join(
        f'<tr><td><b>{r["code"]}</b></td><td>{FACE[r["code"][0]]} '
        f'{LEVEL[r["code"][1]]}</td><td>{r["where"]}</td>'
        f'<td>{"<b>door</b>" if r["kind"] == "door" else KIND_TEXT[r["kind"]]}</td></tr>'
        for r in rows)
    return f"""
<div class="notes">
  <h2>Outer walls and roofs</h2>
  <p>Tick <b>Outer walls</b> to close the building in. The frame turns white and
  the walls are light grey {WALL_T:g} in. panels whose inside face is flush with
  the inside of the steel, so posts, beams and every brace (BR-N, BR-NU-1,
  BR-S, BR-W-2, W.rear.brace) stand proud of them on the outside. The existing
  garage walls that remain on the outside are drawn in the same grey with their
  openings. Doors are blue-grey. Hover a section for its code: face (N/S/E/W),
  L (ground storey) or U (loft storey), then a number counted west→east or
  south→north.</p>
  <p><b>Roofs</b> go on with it (and have their own box): the solar slope is
  black; a hipped cap with a {HIP_RISE:g} in. rise sits over the flat top, with a
  {SOFFIT:g} in. white soffit and {FASCIA:g} in. white fascia all round, ridge at
  z = {g['roof_base'] + FASCIA + HIP_RISE:g}; the lean-to and the unframed strip
  over the shed are dark grey.</p>
  <p><b>NJ</b>, the garage-door jamb post at x = {g['jamb_x']:g} midway between N1
  and N2, is conceptual HSS5×2: 5 in. deep through the wall, 2 in. wide. It is
  pinned top and bottom, removable, and not in the analysis; NL2 and NL3 are the
  two door leaves either side of it.</p>
  <table><tr><th>Code</th><th>Face</th><th>Where</th><th>What</th></tr>{body}</table>
  <p><small>Conceptual envelope for appearance only: panel system, attachment,
  weatherproofing, the flat roof over the shed and the cap's framing are not
  designed, and no wall is credited as bracing.</small></p>
</div>
"""
