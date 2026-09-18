"""Dimensioned west-elevation studies for a 300 ft² full-width solar slope."""
from pathlib import Path
import math
import os

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/garage-roof-options-mpl")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

OUT = Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)

L = 20.75                  # north-south wall length, 20 ft 9 in
W = 23 + 5.5 / 12         # east-west solar width, 23 ft 5.5 in
AREA = 300.0
SLOPE_LENGTH = AREA / W
TOP = 20.0
CEILING_1 = 9.0
FLOOR_2 = 9 + 8 / 12

def feet_inches(value, nearest=0.125):
    sign = "−" if value < 0 else ""
    value = abs(value)
    ft = int(value)
    inches = round((value - ft) * 12 / nearest) * nearest
    if inches >= 12:
        ft += 1
        inches = 0
    if abs(inches - round(inches)) < 1e-8:
        inch = f"{int(round(inches))}"
    else:
        whole = int(inches)
        frac = inches - whole
        glyph = {0.125:"⅛", 0.25:"¼", 0.375:"⅜", 0.5:"½", 0.625:"⅝", 0.75:"¾", 0.875:"⅞"}.get(round(frac,3), f"{frac:.3f}"[1:])
        inch = f"{whole if whole else ''}{glyph}"
    return f"{sign}{ft}′-{inch}″"

def dim_h(ax, x1, x2, y, text, color="#425466"):
    ax.annotate("", (x1,y), (x2,y), arrowprops=dict(arrowstyle="|-|", color=color, lw=.85))
    ax.text((x1+x2)/2, y+.18, text, ha="center", va="bottom", fontsize=7.4, color=color,
            bbox=dict(facecolor="white", edgecolor="none", pad=.5))

def dim_v(ax, x, y1, y2, text, color="#425466"):
    ax.annotate("", (x,y1), (x,y2), arrowprops=dict(arrowstyle="|-|", color=color, lw=.85))
    ax.text(x+.18, (y1+y2)/2, text, ha="left", va="center", rotation=90, fontsize=7.4, color=color,
            bbox=dict(facecolor="white", edgecolor="none", pad=.5))

def base(ax, title, subtitle):
    ax.set_xlim(-2.0, L+3.3); ax.set_ylim(-1.5, 22.2); ax.set_aspect("equal")
    ax.axis("off")
    ax.plot([0,L],[0,0], color="#24292f", lw=1.5)
    ax.plot([0,0],[0,TOP], color="#24292f", lw=1.4)
    ax.plot([L,L],[0,13.6], color="#24292f", lw=1.4)
    ax.plot([0,L],[CEILING_1,CEILING_1], color="#6b7785", lw=1, ls=(0,(3,2)))
    ax.add_patch(Rectangle((0,CEILING_1), L, FLOOR_2-CEILING_1,
                           facecolor="#e1e6ea", edgecolor="#24292f", lw=1))
    ax.text(-.25, CEILING_1/2, "FIRST FLOOR\n9′ ceiling", ha="right", va="center", fontsize=7.5, color="#59636e")
    ax.text(L/2, FLOOR_2+.17, "LOFT FLOOR  •  top at 9′-8″", ha="center", va="bottom", fontsize=7.2, color="#59636e")
    ax.text(0,-.55,"NORTH  •  BACK", ha="left", va="top", fontsize=8, fontweight="bold")
    ax.text(L,-.55,"SOUTH  •  FRONT", ha="right", va="top", fontsize=8, fontweight="bold")
    ax.text(.02,1.03,title,transform=ax.transAxes,fontsize=11,fontweight="bold",color="#183247",va="bottom")
    ax.text(.02,.99,subtitle,transform=ax.transAxes,fontsize=7.7,color="#59636e",va="top")
    dim_h(ax,0,L,-1.1,"EXISTING GARAGE WALL  " + feet_inches(L))
    dim_v(ax,-1.25,0,TOP,"20′-0″")

def solar(ax, start, angle_deg, label="300 ft² SOLAR SLOPE"):
    run = SLOPE_LENGTH * math.cos(math.radians(angle_deg))
    drop = SLOPE_LENGTH * math.sin(math.radians(angle_deg))
    end = start + run
    low = TOP-drop
    ax.plot([start,end],[TOP,low],color="#0d6b55",lw=4.2,solid_capstyle="butt")
    ax.plot([end,L],[low,low],color="#24292f",lw=2)
    if start:
        ax.plot([0,start],[TOP,TOP],color="#24292f",lw=2)
    ax.text((start+end)/2, (TOP+low)/2+.55, label, ha="center", va="bottom", rotation=-angle_deg,
            rotation_mode="anchor", fontsize=7.5, color="#0d6b55", fontweight="bold")
    ax.text((start+end)/2, (TOP+low)/2-.15, f"{feet_inches(SLOPE_LENGTH)} along slope",
            ha="center", va="top", rotation=-angle_deg, fontsize=7, color="#0d6b55")
    ax.text(end+.2,low+.2,"KNEE  " + feet_inches(low),fontsize=7.2,color="#183247",va="bottom")
    dim_h(ax,start,end,7.95,"HORIZONTAL RUN  " + feet_inches(run))
    if end < L:
        dim_h(ax,end,L,7.15,"FLAT SOUTH PORTION  " + feet_inches(L-end))
    dim_v(ax,end+.85,low,TOP,"DROP  " + feet_inches(drop))
    ax.text(start+.35,TOP-.65,f"{angle_deg:g}°",fontsize=8,color="#0d6b55",fontweight="bold")
    return end,low,run,drop

fig, axes = plt.subplots(2,2,figsize=(17,12))

ax=axes[0,0]
base(ax,"A — 30° slope beginning at the north wall","Baseline requested envelope; southern loft becomes low storage space")
end30,low30,run30,drop30=solar(ax,0,30)
ax.fill_between([end30,L],FLOOR_2,low30,color="#f3e5c8",alpha=.55)
ax.text((end30+L)/2,(FLOOR_2+low30)/2,"3′-11⅜″ MAX\nLOW STORAGE",ha="center",va="center",fontsize=8,color="#806126")

ax=axes[0,1]
base(ax,"B — If “30%” is literal","A 30% grade is 16.7°, not 30°; this leaves much more useful front height")
endpct,lowpct,runpct,droppct=solar(ax,0,math.degrees(math.atan(.30)),"300 ft² SOLAR SLOPE  •  30% GRADE")
ax.fill_between([endpct,L],FLOOR_2,lowpct,color="#dbe9f4",alpha=.6)
ax.text((endpct+L)/2,(FLOOR_2+lowpct)/2,"6′-7⅞″ MAX\nAT SOUTH FLAT",ha="center",va="center",fontsize=8,color="#315e7d")

ax=axes[1,0]
base(ax,"C — Move the 30° solar band 4 ft south","Adds a full-height north cap while preserving the same 300 ft² solar plane")
endshift,lowshift,_,_=solar(ax,4,30)
dim_h(ax,0,4,20.65,"4′-0″ HIGH CAP")
ax.fill_between([endshift,L],FLOOR_2,lowshift,color="#f3e5c8",alpha=.55)
ax.text(2,(TOP+FLOOR_2)/2,"10′-4″\nLOFT ENVELOPE",ha="center",va="center",fontsize=8,color="#315e7d")
ax.text((endshift+L)/2,(FLOOR_2+lowshift)/2,"LOW STORAGE",ha="center",va="center",fontsize=8,color="#806126")

ax=axes[1,1]
base(ax,"D — 30° slope with a usable south balcony dormer","A loft-level balcony needs a local raised front volume; dashed line shows winter-noon shadow")
endbal,lowbal,_,_=solar(ax,0,30)
dormer_start=14.75; dormer_top=17+4/12
ax.add_patch(Rectangle((dormer_start,FLOOR_2),L-dormer_start,dormer_top-FLOOR_2,
                       facecolor="white",edgecolor="#a44533",lw=2))
ax.plot([L,L+2],[FLOOR_2,FLOOR_2],color="#a44533",lw=3)
ax.plot([L+2,L+2],[FLOOR_2,FLOOR_2+3.5],color="#a44533",lw=1.5)
door_x=L-3.75
ax.add_patch(Rectangle((door_x,FLOOR_2),3,7,facecolor="#edf3f6",edgecolor="#24292f",lw=1.1))
ax.plot([door_x+1.5,door_x+1.5],[FLOOR_2,FLOOR_2+7],color="#24292f",lw=.8)
ax.text(dormer_start+.25,dormer_top+.25,"LOCAL FRONT DORMER  •  roof 17′-4″",fontsize=7.2,color="#a44533")
ax.text(L+1,FLOOR_2-.35,"2′ BALCONY",ha="center",va="top",fontsize=7.2,color="#a44533")
shadow_end=dormer_start-(dormer_top-lowbal)/math.tan(math.radians(33.9))
ax.plot([dormer_start,shadow_end],[dormer_top,lowbal],color="#a44533",lw=1,ls=(0,(4,3)))
ax.text((dormer_start+shadow_end)/2,(dormer_top+lowbal)/2+.35,"DECEMBER NOON\nSHADOW CHECK",ha="center",fontsize=6.8,color="#a44533",rotation=33.9)
dim_v(ax,L+2.65,FLOOR_2,FLOOR_2+7,"7′-0″ DOOR")

fig.suptitle("WEST ELEVATION — 300 ft² SOLAR-ROOF ENVELOPE STUDIES",fontsize=17,fontweight="bold",color="#183247",y=.985)
fig.text(.5,.955,"Assumes the solar surface spans the full 23′-5½″ east-west width  •  elevations measured from grade",
         ha="center",fontsize=9,color="#59636e")
fig.text(.02,.012,"Concept envelope only. Roof thickness, drainage pitch, parapets, structure and required clearances are not yet included.\n"
         "A dormer or balcony occupying part of the solar plane reduces generating area; option D places the raised volume south of the 300 ft² band but introduces seasonal shadow.",
         fontsize=8,color="#59636e")
fig.subplots_adjust(left=.035,right=.985,top=.925,bottom=.06,wspace=.06,hspace=.17)
fig.savefig(OUT/"west-elevation-roof-options.png",dpi=190,bbox_inches="tight")
fig.savefig(OUT/"west-elevation-roof-options.svg",bbox_inches="tight")
with PdfPages(OUT/"west-elevation-roof-options.pdf") as pdf:
    pdf.savefig(fig,bbox_inches="tight")
plt.close(fig)

summary = f"""# West elevation roof studies

- Solar roof width: {feet_inches(W)}
- Required active solar area: {AREA:.0f} ft²
- Required sloped length at full width: {feet_inches(SLOPE_LENGTH)}
- 30° horizontal run: {feet_inches(run30)}
- 30° vertical drop: {feet_inches(drop30)}
- Roof height after 30° slope: {feet_inches(low30)}
- Remaining south flat length: {feet_inches(L-end30)}
- Loft floor top: {feet_inches(FLOOR_2)}
- Clear envelope at the low flat roof: {feet_inches(low30-FLOOR_2)} before roof structure

Important ambiguity: a 30% grade equals 16.7°, not 30°. At a literal 30% grade, the solar band drops only {feet_inches(droppct)} and ends at {feet_inches(lowpct)}, leaving {feet_inches(lowpct-FLOOR_2)} above the loft floor before roof structure.
"""
(OUT/"README.md").write_text(summary)
print(OUT/"west-elevation-roof-options.png")
