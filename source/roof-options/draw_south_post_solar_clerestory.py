"""West and south elevations: solar slope starts at the outer south post line."""
from pathlib import Path
import math
import os

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/garage-roof-options-mpl")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon, Rectangle

OUT = Path(__file__).parent

# Recovered from the current exposed-frame CAD geometry, in feet.
POST_TO_SOUTH_WALL = 63 / 12
WALL_LENGTH = 249 / 12
NORTH_ROOF_EDGE = 253 / 12
ROOF_WIDTH = 281.5 / 12
WEST_POST_X = 0
S1_X = 180.5 / 12
S2_X = 256.25 / 12

FIRST_CEILING = 9
LOFT_FLOOR = 9 + 8 / 12
LOW_EAVE = 9
TARGET_CLEAR = 8
CAP_EAVE = LOFT_FLOOR + TARGET_CLEAR
CAP_RISE = 18 / 12
AREA = 325
ANGLE = 30
SLOPE_LENGTH = AREA / ROOF_WIDTH
RUN = SLOPE_LENGTH * math.cos(math.radians(ANGLE))
RISE = SLOPE_LENGTH * math.sin(math.radians(ANGLE))
SLOPE_TOP = LOW_EAVE + RISE
CLERESTORY = CAP_EAVE - SLOPE_TOP
SLOPE_END_FROM_SOUTH_WALL = RUN - POST_TO_SOUTH_WALL
CAP_DEPTH = NORTH_ROOF_EDGE - SLOPE_END_FROM_SOUTH_WALL
CAP_RIDGE_Y = SLOPE_END_FROM_SOUTH_WALL + CAP_DEPTH / 2
CAP_RIDGE_LENGTH = max(1.5, ROOF_WIDTH - CAP_DEPTH)

def fi(value, nearest=.125):
    sign = "−" if value < 0 else ""
    value = abs(value); ft = int(value)
    inc = round((value-ft)*12/nearest)*nearest
    if inc >= 12: ft += 1; inc = 0
    whole = int(inc); frac = round(inc-whole,3)
    glyph = {0:"", .125:"⅛", .25:"¼", .375:"⅜", .5:"½", .625:"⅝", .75:"¾", .875:"⅞"}.get(frac,"")
    itxt = f"{whole if whole else ''}{glyph}" if inc else "0"
    return f"{sign}{ft}′-{itxt}″"

def dim_h(ax,x1,x2,y,text,color="#425466"):
    ax.annotate("",(x1,y),(x2,y),arrowprops=dict(arrowstyle="|-|",lw=.9,color=color))
    ax.text((x1+x2)/2,y+.18,text,ha="center",va="bottom",fontsize=7.5,color=color,
            bbox=dict(fc="white",ec="none",pad=.5))

def dim_v(ax,x,y1,y2,text,color="#425466"):
    ax.annotate("",(x,y1),(x,y2),arrowprops=dict(arrowstyle="|-|",lw=.9,color=color))
    ax.text(x+.18,(y1+y2)/2,text,rotation=90,ha="left",va="center",fontsize=7.5,color=color,
            bbox=dict(fc="white",ec="none",pad=.5))

fig = plt.figure(figsize=(17,11.5))
gs = fig.add_gridspec(2,2,height_ratios=[1.45,1],width_ratios=[1.55,1],hspace=.16,wspace=.11)
ax = fig.add_subplot(gs[:,0])

# West elevation / section. Coordinates: x=0 at existing south wall; south is negative.
south_post = -POST_TO_SOUTH_WALL
north_wall = WALL_LENGTH
slope_end = south_post + RUN
ax.set_xlim(south_post-2.6,north_wall+2.4); ax.set_ylim(-1.4,20.4); ax.set_aspect('equal'); ax.axis('off')
ax.plot([0,north_wall],[0,0],color="#252a2e",lw=1.4)
ax.plot([0,0],[0,FIRST_CEILING],color="#252a2e",lw=1.5)
ax.plot([north_wall,north_wall],[0,CAP_EAVE],color="#252a2e",lw=1.5)
ax.plot([south_post,south_post],[0,LOW_EAVE],color="#6d4932",lw=3)
ax.text(south_post-.15,4.4,"OUTER SOUTH\nPOST LINE",ha="right",va="center",fontsize=7.5,color="#6d4932")
ax.plot([0,north_wall],[FIRST_CEILING,FIRST_CEILING],color="#7b8791",lw=1,ls=(0,(3,2)))
ax.add_patch(Rectangle((0,FIRST_CEILING),north_wall,LOFT_FLOOR-FIRST_CEILING,
                       fc="#e1e6ea",ec="#252a2e",lw=1))
ax.text(north_wall/2,LOFT_FLOOR+.15,"LOFT FLOOR  •  top at 9′-8″",ha="center",fontsize=7.7,color="#59636e")

# Main 30 degree solar plane.
ax.plot([south_post,slope_end],[LOW_EAVE,SLOPE_TOP],color="#0d6b55",lw=5,solid_capstyle='butt')
ax.text((south_post+slope_end)/2,(LOW_EAVE+SLOPE_TOP)/2+.55,"325 ft² ACTIVE SOLAR PLANE",
        rotation=ANGLE,ha="center",va="bottom",fontsize=9,color="#0d6b55",fontweight='bold')
ax.text(south_post+.45,LOW_EAVE+.55,"30°",fontsize=9,color="#0d6b55",fontweight='bold')
ax.text((south_post+slope_end)/2,(LOW_EAVE+SLOPE_TOP)/2-.15,fi(SLOPE_LENGTH)+" along slope",
        rotation=ANGLE,ha="center",va="top",fontsize=7.5,color="#0d6b55")

# Clerestory and hip cap.
ax.plot([slope_end,slope_end],[SLOPE_TOP,CAP_EAVE],color="#a44533",lw=5)
ax.text(slope_end+.28,(SLOPE_TOP+CAP_EAVE)/2,"CLERESTORY\n"+fi(CLERESTORY),ha="left",va="center",
        fontsize=8,color="#a44533",fontweight='bold')
for z in [SLOPE_TOP+.15,SLOPE_TOP+CLERESTORY/2,CAP_EAVE-.15]:
    ax.plot([slope_end-.12,slope_end+.12],[z,z],color="white",lw=.7)
ax.plot([slope_end,CAP_RIDGE_Y,north_wall],[CAP_EAVE,CAP_EAVE+CAP_RISE,CAP_EAVE],
        color="#252a2e",lw=2.4)
ax.fill([slope_end,CAP_RIDGE_Y,north_wall],[CAP_EAVE,CAP_EAVE+CAP_RISE,CAP_EAVE],
        color="#d9dde0",alpha=.65)
ax.text((slope_end+north_wall)/2,CAP_EAVE+CAP_RISE+.3,"LOW HIPPED CAP  •  18″ RISE",ha="center",fontsize=8,color="#183247")

# Vertical envelope and dimensions.
ax.fill_between([slope_end,north_wall],LOFT_FLOOR,CAP_EAVE,color="#dceaf2",alpha=.52)
ax.text((slope_end+north_wall)/2,(LOFT_FLOOR+CAP_EAVE)/2,"8′-0″ CLEAR ENVELOPE\nBEFORE ROOF STRUCTURE",
        ha="center",va="center",fontsize=9,color="#315e7d",fontweight='bold')
ax.text((0+slope_end)/2,LOFT_FLOOR+1.4,"SLOPING / LOW-HEADROOM\nLOFT ZONE",ha="center",fontsize=8,color="#806126")
dim_h(ax,south_post,0,-.85,"POSTS TO EXISTING SOUTH WALL  5′-3″")
dim_h(ax,south_post,slope_end,7.75,"SOLAR HORIZONTAL RUN  "+fi(RUN))
dim_h(ax,0,slope_end,7.0,"SLOPE ENDS "+fi(SLOPE_END_FROM_SOUTH_WALL)+" NORTH OF WALL")
dim_h(ax,slope_end,north_wall,6.25,"HIPPED-CAP PLAN LENGTH  "+fi(north_wall-slope_end))
dim_v(ax,south_post-1.55,0,LOW_EAVE,"9′-0″ LOW EDGE")
dim_v(ax,slope_end+.95,LOW_EAVE,SLOPE_TOP,"SOLAR RISE  "+fi(RISE))
dim_v(ax,north_wall+1.15,0,CAP_EAVE,"17′-8″ CAP EAVE")
dim_v(ax,north_wall+2.0,LOFT_FLOOR,CAP_EAVE,"8′-0″ INTERIOR")
ax.text(south_post,-1.22,"SOUTH / FRONT\nPOST LINE",ha="center",va="top",fontsize=7,fontweight='bold')
ax.text(0,-1.22,"EXISTING\nSOUTH WALL",ha="center",va="top",fontsize=7,fontweight='bold')
ax.text(north_wall,-1.22,"NORTH / BACK",ha="right",va="top",fontsize=7,fontweight='bold')
ax.set_title("WEST ELEVATION / ENVELOPE SECTION",loc='left',fontsize=13,fontweight='bold',color="#183247",pad=12)

# South elevation.
ax2 = fig.add_subplot(gs[0,1]); ax2.set_xlim(-1.4,ROOF_WIDTH+1.4); ax2.set_ylim(-.8,20); ax2.set_aspect('equal'); ax2.axis('off')
ax2.plot([0,ROOF_WIDTH],[0,0],color="#252a2e",lw=1.4)
for x,label in [(WEST_POST_X,"SW0"),(S1_X,"S1"),(S2_X,"S2")]:
    ax2.plot([x,x],[0,LOW_EAVE],color="#6d4932",lw=3)
    ax2.text(x,.25,label,ha="center",va="bottom",fontsize=7.5,color="#6d4932",fontweight='bold')
ax2.plot([0,ROOF_WIDTH],[LOW_EAVE,LOW_EAVE],color="#252a2e",lw=2.2)
# Orthographic projection of rising plane, rendered as panel field.
ax2.add_patch(Rectangle((0,LOW_EAVE),ROOF_WIDTH,RISE,fc="#203b40",ec="#0d6b55",lw=1.8,alpha=.95))
for x in [ROOF_WIDTH*i/6 for i in range(1,6)]: ax2.plot([x,x],[LOW_EAVE,SLOPE_TOP],color="#71898b",lw=.8)
for z in [LOW_EAVE+RISE*i/3 for i in range(1,3)]: ax2.plot([0,ROOF_WIDTH],[z,z],color="#71898b",lw=.8)
ax2.text(ROOF_WIDTH/2,(LOW_EAVE+SLOPE_TOP)/2,"30° SOLAR PLANE\nRISING AWAY TO NORTH",ha="center",va="center",fontsize=9,color="white",fontweight='bold')
# Clerestory window band.
ax2.add_patch(Rectangle((0,SLOPE_TOP),ROOF_WIDTH,CLERESTORY,fc="#bcd6df",ec="#a44533",lw=2))
for x in [ROOF_WIDTH*i/7 for i in range(1,7)]: ax2.plot([x,x],[SLOPE_TOP,CAP_EAVE],color="#a44533",lw=1.1)
ax2.text(ROOF_WIDTH/2,(SLOPE_TOP+CAP_EAVE)/2,"CLERESTORY WINDOWS  •  "+fi(CLERESTORY),ha="center",va="center",fontsize=7.5,color="#713326",fontweight='bold')
# Hip-cap south projection: eave width and shortened E-W ridge.
ridge_x1=(ROOF_WIDTH-CAP_RIDGE_LENGTH)/2; ridge_x2=(ROOF_WIDTH+CAP_RIDGE_LENGTH)/2
ax2.add_patch(Polygon([(0,CAP_EAVE),(ridge_x1,CAP_EAVE+CAP_RISE),(ridge_x2,CAP_EAVE+CAP_RISE),(ROOF_WIDTH,CAP_EAVE)],closed=True,fc="#d9dde0",ec="#252a2e",lw=2))
ax2.plot([ridge_x1,ridge_x2],[CAP_EAVE+CAP_RISE,CAP_EAVE+CAP_RISE],color="#252a2e",lw=2.5)
ax2.text(ROOF_WIDTH/2,CAP_EAVE+CAP_RISE+.35,"HIPPED CAP  •  18″ RISE",ha="center",fontsize=8,color="#183247")
dim_h(ax2,0,ROOF_WIDTH,-.65,"OUTER SOUTH BEAM / SOLAR WIDTH  "+fi(ROOF_WIDTH))
dim_v(ax2,ROOF_WIDTH+.75,SLOPE_TOP,CAP_EAVE,"WINDOW BAND  "+fi(CLERESTORY))
dim_v(ax2,ROOF_WIDTH+1.25,CAP_EAVE,CAP_EAVE+CAP_RISE,"18″ CAP")
ax2.set_title("SOUTH ELEVATION",loc='left',fontsize=13,fontweight='bold',color="#183247",pad=12)

# Dimensional sensitivity table.
ax3=fig.add_subplot(gs[1,1]);ax3.axis('off');ax3.set_title("SOLAR-AREA CHECK",loc='left',fontsize=13,fontweight='bold',color="#183247",pad=10)
rows=[]
for area in [320,325,330]:
    sl=area/ROOF_WIDTH; run=sl*math.cos(math.radians(30)); rise=sl*.5; top=LOW_EAVE+rise; pop=CAP_EAVE-top
    rows.append([f"{area} ft²",fi(sl),fi(run),fi(rise),fi(top),fi(pop)])
cols=["Solar area","Slope length","Plan run","Rise","Slope top","Pop to 8′"]
tbl=ax3.table(cellText=rows,colLabels=cols,loc='upper left',cellLoc='center',colLoc='center',bbox=[0,.48,1,.43])
tbl.auto_set_font_size(False);tbl.set_fontsize(7.5)
for (r,c),cell in tbl.get_celld().items():
    cell.set_edgecolor('#aeb9c0');cell.set_linewidth(.5)
    if r==0:cell.set_facecolor('#183247');cell.get_text().set_color('white');cell.get_text().set_fontweight('bold')
    elif r%2==0:cell.set_facecolor('#f1f4f5')
ax3.text(0,.38,"The 325 ft² version is the cleanest geometric fit:",fontsize=9,fontweight='bold',color="#183247")
ax3.text(0,.30,"• about 12 ft of horizontal run\n• about 6 ft 11 in of rise\n• about 20⅞ in of clerestory to reach an 8 ft loft envelope",
         fontsize=8.4,color="#425466",va='top',linespacing=1.45)
ax3.text(0,.03,"The solar roof begins at the T-SO / south-post line, 5 ft 3 in outside the existing south wall.\n"
         "The hipped cap is shown with an 18 in rise. Roof build-up, structural depths and drainage allowance will reduce clear height unless the cap datum is raised accordingly.",
         fontsize=7.5,color="#59636e",va='bottom',wrap=True)

fig.suptitle("SOUTH-POST SOLAR SLOPE + CLERESTORY + LOW HIP CAP",fontsize=17,fontweight='bold',color="#183247",y=.985)
fig.text(.5,.957,"30° solar plane • 325 ft² central study • 9 ft first-floor ceiling • 8 in floor assembly • 8 ft northern loft envelope",
         ha='center',fontsize=9,color="#59636e")
fig.subplots_adjust(left=.035,right=.985,top=.925,bottom=.04)
fig.savefig(OUT/"south-post-solar-clerestory.png",dpi=190,bbox_inches='tight')
fig.savefig(OUT/"south-post-solar-clerestory.svg",bbox_inches='tight')
with PdfPages(OUT/"south-post-solar-clerestory.pdf") as pdf:pdf.savefig(fig,bbox_inches='tight')
plt.close(fig)

(OUT/"south-post-solar-clerestory.md").write_text(f"""# South-post solar slope study

The current CAD model places the T-SO / outer south post line 63 inches south of the existing south wall. This study starts a 30-degree roof at that post line, at a 9-foot low edge.

For the 325-square-foot central version:

- Full east-west width: {fi(ROOF_WIDTH)}
- Slope length: {fi(SLOPE_LENGTH)}
- Horizontal run: {fi(RUN)}
- Vertical rise: {fi(RISE)}
- Slope top: {fi(SLOPE_TOP)} above grade
- Slope termination: {fi(SLOPE_END_FROM_SOUTH_WALL)} north of the existing south wall
- Loft-floor top: {fi(LOFT_FLOOR)}
- Height above loft at slope top: {fi(SLOPE_TOP-LOFT_FLOOR)}
- Clerestory rise to an 8-foot envelope: {fi(CLERESTORY)}
- Hip-cap eave: {fi(CAP_EAVE)} above grade
- Illustrated hip-cap rise: 1'-6"
""")
print(OUT/"south-post-solar-clerestory.png")
