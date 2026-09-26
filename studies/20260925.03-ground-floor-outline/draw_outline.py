"""Ground-floor outline on the renovated envelope, for placing machines.

Top-down plan of the bottom floor: the kept walls of the existing garage, the
new pop-outs (north wall out to y = 268, the NW pop-out W3-W4-N1), the posts
that stand on the slab, braced wall bays, the south lean-to and the stair in
the west strip. Current equipment is ghosted so the outline reads first.

Run from the repository root:
    archive/.venv/bin/python studies/20260925.03-ground-floor-outline/draw_outline.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'src' / 'structural-analysis-v6'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

import cabinets as CB
import existing as EX
import lean_to_rafters as MODEL

INK, MUTED, OLD, NEW = '#20262b', '#727b83', '#9a948a', '#5d6f7d'
SLAB, COVERED, SHED = '#f4f1ea', '#e9ecee', '#dde2e6'
RED, GLASS, GHOST = '#b6423c', '#bfd9e6', '#6f8f86'
T_NEW = CB.NEW_WALL_T
COL = 5.0

POSTS = {'SW0': (-34, -63), 'S1': (169.5, -63), 'E-S2': (247.5, -63),
         'W3': (-34, 185), 'W4': (-34, 268), 'N1': (40.35, 268),
         'N2': (211.5, 268), 'E-N2': (247.5, 268), 'E-S3': (247.5, 2.5),
         'DOOR-W': (110.5, 2.5), 'DOOR-E': (144.5, 2.5)}


def box(ax, x0, x1, y0, y1, fc, ec='none', lw=.8, ls='-', z=1, hatch=None, alpha=1):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec, lw=lw, ls=ls,
                           zorder=z, hatch=hatch, alpha=alpha))


def dim(ax, a, b, at, horiz, text, off=0):
    if horiz:
        ax.annotate('', xy=(a, at), xytext=(b, at), arrowprops=dict(arrowstyle='<->', lw=.6, color=INK))
        ax.text((a + b) / 2, at + 1.5 + off, text, ha='center', va='bottom', fontsize=6.5)
    else:
        ax.annotate('', xy=(at, a), xytext=(at, b), arrowprops=dict(arrowstyle='<->', lw=.6, color=INK))
        ax.text(at - 1.5 + off, (a + b) / 2, text, ha='right', va='center', fontsize=6.5, rotation=90)


def main(solid=False):
    """solid=False: the outline with equipment ghosted; True: the equipment layout."""
    frame, _, _ = MODEL.build()
    W, L, T = EX.W, EX.L, EX.THICK
    wx, ny = POSTS['W4'][0], POSTS['W4'][1]          # new west and north lines
    ex = POSTS['E-N2'][0]
    fig, ax = plt.subplots(figsize=(13, 14))

    # Enclosed floor: existing slab + north strip + NW pop-out.
    ax.add_patch(Polygon([(0, 0), (W, 0), (W, L), (ex, L), (ex, ny), (wx, ny),
                          (wx, POSTS['W3'][1]), (0, POSTS['W3'][1])],
                         closed=True, fc=SLAB, ec='none', zorder=0))
    # South lean-to (y -63..0): shed enclosed east of S1, covered and open west of it.
    sx0, sx1, sy0, sy1 = CB._shed_bounds(frame)
    box(ax, wx, sx0, sy0, 0, COVERED, hatch='///', ec='#c8cdd1', lw=0)
    box(ax, sx0, sx1, sy0, sy1, SHED, ec=NEW, lw=1.6)
    ax.text((wx + sx0) / 2, -31, 'SOUTH LEAN-TO — covered, open\n(outside the garage)',
            ha='center', va='center', fontsize=8, color=MUTED)
    ax.text((sx0 + sx1) / 2, -31, 'SHED\n78 × 63', ha='center', va='center', fontsize=8,
            color=MUTED, weight='bold')
    # West strip south of W3: covered, outside the old west wall; stair climbs north.
    box(ax, wx, 0, 0, POSTS['W3'][1], COVERED, hatch='///', ec='#c8cdd1', lw=0)
    sy_top = 128.0
    box(ax, CB.WEST_FACE, CB.STAIR_EAST, 3.0, sy_top, '#ffffff', ec=INK, lw=.8, z=2)
    for y in range(12, int(sy_top), 10):
        ax.plot([CB.WEST_FACE, CB.STAIR_EAST], [y, y], color=MUTED, lw=.5, zorder=3)
    ax.annotate('', xy=((CB.WEST_FACE + CB.STAIR_EAST) / 2, sy_top - 4),
                xytext=((CB.WEST_FACE + CB.STAIR_EAST) / 2, 10),
                arrowprops=dict(arrowstyle='->', lw=1, color=INK), zorder=4)
    ax.text(-14.5, 66, 'STAIR\nup (N)', ha='center', va='center', fontsize=6.5,
            weight='bold', zorder=4, bbox=dict(fc='white', ec='none', pad=1))
    ax.text(-17, 158, 'covered\nwest strip\n(outside)', ha='center', va='center',
            fontsize=6.5, color=MUTED)

    # Kept existing walls with their openings.
    def wall_run(openings, lo, hi, draw):
        cur = lo
        for a0, a1, z0, _ in openings:
            if a1 <= lo or a0 >= hi:
                continue
            draw(cur, a0, OLD)
            draw(a0, a1, GLASS if z0 > 0 else None)
            cur = a1
        draw(cur, hi, OLD)

    def south(a, b, c):
        if c: box(ax, a, b, 0, T['south'], c, ec=INK if c == OLD else '#7fa3b6', lw=.5, z=5)
    def west(a, b, c):
        if c: box(ax, 0, T['west'], a, b, c, ec=INK if c == OLD else '#7fa3b6', lw=.5, z=5)
    wall_run(EX.openings('south'), 0, W, south)
    wall_run(EX.openings('west'), 0, POSTS['W3'][1], west)
    box(ax, W - T['east'], W, 0, L, OLD, ec=INK, lw=.5, z=5)
    gd = [o for o in EX.openings('south') if o[2] == 0][0]
    ax.text((gd[0] + gd[1]) / 2, -7, f'door {gd[1] - gd[0]:.0f} in.', ha='center',
            fontsize=6.5, weight='bold')
    # Removed walls.
    box(ax, 0, T['west'], POSTS['W3'][1], L, 'none', ec=RED, ls=':', lw=1, z=5)
    box(ax, T['west'], W - T['east'], L - T['north'], L, 'none', ec=RED, ls=':', lw=1, z=5)
    ax.text(95 if solid else 125, L - 11, 'old north wall (removed; had a 165 in. door)', fontsize=6.5,
            color=RED, ha='center')
    ax.text(9, 200, 'old west wall\nremoved', fontsize=6, color=RED, ha='left', va='center')

    # New walls.
    t = T_NEW / 2
    for b in [(wx - t, wx + t, POSTS['W3'][1], ny), (wx, POSTS['N1'][0], ny - t, ny + t),
              (POSTS['N2'][0], ex, ny - t, ny + t), (ex - t, ex + t, L, ny),
              (wx, 0, POSTS['W3'][1] - t, POSTS['W3'][1] + t)]:
        box(ax, *b, NEW, ec=INK, lw=.5, z=5)
    box(ax, POSTS['N1'][0], POSTS['N2'][0], ny - t, ny + t, 'white', ec=NEW, ls='--', lw=1, z=5)
    ax.text((POSTS['N1'][0] + POSTS['N2'][0]) / 2, ny + 5,
            'north wall N1–N2: 171 in. — doors / wall not yet decided', ha='center',
            fontsize=7, color=NEW, weight='bold')

    # Braced bays (X-braces in the wall plane): no door or window there.
    for (x0, y0), (x1, y1), name in [(POSTS['W4'], POSTS['N1'], 'X-brace'),
                                     (POSTS['S1'], POSTS['E-S2'], 'X-brace')]:
        ax.plot([x0, x1], [y0 + 3, y1 - 3] if y0 == y1 else [y0, y1], alpha=0)
        mid = ((x0 + x1) / 2, y0)
        ax.plot([x0, x1], [y0 - 1.5, y0 - 1.5], color=RED, lw=2.2, zorder=6)
        ax.text(mid[0], y0 + 9 if y0 > 0 else y0 - 7, f'{name} — keep clear of doors',
                color=RED, fontsize=6, ha='center', va='top')
    ax.plot([wx - 1.5, wx - 1.5], [POSTS['W3'][1], ny], color=RED, lw=2.2, zorder=6)
    ax.text(wx - 4, (POSTS['W3'][1] + ny) / 2, 'BR-W-2', color=RED, fontsize=6,
            rotation=90, ha='right', va='center')

    # Posts on the slab.
    for n, (x, y) in POSTS.items():
        box(ax, x - COL / 2, x + COL / 2, y - COL / 2, y + COL / 2, INK, z=8)
        dy = 7 if y > 200 else (-10 if y < -30 else 7)
        ax.text(x, y + dy, n, fontsize=7, ha='center', weight='bold', zorder=9)

    # Ghosted current equipment.
    tm = CB._tormach_bounds(frame)
    ghosts = [(tm['machine'][:4], 'Tormach 440\n(placed)', '#5f8f7e'),
              (tm['operator'], 'operator', '#bfe3d4')]
    ghosts += [((c['x0'], c['x1'], c['y0'], c['y1']), c['n'], '#d8c7a6')
               for c in CB.FIRST_FLOOR_CABINETS]
    ghosts.append((CB._laundry_bounds(frame)[:4], 'laundry', '#c6d6df'))
    for n, b in CB._bench_bounds(frame).items():
        ghosts.append((b, f'{n} bench', '#d5bd8d'))
    lathe = CB._lathe_bounds(frame)
    ghosts.append((lathe[:4], f'lathe\n{lathe[1] - lathe[0]:g} × {lathe[3] - lathe[2]:g}',
                   '#9fb0bb'))
    for u in CB._ground_items(frame):
        w, d, h = u['x1'] - u['x0'], u['y1'] - u['y0'], u['z1'] - u['z0']
        label = '' if u['part_of'] else f"{u['n'].lower()}\n{w:g} × {d:g} × {h:g}"
        ghosts.append(((u['x0'], u['x1'], u['y0'], u['y1']), label, u['color']))
    # Stacked shed items (one hung over another) share one label on the upper.
    shed = CB.shed_item_rows(frame)
    under = {}
    for o in shed:
        below = [r for r in shed if r is not o and r['top'] <= o['z0'] + 0.01 and
                 min(r['x1'], o['x1']) > max(r['x0'], o['x0']) and
                 min(r['y1'], o['y1']) > max(r['y0'], o['y0'])]
        if below:
            under[o['n']] = max(below, key=lambda r: r['top'])['n']
    lower = set(under.values())
    for r in shed:
        label = ('' if r['n'] in lower else
                 f"{r['n']}\nover {under[r['n']]}" if r['n'] in under else r['n'])
        ghosts.append(((r['x0'], r['x1'], r['y0'], r['y1']), label or ' ', '#ccd3d8'))
    for (x0, x1, y0, y1), label, color in ghosts:
        if solid:
            part = not label
            box(ax, x0, x1, y0, y1, color, ec=INK, lw=.8, ls=':' if part else '-',
                z=6 if part else 4, alpha=.35 if part else .8)
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, label, fontsize=6, color=INK,
                    ha='center', va='center', zorder=7, weight='bold', linespacing=1.1)
        else:
            box(ax, x0, x1, y0, y1, GHOST, ec=GHOST, ls='--', lw=.8, z=4, alpha=.14)
            box(ax, x0, x1, y0, y1, 'none', ec=GHOST, ls='--', lw=.8, z=4)
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, label, fontsize=5.5, color=GHOST,
                    ha='center', va='center', zorder=4)
    if solid:
        g = {u['n']: u for u in CB._ground_items(frame)}
        mid = g['WOOD']['x1']
        ax.plot([mid, mid], [-4, g['WOOD']['y1'] + 6], color=RED, lw=.7, ls='-.', zorder=8)
        ax.text(mid, -12, 'door\ncentre', color=RED, fontsize=6, ha='center', va='top')
        jamb = g['SAW']['x0']
        ax.plot([jamb, jamb], [-4, g['SAW']['y0']], color=RED, lw=.7, ls='-.', zorder=8)
        ax.text(jamb + 1, 40, 'east jamb', color=RED, fontsize=6, rotation=90, va='center')
        dim(ax, T['south'], g['WOOD']['y0'], mid - 30, False,
            f"{g['WOOD']['y0'] - T['south']:g} in.")
        tt = g['D1-T']
        ax.text(tt['x1'] + 1, tt['y1'] - 3, 'D1 table\n50 in. sweep\nat 36–40 in.',
                fontsize=5.5, va='top', zorder=8)

    # Clear dimensions of the enclosed floor.
    xi0, xi1 = T['west'], W - T['east']
    if not solid:
        dim(ax, xi0, xi1, 120, True,
            f'{xi1 - xi0:.0f} in. clear ({(xi1 - xi0) / 12:.1f} ft) — old walls')
    dim(ax, wx + t, ex - t, 283, True,
        f'{ex - wx - T_NEW:.0f} in. ({(ex - wx - T_NEW) / 12:.1f} ft) along the new north wall')
    if not solid:
        dim(ax, T['south'], ny - t, 185, False,
            f'{ny - t - T['south']:.0f} in. ({(ny - t - T['south']) / 12:.1f} ft) clear, N–S')
    dim(ax, POSTS['W3'][1] + t, ny - t, -44, False, f'{ny - POSTS["W3"][1] - T_NEW:.0f} in.')
    if not solid:
        dim(ax, wx + t, 0, 194, True, f'{-wx - t:.0f}')
    dim(ax, L, ny - t, 232, False, f'{ny - t - L:.0f}')

    ax.set_xlim(-58, 268); ax.set_ylim(-80, 298)
    ax.set_aspect('equal')
    ax.set_xticks(range(-36, 265, 12), minor=True); ax.set_yticks(range(-72, 290, 12), minor=True)
    ax.set_xticks(range(-48, 265, 48)); ax.set_yticks(range(-48, 290, 48))
    ax.grid(which='minor', color='#e3e6e8', lw=.4); ax.grid(which='major', color='#c9ced2', lw=.6)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=7)
    ax.set_xlabel('east (in.) — 1 ft grid', fontsize=8); ax.set_ylabel('north (in.)', fontsize=8)
    ax.annotate('N', xy=(258, 292), xytext=(258, 272), ha='center', fontsize=10, weight='bold',
                arrowprops=dict(arrowstyle='-|>', lw=1.2, color=INK))
    name = 'ground-floor-layout' if solid else 'ground-floor-outline'
    ax.set_title(('Ground floor — equipment layout (plan from above)\n'
                  'labels: E–W × N–S × height, in. · dotted = D1 table sweep'
                  if solid else
                  'Ground floor — renovated outline (plan from above)\n'
                  'grey = kept existing walls · blue-grey = new walls · red dotted = removed · '
                  'dashed green = current equipment'), fontsize=10)
    for ext in ('png', 'pdf'):
        fig.savefig(HERE / f'{name}.{ext}', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(HERE / f'{name}.png')


if __name__ == '__main__':
    main(solid=False)
    main(solid=True)
