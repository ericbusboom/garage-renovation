"""Generate the current conceptual garage drawing set.

The set is deliberately diagrammatic.  It collects the current structural
geometry and equipment layout in one Arch D PDF without presenting the result
as permit or construction documents.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D

import cabinets as CB
import lean_to_rafters as MODEL


PAGE = (36, 24)
INK = "#20262b"
MUTED = "#727b83"
GRID = "#d7dcdf"
BLUE = "#1e6fa8"
RED = "#b6423c"
GREEN = "#3c7c57"
ORANGE = "#c27a20"
PURPLE = "#76558e"
FLOOR = "#f1eee8"
SHEET_DATE = "2026-09-24"
REVISION = "P0"
PROJECT = "GARAGE RENOVATION"

GROUP_STYLE = {
    "Columns": ("#34495e", 2.2), "Beams": ("#2471a3", 1.8),
    "Roof": ("#5b6b73", 1.2), "Rafters": ("#2980b9", 1.0),
    "Joists": ("#7f8c8d", .9), "Bracing": ("#c0392b", 1.4),
    "Clerestory": ("#8e6b3a", 1.5), "Truss": ("#884ea0", 1.4),
}


def new_sheet(title: str, number: str):
    fig = plt.figure(figsize=PAGE, facecolor="white")
    fig.subplots_adjust(left=.035, right=.97, top=.94, bottom=.075)
    fig.text(.035, .963, PROJECT, fontsize=18, weight="bold", color=INK)
    fig.text(.965, .963, "CONCEPT DRAWING SET · NOT FOR CONSTRUCTION",
             fontsize=10, color=RED, weight="bold", ha="right")
    fig.add_artist(Line2D([.035, .965], [.952, .952], transform=fig.transFigure,
                          color=INK, lw=1.2))
    fig.add_artist(Rectangle((.035, .018), .93, .042, transform=fig.transFigure,
                             fill=False, edgecolor=INK, lw=1.1))
    fig.text(.045, .039, title.upper(), fontsize=15, weight="bold", va="center")
    fig.text(.71, .039, "STATUS  CONCEPT", fontsize=8, va="center")
    fig.text(.80, .039, f"REV  {REVISION}", fontsize=8, va="center")
    fig.text(.865, .039, f"DATE  {SHEET_DATE}", fontsize=8, va="center")
    fig.text(.952, .039, number, fontsize=18, weight="bold", ha="right", va="center")
    return fig


def note_box(fig, x, y, w, h, title, lines, color=INK):
    fig.add_artist(Rectangle((x, y), w, h, transform=fig.transFigure,
                             fill=False, edgecolor=color, lw=1.0))
    fig.text(x + .008, y + h - .014, title.upper(), fontsize=9, weight="bold",
             color=color, va="top")
    fig.text(x + .008, y + h - .034, "\n".join(lines), fontsize=7.5, color=INK,
             va="top", linespacing=1.45)


def member_segments(frame):
    for member, ni, nj in frame.segments:
        a, b = frame.xyz(ni), frame.xyz(nj)
        yield member, frame.group(member), a, b


def style_axes(ax, equal=True):
    ax.set_facecolor("white")
    ax.grid(True, color=GRID, lw=.35, alpha=.8)
    ax.tick_params(labelsize=6, colors=MUTED)
    for s in ax.spines.values(): s.set_color(GRID)
    if equal: ax.set_aspect("equal", adjustable="box")


def panel_title(ax, text, subtitle="SCALE: DIAGRAMMATIC"):
    ax.text(0, 1.02, text, transform=ax.transAxes, fontsize=11, weight="bold",
            color=INK, va="bottom")
    ax.text(1, 1.02, subtitle, transform=ax.transAxes, fontsize=6, color=MUTED,
            ha="right", va="bottom")


def draw_elevation(ax, frame, plane, title, flip=False):
    for _, group, a, b in member_segments(frame):
        c, lw = GROUP_STYLE.get(group, (INK, 1))
        if plane == "xz": u = (a[0], b[0]); v = (a[2], b[2])
        else: u = (a[1], b[1]); v = (a[2], b[2])
        ax.plot(u, v, color=c, lw=lw, alpha=.92, solid_capstyle="round")
    style_axes(ax)
    if flip: ax.invert_xaxis()
    ax.set_xlabel("HORIZONTAL SET-OUT · INCHES", fontsize=6, color=MUTED)
    ax.set_ylabel("HEIGHT · INCHES", fontsize=6, color=MUTED)
    panel_title(ax, title)


def draw_iso(ax, frame):
    for _, group, a, b in member_segments(frame):
        c, lw = GROUP_STYLE.get(group, (INK, 1))
        ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color=c, lw=lw, alpha=.95)
    ax.view_init(elev=22, azim=-54)
    ax.set_box_aspect((1.0, 1.18, .84))
    ax.set_axis_off()
    ax.text2D(0, 1.02, "ISOMETRIC — CURRENT FRAME", transform=ax.transAxes,
              fontsize=11, weight="bold", color=INK, va="bottom")
    ax.text2D(1, 1.02, "SCALE: DIAGRAMMATIC", transform=ax.transAxes,
              fontsize=6, color=MUTED, ha="right", va="bottom")


def draw_north(ax, x=.93, y=.91):
    ax.annotate("N", xy=(x, y), xytext=(x, y-.11), xycoords="axes fraction",
                ha="center", va="center", fontsize=8, weight="bold",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0))


def draw_structure_plan(ax, frame, alpha=.30):
    for _, group, a, b in member_segments(frame):
        if abs(a[2] - b[2]) > 1 and group == "Columns": continue
        c, lw = GROUP_STYLE.get(group, (INK, .8))
        ax.plot([a[0], b[0]], [a[1], b[1]], color=c, lw=max(.5, lw*.65), alpha=alpha)


def rect(ax, bounds, fc, label, ec=INK, alpha=.88, fontsize=7, hatch=None):
    x0, x1, y0, y1 = bounds
    p = Rectangle((x0, y0), x1-x0, y1-y0, facecolor=fc, edgecolor=ec,
                  lw=.8, alpha=alpha, hatch=hatch, zorder=3)
    ax.add_patch(p)
    ax.text((x0+x1)/2, (y0+y1)/2, label, ha="center", va="center",
            fontsize=fontsize, weight="bold", color=INK, zorder=4)
    return p


def plan_base(ax, frame, title):
    ax.add_patch(Rectangle((-34, 0), 245.5, 268, facecolor=FLOOR,
                           edgecolor=INK, lw=1.2, zorder=0))
    sx0, sx1, sy0, sy1 = CB._shed_bounds(frame)
    ax.add_patch(Rectangle((sx0, sy0), sx1-sx0, sy1-sy0, facecolor="#d4d7d9",
                           edgecolor=INK, lw=1.2, zorder=0))
    draw_structure_plan(ax, frame)
    ax.set_xlim(-52, 266); ax.set_ylim(-80, 286)
    style_axes(ax); draw_north(ax); panel_title(ax, title)
    ax.set_xlabel("EAST–WEST · INCHES", fontsize=7); ax.set_ylabel("SOUTH–NORTH · INCHES", fontsize=7)


def item_center(row): return ((row["x0"]+row["x1"])/2, (row["y0"]+row["y1"])/2)


def ground_layout(ax, frame, compact=False):
    for c in CB.FIRST_FLOOR_CABINETS:
        rect(ax, (c["x0"], c["x1"], c["y0"], c["y1"]), "#d8c7a6", c["n"], fontsize=5)
    lx0,lx1,ly0,ly1,_,_ = CB._laundry_bounds(frame)
    rect(ax, (lx0,lx1,ly0,ly1), "#c6d6df", "LAUNDRY\n58 × 30")
    for n,b in CB._bench_bounds(frame).items(): rect(ax, b, "#d5bd8d", f"{n.upper()} BENCH", fontsize=5)
    x0,x1,y0,y1,_,_ = CB._lathe_bounds(frame)
    rect(ax, (x0,x1,y0,y1), "#b9a17b", "LATHE", fontsize=6)
    for r in CB.shed_item_rows(frame):
        color = {"PW":"#e9edf0", "EP":"#7da7c1", "SPK":"#c86a65",
                 "RACK":"#65717b", "WH":"#e7e9eb"}.get(r["n"], "#ccc")
        rect(ax, (r["x0"],r["x1"],r["y0"],r["y1"]), color, r["n"], fontsize=5)


def loft_layout(ax, frame):
    colors = {"cabinet":"#cbd6dd", "machine":"#c9a87c", "crate":"#b8956a",
              "shelving":"#9ca3aa", "compressor":"#718293"}
    for r in CB.report(frame):
        label = r["n"] if r["n"] != "CNCg" else "CNC GANTRY"
        rect(ax, (r["x0"],r["x1"],r["y0"],r["y1"]), colors.get(r["kind"],"#ccc"), label, fontsize=5)


def route(ax, points, color, label=None, ls="-", lw=2.0, alpha=.9):
    xs, ys = zip(*points)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, alpha=alpha, zorder=7)
    if label:
        i = len(points)//2
        ax.text(points[i][0], points[i][1], label, fontsize=5.5, color=color,
                weight="bold", bbox=dict(fc="white", ec="none", alpha=.8, pad=1), zorder=8)


def cover(pdf, frame, output):
    fig = new_sheet("Cover / Drawing Index", "G0.01")
    fig.text(.06, .78, "GARAGE RENOVATION", fontsize=38, weight="bold", color=INK)
    fig.text(.06, .72, "CONCEPT DRAWING SET", fontsize=24, color=BLUE, weight="bold")
    fig.text(.06, .665, "Architecture · structure · electrical · data · shop air", fontsize=13, color=MUTED)
    note_box(fig, .06, .34, .38, .25, "Basis of set", [
        f"Current structural model: {frame.path.name}",
        "Current architectural/equipment layout: cabinets.py",
        "Units: inches. North is up on plans unless noted.",
        "Member and equipment locations are taken directly from the current model.",
        "Electrical, Ethernet, compressed-air and dust routes are conceptual.",
    ])
    note_box(fig, .49, .34, .44, .25, "Drawing index", [
        "G0.01  Cover / drawing index",
        "A1.01  Isometric and exterior elevations",
        "A1.02  Loft equipment and cabinet plan",
        "A1.03  Ground-floor and shed equipment plan",
        "E1.01  Concept electrical distribution",
        "T1.01  Concept Ethernet distribution",
        "M1.01  Concept dust collection and compressed air",
    ])
    note_box(fig, .06, .12, .87, .15, "Use and limitations", [
        "This set records design intent for coordination and discussion. It is not a permit set, fabrication package, or construction document.",
        "A licensed design professional must verify dimensions, loads, connections, foundations, fire/life-safety work and all MEP requirements before construction.",
        "Proposed service routes show endpoints and zoning; conductor, cable, pipe and duct sizes remain to be designed.",
    ], color=RED)
    pdf.savefig(fig); plt.close(fig)


def views(pdf, frame):
    fig = new_sheet("Isometric and Exterior Elevations", "A1.01")
    gs = fig.add_gridspec(2, 2, left=.045, right=.955, bottom=.085, top=.92, hspace=.24, wspace=.14)
    draw_iso(fig.add_subplot(gs[0,0], projection="3d"), frame)
    draw_elevation(fig.add_subplot(gs[0,1]), frame, "xz", "NORTH ELEVATION — LOOKING SOUTH", flip=True)
    draw_elevation(fig.add_subplot(gs[1,0]), frame, "yz", "EAST ELEVATION — LOOKING WEST", flip=True)
    draw_elevation(fig.add_subplot(gs[1,1]), frame, "xz", "SOUTH ELEVATION — LOOKING NORTH")
    fig.text(.048, .069, "COLOR KEY  ", fontsize=7, weight="bold")
    x=.085
    for g,(c,_) in GROUP_STYLE.items():
        fig.add_artist(Line2D([x,x+.015],[.071,.071],transform=fig.transFigure,color=c,lw=3))
        fig.text(x+.018,.069,g,fontsize=6); x += .09
    pdf.savefig(fig); plt.close(fig)


def plan_sheet(pdf, frame, loft):
    num, title = ("A1.02", "Loft Equipment and Cabinet Plan") if loft else ("A1.03", "Ground-Floor and Shed Equipment Plan")
    fig = new_sheet(title, num)
    ax = fig.add_axes([.055,.095,.68,.82])
    plan_base(ax, frame, "LOFT PLAN" if loft else "GROUND-FLOOR PLAN")
    if loft: loft_layout(ax, frame)
    else: ground_layout(ax, frame)
    nx=.765
    if loft:
        rows=CB.report(frame)
        fig.text(nx,.88,"LOFT EQUIPMENT",fontsize=11,weight="bold")
        y=.85
        for r in rows:
            fig.text(nx,y,f"{r['n']:<5} {r['kind']:<10} {r['w']:g} × {r['d']:g} × {r['h']:g} in",fontsize=6.8)
            y-=.032
        note_box(fig,nx,.11,.19,.20,"Coordination notes",[
            "Cabinets and equipment are nonstructural.",
            "Maintain the documented walkways and access zones.",
            "Verify anchorage, working clearances and concentrated floor loads.",
            "CNC is shown in its parked position.",
        ])
    else:
        fig.text(nx,.88,"GROUND-FLOOR ELEMENTS",fontsize=11,weight="bold")
        lines=["GF-C1–C3  east built-ins","LAUNDRY  58 × 30 × 66 in","SOUTH BENCH  30 in deep","WEST BENCH  26 in deep","LATHE  24 × 57 in"]
        lines += [f"{r['n']:<5} {r['what']}" for r in CB.shed_item_rows(frame)]
        fig.text(nx,.84,"\n".join(lines),fontsize=6.6,va="top",linespacing=1.45,wrap=True)
        note_box(fig,nx,.11,.19,.19,"Coordination notes",[
            "Shed equipment is shown at the current cabinet-layout positions.",
            "Keep required electrical-panel, heater and sprinkler service clearances.",
            "Confirm wall construction and equipment anchorage before installation.",
        ])
    pdf.savefig(fig); plt.close(fig)


def electrical(pdf, frame):
    fig = new_sheet("Concept Electrical Distribution", "E1.01")
    ax=fig.add_axes([.05,.095,.59,.82]); plan_base(ax,frame,"POWER PLAN — CONCEPT ROUTING"); ground_layout(ax,frame,True)
    shed={r['n']:r for r in CB.shed_item_rows(frame)}
    ep=item_center(shed['EP']); pw=item_center(shed['PW']); wh=item_center(shed['WH'])
    route(ax,[pw,(pw[0],-8),(ep[0],-8),ep],RED,"PW ↔ EP")
    route(ax,[ep,(196,20),(190,20),(190,21)],BLUE,"LOFT RISER")
    route(ax,[ep,(175,8),(175,21),(165,21)],BLUE,"LAUNDRY")
    route(ax,[ep,(160,-5),(160,36),(55,36)],BLUE,"SHOP SOUTH/WEST")
    route(ax,[ep,(235,-5),wh],BLUE,"WH")
    ax.scatter([ep[0]],[ep[1]],s=75,c=RED,zorder=10)
    bx=fig.add_axes([.68,.50,.27,.38]); bx.axis("off"); bx.set_xlim(0,10);bx.set_ylim(0,10)
    boxes=[(4,8.5,"UTILITY / METER"),(4,6.8,"100 A PANEL · EP"),(1.2,4.8,"POWERWALL"),(4,4.8,"SHOP / LAUNDRY"),(6.8,4.8,"WATER HEATER"),(4,2.7,"LOFT EQUIPMENT")]
    for x,y,t in boxes:
        bx.add_patch(Rectangle((x-.9,y-.45),1.8,.9,fc="#eef3f6",ec=INK,lw=1));bx.text(x,y,t,ha="center",va="center",fontsize=6,weight="bold")
    for a,b in [((4,8.05),(4,7.25)),((4,6.35),(1.2,5.25)),((4,6.35),(4,5.25)),((4,6.35),(6.8,5.25)),((4,4.35),(4,3.15))]: bx.add_patch(FancyArrowPatch(a,b,arrowstyle="-|>",mutation_scale=8,color=BLUE,lw=1.4))
    note_box(fig,.68,.10,.27,.31,"Design decisions required",[
        "Confirm service point, available fault current and Powerwall topology.",
        "Develop load calculation and panel schedule; size all feeders and branches.",
        "Provide dedicated circuits as required for laundry, water heater, CNC, mill/drill, dust collector and compressor.",
        "Coordinate disconnects, GFCI/AFCI protection, grounding, lighting, receptacle spacing and code working clearances.",
        "All routes shown are conceptual home-run zones.",
    ],color=BLUE)
    pdf.savefig(fig);plt.close(fig)


def ethernet(pdf,frame):
    fig=new_sheet("Concept Ethernet Distribution","T1.01")
    ax=fig.add_axes([.05,.095,.68,.82]);plan_base(ax,frame,"DATA PLAN — CONCEPT HOME RUNS");ground_layout(ax,frame,True)
    rack=next(r for r in CB.shed_item_rows(frame) if r['n']=='RACK'); origin=item_center(rack)
    targets=[((180,32),"LAUNDRY / SOUTH"),((30,95),"WEST BENCH"),((30,160),"LATHE"),((110,180),"LOFT / SHOP"),((90,130),"CEILING AP")]
    for target,label in targets:
        route(ax,[origin,(215,-5),(215,target[1]),target],PURPLE,label,ls="--",lw=1.6)
        ax.scatter(*target,s=35,facecolor="white",edgecolor=PURPLE,lw=1.5,zorder=10)
    ax.scatter(*origin,s=90,c=PURPLE,zorder=10);ax.text(origin[0]-4,origin[1]-8,"RACK",fontsize=6,weight="bold",color=PURPLE)
    note_box(fig,.765,.56,.19,.31,"System concept",[
        "The wall-mounted 19-inch rack in the shed is the star point.",
        "Provide home-run cabling to shop work zones, the lathe area, loft equipment and a ceiling wireless-access-point location.",
        "Use pathway and spare capacity for future cameras, controls and access points.",
    ],color=PURPLE)
    note_box(fig,.765,.16,.19,.31,"Coordination notes",[
        "Routes are schematic; locate pathways after power and fire-protection coordination.",
        "Maintain separation from line-voltage conductors and sources of interference.",
        "Confirm cable category, patch-panel size, PoE load, rack ventilation, bonding and surge protection.",
        "Label both ends and record final cable IDs on an as-built schedule.",
    ])
    pdf.savefig(fig);plt.close(fig)


def mechanical(pdf,frame):
    fig=new_sheet("Concept Dust Collection and Compressed Air","M1.01")
    ax=fig.add_axes([.05,.095,.68,.82]);plan_base(ax,frame,"LOFT / SHOP SERVICES — CONCEPT ROUTING");loft_layout(ax,frame)
    rows={r['n']:r for r in CB.report(frame)}; dc=item_center(rows['DC']); comp=item_center(rows['C1'])
    dust_targets=[(item_center(rows[n]),n) for n in ('M1','M2','CNC','D1')]
    for target,label in dust_targets:
        route(ax,[dc,(145,90),(target[0],90),target],GREEN,label,lw=2.2)
        ax.scatter(*target,s=30,c=GREEN,zorder=10)
    lathe=CB._lathe_bounds(frame); lt=((lathe[0]+lathe[1])/2,(lathe[2]+lathe[3])/2)
    route(ax,[dc,(145,110),(75,110),(75,lt[1]),lt],GREEN,"DROP TO LATHE",ls="--")
    air_targets=[((35,36),"SOUTH BENCH"),((33,90),"WEST BENCH"),((160,70),"LOFT WORK")]
    for target,label in air_targets: route(ax,[comp,(175,95),(target[0],95),target],BLUE,label,ls="--",lw=1.5)
    ax.scatter(*dc,s=90,c=GREEN,zorder=10);ax.scatter(*comp,s=75,c=BLUE,zorder=10)
    note_box(fig,.765,.55,.19,.33,"Dust collection concept",[
        "DC is the loft collector. Green lines show a conceptual main with branches to M1, M2, CNC and D1 plus a drop to the ground-floor lathe.",
        "Provide a blast gate at every branch and a cleanout at low points.",
        "Final duct diameters, fan static pressure, filtration, grounding/bonding and fire protection require design from actual machine data.",
    ],color=GREEN)
    note_box(fig,.765,.16,.19,.30,"Compressed-air concept",[
        "C1 is the loft compressor. Blue dashed lines show a loop/drop concept serving the loft and both principal ground-floor benches.",
        "Slope mains to drains; provide isolation, filtration/regulation and flexible machine connections.",
        "Verify compressor ventilation, vibration isolation, relief discharge and receiver access.",
    ],color=BLUE)
    pdf.savefig(fig);plt.close(fig)


def build(output: Path):
    frame, _, _ = MODEL.build()
    output.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(output, metadata={"Title":"Garage Renovation Concept Drawing Set","Author":"Project team","Subject":"Concept coordination drawings","CreationDate":datetime(2026,9,24)}) as pdf:
        cover(pdf,frame,output);views(pdf,frame);plan_sheet(pdf,frame,True);plan_sheet(pdf,frame,False)
        electrical(pdf,frame);ethernet(pdf,frame);mechanical(pdf,frame)
    return frame


def main():
    p=argparse.ArgumentParser();p.add_argument("output",type=Path);a=p.parse_args()
    frame=build(a.output)
    print(f"wrote {a.output} from {frame.path.name}")


if __name__ == "__main__": main()
