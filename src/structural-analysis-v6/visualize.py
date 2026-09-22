"""Drawings of the result.

Two kinds.  An interactive three-dimensional model for working in, where the
colouring can be switched between utilisation, what governs, what is removable
and what can be lighter.  And flat figures for the issued report, drawn as plain
orthographic and isometric projections rather than with a 3-D engine, so line
weights and labels stay legible at print size.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

import frame as framemod

# --------------------------------------------------------------------------
# palette -- one scale reused everywhere so the figures read as one set
# --------------------------------------------------------------------------

UTIL_STOPS = [(0.00, '#3a6ea5'), (0.35, '#4c9f70'), (0.60, '#d9b310'),
              (0.85, '#e07a3f'), (1.00, '#c1292e')]

CATEGORY = {
    'enlarge':   ('#c1292e', 'Must be larger -- fails at the section as drawn'),
    'keep':      ('#5c6672', 'Keep as drawn -- working, no change verified'),
    'downsize':  ('#3a6ea5', 'Can be lighter -- a smaller section verifies'),
    'redundant': ('#4c9f70', 'Can be removed -- frame verifies without it'),
    'assumed':   ('#8a63a8', 'Added by this analysis -- assumed secondary framing'),
}

VERDICT_COLOR = {'unstable': '#c1292e', 'overloads': '#5c6672', 'redundant': '#4c9f70'}


def util_color(dcr: float) -> str:
    if dcr >= 1.0:
        return UTIL_STOPS[-1][1]
    for (lo, c0), (hi, c1) in zip(UTIL_STOPS, UTIL_STOPS[1:]):
        if lo <= dcr <= hi:
            f = (dcr - lo) / (hi - lo) if hi > lo else 0.0
            return _mix(c0, c1, f)
    return UTIL_STOPS[0][1]


def _mix(a: str, b: str, f: float) -> str:
    ca, cb = [int(a[i:i + 2], 16) for i in (1, 3, 5)], [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(int(round(ca[k] + f * (cb[k] - ca[k]))) for k in range(3))


# --------------------------------------------------------------------------
# projections
# --------------------------------------------------------------------------

def iso(p) -> tuple[float, float]:
    """Isometric: east to the right, north to the upper right, z up."""
    x, y, z = p
    c, s = math.cos(math.radians(30.0)), math.sin(math.radians(30.0))
    return ((x + y) * c, z + (y - x) * s)


PROJECTIONS = {
    'west elevation (looking east)': lambda p: (p[1], p[2]),
    'north elevation (looking south)': lambda p: (-p[0], p[2]),
    'roof plan (looking down)': lambda p: (p[0], p[1]),
    'isometric from the south-west': iso,
}


def member_polyline(frame: framemod.Frame, member: str) -> list:
    segs = framemod._ordered(frame, [(i, j) for m, i, j in frame.segments if m == member])
    if not segs:
        return []
    return [frame.xyz(segs[0][0])] + [frame.xyz(j) for _, j in segs]


# --------------------------------------------------------------------------
# static figures
# --------------------------------------------------------------------------

def _draw(ax, frame, colors, widths, project, title, annotate=None):
    segs, cs, ws = [], [], []
    for member in frame.members:
        pts = [project(p) for p in member_polyline(frame, member)]
        for a, b in zip(pts, pts[1:]):
            segs.append([a, b])
            cs.append(colors.get(member, '#d6d9dd'))
            ws.append(widths.get(member, 1.0))
    ax.add_collection(LineCollection(segs, colors=cs, linewidths=ws,
                                     capstyle='round', joinstyle='round'))
    xs = [p[0] for s in segs for p in s]
    ys = [p[1] for s in segs for p in s]
    pad = 0.05 * max(max(xs) - min(xs), max(ys) - min(ys))
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=9, loc='left', color='#33383f', pad=6)
    ax.axis('off')
    for txt, pt in (annotate or []):
        p = project(pt)
        ax.annotate(txt, p, fontsize=6.5, color='#c1292e',
                    xytext=(6, 6), textcoords='offset points')


def utilisation_sheet(frame, result, path: Path, title: str, subtitle: str = ''):
    """Four views of the frame coloured by demand-capacity ratio."""
    colors = {m.member: util_color(m.dcr) for m in result.members.values()}
    widths = {m.member: 0.9 + 2.6 * min(m.dcr, 1.2) / 1.2 for m in result.members.values()}
    hot = [(f'{m.member}  DCR {m.dcr:.2f}', _midpoint(frame, m.member))
           for m in sorted(result.members.values(), key=lambda m: -m.dcr)[:6]]

    fig, axes = plt.subplots(2, 2, figsize=(13.5, 10.5))
    for ax, (name, proj) in zip(axes.ravel(), PROJECTIONS.items()):
        _draw(ax, frame, colors, widths, proj, name,
              annotate=hot if 'isometric' in name else None)
    _util_legend(fig)
    fig.suptitle(title, fontsize=13, x=0.06, ha='left', y=0.975, color='#22262b')
    if subtitle:
        fig.text(0.06, 0.945, subtitle, fontsize=8.5, color='#5c6672')
    fig.tight_layout(rect=(0, 0.06, 1, 0.93))
    fig.savefig(path, dpi=170, facecolor='white')
    plt.close(fig)


def _util_legend(fig):
    grad = np.linspace(0, 1.2, 256).reshape(1, -1)
    cax = fig.add_axes((0.30, 0.035, 0.42, 0.016))
    cax.imshow(grad, aspect='auto', extent=(0, 1.2, 0, 1),
               cmap=matplotlib.colors.LinearSegmentedColormap.from_list(
                   'util', [util_color(v) for v in np.linspace(0, 1.2, 64)]))
    cax.set_yticks([])
    cax.set_xticks([0, 0.35, 0.6, 0.85, 1.0, 1.2])
    cax.set_xticklabels(['0', '0.35', '0.60', '0.85', '1.00', '1.20+'], fontsize=7.5)
    cax.set_xlabel('demand / capacity   (1.00 = at the code limit)', fontsize=8,
                   labelpad=3, color='#33383f')
    for s in cax.spines.values():
        s.set_visible(False)


def _midpoint(frame, member):
    pts = member_polyline(frame, member)
    return pts[len(pts) // 2] if pts else (0, 0, 0)


def opportunity_sheet(frame, categories: dict, path: Path, title: str,
                      subtitle: str = '', note: str = ''):
    """Where material can come out: one colour per action."""
    colors = {m: CATEGORY[c][0] for m, c in categories.items()}
    widths = {m: (3.2 if c in ('redundant', 'enlarge') else 1.6)
              for m, c in categories.items()}
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 10.5))
    for ax, (name, proj) in zip(axes.ravel(), PROJECTIONS.items()):
        _draw(ax, frame, colors, widths, proj, name)
    handles = [Line2D([], [], color=c, lw=3, label=f'{lab}') for c, lab in CATEGORY.values()]
    fig.legend(handles=handles, loc='lower center', ncol=2, frameon=False,
               fontsize=8.5, bbox_to_anchor=(0.5, 0.005))
    fig.suptitle(title, fontsize=13, x=0.06, ha='left', y=0.975, color='#22262b')
    if subtitle:
        fig.text(0.06, 0.945, subtitle, fontsize=8.5, color='#5c6672')
    if note:
        fig.text(0.06, 0.075, note, fontsize=7.5, color='#5c6672')
    fig.tight_layout(rect=(0, 0.10, 1, 0.93))
    fig.savefig(path, dpi=170, facecolor='white')
    plt.close(fig)


def weight_chart(frame, categories, downsize, removed, path: Path, title: str):
    """Steel weight by group: as drawn, and after the proposed reductions."""
    groups: dict[str, list[float]] = {}
    for m in frame.members:
        g = frame.group(m)
        cur = frame.member_weight(m)
        new = 0.0 if m in removed else cur * (
            downsize[m].weight / frame.section_of[m].weight if m in downsize else 1.0)
        groups.setdefault(g, [0.0, 0.0])
        groups[g][0] += cur
        groups[g][1] += new
    order = sorted(groups, key=lambda g: -groups[g][0])
    y = np.arange(len(order))
    cur = [groups[g][0] for g in order]
    new = [groups[g][1] for g in order]

    fig, ax = plt.subplots(figsize=(9.5, 0.44 * len(order) + 2.2))
    ax.barh(y + 0.19, cur, 0.36, color='#c4cad1', label='as drawn')
    ax.barh(y - 0.19, new, 0.36, color='#3a6ea5', label='after reductions')
    for k, (c, n) in enumerate(zip(cur, new)):
        if c > 0:
            ax.text(max(c, n) + max(cur) * 0.012, k,
                    f'{c:,.0f} → {n:,.0f} lb   ({(1 - n / c) * 100:.0f}% less)'
                    if n < c else f'{c:,.0f} lb', va='center', fontsize=7.6,
                    color='#5c6672')
    ax.set_yticks(y, order, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel('member weight (lb)', fontsize=9)
    ax.set_xlim(0, max(cur) * 1.55)
    ax.legend(frameon=False, fontsize=8.5, loc='lower right')
    ax.set_title(title, fontsize=12, loc='left', pad=12, color='#22262b')
    for s in ('top', 'right', 'left'):
        ax.spines[s].set_visible(False)
    ax.tick_params(left=False)
    ax.grid(axis='x', color='#eceef0', lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path, dpi=170, facecolor='white')
    plt.close(fig)


def utilisation_histogram(result, path: Path, title: str):
    vals = sorted(m.dcr for m in result.members.values())
    fig, ax = plt.subplots(figsize=(9.5, 4.0))
    bins = np.arange(0, max(1.25, min(max(vals), 5.0)) + 0.1, 0.1)
    n, edges, patches = ax.hist(np.clip(vals, 0, bins[-1]), bins=bins, edgecolor='white')
    for p, e in zip(patches, edges):
        p.set_facecolor(util_color(e + 0.05))
    ax.axvline(1.0, color='#c1292e', lw=1.2, ls='--')
    ax.text(1.0, ax.get_ylim()[1] * 0.94, '  code limit', color='#c1292e', fontsize=8)
    ax.axvline(0.35, color='#3a6ea5', lw=1.0, ls=':')
    ax.text(0.35, ax.get_ylim()[1] * 0.94, '  downsizing threshold', color='#3a6ea5',
            fontsize=8, ha='right')
    ax.set_xlabel('demand / capacity', fontsize=9)
    ax.set_ylabel('members', fontsize=9)
    ax.set_title(title, fontsize=12, loc='left', pad=12, color='#22262b')
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.grid(axis='y', color='#eceef0', lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path, dpi=170, facecolor='white')
    plt.close(fig)
