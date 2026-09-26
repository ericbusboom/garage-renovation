"""Storage cabinets, machines and a crate on the loft, drawn into the viewer.

Everything that stands on the loft floor and has to fit under the roof is
listed once, in ``ITEMS``, and drawn as a plain box with black edges and a
label. Nothing here moves an item to make it fit: each carries its own
clearance in the hover text and in the table under the model, positive if it
clears the rafter soffit above its highest-constrained edge and negative by
the amount it does not.

The loft is the south shelf (one deck from BW to BE since revision 13 of the
beam scheme, framed right through now that the ladder openings are gone), the
three loft bays north of it, and the stair opening west of BWI-2, which since
the stair moved south runs from B-S north to B-1A. The south shelf sits under
the 30 degree solar slope, which is what limits height there; the bays sit
under the flat rafters at z = 225.

To move an item, edit its row. The label is what the owner refers to it by, so
keep the labels and change the positions.
"""
from __future__ import annotations

import math

import plotly.graph_objects as go

import frame as framemod
import existing as EX

# --------------------------------------------------------------------------
# the layout
# --------------------------------------------------------------------------

DECK_T = 0.75                  # 3/4 in. plywood, per the beam-scheme spec
CLERESTORY_Y = 71.0            # the shelf cabinets' fronts, under the glazing
STAIR_EAST = 3.75              # east edge of the stair opening (BWI-2 line)
EAST_FACE = 209.5              # inside face of the east line (HSS4X4 at x = 211.5)
WEST_FACE = -32.0              # inside face of the west line (HSS4X4 at x = -34)
NORTH_FACE = 266.0             # inside face of the north line (HSS4X4 at y = 268)
MIDDLE_POST = 'N-M'            # the post that stands on the loft deck, not on the slab
MIDDLE_POST_X = 88.75          # its line; ``report`` re-reads it and fails if it moves
W3_Y, W4_Y = 185.0, 268.0      # the west wall bay that cabinet 5 stands in

#: The second north-wall post added by ``owner_revisions.add_north_post``: the
#: loading opening is cut to 6 ft and the run from here to W4 is walled. That
#: new wall is the only wall on the loft deep enough to hang a battery on.
#: S3 stands free in the column cabinets 2 and 4 vacated. D1 stood south of
#: it until 2026-09-25, when it moved to the ground floor.
S3_EAST = MIDDLE_POST_X + 2 * 24.0
S3_SOUTH = NORTH_FACE - 90.0

#: The RF-30's table (owner, 2026-09-25): 50 in. across the 24 in. front, the
#: sweep of its travel; 16 deep; 4 thick; underside 36 in. above the floor;
#: front edge 8 in. back from the machine's front face. D1 itself is 24 in.
#: across the front, 36 deep, 72 tall.
D1_W, D1_D, D1_H = 24.0, 36.0, 72.0
D1_TABLE_W, D1_TABLE_D, D1_TABLE_H = 50.0, 16.0, 4.0
D1_TABLE_Z, D1_TABLE_INSET = 36.0, 8.0

NORTH_POST = 'N-M2'
NORTH_POST_X = 16.75
SHED_WALL_T = 5.0              # conceptual infill wall thickness
NEW_WALL_T = 5.0               # conceptual architectural infill thickness
GROUND_FLOOR = '#c6ced3'       # new ground-floor layout outside the old walls

#: The east wall is now stacked three deep, so there are three set-out lines
#: rather than one. Everything on the shelf hangs off them.
EAST_SHELF_X = EAST_FACE - 24.0     # S1 and S2, 24 in. deep on the wall
CRATE_X = EAST_FACE - 26.0          # B1 on its narrow face, 26 in. deep
DUST_X = CRATE_X - 36.0             # DC turned broadside, west of the crate

#: Owner's figure for stored goods, pounds per cubic foot of the item's
#: envelope -- the box and everything in it. Applied to anything without an
#: explicit ``weight``: the cabinets, the shelving and the crate.
#:
#: Note what this density means on its own. Pressure under an item is
#: weight / footprint = density x height, so under this rule the load an item
#: puts on the deck depends only on how tall it is and not at all on its plan
#: size. 12.13 lb/ft3 reaches the 100 psf design live load at 8.24 ft of
#: stacking; nothing here is taller than 7.5 ft.
STORAGE_DENSITY = 12.13

#: label, kind, width (east-west), depth (north-south), height, x and y of the
#: south-west corner.  All in inches.
#:
#: 2026-09-19 layout, eighth pass -- the walkway now decides where things go.
#:
#: Cabinets 1 and 2 have left the N-M post for the clerestory, where they run on
#: rails. S3 holds the column they vacated. Cabinets 3
#: and 4 have been deleted and their numbers retired.
#:
#: Cabinet 5 remains on the west wall in the W3-W4 bay. The Powerwall has moved
#: off that wall to the new shed equipment area.
#:
#: The machines are turned, two 24 in. bodies filling the 48 in. cabinet 5
#: originally occupied. Turned, they are 48 in. deep instead of 24, so they run
#: 24 in. further south than 5 did, into the low space under the slope -- still
#: clearing it by 8.9 in., because what governs is their south edge and that has
#: not moved.
#:
#: The crate B1, unturned (60 in. wide, 36 in. deep), keeps the space east of
#: the machines with its front on the clerestory line; there its back is far
#: enough north to clear the slope.
ITEMS = [
    # 1 and 2 turned: 24 in. across the room, 48 in. into it, backs to the
    # north wall, cabinet 1's west face on the centreline of the post.
    # 1 and 2 turned broadside -- 48 across, 24 deep -- and brought down to the
    # clerestory, backs on the line at y = 71. They run east to west on rails in
    # front of the glazing: 1 sits in the corner where S1, DC and M2 all meet it,
    # 2 immediately west. Their tops are at z = 183.25 and the clerestory sill is
    # at 189.61, so they pass under the glass with 6.4 in. to spare -- which is
    # what makes the sliding idea work at all.
    #
    # The strip they run in is only 24 in. deep: the clerestory at y = 71 and the
    # east walkway run at y = 95. The walkway used to start at 92 and was moved
    # north 3 in. to clear them -- see WALK_CROSS.
    dict(n='1', kind='cabinet', w=48.0, d=24.0, h=72.0,
         x=EAST_SHELF_X - 1 * 48.0, y=CLERESTORY_Y),
    dict(n='2', kind='cabinet', w=48.0, d=24.0, h=72.0,
         x=EAST_SHELF_X - 2 * 48.0, y=CLERESTORY_Y),
    # 5 remains at its previous west-wall location in the W3-W4 bay. The 24 in.
    # strip south of it is now open because the Powerwall moved to the shed.
    dict(n='5', kind='cabinet', w=24.0, d=48.0, h=64.0,
         x=WEST_FACE, y=W3_Y + 24.0),
    # B1 measured properly: 50 long, 26 wide, 46 high. Stood on its narrow face
    # -- 26 across, 50 into the slope -- it goes wholly behind the clerestory,
    # north face exactly on the line at y = 71 and back at y = 21.
    #
    # At y = 21 the rafter soffit is 159.0 and the crate tops out at 157.25, so
    # it clears by 1.75 in. *under a rafter*. It happens also to sit in the last
    # bay before the east wall with 11.9 in. of room to spare, which lifts the
    # clearance to 5.25 -- but nothing depends on that. The previous 36 in. wide
    # placement needed the bay and had only 1.9 in. of lateral slack to get it.
    dict(n='B1', kind='crate', w=26.0, d=50.0, h=46.0,
         x=CRATE_X, y=CLERESTORY_Y - 50.0),
    # The machines sit west of the dust collector, M2 against it. They give up
    # 24 in. of easting to it: turned broadside DC is 36 across and needs the
    # ground between the crate and them. Their south face stays on y = 23, which
    # is what sets their headroom -- moving along the shelf does not change it.
    dict(n='M1', kind='machine', w=24.0, d=48.0, h=40.0,
         x=DUST_X - 2 * 24.0, y=CLERESTORY_Y - 48.0,
         weight=250.0),
    dict(n='M2', kind='machine', w=24.0, d=48.0, h=40.0,
         x=DUST_X - 1 * 24.0, y=CLERESTORY_Y - 48.0,
         weight=250.0),
    # Industrial shelving, 24 deep x 90 long x 90 high, against the east wall.
    #
    # 2026-09-18, fifth pass. Cabinets 1 and 2 used to be jammed into the
    # north-east corner, and their west end stopped the east wall run at
    # y = 242 -- 171 in., nine inches short of a second unit. Sliding the pair
    # west onto the N-M post line frees the wall the whole way to the north
    # face: y 71 to 266, 195 in., which takes two units end to end with 15 in.
    # left over at the south end for access to the crate behind them.
    #
    # The pair lands 0.75 in. clear of the shelving line, which is what makes
    # the alignment work rather than a coincidence: 88.75 + 2 x 48 = 184.75,
    # and the shelving stands at x = 185.5.
    dict(n='S1', kind='shelving', w=24.0, d=90.0, h=90.0,
         x=EAST_SHELF_X, y=NORTH_FACE - 2 * 90.0),
    dict(n='S2', kind='shelving', w=24.0, d=90.0, h=90.0,
         x=EAST_SHELF_X, y=NORTH_FACE - 1 * 90.0),
    # S3, a third unit of the same 24 x 90 x 90, standing free in the column
    # cabinets 2 and 4 vacated. That column is 96 in. long and the unit is 90,
    # so it is set to the north wall and lines up with S2 exactly -- both run
    # y 176 to 266 -- leaving 6 in. of floor at its south end.
    dict(n='S3', kind='shelving', w=24.0, d=90.0, h=90.0,
         x=S3_EAST - 24.0, y=S3_SOUTH),
    # California Air Tools 10020C Ultra Quiet, drawn to the owner's envelope
    # (18 in. across, 36 in. tall) rather than to the real twin-tank machine --
    # no public CAD model exists for it. It follows the dust collector, sitting
    # south of it again now that DC has moved west of the crate.
    dict(n='C1', kind='compressor', shape='cylinder', w=18.0, d=18.0, h=36.0,
         x=DUST_X, y=29.0,
         what='California Air Tools 10020C Ultra Quiet, 10 gal',
         weight=70.0),
    # Dust collector, turned broadside and set west of the crate. Turning it is
    # what makes it fit: 60 in. tall, it needs the roof at 171.25 or higher, and
    # the slope does not reach that until y = 42.2. Left 24 across x 36 deep its
    # north face would then have run to y = 78, seven inches past the clerestory
    # line. Turned 36 across x 24 deep it sits at y = 47 to 71 -- back against
    # the slope, front exactly on the clerestory -- and clears by 2.8 in.
    #
    # SIZE IS ASSUMED: no model was given. A full-height 2 HP bag collector at
    # 78 in. does not go under the slope at all, at any y.
    dict(n='DC', kind='machine', w=36.0, d=24.0, h=60.0,
         x=DUST_X, y=CLERESTORY_Y - 24.0,
         what='dust collector — envelope assumed, 24 × 36 × 60 in.',
         weight=70.0),
    # D1, the Rong Fu RF-30, left the loft on 2026-09-25 for the west wall
    # of the ground floor, north of the lathe. See GROUND_ITEMS.
    # Shapeoko 5 Pro 4x4, west of the machines, wholly under the solar slope.
    # It lives here; it is on wheels and gets rolled north into the room to cut,
    # so this is a parking space and nothing else. Y travel under the slope is
    # not a constraint and is not reasoned about.
    #
    # Drawn as two boxes because that is its actual shape. Carbide's own side
    # elevation shows a low rail over most of the Y length with the gantry --
    # the whole 23.25 in. of the published 60 x 59 x 23.25 envelope -- standing
    # at one end of it. A single box would be 23 in. tall over ground that is
    # mostly 7 in. tall, and would report hitting a roof it does not touch.
    #
    # The gantry parks at the NORTH end, where the slope has risen. Parked, the
    # bed is what governs and the bed is low:
    #
    #   south edge y = 12   headroom 42.55   bed 7 + stand 30 = 37   5.55 spare
    #   gantry face y = 58  headroom 69.11   23.25 + 30 = 53.25     15.86 spare
    #
    # Those 5.55 in. are the caster budget. Casters raise the whole machine, and
    # the bed at the south end is the first thing to touch: a stand of 34 in.
    # still parks, 36 in. only parks a foot further north, and past that it does
    # not go under at all.
    #
    # Rolling out: 15.5 in. north puts the gantry far enough up the slope for
    # the full 48.7 in. of travel, at which point the machine sits y 27.5 to
    # 86.5 -- clear of every other item, clear of every walkway tile, and 8.5
    # in. short of the east walkway run. A taller stand needs a longer pull and
    # runs out of room: 34 in. needs 22.5 and leaves 1.5 in., 36 in. does not
    # fit in front of the walkway at all.
    #
    # BED AND STAND HEIGHTS ARE ASSUMED: 7 in. scaled off the Carbide side
    # elevation, 30 in. for a shop-built rolling stand. Weights are assumed too
    # -- the five shipping boxes total 288 lb, so 400 is the machine plus stand.
    dict(n='CNC', kind='machine', w=60.0, d=46.0, h=37.0,
         x=STAIR_EAST, y=CLERESTORY_Y - 59.0, weight=300.0,
         what='Shapeoko 5 Pro 4x4 bed, parked; 30 in. rolling stand'),
    dict(n='CNCg', kind='machine', w=60.0, d=13.0, h=53.25,
         x=STAIR_EAST, y=CLERESTORY_Y - 13.0, weight=100.0,
         what='Shapeoko gantry, parked at the north end'),
]

#: Equipment on the shed walls. ``along`` is measured from the west end of a
#: north/south wall or the south end of the east wall. The rack envelope
#: is intentionally an assumption: 12U gives 21 in. of rail height, represented
#: here by a 24 in. tall cabinet, and the owner selected the shallow 14 in. depth.
SHED_ITEMS = [
    # 2026-09-25 (owner): the Powerwall hangs on the east wall at its south
    # end, against the south wall, facing west; back at its old 12 in. mounting
    # height now that nothing stands under it.
    dict(n='PW', kind='battery', wall='east', along=SHED_WALL_T,
         width=24.0, depth=7.6, h=43.5, z=12.0,
         what='Tesla Powerwall 3 · 291 lb · east wall, south end'),
    dict(n='EP', kind='electrical', wall='north', along=18.5,
         width=16.0, depth=5.0, h=30.0, z=48.0,
         what='100 A electrical panel · conceptual 16 × 5 × 30 in. envelope'),
    # 2026-09-25 (owner): the separate sprinkler cabinet is gone; its
    # equipment goes in the rack, which takes the cabinet's place on the north
    # wall, centred where the 18 in. cabinet was, top at 78 in. with the panels.
    dict(n='RACK', kind='rack', wall='north', along=40.5 - 2.0,
         width=22.0, depth=14.0, h=24.0, z=54.0,
         what='wall-mounted 19 in. rack · conceptual 12U · 14 in. deep · '
              'houses the sprinkler equipment'),
    dict(n='WH', kind='water_heater', wall='floor', corner='northeast',
         width=20.0, depth=20.0, h=29.0, z=0.0, shape='cylinder',
         what='15 gal electric water heater · 20 in. diameter × 29 in. high'),
]

# The original first-floor cabinet study recorded four one-inch frame stations
# around three 48-inch paired-door bays.  The owner has since decided that the
# built-ins have no structural role, so only their architectural envelopes are
# carried into this viewer.  In particular, these are deliberately separate
# from ``ITEMS`` (which drives loft loads) and from the finite-element frame.
FIRST_FLOOR_CABINETS = [
    dict(n=f'GF-C{i + 1}', x0=211.5, x1=241.5,
         y0=a + 0.5, y1=b - 0.5)
    for i, (a, b) in enumerate(zip((56.0, 105.0, 154.0),
                                    (105.0, 154.0, 203.0)))
]
FIRST_FLOOR_CABINET_HEIGHT = 98.5
FIRST_FLOOR_BENCH = 40.0
FIRST_FLOOR_UPPER_SILL = 60.0

LAUNDRY_WIDTH = 58.0
LAUNDRY_DEPTH = 30.0
LAUNDRY_HEIGHT = 66.0
LAUNDRY_JAMB_CLEAR = 4.0

BENCH_HEIGHT = 37.5
BENCH_TOP_T = 1.5
SOUTH_BENCH_DEPTH = 30.0
#: B-W is retired (owner, 2026-09-25): the west wall north of B-S is rolling
#: storage and machines, not a bench. Sizes as (along the wall, off it, high).
CHEST_SIZE = (26.0, 18.0, 58.0)    # Craftsman tool chest, red
HUSKY_SIZE = (46.0, 25.0, 36.0)    # Husky rolling tool cabinet

#: The freestanding tables in the middle of the room (owner, 2026-09-25), all
#: set out from the south door: (east-west, north-south, height).
WOOD_TABLE = (60.0, 36.0, 36.0)    # height assumed
METAL_TABLE = (48.0, 36.0, 36.0)   # height assumed
TABLES_SOUTH = 72.0                # south edges, north of the inside south wall
SAW_ROUTER = (32.0, 77.0, 38.0)    # table saw and router, one unit
SIDE_TABLE = (26.0, 32.0, 38.0)    # north of the saw; height assumed

LATHE_DEPTH = 24.0
LATHE_LENGTH = 57.0
LATHE_DISPLAY_HEIGHT = 48.0       # display envelope only; owner gave no height

#: Tormach PCNC 440 with stand and enclosure, planned from Tormach drawing
#: D35684: 42 x 36 x 72 in., widened to 46 in. for the ATC on the left of the
#: head. It sits in the NW pop-out facing east, with its back to the W3-W4
#: wall and its right side to the W4-N1 wall, TORMACH_WALL_GAP clear of each.
#: The operator faces west, so the left (ATC) side faces south into the open
#: strip along the W3 wall, and the console on the north wall is at the
#: operator's right.
#: Study: studies/20260925.01-tormach-770m-placement/.
TORMACH_WIDTH = 46.0              # along the wall, north-south
TORMACH_DEPTH = 36.0              # out from the wall, east-west
TORMACH_HEIGHT = 72.0
TORMACH_WALL_GAP = 2.0
TORMACH_FRONT = 36.0              # two people at the machine
TORMACH_CONSOLE = (16.0, 4.0, 12.0, 48.0)   # width, depth, height, bottom z

KINDS = {
    'cabinet': dict(face='#d6d8da', label='Cabinet'),      # light grey
    'machine': dict(face='#c9a87c', label='Machine'),      # light brown
    'crate':   dict(face='#b8956a', label='Crate'),        # a shade darker
    'shelving': dict(face='#9ca3aa', label='Shelving'),    # bare steel
    'compressor': dict(face='#5b6a78', label='Compressor'),   # painted steel
    'battery': dict(face='#eceff1', label='Battery'),         # Powerwall white
    'electrical': dict(face='#b9c4cc', label='Electrical panel'),
    'sprinkler': dict(face='#b84a45', label='Sprinkler cabinet'),
    'rack': dict(face='#3f4852', label='Network rack'),
    'water_heater': dict(face='#e7e9eb', label='Water heater'),
    'table': dict(face='#8a6f4d', label='Machine table'),
}
EDGE = '#141618'               # near-black edges so the boxes read as boxes
FLOOR = '#d8c69f'              # plywood
WALL = '#e9e6df'
CONCRETE = '#8f969c'           # exterior shed slab


# --------------------------------------------------------------------------
# what the frame says about the room
# --------------------------------------------------------------------------

def _ends(frame: framemod.Frame, member: str):
    segs = framemod._ordered(frame, [(i, j) for m, i, j in frame.segments
                                     if m == member])
    return frame.xyz(segs[0][0]), frame.xyz(segs[-1][1])


def floor_top(frame: framemod.Frame) -> float:
    """Top of the deck: over the beams' top flanges.

    The joists sit on the beam axis in this model, mid-depth of a W12X16, so
    their tops are 2.4 in. below the beam tops. A deck laid on the joists would
    have every beam standing proud of it; the built condition hangs the joists
    flush with the beam tops and runs the deck over both, so the floor is taken
    at beam top plus the plywood. Clearances under the slope are 2.4 in. tighter
    than they would be with the deck on the joist tops as modelled.
    """
    a, _ = _ends(frame, 'B-1')
    return a[2] + frame.section_of['B-1'].d / 2.0 + DECK_T


def roof_soffit(frame: framemod.Frame):
    """Underside of the rafters as a function of y, and the rafter stations.

    South of the clerestory line the slope rafters govern; north of it the
    flat rafters do. Both sets share the same x stations.
    """
    rs = sorted(m for m in frame.members if m.startswith('RS @'))
    rf = sorted(m for m in frame.members if m.startswith('RF @'))
    a, b = _ends(frame, rs[0])
    d_slope = frame.section_of[rs[0]].d
    slope = (b[2] - a[2]) / (b[1] - a[1])
    y_ct = b[1]
    z_flat = _ends(frame, rf[0])[0][2] - frame.section_of[rf[0]].d / 2.0
    xs = sorted(_ends(frame, m)[0][0] for m in rs)

    def soffit(y: float) -> float:
        if y <= y_ct:
            return a[2] + slope * (y - a[1]) - d_slope / 2.0
        return z_flat
    return soffit, xs, d_slope, slope, y_ct


def item_weight(c: dict) -> tuple[float, str]:
    """Pounds, and where the figure came from.

    An explicit ``weight`` is the owner's figure for a named machine. Anything
    else is stored goods and is taken at ``STORAGE_DENSITY`` times the volume
    of its envelope.
    """
    if 'weight' in c:
        return float(c['weight']), 'given'
    vol = c['w'] * c['d'] * c['h'] / 1728.0
    return vol * STORAGE_DENSITY, 'density'


def footprint_sf(c: dict) -> float:
    """Plan area in square feet; a cylinder sits on its circle, not its box."""
    if c.get('shape') == 'cylinder':
        return math.pi / 4.0 * c['w'] * c['d'] / 144.0
    return c['w'] * c['d'] / 144.0


def deck_area_sf(frame: framemod.Frame) -> float:
    """Loft deck the items and the walkway share, east of BE excluded."""
    east = _ends(frame, 'BE')[0][0] if 'BE' in frame.members else 211.5
    total = 0.0
    for d in frame.decks:
        x0, x1 = sorted(d['x'])
        y0, y1 = sorted(d['y'])
        x1 = min(x1, east)
        if x1 > x0:
            total += (x1 - x0) * (y1 - y0) / 144.0
    return total


#: The two roof planes, each as a member-name test and the edge members that
#: bound it. They are different sections: the slope runs HSS3-1/2 rafters, the
#: flat roof HSS2-1/2, so the depth an item can borrow between them differs.
ROOF_PLANES = {
    False: ('RS @', ('E.slope', 'W.slope')),    # under the solar slope
    True: ('RF @', ('E.top', 'W.top')),         # north of the clerestory
}


def roof_members(frame: framemod.Frame,
                 flat: bool) -> tuple[list[tuple[float, float]], float]:
    """Members of one roof plane as (centreline x, half width), and the depth.

    An item that falls wholly between two of them has the roof *panel* over it.
    The panel sits on top of the rafters, so its underside is one rafter depth
    above their soffit. An item that any of them crosses is stuck with the
    soffit, and the depth it could have borrowed is the depth of that plane's
    rafters -- 3.5 in. on the slope, 2.5 in. on the flat.
    """
    prefix, edges = ROOF_PLANES[flat]
    out, depth = [], 0.0
    for m in frame.members:
        if not (m.startswith(prefix) or m in edges):
            continue
        pts = [frame.xyz(n) for mm, i, j in frame.segments if mm == m for n in (i, j)]
        if not pts:
            continue
        sec = frame.section_of[m]
        out.append((sum(q[0] for q in pts) / len(pts), sec.b / 2.0))
        if m.startswith(prefix):
            depth = sec.d
    return sorted(out), depth


def bay_for(frame: framemod.Frame, x0: float, x1: float, flat: bool):
    """Which members of that roof plane cross x0..x1, and the clear bay.

    Returns (blocked, slack, depth). ``blocked`` lists the centrelines crossing
    the item. ``slack`` is how much narrower the item is than the clear bay when
    nothing crosses it -- the margin such a placement depends on, and it can be
    very small. ``depth`` is what the item may borrow if it is clear.
    """
    members, depth = roof_members(frame, flat)
    blocked = [x for x, hw in members if x0 - hw < x < x1 + hw]
    if blocked:
        return blocked, None, depth
    west = max((x + hw for x, hw in members if x + hw <= x0), default=None)
    east = min((x - hw for x, hw in members if x - hw >= x1), default=None)
    if west is None or east is None:
        return blocked, None, depth
    return blocked, (east - west) - (x1 - x0), depth


def middle_post_x(frame: framemod.Frame) -> float | None:
    """The x of the post that stands on the loft deck rather than on the slab."""
    if MIDDLE_POST not in frame.members:
        return None
    return _ends(frame, MIDDLE_POST)[0][0]


def report(frame: framemod.Frame) -> list[dict]:
    """One row per item: where it is and what it hits.

    Cabinets 1 and 2 are placed against a post line rather than a wall, so the
    line is re-read from the frame every run. A layout that quietly stops
    lining up with the thing it was aligned to is worse than one that fails.
    """
    post = middle_post_x(frame)
    if post is not None and abs(post - MIDDLE_POST_X) > 0.5:
        raise ValueError(
            f'{MIDDLE_POST} has moved to x = {post:g}; cabinets 1 and 2 are '
            f'placed on MIDDLE_POST_X = {MIDDLE_POST_X:g} in cabinets.py')
    z0 = floor_top(frame)
    soffit, rafter_x, depth, slope, y_ct = roof_soffit(frame)
    rows = []
    for c in ITEMS:
        x0, x1 = c['x'], c['x'] + c['w']
        y0, y1 = c['y'], c['y'] + c['d']
        base = z0 + c.get('z', 0.0)          # 0 for anything standing on the deck
        top = base + c['h']
        # The roof is lowest over whichever edge is furthest south. What is
        # over it there depends on where it sits across the building: under a
        # rafter it is the rafter soffit, between rafters it is the panel, one
        # rafter depth higher.
        y_low = y0
        blocked, slack, borrow = bay_for(frame, x0, x1, y_low > y_ct)
        head = soffit(y_low) + (0.0 if blocked else borrow)
        clear = head - top
        under = [x for x in rafter_x if x0 - 1.75 <= x <= x1 + 1.75]
        # how far north the item would have to move for that edge to clear
        shift = max(0.0, -clear) / slope if (clear < 0 and y_low <= y_ct) else None
        lb, source = item_weight(c)
        area = footprint_sf(c)
        rows.append(dict(
            n=c['n'], kind=c['kind'], w=c['w'], d=c['d'], h=c['h'],
            shape=c.get('shape', 'box'), mount=c.get('mount', 'floor'),
            part_of=c.get('part_of'),
            what=c.get('what', ''),
            between_rafters=not blocked,
            bay_slack=round(slack, 2) if slack is not None else None,
            weight=round(lb, 1), weight_source=source,
            area_sf=round(area, 2),
            psf=(round(lb / area, 1) if area and c.get('mount', 'floor') == 'floor'
                 else None),
            x0=x0, x1=x1, y0=y0, y1=y1,
            z0=base, top=top, soffit=round(head, 2),
            clear_in=round(clear, 2), rafters_over=[round(x, 1) for x in under],
            fits=clear >= 0.0,
            shift_north_in=round(shift, 1) if shift is not None else None))
    _check_footprints(rows)
    _check_on_deck(frame, rows)
    _check_walkway(frame, rows)
    return rows


def _check_on_deck(frame: framemod.Frame, rows: list[dict]) -> None:
    """Every item has to stand on floor that exists.

    Nothing else here looks down. The clearance test looks up at the rafters
    and the footprint test looks sideways at the other items, so an item parked
    over the stair opening -- or over the strip the stair used to occupy, or
    east of BE where the lean-to roof is -- would draw, report a cheerful
    clearance, and be standing on air. Cabinet 5 moved to the west side, which
    is where the opening is, so the question is now live.

    The declared decks do not overlap, so an item is fully supported when the
    areas it shares with them add up to its own.
    """
    east = _ends(frame, 'BE')[0][0] if 'BE' in frame.members else 211.5
    for r in rows:
        if r['mount'] != 'floor':
            continue                          # hung on a wall, holds itself up
        area = (r['x1'] - r['x0']) * (r['y1'] - r['y0'])
        on = 0.0
        for d in frame.decks:
            dx0, dx1 = sorted(d['x'])
            dy0, dy1 = sorted(d['y'])
            dx1 = min(dx1, east)               # no floor over the lean-to
            w = min(r['x1'], dx1) - max(r['x0'], dx0)
            h = min(r['y1'], dy1) - max(r['y0'], dy0)
            if w > 0 and h > 0:
                on += w * h
        if on < area - 0.5:
            raise ValueError(
                f'{KINDS[r["kind"]]["label"]} {r["n"]} at x {r["x0"]:g}..'
                f'{r["x1"]:g}, y {r["y0"]:g}..{r["y1"]:g} overhangs the deck by '
                f'{(area - on) / 144.0:.1f} sq ft; edit cabinets.py')


def _check_footprints(rows: list[dict]) -> None:
    """No two items may stand in the same place.

    The roof clearance test looks at one item at a time, so it has nothing to
    say about two boxes occupying the same square foot of deck. With the pair
    of shelving units butted end to end and cabinet 2 finishing 0.75 in. off
    the shelving line, the layout is now tight enough that a future nudge could
    overlap without anything in the drawing objecting.
    """
    for a, b in ((a, b) for i, a in enumerate(rows) for b in rows[i + 1:]):
        if a['n'] == b.get('part_of') or b['n'] == a.get('part_of'):
            continue                          # a machine and its own table
        dx = min(a['x1'], b['x1']) - max(a['x0'], b['x0'])
        dy = min(a['y1'], b['y1']) - max(a['y0'], b['y0'])
        if dx > 0.01 and dy > 0.01:
            raise ValueError(
                f'{KINDS[a["kind"]]["label"]} {a["n"]} and '
                f'{KINDS[b["kind"]]["label"]} {b["n"]} overlap on the deck by '
                f'{dx:.2f} x {dy:.2f} in.; edit cabinets.py')


# --------------------------------------------------------------------------
# meshes
# --------------------------------------------------------------------------

_BOX_FACES = [(0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6),
              (0, 4, 5), (0, 5, 1), (1, 5, 6), (1, 6, 2),
              (2, 6, 7), (2, 7, 3), (3, 7, 4), (3, 4, 0)]


def _box(x0, x1, y0, y1, z0, z1):
    verts = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
             [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]]
    return verts, list(_BOX_FACES)


def _cylinder(x0, x1, y0, y1, z0, z1, n=36):
    """A closed vertical cylinder inscribed in the given footprint."""
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    rx, ry = (x1 - x0) / 2.0, (y1 - y0) / 2.0
    ring = [(cx + rx * math.cos(2 * math.pi * k / n),
             cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]
    verts = ([[x, y, z0] for x, y in ring] + [[x, y, z1] for x, y in ring]
             + [[cx, cy, z0], [cx, cy, z1]])
    lo, hi = 2 * n, 2 * n + 1
    faces = []
    for k in range(n):
        j = (k + 1) % n
        faces.append((lo, j, k))                       # bottom cap
        faces.append((hi, n + k, n + j))               # top cap
        faces.append((k, j, n + j))                    # side
        faces.append((k, n + j, n + k))
    return verts, faces


def _cylinder_edges(x0, x1, y0, y1, z0, z1, n=36, ribs=4):
    """Both rims and a few verticals, as one polyline with breaks."""
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    rx, ry = (x1 - x0) / 2.0, (y1 - y0) / 2.0
    pt = lambda k: (cx + rx * math.cos(2 * math.pi * k / n),
                    cy + ry * math.sin(2 * math.pi * k / n))
    xs, ys, zs = [], [], []
    for z in (z0, z1):
        for k in list(range(n)) + [0]:
            x, y = pt(k)
            xs.append(x), ys.append(y), zs.append(z)
        xs.append(None), ys.append(None), zs.append(None)
    for r in range(ribs):
        x, y = pt(r * n / ribs)
        xs += [x, x, None]
        ys += [y, y, None]
        zs += [z0, z1, None]
    return xs, ys, zs


def _box_edges(x0, x1, y0, y1, z0, z1):
    """The twelve edges as one polyline with breaks, for a Scatter3d."""
    xs, ys, zs = [], [], []
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    for z in (z0, z1):
        for x, y in ring:
            xs.append(x), ys.append(y), zs.append(z)
        xs.append(None), ys.append(None), zs.append(None)
    for x, y in ring[:4]:
        xs += [x, x, None]
        ys += [y, y, None]
        zs += [z0, z1, None]
    return xs, ys, zs


def _slab(poly, offset):
    """A convex planar polygon extruded by ``offset`` (a 3-vector)."""
    n = len(poly)
    verts = [list(p) for p in poly] + [[p[k] + offset[k] for k in range(3)]
                                        for p in poly]
    faces = []
    for i in range(1, n - 1):                  # near face, far face
        faces.append((0, i, i + 1))
        faces.append((n, n + i + 1, n + i))
    for i in range(n):                         # sides
        j = (i + 1) % n
        faces.append((i, j, n + j))
        faces.append((i, n + j, n + i))
    return verts, faces


def _mesh(verts, faces, color, name, hover, opacity=1.0):
    return go.Mesh3d(
        x=[v[0] for v in verts], y=[v[1] for v in verts], z=[v[2] for v in verts],
        i=[f[0] for f in faces], j=[f[1] for f in faces], k=[f[2] for f in faces],
        color=color, opacity=opacity, flatshading=True,
        lighting=dict(ambient=0.66, diffuse=0.8, specular=0.08, roughness=0.95),
        lightposition=dict(x=-8000, y=-12000, z=16000),
        name=name, hovertemplate=hover + '<extra></extra>', showlegend=False,
        visible=False)


def floor_traces(frame: framemod.Frame) -> list:
    """The deck, one slab per deck rectangle, over the beam tops."""
    z1 = floor_top(frame)
    z0 = z1 - DECK_T
    east = _ends(frame, 'BE')[0][0] if 'BE' in frame.members else 211.5
    out = []
    for d in frame.decks:
        x0, x1 = d['x'][0], min(d['x'][1], east)
        if x1 - x0 < 1.0:
            continue                           # SH-E: over the lean-to, no floor
        y0, y1 = d['y']
        v, f = _box(x0, x1, y0, y1, z0, z1)
        out.append(_mesh(v, f, FLOOR, f'floor {d["name"]}',
                         f'<b>Floor — {d["name"]}</b><br>3/4 in. plywood, top at '
                         f'z = {z1:g}<br>{x0:g} → {x1:g} east · {y0:g} → {y1:g} north'))
    return out


def east_wall_traces(frame: framemod.Frame) -> list:
    """A panel on the inhabited east wall line, not the outer lean-to beam."""
    # BE is the outer lean-to beam at x=247.5.  The actual wall is the inner
    # east frame through E.top, E.clerestory, BE.upper and E.W3 at x=211.5.
    wall_members = ('E.top', 'E.clerestory', 'BE.upper', 'E.W3')
    wall_x = {round(p[0], 6) for m in wall_members for p in _ends(frame, m)}
    if len(wall_x) != 1:
        raise ValueError(f'east wall members do not share one x line: {wall_x}')
    x = wall_x.pop()
    z_bot = _ends(frame, 'BE')[0][2]
    y_s = _ends(frame, 'B-S')[0][1]
    y_n = _ends(frame, 'B-N')[0][1]
    (ya, za), (yb, zb) = [(p[1], p[2]) for p in _ends(frame, 'E.slope')]
    z_at = lambda y: za + (zb - za) * (y - ya) / (yb - ya)
    y_ct = yb                                  # the clerestory line
    z_top = _ends(frame, 'E.top')[0][2]
    off = (1.0, 0.0, 0.0)
    south = [(x, y_s, z_bot), (x, y_ct, z_bot), (x, y_ct, z_at(y_ct)), (x, y_s, z_at(y_s))]
    north = [(x, y_ct, z_bot), (x, y_n, z_bot), (x, y_n, z_top), (x, y_ct, z_top)]
    out = []
    for poly, tag in ((south, 'under the slope'), (north, 'to the roof beams')):
        v, f = _slab(poly, off)
        out.append(_mesh(v, f, WALL, f'east wall {tag}',
                         f'<b>East wall</b> on the E.top / E.clerestory / '
                         f'BE.upper / E.W3 line, x = {x:g}<br>{tag}',
                         opacity=0.94))
    return out


def _base_point(frame: framemod.Frame, member: str) -> tuple[float, float, float]:
    """The ground endpoint of a vertical post."""
    ground = [p for p in _ends(frame, member) if abs(p[2]) < 1e-6]
    if len(ground) != 1:
        raise ValueError(f'{member} does not have one ground endpoint: {ground}')
    return ground[0]


def _soffit(frame: framemod.Frame, member: str) -> float:
    """Bottom of a horizontal wall beam."""
    ends = _ends(frame, member)
    z = {round(p[2], 6) for p in ends}
    if len(z) != 1:
        raise ValueError(f'{member} is not horizontal: {z}')
    return z.pop() - frame.section_of[member].d / 2.0


def ground_floor_layout_traces(frame: framemod.Frame) -> list:
    """New ground-floor footprint outside the existing building envelope."""
    w3 = _base_point(frame, 'W3')
    w4 = _base_point(frame, 'W4')
    en2 = _base_point(frame, 'E-N2')
    slabs = [
        ('west addition', (w4[0], 0.0, w3[1], w4[1], -0.3, 0.0)),
        ('north addition', (0.0, en2[0], EX.L, en2[1], -0.3, 0.0)),
    ]
    out = []
    for name, bounds in slabs:
        v, f = _box(*bounds)
        out.append(_mesh(v, f, GROUND_FLOOR, f'ground floor {name}',
                         f'<b>New ground-floor layout — {name}</b><br>'
                         f'outside the existing building footprint', opacity=0.92))
    return out


def first_floor_cabinet_traces(frame: framemod.Frame) -> list:
    """The cabinet-study built-ins, drawn as nonstructural furniture only."""
    del frame                              # geometry is the cabinet-study set-out
    out = []
    face = KINDS['cabinet']['face']
    for c in FIRST_FLOOR_CABINETS:
        hover = (f'<b>{c["n"]} — first-floor built-in</b><br>'
                 f'48 in. paired-door bay · 30 in. deep<br>'
                 f'lower cabinet 0–{FIRST_FLOOR_BENCH:g} in. · upper cabinet '
                 f'{FIRST_FLOOR_UPPER_SILL:g}–{FIRST_FLOOR_CABINET_HEIGHT:g} in.'
                 f'<br><b>Architectural only — no structural credit</b>')
        for z0, z1, part in ((0.0, FIRST_FLOOR_BENCH, 'lower'),
                             (FIRST_FLOOR_UPPER_SILL,
                              FIRST_FLOOR_CABINET_HEIGHT, 'upper')):
            v, f = _box(c['x0'], c['x1'], c['y0'], c['y1'], z0, z1)
            out.append(_mesh(v, f, face, f'{c["n"]} {part}', hover, opacity=0.95))
            ex, ey, ez = _box_edges(c['x0'], c['x1'], c['y0'], c['y1'], z0, z1)
            out.append(go.Scatter3d(
                x=ex, y=ey, z=ez, mode='lines', line=dict(color=EDGE, width=3),
                hoverinfo='skip', showlegend=False, visible=False,
                name=f'{c["n"]} {part} edges'))
        out.append(go.Scatter3d(
            x=[(c['x0'] + c['x1']) / 2.0], y=[(c['y0'] + c['y1']) / 2.0],
            z=[FIRST_FLOOR_CABINET_HEIGHT + 5.0], mode='text', text=[c['n']],
            textposition='middle center',
            textfont=dict(size=16, color=EDGE, family='Helvetica, Arial'),
            hoverinfo='skip', showlegend=False, visible=False,
            name=f'{c["n"]} label'))
    return out


def first_floor_cabinets_html() -> str:
    """Describe the recovered cabinet study without assigning load capacity."""
    return f"""
<div class="notes">
  <h2>First-floor built-in cabinets</h2>
  <p>The cabinet-layout view restores the three paired-door bays from the
  2026-09-19 cabinet study. Each clear bay is 48 inches wide and nominally
  30 inches deep. The lower cabinets rise to {FIRST_FLOOR_BENCH:g} inches;
  the upper cabinets run from {FIRST_FLOOR_UPPER_SILL:g} to
  {FIRST_FLOOR_CABINET_HEIGHT:g} inches, leaving the open work zone shown in
  the study elevation.</p>
  <p><b>These cabinets are architectural furniture only.</b> They are not
  members of the analysis model, carry no building loads, and receive no
  structural credit. Their frame stations, rail heights and overall height
  remain study assumptions to be checked in the building.</p>
</div>
"""


def _laundry_bounds(frame: framemod.Frame) -> tuple[float, float, float, float, float, float]:
    """Laundry cabinet against the inside south wall, east of its door jamb."""
    door_e = _base_point(frame, 'DOOR-E')
    sec = frame.section_of['DOOR-E']
    # The HSS6x2 post has its 2-inch face along the wall; the 6-inch dimension
    # runs through it.  Start four inches beyond the post's east face.
    jamb_east = door_e[0] + min(sec.b, sec.d) / 2.0
    x0 = jamb_east + LAUNDRY_JAMB_CLEAR
    y0 = EX.THICK['south']
    return x0, x0 + LAUNDRY_WIDTH, y0, y0 + LAUNDRY_DEPTH, 0.0, LAUNDRY_HEIGHT


def laundry_console_traces(frame: framemod.Frame) -> list:
    """Washer/dryer console, an architectural item with no structural role."""
    x0, x1, y0, y1, z0, z1 = _laundry_bounds(frame)
    hover = (f'<b>LC — laundry console</b><br>{LAUNDRY_WIDTH:g} wide × '
             f'{LAUNDRY_HEIGHT:g} high × {LAUNDRY_DEPTH:g} in. deep<br>'
             f'inside south wall · faces north<br>{LAUNDRY_JAMB_CLEAR:g} in. '
             f'east of the DOOR-E jamb face<br><b>Architectural only — no '
             f'structural credit</b>')
    v, f = _box(x0, x1, y0, y1, z0, z1)
    out = [_mesh(v, f, '#c8cdd1', 'LC laundry cabinet', hover, opacity=0.72)]
    ex, ey, ez = _box_edges(x0, x1, y0, y1, z0, z1)
    out.append(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines',
                            line=dict(color=EDGE, width=4), hoverinfo='skip',
                            showlegend=False, visible=False, name='LC cabinet edges'))

    # Two equal front openings make the side-by-side arrangement legible. The
    # exact appliance widths and which machine goes on which side are open.
    gap, side, face_t, machine_h = 1.5, 1.5, 0.5, 39.0
    mid = (x0 + x1) / 2.0
    bays = ((x0 + side, mid - gap / 2.0),
            (mid + gap / 2.0, x1 - side))
    for i, (a, b) in enumerate(bays, 1):
        v, f = _box(a, b, y1 - face_t, y1, 1.5, machine_h)
        out.append(_mesh(v, f, '#8fa5b3', f'LC appliance bay {i}',
                         '<b>Laundry appliance bay</b><br>washer/dryer side-by-side'
                         '<br>side assignment and appliance dimensions not specified'))
    out.append(go.Scatter3d(
        x=[(x0 + x1) / 2.0], y=[y1 + 2.0], z=[z1 + 5.0], mode='text',
        text=['LC · W + D'], textposition='middle center',
        textfont=dict(size=16, color=EDGE, family='Helvetica, Arial'),
        hoverinfo='skip', showlegend=False, visible=False, name='LC label'))
    return out


def laundry_console_html(frame: framemod.Frame) -> str:
    """Describe the south-wall laundry-console set-out."""
    x0, x1, y0, y1, _, _ = _laundry_bounds(frame)
    return f"""
<div class="notes">
  <h2>Laundry console</h2>
  <p><b>LC</b> contains the side-by-side washer and dryer on the first floor.
  Its overall cabinet is {LAUNDRY_WIDTH:g} inches wide,
  {LAUNDRY_HEIGHT:g} inches high and {LAUNDRY_DEPTH:g} inches deep. It stands
  against the inside of the south wall, faces north, and runs x = {x0:g} to
  {x1:g}, y = {y0:g} to {y1:g} inches.</p>
  <p>The west cabinet edge is {LAUNDRY_JAMB_CLEAR:g} inches east of the outer
  face of the DOOR-E steel jamb. The two appliance openings are shown equally
  for layout; exact appliance sizes and the washer/dryer side assignment have
  not been specified. The console is architectural only and has no role in the
  structural analysis.</p>
</div>
"""


def _bench_bounds(frame: framemod.Frame) -> dict[str, tuple[float, float, float, float]]:
    """Plan rectangles for the L-shaped south/west first-floor workbench."""
    door_w = _base_point(frame, 'DOOR-W')
    sec = frame.section_of['DOOR-W']
    jamb_west = door_w[0] - min(sec.b, sec.d) / 2.0
    x_wall = EX.THICK['west']
    y_wall = EX.THICK['south']
    south = (x_wall, jamb_west, y_wall, y_wall + SOUTH_BENCH_DEPTH)
    return dict(south=south)


def _husky_bounds(frame: framemod.Frame) -> tuple[float, float, float, float]:
    """The Husky, back to the west wall, abutting B-S's north face."""
    run, depth, _ = HUSKY_SIZE
    x0 = EX.THICK['west']
    y0 = _bench_bounds(frame)['south'][3]
    return (x0, x0 + depth, y0, y0 + run)


def _ground_items(frame: framemod.Frame) -> list[dict]:
    """Loose ground-floor furniture and machines, set out from walls and door.

    Each row: n, what, x0, x1, y0, y1, z0, z1, color, and part_of for a part
    that may overlap its parent (D1's table) but nothing else.
    """
    rows = []

    def add(n, what, b, z0, z1, color, part_of=None):
        rows.append(dict(n=n, what=what, x0=b[0], x1=b[1], y0=b[2], y1=b[3],
                         z0=z0, z1=z1, color=color, part_of=part_of))

    x_wall = EX.THICK['west']
    y_wall = EX.THICK['south']
    # CHEST in the niche: the NW pop-out south of the Tormach, back to the
    # W3-W4 wall and south end on the W3 infill wall, drawers facing east.
    w3 = _base_point(frame, 'W3')
    run, depth, h = CHEST_SIZE
    cx0 = w3[0] + NEW_WALL_T / 2.0
    cy0 = w3[1] + NEW_WALL_T / 2.0
    add('CHEST', 'Craftsman tool chest · faces east', (cx0, cx0 + depth, cy0, cy0 + run),
        0.0, h, '#b23a32')
    add('HUSKY', 'Husky rolling tool cabinet', _husky_bounds(frame), 0.0, HUSKY_SIZE[2],
        '#e0782a')
    # D1 north of the lathe, back to the west wall, facing east. Its table
    # runs north-south across the front and sweeps 13 in. past the body each
    # way, so the body stands 13 in. off the lathe and the table's south end
    # just meets it.
    lathe = _lathe_bounds(frame)
    reach = (D1_TABLE_W - D1_W) / 2.0
    dy0 = lathe[3] + reach
    d1 = (x_wall, x_wall + D1_D, dy0, dy0 + D1_W)
    add('D1', 'Rong Fu RF-30 mill/drill on a stand · faces east', d1, 0.0, D1_H, '#c9a87c')
    tx1 = d1[1] - D1_TABLE_INSET
    add('D1-T', 'RF-30 table · 50 in. travel envelope × 16 × 4',
        (tx1 - D1_TABLE_D, tx1, dy0 - reach, dy0 + D1_W + reach),
        D1_TABLE_Z, D1_TABLE_Z + D1_TABLE_H, '#8a6f4d', part_of='D1')
    # Tables set out from the south door: the wood and metal tables meet on
    # the door's centre line, south edges TABLES_SOUTH off the inside wall.
    door = next(o for o in EX.openings('south') if o[2] == 0.0)
    mid = (door[0] + door[1]) / 2.0
    ty0 = y_wall + TABLES_SOUTH
    w, d, h = WOOD_TABLE
    add('WOOD', 'wood table · height assumed', (mid - w, mid, ty0, ty0 + d), 0.0, h, '#b98a55')
    w, d, h = METAL_TABLE
    add('METAL', 'metal table · height assumed', (mid, mid + w, ty0, ty0 + d), 0.0, h, '#8e979e')
    # Saw/router and its side table, west edges on the door's east jamb, run
    # south from the north wall: side table first, then the saw.
    north = _base_point(frame, 'W4')[1] - NEW_WALL_T / 2.0
    sw, sd, sh = SAW_ROUTER
    tw, td, th = SIDE_TABLE
    sx0 = door[1]
    add('SIDE', 'side table north of the saw · height assumed',
        (sx0 + (sw - tw) / 2.0, sx0 + (sw + tw) / 2.0, north - td, north), 0.0, th, '#b98a55')
    add('SAW', 'table saw and router, one unit', (sx0, sx0 + sw, north - td - sd, north - td),
        0.0, sh, '#6d7f8c')
    _check_ground(frame, rows)
    return rows


def _check_ground(frame: framemod.Frame, rows: list[dict]) -> None:
    """No two ground-floor pieces in the same place, fixed ones included."""
    fixed = [dict(n='B-S', b=_bench_bounds(frame)['south']),
             dict(n='LATHE', b=_lathe_bounds(frame)[:4]),
             dict(n='TORMACH', b=_tormach_bounds(frame)['machine'][:4]),
             dict(n='LAUNDRY', b=_laundry_bounds(frame)[:4])]
    fixed += [dict(n=c['n'], b=(c['x0'], c['x1'], c['y0'], c['y1']))
              for c in FIRST_FLOOR_CABINETS]
    boxes = [dict(n=r['n'], b=(r['x0'], r['x1'], r['y0'], r['y1']),
                  part_of=r['part_of']) for r in rows] + fixed
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if a['n'] == b.get('part_of') or b['n'] == a.get('part_of'):
                continue
            dx = min(a['b'][1], b['b'][1]) - max(a['b'][0], b['b'][0])
            dy = min(a['b'][3], b['b'][3]) - max(a['b'][2], b['b'][2])
            if dx > 0.01 and dy > 0.01:
                raise ValueError(f'ground floor: {a["n"]} and {b["n"]} overlap by '
                                 f'{dx:.2f} x {dy:.2f} in.; edit cabinets.py')


def bench_traces(frame: framemod.Frame) -> list:
    """The south bench and the loose ground-floor furniture and machines."""
    out = []
    for u in _ground_items(frame):
        x0, x1, y0, y1, z0, z1 = u['x0'], u['x1'], u['y0'], u['y1'], u['z0'], u['z1']
        hover = (f'<b>{u["n"]} · {u["what"]}</b><br>{x1 - x0:g} E–W × {y1 - y0:g} N–S × '
                 f'{z1 - z0:g} in. high, z {z0:g} → {z1:g}<br>'
                 f'x {x0:g} → {x1:g} · y {y0:g} → {y1:g}')
        v, f = _box(x0, x1, y0, y1, z0, z1)
        out.append(_mesh(v, f, u['color'], u['n'], hover, opacity=0.95))
        ex, ey, ez = _box_edges(x0, x1, y0, y1, z0, z1)
        out.append(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines',
                                line=dict(color=EDGE, width=3), hoverinfo='skip',
                                showlegend=False, visible=False,
                                name=u['n'] + ' edges'))
        if u['part_of']:
            continue
        out.append(go.Scatter3d(
            x=[(x0 + x1) / 2.0], y=[(y0 + y1) / 2.0], z=[z1 + 4.0],
            mode='text', text=[u['n']], textposition='middle center',
            textfont=dict(size=15, color=EDGE, family='Helvetica, Arial'),
            hoverinfo='skip', showlegend=False, visible=False,
            name=u['n'] + ' label'))
    for key, label in (('south', 'B-S · south-wall bench'),):
        x0, x1, y0, y1 = _bench_bounds(frame)[key]
        detail = (f'{x1 - x0:g} in. run · {SOUTH_BENCH_DEPTH:g} in. deep · '
                  f'ends at west face of DOOR-W jamb')
        hover = (f'<b>{label}</b><br>{detail}<br>top z = {BENCH_HEIGHT:g} in.'
                 f'<br>architectural envelope · construction unspecified')
        v, f = _box(x0, x1, y0, y1, 0.0, BENCH_HEIGHT - BENCH_TOP_T)
        out.append(_mesh(v, f, '#aeb4b8', label + ' base', hover, opacity=0.38))
        v, f = _box(x0, x1, y0, y1,
                    BENCH_HEIGHT - BENCH_TOP_T, BENCH_HEIGHT)
        out.append(_mesh(v, f, '#a46f3e', label + ' top', hover, opacity=0.98))
        ex, ey, ez = _box_edges(x0, x1, y0, y1, 0.0, BENCH_HEIGHT)
        out.append(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines',
                                line=dict(color=EDGE, width=3), hoverinfo='skip',
                                showlegend=False, visible=False,
                                name=label + ' edges'))
        out.append(go.Scatter3d(
            x=[(x0 + x1) / 2.0], y=[(y0 + y1) / 2.0],
            z=[BENCH_HEIGHT + 4.0], mode='text',
            text=['B-S'],
            textposition='middle center',
            textfont=dict(size=15, color=EDGE, family='Helvetica, Arial'),
            hoverinfo='skip', showlegend=False, visible=False,
            name=label + ' label'))
    return out


def benches_html(frame: framemod.Frame) -> str:
    """Describe the south bench and the loose ground-floor items."""
    south = _bench_bounds(frame)['south']
    window_clear = EX.PARAMS['window_sill'] - BENCH_HEIGHT
    body = ''.join(
        f'<tr><td><b>{u["n"]}</b></td><td>{u["what"]}</td>'
        f'<td>{u["x1"] - u["x0"]:g} × {u["y1"] - u["y0"]:g} × {u["z1"] - u["z0"]:g}</td>'
        f'<td>x {u["x0"]:g}–{u["x1"]:g}, y {u["y0"]:g}–{u["y1"]:g}, z {u["z0"]:g}–{u["z1"]:g}</td></tr>'
        for u in _ground_items(frame))
    return f"""
<div class="notes">
  <h2>South bench and ground-floor layout</h2>
  <p><b>B-S</b> is {BENCH_HEIGHT:g} inches high and
  {SOUTH_BENCH_DEPTH:g} inches deep. It runs along the inside south wall from
  x = {south[0]:g} at the west wall to x = {south[1]:g}, the outer west face
  of the DOOR-W steel jamb. Its top is {window_clear:g} inches below the
  48-inch window sills.</p>
  <p>Up the west wall from B-S: HUSKY, the lathe, then D1 with its table
  sweeping north–south across its front. The tool chest stands in the niche
  south of the Tormach. The wood and metal tables meet on the south door's
  centre line, 6 ft north of the south wall; the saw/router unit and its side
  table line up on the door's east jamb and run south from the north wall.
  Dimensions are E–W × N–S × height, in inches.</p>
  <table style="border-collapse:collapse;font-size:13px">
    <tr style="text-align:left"><th></th><th></th><th>size</th><th>where</th></tr>
    {body}
  </table>
  <p><small>Layout envelopes only; none of these participates in the
  structural analysis.</small></p>
</div>
"""


def _lathe_bounds(frame: framemod.Frame) -> tuple[float, float, float, float, float, float]:
    """Lathe footprint, back to the west wall, abutting the Husky's north end."""
    x0 = EX.THICK['west']
    y0 = _husky_bounds(frame)[3]
    return (x0, x0 + LATHE_DEPTH, y0, y0 + LATHE_LENGTH,
            0.0, LATHE_DISPLAY_HEIGHT)


def lathe_traces(frame: framemod.Frame) -> list:
    """West-wall lathe envelope, north of the Husky."""
    x0, x1, y0, y1, z0, z1 = _lathe_bounds(frame)
    hover = (f'<b>LATHE — west-wall equipment</b><br>{LATHE_LENGTH:g} in. long × '
             f'{LATHE_DEPTH:g} in. out from wall<br>y {y0:g} → {y1:g}, abutting HUSKY'
             f'<br>height shown as {LATHE_DISPLAY_HEIGHT:g} in. for display only')
    v, f = _box(x0, x1, y0, y1, z0, z1)
    out = [_mesh(v, f, '#657783', 'LATHE envelope', hover, opacity=0.82)]
    ex, ey, ez = _box_edges(x0, x1, y0, y1, z0, z1)
    out.append(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines',
                            line=dict(color=EDGE, width=4), hoverinfo='skip',
                            showlegend=False, visible=False, name='LATHE edges'))
    out.append(go.Scatter3d(
        x=[(x0 + x1) / 2.0], y=[(y0 + y1) / 2.0], z=[z1 + 4.0],
        mode='text', text=['LATHE'], textposition='middle center',
        textfont=dict(size=15, color=EDGE, family='Helvetica, Arial'),
        hoverinfo='skip', showlegend=False, visible=False, name='LATHE label'))
    return out


def lathe_html(frame: framemod.Frame) -> str:
    """Describe the west-wall lathe placement and its one display assumption."""
    x0, x1, y0, y1, _, _ = _lathe_bounds(frame)
    return f"""
<div class="notes">
  <h2>West-wall lathe</h2>
  <p><b>LATHE</b> extends {LATHE_DEPTH:g} inches east from the inside west-wall
  face and runs {LATHE_LENGTH:g} inches north, from y = {y0:g} to {y1:g},
  abutting the Husky cabinet to its south.</p>
  <p>The owner supplied the plan dimensions but no height, so the
  3D view uses a {LATHE_DISPLAY_HEIGHT:g}-inch-high display envelope. Confirm
  the actual machine and stand height before checking the window or services.
  The lathe is equipment only and does not participate in the structural
  analysis.</p>
</div>
"""


def _tormach_bounds(frame: framemod.Frame) -> dict:
    """Machine, operator zone and console boxes, set out from W3/W4 and the walls."""
    w4 = _base_point(frame, 'W4')
    west_face = w4[0] + NEW_WALL_T / 2.0
    north_face = w4[1] - NEW_WALL_T / 2.0
    x0 = west_face + TORMACH_WALL_GAP
    x1 = x0 + TORMACH_DEPTH
    y1 = north_face - TORMACH_WALL_GAP
    y0 = y1 - TORMACH_WIDTH
    cw, cd, ch, cz = TORMACH_CONSOLE
    return dict(machine=(x0, x1, y0, y1, 0.0, TORMACH_HEIGHT),
                operator=(x1, x1 + TORMACH_FRONT, y0, y1),
                console=(x1 + 2.0, x1 + 2.0 + cw, north_face - cd, north_face,
                         cz, cz + ch))


def tormach_traces(frame: framemod.Frame) -> list:
    """The PCNC 440 envelope, its wall console and the operator standing zone."""
    b = _tormach_bounds(frame)
    x0, x1, y0, y1, z0, z1 = b['machine']
    hover = (f'<b>TORMACH PCNC 440</b> with stand and enclosure<br>'
             f'{TORMACH_WIDTH:g} × {TORMACH_DEPTH:g} × {TORMACH_HEIGHT:g} in. '
             f'(42 in. + ATC allowance) · about 600 lb<br>faces east; back and right '
             f'side {TORMACH_WALL_GAP:g} in. off the W3–W4 and W4–N1 walls; '
             f'ATC side faces south')
    v, f = _box(x0, x1, y0, y1, z0, z1)
    out = [_mesh(v, f, '#5f8f7e', 'TORMACH 440 envelope', hover, opacity=1.0)]
    ex, ey, ez = _box_edges(x0, x1, y0, y1, z0, z1)
    out.append(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines',
                            line=dict(color=EDGE, width=4), hoverinfo='skip',
                            showlegend=False, visible=False, name='TORMACH edges'))
    ox0, ox1, oy0, oy1 = b['operator']
    v, f = _box(ox0, ox1, oy0, oy1, 0.0, 0.3)
    out.append(_mesh(v, f, '#bfe3d4', 'TORMACH operator zone',
                     f'<b>Tormach operator zone</b><br>{TORMACH_FRONT:g} in. in front '
                     f'of the machine, room for two', opacity=0.7))
    v, f = _box(*b['console'])
    out.append(_mesh(v, f, '#d9b36a', 'TORMACH console',
                     '<b>Tormach console</b><br>wall-mounted on the W4–N1 wall at '
                     'the operator\'s right', opacity=0.95))
    out.append(go.Scatter3d(
        x=[(x0 + x1) / 2.0], y=[(y0 + y1) / 2.0], z=[z1 + 4.0],
        mode='text', text=['TORMACH 440'], textposition='middle center',
        textfont=dict(size=15, color=EDGE, family='Helvetica, Arial'),
        hoverinfo='skip', showlegend=False, visible=False, name='TORMACH label'))
    return out


def tormach_html(frame: framemod.Frame) -> str:
    """Describe the Tormach placement."""
    b = _tormach_bounds(frame)
    x0, x1, y0, y1, _, _ = b['machine']
    return f"""
<div class="notes">
  <h2>Tormach PCNC 440</h2>
  <p>The mill stands in the northwest pop-out, facing east. Its back is
  {TORMACH_WALL_GAP:g} inches off the W3–W4 wall and its right side
  {TORMACH_WALL_GAP:g} inches off the W4–N1 wall; the left (ATC) side faces
  south into the open strip along the W3 wall: x = {x0:g} to {x1:g},
  y = {y0:g} to {y1:g}. The {TORMACH_WIDTH:g} × {TORMACH_DEPTH:g} × {TORMACH_HEIGHT:g}
  inch envelope is Tormach's 42 × 36 × 72 inch space-planning footprint
  (drawing D35684), widened 4 inches for the ATC. Confirm that allowance against the drawing before
  building. The operator zone runs {TORMACH_FRONT:g} inches east, to
  x = {x1 + TORMACH_FRONT:g}, and the console hangs on the north wall at the
  operator's right. The machine is about 600 pounds on the slab and does not load
  the frame.</p>
</div>
"""


def new_wall_traces(frame: framemod.Frame) -> list:
    """Owner-requested infill walls around the north and west additions."""
    w3 = _base_point(frame, 'W3')
    w4 = _base_point(frame, 'W4')
    n1 = _base_point(frame, 'N1')
    n2 = _base_point(frame, 'N2')
    en2 = _base_point(frame, 'E-N2')
    t = NEW_WALL_T / 2.0
    walls = [
        ('E-N2 south to existing building',
         (en2[0] - t, en2[0] + t, EX.L, en2[1], 0.0, _soffit(frame, 'BE'))),
        ('N2 to E-N2',
         (n2[0], en2[0], en2[1] - t, en2[1] + t, 0.0, _soffit(frame, 'B-N'))),
        ('W4 to N1',
         (w4[0], n1[0], w4[1] - t, w4[1] + t, 0.0, _soffit(frame, 'B-N'))),
        ('W3 to W4',
         (w4[0] - t, w4[0] + t, w3[1], w4[1], 0.0, _soffit(frame, 'BW'))),
        ('W3 east to existing building',
         (w3[0], 0.0, w3[1] - t, w3[1] + t, 0.0, _soffit(frame, 'B-2'))),
    ]
    out = []
    for name, bounds in walls:
        v, f = _box(*bounds)
        out.append(_mesh(v, f, WALL, f'new wall {name}',
                         f'<b>New infill wall — {name}</b><br>{NEW_WALL_T:g} in. '
                         f'conceptual thickness · to underside of steel', opacity=0.78))

    # A second electrical panel, centered in the short north wall between the
    # N2 and E-N2 posts. It faces south into the new floor area.
    width, depth, height, z0 = 16.0, 5.0, 30.0, 48.0
    cx = (n2[0] + en2[0]) / 2.0
    x0, x1 = cx - width / 2.0, cx + width / 2.0
    y1 = en2[1] - t
    y0 = y1 - depth
    v, f = _box(x0, x1, y0, y1, z0, z0 + height)
    out.append(_mesh(v, f, KINDS['electrical']['face'], 'north wall EP-N',
                     '<b>Electrical panel EP-N</b><br>between N2 and E-N2 · faces south'
                     '<br>conceptual 16 × 5 × 30 in. envelope<br>bottom z = 48 · top z = 78'))
    ex, ey, ez = _box_edges(x0, x1, y0, y1, z0, z0 + height)
    out.append(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines',
                            line=dict(color=EDGE, width=4), hoverinfo='skip',
                            showlegend=False, visible=False, name='EP-N edges'))
    out.append(go.Scatter3d(x=[cx], y=[y0 - 2.0], z=[z0 + height + 5.0],
                            mode='text', text=['EP-N'], textposition='middle center',
                            textfont=dict(size=18, color=EDGE, family='Helvetica, Arial'),
                            hoverinfo='skip', showlegend=False, visible=False,
                            name='EP-N label'))
    return out


def new_walls_html(frame: framemod.Frame) -> str:
    """Describe the ground-floor architectural overlay."""
    n2, en2 = _base_point(frame, 'N2'), _base_point(frame, 'E-N2')
    clear = en2[0] - n2[0]
    return f"""
<div class="notes">
  <h2>New ground-floor walls</h2>
  <p>The cabinet-layout view now shades the new floor outside the existing
  building and adds five conceptual {NEW_WALL_T:g}-inch infill runs: E-N2 south
  to the existing north wall; N2 to E-N2; W4 to N1; W3 to W4; and W3 east to
  the existing west wall. Electrical panel <b>EP-N</b> is centered in the
  {clear:g}-inch N2–E-N2 wall and faces south.</p>
  <p><small>Wall framing, openings, fire/weather assemblies, panel working
  clearance, feeds and connections remain to be designed.</small></p>
</div>
"""


def _shed_bounds(frame: framemod.Frame) -> tuple[float, float, float, float]:
    """Interior plan bounds: west, east, south, existing-building wall."""
    s1 = _ends(frame, 'S1')
    es2 = _ends(frame, 'E-S2')
    x0 = next(p[0] for p in s1 if abs(p[2]) < 1e-6)
    x1 = next(p[0] for p in es2 if abs(p[2]) < 1e-6)
    y0 = next(p[1] for p in s1 if abs(p[2]) < 1e-6)
    if abs(next(p[1] for p in es2 if abs(p[2]) < 1e-6) - y0) > 1e-6:
        raise ValueError('S1 and E-S2 do not share the shed outer line')
    y1 = 0.0                       # exterior face of the existing south wall
    return min(x0, x1), max(x0, x1), y0, y1


def shed_item_rows(frame: framemod.Frame) -> list[dict]:
    """Resolve wall-relative shed equipment into model coordinates."""
    bx0, bx1, by0, by1 = _shed_bounds(frame)
    rows = []
    for item in SHED_ITEMS:
        if item['wall'] == 'south':
            if item.get('align') == 'east':
                x1 = bx1 - SHED_WALL_T
                x0 = x1 - item['width']
            else:
                x0 = bx0 + item['along']
                x1 = x0 + item['width']
            y0 = by0 + SHED_WALL_T
            y1 = y0 + item['depth']
            faces = 'north'
        elif item['wall'] == 'east':
            x1 = bx1 - SHED_WALL_T
            x0 = x1 - item['depth']
            y0 = by0 + item['along']
            y1 = y0 + item['width']
            faces = 'west'
        elif item['wall'] == 'north':
            x0 = bx0 + item['along']
            x1 = x0 + item['width']
            y1 = by1
            y0 = y1 - item['depth']
            faces = 'south'
        elif item['wall'] == 'floor':
            if item.get('corner') == 'northeast':
                x1 = bx1 - SHED_WALL_T
                x0 = x1 - item['width']
                y1 = by1
                y0 = y1 - item['depth']
            else:
                x0 = bx0 + item['east']
                x1 = x0 + item['width']
                y0 = by0 + item['north']
                y1 = y0 + item['depth']
            faces = 'freestanding'
        else:
            raise ValueError(f'unknown shed wall {item["wall"]!r}')
        row = dict(item, x0=x0, x1=x1, y0=y0, y1=y1,
                   z0=item['z'], top=item['z'] + item['h'], faces=faces)
        if x0 < bx0 - 0.01 or x1 > bx1 + 0.01 or y0 < by0 - 0.01 or y1 > by1 + 0.01:
            raise ValueError(f'shed item {item["n"]} falls outside the shed walls')
        rows.append(row)
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            dx = min(a['x1'], b['x1']) - max(a['x0'], b['x0'])
            dy = min(a['y1'], b['y1']) - max(a['y0'], b['y0'])
            dz = min(a['top'], b['top']) - max(a['z0'], b['z0'])
            if dx > 0.01 and dy > 0.01 and dz > 0.01:
                raise ValueError(f'shed items {a["n"]} and {b["n"]} overlap')
    return rows


def shed_traces(frame: framemod.Frame) -> list:
    """Concrete pad, south/east infill walls, and wall-mounted equipment."""
    x0, x1, y0, y1 = _shed_bounds(frame)
    z0, z1 = -4.0, 0.0            # conceptual four-inch slab at ground datum
    v, f = _box(min(x0, x1), max(x0, x1), y0, y1, z0, z1)
    area = abs((x1 - x0) * (y1 - y0)) / 144.0
    out = [_mesh(v, f, CONCRETE, 'shed concrete pad',
                 f'<b>Shed area — concrete</b><br>S1 to E-S2 · existing south '
                 f'wall to outer line<br>{abs(x1-x0):g} × {abs(y1-y0):g} in. · '
                 f'{area:.1f} sq ft<br>4 in. conceptual slab', opacity=0.96)]

    south_top = _ends(frame, 'B-SO')[0][2] - frame.section_of['B-SO'].d / 2.0
    east_top = _ends(frame, 'BE')[0][2] - frame.section_of['BE'].d / 2.0
    wall_specs = [
        ('south', (x0, x1, y0, y0 + SHED_WALL_T, 0.0, south_top)),
        ('east', (x1 - SHED_WALL_T, x1, y0, y1, 0.0, east_top)),
    ]
    for name, bounds in wall_specs:
        v, f = _box(*bounds)
        out.append(_mesh(v, f, WALL, f'shed {name} wall',
                         f'<b>Shed {name} infill wall</b><br>{SHED_WALL_T:g} in. '
                         f'conceptual thickness · to underside of steel',
                         opacity=0.72))

    rows = shed_item_rows(frame)
    for r in rows:
        kind = KINDS[r['kind']]
        shape = _cylinder if r.get('shape') == 'cylinder' else _box
        v, f = shape(r['x0'], r['x1'], r['y0'], r['y1'], r['z0'], r['top'])
        size = (f'{r["width"]:g} diameter × {r["h"]:g} high'
                if r.get('shape') == 'cylinder' else
                f'{r["width"]:g} wide × {r["depth"]:g} deep × {r["h"]:g} high')
        location = ('on the concrete pad' if r['wall'] == 'floor' else
                    f'on {r["wall"]} shed wall · faces {r["faces"]}')
        hover = (f'<b>{kind["label"]} {r["n"]}</b><br>{r["what"]}<br>{size} in.'
                 f'<br>{location}'
                 f'<br>bottom z = {r["z0"]:g} · top z = {r["top"]:g}')
        out.append(_mesh(v, f, kind['face'], f'shed {r["n"]}', hover))
        edge_shape = _cylinder_edges if r.get('shape') == 'cylinder' else _box_edges
        ex, ey, ez = edge_shape(r['x0'], r['x1'], r['y0'], r['y1'], r['z0'], r['top'])
        out.append(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines',
                                line=dict(color=EDGE, width=4), hoverinfo='skip',
                                showlegend=False, visible=False,
                                name=f'shed {r["n"]} edges'))
    out.append(go.Scatter3d(
        x=[(r['x0'] + r['x1']) / 2 for r in rows],
        y=[(r['y0'] + r['y1']) / 2 for r in rows],
        z=[r['top'] + 5.0 for r in rows], mode='text',
        text=[r['n'] for r in rows], textposition='middle center',
        textfont=dict(size=20, color=EDGE, family='Helvetica, Arial'),
        hoverinfo='skip', showlegend=False, visible=False,
        name='shed equipment labels'))
    return out


def shed_html(frame: framemod.Frame) -> str:
    """Short schedule for the wall-mounted shed equipment."""
    rows = shed_item_rows(frame)
    body = ''.join(
        f'<tr><td><b>{r["n"]}</b></td><td>{KINDS[r["kind"]]["label"]}</td>'
        f'<td>{r["wall"]}</td><td>{r["width"]:g} × {r["depth"]:g} × '
        f'{r["h"]:g} in.</td><td>{r["z0"]:g} → {r["top"]:g}</td>'
        f'<td>{r["what"]}</td></tr>' for r in rows)
    return f"""
<div class="notes">
  <h2>Concrete shed equipment</h2>
  <p>The shed is enclosed on its south and east sides with conceptual
  {SHED_WALL_T:g}-inch infill walls. The 100 A panel and the shallow rack face south from the
  existing building wall at the north side; the rack also houses the
  sprinkler equipment, so there is no separate sprinkler cabinet. The
  15-gallon electric water heater stands on the concrete pad in the northeast
  corner against the east and existing-building walls, and the Powerwall hangs
  on the east wall at its south end, tight to the south wall, facing west.
  The south wall is clear.</p>
  <table style="border-collapse:collapse;font-size:13px">
    <tr style="text-align:left"><th>#</th><th>item</th><th>wall</th>
      <th>width × depth × height</th><th>z</th><th>basis</th></tr>
    {body}
  </table>
  <p><small>The panel and rack envelopes are layout assumptions; confirm the sprinkler equipment fits the rack. Final equipment,
  working clearances, ventilation, weather rating, conduit routes, mounting and
  electrical/plumbing design remain to be selected.</small></p>
</div>
"""


def item_traces(frame: framemod.Frame) -> tuple[list, list[dict]]:
    """Boxes with black edges and a label on each; plus the clearance report."""
    rows = report(frame)
    out = []
    for r in rows:
        x0, x1, y0, y1, z0, z1 = r['x0'], r['x1'], r['y0'], r['y1'], r['z0'], r['top']
        kind = KINDS[r['kind']]
        if r['fits']:
            fit = f'clears the rafter soffit by <b>{r["clear_in"]:g} in.</b>'
        else:
            fit = (f'<b>hits the rafters by {-r["clear_in"]:g} in.</b> at its south '
                   f'top edge')
            if r['shift_north_in']:
                fit += f'<br>would clear if moved {r["shift_north_in"]:g} in. north'
        if r['between_rafters']:
            over = ('<b>no rafter crosses it</b> — the panel is overhead, '
                    f'{r["bay_slack"]:.2f} in. narrower bay than the item is wide'
                    if r['bay_slack'] is not None else 'no rafter crosses it')
        else:
            over = (f'rafters over it at x = '
                    f'{", ".join(f"{x:g}" for x in r["rafters_over"])}')
        size = (f'{r["w"]:g} in. diameter × {r["h"]:g} in. tall'
                if r['shape'] == 'cylinder' else
                f'{r["w"]/12:g} ft × {r["d"]/12:g} ft × {r["h"]:g} in. tall')
        what = f'{r["what"]}<br>' if r['what'] else ''
        stands = ('hung on the wall, bottom at z = {:g}'.format(z0)
                  if r['mount'] == 'wall' else
                  f'on {r["part_of"]}, underside at z = {z0:g}' if r['part_of'] else
                  f'on the deck at z = {z0:g}')
        load = (f'{r["weight"]:,.0f} lb'
                + (f' ({r["weight"]/r["area_sf"]:.0f} psf on {r["area_sf"]:.1f} sq ft)'
                   if r['psf'] is not None else
                   f', included in {r["part_of"]}' if r['part_of'] else ', hung on the wall'))
        hover = (f'<b>{kind["label"]} {r["n"]}</b> · {size}<br>{what}'
                 f'x {x0:g} → {x1:g} · y {y0:g} → {y1:g} · top at z = {z1:g}<br>'
                 f'{load}<br>{stands}<br>{fit}<br>{over}')
        shape = _cylinder if r['shape'] == 'cylinder' else _box
        v, f = shape(x0, x1, y0, y1, z0, z1)
        out.append(_mesh(v, f, kind['face'], f'{r["kind"]} {r["n"]}', hover))
        edges = _cylinder_edges if r['shape'] == 'cylinder' else _box_edges
        ex, ey, ez = edges(x0, x1, y0, y1, z0, z1)
        out.append(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines',
                                line=dict(color=EDGE, width=4),
                                hoverinfo='skip', showlegend=False, visible=False,
                                name=f'{r["kind"]} {r["n"]} edges'))
    out.append(go.Scatter3d(
        x=[(r['x0'] + r['x1']) / 2 for r in rows],
        y=[(r['y0'] + r['y1']) / 2 for r in rows],
        z=[r['top'] + 7.0 for r in rows],
        mode='text', text=[r['n'] for r in rows],
        textposition='middle center',
        textfont=dict(size=22, color=EDGE, family='Helvetica, Arial'),
        hoverinfo='skip', showlegend=False, visible=False, name='item labels'))
    return out, rows


# kept for callers that used the first name
cabinet_traces = item_traces


def _to_clear(r: dict) -> str:
    if r['fits']:
        return ''
    return f'{r["shift_north_in"]:g} in. north' if r['shift_north_in'] else 'cannot, flat roof'


def _size_text(r: dict) -> str:
    if r['shape'] == 'cylinder':
        return f'&#8960;{r["w"]:g} &times; {r["h"]:g} in.'
    return f'{r["w"]/12:g} &times; {r["d"]/12:g} ft &times; {r["h"]:g} in.'


def loads_html(frame: framemod.Frame, rows: list[dict]) -> str:
    """What the stored kit weighs, and what it does to the deck."""
    area = deck_area_sf(frame)
    on_floor = [r for r in rows if r['mount'] == 'floor']
    w_floor = sum(r['weight'] for r in on_floor)
    design = 100.0
    worst = max(on_floor, key=lambda r: r['psf'])
    body = ''.join(
        f'<tr><td><b>{r["n"]}</b></td><td>{KINDS[r["kind"]]["label"]}</td>'
        f'<td style="text-align:right">{r["h"]:g} in.</td>'
        f'<td style="text-align:right">{r["weight"]:,.0f} lb</td>'
        f'<td>{"given" if r["weight_source"] == "given" else "density"}</td>'
        f'<td style="text-align:right">{r["area_sf"]:.2f}</td>'
        f'<td style="text-align:right">'
        f'{f"{r[chr(112)+chr(115)+chr(102)]:.1f}" if r["psf"] is not None else "&mdash;"}</td></tr>'
        for r in sorted(rows, key=lambda r: -r['weight']))
    return f"""
<div class="notes">
  <h2>Stored load</h2>
  <p>Machines are at their stated weights. Everything else —
  cabinets, shelving, the crate — is stored goods at
  <b>{STORAGE_DENSITY:g}&nbsp;lb per cubic foot</b> of its envelope.</p>
  <table style="border-collapse:collapse;font-size:13px">
    <tr style="text-align:left"><th>#</th><th></th><th>height</th><th>weight</th>
        <th>from</th><th>sq&nbsp;ft</th><th>psf</th></tr>
    {body}
    <tr style="border-top:2px solid #888;font-weight:bold">
      <td colspan="3">on the deck</td>
      <td style="text-align:right">{w_floor:,.0f} lb</td><td></td>
      <td style="text-align:right">{area:.0f}</td>
      <td style="text-align:right">{w_floor / area:.1f}</td></tr>
  </table>
  <p><b>{w_floor:,.0f} lb over {area:.0f} sq ft of deck — an average of
  {w_floor / area:.1f} psf, {100 * w_floor / (design * area):.0f}% of the
  {design:g} psf the loft is designed for.</b> The design live load corresponds
  to {design * area / 1000:,.1f} kip on this deck; the stored kit is
  {w_floor / 1000:.1f}.</p>
  <p>The average is not the test, though. Under the density rule the pressure an
  item puts on the deck is <i>density &times; height</i> — its plan size cancels
  — so it depends only on how tall the item is. That makes
  <b>{worst['n']}</b> the worst at <b>{worst['psf']:.1f} psf</b>, and puts the
  {STORAGE_DENSITY:g}&nbsp;lb/ft&sup3; ceiling at
  <b>{design / STORAGE_DENSITY:.2f} ft</b> of stacking: anything taller than
  that exceeds {design:g} psf locally however small its footprint. Nothing here
  is over 7.5&nbsp;ft.</p>
</div>
"""


def legend_html(rows: list[dict]) -> str:
    tr = ''.join(
        f'<tr><td><b>{r["n"]}</b></td>'
        f'<td>{KINDS[r["kind"]]["label"]}'
        f'{"<br><small>" + r["what"] + "</small>" if r["what"] else ""}</td>'
        f'<td>{_size_text(r)}'
        f'{" · wall mounted" if r["mount"] == "wall" else ""}</td>'
        f'<td>{r["x0"]:g} → {r["x1"]:g}</td>'
        f'<td>{r["y0"]:g} → {r["y1"]:g}</td><td>{r["top"]:g}</td>'
        f'<td style="color:{"#2e7d32" if r["fits"] else "#c1292e"}">'
        f'{"clears by" if r["fits"] else "hits by"} {abs(r["clear_in"]):g} in.</td>'
        f'<td>{_to_clear(r)}</td>'
        f'<td>{f"between, {r[chr(98)+chr(97)+chr(121)+chr(95)+chr(115)+chr(108)+chr(97)+chr(99)+chr(107)]:.1f} in. slack" if r["between_rafters"] and r["bay_slack"] is not None else "under a rafter"}</td>'
        f'</tr>'
        for r in rows)
    z0 = rows[0]['z0']
    return f"""
<div class="notes">
  <h2>Cabinet layout</h2>
  <p>Press <b>Cabinet layout</b> above the model: the floor and the east wall go
  in, the existing roof comes off, and everything that stands on the loft appears
  with its label. Items stand on the deck at z&nbsp;=&nbsp;{z0:g} (beam top plus
  3/4 in. plywood). Clearance is measured from each item's south top edge to the
  underside of the rafters above it; under the slope the roof panel itself sits
  3.5 in. higher, on top of the rafters.</p>
  <table style="border-collapse:collapse;font-size:13px">
    <tr style="text-align:left"><th>#</th><th></th><th>size</th><th>x (east)</th>
        <th>y (north)</th><th>top z</th><th>rafters</th><th>to clear, move</th>
        <th>roof over it</th></tr>
    {tr}
  </table>
  <p><small>Move one by editing its row in
  <code>src/structural-analysis-v6/cabinets.py</code>; the labels stay put.</small></p>
</div>
"""


# --------------------------------------------------------------------------
# the walkway
# --------------------------------------------------------------------------

#: Floor kept clear so the storage can be reached. Each run is a rectangle
#: (x0, x1, y0, y1) subdivided into nominal 3 ft tiles; the runs meet edge to
#: edge and the network is continuous from the head of the stair to every
#: stored item.
#:
#: Two anchors, not one. The stair, the east-west run and the shelving run are
#: set out from the head of the stair on a 36 in. pitch. The loading area and
#: its spur are set out from the 6 ft north-wall opening and the west face of
#: cabinets 1 and 2, which is where they have to line up and which is not on
#: the first grid. Forcing one grid over both would have put a sliver against
#: the opening, so they are laid out as two and meet where the spur reaches
#: the east-west run.
TILE = 36.0                    # 3 ft nominal
WALK_Z = 0.25                  # tile proud of the deck, so it reads as laid on

#: The east run and the shelving run cross. Rather than let one overwrite the
#: other, the shelving run is declared as the two segments either side of the
#: crossing and the shared cell belongs to the east run. Runs must not overlap
#: -- ``tiles`` raises if they do -- because a tile drawn twice is a tile whose
#: number means two different pieces of floor.
#: The east run's band. Its south edge was 92 until cabinets 1 and 2 came down
#: to the clerestory: they are 24 in. deep off a line at y = 71, so they reach
#: y = 95 and the walkway had to give up 3 in. to them. The run is 33 in. deep
#: now rather than 36 -- still a 3 ft tile, just not a 36 in. one.
WALK_CROSS = (95.0, 128.0)     # the east run's band, where the two meet
WALK_SHELF_X = (147.75, 183.75)

#: The head of the stair is at y = 128, the north end of the opening: you climb
#: northwards and step off there onto T1, in the west strip. T2 is the corner
#: tile -- east of T1 and north of T3 at once, because those are the same cell
#: -- and it is what ties the west strip to the landing and the east run. The
#: west strip is not walked any further north than this: an earlier version ran
#: it up to y = 236 and took the whole W3-W4 bay with it, which left cabinet 5
#: with nowhere on the west wall to stand.
WALK_STEP_N = 164.0            # north edge of the two tiles at the stair head

#: Tile numbers are written down, not counted off. They used to come from the
#: position of the run in this list, so reordering or dropping a run renumbered
#: everything after it -- three times in three revisions, each time invalidating
#: the numbers the owner had just learned. Now each run carries its own ids and
#: they stay put. Dropping the old T10 leaves a gap in the sequence rather than
#: pulling T11 down into its place, which is the whole point.
WALKWAY = [
    dict(run='stair head', ids=['T1'],
         rect=(WEST_FACE, STAIR_EAST, WALK_CROSS[1], WALK_STEP_N),
         note='off the top step, in the west strip'),
    dict(run='stair head', ids=['T2'],
         rect=(STAIR_EAST, STAIR_EAST + TILE, WALK_CROSS[1], WALK_STEP_N),
         note='the corner: east of T1, north of the landing'),
    dict(run='landing', ids=['T3'],
         rect=(STAIR_EAST, STAIR_EAST + TILE, *WALK_CROSS),
         note='south of the corner, onto the east run'),
    dict(run='east run', ids=['T4', 'T5', 'T6', 'T7'],
         rect=(STAIR_EAST + TILE, WALK_SHELF_X[1], *WALK_CROSS),
         note='east from the landing to the shelving'),
    dict(run='spur', ids=['T8', 'T9'],
         rect=(STAIR_EAST + TILE, 75.75, WALK_CROSS[1], 194.0),
         note='north off the east run to the loading area'),
    # T10 was the tile between the east run and B-1, x 147.75-183.75,
    # y 71-92. The owner does not need it and the crate now stands there.
    dict(run='shelving run', ids=['T11', 'T12', 'T13', 'T14'],
         rect=(*WALK_SHELF_X, WALK_CROSS[1], NORTH_FACE),
         note='up the west face of S1 and S2 to the north wall'),
    dict(run='loading area', ids=['T15', 'T16', 'T17', 'T18'],
         rect=(NORTH_POST_X, MIDDLE_POST_X, 194.0, NORTH_FACE),
         note='6 ft x 6 ft inside the north opening, out to the N-M post line'),
]

WALK_FACE = '#c7b995'          # the deck one shade cooler and darker
WALK_LINE = '#a39877'          # tile joints
WALK_TREAD = '#b3a684'         # the diamond pattern
WALK_TEXT = '#7a7157'          # the numbers, quiet


def tiles(frame: framemod.Frame) -> list[dict]:
    """Lay the runs out as numbered tiles.

    A run is divided into whole tiles as near 3 ft as its length allows, so a
    138 in. run becomes four of 34.5 rather than three of 36 and one of 30.
    Each run is sized on its own length, which is why the shelving run's tiles
    are not the same size as the east run's -- they are 3 ft nominal, not 3 ft.

    Runs may not overlap. An earlier version skipped a cell whose centre fell
    inside one already laid, which let the shelving run straddle the east run:
    two of its tiles half-covered the crossing tile, and the drawing showed
    three numbered tiles over two tiles' worth of floor. Declare the segments
    either side of a crossing instead.
    """
    z = floor_top(frame)
    out: list[dict] = []
    for spec in WALKWAY:
        x0, x1, y0, y1 = spec['rect']
        nx = max(1, round((x1 - x0) / TILE))
        ny = max(1, round((y1 - y0) / TILE))
        if len(spec['ids']) != nx * ny:
            raise ValueError(
                f'walkway run {spec["run"]!r} at {spec["rect"]} divides into '
                f'{nx * ny} tiles but carries {len(spec["ids"])} ids '
                f'({", ".join(spec["ids"])}); fix the ids in cabinets.py')
        dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
        for jy in range(ny):
            for ix in range(nx):
                a, b = x0 + ix * dx, y0 + jy * dy
                tile = dict(n=spec['ids'][jy * nx + ix], run=spec['run'],
                            note=spec['note'],
                            x0=a, x1=a + dx, y0=b, y1=b + dy,
                            z=z + WALK_Z, w=round(dx, 2), d=round(dy, 2))
                for other in out:
                    ox = min(tile['x1'], other['x1']) - max(tile['x0'], other['x0'])
                    oy = min(tile['y1'], other['y1']) - max(tile['y0'], other['y0'])
                    if ox > 0.5 and oy > 0.5:
                        raise ValueError(
                            f'walkway run {spec["run"]!r} overlaps {other["n"]} '
                            f'({other["run"]}) by {ox:.1f} x {oy:.1f} in.; split '
                            f'the run into segments either side of the crossing')
                out.append(tile)
    return out


def walkway_traces(frame: framemod.Frame) -> tuple[list, list[dict]]:
    """Tiles as thin slabs, with joints, a tread pattern and a quiet number."""
    ts = tiles(frame)
    out = []
    for t in ts:
        v, f = _box(t['x0'], t['x1'], t['y0'], t['y1'], t['z'] - WALK_Z, t['z'])
        out.append(_mesh(
            v, f, WALK_FACE, f'walkway {t["n"]}',
            f'<b>Walkway {t["n"]}</b> · {t["w"]:g} × {t["d"]:g} in.<br>'
            f'{t["run"]} — {t["note"]}<br>keep clear'))
    jx, jy, jz = [], [], []
    tx, ty, tz = [], [], []
    for t in ts:
        ring = [(t['x0'], t['y0']), (t['x1'], t['y0']),
                (t['x1'], t['y1']), (t['x0'], t['y1']), (t['x0'], t['y0'])]
        for x, y in ring:
            jx.append(x), jy.append(y), jz.append(t['z'] + 0.02)
        jx.append(None), jy.append(None), jz.append(None)
        # a shallow diamond, two diagonals each way, for the treadplate read
        for k in (0.25, 0.75):
            tx += [t['x0'] + k * (t['x1'] - t['x0']), t['x1'], None,
                   t['x0'], t['x0'] + k * (t['x1'] - t['x0']), None]
            ty += [t['y0'], t['y0'] + (1 - k) * (t['y1'] - t['y0']), None,
                   t['y0'] + k * (t['y1'] - t['y0']), t['y1'], None]
            tz += [t['z'] + 0.02, t['z'] + 0.02, None,
                   t['z'] + 0.02, t['z'] + 0.02, None]
    out.append(go.Scatter3d(x=tx, y=ty, z=tz, mode='lines',
                            line=dict(color=WALK_TREAD, width=1),
                            hoverinfo='skip', showlegend=False, visible=False,
                            name='walkway tread'))
    out.append(go.Scatter3d(x=jx, y=jy, z=jz, mode='lines',
                            line=dict(color=WALK_LINE, width=2),
                            hoverinfo='skip', showlegend=False, visible=False,
                            name='walkway joints'))
    out.append(go.Scatter3d(
        x=[(t['x0'] + t['x1']) / 2 for t in ts],
        y=[(t['y0'] + t['y1']) / 2 for t in ts],
        z=[t['z'] + 0.1 for t in ts],
        mode='text', text=[t['n'] for t in ts], textposition='middle center',
        textfont=dict(size=11, color=WALK_TEXT, family='Helvetica, Arial'),
        hoverinfo='skip', showlegend=False, visible=False, name='walkway numbers'))
    return out, ts


def _check_walkway(frame: framemod.Frame, rows: list[dict]) -> None:
    """Nothing may stand on the walkway -- that is the whole point of it.

    A machine's table counts too: at hip height it is in the way of anyone
    walking the tile, whatever it stands on.
    """
    for t in tiles(frame):
        for r in rows:
            if r['mount'] == 'wall':
                continue
            dx = min(r['x1'], t['x1']) - max(r['x0'], t['x0'])
            dy = min(r['y1'], t['y1']) - max(r['y0'], t['y0'])
            if dx > 0.01 and dy > 0.01:
                raise ValueError(
                    f'{KINDS[r["kind"]]["label"]} {r["n"]} stands on walkway '
                    f'tile {t["n"]} ({t["run"]}) by {dx:.1f} x {dy:.1f} in.; '
                    f'move the item or the run in cabinets.py')


def walkway_html(ts: list[dict]) -> str:
    runs = {}
    for t in ts:
        runs.setdefault((t['run'], t['note']), []).append(t)
    body = ''.join(
        f'<tr><td><b>{", ".join(t["n"] for t in v)}</b></td><td>{k[0]}</td>'
        f'<td>{k[1]}</td><td>{len(v)} × {v[0]["w"]:g} × {v[0]["d"]:g} in.</td></tr>'
        for k, v in runs.items())
    total = sum((t['x1'] - t['x0']) * (t['y1'] - t['y0']) for t in ts) / 144.0
    return f"""
<div class="notes">
  <h2>Walkway</h2>
  <p>{len(ts)} tiles, {total:.0f} sq ft of floor kept clear, drawn a shade
  cooler than the deck with a tread pattern. Nothing in the item list may stand
  on one — the layout fails to build if it does. Tiles are 3&nbsp;ft
  <i>nominal</i>: each run is divided into whole tiles as near 3&nbsp;ft as its
  own length allows, so tile sizes differ between runs. One is genuinely short
  — <b>T6</b> is 21&nbsp;in. deep, because the gap between the east run and
  B-1 is only 21&nbsp;in. and a step there is worth more than a tidy number.</p>
  <table style="border-collapse:collapse;font-size:13px">
    <tr style="text-align:left"><th>tiles</th><th>run</th><th></th><th>size</th></tr>
    {body}
  </table>
</div>
"""
