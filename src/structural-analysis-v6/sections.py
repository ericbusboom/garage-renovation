"""Section property library for the garage frame.

Square/rectangular HSS properties are computed from first principles using the
AISC convention: design wall thickness ``t = 0.93 * t_nominal`` and an outside
corner radius of ``2t`` (inside radius ``t``).  Areas and second moments come
from an exact polygon integration of the rounded outer boundary minus the
rounded inner boundary, so they reproduce the AISC Manual tables to well under
one percent.  The torsional constant uses Bredt's thin-walled formula.

Wide-flange properties are transcribed from the AISC Shapes Database.

Why compute rather than transcribe the whole HSS table: 61 of the 122 members in
the frame model carry the section reference ``concept envelope`` -- a nominal
outside dimension with no wall thickness ever chosen.  Those members are
assigned the *lightest* standard wall for their nominal size (see
``DEFAULT_WALL``), which is the conservative reading and is what makes the
downsizing study meaningful: if a member is still lightly stressed at the
thinnest available wall, the nominal size itself can come down.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict

# --------------------------------------------------------------------------
# polygon integration helpers
# --------------------------------------------------------------------------

def _rounded_rect(b: float, d: float, r: float, n: int = 48) -> list[tuple[float, float]]:
    """Centroidal rounded rectangle, width ``b`` (y) by depth ``d`` (z), corner radius ``r``."""
    r = min(r, b / 2.0, d / 2.0)
    hy, hz = b / 2.0 - r, d / 2.0 - r
    pts: list[tuple[float, float]] = []
    for cy, cz, a0 in ((hy, hz, 0.0), (-hy, hz, 90.0), (-hy, -hz, 180.0), (hy, -hz, 270.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def _polygon_props(pts: list[tuple[float, float]]) -> tuple[float, float, float]:
    """Return (area, Iyy, Izz) about the origin for a closed CCW polygon."""
    a = iyy = izz = 0.0
    n = len(pts)
    for i in range(n):
        y0, z0 = pts[i]
        y1, z1 = pts[(i + 1) % n]
        cross = y0 * z1 - y1 * z0
        a += cross
        # second moments by Green's theorem
        izz += cross * (y0 * y0 + y0 * y1 + y1 * y1)   # about the z (strong) axis -> integral of y^2
        iyy += cross * (z0 * z0 + z0 * z1 + z1 * z1)
    return a / 2.0, iyy / 12.0, izz / 12.0


# --------------------------------------------------------------------------
# section record
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Section:
    name: str
    family: str          # 'HSS' | 'W' | 'wood'
    b: float             # outside width  (in)
    d: float             # outside depth  (in)
    t: float             # design wall thickness, 0 for W / wood
    A: float
    Iy: float            # weak-axis second moment (about the local y axis)
    Iz: float            # strong-axis second moment
    J: float
    Zy: float            # plastic section modulus, weak
    Zz: float            # plastic section modulus, strong
    Sy: float
    Sz: float
    ry: float
    rz: float
    weight: float        # lb/ft
    compact: bool = True
    note: str = ''

    def as_dict(self) -> dict:
        return asdict(self)


STEEL_DENSITY = 0.2836   # lb/in^3  (490 pcf)
WOOD_DENSITY = 0.0185    # lb/in^3  (32 pcf, Douglas fir-larch)


def hss_square(b: float, t_nom: float, name: str | None = None) -> Section:
    """Square HSS from nominal outside dimension and nominal wall thickness."""
    return hss_rect(b, b, t_nom, name)


def hss_rect(b: float, d: float, t_nom: float, name: str | None = None) -> Section:
    t = 0.93 * t_nom
    outer = _rounded_rect(b, d, 2.0 * t)
    inner = _rounded_rect(b - 2.0 * t, d - 2.0 * t, t)
    Ao, Iyo, Izo = _polygon_props(outer)
    Ai, Iyi, Izi = _polygon_props(inner)
    A, Iy, Iz = Ao - Ai, Iyo - Iyi, Izo - Izi

    # Bredt torsion on the mid-thickness contour
    rm = 1.5 * t
    bm, dm = b - t, d - t
    Am = bm * dm - (4.0 - math.pi) * rm * rm
    pm = 2.0 * (bm + dm) - 8.0 * rm + 2.0 * math.pi * rm
    J = 4.0 * Am * Am * t / pm

    # plastic moduli, square-corner idealisation (slightly conservative vs. rounded)
    bi, di = b - 2.0 * t, d - 2.0 * t
    Zz = (b * d * d - bi * di * di) / 4.0
    Zy = (d * b * b - di * bi * bi) / 4.0
    Sz, Sy = Iz / (d / 2.0), Iy / (b / 2.0)

    # AISC Table B4.1b compactness for HSS walls in flexure: lambda_p = 1.12 sqrt(E/Fy)
    lam = max(b - 3.0 * t, d - 3.0 * t) / t
    compact = lam <= 1.12 * math.sqrt(29000.0 / 50.0)

    if name is None:
        name = f'HSS{_frac(b)}X{_frac(d)}X{_frac(t_nom)}'
    return Section(name, 'HSS', b, d, t, A, Iy, Iz, J, Zy, Zz, Sy, Sz,
                   math.sqrt(Iy / A), math.sqrt(Iz / A), A * STEEL_DENSITY * 12.0,
                   compact)


def _frac(v: float) -> str:
    """AISC-style dimension label: 3.5 -> 3-1/2, 0.1875 -> 3/16."""
    whole = int(v)
    rem = v - whole
    for den in (2, 4, 8, 16):
        num = round(rem * den)
        if abs(rem - num / den) < 1e-6 and num:
            g = math.gcd(num, den)
            frac = f'{num // g}/{den // g}'
            return f'{whole}-{frac}' if whole else frac
    return str(whole) if abs(rem) < 1e-6 else f'{v:g}'


def wide_flange(name, A, d, bf, tw, tf, Ix, Iy, Zx, Zy, Sx, Sy, J, rx, ry, wt) -> Section:
    return Section(name, 'W', bf, d, tf, A, Iy, Ix, J, Zy, Zx, Sy, Sx, ry, rx, wt, True)


def sawn_lumber(name: str, b: float, d: float) -> Section:
    A = b * d
    Iz, Iy = b * d ** 3 / 12.0, d * b ** 3 / 12.0
    # St Venant torsion for a solid rectangle
    a, c = max(b, d) / 2.0, min(b, d) / 2.0
    J = a * c ** 3 * (16.0 / 3.0 - 3.36 * c / a * (1.0 - c ** 4 / (12.0 * a ** 4)))
    return Section(name, 'wood', b, d, 0.0, A, Iy, Iz, J,
                   d * b * b / 4.0, b * d * d / 4.0, Iy / (b / 2.0), Iz / (d / 2.0),
                   math.sqrt(Iy / A), math.sqrt(Iz / A), A * WOOD_DENSITY * 12.0, True)


# --------------------------------------------------------------------------
# catalogue
# --------------------------------------------------------------------------

#: Lightest standard wall used when a member carries only a nominal envelope.
DEFAULT_WALL = {
    1.5: 0.125, 2.0: 0.125, 2.25: 0.125, 2.5: 0.125, 3.0: 0.125,
    3.5: 0.1875, 4.0: 0.1875, 5.0: 0.1875, 6.0: 0.25,
}

#: Square HSS ladder used by the downsizing search, lightest first.
HSS_LADDER = [
    (1.5, 0.125), (1.5, 0.1875), (2.0, 0.125), (2.0, 0.1875), (2.5, 0.125),
    (2.5, 0.1875), (3.0, 0.125), (3.0, 0.1875), (3.0, 0.25), (3.5, 0.1875),
    (3.5, 0.25), (4.0, 0.1875), (4.0, 0.25), (4.0, 0.375), (4.0, 0.5),
    (5.0, 0.1875), (5.0, 0.25), (5.0, 0.375), (6.0, 0.25), (6.0, 0.375),
]

W_SHAPES = {
    'W6X8.5': dict(A=2.52, d=5.83, bf=3.94, tw=0.170, tf=0.195, Ix=14.9, Iy=1.99,
                   Zx=5.73, Zy=1.01, Sx=5.10, Sy=1.01, J=0.0333, rx=2.43, ry=0.890, wt=8.5),
    'W8X24':  dict(A=7.08, d=7.93, bf=6.50, tw=0.245, tf=0.400, Ix=82.7, Iy=18.3,
                   Zx=23.1, Zy=8.57, Sx=20.9, Sy=5.63, J=0.346, rx=3.42, ry=1.61, wt=24.0),
    # Added for the BEAM-001 alternate scheme, whose beams are all W14X22.
    # wt, A, d, bf, tw, tf, Ix, Sx, Zx, Iy and ry agree exactly with this project's
    # other transcription, loft-span-study/wshapes.py. Sy, Zy, J and rx are added
    # here and each reproduces from the geometry: Sy = Iy/(bf/2) = 2.800;
    # Zy = tf*bf^2/2 + (d-2tf)*tw^2/4 = 4.36 vs 4.39 published (fillets);
    # rx = sqrt(Ix/A) = 5.537; J is above the thin-walled lower bound 0.178.
    'W14X22': dict(A=6.49, d=13.7, bf=5.00, tw=0.230, tf=0.335, Ix=199.0, Iy=7.00,
                   Zx=33.2, Zy=4.39, Sx=29.0, Sy=2.80, J=0.208, rx=5.54, ry=1.04, wt=22.0),
    # BEAM-001's primary section from revision 9. Same provenance and the same
    # checks as W14X22 above: wt, A, d, bf, tw, tf, Ix, Sx, Zx, Iy and ry are
    # loft-span-study/wshapes.py; Sy = Iy/(bf/2) = 1.4135 vs 1.41 published,
    # Zy = 2.248 vs 2.26, rx = sqrt(Ix/A) = 4.676 vs 4.67, and J = 0.103 is kept
    # at the published value rather than the 0.090 thin-walled lower bound.
    'W12X16': dict(A=4.71, d=12.0, bf=3.99, tw=0.220, tf=0.265, Ix=103.0, Iy=2.82,
                   Zx=20.1, Zy=2.26, Sx=17.1, Sy=1.41, J=0.103, rx=4.67, ry=0.773,
                   wt=16.0),
}

# --------------------------------------------------------------------------
# back-to-back double angle, forming a T
# --------------------------------------------------------------------------

def double_angle_tee(leg: float, t: float, name: str = '') -> Section:
    """Two equal-leg angles back to back, stems together, making a T.

    Requested for the BEAM-001 clerestory so the glazing has a rebate: the flange
    is the two coplanar legs and faces out, the stem is the two touching legs and
    points in. Everything below is computed from the two rectangles, not
    transcribed, and the area reproduces twice the AISC single-angle area.

        flange   2*leg wide by t thick     -- in the wall plane, faces out
        stem     2*t wide by (leg - t)     -- points inward, the window rebate

    Local axes follow this file's convention: ``d`` is the in-plane dimension
    (the flange, 2*leg) and ``z`` is its strong axis; ``b`` is the stem reach.
    """
    fw, ft = 2.0 * leg, t                  # flange width and thickness
    sw, sd = 2.0 * t, leg - t              # stem width and depth
    Af, As = fw * ft, sw * sd
    A = Af + As

    # Strong axis: bending in the plane of the flange, so the section is
    # symmetric about it and the centroid is at mid-flange-width.
    Iz = ft * fw ** 3 / 12.0 + sd * sw ** 3 / 12.0
    Sz = Iz / (fw / 2.0)
    Zz = ft * fw ** 2 / 4.0 + sd * sw ** 2 / 4.0

    # Weak axis: along the stem, unsymmetric, so locate the centroid first.
    yf, ys = ft / 2.0, ft + sd / 2.0
    ybar = (Af * yf + As * ys) / A
    Iy = (fw * ft ** 3 / 12.0 + Af * (ybar - yf) ** 2
          + sw * sd ** 3 / 12.0 + As * (ys - ybar) ** 2)
    depth = ft + sd
    Sy = Iy / max(ybar, depth - ybar)
    # Plastic neutral axis: equal areas. It falls in the flange whenever the
    # flange is the larger half, which it is for every angle used here.
    half = A / 2.0
    a = half / fw if half <= Af else ft
    Zy = (fw * a * (a / 2.0) + fw * (ft - a) * ((ft - a) / 2.0)
          + As * abs(ys - a))

    J = (fw * ft ** 3 + sd * sw ** 3) / 3.0        # thin-walled open section
    ry, rz = (Iy / A) ** 0.5, (Iz / A) ** 0.5
    # AISC Table B4.1: flange leg b/t against 0.38*sqrt(E/Fy), stem d/t against
    # 0.84*sqrt(E/Fy). Fy = 50 ksi.
    lim_f, lim_s = 0.38 * (29000.0 / 50.0) ** 0.5, 0.84 * (29000.0 / 50.0) ** 0.5
    compact = (leg / t) <= lim_f and (sd / sw) <= lim_s
    return Section(
        name=name or f'2L{leg:g}X{leg:g}X{t:g} back-to-back T',
        family='tee', b=ft + sd, d=fw, t=t, A=A, Iy=Iy, Iz=Iz, J=J,
        Zy=Zy, Zz=Zz, Sy=Sy, Sz=Sz, ry=ry, rz=rz,
        weight=A * 0.2836 * 12.0, compact=compact,
        note='two equal-leg angles back to back; properties computed from the '
             'two rectangles, glazing rebate on the stem side')


#: The double angles BEAM-001 uses, by the name its members reference.
TEE_SHAPES = {
    '2L3X3X3/8 T': (3.0, 0.375),
    '2L2X2X1/4 T': (2.0, 0.25),
}


_CACHE: dict[str, Section] = {}


def get(name: str) -> Section:
    """Resolve a section by AISC-style name, building it on first use."""
    if name in _CACHE:
        return _CACHE[name]
    if name in W_SHAPES:
        s = wide_flange(name, **W_SHAPES[name])
    elif name in TEE_SHAPES:
        s = double_angle_tee(*TEE_SHAPES[name], name=name)
    elif name.startswith('2x8'):
        s = sawn_lumber(name, 1.5, 7.25)
    else:
        raise KeyError(name)
    _CACHE[name] = s
    return s


def square(b: float, t_nom: float) -> Section:
    key = f'HSS{b:g}x{t_nom:g}'
    if key not in _CACHE:
        _CACHE[key] = hss_square(b, t_nom)
    return _CACHE[key]


def ladder() -> list[Section]:
    """The HSS downsizing ladder, ordered by weight."""
    return sorted((square(b, t) for b, t in HSS_LADDER), key=lambda s: s.weight)


if __name__ == '__main__':
    print(f"{'section':<26}{'A':>8}{'Iz':>9}{'Iy':>9}{'J':>9}{'Zz':>8}{'rz':>7}{'lb/ft':>8}  cpt")
    for s in ladder():
        print(f'{s.name:<26}{s.A:8.3f}{s.Iz:9.3f}{s.Iy:9.3f}{s.J:9.3f}{s.Zz:8.3f}'
              f'{s.rz:7.3f}{s.weight:8.2f}  {"Y" if s.compact else "N"}')
    for n in ('W6X8.5', 'W8X24', '2x8 DF'):
        s = get(n)
        print(f'{s.name:<26}{s.A:8.3f}{s.Iz:9.3f}{s.Iy:9.3f}{s.J:9.3f}{s.Zz:8.3f}'
              f'{s.rz:7.3f}{s.weight:8.2f}')
