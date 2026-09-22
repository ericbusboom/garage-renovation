"""BEAM-001 plan — columns, beam grid and the existing building, top down.

Writes beam-plan.png and beam-plan.svg. PNG is drawn at 2x and downsampled.
"""
import html
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import geometry as G

OUT = Path(__file__).resolve().parent
W, H = 1900, 1460
SS = 2
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'

INK = '#333e46'
GRAY = '#d9dde0'
LABEL = '#9aa2a8'
BLUE = '#32677e'
TEAL = '#397f77'
BEAM = '#b4472f'
AMBER = '#b17a36'
BEAM_OPT = '#d99a86'
COL = '#1f2d34'
PLUM = '#8e4b6e'

im = Image.new('RGB', (W * SS, H * SS), 'white')
dr = ImageDraw.Draw(im)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/>']
_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT, size * SS)
    return _fonts[size]


def line(x1, y1, x2, y2, c=INK, w=1.0, dash=None):
    d = f' stroke-dasharray="{dash[0]} {dash[1]}"' if dash else ''
    svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
               f'stroke="{c}" stroke-width="{w}"{d} stroke-linecap="round"/>')
    pw = max(1, round(w * SS))
    if dash:
        on, off = dash
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist == 0:
            return
        k = 0.0
        while k < dist:
            a, b = k / dist, min(k + on, dist) / dist
            dr.line([(SS * (x1 + (x2 - x1) * a), SS * (y1 + (y2 - y1) * a)),
                     (SS * (x1 + (x2 - x1) * b), SS * (y1 + (y2 - y1) * b))], fill=c, width=pw)
            k += on + off
    else:
        dr.line([(x1 * SS, y1 * SS), (x2 * SS, y2 * SS)], fill=c, width=pw)


def box(x1, y1, x2, y2, fill=None, c=INK, w=1.0, dash=None):
    if fill:
        svg.append(f'<rect x="{min(x1,x2):.1f}" y="{min(y1,y2):.1f}" width="{abs(x2-x1):.1f}" '
                   f'height="{abs(y2-y1):.1f}" fill="{fill}"/>')
        dr.rectangle([min(x1, x2) * SS, min(y1, y2) * SS, max(x1, x2) * SS, max(y1, y2) * SS], fill=fill)
    if c:
        for a, b, d, e in [(x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)]:
            line(a, b, d, e, c, w, dash)


def text(x, y, t, size=14, c=INK, anchor='start', weight=None):
    wt = ' font-weight="bold"' if weight else ''
    svg.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{c}" font-family="Arial, Helvetica, sans-serif" '
               f'font-size="{size}" text-anchor="{anchor}"{wt}>{html.escape(t)}</text>')
    dr.text((x * SS, y * SS), t, fill=c, font=font(size),
            anchor={'start': 'ls', 'middle': 'ms', 'end': 'rs'}[anchor])


def group(name):
    svg.append(f'<g id="{name}">')


def end():
    svg.append('</g>')


# ---------------------------------------------------------------- plan mapping
S = 2.35
OX, OY = 579, 1040


def xy(x, y):
    return OX + x * S, OY - y * S


def pl(x1, y1, x2, y2, c=INK, w=1.0, dash=None):
    line(*xy(x1, y1), *xy(x2, y2), c, w, dash)


def pbox(x1, y1, x2, y2, fill=None, c=INK, w=1.0, dash=None):
    a, b = xy(x1, y1), xy(x2, y2)
    box(a[0], a[1], b[0], b[1], fill, c, w, dash)


def ptext(x, y, t, size=13, c=INK, anchor='start', dx=0, dy=0, weight=None):
    sx, sy = xy(x, y)
    text(sx + dx, sy + dy, t, size, c, anchor, weight)


def dim_h(x1, x2, y, t, c=INK, size=12):
    pl(x1, y, x2, y, c, .8)
    for x in (x1, x2):
        pl(x, y - 2.5, x, y + 2.5, c, .8)
    ptext((x1 + x2) / 2, y, t, size, c, 'middle', dy=-6)


def dim_v(x, y1, y2, t, c=INK, size=12, side='left'):
    pl(x, y1, x, y2, c, .8)
    for y in (y1, y2):
        pl(x - 2.5, y, x + 2.5, y, c, .8)
    if side == 'left':
        ptext(x, (y1 + y2) / 2, t, size, c, 'end', dx=-6, dy=4)
    else:
        ptext(x, (y1 + y2) / 2, t, size, c, 'start', dx=6, dy=4)


FRAC = {0: '', 1: '¼', 2: '½', 3: '¾'}


def ft(inches):
    """Feet and inches to the quarter, which is as fine as these stations go."""
    quarters = round(inches * 4)
    whole, q = divmod(quarters, 4)
    f, i = divmod(whole, 12)
    frac = FRAC[q]
    if i == 0 and not frac:
        return f'{f} ft'
    return f'{f} ft {i}{frac} in'


# ------------------------------------------------------------------- titleblock
text(62, 62, 'GARAGE / BEAM-SCHEME PLAN', 30)
text(62, 96, 'Alternate design — rolled beams in place of trusses', 17, INK)
text(62, 126, 'Top-down: all specified columns, the beam grid, and the existing building', 14, LABEL)
text(62, 154, 'BEAM-001  |  Rev 12  |  2026-09-18  |  Status: draft for discussion  |  '
              'Units: in / ft  |  Not to scale — use dimensions', 12, LABEL)
text(62, 188, f'Rev 12: slope rafters are one straight run over the top of R-W1 · flat rafters dead level · '
              f'four braced bays · four east lean-to rafters', 13, BEAM)

ex = G.EX
EW, EL = ex['width'], ex['length']
WESTX, EASTX, OUTX = G.WEST, G.BE_X, G.BEW_X
L = G.LOFT

# --------------------------------------------------------------- loft envelope
group('loft-over')
pbox(L['west'], L['south'], L['east'], L['north'], fill='#f0f6f4', c=None)
BAYS = [(L['south'], G.B_1A_Y), (G.B_1A_Y, G.B_2_Y), (G.B_2_Y, L['north'])]
SW = G.STAIR_WELL
for i in range(1, 18):
    x = L['west'] + (L['east'] - L['west']) * i / 18
    for y0, y1 in BAYS:
        if SW['west'] < x < SW['east'] and y0 >= SW['south'] and y1 <= SW['north']:
            continue                      # stair well: no deck, no joists
        pl(x, y0 + 2, x, y1 - 2, '#c8ded8', .7)
pbox(SW['west'], SW['south'], SW['east'], SW['north'], fill='white', c=None)
pbox(SW['west'], SW['south'], SW['east'], SW['north'], fill=None, c=AMBER, w=1.8)
for k in range(1, 9):
    yy = SW['south'] + (SW['north'] - SW['south']) * k / 9
    pl(SW['west'] + 2, yy, SW['east'] - 2, yy, AMBER, .9)
ptext((SW['west'] + SW['east']) / 2, (SW['south'] + SW['north']) / 2, 'STAIR', 11,
      AMBER, 'middle', dy=-4)
ptext((SW['west'] + SW['east']) / 2, (SW['south'] + SW['north']) / 2, 'OPEN', 11,
      AMBER, 'middle', dy=10)
pbox(L['west'], L['south'], L['east'], L['north'], fill=None, c=TEAL, w=1.6, dash=(9, 6))
end()

# ----------------------------------------------------------- existing building
group('existing-building')
for side, y0, y1 in [('south', 0, ex['wall_south']), ('north', EL - ex['wall_north'], EL)]:
    ops = sorted([o for o in ex['openings'] if o['side'] == side],
                 key=lambda o: EW - o['offset'] - o['width'])
    cursor = 0.0
    for o in ops:
        x = EW - o['offset'] - o['width']
        pbox(cursor, y0, x, y1, fill='#dfe5e8', c='#a8b1b6', w=.8)
        mid = (y0 + y1) / 2
        if o['type'] == 'window':
            pl(x, mid, x + o['width'], mid, '#a8b1b6', .9)
            ptext(x + o['width'] / 2, y0, 'WINDOW', 10, LABEL, 'middle', dy=(18 if side == 'south' else -9))
        elif o['type'] == 'garage':
            pl(x, mid, x + o['width'], mid, '#a8b1b6', .9)
            ptext(x + o['width'] / 2, y1, 'EXISTING GARAGE DOOR', 12, LABEL, 'middle', dy=-13)
        else:
            pl(x, y0, x, y0 - o['width'], '#a8b1b6', .9)
            ptext(x + o['width'] / 2, y0, 'ENTRY', 10, LABEL, 'middle', dy=32)
        cursor = x + o['width']
    pbox(cursor, y0, EW, y1, fill='#dfe5e8', c='#a8b1b6', w=.8)
pbox(EW - ex['wall_east'], ex['wall_south'], EW, EL - ex['wall_north'],
     fill='#dfe5e8', c='#a8b1b6', w=.8)
cursor = ex['wall_south']
for o in sorted([o for o in ex['openings'] if o['side'] == 'west'], key=lambda o: o['offset']):
    y = o['offset']
    pbox(0, cursor, ex['wall_west'], y, fill='#dfe5e8', c='#a8b1b6', w=.8)
    pl(ex['wall_west'] / 2, y, ex['wall_west'] / 2, y + o['width'], '#a8b1b6', .9)
    ptext(ex['wall_west'], y + o['width'] / 2, 'WINDOW', 10, LABEL, 'start', dx=7, dy=4)
    cursor = y + o['width']
pbox(0, cursor, ex['wall_west'], EL - ex['wall_north'], fill='#dfe5e8', c='#a8b1b6', w=.8)
pbox(0, 0, EW, EL, fill=None, c='#7d878d', w=1.8)
ptext(EW / 2, 34, 'EXISTING GARAGE', 15, '#6f7b82', 'middle')
ptext(EW / 2, 34, f'{ft(EW)} × {ft(EL)} outside', 12, '#8d979d', 'middle', dy=18)
pl(0, G.NEW_NORTH_FACE, EW, G.NEW_NORTH_FACE, '#8d979d', 1.4, dash=(7, 5))
pl(0, EL, 0, G.NEW_NORTH_FACE, '#8d979d', 1.4, dash=(7, 5))
pl(EW, EL, EW, G.NEW_NORTH_FACE, '#8d979d', 1.4, dash=(7, 5))
ptext(52, G.NEW_NORTH_FACE, 'NORTH WALL MOVED NORTH 22 IN', 11, '#7d878d', 'start', dy=-8)
ptext(L['west'] + 44, 210, 'LOFT FLOOR OVER', 14, TEAL)
ptext(L['west'] + 44, 210, f"{ft(L['north'] - L['south'])} north–south · joists N–S", 11, TEAL, dy=16)
end()


# ------------------------------------------------------- south storage shelf
group('south-storage-shelf')
for name, x1, x2, note in G.SHELF_PANELS:
    pbox(x1, G.SHELF_SOUTH, x2, G.SHELF_NORTH, fill='#f0f6f4', c=None)
    n = max(1, int((x2 - x1) / 16))
    for i in range(1, n):
        x = x1 + (x2 - x1) * i / n
        pl(x, G.SHELF_SOUTH + 2, x, G.SHELF_NORTH - 2, '#c8ded8', .7)
    pbox(x1, G.SHELF_SOUTH, x2, G.SHELF_NORTH, fill=None, c=TEAL, w=1.6, dash=(9, 6))
    lx = (x1 + x2) / 2
    ptext(lx, G.SHELF_SOUTH + 20, name, 12, TEAL, 'middle', weight=True)
for x1, x2 in G.SHELF_GAPS:
    ptext((x1 + x2) / 2, G.SHELF_SOUTH + 30, 'OPEN', 10, '#9aa2a8', 'middle')
    ptext((x1 + x2) / 2, G.SHELF_SOUTH + 30, '3 ft', 10, '#9aa2a8', 'middle', dy=14)
end()

ptext(56, G.SHELF_NORTH, 'SOUTH STORAGE SHELF — framed through, cabinets on it',
      11, TEAL, 'start', dy=-9)

RAFT = '#9aa7b0'
group('rafters-above')
for rx in G.rafter_x():
    pl(rx, G.B_SO_Y, rx, G.B_N_Y, RAFT, .9, dash=(6, 5))
ptext(G.rafter_x()[0], G.B_SO_Y, f'rafters @ {(G.BE_X - G.WEST) / G.CT_PANELS:.1f} in o.c.',
      10, RAFT, 'start', dx=6, dy=14)
for mid, a, b, note in G.EAST_RAFTERS:
    pl(a[0], a[1], b[0], b[1], RAFT, 1.6)
    ptext(a[0], a[1], mid, 10, RAFT, 'start', dx=10, dy=4, weight=True)
end()

CLER = '#c98b3a'
BRACE = '#8a9a5b'
group('clerestory-truss-above')
pl(WESTX, G.CLERESTORY_Y, EASTX, G.CLERESTORY_Y, '#f0dcb8', 9.0)
pl(WESTX, G.CLERESTORY_Y, EASTX, G.CLERESTORY_Y, CLER, 1.4)
for mx in G.ct_mullion_x():
    pl(mx, G.CLERESTORY_Y - 4, mx, G.CLERESTORY_Y + 4, CLER, 1.2)
ptext(EASTX, G.CLERESTORY_Y, 'CT — clerestory truss', 12, CLER, 'end', dx=-16, dy=-11,
      weight=True)
end()

group('cross-braced-bays')
for bid, axis, fixed, a0, a1, z0, z1, note in G.CROSS_BRACED_BAYS:
    if axis == 'y':
        pl(a0, fixed, a1, fixed, BRACE, 6.0)
        for t in (0.25, 0.75):
            xm = a0 + (a1 - a0) * t
            pl(xm - 5, fixed - 4, xm + 5, fixed + 4, BRACE, 1.0)
            pl(xm - 5, fixed + 4, xm + 5, fixed - 4, BRACE, 1.0)
        ptext((a0 + a1) / 2, fixed, bid, 11, BRACE, 'middle', dy=20, weight=True)
    else:
        pl(fixed, a0, fixed, a1, BRACE, 6.0)
        for t in (0.25, 0.75):
            ym = a0 + (a1 - a0) * t
            pl(fixed - 4, ym - 5, fixed + 4, ym + 5, BRACE, 1.0)
            pl(fixed - 4, ym + 5, fixed + 4, ym - 5, BRACE, 1.0)
        ptext(fixed, (a0 + a1) / 2, bid, 11, BRACE, 'end', dx=-8, dy=4, weight=True)
end()

ROOF = '#6b5b95'
group('roof-beams-above')
for mid, y, z, note in G.ROOF_BEAMS:
    pl(WESTX, y, EASTX, y, '#cfc7e0', 8.0)
    pl(WESTX, y, EASTX, y, ROOF, 1.2, dash=(14, 8))
    ptext(EASTX, y, mid, 12, ROOF, 'end', dx=-16, dy=-11, weight=True)
end()

# ------------------------------------------------------------------ beam grid
# Two families: beams of the new frame, and beams bearing on the existing walls.
# The second family sits roughly 15 in lower, at the existing wall plate.
group('beam-grid-east-west')
for name, y, x1, x2, on_wall, note in G.CROSS_BEAMS:
    c = PLUM if on_wall else BEAM
    pl(x1, y, x2, y, c, 3.6)
    ptext(x1 + 16, y, name, 14, c, 'start', dy=-8, weight=True)
end()

group('beam-grid-north-south')
for name, x, y1, y2, on_wall, note in G.LINE_BEAMS:
    c = PLUM if on_wall else BEAM
    pl(x, y1, x, y2, c, 3.6 if not on_wall else 3.0)
    if name.startswith('BWI'):
        frac = {'BWI-1': .55, 'BWI-2': .30, 'BWI-3': .55}[name]
        ptext(x, y1 + (y2 - y1) * frac, name, 12, c, 'start', dx=8, dy=4, weight=True)
    else:
        ptext(x, y2, name, 14, c, 'middle', dy=-36, weight=True)
end()

# --------------------------------------------------------------------- columns
group('columns')
for cid, x, y, size, kind in G.COLUMNS:
    h = size / 2
    if kind == 'wall-option':
        pbox(x - h, y - h, x + h, y + h, fill='#f4e6ec', c=PLUM, w=1.4, dash=(4, 3))
    elif kind == 'wall':
        pbox(x - h, y - h, x + h, y + h, fill=PLUM, c=PLUM, w=1.2)
    else:
        pbox(x - h, y - h, x + h, y + h, fill=COL, c=COL, w=1.2)
end()

group('column-labels')
PLACE = {
    'SW0': (-12, 5), 'W1': (-12, 5), 'W2': (-12, 5), 'W3': (-12, 5), 'W4': (-12, 5),
    'S1': (0, 26), 'S2': (4, 26), 'S3': (-8, 24),
    'N1': (0, -16), 'N-M': (0, -16), 'N2': (6, -16),
    'E-S': (16, 20), 'E-N': (16, 20), 'E-M/B': (16, 5), 'E-M1/B': (16, 5),
}
NEW_IN_REV1 = {'W2', 'E-M1/B'}
for cid, x, y, size, kind in G.COLUMNS:
    dx, dy = PLACE[cid]
    anchor = 'end' if dx < 0 else ('middle' if dx == 0 else 'start')
    c = PLUM if kind.startswith('wall') else COL
    ptext(x, y, cid, 14, c, anchor, dx=dx, dy=dy, weight=True)
    if cid in NEW_IN_REV1:
        ptext(x, y, 'NEW', 9, BEAM, anchor, dx=dx, dy=dy + 13, weight=True)
end()

group('b1-window-note')
# Leader from the clear text block up to the window edge B-1 was set from.
pl(30, 58, 30, G.SOUTH_WINDOW[0], BEAM, .8)
pl(30, G.SOUTH_WINDOW[0], 9, G.SOUTH_WINDOW[0], BEAM, .8)
ptext(36, 58, f"south window south edge y = {G.SOUTH_WINDOW[0]:g}", 10, BEAM, dy=-2)
ptext(36, 58, f"B-1 north face flush with it \u2014 {G.B_1_W:g} in beam, center y = {G.B_1_Y:g}",
      10, BEAM, dy=12)
end()

# ------------------------------------------------------------------ dimensions
group('dimensions')
STATIONS = [G.B_SO_Y, G.B_S_Y, G.B_1_Y, G.B_1A_Y, G.B_2_Y, G.B_N_Y]
for y1, y2 in zip(STATIONS, STATIONS[1:]):
    dim_v(WESTX - 24, y1, y2, ft(y2 - y1), BLUE)
dim_v(WESTX - 80, G.B_S_Y, G.B_2_Y, ft(G.B_2_Y - G.B_S_Y) + '  W1 → W3', TEAL)
dim_v(WESTX - 136, G.B_SO_Y, G.B_N_Y, ft(G.B_N_Y - G.B_SO_Y) + '  overall', BLUE)
dim_h(WESTX, EASTX, G.B_SO_Y - 30, f'{ft(EASTX - WESTX)}   ({EASTX - WESTX:g} in)   B-SO / B-N', BEAM)
dim_h(WESTX, OUTX, G.B_SO_Y - 58,
      f'{ft(OUTX - WESTX)}   ({OUTX - WESTX:g} in)   B-S and B-1, west row to the east wall', BEAM)
dim_h(0, EW, G.B_SO_Y - 86, f'existing {ft(EW)}', LABEL)
CHAIN = sorted([(a, b, True) for _, a, b, _ in G.SHELF_PANELS]
               + [(a, b, False) for a, b in G.SHELF_GAPS])
for a, b, is_panel in CHAIN:
    dim_h(a, b, -26, ft(b - a), TEAL if is_panel else '#9aa2a8', 11)
ptext(WESTX, -26, 'SHELF', 11, TEAL, 'end', dx=-8, dy=-6)
dim_v(OUTX + 22, G.SHELF_SOUTH, G.SHELF_NORTH, ft(G.SHELF_DEPTH) + ' deep', TEAL, side='right')
N1X = [c[1] for c in G.COLUMNS if c[0] == 'N1'][0]
dim_h(N1X, EASTX, G.B_N_Y + 52, f'{ft(EASTX - N1X)} N1–N2 centers', BLUE)
# The two numbers the owner set this revision from.
dim_v(EASTX + 48, EL, G.B_N_Y, '19 in', BEAM, side='right')
dim_v(EASTX + 88, EL, G.NEW_NORTH_FACE, '22 in', '#7d878d', side='right')
end()

# ----------------------------------------------------------- context reference
group('context')
pl(WESTX - 140, 331, OUTX + 56, 331, '#c3c9cc', 1.2, dash=(11, 8))
ptext(WESTX - 138, 331, 'PROPERTY LINE — NORTH / ALLEY', 11, '#9aa2a8', dy=-9)
pl(261.5, G.B_SO_Y - 66, 261.5, 345, '#c3c9cc', 1.2, dash=(11, 8))
ptext(261.5, -30, 'PROPERTY LINE (EAST)', 11, '#9aa2a8', dx=8, dy=4)
end()

# --------------------------------------------------------- north arrow + scale
nx, ny = 1210, 292
line(nx, ny + 64, nx, ny, INK, 1.4)
dr.polygon([(nx * SS, (ny - 11) * SS), ((nx - 7) * SS, (ny + 8) * SS), ((nx + 7) * SS, (ny + 8) * SS)], fill=INK)
svg.append(f'<polygon points="{nx},{ny-11} {nx-7},{ny+8} {nx+7},{ny+8}" fill="{INK}"/>')
text(nx, ny - 22, 'N', 17, INK, 'middle')

bx, by = 300, 1392
text(bx, by - 15, 'SCALE', 11, LABEL)
for i in range(6):
    box(bx + i * 12 * S, by, bx + (i + 1) * 12 * S, by + 9,
        fill=(INK if i % 2 == 0 else 'white'), c=INK, w=.8)
for i in range(0, 7, 2):
    text(bx + i * 12 * S, by + 26, f'{i} ft', 11, LABEL, 'middle')

# -------------------------------------------------------------- legend / notes
LX = 1330
y = 250
text(LX, y, 'WHAT IS DRAWN', 16, INK)
y += 30


def key(sym, lab, note=None):
    global y
    if sym == 'beam':
        line(LX, y - 5, LX + 34, y - 5, BEAM, 3.6)
    elif sym == 'wallbeam':
        line(LX, y - 5, LX + 34, y - 5, PLUM, 3.2)
    elif sym == 'col':
        box(LX + 11, y - 13, LX + 24, y, fill=COL, c=COL)
    elif sym == 'wallcol':
        box(LX + 11, y - 13, LX + 24, y, fill=PLUM, c=PLUM)
    elif sym == 'optcol':
        box(LX + 11, y - 13, LX + 24, y, fill='#f4e6ec', c=PLUM, w=1.2, dash=(4, 3))
    elif sym == 'loft':
        box(LX, y - 13, LX + 34, y, fill='#f0f6f4', c=TEAL, w=1.4, dash=(6, 4))
    elif sym == 'raft':
        line(LX + 4, y - 13, LX + 4, y, '#9aa7b0', .9, dash=(5, 4))
        line(LX + 14, y - 13, LX + 14, y, '#9aa7b0', .9, dash=(5, 4))
        line(LX + 24, y - 13, LX + 24, y, '#9aa7b0', .9, dash=(5, 4))
        line(LX, y - 6, LX + 34, y - 6, '#9aa7b0', 1.6)
    elif sym == 'cler':
        line(LX, y - 5, LX + 34, y - 5, '#f0dcb8', 9.0)
        line(LX, y - 5, LX + 34, y - 5, '#c98b3a', 1.4)
    elif sym == 'brace':
        line(LX, y - 5, LX + 34, y - 5, '#8a9a5b', 6.0)
        line(LX + 8, y - 9, LX + 26, y - 1, '#8a9a5b', 1.0)
        line(LX + 8, y - 1, LX + 26, y - 9, '#8a9a5b', 1.0)
    elif sym == 'roof':
        line(LX, y - 5, LX + 34, y - 5, '#cfc7e0', 8.0)
        line(LX, y - 5, LX + 34, y - 5, '#6b5b95', 1.2, dash=(10, 6))
    elif sym == 'stair':
        box(LX, y - 13, LX + 34, y, fill='white', c=AMBER, w=1.4)
        for q in range(1, 4):
            line(LX + 2, y - 13 + 13 * q / 4, LX + 32, y - 13 + 13 * q / 4, AMBER, .9)
    elif sym == 'exist':
        box(LX, y - 13, LX + 34, y, fill='#dfe5e8', c='#7d878d', w=1.4)
    text(LX + 48, y, lab, 14, INK)
    y += 19
    if note:
        text(LX + 48, y, note, 12, LABEL)
        y += 21
    else:
        y += 5


key('beam', 'Beam bearing on new columns',
    f'{G.BEAM_SECTION}, soffit on the wall-top plane z = {G.WALL_TOP_Z:g}')
key('wallbeam', 'Beam bearing on existing masonry', 'B-S, BWI-1/2/3, BEW — same plane, 5 in flange')
key('col', 'Column, new frame', 'Ten, 4 in HSS, bolted to a pier')
key('wallcol', 'Post on the existing east wall', 'E-S and E-N')
key('optcol', 'Embedded east-wall post, option B', 'E-M1/B under B-1, E-M/B under B-2')
key('loft', 'Loft floor over', 'Joists north–south, three bays')
key('loft', 'South storage shelf', 'One deck BW to BE plus SH-E; joists through, no ladder openings')
key('raft', 'Light roof framing above', f'Rafters at {(G.BE_X - G.WEST) / G.CT_PANELS:.1f} in o.c.; RE-* east lean-to')
key('cler', 'Clerestory truss above', f'{G.CT_PANELS} glazed panels, double-angle T')
key('brace', 'Cross-braced bay', 'Ground level, X in the plane of the wall')
key('roof', 'Roof beam above, east–west',
    'Directly over B-S, B-1, B-2, B-N — see the stations below')
key('stair', 'Stair opening', f'{G.stair_well_sf():.0f} sf, framed by BW / BWI-2 / B-1 / B-2')
key('exist', 'Existing garage', f'{ft(EW)} × {ft(EL)}, north wall moving north 22 in')

y += 10
text(LX, y, 'THE BEAM GRID', 16, INK)
y += 28
text(LX, y, 'EAST–WEST', 12, LABEL)
y += 22
for name, ys, x1, x2, on_wall, note in G.CROSS_BEAMS:
    text(LX, y, name, 13, PLUM if on_wall else BEAM, weight=True)
    text(LX + 58, y, f'y = {round(ys, 2):g}', 13, INK)
    text(LX + 136, y, note, 12, LABEL)
    y += 21
y += 10
text(LX, y, 'NORTH–SOUTH', 12, LABEL)
y += 22
for name, xs, y1, y2, on_wall, note in G.LINE_BEAMS:
    text(LX, y, name, 13, PLUM if on_wall else BEAM, weight=True)
    text(LX + 58, y, f'x = {round(xs, 2):g}', 13, INK)
    text(LX + 136, y, note, 12, LABEL)
    y += 21

y += 10
text(LX, y, 'ROOF BEAMS ABOVE — east–west', 12, LABEL)
y += 22
for mid, ys, zs, note in G.ROOF_BEAMS:
    text(LX, y, mid, 13, ROOF, weight=True)
    text(LX + 58, y, f'y = {ys:g}', 13, INK)
    text(LX + 136, y, f'z = {zs:.2f} · {note}', 12, LABEL)
    y += 21

y += 20
text(LX, y, 'CHECK THESE', 16, BEAM)
y += 28
NOTES = [
    ('1', 'One plane now — the 15 in split is gone.',
     ['Every beam soffit sits on the existing wall top at z = 98.5, so all',
      f'{G.BEAM_SECTION} axes are at z = {G.BEAM_AXIS_Z:g}. Shelf and loft bear on',
      'members at the same level. A 5 in flange fits every wall.']),
    ('2', 'The shelf is framed right through.',
     ['The two 3 ft ladder openings are closed. SH runs BW to BE as one',
      'deck at loft joist spacing and carries the storage cabinets; SH-E',
      'is still its own 3 ft panel over the lean-to zone, west edge on BE.']),
    ('3', 'B-1A stopping at BWI-2 is correct after all.',
     ['That strip is the stair opening, so there is nothing to support at',
      'y = 128 west of BWI-2. The well is framed on all four sides by beams',
      'already — BW, BWI-2, B-1, B-2 — so it needs no header.']),
    ('4', 'E-M1/B and E-M/B moved to the BEW axis.',
     ['The truss scheme put them 1 in off at x = 246.5, an eccentric bearing',
      f'beside a 3 in tube. With a {G.BEAM_SECTION} on the wall top the post sits',
      'the beam axis, so both are now on x = 247.5.']),
]
for num, head, body in NOTES:
    text(LX, y, num, 13, BEAM, weight=True)
    text(LX + 18, y, head, 13, INK)
    y += 19
    for ln in body:
        text(LX + 18, y, ln, 12, LABEL)
        y += 17
    y += 12

text(LX, 1392, 'Layout study only. No member sizes, connections, reactions or foundations', 11, LABEL)
text(LX, 1410, 'are established by this drawing.', 11, LABEL)

svg.append('</svg>')
(OUT / 'beam-plan.svg').write_text('\n'.join(svg))
im.resize((W, H), Image.LANCZOS).save(OUT / 'beam-plan.png')
print('wrote beam-plan.png and beam-plan.svg')
