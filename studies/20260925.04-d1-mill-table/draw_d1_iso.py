"""RF-30 mill/drill (D1) with its table, isometric, in its loft position.

Reads D1, its table D1-T, S3 and the walkway tiles from
src/structural-analysis-v6/cabinets.py, so the picture is the model.

Run from the repository root:
    archive/.venv/bin/python studies/20260925.04-d1-mill-table/draw_d1_iso.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'src' / 'structural-analysis-v6'))

import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

import cabinets as CB
import lean_to_rafters as MODEL

# True isometric seen from the south-west, drawn in 2-D with a painter's sort
# (matplotlib's 3-D mode layers intersecting boxes wrongly).
C30 = math.cos(math.radians(30))


def iso(x, y, z):
    """Screen point; the viewer stands south-west, so +x runs right-up, +y left-up."""
    return ((x - y) * C30, (x + y) * 0.5 + z)


def depth(pts):
    """Larger is nearer the viewer (south-west and high)."""
    return sum(-(x + y) + 0.01 * z for x, y, z in pts) / len(pts)


def box_faces(x0, x1, y0, y1, z0, z1):
    return [
        [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],    # top
        [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],    # south
        [(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)],    # west
    ]


SHADE = {0: 1.0, 1: .82, 2: .68}


def tint(hex_, k):
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return (r * k, g * k, b * k)


def main():
    frame, _, _ = MODEL.build()
    rows = {r['n']: r for r in CB.report(frame)}
    deck = rows['D1']['z0']
    box = lambda r: (r['x0'], r['x1'], r['y0'], r['y1'], r['z0'] - deck, r['top'] - deck)
    d1, t, s3 = rows['D1'], rows['D1-T'], rows['S3']
    fig, ax = plt.subplots(figsize=(12, 10))

    def poly(pts, fc, ec='#141618', lw=.8, alpha=1, z=1):
        ax.add_patch(Polygon([iso(*p) for p in pts], closed=True, fc=fc, ec=ec, lw=lw,
                             alpha=alpha, zorder=z))

    def line(a, b, **kw):
        (u0, v0), (u1, v1) = iso(*a), iso(*b)
        ax.plot([u0, u1], [v0, v1], **kw)

    def text(p, s, **kw):
        u, v = iso(*p)
        ax.text(u, v, s, **kw)

    # Deck and walkway tiles around the machine.
    x0, x1, y0, y1 = 80, 190, 90, 215
    poly([(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], CB.FLOOR, ec='none', alpha=.55, z=0)
    for tl in CB.tiles(frame):
        a0, a1 = max(tl['x0'], x0), min(tl['x1'], x1)
        b0, b1 = max(tl['y0'], y0), min(tl['y1'], y1)
        if a1 > a0 and b1 > b0:
            poly([(a0, b0, 0), (a1, b0, 0), (a1, b1, 0), (a0, b1, 0)], CB.WALK_FACE,
                 ec=CB.WALK_LINE, lw=.6, z=0)
            text(((a0 + a1) / 2, (b0 + b1) / 2, 0), tl['n'], fontsize=7, color=CB.WALK_TEXT,
                 ha='center', va='center', zorder=0)

    # Solids, all visible faces sorted together.
    faces = []
    for r, color, alpha in ((s3, CB.KINDS['shelving']['face'], .9),
                            (d1, CB.KINDS['machine']['face'], .78),
                            (t, CB.KINDS['table']['face'], 1.0)):
        for k, f in enumerate(box_faces(*box(r))):
            faces.append((depth(f), f, tint(color, SHADE[k]), alpha))
    faces.sort(key=lambda f: f[0])
    for i, (_, f, fc, a) in enumerate(faces):
        poly(f, fc, alpha=a, z=2 + i * .01)

    # Front of D1, and the table's hidden outline through the machine.
    fx0, fx1, fy = d1['x0'], d1['x1'], d1['y0']
    line((fx0, fy, 0), (fx1, fy, 0), color='#b6423c', lw=3, zorder=5)
    text(((fx0 + fx1) / 2 + 6, fy - 14, 0), 'FRONT (south)', color='#b6423c', fontsize=8,
         ha='center', weight='bold', zorder=6)
    tb = box(t)
    for a, b in (((tb[0], tb[3], tb[5]), (tb[1], tb[3], tb[5])),
                 ((tb[1], tb[2], tb[5]), (tb[1], tb[3], tb[5]))):
        line(a, b, color='#141618', lw=.6, ls=':', zorder=5)

    # Dimensions.
    tz = tb[5]
    line((tb[0], tb[2] - 8, tz), (tb[1], tb[2] - 8, tz), color='#20262b', lw=.7, zorder=6)
    text(((tb[0] + tb[1]) / 2 - 10, tb[2] - 12, tz), f'table {t["w"]:g} in. (travel)',
         fontsize=8, ha='center', va='top', zorder=6)
    line((tb[0] - 6, tb[2], tz), (tb[0] - 6, tb[3], tz), color='#20262b', lw=.7, zorder=6)
    text((tb[0] - 8, (tb[2] + tb[3]) / 2, tz), f'{t["d"]:g} deep', fontsize=7,
         ha='right', zorder=6)
    line((tb[0], tb[2], 0), (tb[0], tb[2], tb[4]), color='#20262b', lw=.7, ls='--', zorder=6)
    text((tb[0] - 2, tb[2], tb[4] / 2), f'{tb[4]:g} in.\nto underside', fontsize=7,
         ha='right', zorder=6)
    line((fx1 + 3, fy, tb[4]), (fx1 + 3, tb[2], tb[4]), color='#b6423c', lw=1, zorder=6)
    text((fx1 + 5, (fy + tb[2]) / 2, tb[4] - 3), f'{tb[2] - fy:g} in. inset', fontsize=7,
         color='#b6423c', va='top', zorder=6)
    text(((d1['x0'] + d1['x1']) / 2, (d1['y0'] + d1['y1']) / 2, d1['top'] - deck + 8),
         f'D1  RF-30\n{d1["w"]:g} W × {d1["d"]:g} D × {d1["h"]:g} H', fontsize=9,
         ha='center', weight='bold', zorder=9)
    text(((s3['x0'] + s3['x1']) / 2, (s3['y0'] + s3['y1']) / 2, s3['top'] - deck + 6),
         'S3 shelving', fontsize=9, ha='center', color='#555', zorder=9)

    ax.set_aspect('equal'); ax.autoscale_view(); ax.axis('off')
    ax.set_title(f'D1 (RF-30) with table — isometric from the south-west\n'
                 f'machine x {d1["x0"]:g}–{d1["x1"]:g}, y {d1["y0"]:g}–{d1["y1"]:g}; '
                 f'table x {t["x0"]:g}–{t["x1"]:g}, y {t["y0"]:g}–{t["y1"]:g}, '
                 f'{tb[4]:g}–{tb[5]:g} in. above the deck', fontsize=10)
    for ext in ('png', 'pdf'):
        fig.savefig(HERE / f'd1-table-iso.{ext}', dpi=150, bbox_inches='tight')
    print(HERE / 'd1-table-iso.png')


if __name__ == '__main__':
    main()
