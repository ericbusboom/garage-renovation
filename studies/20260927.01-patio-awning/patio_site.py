"""Site geometry for the patio awning study, shared by the scripts here.

Plan frame, inches, as Eric's sketch is drawn: x = page right, y = page up,
z = height above the patio. Origin at P1 centre. Page UP IS SOUTH and page
right is west: the P2-P3-P4 fence is the west property line; P1 and the
electrical pillar are on the east side.
"""

# name: (x, y, width_EW, depth_NS, height)  -- centres, inches
# P2-P3 and P3-P4 are 8 ft face to face (set for 8 ft stringers), so
# centres are 8 ft + one 8 in post depth = 104 in apart.
POSTS = {
    "P1": (0, 0, 8, 6, 72),      # NE (page bottom-left)
    "P2": (174, 0, 6, 8, 72),    # NW (page bottom-right)
    "P3": (174, 104, 6, 8, 82),  # on the west fence
    "P4": (174, 208, 6, 8, 82),  # SW, on the fence past the pillar line
}
PATIO_N = 150                     # north line of the sketch rectangle
PILLAR = (0, 13, PATIO_N - 48, PATIO_N)  # x0, x1, y0, y1 (4 ft long)
# Airstream, inside the fence (east of it): 18 in off the fence line, front
# 2'-8" beyond the patio edge (page up), 8 ft wide, 2 ft corner fillets.
# Length not given; drawn running off the top (south) of the sheet.
TRAILER_W, TRAILER_R = 96, 24
TRAILER_X0 = 174 - 18 - TRAILER_W
TRAILER_Y0 = PATIO_N + 32

# Tie points on the fence-side (west) face of the pillar. Page up is south,
# so T1 (south corner) is the pillar's page-top corner, T2 (north) its
# page-bottom corner.
TIE_Z = 101  # tie-point height on the pillar, in
TIES = {"T1": (PILLAR[1], PILLAR[3]), "T2": (PILLAR[1], PILLAR[2])}
# P4 end is its south face (page-up face); other ends at post centres.
CABLES = [("T2", "P4", (174, 212)), ("T1", "P3", None),
          ("T2", "P1", None), ("T2", "P2", None)]


def trailer_sdf(x, y):
    """Signed plan distance (in) from (x, y) to the Airstream outline; < 0 inside.

    Rounded-box distance with the body running far off the sheet.
    """
    hw, hh, r = TRAILER_W / 2, 1000.0, TRAILER_R
    qx = abs(x - (TRAILER_X0 + hw)) - (hw - r)
    qy = abs(y - (TRAILER_Y0 + hh)) - (hh - r)
    outside = (max(qx, 0) ** 2 + max(qy, 0) ** 2) ** 0.5
    return outside + min(max(qx, qy), 0) - r


def trailer_clearance(p, q, n=4000):
    """Least plan clearance (in) from straight cable p-q to the trailer."""
    return min(trailer_sdf(p[0] + i / n * (q[0] - p[0]), p[1] + i / n * (q[1] - p[1]))
               for i in range(n + 1))


def heights_over_trailer(p, q, za, zb, n=4000):
    """(min, max) cable height (in) where the cable is over the trailer plan, or None.

    Cable taken as straight between its end heights (no sag).
    """
    zs = [za + i / n * (zb - za) for i in range(n + 1)
          if trailer_sdf(p[0] + i / n * (q[0] - p[0]), p[1] + i / n * (q[1] - p[1])) < 0]
    return (min(zs), max(zs)) if zs else None

# T3: pillar's north-east (page bottom-left) corner, same height.
TIES["T3"] = (PILLAR[0], PILLAR[2])


def anchor(name):
    """(x, y, z) of a post top or pillar tie point, inches."""
    if name in POSTS:
        x, y, _, _, h = POSTS[name]
        return (x, y, h)
    x, y = TIES[name]
    return (x, y, TIE_Z)
