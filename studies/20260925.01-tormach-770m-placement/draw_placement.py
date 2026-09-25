"""Tormach 770M placement in the NW pop-out (W3-W4-N1), plan and wall elevation.

Run from the repository root:
    archive/.venv/bin/python studies/20260925.01-tormach-770m-placement/draw_placement.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'src' / 'structural-analysis-v6'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import cabinets as CB
import existing as EX

# Machine and clearances (owner-supplied sizing): block 56 W x 49 D x 88 in.
# tall; back and left side may be against walls; 18 in. on the right for the
# electrical-cabinet door and console arm; 24 in. front for one operator,
# 36 in. with students.
MACHINE_W, MACHINE_D, MACHINE_H = 56.0, 49.0, 88.0
RIGHT_CLEAR, FRONT_MIN, FRONT_STUDENTS = 18.0, 24.0, 36.0
NEW_WALL_T = CB.NEW_WALL_T
COLUMN = 5.0                                   # HSS5X5 posts

W3, W4, N1, N2, EN2 = (-34.0, 185.0), (-34.0, 268.0), (40.4, 268.0), (211.5, 268.0), (247.5, 268.0)
WEST_FACE = W4[0] + NEW_WALL_T / 2             # inside face of the W3-W4 wall
NORTH_FACE = W4[1] - NEW_WALL_T / 2            # inside face of the W4-N1 wall
POP_SOUTH_FACE = W3[1] + NEW_WALL_T / 2        # north face of the W3 infill wall

# Option A: back on the north wall, left side on the west wall, facing south.
MX0, MX1 = WEST_FACE, WEST_FACE + MACHINE_W
MY0, MY1 = NORTH_FACE - MACHINE_D, NORTH_FACE


def r(a, x0, x1, y0, y1, fc, ec='#444', label=None, ls='-', alpha=1, fs=7, lw=0.8):
    a.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec, ls=ls,
                          alpha=alpha, lw=lw))
    if label:
        a.text((x0 + x1) / 2, (y0 + y1) / 2, label, ha='center', va='center', fontsize=fs)


def base_plan(ax):
    """New envelope, removed walls, posts and the current ground-floor layout."""
    T, W, L = EX.THICK, EX.W, EX.L
    old, new, slab = '#bdb8ae', '#8c9aa6', '#eef1f3'
    r(ax, W3[0], 0, W3[1], W4[1], slab, ec='none')
    r(ax, 0, EN2[0], L, EN2[1], slab, ec='none')
    # Existing walls that stay: south, east, and the west wall south of W3.
    r(ax, 0, T['west'], 0, W3[1], old)
    for a0, a1, z0, _ in EX.openings('west'):
        if a1 < W3[1]:
            r(ax, 0, T['west'], a0, a1, '#dfe9ef', ec='#8aa')
    r(ax, W - T['east'], W, 0, L, old)
    cur = T['west']
    for a0, a1, z0, _ in EX.openings('south'):
        r(ax, cur, a0, 0, T['south'], old)
        if z0 > 0:
            r(ax, a0, a1, 0, T['south'], '#dfe9ef', ec='#8aa')
        cur = a1
    r(ax, cur, W - T['east'], 0, T['south'], old)
    # Existing walls removed by the pop-outs.
    r(ax, 0, T['west'], W3[1], L, 'none', ec='#b55', ls=':')
    r(ax, T['west'], W - T['east'], L - T['north'], L, 'none', ec='#b55', ls=':')
    ax.text(120, 245, 'old north wall removed: pops out to y = 268', fontsize=6.5,
            color='#b55', ha='center')
    ax.text(-39, 176, 'old west wall removed\nbetween W3 and the north wall',
            fontsize=5.5, color='#b55', ha='left', va='top')
    # New infill walls.
    t = NEW_WALL_T / 2
    for b in [(W4[0] - t, W4[0] + t, W3[1], W4[1]), (W4[0], N1[0], W4[1] - t, W4[1] + t),
              (N2[0], EN2[0], N2[1] - t, N2[1] + t), (EN2[0] - t, EN2[0] + t, L, EN2[1]),
              (W3[0], 0, W3[1] - t, W3[1] + t)]:
        r(ax, *b, new)
    ax.plot([N1[0], N2[0]], [268, 268], color=new, lw=1.2, ls='--')
    ax.text(126, 271, 'north line N1–N2 (envelope not yet modelled)', fontsize=6,
            ha='center', color='#555')
    for n, (x, y) in dict(W3=W3, W4=W4, N1=N1, N2=N2, **{'E-N2': EN2}).items():
        r(ax, x - COLUMN / 2, x + COLUMN / 2, y - COLUMN / 2, y + COLUMN / 2, '#22262b')
        ax.text(x, y + 6 if y > 200 else y - 9, n, fontsize=7, ha='center', weight='bold')
    # Current ground-floor layout.
    tan = '#e2cf9f'
    bench = {'south': (7.5, 109.5, 6, 36.0), 'west': (7.5, 33.5, 36.0, 110.0)}
    r(ax, *bench['south'], tan, label='south bench')
    r(ax, *bench['west'], tan, label='west\nbench')
    r(ax, 7.5, 31.5, 110.625, 167.625, '#c9b08a', label='lathe')
    r(ax, 149.5, 207.5, 6, 36, '#cfdce4', label='laundry')
    for c in CB.FIRST_FLOOR_CABINETS:
        r(ax, c['x0'], c['x1'], c['y0'], c['y1'], tan, label=c['n'])
    ax.set_xlim(-45, 258); ax.set_ylim(-5, 288); ax.set_aspect('equal'); ax.grid(alpha=.25)
    ax.set_xlabel('east (in.)', fontsize=7); ax.set_ylabel('north (in.)', fontsize=7)
    ax.tick_params(labelsize=6)


def plan(ax):
    base_plan(ax)
    # Option A machine and clearances.
    r(ax, MX1, MX1 + RIGHT_CLEAR, MY0, MY1, '#fff4e0', ec='#c98', ls=':')
    ax.text(MX1 + RIGHT_CLEAR / 2, 240, '18 in.\ncabinet\ndoor +\nconsole',
            fontsize=5.5, ha='center', va='center')
    r(ax, MX0, MX1, POP_SOUTH_FACE, MY0, '#e3f2ec', ec='#2a7f62', ls=':')
    r(ax, 0, MX1, MY0 - FRONT_STUDENTS, POP_SOUTH_FACE, '#f1f8f5', ec='#2a7f62', ls=':')
    ax.text(-4, 202, f'{MY0 - POP_SOUTH_FACE:.0f} in. front clear west of x = 0;\n'
                     f'{FRONT_STUDENTS:.0f} in.+ east of it', fontsize=5.5, ha='center')
    r(ax, MX0, MX1, MY0, MY1, '#bfe3d4', ec='#1d5c46',
      label=f'Tormach 770M\n(option A)\n{MACHINE_W:g} × {MACHINE_D:g} × {MACHINE_H:g}', fs=7)
    r(ax, MX0 + 4, MX1 - 4, MY0, MY0 + 3, '#e8d9b8', ec='#998')      # enclosure doors
    r(ax, MX1 - 3, MX1, MY0 + 22, MY1 - 6, '#e8d9b8', ec='#998')     # electrical cabinet
    ax.annotate('', xy=(MX0, 277), xytext=(MX1 + RIGHT_CLEAR, 277),
                arrowprops=dict(arrowstyle='<->', lw=.7))
    ax.text((MX0 + MX1 + RIGHT_CLEAR) / 2, 279.5,
            f'{MACHINE_W + RIGHT_CLEAR:g} in. = {MACHINE_W:g} + {RIGHT_CLEAR:g}',
            fontsize=7, ha='center')
    ax.set_title('Ground floor with the NW pop-out (W3–W4–N1) and north wall at y = 268',
                 fontsize=9)


def elevation(ev):
    beam_z = 112.5
    for x in (W4[0], N1[0]):
        ev.plot([x, x], [0, beam_z], color='#22262b', lw=4)
    ev.plot([W4[0], N1[0]], [beam_z, beam_z], color='#1f5f99', lw=5)
    ev.text(3, 116, 'B-N  W12×16', fontsize=7, ha='center')
    ev.plot([W4[0], N1[0]], [0, beam_z], color='#c0392b', lw=2)
    ev.plot([W4[0], N1[0]], [beam_z, 0], color='#c0392b', lw=2)
    ev.text(W4[0], -7, 'W4', ha='center', fontsize=8, weight='bold')
    ev.text(N1[0], -7, 'N1', ha='center', fontsize=8, weight='bold')
    ev.text(22, 30, 'BR-N-1 / BR-N-2\nX-brace', fontsize=7, color='#c0392b')
    r(ev, MX0, MX1, 0, MACHINE_H, '#bfe3d4', ec='#1d5c46', alpha=.55,
      label='option A:\nmachine back\nagainst this wall', fs=7)
    r(ev, WEST_FACE, -3.5, 6, 80, 'none', ec='#8e44ad', ls='--', lw=1.3)
    ev.text(-17.5, -17, 'option B door\n(cabinet side)', fontsize=6.5, ha='center',
            color='#8e44ad')
    ev.set_xlim(-45, 52); ev.set_ylim(-25, 125); ev.set_aspect('equal'); ev.grid(alpha=.25)
    ev.set_title('North wall W4–N1, looking north from inside', fontsize=9)
    ev.tick_params(labelsize=6)


def main():
    fig, (ax, ev) = plt.subplots(1, 2, figsize=(14, 8),
                                 gridspec_kw=dict(width_ratios=[1.45, 1]))
    plan(ax)
    elevation(ev)
    for ext in ('png', 'pdf'):
        fig.savefig(HERE / f'tormach-popout.{ext}', dpi=150, bbox_inches='tight')
    print(HERE / 'tormach-popout.png')


if __name__ == '__main__':
    main()
