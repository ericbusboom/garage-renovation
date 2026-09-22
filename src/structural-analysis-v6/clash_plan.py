"""Plan view of the existing roof, shaded where the new frame goes through it.

The three-dimensional model cannot really show this: the existing roof sits
between the new floor and the new roof, so the joists hide it from above and the
floor hides it from below. In plan it reads at a glance -- grey is roof that can
stay, red is roof that has to be opened, and the contours show how much headroom
there is under each part of the hip.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

import existing as EX
import frame as framemod


def draw(frame: framemod.Frame, omit: set[str], path: Path, subtitle: str = '') -> dict:
    verts, faces, colors, members, frac = EX.roof_mesh(frame, omit)
    fig, ax = plt.subplots(figsize=(9.6, 9.8))

    step = 6.0
    nx, ny = int(round(EX.W / step)), int(round(EX.L / step))
    xs = np.linspace(0, EX.W, nx + 1)
    ys = np.linspace(0, EX.L, ny + 1)
    hot = np.zeros((nx, ny), dtype=bool)
    for f, c in zip(faces[::2], colors[::2]):
        i, j = divmod(f[0], ny + 1)
        if c == EX.RED and i < nx and j < ny:
            hot[i, j] = True

    gx, gy = np.meshgrid(xs, ys, indexing='ij')
    ax.pcolormesh(gx, gy, np.where(hot, 1.0, 0.0), cmap=matplotlib.colors.ListedColormap(
        ['#dfe3e7', '#c1292e']), shading='flat', alpha=0.9, zorder=1)

    cz = EX.roof_z(gx, gy)
    cs = ax.contour(gx, gy, cz, levels=np.arange(110, EX.PEAK + 1, 10),
                    colors='#8b949c', linewidths=0.7, zorder=2)
    ax.clabel(cs, fmt='%.0f', fontsize=6.5, colors='#6b7279')

    for member in frame.members:
        if member in omit:
            continue
        for m, i, j in frame.segments:
            if m != member:
                continue
            a, b = frame.xyz(i), frame.xyz(j)
            ax.plot([a[0], b[0]], [a[1], b[1]], color='#22262b', lw=0.8,
                    alpha=0.55, zorder=3, solid_capstyle='round')

    ax.add_patch(plt.Rectangle((0, 0), EX.W, EX.L, fill=False, lw=1.6,
                               edgecolor='#22262b', zorder=4))
    ax.set_aspect('equal')
    ax.set_xlim(-45, 260)
    ax.set_ylim(-70, 280)
    ax.set_xlabel('east (in)', fontsize=9)
    ax.set_ylabel('north (in)', fontsize=9)
    ax.set_title('Existing roof: what has to be opened to build the new frame',
                 fontsize=13, loc='left', pad=26, color='#22262b')
    if subtitle:
        ax.text(0, 1.012, subtitle, transform=ax.transAxes, fontsize=8.5,
                color='#5c6672', va='bottom')
    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor='#dfe3e7', edgecolor='none',
                      label=f'roof that can stay — {100 - 100 * frac:.0f} % of the area'),
        plt.Rectangle((0, 0), 1, 1, facecolor='#c1292e', edgecolor='none',
                      label=f'roof to be opened — {100 * frac:.0f} % of the area'),
        Line2D([], [], color='#8b949c', lw=0.9, label='existing roof height (in)'),
        Line2D([], [], color='#22262b', lw=1.0, alpha=0.6, label='new frame in plan'),
    ]
    ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.075),
              ncol=2, frameon=False, fontsize=8.5)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=170, facecolor='white')
    plt.close(fig)
    return dict(disturbed_pct=round(100 * frac, 1), clashing_members=members)
