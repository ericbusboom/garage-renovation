"""Tormach PCNC 440 in the NW pop-out: two orientations on the new plan.

Run from the repository root:
    archive/.venv/bin/python studies/20260925.01-tormach-770m-placement/draw_440.py
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from draw_placement import (HERE, N1, COLUMN, NORTH_FACE, POP_SOUTH_FACE,
                            WEST_FACE, base_plan, r)

# Tormach space-planning figures (drawing D35684, PCNC 440 w Stand and
# Enclosure): typical footprint 42 W x 36 D x 72 in. tall, ~600 lb equipped.
# The ATC hangs off the left of the head; plan 46 in. wide to be safe.
# Console mounts on a wall, so no side clearance. Front: 24 in. one person,
# 36 in. two.
W440, D440, H440 = 46.0, 36.0, 72.0
FRONT_MIN, FRONT_TWO = 24.0, 36.0
CONSOLE_W, CONSOLE_T = 16.0, 4.0
N1_FACE = N1[0] - COLUMN / 2                   # west face of the N1 post

MACHINE, CLEAR1, CLEAR2, CONSOLE = '#bfe3d4', '#e3f2ec', '#f1f8f5', '#f3d9a4'


def option_east(ax):
    """Back on the W3-W4 wall, facing east; right side (console) north."""
    x0, x1 = WEST_FACE, WEST_FACE + D440
    y1 = NORTH_FACE
    y0 = y1 - W440
    r(ax, x1, x1 + FRONT_MIN, y0, y1, CLEAR1, ec='#2a7f62', ls=':')
    r(ax, x1 + FRONT_MIN, x1 + FRONT_TWO, y0, y1, CLEAR2, ec='#2a7f62', ls=':')
    r(ax, x0, x1, y0, y1, MACHINE, ec='#1d5c46', label='PCNC 440\n46 × 36\nfaces east', fs=6.5)
    r(ax, x0 + 6, x1 - 4, y0, y0 + 3, '#e8d9b8', ec='#998')          # ATC side (left)
    r(ax, x1 + 2, x1 + 2 + CONSOLE_W, NORTH_FACE - CONSOLE_T, NORTH_FACE,
      CONSOLE, ec='#998')
    ax.text(x1 + 10, NORTH_FACE - 9, 'console\non wall', fontsize=5, ha='center')
    ax.text(x1 + FRONT_TWO / 2, y0 + 16, f'{FRONT_TWO:g} in.\nfront', fontsize=5.5, ha='center')
    free = y0 - POP_SOUTH_FACE
    r(ax, WEST_FACE, N1_FACE, POP_SOUTH_FACE, y0, 'none', ec='#8e44ad', ls='--', lw=1)
    ax.text((WEST_FACE + N1_FACE) / 2, (POP_SOUTH_FACE + y0) / 2,
            f'free {N1_FACE - WEST_FACE:.0f} × {free:.0f} in.\n(ATC side)',
            fontsize=5.5, ha='center', va='center', color='#8e44ad')
    return dict(machine=(x0, x1, y0, y1), front_to=x1 + FRONT_TWO, free=(N1_FACE - WEST_FACE, free))


def option_south(ax):
    """Back on the W4-N1 wall, left (ATC) side on the W3-W4 wall, facing south."""
    x0, x1 = WEST_FACE, WEST_FACE + W440
    y1 = NORTH_FACE
    y0 = y1 - D440
    r(ax, x0, x1, y0 - FRONT_MIN, y0, CLEAR1, ec='#2a7f62', ls=':')
    r(ax, x0, x1, y0 - FRONT_TWO, y0 - FRONT_MIN, CLEAR2, ec='#2a7f62', ls=':')
    r(ax, x0, x1, y0, y1, MACHINE, ec='#1d5c46', label='PCNC 440\n46 × 36\nfaces south', fs=6.5)
    r(ax, x1 + 2, x1 + 2 + CONSOLE_W, NORTH_FACE - CONSOLE_T, NORTH_FACE,
      CONSOLE, ec='#998')
    ax.text(x1 + 10, NORTH_FACE - 9, 'console\non wall', fontsize=5, ha='center')
    ax.text((x0 + x1) / 2, y0 - FRONT_TWO / 2, f'{FRONT_TWO:g} in. front', fontsize=5.5, ha='center')
    left = y0 - FRONT_TWO - POP_SOUTH_FACE
    ax.text((x1 + N1_FACE) / 2, 205, f'{N1_FACE - x1:.0f} in.\nfree', fontsize=5.5,
            ha='center', color='#8e44ad')
    return dict(machine=(x0, x1, y0, y1), front_to=y0 - FRONT_TWO, spare_south=left,
                spare_east=N1_FACE - x1)


def main():
    fig, axes = plt.subplots(1, 2, figsize=(13, 7.5))
    out = {}
    for ax, fn, title in zip(axes, (option_east, option_south),
                             ('Option 1: faces east (recommended)', 'Option 2: faces south')):
        base_plan(ax)
        out[fn.__name__] = fn(ax)
        ax.set_xlim(-45, 90); ax.set_ylim(150, 285)
        for t in ax.texts:              # zoomed in: keep labels inside the panel
            t.set_clip_on(True)
        ax.set_title(f'Tormach PCNC 440 in the NW pop-out: {title}', fontsize=9)
    for ext in ('png', 'pdf'):
        fig.savefig(HERE / f'tormach-440-popout.{ext}', dpi=150, bbox_inches='tight')
    for k, v in out.items():
        print(k, {a: (tuple(round(c, 1) for c in b) if isinstance(b, tuple) else round(b, 1))
                  for a, b in v.items()})


if __name__ == '__main__':
    main()
