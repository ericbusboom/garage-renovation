from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, PathPatch, Polygon, Rectangle
from matplotlib.path import Path as MplPath


OUT = Path(__file__).resolve().parent

INK = "#193746"
MUTED = "#657780"
LIGHT = "#dfe7e8"
PAPER = "#fbfaf6"
STEEL = "#263f4a"
STEEL_HI = "#49626c"
WOOD = "#c58c52"
WOOD_DARK = "#8d5d32"
PLY = "#e0bb7f"
OSB = "#b99a69"
WIRE = "#dc6a3b"
TEAL = "#2f7f7a"
RED = "#b74e3a"


def setup_ax(ax, xlim=(0, 100), ylim=(0, 100)):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


def label(ax, x, y, text, size=9, color=INK, weight="normal", ha="left", va="center", **kw):
    ax.text(x, y, text, fontsize=size, color=color, fontweight=weight,
            ha=ha, va=va, family="DejaVu Sans", **kw)


def line(ax, x1, y1, x2, y2, color=INK, lw=1.2, **kw):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, solid_capstyle="round", **kw)


def w_section(ax, cx, top, scale=2.4, face=STEEL):
    # W12x16 proportions: d 12.0, bf 3.99, tw .220, tf .265.
    d, bf, tw, tf = 12.0 * scale, 3.99 * scale, .22 * scale, .265 * scale
    x0 = cx - bf / 2
    ax.add_patch(Rectangle((x0, top - tf), bf, tf, facecolor=face, edgecolor=INK, lw=.8))
    ax.add_patch(Rectangle((cx - tw / 2, top - d + tf), tw, d - 2 * tf,
                           facecolor=face, edgecolor=INK, lw=.6))
    ax.add_patch(Rectangle((x0, top - d), bf, tf, facecolor=face, edgecolor=INK, lw=.8))
    return dict(d=d, bf=bf, tw=tw, tf=tf, x0=x0, bottom=top-d)


def dim(ax, x1, y1, x2, y2, text, offset=0, color=MUTED, size=7.5):
    # Horizontal or vertical dimension.
    if abs(y2-y1) < 1e-6:
        y = y1 + offset
        line(ax, x1, y, x2, y, color=color, lw=.8)
        line(ax, x1, y-1, x1, y+1, color=color, lw=.8)
        line(ax, x2, y-1, x2, y+1, color=color, lw=.8)
        label(ax, (x1+x2)/2, y+1.5, text, size=size, color=color, ha="center", va="bottom")
    else:
        x = x1 + offset
        line(ax, x, y1, x, y2, color=color, lw=.8)
        line(ax, x-1, y1, x+1, y1, color=color, lw=.8)
        line(ax, x-1, y2, x+1, y2, color=color, lw=.8)
        label(ax, x+1.5, (y1+y2)/2, text, size=size, color=color, va="center")


def draw_flush_detail(ax):
    setup_ax(ax, (0, 100), (0, 78))
    label(ax, 2, 74, "A  FLUSH TUCKED JOIST — CLEANEST CUSTOM DETAIL", 12, INK, "bold")
    label(ax, 2, 69.5, "Joists stop at the web; paired joists align on opposite sides. The steel seat carries them.", 8.2, MUTED)

    top = 58
    ws = w_section(ax, 50, top, 2.2)
    # Joists, with top cope under flange projection.
    jh = 7.25 * 2.2
    tf = ws["tf"] + .35
    left_tip = 50 - ws["tw"] / 2
    right_tip = 50 + ws["tw"] / 2
    flange_l = ws["x0"]
    flange_r = ws["x0"] + ws["bf"]
    # left wood polygon
    lp = [(5, top), (flange_l-.2, top), (flange_l-.2, top-tf),
          (left_tip-.4, top-tf), (left_tip-.4, top-jh), (5, top-jh)]
    rp = [(95, top), (flange_r+.2, top), (flange_r+.2, top-tf),
          (right_tip+.4, top-tf), (right_tip+.4, top-jh), (95, top-jh)]
    ax.add_patch(Polygon(lp, closed=True, facecolor=WOOD, edgecolor=WOOD_DARK, lw=1.2, zorder=2))
    ax.add_patch(Polygon(rp, closed=True, facecolor=WOOD, edgecolor=WOOD_DARK, lw=1.2, zorder=2))
    # Redraw flange atop wood to show tuck.
    ax.add_patch(Rectangle((ws["x0"], top-ws["tf"]), ws["bf"], ws["tf"],
                           facecolor=STEEL, edgecolor=INK, lw=.8, zorder=4))
    # Continuous bearing angle both sides, schematic.
    seat_y = top-jh
    for side in (-1, 1):
        webx = 50 + side*ws["tw"]/2
        xout = webx + side*5.1
        line(ax, webx, seat_y, xout, seat_y, STEEL_HI, 3.0, zorder=5)
        line(ax, webx + side*.4, seat_y, webx + side*.4, seat_y+5.5, STEEL_HI, 2.4, zorder=5)
        # small side clip
        clipx = webx + side*4.1
        line(ax, clipx, seat_y+.7, clipx, seat_y+5.0, STEEL_HI, 1.8, zorder=5)
        ax.add_patch(Circle((clipx, seat_y+3.0), .45, facecolor=PAPER, edgecolor=STEEL, lw=.8, zorder=6))

    dim(ax, 50, top, 50, top-ws["d"], "12.0″ W12×16", offset=11)
    dim(ax, ws["x0"], top+1, ws["x0"]+ws["bf"], top+1, "3.99″ flange", offset=0)
    dim(ax, 8, top, 8, top-jh, "7.25″ 2×8", offset=-3)
    line(ax, 67, 46, 57, seat_y+1.0, MUTED, .9)
    label(ax, 68, 46, "continuous seat angle +\ndiscrete side clip\n(size/welds by engineer)", 7.6, MUTED, va="top")
    line(ax, 29, 64, 43, top-tf/2, MUTED, .9)
    label(ax, 28, 65, "≈ 5⁄16″ deep × 1⅞″ long\ntop cope + fit allowance", 7.6, MUTED, ha="right", va="bottom")
    label(ax, 50, 7.5, "VISUAL RESULT: wood and steel share one crisp top plane; almost all hardware disappears in the W pocket.",
          8.2, TEAL, "bold", ha="center")
    label(ax, 50, 3.3, "Do not assume the cope provides bearing. Confirm end shear, seat, welds, web local strength, uplift and lateral restraint.",
          7.4, RED, ha="center")


def draw_service_section(ax):
    setup_ax(ax, (0, 100), (0, 78))
    label(ax, 2, 74, "B  HIDDEN SERVICE FLOOR — LIGHTS + WIRING ABOVE THE CEILING", 12, INK, "bold")
    label(ax, 2, 69.5, "Your layered idea works best when the upper panel is the structural deck and the lower panel is the visible ceiling.", 8.2, MUTED)
    x0, x1 = 5, 73
    y0 = 22
    # exposed joists below ceiling
    for x in (16, 39, 62):
        ax.add_patch(Rectangle((x-2.6, y0-12), 5.2, 12, facecolor=WOOD, edgecolor=WOOD_DARK, lw=1.0))
    # visible ceiling panel
    ax.add_patch(Rectangle((x0, y0), x1-x0, 3.0, facecolor=PLY, edgecolor=WOOD_DARK, lw=.9))
    # service sleepers on edge (recommended)
    sleeper_y = y0+3
    for x in (16, 39, 62):
        ax.add_patch(Rectangle((x-2.6, sleeper_y), 5.2, 15.0, facecolor=WOOD, edgecolor=WOOD_DARK, lw=.9))
    # structural subfloor
    ax.add_patch(Rectangle((x0, sleeper_y+15), x1-x0, 4.4, facecolor=OSB, edgecolor=WOOD_DARK, lw=.9))
    # finish floor
    ax.add_patch(Rectangle((x0, sleeper_y+19.4), x1-x0, 2.0, facecolor="#8f6d4b", edgecolor=WOOD_DARK, lw=.7))
    # conduit and cable
    line(ax, 20, sleeper_y+6, 35, sleeper_y+6, WIRE, 2.2)
    ax.add_patch(Circle((27.5, sleeper_y+6), 2.0, facecolor=PAPER, edgecolor=STEEL, lw=1.2))
    label(ax, 27.5, sleeper_y+6, "EMT", 5.7, STEEL, "bold", ha="center")
    # light opening + wafer
    ax.add_patch(Rectangle((45, y0-.7), 10, 1.4, facecolor="#f1c657", edgecolor=INK, lw=.8))
    ax.add_patch(Rectangle((46.2, y0+3.0), 7.6, 4.2, facecolor=PAPER, edgecolor=STEEL, lw=.9))
    line(ax, 35, sleeper_y+6, 46.2, sleeper_y+5.1, WIRE, 2.2)
    # access box at edge
    ax.add_patch(Rectangle((65, sleeper_y+4), 6, 6, facecolor=PAPER, edgecolor=STEEL, lw=1.0))
    label(ax, 68, sleeper_y+7, "J", 7, STEEL, "bold", ha="center")
    # leaders
    label(ax, 76, sleeper_y+20.5, "finish floor", 7.2, MUTED, va="center")
    label(ax, 76, sleeper_y+17.2, "23⁄32″ T&G structural deck", 7.2, INK, "bold", va="center")
    label(ax, 76, sleeper_y+10.5, "2×3 sleepers on edge\n2½″ service cavity", 7.2, MUTED, va="center")
    label(ax, 76, y0+1.5, "½″ A-grade plywood\nvisible ceiling plane", 7.2, MUTED, va="center")
    label(ax, 50, 12, "low-profile light", 7.2, MUTED, ha="center")
    line(ax, 50, 14, 50, 21.3, MUTED, .8)
    label(ax, 34, 53, "Dedicated conduit lanes cross over the W-beam top flange in the same cavity.\nKeep junction boxes accessible through a removable light or perimeter access panel.",
          8.0, TEAL, "bold", ha="center", va="bottom")
    label(ax, 50, 4, "If floor height must stay minimal: flat 2×4 sleepers give only 1½″. Use EMT / engineered steel protection; ordinary cable cannot sit safely in the screw zone.",
          7.4, RED, ha="center")


def arched_joist(ax, x, y, length=78, depth=15, rise=4.5, color=WOOD):
    verts = [(x, y+depth), (x+length, y+depth), (x+length, y),
             (x+length*.75, y+rise*.45), (x+length*.5, y+rise),
             (x+length*.25, y+rise*.45), (x, y), (x, y+depth)]
    codes = [MplPath.MOVETO, MplPath.LINETO, MplPath.LINETO,
             MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
             MplPath.LINETO, MplPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=color, edgecolor=WOOD_DARK, lw=1.2))


def draw_arch_detail(ax):
    setup_ax(ax, (0, 100), (0, 78))
    label(ax, 2, 74, "C  SHALLOW ARCH — MAKE THE SHAPE HONEST", 12, INK, "bold")
    label(ax, 2, 69.5, "The graceful version starts deeper; it does not carve capacity out of a 2×8 at midspan.", 8.2, MUTED)

    # good option
    arched_joist(ax, 9, 36, 82, 17, 4.5)
    line(ax, 9, 57, 91, 57, LIGHT, .9, linestyle="--")
    label(ax, 50, 59, "flat floor / ceiling panel above", 7.5, MUTED, ha="center")
    label(ax, 50, 27, "GOOD CONCEPT", 8.5, TEAL, "bold", ha="center")
    label(ax, 50, 23, "engineered 2×10 / LVL / glulam profile; smooth CNC curve; minimum depth preserved at center", 7.5, MUTED, ha="center")
    # mini bad comparison
    ax.add_patch(Rectangle((12, 7), 30, 10, facecolor=WOOD, edgecolor=WOOD_DARK, lw=1.0))
    arc = Arc((27, 7), 28, 7, theta1=0, theta2=180, color=RED, lw=2.0)
    ax.add_patch(arc)
    label(ax, 46, 12, "DON'T: field-cut the tension edge of the already-sized 2×8.\nThe maximum cut lands near maximum bending.", 7.2, RED, va="center")
    label(ax, 50, 2.4, "At the 125 psf storage reading the current 2×8 study is already at DCR 0.96—there is effectively no reserve for an arch cut.",
          7.4, RED, "bold", ha="center")


def draw_option_strip(ax):
    setup_ax(ax, (0, 210), (0, 40))
    label(ax, 3, 37, "CONNECTION FAMILY — FROM QUIETEST TO MOST EXPRESSIVE", 10.5, INK, "bold")
    options = [
        (5, "1", "TUCKED + SEAT ANGLE", "best fit for this frame", TEAL),
        (57, "2", "TOP-FLANGE HANGER", "simplest listed hardware", STEEL_HI),
        (109, "3", "CONCEALED KNIFE PLATE", "premium; thicker timber", WOOD_DARK),
        (161, "4", "EXPOSED CLIP", "celebrate the rhythm", "#9b6a3d"),
    ]
    for x, n, title, sub, c in options:
        ax.add_patch(Rectangle((x, 7), 44, 24, facecolor="#ffffff", edgecolor=LIGHT, lw=1.2))
        ax.add_patch(Circle((x+6, 25), 3.3, facecolor=c, edgecolor="none"))
        label(ax, x+6, 25, n, 8, "white", "bold", ha="center")
        label(ax, x+11, 26, title, 6.8, INK, "bold")
        label(ax, x+11, 21.5, sub, 6.8, MUTED)
        # tiny connector glyph
        line(ax, x+9, 12, x+35, 12, WOOD, 5)
        line(ax, x+22, 9, x+22, 17, STEEL, 4)
        if n == "1":
            line(ax, x+18, 11, x+26, 11, c, 2)
        elif n == "2":
            ax.add_patch(Rectangle((x+18, 10), 8, 4, facecolor="none", edgecolor=c, lw=1.5))
        elif n == "3":
            line(ax, x+22, 10, x+22, 14, c, 1.5)
            for yy in (10.7, 12, 13.3):
                ax.add_patch(Circle((x+22, yy), .35, facecolor=PAPER, edgecolor=c, lw=.6))
        else:
            ax.add_patch(Circle((x+19, 12), 1.2, facecolor=c, edgecolor="none"))
            ax.add_patch(Circle((x+25, 12), 1.2, facecolor=c, edgecolor="none"))


def make_sheet():
    fig = plt.figure(figsize=(16, 12), facecolor=PAPER)
    gs = fig.add_gridspec(3, 2, height_ratios=[0.18, 1, 1], hspace=.18, wspace=.08,
                          left=.035, right=.975, top=.965, bottom=.045)
    title_ax = fig.add_subplot(gs[0, :])
    setup_ax(title_ax, (0, 210), (0, 40))
    title_ax.set_aspect("auto")
    label(title_ax, 3, 34, "EXPOSED LOFT FLOOR · JOIST / W-BEAM CONNECTION STUDY", 19, INK, "bold")
    label(title_ax, 3, 22, "Garage study · W12×16 concept · 2×8 joists at 16″ o.c. · preliminary architectural details", 9.5, MUTED)
    label(title_ax, 207, 33, "JH-001", 10, INK, "bold", ha="right")
    label(title_ax, 207, 25, "21 SEPTEMBER 2026", 7.5, MUTED, ha="right")
    line(title_ax, 3, 15, 207, 15, LIGHT, 1.3)
    label(title_ax, 3, 7, "DESIGN INTENT", 7.5, TEAL, "bold")
    label(title_ax, 27, 7, "quiet painted wood cells, dark steel lines, flush top plane, wiring and low-profile lights hidden above", 8.5, INK)
    label(title_ax, 207, 7, "NOT FOR CONSTRUCTION", 7.5, RED, "bold", ha="right")

    draw_flush_detail(fig.add_subplot(gs[1, 0]))
    draw_service_section(fig.add_subplot(gs[1, 1]))
    draw_arch_detail(fig.add_subplot(gs[2, 0]))
    draw_option_strip(fig.add_subplot(gs[2, 1]))

    fig.text(.5, .012, "Connection sizes, welds, fasteners, fire protection, diaphragm and electrical routing require project-specific engineering and permitting.",
             ha="center", va="bottom", fontsize=7.5, color=MUTED, family="DejaVu Sans")
    fig.savefig(OUT / "joist-hanger-options.png", dpi=180, facecolor=PAPER)
    fig.savefig(OUT / "joist-hanger-options.pdf", facecolor=PAPER)
    fig.savefig(OUT / "joist-hanger-options.svg", facecolor=PAPER)
    plt.close(fig)


def draw_closed_ceiling_section(ax):
    setup_ax(ax, (0, 110), (0, 78))
    label(ax, 2, 74, "A  DIRECT CEILING BELOW THE 2×8s", 12, INK, "bold")
    label(ax, 2, 69.5, "No raised floor. The joist cavity becomes the service space; the W-beam remains expressed below it.", 8.2, MUTED)
    top = 59
    ws = w_section(ax, 55, top, 2.3)
    jh = 7.25 * 2.3
    # Joists finish flush to steel top and terminate at the beam pocket.
    for x, w in ((5, 45), (60, 45)):
        ax.add_patch(Rectangle((x, top-jh), w, jh, facecolor=WOOD, edgecolor=WOOD_DARK, lw=1.1, zorder=2))
    # Schematic nailers and ordinary hangers inside pocket.
    for side in (-1, 1):
        nx = 55 + side*3.0
        ax.add_patch(Rectangle((nx-(1.8 if side < 0 else 0), top-jh+1), 1.8, jh-2,
                               facecolor="#a87845", edgecolor=WOOD_DARK, lw=.8, zorder=4))
        hx = 55 + side*5.2
        line(ax, hx, top-jh+.5, hx, top-4, STEEL_HI, 2.2, zorder=5)
        line(ax, hx, top-jh+.5, hx-side*2.2, top-jh+.5, STEEL_HI, 2.2, zorder=5)
    # Electrical hole and cable through joist center.
    cy = top-jh/2
    ax.add_patch(Circle((31, cy), 2.0, facecolor=PAPER, edgecolor=INK, lw=1.0, zorder=6))
    line(ax, 9, cy, 48, cy, WIRE, 2.0, zorder=5)
    # furring and ceiling plane
    ceil_y = top-jh-2.0
    for x in (12, 27, 42, 68, 83, 98):
        ax.add_patch(Rectangle((x-2.7, top-jh-2.0), 5.4, 2.0, facecolor=WOOD_DARK, edgecolor=WOOD_DARK, lw=.6))
    ax.add_patch(Rectangle((5, ceil_y-2.2), 45, 2.2, facecolor="#eee9df", edgecolor=MUTED, lw=.8))
    ax.add_patch(Rectangle((60, ceil_y-2.2), 45, 2.2, facecolor=PLY, edgecolor=WOOD_DARK, lw=.8))
    # small lights
    for x in (22, 82):
        ax.add_patch(Rectangle((x-4, ceil_y-2.8), 8, 1.2, facecolor="#f1c657", edgecolor=INK, lw=.7))
    dim(ax, 108, top, 108, top-ws["d"], "12″ W-beam", offset=0)
    dim(ax, 103, top, 103, top-jh, "7¼″ joist", offset=0)
    dim(ax, 55, top-jh, 55, top-ws["d"], "≈ 4¾″ beam reveal", offset=9)
    label(ax, 17, ceil_y-7, "5⁄8″ drywall", 7.5, MUTED, ha="center")
    label(ax, 83, ceil_y-7, "wood panel / T&G", 7.5, MUTED, ha="center")
    label(ax, 31, cy+5.5, "bored hole near joist centerline", 7.2, WIRE, ha="center")
    label(ax, 55, 6, "A thin furring layer clears hanger seats, gives the finish a continuous fastening plane, and reduces drywall cracking at hardware.",
          7.7, TEAL, "bold", ha="center")


def draw_wiring_plan(ax):
    setup_ax(ax, (0, 110), (0, 78))
    label(ax, 2, 74, "B  EAST LEAN-TO AS THE ELECTRICAL SPINE", 12, INK, "bold")
    label(ax, 2, 69.5, "Feed each beam bay independently from the hidden east zone; never ask a cable to cross a W-web.", 8.2, MUTED)
    x0, x1, y0, y1 = 8, 88, 9, 62
    # Plan: three W beams bound two bays.
    for y in (y0, (y0+y1)/2, y1):
        line(ax, x0, y, x1, y, STEEL, 4.2)
    # N-S joists in each bay.
    for x in range(14, 88, 8):
        line(ax, x, y0+2, x, (y0+y1)/2-2, WOOD, 2.0)
        line(ax, x, (y0+y1)/2+2, x, y1-2, WOOD, 2.0)
    # Lean-to/wall spine.
    ax.add_patch(Rectangle((91, 7), 12, 58, facecolor="#dfe9e4", edgecolor=TEAL, lw=1.2))
    label(ax, 97, 36, "HIDDEN\nLEAN-TO\nCHASE", 7.2, TEAL, "bold", ha="center")
    line(ax, 94, 11, 94, 61, WIRE, 3.0)
    # Branch circuits enter each beam bay and cross joists via holes.
    for yy in (22, 49):
        line(ax, 94, yy, 18, yy, WIRE, 2.2)
        for xx in (28, 52, 76):
            ax.add_patch(Circle((xx, yy), 1.8, facecolor="#f1c657", edgecolor=INK, lw=.8))
    # symbols and callouts
    label(ax, 48, 66, "W-BEAMS", 7.2, STEEL, "bold", ha="center")
    label(ax, 46, 4, "lights and cable remain inside one bay", 7.2, MUTED, ha="center")
    line(ax, 96, 67, 96, 62, TEAL, .9)
    label(ax, 96, 70, "accessible junction / pull points", 7.2, TEAL, "bold", ha="center")


def draw_hole_rules(ax):
    setup_ax(ax, (0, 110), (0, 48))
    label(ax, 2, 44, "C  2×8 BORING ZONE — SIMPLE, BUT DISCIPLINED", 11.5, INK, "bold")
    x0, y0, w, h = 8, 12, 82, 20
    ax.add_patch(Rectangle((x0, y0), w, h, facecolor=WOOD, edgecolor=WOOD_DARK, lw=1.2))
    # 2-inch exclusion strips (schematic).
    strip = h*(2/7.25)
    ax.add_patch(Rectangle((x0, y0), w, strip, facecolor=RED, alpha=.18, edgecolor="none"))
    ax.add_patch(Rectangle((x0, y0+h-strip), w, strip, facecolor=RED, alpha=.18, edgecolor="none"))
    # centered cable hole
    r = h*(1.0/7.25)
    ax.add_patch(Circle((50, y0+h/2), r, facecolor=PAPER, edgecolor=TEAL, lw=2.0))
    line(ax, 15, y0+h/2, 83, y0+h/2, WIRE, 2.2)
    label(ax, 50, y0+h/2, "≤ 2⅜″", 6.5, TEAL, "bold", ha="center")
    label(ax, 94, y0+h-strip/2, "2″ no-hole zone", 7.2, RED)
    label(ax, 94, y0+strip/2, "2″ no-hole zone", 7.2, RED)
    label(ax, 50, 5, "For a 7¼″ sawn joist: hole diameter ≤ one-third depth (2.42″), ≥ 2″ from top, bottom, other holes and any notch.",
          7.6, MUTED, ha="center")


def draw_finish_choices(ax):
    setup_ax(ax, (0, 110), (0, 48))
    label(ax, 2, 44, "D  WHAT THE ROOM WILL FEEL LIKE", 11.5, INK, "bold")
    cards = [
        (4, "DRYWALL", "quietest + brightest", "best fire/acoustic finish", "#eee9df"),
        (39, "VENEER PLYWOOD", "warm modern grid", "expressed ⅛″ reveals", PLY),
        (74, "T&G WOOD", "richest / most crafted", "more joints and movement", WOOD),
    ]
    for x, title, sub, note, c in cards:
        ax.add_patch(Rectangle((x, 8), 30, 27, facecolor="#fff", edgecolor=LIGHT, lw=1.1))
        ax.add_patch(Rectangle((x+3, 21), 24, 10, facecolor=c, edgecolor=WOOD_DARK if c != "#eee9df" else MUTED, lw=.8))
        for xx in (x+11, x+19):
            line(ax, xx, 21, xx, 31, WOOD_DARK, .7)
        ax.add_patch(Circle((x+15, 26), 1.5, facecolor="#f1c657", edgecolor=INK, lw=.6))
        label(ax, x+15, 17, title, 7.2, INK, "bold", ha="center")
        label(ax, x+15, 13.2, sub, 6.7, TEAL, ha="center")
        label(ax, x+15, 9.8, note, 6.3, MUTED, ha="center")


def make_closed_ceiling_sheet():
    fig = plt.figure(figsize=(16, 11), facecolor=PAPER)
    gs = fig.add_gridspec(3, 2, height_ratios=[.20, 1, .62], hspace=.18, wspace=.08,
                          left=.035, right=.975, top=.965, bottom=.05)
    title_ax = fig.add_subplot(gs[0, :])
    setup_ax(title_ax, (0, 210), (0, 40))
    title_ax.set_aspect("auto")
    label(title_ax, 3, 34, "CLOSED JOIST CEILING · NO RAISED SERVICE FLOOR", 19, INK, "bold")
    label(title_ax, 3, 22, "ordinary hangers + hidden wiring in the 2×8 cavities + east lean-to distribution spine", 9.5, MUTED)
    label(title_ax, 207, 33, "JH-002", 10, INK, "bold", ha="right")
    label(title_ax, 207, 25, "21 SEPTEMBER 2026", 7.5, MUTED, ha="right")
    line(title_ax, 3, 15, 207, 15, LIGHT, 1.3)
    label(title_ax, 3, 7, "BEST VALUE", 7.5, TEAL, "bold")
    label(title_ax, 27, 7, "direct ceiling under joists; keep the W-beams exposed; feed every bay separately from the hidden east chase", 8.5, INK)
    label(title_ax, 207, 7, "NOT FOR CONSTRUCTION", 7.5, RED, "bold", ha="right")
    draw_closed_ceiling_section(fig.add_subplot(gs[1, 0]))
    draw_wiring_plan(fig.add_subplot(gs[1, 1]))
    draw_hole_rules(fig.add_subplot(gs[2, 0]))
    draw_finish_choices(fig.add_subplot(gs[2, 1]))
    fig.text(.5, .014, "Final hanger/nailer, hole locations, ceiling fire rating, fixture listings, conductor support and junction-box access require project-specific design and inspection.",
             ha="center", va="bottom", fontsize=7.5, color=MUTED, family="DejaVu Sans")
    fig.savefig(OUT / "closed-ceiling-electrical-option.png", dpi=180, facecolor=PAPER)
    fig.savefig(OUT / "closed-ceiling-electrical-option.pdf", facecolor=PAPER)
    fig.savefig(OUT / "closed-ceiling-electrical-option.svg", facecolor=PAPER)
    plt.close(fig)


if __name__ == "__main__":
    make_sheet()
    make_closed_ceiling_sheet()
