#!/usr/bin/env python
"""Elevation and side-frame section of the cabinet frames built in under BE.

    python draw_cabinet_frames.py

Left: the cabinet run seen from inside the garage looking east, north to the
left as in photograph 4271. Right: one side frame in section, looking north,
with the beam on top and the proposed strengthening. Geometry from
``cabinet_frames.py``; nothing here is measured from the analysis.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

import cabinet_frames as C

HERE = Path(__file__).resolve().parent
INK = '#34434b'
STEEL = '#2c6fac'
NEW = '#e67e22'
BRACE = '#c9a227'
BEAM = '#c0392b'
WALL = '#d9d2c5'
CONC = '#b7bcc0'
WOOD = '#e8d9b5'

BEAM_D, BEAM_BF = 12.0, 3.99
DECK_Z = 104.5 + BEAM_D / 2 + 0.75        # 111.25, deck on the top flange
BEW_X = 247.5
FOOT_D, FOOT_W = 12.0, 12.0               # strip footing depth and width (concept)


def rect(ax, x, y, w, h, fc, ec=INK, lw=0.8, **kw):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, lw=lw, **kw))


def dim(ax, a, b, level, text, vertical=False, color='#326e8b', off=4):
    if vertical:
        ax.annotate('', (level, a), (level, b), arrowprops=dict(arrowstyle='|-|', color=color, lw=0.8))
        ax.text(level + off, (a + b) / 2, text, rotation=90, color=color, ha='center', va='center', fontsize=8)
    else:
        ax.annotate('', (a, level), (b, level), arrowprops=dict(arrowstyle='|-|', color=color, lw=0.8))
        ax.text((a + b) / 2, level + off, text, color=color, ha='center', va='bottom', fontsize=8)


# ---------------------------------------------------------------------------
# front elevation, looking east: y runs right-to-left so north is on the left
# ---------------------------------------------------------------------------

def elevation(ax):
    ax.invert_xaxis()
    # existing walls and floor
    rect(ax, *C.EXISTING_SOUTH_WALL[::-1], -(C.EXISTING_SOUTH_WALL[1] - C.EXISTING_SOUTH_WALL[0]), 98.5, WALL, lw=0.5)
    rect(ax, C.EXISTING_NORTH_WALL[0], 0, C.EXISTING_NORTH_WALL[1] - C.EXISTING_NORTH_WALL[0], 98.5, WALL, lw=0.5)
    ax.axhline(0, color=INK, lw=1.2)
    ax.axhline(98.5, color=INK, lw=0.5, ls=':')
    ax.text(262, 99.5, 'existing wall top 98.5', fontsize=7, color=INK, ha='left')

    # BE, the loft deck, and the columns it stands on
    rect(ax, -63, 98.5, 331, BEAM_D, '#f2c9c4', ec=BEAM, lw=1.2)
    ax.text(230, 104.5, 'BE  W12X16', color=BEAM, fontsize=9, va='center', ha='left', fontweight='bold')
    ax.plot([-63, 268], [DECK_Z, DECK_Z], color=INK, lw=2)
    ax.text(-20, DECK_Z + 2, 'loft deck', fontsize=7, color=INK)
    for name, y, top in (('S3', 3.0, 130), ('N2', 268.0, 130), ('S2', -63.0, 117)):
        rect(ax, y - 2.5, 0, 5, top, '#dfe6ec', ec=INK)
        ax.text(y, top + 3, name, ha='center', fontsize=8, color=INK)
    ax.text(3, 60, 'S3 (and S2)\nremovable with\nthe frames built in', ha='center', fontsize=6.5, color='#7f8c8d', style='italic')

    # strip footing (concept)
    rect(ax, C.RUN_SOUTH - 12, -FOOT_D, (C.RUN_NORTH + 12) - (C.RUN_SOUTH - 12), FOOT_D, CONC, lw=0.6, hatch='//')
    ax.text(C.RUN_NORTH + 14, -FOOT_D / 2, 'strip footing, 16 in. wide, under the frame line,\nslab cut out (concept; sized in cabinet-frame-study.md)',
            ha='right', va='center', fontsize=7, color=INK)

    # bays: doors and drawers, drawn light so the steel reads
    for ya, yb in zip(C.FRAME_Y, C.FRAME_Y[1:]):
        y0, y1 = ya + C.FACE / 2, yb - C.FACE / 2
        for k in range(2):
            rect(ax, y0 + k * (y1 - y0) / 2, C.UPPER_SILL_Z + 0.5, (y1 - y0) / 2, C.HEIGHT - C.UPPER_SILL_Z - 1, WOOD, lw=0.4)
        rect(ax, y0, C.BENCH_Z - 1.5, y1 - y0, 1.5, '#d4b483', lw=0.4)        # bench top
        for k in range(4):
            rect(ax, y0 + 1, 3 + k * 9, y1 - y0 - 2, 8, '#3b3b3b', ec='#222', lw=0.3)   # drawers
    # bolted rails between frames
    for z in C.RAIL_LEVELS:
        ax.plot([C.FRAME_Y[0], C.FRAME_Y[-1]], [z, z], color=STEEL, lw=1.2)
    # the frames: 1 in. face at the door line
    for name, y in zip(C.FRAME_NAMES, C.FRAME_Y):
        rect(ax, y - C.FACE / 2, 0, C.FACE, C.HEIGHT, STEEL, ec=STEEL, lw=2.5)
        ax.text(y, -3, name, ha='center', va='top', fontsize=8, color=STEEL, fontweight='bold')
        rect(ax, y - 2, 0, 4, 0.8, INK, ec=INK)                            # base plate
    ax.text(C.FRAME_Y[-1], C.HEIGHT + 14, 'CF4: cutout in top\ncorner (not drawn)', ha='center', fontsize=6.5, color=STEEL)

    # dimensions
    for ya, yb in zip(C.FRAME_Y, C.FRAME_Y[1:]):
        dim(ax, ya + 0.5, yb - 0.5, -24, '48')
    dim(ax, 0, C.FRAME_Y[0], -24, f'{C.FRAME_Y[0]:g}* from S face')
    dim(ax, 0, C.HEIGHT, 285, f'{C.HEIGHT:g}', vertical=True, off=5)
    ax.set_xlim(300, -75)
    ax.set_ylim(-34, 132)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Front elevation, looking east (north to the left) — front legs on the BE line', fontsize=10, loc='left')
    ax.text(300, -32, '* frame stations assumed from the 2026-09-18 study; measure before fabrication', fontsize=7, color='#326e8b', ha='left')


# ---------------------------------------------------------------------------
# side frame in section, looking north
# ---------------------------------------------------------------------------

def side_frame(ax):
    x0, x1 = C.FRONT_X, C.REAR_X
    # existing wall, slab, footing
    rect(ax, C.EXISTING_EAST_WALL[0], 0, 6, 98.5, WALL, lw=0.5)
    ax.text(C.EXISTING_EAST_WALL[0] + 3, 50, 'existing\neast wall', rotation=90, ha='center', va='center', fontsize=7)
    ax.axhline(0, color=INK, lw=1.2)
    rect(ax, x0 - 6, -FOOT_D, C.DEPTH + 12, FOOT_D, CONC, lw=0.6, hatch='//')
    ax.text(x0 + C.DEPTH / 2, -FOOT_D - 2, f'pad {C.DEPTH:g} x 20-26 in. per frame,\nor a 16 in. strip', ha='center', va='top', fontsize=7)

    # the beams: BE on the front leg, BEW on the wall, the SH-E deck between
    rect(ax, x0 - BEAM_BF / 2, 98.5, BEAM_BF, BEAM_D, '#f2c9c4', ec=BEAM, lw=1.2)
    ax.text(x0, 112.5, 'BE', color=BEAM, ha='center', fontsize=9, fontweight='bold')
    rect(ax, BEW_X - BEAM_BF / 2, 98.5, BEAM_BF, BEAM_D, '#f2c9c4', ec=BEAM, lw=0.8)
    ax.text(BEW_X, 112.5, 'BEW', color=BEAM, ha='center', fontsize=8)
    ax.plot([x0, BEW_X], [DECK_Z, DECK_Z], color=INK, lw=2)
    ax.text((x0 + BEW_X) / 2, DECK_Z + 2, 'SH-E deck', ha='center', fontsize=7)
    ax.plot([x0 - 12, x0], [DECK_Z, DECK_Z], color=INK, lw=2)

    # existing frame: legs 2 in. deep, top and bottom rails
    rect(ax, x0, 0, C.SIDE, C.HEIGHT, STEEL, ec=STEEL)
    rect(ax, x1 - C.SIDE, 0, C.SIDE, C.HEIGHT, STEEL, ec=STEEL)
    rect(ax, x0, C.HEIGHT - 1, C.DEPTH, 1, STEEL, ec=STEEL)
    rect(ax, x0, 0, C.DEPTH, 1, STEEL, ec=STEEL)
    # bolted rails, seen end-on
    for z in (C.BENCH_Z, C.UPPER_SILL_Z):
        for x in (x0, x1 - C.SIDE):
            rect(ax, x, z - 0.5, C.SIDE, 1, 'white', ec=STEEL, lw=0.8)
    # proposed: second tube behind the front leg, strut and N-brace
    rect(ax, x0 + C.SIDE, 0, C.SIDE, C.HEIGHT, NEW, ec=NEW)
    zm = C.HEIGHT / 2
    ax.plot([x0 + 4, x1 - 2], [zm, zm], color=BRACE, lw=3)
    ax.plot([x0 + 4, x1 - 2], [1, zm], color=BRACE, lw=3)
    ax.plot([x1 - 2, x0 + 4], [zm, C.HEIGHT - 1], color=BRACE, lw=3)
    # cap under the beam
    rect(ax, x0 - 3, C.HEIGHT - 0.5, 8, 0.5, INK, ec=INK)

    # labels
    ax.text(x0 - 3, 30, 'existing 1x2 leg (1 in. face at the door line)', rotation=90, ha='right', va='center', fontsize=6.5, color=STEEL)
    ax.annotate('second 2x1 welded behind:\n1 x 4 built-up', (x0 + 3, 75), (x0 - 14, 122), fontsize=6.5, color=NEW,
                arrowprops=dict(arrowstyle='->', color=NEW, lw=0.7), ha='left')
    ax.annotate('strut + N-brace, 2x1,\ninside the 1 in. side panel', (x0 + 15, zm), (x1 - 4, 128), fontsize=6.5, color=BRACE,
                arrowprops=dict(arrowstyle='->', color=BRACE, lw=0.7), ha='center')
    ax.text(x0 + 3, C.HEIGHT + 1.5, 'cap plate', ha='left', va='bottom', fontsize=6.5, color=INK)
    dim(ax, x0, x1, -30, f'{C.DEPTH:g}', off=-6)
    dim(ax, 0, C.HEIGHT, x1 + 8, f'{C.HEIGHT:g}', vertical=True, off=1.5)
    ax.set_xlim(x0 - 16, C.EXISTING_EAST_WALL[1] + 6)
    ax.set_ylim(-40, 138)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Side frame, looking north —\nproposed strengthening', fontsize=10, loc='left')


def main() -> None:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(17, 7.2), gridspec_kw=dict(width_ratios=[3.4, 1.15]))
    elevation(a1)
    side_frame(a2)
    fig.suptitle('Cabinet frames built in under BE — 2 x 1 x 11 ga tube, four frames, three 48 in. bays', x=0.02, ha='left', fontsize=13, y=0.98)
    handles = [plt.Line2D([], [], color=STEEL, lw=4, label='existing cabinet steel'),
               plt.Line2D([], [], color=NEW, lw=4, label='added: doubled front leg'),
               plt.Line2D([], [], color=BRACE, lw=3, label='added: bracing'),
               plt.Line2D([], [], color=BEAM, lw=3, label='beam scheme (W12X16)'),
               Rectangle((0, 0), 1, 1, facecolor=CONC, hatch='//', label='new footing (concept)')]
    fig.legend(handles=handles, loc='lower left', ncol=5, fontsize=8, frameon=False, bbox_to_anchor=(0.02, 0.0))
    fig.subplots_adjust(left=0.02, right=0.99, top=0.9, bottom=0.08, wspace=0.05)
    for ext in ('png', 'svg'):
        fig.savefig(HERE / f'cabinet-frames-elevation.{ext}', dpi=170, facecolor='white')
    print('wrote', HERE / 'cabinet-frames-elevation.png')


if __name__ == '__main__':
    main()
