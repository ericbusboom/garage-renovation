"""Build dimensioned garage elevations as SVG — auto-fit version.
Projects the real FreeCAD member geometry, computes each view's bounds,
and scales/centers it to fit its viewport exactly. No overflow.
"""
import json, math
from pathlib import Path

R = Path(__file__).resolve().parent

# ── Locate data ─────────────────────────────────────────────────────────
EF = R / 'source' / 'optimization' / 'exposed-frame'
for cand in [EF,
             Path('/Volumes/Proj/Buzzkill-Proj/garage/optimization/exposed-frame'),
             Path('/Volumes/Proj/proj/CAD/garage/optimization/exposed-frame')]:
    if (cand / 'geometry.json').exists():
        EF = cand
        break

geo = json.loads((EF / 'geometry.json').read_text())
sel = json.loads((EF / 'selected.json').read_text())
cat = json.loads((EF / 'catalog.json').read_text())
members = {m['id']: m for m in geo['members']}

INCH = 25.4

# ── Build member list with section sizes ────────────────────────────────
MEMBERS = []
for mid, key in sel.items():
    m = members.get(mid)
    if not m:
        continue
    s = cat.get(key, {})
    if s.get('type') == 'HSS':
        w = d = s.get('d', 4.0)
    else:
        w, d = s.get('bf', 4.0), s.get('d', 8.0)
    MEMBERS.append({
        'id': mid,
        'a': tuple(m['a']), 'b': tuple(m['b']),
        'w': w, 'd': d,
        'role': m.get('role', ''),
        'len': m.get('length_inches', 0),
    })

# Column positions (centerline at floor)
COLUMNS = {}
for mm in MEMBERS:
    if mm['role'] == 'column':
        COLUMNS[mm['id']] = ((mm['a'][0] + mm['b'][0]) / 2,
                             (mm['a'][1] + mm['b'][1]) / 2)

# Existing garage footprint: SW at origin, 249.5 x 249.5
EXISTING = [(0, 0), (249.5, 0), (249.5, 249.5), (0, 249.5), (0, 0)]
# New frame footprint (centerline envelope), from geometry review
FRAME = [(-32, -63), (249.5, -63), (249.5, 253), (-32, 253), (-32, -63)]

# ═══════════════════════════════════════════════════════════════════════
# PROJECTIONS
# ═══════════════════════════════════════════════════════════════════════

def proj_plan(p):      # look down: (x, y)
    return (p[0], p[1])

def proj_north(p):     # look south (-Y): X→right, Z→up
    return (p[0], p[2])

def proj_west(p):      # look east (+X): North appears LEFT, Z up
    return (-p[1], p[2])

def proj_iso(p):
    """Isometric from SE, tilted. Returns (x, z_up) — y_flip handles screen-Y."""
    from math import sin, cos, radians
    x, y, z = p
    a = radians(-45)
    rx = x * cos(a) - y * sin(a)
    ry = x * sin(a) + y * cos(a)  # "forward" dim
    return (rx, ry * 0.55 + z * 0.83)   # positive = up → y_flip handles

PROJECTIONS = {
    'iso':   (proj_iso,   [m for m in MEMBERS] + [
                 {'id':'_e','a':(*c,0),'b':(*c,0)} for c in EXISTING]),
    'north': (proj_north, [m for m in MEMBERS]),
    'west':  (proj_west,  [m for m in MEMBERS]),
    'plan':  (proj_plan,  [m for m in MEMBERS]),
}

def view_bounds(member_list, proj):
    """Compute 2D bounds of projected member endpoints."""
    pts = []
    for m in member_list:
        pa = proj(m['a']); pb = proj(m['b'])
        pts += [pa, pb]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

# ═══════════════════════════════════════════════════════════════════════
# SVG BUILDER
# ═══════════════════════════════════════════════════════════════════════
class Sheet:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.el = []

    def rect(self, x, y, w, h, fill='#ffffff', stroke='#d0d0cc', sw=0.3, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.el.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
                       f'height="{h:.1f}" fill="{fill}" stroke="{stroke}" '
                       f'stroke-width="{sw}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke='#2d3a3d', sw=0.5, dash=None, cap='round'):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.el.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                       f'y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" '
                       f'stroke-linecap="{cap}"{d}/>')

    def circ(self, cx, cy, r, fill='#2d3a3d', stroke='none', sw=0.3):
        self.el.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
                       f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def poly(self, pts, stroke='#c8c5c0', sw=0.4, fill='none', dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        p = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        self.el.append(f'<polyline points="{p}" fill="{fill}" stroke="{stroke}" '
                       f'stroke-width="{sw}"{d}/>')

    def text(self, x, y, t, size=3.0, anchor='middle', fill='#333',
             weight='normal', rotate=None, family='Helvetica, Arial, sans-serif'):
        t = str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        tr = f' transform="rotate({rotate},{x:.1f},{y:.1f})"' if rotate else ''
        self.el.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
                       f'text-anchor="{anchor}" fill="{fill}" '
                       f'font-family="{family}" font-weight="{weight}"{tr}>{t}</text>')

    def dim(self, x1, y1, x2, y2, label, off=14, size=3.2):
        """Dimension line between 2 pts, offset perpendicular, with ticks+label."""
        vx, vy = x2 - x1, y2 - y1
        mag = math.hypot(vx, vy)
        if mag < 0.5:
            return
        ux, uy = vx / mag, vy / mag
        nx, ny = -uy, ux
        # extension lines
        for px, py in [(x1, y1), (x2, y2)]:
            self.line(px, py, px + nx * off * 0.55, py + ny * off * 0.55,
                      '#777', 0.25)
        # dim line
        ax, ay = x1 + nx * off, y1 + ny * off
        bx, by = x2 + nx * off, y2 + ny * off
        self.line(ax, ay, bx, by, '#444', 0.35, cap='butt')
        # ticks (45° slashes)
        tk = 3.0
        for px, py in [(ax, ay), (bx, by)]:
            self.line(px - (ux + nx) * tk, py - (uy + ny) * tk,
                      px + (ux + nx) * tk, py + (uy + ny) * tk, '#444', 0.35)
        # label
        mx, my = (ax + bx) / 2 + nx * 5.5, (ay + by) / 2 + ny * 5.5
        rot = 0
        if abs(uy) > 0.7:
            rot = -90
        self.text(mx, my + (1.0 if not rot else 0), label, size, 'middle', '#1a1a1a',
                  rotate=rot if rot else None)

    def svg(self):
        head = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{self.w}mm" height="{self.h}mm" '
                f'viewBox="0 0 {self.w} {self.h}">\n'
                f'<rect width="{self.w}" height="{self.h}" fill="#fbfbf9"/>\n')
        return head + '\n'.join(self.el) + '\n</svg>\n'


# ═══════════════════════════════════════════════════════════════════════
# SHEET + VIEWPORTS  (A0 landscape 1189 × 841)
# ═══════════════════════════════════════════════════════════════════════
PW, PH = 1189, 841
M = 26
G = 14
sh = Sheet(PW, PH)

TOP_H = 310
MID_H = 240
BOT_H = 175

COL_W = (PW - 2 * M - G) / 2

# Title block: 28mm tall, positioned below all panels
TB_H = 28
TB_Y = PH - M - TB_H  # = 787

# Bottom row Y starts so that notes panel's bottom = TB_Y - 5
BOT_Y = TB_Y - BOT_H - 3  # = 609

# Plan row Y = M + TOP_H + G
PLAN_Y = M + TOP_H + G  # = 350

VP = {
    'iso':   (M, M, COL_W, TOP_H),
    'north': (M + COL_W + G, M, COL_W, TOP_H),
    'plan':  (M, PLAN_Y, PW - 2 * M, MID_H),
    'west':  (M, BOT_Y, COL_W + 70, BOT_H),
}

def fit_transform(proj, member_list, vp, pad=0.86, y_flip=True, extra_points=None):
    """Return a function mapping model→SVG fitted to viewport.
    extra_points: model-space points that MUST be inside the view (for dims)."""
    x0, y0, w, h = vp
    mnx, mny, mxx, mxy = view_bounds(member_list, proj)
    # Include any extra reference points in the bounds
    if extra_points:
        for p in extra_points:
            u, v = proj(p)
            mnx, mny = min(mnx, u), min(mny, v)
            mxx, mxy = max(mxx, u), max(mxy, v)
    mw, mh = (mxx - mnx) or 1, (mxy - mny) or 1
    s = min(w * pad / mw, h * pad / mh)
    ox = x0 + w / 2 - (mnx + mxx) / 2 * s
    if y_flip:
        oy = y0 + h / 2 + (mny + mxy) / 2 * s
        def f(p): u, v = proj(p); return ox + u * s, oy - v * s
    else:
        oy = y0 + h / 2 - (mny + mxy) / 2 * s
        def f(p): u, v = proj(p); return ox + u * s, oy + v * s
    return f, s

# ═══ VIEW 1: ISOMETRIC ═══════════════════════════════════════════════════
vx, vy, vw, vh = VP['iso']
sh.rect(vx, vy, vw, vh)
iso_list = PROJECTIONS['iso'][1]
f_iso, s_iso = fit_transform(proj_iso, iso_list, VP['iso'], pad=0.80)

# existing garage outline (dashed)
sh.poly([f_iso((*c, 0)) for c in EXISTING], stroke='#c0bdb6', sw=0.5, dash='4,2')
# steel members
for m in MEMBERS:
    x1, y1 = f_iso(m['a'])
    x2, y2 = f_iso(m['b'])
    if m['role'] == 'column':
        col, wdt = '#25313a', max(m['w'] * s_iso * 1.1, 0.9)
    elif m['id'].startswith('BR'):
        col, wdt = '#4a6068', max(m['w'] * s_iso * 0.7, 0.6)
    else:
        col, wdt = '#354247', max(m['d'] * s_iso * 0.55, 0.5)
    sh.line(x1, y1, x2, y2, col, wdt)

# roof plane trace (eave to ridge) for readability
sh.poly([f_iso((x, y, 0)) for x, y in [(-32, -63), (249.5, -63), (249.5, 253), (-32, 253), (-32, -63)]],
        stroke='#6b7a80', sw=0.5)
sh.text(vx + vw / 2, vy + vh - 7, 'ISOMETRIC VIEW  (from SE)', 4.2, 'middle', '#444', 'bold')

# ═══ VIEW 2: NORTH ELEVATION ════════════════════════════════════════════
vx, vy, vw, vh = VP['north']
sh.rect(vx, vy, vw, vh)
f_n, s_n = fit_transform(proj_north, MEMBERS, VP['north'], pad=0.84,
                          extra_points=[(-45, 0, 0), (300, 0, 0),  # ground extent
                                        (-32, 0, 253.25), (249.5, 0, 253.25)])  # full height

for m in MEMBERS:
    x1, y1 = f_n(m['a'])
    x2, y2 = f_n(m['b'])
    if m['role'] == 'column':
        sh.line(x1, y1, x2, y2, '#25313a', max(m['w'] * s_n * 1.1, 0.9))
    else:
        sh.line(x1, y1, x2, y2, '#354247', max(m['d'] * s_n * 0.5, 0.45))

# ground line
gx1, gy = f_n((-45, 0, 0)); gx2, _ = f_n((300, 0, 0))
sh.line(gx1, gy, gx2, gy, '#8a8a86', 0.6)
# hatched ground
for i in range(int(gx1), int(gx2), 7):
    sh.line(i, gy, i - 5, gy + 5, '#c8c8c4', 0.3)

# dims: overall width (X)
ax, _ = f_n((-32, 0, 0)); bx, _ = f_n((249.5, 0, 0))
sh.dim(ax, gy + 26, bx, gy + 26, f'{(249.5 - -32):.1f}" / {((249.5 - -32)) * INCH:.0f} mm', 13)
# dims: ridge height (Z)
_, fy = f_n((0, 0, 0)); _, ry = f_n((0, 0, 253.25))
sh.dim(bx + 40, fy, bx + 40, ry, f'253.25" / {253.25 * INCH:.0f} mm', 12)
# eave height
_, ey = f_n((0, 0, 227.25))
sh.dim(bx + 12, fy, bx + 12, ey, '227.25"', 11)

sh.text(vx + vw / 2, vy + vh - 7, 'NORTH ELEVATION  (looking South)', 4.2, 'middle', '#444', 'bold')

# ═══ VIEW 3: GROUND PLAN (existing + new columns) ═══════════════════════
vx, vy, vw, vh = VP['plan']
sh.rect(vx, vy, vw, vh)

# Plan uses same model XY, fitted
plan_list = [{'a': (*c, 0), 'b': (*c, 0)} for c in EXISTING + FRAME]
f_p, s_p = fit_transform(proj_plan, [m for m in MEMBERS] + plan_list,
                         VP['plan'], pad=0.72)

# existing outline
sh.poly([f_p((x, y)) for x, y in EXISTING], stroke='#b0ada6', sw=0.7, dash='6,3', fill='#f0efec')
# new frame outline
sh.poly([f_p((x, y)) for x, y in FRAME], stroke='#25313a', sw=0.6)

# columns
for mid, (cx, cy) in sorted(COLUMNS.items()):
    px, py = f_p((cx, cy))
    sh.circ(px, py, 3.6, '#25313a')
    sh.circ(px, py, 1.3, '#ffffff')
    sh.text(px + 6.5, py + 1.2, mid, 3.1, 'start', '#222', 'bold')

# grid lines connecting columns (structural grid)
xs_sorted = sorted(set(round(c[0], 1) for c in COLUMNS.values()))
ys_sorted = sorted(set(round(c[1], 1) for c in COLUMNS.values()))
for gx in xs_sorted:
    p1 = f_p((gx, min(ys_sorted) - 12)); p2 = f_p((gx, max(ys_sorted) + 12))
    sh.line(p1[0], p1[1], p2[0], p2[1], '#c8ccd0', 0.3, dash='3,3')
for gyv in ys_sorted:
    p1 = f_p((min(xs_sorted) - 12, gyv)); p2 = f_p((max(xs_sorted) + 12, gyv))
    sh.line(p1[0], p1[1], p2[0], p2[1], '#c8ccd0', 0.3, dash='3,3')

# overall dims on plan
px1, py1 = f_p((-32, -63)); px2, py2 = f_p((249.5, -63))
sh.dim(px1, py1 + 30, px2, py2 + 30, f'281.5" / {281.5 * INCH:.0f} mm', 13)
px3, py3 = f_p((249.5, 253))
sh.dim(px2 + 34, py2, px3 + 34, py3, f'316" / {316 * INCH:.0f} mm', 13)
# existing dim
ex1, ey1 = f_p((0, 0)); ex2, ey2 = f_p((249.5, 0))
sh.dim(ex1, ey1 - 16, ex2, ey2 - 16, '249.5" existing', 11, size=2.9)

sh.text(vx + vw / 2, vy + vh - 7, 'TOP VIEW / GROUND PLAN  —  columns + existing garage outline',
        4.2, 'middle', '#444', 'bold')
# North arrow
nx_arrow = vx + vw - 30
ny_arrow = vy + 18
sh.line(nx_arrow, ny_arrow, nx_arrow, ny_arrow - 22, '#25313a', 0.8)
sh.line(nx_arrow, ny_arrow, nx_arrow - 5, ny_arrow - 14, '#25313a', 0.8)
sh.line(nx_arrow, ny_arrow, nx_arrow + 5, ny_arrow - 14, '#25313a', 0.8)
sh.text(nx_arrow, ny_arrow - 25, 'N', 4.5, 'middle', '#25313a', 'bold')

# ═══ VIEW 4: WEST ELEVATION ═════════════════════════════════════════════
vx, vy, vw, vh = VP['west']
sh.rect(vx, vy, vw, vh)
f_w, s_w = fit_transform(proj_west, MEMBERS, VP['west'], pad=0.84,
                         extra_points=[(0, -80, 0), (0, 280, 0),  # ground extent
                                       (0, 0, 253.25)])  # full height

for m in MEMBERS:
    x1, y1 = f_w(m['a'])
    x2, y2 = f_w(m['b'])
    if m['role'] == 'column':
        sh.line(x1, y1, x2, y2, '#25313a', max(m['w'] * s_w * 1.1, 0.9))
    else:
        sh.line(x1, y1, x2, y2, '#354247', max(m['d'] * s_w * 0.5, 0.45))

gx1, gy = f_w((0, -80, 0)); gx2, _ = f_w((0, 280, 0))
sh.line(gx1, gy, gx2, gy, '#8a8a86', 0.6)
for i in range(int(gx1), int(gx2), 7):
    sh.line(i, gy, i - 5, gy + 5, '#c8c8c4', 0.3)

_, fy = f_w((0, 0, 0)); _, ry = f_w((0, 0, 253.25))
sh.dim(gx2 + 30, fy, gx2 + 30, ry, f'253.25" / {253.25 * INCH:.0f} mm', 12)

sh.text(vx + vw / 2, vy + vh - 7, 'WEST ELEVATION  (looking East)', 4.2, 'middle', '#444', 'bold')

# ═══ NOTES PANEL (bottom-right) ═════════════════════════════════════════
nx = M + COL_W + 90
ny = BOT_Y
sh.rect(nx, ny, PW - M - nx, BOT_H)

notes = [
    ('KEY DIMENSIONS  [inches]', True, 3.6),
    ('Overall new frame          281.5" × 316.0"', False, 3.0),
    ('Existing garage            249.5" × 249.5"', False, 3.0),
    ('', False, 3.0),
    ('COLUMN GRID (from existing SW corner)', True, 3.2),
]
for mid, (cx, cy) in sorted(COLUMNS.items()):
    notes.append((f'   {mid:<5} X = {cx:>8.2f}"   Y = {cy:>8.2f}"', False, 3.0))
notes += [
    ('', False, 3.0),
    ('HEIGHTS', True, 3.2),
    ('Eave (north/main)         227.25"', False, 3.0),
    ('Eave (south)              235.25"', False, 3.0),
    ('Hip ridge                  253.25"', False, 3.0),
    ('Loft floor / B2 beam       120.75"', False, 3.0),
    ('Roof pitch                 30°', False, 3.0),
    ('', False, 3.0),
    ('PRIMARY STEEL — 5,290 lb, 88 members', True, 3.2),
    ('Columns        HSS4×4×3/16  to  HSS4×4×1/2', False, 3.0),
    ('B2 main beam   W8×24', False, 3.0),
    ('T1 hoist rail  W6×8.5', False, 3.0),
    ('Max utilization   0.951', False, 3.0),
    ('', False, 3.0),
    ('LIMITATIONS', True, 3.2),
    ('Connections, foundations, wind/seismic,', False, 2.9),
    ('lateral restraint, bracing details, and', False, 2.9),
    ('erection sequence are NOT designed.', False, 2.9),
    ('Preliminary owner study — engineering', False, 2.9),
    ('review required before construction.', False, 2.9),
]
for i, (line, bold, size) in enumerate(notes):
    sh.text(nx + 8, ny + 14 + i * 5.2, line, size, 'start',
            '#1a1a1a' if bold else '#3a3a3a', 'bold' if bold else 'normal',
            family='Helvetica, Arial, sans-serif' if bold else 'Menlo, Consolas, monospace')

# ═══ TITLE BLOCK ════════════════════════════════════════════════════════
tb_y = TB_Y
tb_x = M
sh.rect(tb_x, tb_y, PW - 2 * M, TB_H)
sh.line(tb_x, tb_y + 12, tb_x + PW - 2 * M, tb_y + 12, '#c0c0bc', 0.3)
sh.text(tb_x + 6, tb_y + 9, 'GARAGE RENOVATION — EXPOSED STEEL FRAME', 5.2, 'start', '#111', 'bold')
sh.text(tb_x + 6, tb_y + 22,
        'Structural Elevations & Ground Plan   ·   Units: inches (model) / mm shown   ·   '
        'SEP 2026   ·   Sheet 1 of 1', 3.0, 'start', '#555')
sh.text(tb_x + PW - 2 * M - 6, tb_y + 9,
        'PRELIMINARY — NOT FOR CONSTRUCTION', 3.4, 'end', '#8a2020', 'bold')
sh.text(tb_x + PW - 2 * M - 6, tb_y + 22,
        'Engineering review required', 2.8, 'end', '#777')

# ── Write ───────────────────────────────────────────────────────────────
out = R / 'garage-elevations.svg'
out.write_text(sh.svg())
print(f"✓ SVG: {out} ({out.stat().st_size:,} bytes)")

# Verify no overflow
import re
svg_text = out.read_text()
xs = [float(v) for v in re.findall(r'x[12]?="([\d.-]+)"', svg_text)]
ys = [float(v) for v in re.findall(r'y[12]?="([\d.-]+)"', svg_text)]
oob = sum(1 for x in xs if x < -1 or x > PW + 1) + sum(1 for y in ys if y < -1 or y > PH + 1)
print(f"  Coordinate range: X {min(xs):.0f}..{max(xs):.0f}, Y {min(ys):.0f}..{max(ys):.0f}")
print(f"  Out-of-bounds: {oob}")

try:
    import cairosvg
    cairosvg.svg2pdf(url=str(out), write_to=str(R / 'garage-elevations.pdf'))
    print(f"✓ PDF generated")
except ImportError:
    print("  (install cairosvg for direct PDF: pip install cairosvg)")
print("DONE")