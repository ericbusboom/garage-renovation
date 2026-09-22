"""The existing garage, drawn under the new frame, and where the two collide.

The question this answers is a sequencing one: how much of the new structure can
be erected while the existing roof is still on. So the roof is drawn as a
surface and shaded red wherever a new member passes through it -- each red patch
is somewhere the roof has to be opened before that member can go in, and the grey
remainder is what can stay.

Geometry comes from ``model/parameters.json``, the existing-conditions record,
and the roof surface is the same hip function ``construction-sequence-study``
uses, so this drawing and that study cannot disagree:

    z(x, y) = wall_top + rise * min(x/(W/2), (W-x)/(W/2),
                                    y/((L-ridge)/2), (L-y)/((L-ridge)/2), 1)

The existing building's outside south-west corner is the origin of the frame's
coordinate system, so no transform is needed between them.
"""
from __future__ import annotations

import json
import math
import numpy as np

import frame as framemod
from project_paths import PROJECT_ROOT as ROOT, MODEL_DIR

PARAMS = json.loads((MODEL_DIR / 'parameters.json').read_text())

W = PARAMS['width']
L = PARAMS['length']
WALL_TOP = PARAMS['wall_height']
RISE = PARAMS['roof_rise']
RIDGE = PARAMS['ridge_length']
PEAK = WALL_TOP + RISE
THICK = {'west': PARAMS['wall_west'], 'east': PARAMS['wall_east'],
         'south': PARAMS['wall_south'], 'north': PARAMS['wall_north']}

GREY = '#9aa3ab'
RED = '#c1292e'


def roof_z(x, y):
    """Height of the existing hip roof above the origin datum."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    half_y = (L - RIDGE) / 2.0
    f = np.minimum.reduce([x / (W / 2.0), (W - x) / (W / 2.0),
                           y / half_y, (L - y) / half_y,
                           np.ones(np.broadcast(x, y).shape)])
    return WALL_TOP + RISE * np.clip(f, 0.0, 1.0)


def inside(x: float, y: float) -> bool:
    return 0.0 <= x <= W and 0.0 <= y <= L


# ---------------------------------------------------------------------------
# walls
# ---------------------------------------------------------------------------

#: The doors and windows recorded in the existing-conditions model. Offsets
#: follow ``model/build_model.py``: measured from the east edge on the south and
#: north walls, from the south end on the west wall.
GLASS = '#6f7c88'


def openings(side: str) -> list[tuple[float, float, float, float]]:
    """Openings on one wall as (along-axis start, end, sill, head)."""
    out = []
    for op in PARAMS.get('openings', ()):
        if op['side'] != side:
            continue
        w = float(op['width'])
        kind = op['type']
        z0 = float(PARAMS['window_sill']) if kind == 'window' else 0.0
        h = (PARAMS['window_height'] if kind == 'window'
             else PARAMS['door_height'] if kind == 'door'
             else PARAMS['garage_door_height'])
        a0 = (float(op['offset']) if side == 'west'
              else W - float(op['offset']) - w)
        out.append((a0, a0 + w, z0, z0 + float(h)))
    return sorted(out)


def _box(verts, faces, x0, x1, y0, y1, z0, z1):
    base = len(verts)
    for z in (z0, z1):
        verts += [[x0, y0, z], [x1, y0, z], [x1, y1, z], [x0, y1, z]]
    faces += [(base + a, base + b, base + c) for a, b, c in (
        (0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6),
        (0, 4, 5), (0, 5, 1), (1, 5, 6), (1, 6, 2),
        (2, 6, 7), (2, 7, 3), (3, 7, 4), (3, 4, 0))]


def _pierced(verts, faces, side, along0, along1, cross0, cross1, horizontal):
    """One wall, tiled with sub-boxes so the openings are left as holes.

    No CSG: the wall is emitted as the solid pieces around each opening -- full
    height between them, then the spandrel over each one and the sill under it.
    """
    cuts = [o for o in openings(side) if along0 - 1e-6 < o[0] and o[1] < along1 + 1e-6]
    def put(a0, a1, z0, z1):
        if a1 - a0 > 1e-6 and z1 - z0 > 1e-6:
            if horizontal:
                _box(verts, faces, a0, a1, cross0, cross1, z0, z1)
            else:
                _box(verts, faces, cross0, cross1, a0, a1, z0, z1)
    cursor = along0
    for a0, a1, z0, z1 in cuts:
        put(cursor, a0, 0.0, WALL_TOP)      # solid pier before the opening
        put(a0, a1, 0.0, z0)                # under the sill
        put(a0, a1, z1, WALL_TOP)           # over the head
        cursor = a1
    put(cursor, along1, 0.0, WALL_TOP)


def wall_mesh():
    """The four existing walls, with the doors and windows cut out of them."""
    verts, faces = [], []
    _pierced(verts, faces, 'west', 0.0, L, 0.0, THICK['west'], False)
    _pierced(verts, faces, 'east', 0.0, L, W - THICK['east'], W, False)
    _pierced(verts, faces, 'south', THICK['west'], W - THICK['east'],
             0.0, THICK['south'], True)
    _pierced(verts, faces, 'north', THICK['west'], W - THICK['east'],
             L - THICK['north'], L, True)
    return verts, faces


def opening_mesh():
    """A thin leaf in each opening, so a door reads as a door and not a gap."""
    verts, faces = [], []
    for side in ('west', 'east', 'south', 'north'):
        for a0, a1, z0, z1 in openings(side):
            if side == 'west':
                _box(verts, faces, 1.0, THICK['west'] - 1.0, a0, a1, z0, z1)
            elif side == 'east':
                _box(verts, faces, W - THICK['east'] + 1.0, W - 1.0, a0, a1, z0, z1)
            elif side == 'south':
                _box(verts, faces, a0, a1, 1.0, THICK['south'] - 1.0, z0, z1)
            else:
                _box(verts, faces, a0, a1, L - THICK['north'] + 1.0, L - 1.0, z0, z1)
    return verts, faces


# ---------------------------------------------------------------------------
# roof, with the clash colouring
# ---------------------------------------------------------------------------

def roof_mesh(frame: framemod.Frame, omit: set[str] = frozenset(),
              step: float = 6.0, pad: float = 3.0):
    """Roof surface triangles plus a colour per triangle: grey, or red at a clash.

    ``pad`` widens each clash by a couple of inches so a red patch is the size of
    an opening someone would actually cut, not a hairline where the axis crosses.
    """
    nx = max(2, int(round(W / step)))
    ny = max(2, int(round(L / step)))
    xs = np.linspace(0.0, W, nx + 1)
    ys = np.linspace(0.0, L, ny + 1)
    gx, gy = np.meshgrid(xs, ys, indexing='ij')
    gz = roof_z(gx, gy)

    clashes, members = _clash_cells(frame, omit, xs, ys, pad)

    verts = [[round(float(gx[i, j]), 2), round(float(gy[i, j]), 2),
              round(float(gz[i, j]), 2)]
             for i in range(nx + 1) for j in range(ny + 1)]

    def vid(i, j):
        return i * (ny + 1) + j

    faces, colors = [], []
    for i in range(nx):
        for j in range(ny):
            hot = (i, j) in clashes
            faces.append((vid(i, j), vid(i + 1, j), vid(i + 1, j + 1)))
            faces.append((vid(i, j), vid(i + 1, j + 1), vid(i, j + 1)))
            colors += [RED if hot else GREY] * 2
    return verts, faces, colors, members, len(clashes) / float(nx * ny)


def _clash_cells(frame: framemod.Frame, omit: set[str], xs, ys, pad: float):
    """Grid cells the new frame passes through, and the members responsible."""
    cells: set[tuple[int, int]] = set()
    culprits: dict[str, float] = {}
    dx = xs[1] - xs[0]
    dy = ys[1] - ys[0]
    for member in frame.members:
        if member in omit:
            continue
        sec = frame.section_of[member]
        half = max(sec.d, sec.b) / 2.0
        segs = framemod._ordered(frame, [(i, j) for m, i, j in frame.segments
                                         if m == member])
        for a_name, b_name in segs:
            a, b = frame.xyz(a_name), frame.xyz(b_name)
            n = max(2, int(math.dist(a, b) / 2.0))
            for k in range(n + 1):
                t = k / n
                px = a[0] + t * (b[0] - a[0])
                py = a[1] + t * (b[1] - a[1])
                pz = a[2] + t * (b[2] - a[2])
                if not inside(px, py):
                    continue
                rz = float(roof_z(px, py))
                # the roof surface passes through this member's depth
                if pz - half <= rz <= pz + half:
                    culprits[member] = min(culprits.get(member, 1e9), rz)
                    i0 = int((px - pad) // dx)
                    i1 = int((px + pad) // dx)
                    j0 = int((py - pad) // dy)
                    j1 = int((py + pad) // dy)
                    for i in range(max(0, i0), min(len(xs) - 2, i1) + 1):
                        for j in range(max(0, j0), min(len(ys) - 2, j1) + 1):
                            cells.add((i, j))
    return cells, sorted(culprits)


def summary(frame: framemod.Frame, omit: set[str] = frozenset()) -> dict:
    _, _, _, members, fraction = roof_mesh(frame, omit)
    return dict(footprint_in=[W, L], wall_top_z=WALL_TOP, peak_z=PEAK,
                clashing_members=members,
                roof_area_disturbed_pct=round(100.0 * fraction, 1))
