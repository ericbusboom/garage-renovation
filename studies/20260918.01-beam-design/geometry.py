"""Beam-scheme plan geometry — alternate design BEAM-001, revision 1.

Revision 0 read its columns straight out of the truss frame model. This revision
moves five of them and adds three, so the scheme is now its own spec. Stations are
derived from the existing building wherever the owner set them that way, so the
arithmetic stays visible instead of being a typed-in number.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / 'frame-models/frame-20260917.05-square-upper-west.compas.json'

EX = json.loads((ROOT / 'model/parameters.json').read_text())
EW, EL = EX['width'], EX['length']              # 249.5 x 249, outside faces

# --- the existing west-wall windows set the B-1 station ----------------------
WEST_WINDOWS = sorted(
    [(o['offset'], o['offset'] + o['width']) for o in EX['openings'] if o['side'] == 'west'])
SOUTH_WINDOW = WEST_WINDOWS[0]                  # y 73.0 .. 101.5
NORTH_WINDOW = WEST_WINDOWS[1]                  # y 153.25 .. 182.0

# --- column rows -------------------------------------------------------------
WEST = -34.0                                    # new west column row
BE_X = 211.5                                    # inner east column row
BEW_X = 247.5                                   # east-wall post / beam row
EMB_X = 247.5                                   # embedded east-wall posts, on the BEW axis
BWI_X = EX['wall_west'] / 2                     # 3.75, centered on the existing west wall

# --- east-west beam stations -------------------------------------------------
B_SO_Y = -63.0                                  # south roof edge, unchanged
B_S_Y = EX['wall_south'] / 2                    # 3.0, centered on the existing south wall
B_1_W = 4.0                                     # B-1 is a 4-inch-wide beam
B_1_Y = SOUTH_WINDOW[0] - B_1_W / 2             # 71.0, north face on the window's south edge
B_2_Y = 185.0                                   # unchanged
B_1A_Y = (B_1_Y + B_2_Y) / 2                    # 128.0, midpoint of BWI-2  -- ASSUMED, see README
NORTH_SHIFT = 22.0                              # the whole north wall moves north
B_N_W = 6.0                                     # assume up to a 6-inch beam
B_N_Y = EL + NORTH_SHIFT - B_N_W / 2            # 268.0, north face flush with the new wall face
NEW_NORTH_FACE = EL + NORTH_SHIFT               # 271.0

# --- columns standing on the ground -----------------------------------------
# id, x, y, size, kind
COLUMNS = [
    ('SW0',     WEST,   B_SO_Y,  4, 'frame'),
    ('W1',      WEST,   B_S_Y,   4, 'frame'),
    ('W2',      WEST,   B_1_Y,   4, 'frame'),
    ('W3',      WEST,   B_2_Y,   4, 'frame'),
    ('W4',      WEST,   B_N_Y,   4, 'frame'),
    ('S1',      145.5,  B_SO_Y,  4, 'frame'),
    ('S2',      BE_X,   B_SO_Y,  4, 'frame'),
    ('S3',      BE_X,   B_S_Y,   4, 'frame'),
    ('N1',      40.35,  B_N_Y,   6, 'frame'),
    ('N2',      BE_X,   B_N_Y,   4, 'frame'),
    ('E-S',     BEW_X,  -2.0,    4, 'wall'),
    ('E-M1/B',  EMB_X,  B_1_Y,   4, 'wall-option'),
    ('E-M/B',   EMB_X,  B_2_Y,   4, 'wall-option'),
    ('E-N',     BEW_X,  251.0,   4, 'wall'),
]

# --- east-west beams ---------------------------------------------------------
# id, y, x_from, x_to, bears_on_existing_wall, note
CROSS_BEAMS = [
    ('B-SO', B_SO_Y, WEST, BE_X,  False, 'south roof edge — SW0 / S1 / S2'),
    ('B-S',  B_S_Y,  WEST, BEW_X, True,  'on the existing south wall — W1 / S3, ties into BEW'),
    ('B-1',  B_1_Y,  WEST, BEW_X, False, 'W2 → E-M1/B — north face on the south window edge'),
    ('B-1A', B_1A_Y, BWI_X, BEW_X, False, 'BWI-2 → BEW — no column either end'),
    ('B-2',  B_2_Y,  WEST, BEW_X, False, 'W3 → E-M/B'),
    ('B-N',  B_N_Y,  WEST, BE_X,  False, 'north edge — W4 / N1 / N2'),
]

# --- north-south beams -------------------------------------------------------
# id, x, y_from, y_to, bears_on_existing_wall, note
LINE_BEAMS = [
    ('BW',    WEST,  B_SO_Y, B_N_Y, False, 'on SW0 / W1 / W2 / W3 / W4'),
    ('BE',    BE_X,  B_SO_Y, B_N_Y, False, 'on S2 / S3 / N2'),
    ('BWI-1', BWI_X, B_2_Y,  B_N_Y, True,  'on the existing west wall, B-2 → B-N'),
    ('BWI-2', BWI_X, B_1_Y,  B_2_Y, True,  'on the existing west wall, B-1 → B-2'),
    ('BWI-3', BWI_X, B_S_Y,  B_1_Y, True,  'on the existing west wall, B-S → B-1'),
    ('BEW',   BEW_X, -4.0,   253.0, True,  'on the existing east wall — E-S / E-M1 / E-M / E-N'),
]

LOFT = dict(south=B_1_Y, north=B_N_Y, west=WEST, east=BE_X)


# --- south storage shelf ------------------------------------------------------
# Revision 13, owner direction 2026-09-18: the shelf is framed right through. The
# two 3 ft ladder openings of revisions 2-12 are gone -- the owner will not be
# climbing up from below -- and the 68 in bay between B-S and B-1 is one deck
# from BW to BE with joists at the same spacing as the loft. It now takes the
# storage cabinets (see structural-analysis-v6/cabinets.py). SH-E, the 3 ft
# east of BE over the lean-to zone, is kept as its own panel because it is a
# different structural condition.
SHELF_SOUTH = B_S_Y                             # 3.0, on B-S
SHELF_NORTH = B_1_Y                             # 71.0, on B-1
SHELF_DEPTH = SHELF_NORTH - SHELF_SOUTH         # 68.0 = 5 ft 8 in
SHELF_MODULE = 36.0                             # the 3 ft module, SH-E only

# id, x_from, x_to, note
SHELF_PANELS = [
    ('SH', WEST, BE_X,
     'one deck, BW to BE, joists through -- the ladder openings are closed'),
    ('SH-E', BE_X, BEW_X,
     '3 ft west from BEW; the west edge lands exactly on BE'),
]
SHELF_GAPS: list = []                           # none since revision 13
# The chain closes: 245.5 + 36 = 281.5 = BEW_X - WEST.


# --- elevations, sections and decks for the analysis model --------------------
# Owner direction: every beam sits on top of the existing walls, so the frame is a
# single-level grillage. That removes the two-level split earlier revisions carried.
WALL_TOP_Z = EX['wall_height']                  # 98.5, existing wall plate
BEAM_SECTION = 'W12X16'                         # owner direction, revision 9
BEAM_D = 12.0                                   # W12X16 depth
BEAM_BF = 3.99                                  # W12X16 flange width
BEAM_AXIS_Z = WALL_TOP_Z + BEAM_D / 2           # 104.5, soffit on the wall top
COLUMN_SECTION = 'HSS4X4X1/4'
COLUMN_SIZE = 4.0
JOIST_SECTION = '2x8 DF-L No.2'
JOIST_W, JOIST_D = 1.5, 7.25
JOIST_SPACING_MAX = 16.0
DECK = '3/4 in plywood'
DESIGN_LIVE_PSF = 100.0                         # owner direction

# Decks that carry load. Each is (name, x_from, x_to, y_from, y_to, joist rims).
# 'rims' names which side edges need a joist of their own because no beam is there.
# The strip west of BWI-2 between B-1 and B-2 is the STAIR OPENING, not deck. Its
# 114 in length matches the 88/sin(50 deg) = 114.9 in flight in ../stair-study. All
# four of its edges are already beams -- BW, BWI-2, B-1, B-2 -- so the well is framed
# without adding a header. This is also why B-1A correctly stops at BWI-2: there is
# nothing to support west of that line at y = 128.
STAIR_WELL = dict(west=WEST, east=BWI_X, south=B_1_Y, north=B_2_Y)
DECKS = [
    ('loft bay 1', BWI_X, BE_X, B_1_Y, B_1A_Y, ()),
    ('loft bay 2', BWI_X, BE_X, B_1A_Y, B_2_Y, ()),
    ('loft bay 3', WEST, BE_X, B_2_Y, B_N_Y, ()),
    ('shelf SH', WEST, BE_X, SHELF_SOUTH, SHELF_NORTH, ()),
    ('shelf SH-E', BE_X, BEW_X, SHELF_SOUTH, SHELF_NORTH, ()),
]


def stair_well_sf():
    w = STAIR_WELL
    return (w['east'] - w['west']) * (w['north'] - w['south']) / 144.0


def deck_area_sf():
    return sum((x2 - x1) * (y2 - y1) for _, x1, x2, y1, y2, _ in DECKS) / 144.0


# --- E-N tie ------------------------------------------------------------------
# E-S reaches BE through B-S and the two embedded posts reach it through B-1 and
# B-2, but E-N had no east-west tie: B-N is at y = 268, eight inches north of it.
CROSS_BEAMS.append(
    ('C-EN', 251.0, BE_X, BEW_X, False, 'E-N → BE tie, keeping the name from STR-006'))


# --- roof envelope, carried over from the truss lineage -----------------------
# Absolute heights are preserved from frame-20260917.05 so the west, east and north
# elevations read as they did: 30 degree solar slope starting at z = 117 over the
# south edge, square upper chord at z = 228.75. The clerestory vertical moves from
# y = 76.07 to y = 71, onto W2 and B-1, which is where a vertical belongs now that
# B-1 sits on the window edge. That lengthens the clerestory glazing by 2.9 in.
SOLAR_START_Z = 117.0
SOLAR_SLOPE = 0.5773502691896256                # tan(30 degrees)
SQUARE_TOP_Z = 228.75
CLERESTORY_Y = B_1_Y                            # 71, was 76.0718 in the truss model


def solar_z(y):
    """Underside of the solar slope at a given north station."""
    return SOLAR_START_Z + (y - B_SO_Y) * SOLAR_SLOPE


# Posts that grow past the beam plane, and where each one stops. Anything absent
# from this map still stops at the beam plane.
POST_TOPS = {
    'SW0': SOLAR_START_Z,            # 117.0    — south end of the solar slope
    'W1':  solar_z(B_S_Y),           # 155.11   — up to the slope chord
    'W2':  SQUARE_TOP_Z,             # 228.75   — the clerestory vertical
    'W3':  SQUARE_TOP_Z,
    'W4':  SQUARE_TOP_Z,
    'S2':  SOLAR_START_Z,            # east mirror of SW0
    'S3':  solar_z(B_S_Y),           # east mirror of W1
    'N2':  SQUARE_TOP_Z,             # east mirror of W4
}

# The east plane needs verticals at the clerestory and W3 stations, but no ground
# column stands there, so they hang off BE exactly as E.clerestory and E.W3 did.
HUNG_VERTICALS = [
    ('E.clerestory', BE_X, CLERESTORY_Y, BEAM_AXIS_Z, SQUARE_TOP_Z, 4.0,
     'concept envelope', 'east clerestory vertical, no column below'),
    ('E.W3', BE_X, 185.0, BEAM_AXIS_Z, SQUARE_TOP_Z, 4.0,
     'concept envelope', 'east vertical at the W3 station, no column below'),
]

# One truss plane, described once and built at both x stations. Sections and the
# two-brace pattern are the previous model's.
# id suffix, (y, z) start, (y, z) end, width, section reference, note
TRUSS_PLANE = [
    ('slope', (B_SO_Y, SOLAR_START_Z), (CLERESTORY_Y, solar_z(CLERESTORY_Y)), 2.5,
     'concept envelope', 'solar slope chord, 30 degrees'),
    ('top', (CLERESTORY_Y, SQUARE_TOP_Z), (B_N_Y, SQUARE_TOP_Z), 5.0,
     'concept envelope', 'square upper chord'),
    ('square.brace', (185.0, BEAM_AXIS_Z), (CLERESTORY_Y, SQUARE_TOP_Z), 2.2,
     'concept envelope', 'W3 base to the clerestory head'),
    ('rear.brace', (185.0, BEAM_AXIS_Z), (B_N_Y, SQUARE_TOP_Z), 2.2,
     'concept envelope', 'W3 base to the north head'),
]
TRUSS_PLANES = [('W', WEST), ('E', BE_X)]


# --- roof beams, east to west ------------------------------------------------
# One across the top of each post that rises above the loft: W1, W2, W3, W4. Each
# lands on the matching east-plane vertical at exactly the same height, so the two
# truss planes are tied together at four stations.
#   R-W1 sits under the solar slope; the other three are at the square top.
# Section is a placeholder: no roof load is defined yet, and some of these are to
# become trusses.
ROOF_BEAM_SECTION = BEAM_SECTION                 # W14X22, placeholder

# Chord envelopes the roof beams have to sit inside, from TRUSS_PLANE above.
SQUARE_TOP_CHORD_W = 5.0
SLOPE_CHORD_W = 2.5
SQUARE_TOP_FACE_Z = SQUARE_TOP_Z + SQUARE_TOP_CHORD_W / 2      # 231.25

#: Vertical half-thickness of the raking slope chord: its section is measured
#: perpendicular to the rake, so the vertical projection is larger by 1/cos.
_SLOPE_COS = 1.0 / math.hypot(1.0, SOLAR_SLOPE)
SLOPE_HALF_VERT = (SLOPE_CHORD_W / 2) / _SLOPE_COS             # 1.4434


def roof_beam_axis(top_face_z):
    """Beam axis that puts the beam's top flush with a chord's top face.

    Owner correction: these sit under the roof surface, so the top of the beam
    lines up with the top of the chord it runs beside rather than the beam being
    centred on the chord axis, which stood it 6.85 in proud of the envelope.
    """
    return top_face_z - BEAM_D / 2


ROOF_BEAMS = [
    ('R-W1', B_S_Y, None, 'under the solar slope, W1 to S3; set below'),
    ('R-W2', B_1_Y, roof_beam_axis(SQUARE_TOP_FACE_Z),
     'clerestory head, W2 to E.clerestory'),
    ('R-W3', 185.0, roof_beam_axis(SQUARE_TOP_FACE_Z),
     'square top, W3 to E.W3'),
    ('R-W4', B_N_Y, roof_beam_axis(SQUARE_TOP_FACE_Z),
     'north head, W4 to N2'),
]


# --- north wall middle post ---------------------------------------------------
# Owner direction: a post midway between W4 and N2, dividing the north wall in
# two. That is 122.75 in from W4, which is the "about 10 ft" the owner settled on.
N_MID_X = (WEST + BE_X) / 2                     # 88.75
# Owner direction: N-M does not reach the ground. It is a second-floor post,
# standing on B-N and carrying R-W4 at midspan, so it is a hung vertical rather
# than a column and takes no footing.
N_MID_TOP = roof_beam_axis(SQUARE_TOP_FACE_Z)   # 225.25, R-W4's axis
HUNG_VERTICALS.append(
    ('N-M', N_MID_X, B_N_Y, BEAM_AXIS_Z, N_MID_TOP, 4.0, 'HSS4X4X1/4',
     'north wall middle post, second floor only, stands on B-N and carries R-W4'))

# --- ground-level cross bracing ----------------------------------------------
# Vertical X in the plane of a wall, from the footings up to the beam plane.
# Group name 'Bracing' matters: structural-analysis-v6 pin-releases that group,
# which is what a discrete diagonal wants.
BRACE_SECTION = 'HSS2-1/2X2-1/2X3/16'
# id, plane axis ('x' fixed or 'y' fixed), fixed coordinate, from, to, z0, z1
CROSS_BRACED_BAYS = [
    ('BR-S', 'y', B_SO_Y, 145.5, BE_X, 0.0, BEAM_AXIS_Z,
     'south row, S1 to S2'),
    ('BR-W', 'x', WEST, 185.0, B_N_Y, 0.0, BEAM_AXIS_Z,
     'west row, W3 to W4'),
    ('BR-N', 'y', B_N_Y, WEST, 40.35, 0.0, BEAM_AXIS_Z,
     'north row ground floor, W4 to N1; the open bay is above this'),
    ('BR-NU', 'y', B_N_Y, N_MID_X, BE_X, BEAM_AXIS_Z, N_MID_TOP,
     'north row second floor, N-M to N2'),
]

# --- clerestory truss ---------------------------------------------------------
# Replaces R-W2. A vertical truss in the y = CLERESTORY_Y plane, running the full
# width between the two truss planes, from where the slope chords meet the posts
# up to the square top. The glazing sits in it, so the chords and mullions are
# back-to-back double angles forming a T: flange out, stem in, giving a rebate.
CT_CHORD = '2L3X3X3/8 T'
CT_MULLION = '2L2X2X1/4 T'
CT_DIAGONAL = 'HSS2X2X1/8'
CT_CHORD_D, CT_CHORD_B = 6.0, 3.0               # flange height, stem reach
CT_MULLION_D, CT_MULLION_B = 4.0, 2.0
CT_BOTTOM_Z = solar_z(CLERESTORY_Y)             # 194.365, slope meets the post
CT_TOP_Z = SQUARE_TOP_FACE_Z - CT_CHORD_D / 2   # 228.25, flange top flush at 231.25
CT_PANELS = 6                                   # glazed bays across the width


def ct_mullion_x():
    """Mullion stations. The middle one lands on N-M's line at x = 88.75."""
    return [WEST + (BE_X - WEST) * k / CT_PANELS for k in range(1, CT_PANELS)]


# R-W2 is now the clerestory truss's top chord, so it is no longer its own beam.
ROOF_BEAMS = [b for b in ROOF_BEAMS if b[0] != 'R-W2']


# --- light roof framing -------------------------------------------------------
# Typical metal-roof secondary framing: rafters at the clerestory mullion spacing,
# 40.92 in o.c., landing on the primary east-west members already there.
#
# Convention, and it matters: the primary members have their tops flush with the
# roof surface but different depths, so their axes sit at different elevations.
# A line model cannot put a rafter both on those axes and on one plane. The
# rafters therefore run axis-to-axis between the members they bear on, which
# leaves a small kink of 3 in over 114 in at the clerestory. Real depth layering
# -- rafter seated on beam, panel on rafter -- is a detailing matter, not
# something this model resolves.
RAFTER_SECTION = 'HSS2-1/2X2-1/2X1/8'       # flat plane, split by R-W3
SLOPE_RAFTER_SECTION = 'HSS3-1/2X3-1/2X1/8'  # slope plane, one unbroken piece
SLOPE_RAFTER_D = 3.5
EAVE_SECTION = 'HSS3-1/2X3-1/2X1/8'

# Owner correction: the slope rafters are ONE straight member each, running across
# the top of R-W1 rather than kinking at it. Putting them on the slope chord axis
# makes that work, because solar_z is a straight line through both ends:
#   low end  (y = -63, z = 117)      -> R-SO, the eave
#   high end (y = 71, z = 194.365)   -> CT.bottom
# Two things follow. R-SO drops onto that line so the rafters frame into it, and
# R-W1 drops until its top is the rafter soffit, so the rafters pass over it.
R_SO_Z = solar_z(B_SO_Y)                                   # 117.0
POST_TOPS['S1'] = R_SO_Z            # S1 reaches the eave to halve R-SO's span
R_W1_TOP = solar_z(B_S_Y) - SLOPE_RAFTER_D / 2             # 153.355, rafter soffit
R_W1_Z = R_W1_TOP - BEAM_D / 2                             # 147.355

# The flat rafters run dead level, so CT.top drops to the roof beams' axis. Its
# flange top is then 228.25, three inches under the square chord -- which is where
# a window head belongs anyway, below the roof.
FLAT_AXIS_Z = roof_beam_axis(SQUARE_TOP_FACE_Z)            # 225.25
CT_TOP_Z = FLAT_AXIS_Z


def rafter_x():
    """Rafter stations: the clerestory mullion lines, so everything lines up."""
    return ct_mullion_x()


#: One straight rafter per station in each plane. The flat one is split where it
#: crosses R-W3, which shares its axis; the slope one is not split at all.
SLOPE_RAFTERS = [('RS', (B_SO_Y, R_SO_Z), (CLERESTORY_Y, CT_BOTTOM_Z))]
FLAT_RAFTERS = [('RF', (CLERESTORY_Y, CT_TOP_Z), (B_N_Y, FLAT_AXIS_Z))]

# R-W1's elevation is set by the slope rafters that pass over it, so it is filled
# in once they are defined.
ROOF_BEAMS = [(mid, y, (R_W1_Z if mid == 'R-W1' else z), note)
              for mid, y, z, note in ROOF_BEAMS]

# --- east lean-to rafters -----------------------------------------------------
# Owner direction: one light beam from each east-wall post up to the east truss
# plane. These rake at 54 to 74 degrees, the same range the truss lineage used.
# id, (x, y, z) at the wall post, (x, y, z) at the truss plane, note
EAST_RAFTERS = [
    ('RE-S',  (BEW_X, -2.0, BEAM_AXIS_Z), (BE_X, B_S_Y, solar_z(B_S_Y)),
     'E-S to the top of S3'),
    ('RE-M1', (BEW_X, B_1_Y, BEAM_AXIS_Z), (BE_X, B_1_Y, SQUARE_TOP_Z),
     'E-M1/B to the top of E.clerestory'),
    ('RE-M',  (BEW_X, B_2_Y, BEAM_AXIS_Z), (BE_X, B_2_Y, SQUARE_TOP_Z),
     'E-M/B to the top of E.W3'),
    ('RE-N',  (BEW_X, 251.0, BEAM_AXIS_Z), (BE_X, B_N_Y, SQUARE_TOP_Z),
     'E-N to the top of N2'),
]
