"""Top view of the frame: every member named, every station dimensioned.

Drawn from the ``Frame`` object after the owner revisions, not from the geometry
spec, so the plan and the analysis cannot drift apart -- the labels are the same
member names the schedules and the 3-D model use, and a member that moved in the
analysis has moved here.

Levels are separated by line weight and colour rather than by drawing several
plans: the floor grillage at z = 104.5 is the heaviest, the upper beams are
dashed, and the framing above is light. Anything the analysis is not carrying --
the east lean-to and the existing building -- is drawn but muted.
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

import existing as EX
import frame as framemod

INK = '#22262b'
GREY = '#aab1b7'
FLOOR = '#b4472f'        # the beam grillage
UPPER = '#8e4b6e'        # beams above the floor plane
ROOFB = '#6b5b95'        # roof beams
RAFTER = '#7f8c99'
JOIST = '#9fbdb6'
BRACE = '#8a9a5b'
CLERE = '#b17a36'
WOOD = '#b08a54'
COLUMN = '#1f2d34'

FLOOR_Z = 104.5


def _style(frame: framemod.Frame, member: str):
    """Colour, line width, dash and z-order for one member in plan."""
    g = frame.group(member)
    zs = [frame.xyz(n)[2] for m, i, j in frame.segments if m == member for n in (i, j)]
    zlo, zhi = min(zs), max(zs)
    if g == 'Columns':
        return COLUMN, 0, None, 6
    if g == 'Joists':
        if frame.material(member) == 'wood' and 'East wood' in member:
            return WOOD, 1.4, None, 3
        return JOIST, 0.7, None, 2
    if g == 'Bracing':
        return BRACE, 1.3, (0, (5, 3)), 3
    if g == 'Clerestory':
        return CLERE, 1.6, None, 4
    if g == 'Rafters':
        if frame.material(member) == 'wood':
            return WOOD, 1.6, None, 3
        return RAFTER, 1.0, None, 3
    if g == 'Roof':
        return ROOFB, 2.0, (0, (7, 3)), 4
    if g == 'Beams':
        if abs(zlo - FLOOR_Z) < 1.0 and abs(zhi - FLOOR_Z) < 1.0:
            return FLOOR, 3.0, None, 5
        return UPPER, 2.4, (0, (7, 3)), 5
    return GREY, 1.0, None, 2


def draw(frame: framemod.Frame, path: Path, title: str, subtitle: str = '',
         lean_to: dict | None = None, omit: set[str] = frozenset()) -> dict:
    fig = plt.figure(figsize=(17.5, 13.5))
    ax = fig.add_axes((0.045, 0.075, 0.60, 0.845))

    # -- the existing building ------------------------------------------
    ax.add_patch(Rectangle((0, 0), EX.W, EX.L, facecolor='#eef1f3',
                           edgecolor='#c3c9ce', lw=1.2, zorder=0))
    ax.text(EX.W / 2, EX.L - 14, 'EXISTING GARAGE', ha='center', fontsize=8.5,
            color='#8b949c', zorder=1)
    for side, (x, y, w, h) in (
            ('west', (0, 0, EX.THICK['west'], EX.L)),
            ('east', (EX.W - EX.THICK['east'], 0, EX.THICK['east'], EX.L)),
            ('south', (0, 0, EX.W, EX.THICK['south'])),
            ('north', (0, EX.L - EX.THICK['north'], EX.W, EX.THICK['north']))):
        ax.add_patch(Rectangle((x, y), w, h, facecolor='#d7dce0',
                               edgecolor='none', zorder=1))

    # -- decked area, so the openings read as openings --------------------
    for deck in frame.decks:
        x0, x1 = sorted(deck['x'])
        y0, y1 = sorted(deck['y'])
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor='#dfeae7',
                               edgecolor='none', alpha=0.85, zorder=1.5))
    _mark_openings(ax, frame)

    # -- the lean-to, drawn but analysed apart ---------------------------
    if lean_to:
        for a, b in lean_to.get('geometry', []):
            ax.plot([a[0], b[0]], [a[1], b[1]], color=WOOD, lw=1.6, zorder=3)
        if lean_to.get('ledger'):
            a, b = lean_to['ledger']
            ax.plot([a[0], b[0]], [a[1], b[1]], color=WOOD, lw=2.6, zorder=3)

    # -- members ----------------------------------------------------------
    # Several members share a station -- B-2 and R-W3 both sit on y = 185, B-S
    # under R-W1, B-N under R-W4 -- so a label at each member's midpoint puts
    # one on top of another and only the last one drawn is readable. Labels are
    # spread along the member and stepped away from the line, one step per
    # member already using that station.
    at_station: dict[tuple, int] = {}
    columns, labels = [], []
    for member in sorted(frame.members):
        if member in omit:
            continue
        colour, lw, dash, z = _style(frame, member)
        pts = [frame.xyz(n) for m, i, j in frame.segments if m == member
               for n in (i, j)]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        if frame.group(member) == 'Columns':
            columns.append((sum(xs) / len(xs), sum(ys) / len(ys), member))
            continue
        if max(xs) - min(xs) < 1.0 and max(ys) - min(ys) < 1.0:
            continue                                  # vertical, no plan extent
        ax.plot([min(xs), max(xs)] if max(xs) - min(xs) > max(ys) - min(ys)
                else [xs[0], xs[0]],
                [ys[0], ys[0]] if max(xs) - min(xs) > max(ys) - min(ys)
                else [min(ys), max(ys)],
                color=colour, lw=lw, linestyle=dash or '-', zorder=z,
                solid_capstyle='butt')
        horiz = max(xs) - min(xs) > max(ys) - min(ys)
        if frame.group(member) in ('Beams', 'Roof', 'Clerestory'):
            key = ('y', round(ys[0], 1)) if horiz else ('x', round(xs[0], 1))
            n = at_station.get(key, 0)
            at_station[key] = n + 1
            frac = (0.30, 0.66, 0.46, 0.80, 0.18)[n % 5]
            if horiz:
                lx = min(xs) + frac * (max(xs) - min(xs))
                ly = ys[0] + (7 if n % 2 == 0 else -13)
            else:
                lx = xs[0] + (8 if n % 2 == 0 else -8)
                ly = min(ys) + frac * (max(ys) - min(ys))
            labels.append((lx, ly, member, colour, horiz, n % 2 == 0,
                           lx if horiz else xs[0], ys[0] if horiz else ly))

    for x, y, name in columns:
        ax.add_patch(Rectangle((x - 3, y - 3), 6, 6, facecolor=COLUMN,
                               edgecolor='white', lw=0.8, zorder=7))
        ax.annotate(name, (x, y), fontsize=8.5, fontweight='bold', color=COLUMN,
                    xytext=(-7, 8), textcoords='offset points', ha='right',
                    zorder=8)

    for lx, ly, name, colour, horiz, above, ax_, ay_ in labels:
        # a short leader, because a label stepped clear of a crowded station is
        # otherwise ambiguous about which line it belongs to
        ax.plot([lx, ax_], [ly, ay_], color=colour, lw=0.6, alpha=0.75, zorder=8)
        ax.annotate(name, (lx, ly), fontsize=8.4, fontweight='bold', color=colour,
                    ha='center' if horiz else ('left' if above else 'right'),
                    va=('bottom' if above else 'top') if horiz else 'center',
                    zorder=9,
                    bbox=dict(boxstyle='round,pad=0.16', fc='white', ec=colour,
                              lw=0.5, alpha=0.9))

    # -- dimensions --------------------------------------------------------
    raf = sorted({round(frame.xyz(i)[0], 1) for m, i, j in frame.segments
                  if frame.group(m) == 'Rafters' and frame.material(m) == 'steel'
                  and m not in omit
                  and abs(frame.xyz(i)[0] - frame.xyz(j)[0]) < 1.0})
    if len(raf) > 1:
        gap = min(b - a for a, b in zip(raf, raf[1:]))
        ax.text(sum(raf) / len(raf), 292,
                f'slope and flat rafters at {gap:.1f} in o.c.', ha='center',
                fontsize=8, color=RAFTER, style='italic')

    xs_st = sorted({round(x, 2) for x, _, _ in columns})
    ys_st = sorted({round(y, 2) for _, y, _ in columns})
    _dim_row(ax, xs_st, y=-92, axis='x')
    _dim_row(ax, ys_st, y=-58, axis='y')
    far = EX.W - EX.THICK['east'] / 2 if lean_to else max(xs_st)
    for yy, a, b, lab in ((-118, min(xs_st), max(xs_st), 'column grid'),
                          (-134, min(xs_st), far, 'to the east wall')):
        ax.annotate('', xy=(a, yy), xytext=(b, yy),
                    arrowprops=dict(arrowstyle='<->', color=INK, lw=1.0))
        ax.text((a + b) / 2, yy - 6, f'{_ft(b - a)}   ({lab})',
                ha='center', va='top', fontsize=8.6, color=INK)

    ax.set_xlim(-95, 300)
    ax.set_ylim(-158, 305)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.annotate('N', (285, 265), fontsize=13, fontweight='bold', color=INK,
                ha='center')
    ax.annotate('', xy=(285, 288), xytext=(285, 250),
                arrowprops=dict(arrowstyle='-|>', color=INK, lw=1.6))

    fig.text(0.045, 0.962, title, fontsize=19, color=INK)
    if subtitle:
        fig.text(0.045, 0.940, subtitle, fontsize=9.5, color='#5c6672')

    _side_panel(fig, frame, omit, lean_to)
    fig.savefig(path, dpi=150, facecolor='white')
    plt.close(fig)
    return dict(x_stations=xs_st, y_stations=ys_st, columns=len(columns))


def _mark_openings(ax, frame):
    """Hatch the floor plane where no deck is declared, and name the big one.

    An opening is the absence of a deck rather than a thing in the model, so it
    has to be found by subtraction -- otherwise the stairwell is just white space
    that could as easily be a drafting slip.
    """
    from matplotlib.path import Path as MPath
    from matplotlib.patches import PathPatch
    decks = [(sorted(d['x']), sorted(d['y'])) for d in frame.decks]
    if not decks:
        return
    x0 = min(x[0] for x, _ in decks)
    x1 = max(x[1] for x, _ in decks)
    y0 = min(y[0] for _, y in decks)
    y1 = max(y[1] for _, y in decks)
    verts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    codes = [MPath.MOVETO] + [MPath.LINETO] * 3 + [MPath.CLOSEPOLY]
    for (dx, dy) in decks:                       # holes, wound the other way
        verts += [(dx[0], dy[0]), (dx[0], dy[1]), (dx[1], dy[1]),
                  (dx[1], dy[0]), (dx[0], dy[0])]
        codes += [MPath.MOVETO] + [MPath.LINETO] * 3 + [MPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MPath(verts, codes), facecolor='none',
                           edgecolor='#b4472f', hatch='///', lw=0.0,
                           alpha=0.45, zorder=1.6))
    # name the largest opening
    gaps = []
    for a, b in zip(sorted({y for _, y in decks for y in y}),
                    sorted({y for _, y in decks for y in y})[1:]):
        covered = [d for d in decks if d[1][0] <= a + 0.5 and d[1][1] >= b - 0.5]
        if not covered:
            continue
        west = min(d[0][0] for d in covered)
        if west > x0 + 0.5:
            gaps.append((west - x0, a, b, x0, west))
    if gaps:
        w, ya, yb, gx0, gx1 = max(gaps, key=lambda g: g[0] * (g[2] - g[1]))
        ax.text((gx0 + gx1) / 2, (ya + yb) / 2, 'STAIR\nOPEN', ha='center',
                va='center', fontsize=8.5, color='#b4472f', fontweight='bold',
                rotation=90, zorder=6)


def _ft(v: float) -> str:
    feet, inch = divmod(abs(v), 12.0)
    if inch < 0.05:
        return f'{feet:.0f} ft'
    return f'{feet:.0f} ft {inch:.1f} in'.replace('.0 in', ' in')


def _dim_row(ax, stations, y, axis):
    if len(stations) < 2:
        return
    for a, b in zip(stations, stations[1:]):
        if axis == 'x':
            ax.annotate('', xy=(a, y), xytext=(b, y),
                        arrowprops=dict(arrowstyle='<->', color='#6b7279', lw=0.8))
            ax.text((a + b) / 2, y - 7, _ft(b - a), ha='center', va='top',
                    fontsize=7.6, color='#5c6672')
            for s in (a, b):
                ax.plot([s, s], [y, y + 6], color='#c3c9ce', lw=0.6, zorder=1)
        else:
            ax.annotate('', xy=(y, a), xytext=(y, b),
                        arrowprops=dict(arrowstyle='<->', color='#6b7279', lw=0.8))
            ax.text(y - 6, (a + b) / 2, _ft(b - a), ha='right', va='center',
                    fontsize=7.6, color='#5c6672', rotation=90)
    if axis == 'x':
        for s in stations:
            ax.text(s, y + 10, f'{s:g}', ha='center', va='bottom', fontsize=7,
                    color='#9aa2a8')
    else:
        for s in stations:
            ax.text(y + 8, s, f'{s:g}', ha='left', va='center', fontsize=7,
                    color='#9aa2a8')


def _side_panel(fig, frame, omit, lean_to):
    x0, y = 0.665, 0.905
    col_top = y
    fig.text(x0, y, 'WHAT IS DRAWN', fontsize=11, color=INK, fontweight='bold')
    y -= 0.022
    keys = [(FLOOR, 3.0, '-', 'Floor grillage, z = 104.5'),
            (UPPER, 2.4, '--', 'Beams above the floor plane'),
            (ROOFB, 2.0, '--', 'Roof beams'),
            (RAFTER, 1.0, '-', 'Rafters, slope and flat'),
            (CLERE, 1.6, '-', 'Clerestory truss above'),
            (BRACE, 1.3, '--', 'Cross bracing'),
            (JOIST, 0.7, '-', 'Loft joists'),
            ('#dfeae7', 7.0, '-', 'Decked; hatched red where open'),
            (WOOD, 1.6, '-', 'East lean-to in wood, analysed separately')]
    for colour, lw, ls, text in keys:
        fig.lines.append(Line2D([x0, x0 + 0.022], [y + 0.004, y + 0.004],
                                color=colour, lw=lw, linestyle=ls,
                                transform=fig.transFigure))
        fig.text(x0 + 0.03, y, text, fontsize=8.6, color='#3b444b')
        y -= 0.0185
    fig.patches.append(Rectangle((x0, y - 0.002), 0.012, 0.010,
                                 facecolor=COLUMN, transform=fig.transFigure))
    fig.text(x0 + 0.03, y, 'Column, labelled', fontsize=8.6, color='#3b444b')
    y -= 0.032

    for heading, rows in _schedules(frame, omit, lean_to):
        if y - 0.019 - len(rows) * 0.0165 < 0.04 and x0 < 0.8:
            x0, y = 0.828, col_top            # start a second column
        fig.text(x0, y, heading, fontsize=10, color=INK, fontweight='bold')
        y -= 0.019
        for name, where, note in rows:
            fig.text(x0, y, name, fontsize=8.0, color=INK, fontweight='bold')
            fig.text(x0 + 0.062, y, where, fontsize=8.0, color='#5c6672')
            fig.text(x0 + 0.152, y, note, fontsize=7.4, color='#5c6672')
            y -= 0.0158
        y -= 0.012


def _schedules(frame, omit, lean_to=None):
    ew, ns, cols = [], [], []
    for member in sorted(frame.members):
        if member in omit:
            continue
        pts = [frame.xyz(n) for m, i, j in frame.segments if m == member
               for n in (i, j)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        zs = [p[2] for p in pts]
        sec = frame.section_of[member].name
        if frame.group(member) == 'Columns':
            cols.append((member, f'{xs[0]:g}, {ys[0]:g}',
                         f'{sec}, to z {max(zs):.4g}'))
        elif frame.group(member) in ('Beams', 'Roof'):
            if max(xs) - min(xs) > max(ys) - min(ys):
                ew.append((member, f'y = {ys[0]:g}',
                           f'z {min(zs):.4g} · {sec}'))
            else:
                ns.append((member, f'x = {xs[0]:g}',
                           f'z {min(zs):.4g} · {sec}'))
    # Twenty-two rafters listed one per line clip off the sheet and say nothing
    # a set does not. They are grouped by run and section instead.
    sets: dict[tuple, list] = {}
    for member in sorted(frame.members):
        if member in omit or frame.group(member) != 'Rafters':
            continue
        pts = [frame.xyz(n) for m, i, j in frame.segments if m == member
               for n in (i, j)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        zs = [p[2] for p in pts]
        key = (member.split('@')[0].strip() or member,
               frame.section_of[member].name,
               round(min(zs), 1), round(max(zs), 1))
        along = xs if max(xs) - min(xs) < max(ys) - min(ys) else ys
        sets.setdefault(key, []).append(round(sum(along) / len(along), 1))
    raf = []
    for (name, sec, zlo, zhi), stations in sets.items():
        stations.sort()
        gap = (min(b - a for a, b in zip(stations, stations[1:]))
               if len(stations) > 1 else None)
        where = (f'{len(stations)} at {gap:.1f} in o.c.' if gap
                 else f'{len(stations)} off')
        raf.append((name, where, f'z {zlo:g}-{zhi:g} · {sec}'))
    if lean_to and lean_to.get('geometry'):
        g = lean_to['geometry']
        ys = sorted(a[1] for a, _ in g)
        gap = min(b - a for a, b in zip(ys, ys[1:])) if len(ys) > 1 else 0
        raf.append(('East lean-to', f'{len(g)} at {gap:.1f} in o.c.',
                    'wood, 2x10 DF-L · separate'))
    return [('EAST-WEST BEAMS', ew), ('NORTH-SOUTH BEAMS', ns),
            ('COLUMNS', cols), ('RAFTERS', raf)]
