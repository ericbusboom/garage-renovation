"""Two-dimensional views of the W1 -> E-S span.

Two drawings, because the study has two answers to give.

``elevation`` is the section itself: one line of east-west framing, looking
north, drawn over the existing garage so the three things that set the span are
visible at once --- W1 standing outside the west wall, E-S standing on the east
wall, and the 17-1/2 in. of clear depth between the loft floor and the existing
wall plate.  Geometry comes out of the COMPAS graph built by ``span_model``, not
out of numbers restated here.

``answer`` is the sizing chart: required depth against the two live-load
readings and the two tributary readings, with the depth budget drawn across it.

Both are matplotlib renderings of COMPAS geometry, which is how the rest of this
project draws its elevations (see ``compas-study/north_frame_elevation.py``).
"""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/garage-mpl')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

OUT = Path(__file__).resolve().parent / 'output'

INK = '#264c5d'
MUTE = '#6d858d'
PALE = '#cdd4d5'
STEEL = '#355867'
ACCENT = '#d06c31'
BG = '#fbfbf8'


def _dim(ax, x0, x1, z, text, colour=MUTE, offset=0.0, fontsize=10):
    """A horizontal dimension line with arrowheads and a centred label."""
    ax.annotate('', xy=(x0, z), xytext=(x1, z),
                arrowprops=dict(arrowstyle='<->', color=colour, lw=1.0))
    ax.text((x0 + x1) / 2.0, z + 3.0 + offset, text, ha='center', va='bottom',
            fontsize=fontsize, color=colour,
            bbox=dict(fc=BG, ec='none', pad=1.2))


def _vdim(ax, x, z0, z1, text, colour=MUTE, fontsize=9, side='left'):
    ax.annotate('', xy=(x, z0), xytext=(x, z1),
                arrowprops=dict(arrowstyle='<->', color=colour, lw=1.0))
    dx = 4.0 if side == 'left' else -4.0
    ax.text(x + dx, (z0 + z1) / 2.0, text, ha=side, va='center',
            fontsize=fontsize, color=colour,
            bbox=dict(fc=BG, ec='none', pad=1.2))


def elevation(geom, graph, section, case, result, path: Path) -> Path:
    """Section through one east-west loft beam, looking north."""
    fig, ax = plt.subplots(figsize=(15.0, 8.6))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    d = section.d
    soffit = geom.soffit_z(d)

    # -- the existing garage, as context --------------------------------------
    ax.add_patch(Rectangle((geom.existing_west_x, 0.0),
                           geom.existing_east_x - geom.existing_west_x,
                           geom.existing_wall_top_z,
                           fc='#e8ecec', ec=PALE, lw=1.0, zorder=0))
    for x0, x1 in ((0.0, 6.0), (243.5, 249.5)):
        ax.add_patch(Rectangle((x0, 0.0), x1 - x0, geom.existing_wall_top_z,
                               fc=PALE, ec=MUTE, lw=0.8, zorder=1))
    ax.plot([geom.existing_west_x, geom.existing_east_x],
            [geom.existing_wall_top_z] * 2, color=MUTE, lw=1.2, zorder=2)
    ax.text(125.0, 42.0, 'E X I S T I N G   G A R A G E', ha='center', fontsize=12,
            color='#93a6ab', weight='bold', zorder=1)
    ax.plot([-70, 285], [0, 0], color='#71818a', lw=1.4, zorder=2)
    ax.text(20.0, -14, 'existing slab  z = 0', fontsize=9, color=MUTE)

    # -- columns, straight off the COMPAS graph -------------------------------
    for u, v in graph.edges():
        if graph.edge_attribute((u, v), 'role') != 'column':
            continue
        xa, _, za = graph.node_coordinates(u)
        xb, _, zb = graph.node_coordinates(v)
        w = graph.edge_attribute((u, v), 'depth')
        ax.add_patch(Rectangle((min(xa, xb) - w / 2.0, min(za, zb)), w,
                               abs(zb - za), fc=STEEL, ec='none', zorder=4))

    # -- the beam, drawn at its real depth ------------------------------------
    ax.add_patch(Rectangle((geom.west_x, soffit), geom.span_in, d,
                           fc=STEEL, ec='none', zorder=5))
    ax.text((geom.west_x + geom.east_x) / 2.0, soffit + d / 2.0,
            f'{section.name}   d = {d:.2f} in',
            ha='center', va='center', fontsize=13, color='white',
            weight='bold', zorder=6)

    # -- loft deck and joists above -------------------------------------------
    ax.add_patch(Rectangle((geom.west_x, geom.floor_z), geom.span_in, 2.5,
                           fc='#b08968', ec='none', zorder=5))
    ax.text(geom.west_x + 6.0, geom.floor_z + 7.0,
            'loft deck on 2x8 joists at 16 in. o.c., spanning N-S into the page',
            fontsize=9, color=MUTE, va='bottom')

    # -- load, as the case actually applies it --------------------------------
    top = geom.floor_z + 22.0
    for i in range(19):
        x = geom.west_x + geom.span_in * i / 18.0
        ax.add_patch(FancyArrowPatch((x, top), (x, geom.floor_z + 13.0),
                                     arrowstyle='-|>', mutation_scale=9,
                                     color=ACCENT, lw=1.0, zorder=7))
    ax.plot([geom.west_x, geom.east_x], [top] * 2, color=ACCENT, lw=1.4, zorder=7)
    ax.text((geom.west_x + geom.east_x) / 2.0, top + 5.0,
            f'{case.dead_psf:.0f} psf dead + {case.live_psf:.0f} psf live  '
            f'on {case.trib_ft:.2f} ft tributary  =  '
            f'{case.wD_plf + section.wt:.0f} + {case.wL_plf:.0f} plf',
            ha='center', fontsize=11, color=ACCENT, weight='bold')

    # -- supports --------------------------------------------------------------
    for x, label in ((geom.west_x, 'W1'), (geom.east_x, 'E-S')):
        ax.plot([x - 7, x + 7, x, x - 7], [-9, -9, 0, -9], color=INK, lw=1.4,
                zorder=6)
        ax.text(x, -26, label, ha='center', fontsize=13, weight='bold', color=INK)
    ax.text(geom.east_x, -38, 'on the existing east wall', ha='center',
            fontsize=9, color=MUTE)
    ax.text(geom.west_x, -38, f'{geom.west_overhang_in:.0f} in. outside\n'
                              'the west wall', ha='center', fontsize=9, color=MUTE)

    # -- dimensions ------------------------------------------------------------
    _dim(ax, geom.west_x, geom.east_x, 172.0,
         f'STUDY SPAN   {geom.span_in:.1f} in = {geom.span_ft:.2f} ft '
         f"({int(geom.span_ft)}' {(geom.span_ft % 1) * 12:.1f}\")",
         colour=INK, fontsize=12)
    _dim(ax, geom.west_x, geom.inner_east_x, 157.0,
         f'span in the built frame   {geom.built_span_in:.1f} in', colour=MUTE)
    ax.plot([geom.inner_east_x] * 2, [geom.floor_z, 160.0], color=MUTE,
            lw=0.8, ls=':')
    for x in (geom.west_x, geom.east_x):
        ax.plot([x] * 2, [geom.floor_z, 175.0], color=MUTE, lw=0.8, ls=':')

    _vdim(ax, geom.east_x + 16.0, geom.existing_wall_top_z, geom.floor_z,
          f'depth budget {geom.depth_budget_in:.1f} in')
    _vdim(ax, -46.0, 0.0, soffit, f'clear below\n{soffit:.1f} in '
                                  f"= {int(soffit // 12)}'-{soffit % 12:.0f}\"",
          side='right')
    ax.plot([-56, geom.east_x + 46], [geom.existing_wall_top_z] * 2,
            color=MUTE, lw=0.7, ls='--', zorder=1)
    ax.plot([-56, geom.east_x + 46], [soffit] * 2, color=ACCENT, lw=0.8,
            ls='--', zorder=3)
    ax.plot([60, 265], [geom.garage_door_head_z] * 2, color='#9aa7ac', lw=0.7,
            ls=':', zorder=1)
    ax.text(160.0, geom.garage_door_head_z + 2.5,
            f'existing garage door head  z = {geom.garage_door_head_z:.0f}',
            fontsize=8.5, color='#8a999e', ha='center')

    ax.set_aspect('equal')
    ax.set_xlim(-72, 300)
    ax.set_ylim(-46, 190)
    ax.set_xticks([-34, 0, 100, 211.5, 247.5])
    ax.set_xticklabels(['-34\nW1', '0', '100', '211.5', '247.5\nE-S'], fontsize=9)
    ax.set_yticks([0, 50, 86, 98.5, 116])
    ax.tick_params(axis='y', labelsize=9)
    ax.set_xlabel('Plan X / inches — west ← → east', labelpad=10, color=INK)
    ax.set_ylabel('Height above slab / inches', labelpad=8, color=INK)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(alpha=0.10)

    # -- result panel, in the right-hand margin --------------------------------
    who, dcr = result.governing
    panel = (f'{section.name}\n'
             f'{"":-<44}\n'
             f'weight       {section.wt:>5.0f} lb/ft\n'
             f'             {section.wt * geom.span_ft:>5.0f} lb per beam\n\n'
             f'Mu           {result.Mu_kipft:>6.1f} k-ft\n'
             f'φMn          {section.phiMn_kipft:>6.1f} k-ft   DCR '
             f'{result.dcr_flexure:.2f}\n\n'
             f'live Δ       {result.defl_live_in:>6.3f} in\n'
             f'L/360        {geom.span_in / 360.0:>6.3f} in   DCR '
             f'{result.dcr_defl_live:.2f}\n\n'
             f'total Δ      {result.defl_total_in:>6.3f} in\n'
             f'L/240        {geom.span_in / 240.0:>6.3f} in   DCR '
             f'{result.dcr_defl_total:.2f}\n\n'
             f'first mode   {result.fn_hz:>6.1f} Hz\n'
             f'{"":-<44}\n'
             f'governs      {who}\n'
             f'             at {dcr:.2f}')
    fig.text(0.795, 0.815, panel, fontsize=10, color=INK, family='monospace',
             va='top', ha='left',
             bbox=dict(boxstyle='round,pad=0.8', fc='white', ec='#b7c7cc'))

    fig.suptitle('LOFT SPAN STUDY · W1 TO E-S · ONE OF THREE EAST-WEST BEAMS',
                 x=0.045, ha='left', fontsize=18, weight='bold', color=INK)
    fig.text(0.045, 0.912, f'Section looking north  |  {case.label()}  |  '
                           'simple span, deck bracing the compression flange',
             fontsize=11, color='#4b6570')
    fig.text(0.045, 0.035,
             'Geometry from frame-spec.json via the COMPAS study model. '
             'Loads from structural-analysis-v6/loads.py. AISC 360-16 LRFD strength, '
             'IBC Table 1604.3 deflection.\n'
             'Preliminary sizing study for discussion. Not a structural verification; '
             'connection design, the columns themselves and the foundations are outside it, '
             'and it needs review and sealing by the responsible California-licensed engineer.',
             fontsize=8.5, color='#526b73')
    fig.subplots_adjust(left=0.065, right=0.775, top=0.875, bottom=0.135)

    OUT.mkdir(exist_ok=True)
    for ext in ('png', 'svg'):
        fig.savefig(path.with_suffix('.' + ext), dpi=170)
    plt.close(fig)
    return path.with_suffix('.png')


def answer(geom, rows, truss_rows, path: Path) -> Path:
    """Required depth for each reading of the load, against the depth budget."""
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(15.0, 7.2),
                                  gridspec_kw=dict(width_ratios=[1.15, 1]))
    fig.patch.set_facecolor(BG)
    for a in (ax, ax2):
        a.set_facecolor(BG)
        a.spines[['top', 'right']].set_visible(False)

    labels = [r['case'] for r in rows]
    depths = [r['d'] for r in rows]
    colours = [ACCENT if r['live_psf'] > 100 else STEEL for r in rows]
    bars = ax.barh(range(len(rows)), depths, color=colours, height=0.58)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(labels, fontsize=10.5)
    for b, r in zip(bars, rows):
        ax.text(b.get_width() + 0.35, b.get_y() + b.get_height() / 2.0,
                f"{r['section']}  ·  {r['d']:.1f} in  ·  {r['weight_lb']:.0f} lb\n"
                f"governed by {r['governing']} at {r['dcr']:.2f}",
                va='center', fontsize=9.5, color=INK)
    ax.axvline(geom.depth_budget_in, color='#8a999e', ls='--', lw=1.3)
    ax.text(geom.depth_budget_in + 0.4, -0.85,
            f'depth budget {geom.depth_budget_in:.1f} in\n'
            '(loft floor down to the existing wall plate)',
            ha='left', va='center', fontsize=9.5, color='#6a797e')
    ax.set_xlim(0, 30)
    ax.set_ylim(len(rows) - 0.35, -1.25)
    ax.set_xlabel('Required section depth / inches', labelpad=8, color=INK)
    ax.set_title('How deep does the W beam have to be?', loc='left',
                 fontsize=14, weight='bold', color=INK, pad=14)

    # -- truss alternatives ----------------------------------------------------
    for tag, marker, colour in (('L40-interior', 'o', STEEL),
                                ('L125-interior', 's', ACCENT)):
        pts = [t for t in truss_rows if t['case'] == tag]
        ax2.plot([t['depth'] for t in pts], [t['weight_lb'] for t in pts],
                 marker=marker, color=colour, lw=1.6, ms=7,
                 label=f'truss · {tag.split("-")[0][1:]} psf live')
        for t in pts:
            ax2.annotate(f"{t['n_joints']} jt", (t['depth'], t['weight_lb']),
                         textcoords='offset points', xytext=(0, 9),
                         ha='center', fontsize=8, color=colour)
    for r, colour in ((rows[1], STEEL), (rows[3], ACCENT)):
        ax2.scatter([r['d']], [r['weight_lb']], marker='*', s=260, color=colour,
                    zorder=5, edgecolor='white', linewidth=0.8)
        ax2.annotate(f"{r['section']}\n0 joints", (r['d'], r['weight_lb']),
                     textcoords='offset points', xytext=(12, -4), fontsize=9,
                     color=colour, weight='bold')
    ax2.axvline(geom.depth_budget_in, color='#8a999e', ls='--', lw=1.3)
    ax2.set_xlabel('Framing depth / inches', labelpad=8, color=INK)
    ax2.set_ylabel('Steel per beam / lb', labelpad=8, color=INK)
    ax2.set_title('Truss instead? Weight falls, joints appear', loc='left',
                  fontsize=14, weight='bold', color=INK, pad=14)
    ax2.legend(frameon=False, fontsize=10, loc='upper right')
    ax2.grid(alpha=0.12)

    fig.suptitle('LOFT SPAN STUDY · THE ANSWER AND THE ALTERNATIVE',
                 x=0.04, ha='left', fontsize=18, weight='bold', color=INK)
    fig.text(0.04, 0.905,
             f'Span {geom.span_in:.1f} in = {geom.span_ft:.2f} ft, W1 to E-S  |  '
             'three east-west beams carrying the loft floor only  |  '
             'stars are the rolled-beam answers, lines are Warren trusses',
             fontsize=11, color='#4b6570')
    fig.text(0.04, 0.032,
             'Trusses sized by plane pin-jointed direct stiffness on the project HSS ladder, '
             'including top-chord local bending between panel points.\n'
             'Joint counts are fitted tube ends, the cost driver identified in '
             'EW-TRUSS-PROCUREMENT.md. Preliminary; requires engineer review and seal.',
             fontsize=8.5, color='#526b73')
    fig.subplots_adjust(left=0.185, right=0.975, top=0.835, bottom=0.145,
                        wspace=0.42)

    OUT.mkdir(exist_ok=True)
    for ext in ('png', 'svg'):
        fig.savefig(path.with_suffix('.' + ext), dpi=170)
    plt.close(fig)
    return path.with_suffix('.png')


def tributary(geom, rows, path: Path) -> Path:
    """Plan of the loft showing what 'tributary' means, and why it has two readings.

    Tributary width is just the strip of floor whose load has nowhere to go but
    that beam --- half the bay on each side of it.  The drawing exists because
    the two readings in the sizing table are not two opinions about the same
    layout: they are two different layouts, and only one of them is buildable
    with three beams landing on the loft edges.
    """
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14.5, 7.4))
    fig.patch.set_facecolor(BG)

    sy, ny = geom.loft_south_y, geom.loft_north_y
    wx, ex = geom.west_x, geom.east_x
    bays = [sy, sy + geom.loft_depth_in / 2.0, ny]          # three beams, equal spacing
    thirds = [sy + geom.loft_depth_in * f for f in (1 / 6, 0.5, 5 / 6)]

    panels = (
        (ax, 'AS BUILT — three beams on the loft edges',
         bays, [3.81, 7.62, 3.81],
         'The centre beam has half a bay on each side: 3.81 + 3.81 = 7.62 ft.\n'
         'The edge beams have floor on one side only.'),
        (ax2, 'THE EVEN-THIRD READING — 5.08 ft each',
         thirds, [5.08, 5.08, 5.08],
         'Equal shares need the beams pulled inboard and the deck cantilevered\n'
         'past the outer two. Nobody builds this; it is the brief as stated.'),
    )

    for a, title, lines, tribs, note in panels:
        a.set_facecolor(BG)
        a.add_patch(Rectangle((wx, sy), geom.span_in, geom.loft_depth_in,
                              fc='#eef1f0', ec=PALE, lw=1.0, zorder=0))
        edges = [sy] + [(lines[i] + lines[i + 1]) / 2.0
                        for i in range(len(lines) - 1)] + [ny]
        for i, (y0, y1) in enumerate(zip(edges, edges[1:])):
            a.add_patch(Rectangle((wx, y0), geom.span_in, y1 - y0,
                                  fc=ACCENT if i == 1 else STEEL, alpha=0.16,
                                  ec='white', lw=1.4, zorder=1))
            a.annotate('', xy=(wx + 26, y0), xytext=(wx + 26, y1),
                       arrowprops=dict(arrowstyle='<->', color=MUTE, lw=1.0))
            a.text(wx + 32, (y0 + y1) / 2.0, f'{tribs[i]:.2f} ft',
                   va='center', fontsize=11, color=INK, weight='bold', zorder=6,
                   bbox=dict(fc=BG, ec='none', pad=2.0))
        for y, t in zip(lines, tribs):
            a.plot([wx, ex], [y, y], color=STEEL, lw=7, solid_capstyle='butt',
                   zorder=3)
        # joists, spanning north-south between the beams
        for x in range(int(wx) + 20, int(ex), 16):
            a.plot([x, x], [sy, ny], color='#b08968', lw=0.8, alpha=0.55, zorder=2)
        a.text((wx + ex) / 2.0, ny + 9, 'joists span N–S, 2x8 at 16 in. o.c.',
               ha='center', fontsize=9, color='#96805f')

        a.text(ex - 6, sy + 8, 'south edge\n(clerestory)', ha='right', fontsize=8.5,
               color=MUTE)
        a.text(ex - 6, ny - 8, 'north wall', ha='right', va='top', fontsize=8.5,
               color=MUTE)
        for x, lbl in ((wx, 'W1'), (ex, 'E-S')):
            a.plot([x, x], [sy - 14, ny + 14], color=MUTE, lw=0.8, ls=':')
            a.text(x, sy - 22, lbl, ha='center', fontsize=11, weight='bold',
                   color=INK)
        a.set_aspect('equal')
        a.set_xlim(wx - 30, ex + 22)
        a.set_ylim(sy - 34, ny + 34)
        a.axis('off')
        a.set_title(title, loc='left', fontsize=12.5, weight='bold', color=INK,
                    pad=30)
        a.text(wx - 26, ny + 26, note, fontsize=9.5, color='#4b6570', va='bottom')

    fig.suptitle('WHAT "TRIBUTARY" MEANS · the strip of floor each beam has to carry',
                 x=0.035, ha='left', fontsize=17, weight='bold', color=INK)
    fig.text(0.035, 0.905,
             f'Loft plan, {geom.span_ft:.2f} ft east–west by {geom.loft_depth_ft:.2f} ft '
             'north–south  |  north is up  |  orange strip is the worst-loaded beam',
             fontsize=10.5, color='#4b6570')
    fig.text(0.035, 0.035,
             'Load on a beam = tributary width x the floor load in psf. '
             'At 125 psf the centre beam picks up 7.62 x 135 = 1,029 plf, '
             'against 5.08 x 135 = 686 plf on the even-third reading — '
             '50 % more, which is W16x26 instead of W14x22.',
             fontsize=9, color='#526b73')
    fig.subplots_adjust(left=0.04, right=0.985, top=0.80, bottom=0.095, wspace=0.10)

    OUT.mkdir(exist_ok=True)
    for ext in ('png', 'svg'):
        fig.savefig(path.with_suffix('.' + ext), dpi=170)
    plt.close(fig)
    return path.with_suffix('.png')
