"""Redraw Eric's patio sketch (data/images/patio.svg) as a clean labelled plan.

Plan frame, inches, as the sketch is drawn: x = page right, y = page up.
Origin at P1 centre. Eric views it from the house, so page UP IS SOUTH and
page right is west: the P2-P3-P4 fence is the west property line, P1 and
the pillar are on the east side. Dimensions are rounded from the OmniGraffle sketch, which was
drawn at 6 px/in; Eric says the odd fractions there are not real.
"""

from pathlib import Path

OUT = Path(__file__).with_name("patio-plan.svg")

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
# 3'-6" south (page up) of the pillar's end, 8 ft wide, 2 ft corner fillets.
# Length not given; drawn running off the top (south) of the sheet.
TRAILER_W, TRAILER_R = 96, 24
TRAILER_X0 = 174 - 18 - TRAILER_W
TRAILER_Y0 = PATIO_N + 42

S = 3.0             # px per inch in the output
M = 110             # margin px
XMIN, XMAX, YMIN, YMAX = -12, 200, -12, 264
W = (XMAX - XMIN) * S + 2 * M
H = (YMAX - YMIN) * S + 2 * M


def px(x, y):
    return M + (x - XMIN) * S, M + (YMAX - y) * S


def ftin(n):
    f, i = divmod(round(n), 12)
    return f"{f}′-{i}″"


out = []
a = out.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
  f'width="{W:.0f}" height="{H:.0f}" font-family="Helvetica, Arial, sans-serif">')
a('<defs><marker id="ar" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" '
  'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z"/></marker></defs>')
a(f'<rect width="{W:.0f}" height="{H:.0f}" fill="white"/>')

# 1-ft grid
for gx in range(0, XMAX + 1, 12):
    x0, y0 = px(gx, YMIN); x1, y1 = px(gx, YMAX)
    a(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#eee"/>')
for gy in range(0, YMAX + 1, 12):
    x0, y0 = px(XMIN, gy); x1, y1 = px(XMAX, gy)
    a(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#eee"/>')

# patio rectangle from the sketch
x0, y0 = px(0, PATIO_N); x1, y1 = px(174, 0)
a(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#f6f1e7" '
  'stroke="#555" stroke-dasharray="8 5"/>')
cx, cy = px(87, 75)
a(f'<text x="{cx}" y="{cy}" text-anchor="middle" fill="#999" font-size="18">work patio</text>')

# electrical pillar
x0, y0 = px(PILLAR[0], PILLAR[3]); x1, y1 = px(PILLAR[1], PILLAR[2])
a(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#bbb" stroke="#666"/>')
tx, ty = px(2, PILLAR[2] - 8)
a(f'<text x="{tx}" y="{ty}" font-size="13" fill="#444">electrical pillar</text>')
a(f'<text x="{tx}" y="{ty+16}" font-size="13" fill="#444">(carries outbuilding roof)</text>')

# Airstream (front end only; body runs off the sheet to the north)
x0, x1 = TRAILER_X0, TRAILER_X0 + TRAILER_W
r, yf, ytop = TRAILER_R, TRAILER_Y0, YMAX - 2
pts = [px(x0, ytop), px(x0, yf + r), px(x0 + r, yf), px(x1 - r, yf), px(x1, yf + r), px(x1, ytop)]
rp = r * S
a(f'<path d="M{pts[0][0]},{pts[0][1]} L{pts[1][0]},{pts[1][1]} '
  f'A{rp},{rp} 0 0 0 {pts[2][0]},{pts[2][1]} L{pts[3][0]},{pts[3][1]} '
  f'A{rp},{rp} 0 0 0 {pts[4][0]},{pts[4][1]} L{pts[5][0]},{pts[5][1]}" '
  'fill="#dde3ea" stroke="#556" stroke-width="1.5"/>')
bx0, by = px(x0, ytop)
a(f'<path d="M{bx0},{by} l{TRAILER_W*S/4},-8 l{TRAILER_W*S/4},16 l{TRAILER_W*S/4},-16 '
  f'l{TRAILER_W*S/4},8" fill="white" stroke="#556"/>')
cx, cy = px(x0 + TRAILER_W / 2, yf + 34)
a(f'<text x="{cx}" y="{cy}" text-anchor="middle" font-size="16" fill="#334">Airstream</text>')
a(f'<text x="{cx}" y="{cy+17}" text-anchor="middle" font-size="12" fill="#556">front · 2′ radius corners</text>')
# fence line through P2-P3-P4
fa, fb = px(174, 0), px(174, 208)
a(f'<line x1="{fa[0]}" y1="{fa[1]}" x2="{fb[0]}" y2="{fb[1]}" stroke="#7a5a33" stroke-width="2"/>')
tx, ty = px(177, 22)
a(f'<text transform="translate({tx-12},{ty}) rotate(-90)" font-size="12" fill="#7a5a33">fence (west property line)</text>')

# posts
for name, (x, y, w, d, h) in POSTS.items():
    x0, y0 = px(x - w / 2, y + d / 2)
    a(f'<rect x="{x0}" y="{y0}" width="{w*S}" height="{d*S}" fill="#ab7942" stroke="black"/>')
    lx, ly = px(x, y)
    west = x < 87
    anchor = "end" if not west else "start"
    dx = -16 if not west else 16
    if west:  # P1: label below-right, clear of the dimension line
        lx, ly = lx + 4, ly + 40
        dx = 0
    a(f'<text x="{lx+dx}" y="{ly-2}" text-anchor="{anchor}" font-size="20" '
      f'font-weight="bold">{name}</text>')
    a(f'<text x="{lx+dx}" y="{ly+16}" text-anchor="{anchor}" font-size="14" '
      f'fill="#333">{ftin(h)} tall</text>')


def dim(p, q, label, off, horiz):
    """Dimension between plan points p and q, offset `off` inches."""
    if horiz:
        (xa, ya), (xb, yb) = px(p[0], p[1] + off), px(q[0], q[1] + off)
        ext = [(px(p[0], p[1]), (xa, ya)), (px(q[0], q[1]), (xb, yb))]
    else:
        (xa, ya), (xb, yb) = px(p[0] + off, p[1]), px(q[0] + off, q[1])
        ext = [(px(p[0], p[1]), (xa, ya)), (px(q[0], q[1]), (xb, yb))]
    for (u, v), (s, t) in ext:
        a(f'<line x1="{u}" y1="{v}" x2="{s}" y2="{t}" stroke="#777" stroke-width="0.8"/>')
    a(f'<line x1="{xa}" y1="{ya}" x2="{xb}" y2="{yb}" stroke="black" stroke-width="1.4" '
      'marker-start="url(#ar)" marker-end="url(#ar)"/>')
    mx, my = (xa + xb) / 2, (ya + yb) / 2
    if not label:
        return
    if horiz:
        a(f'<rect x="{mx-34}" y="{my-11}" width="68" height="20" fill="white"/>')
        a(f'<text x="{mx}" y="{my+5}" text-anchor="middle" font-size="15">{label}</text>')
    else:
        a(f'<g transform="translate({mx},{my}) rotate(-90)"><rect x="-44" y="-11" '
          f'width="88" height="20" fill="white"/><text y="5" text-anchor="middle" '
          f'font-size="15">{label}</text></g>')


dim((0, PATIO_N), (174, PATIO_N), "14′-6″", 30, True)
dim((13, PATIO_N - 20), (174, PATIO_N - 20), "13′-5″", 0, True)
dim((0, 0), (174, 0), "14′-6″", -24, True)
dim((0, 0), (0, PATIO_N), "12′-6″", -24, False)
dim((0, PILLAR[2]), (0, PILLAR[3]), "4′-0″", -10, False)
dim((174, 4), (174, 100), "8′-0″ clear", 11, False)
dim((174, 108), (174, 204), "8′-0″ clear", 11, False)
dim((174, PATIO_N), (174, 208), "4′-10″", 30, False)

dim((TRAILER_X0 + TRAILER_W, TRAILER_Y0 + 60), (174, TRAILER_Y0 + 60), "", 0, True)
lx, ly = px(174, TRAILER_Y0 + 60)
a(f'<text x="{lx+8}" y="{ly+5}" font-size="15">1′-6″</text>')
dim((TRAILER_X0, TRAILER_Y0 + 10), (TRAILER_X0 + TRAILER_W, TRAILER_Y0 + 10), "8′-0″", 0, True)
dim((TRAILER_X0, PATIO_N), (TRAILER_X0, TRAILER_Y0), "3′-6″", -14, False)
a('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#777" stroke-width="0.8" stroke-dasharray="4 3"/>'
  % (*px(TRAILER_X0 - 14, PATIO_N), *px(TRAILER_X0, PATIO_N)))

# north arrow
nx, ny = px(-4, 200)
a(f'<g transform="translate({nx},{ny})"><path d="M0,-30 L10,0 L0,-8 L-10,0 z" fill="black"/>'
  '<text y="20" text-anchor="middle" font-size="18" font-weight="bold">S</text></g>')

a(f'<text x="{M}" y="40" font-size="22" font-weight="bold">Work patio — posts and dimensions (plan)</text>')
a(f'<text x="{M}" y="64" font-size="14" fill="#555">Redrawn from data/images/patio.svg, dims rounded. '
  '“?” = scaled off the sketch. Grid 1 ft.</text>')
a('</svg>')

OUT.write_text("\n".join(out))
print(OUT)
