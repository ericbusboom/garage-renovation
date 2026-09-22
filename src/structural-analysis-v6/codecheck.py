"""Member strength checks.

Steel follows AISC 360-16 with LRFD resistance factors, applied to the factored
demands from the ASCE 7-16 strength combinations.  Sawn lumber follows NDS
allowable stress design against the service combinations, because that is the
basis the reference design values belong to.  Both are reported as a
demand-capacity ratio where 1.0 means "exactly at capacity", so a single map can
show the whole frame -- with the basis named per member in the schedule.

What is checked
---------------
Axial tension (D2), axial compression including flexural buckling (E3), flexure
of compact and non-compact HSS and W shapes (F2/F7), shear (G), and the combined
axial-plus-flexure interaction (H1-1).  Slenderness is reported against the
KL/r <= 200 recommendation for compression members.

What is not checked, and must be before anything is built
---------------------------------------------------------
Connections of any kind, base plates and anchorage, foundations, web local
crippling, torsion combined with flexure in open shapes, fatigue from hoist use,
fire, corrosion, second-order (P-Delta) amplification beyond the linear solution,
and any seismic detailing requirement.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import sections

PHI_T = 0.90      # tension yielding
PHI_C = 0.90      # compression
PHI_B = 0.90      # flexure
PHI_V = 0.90      # shear
E_STEEL = 29000.0     # ksi
SLENDER_LIMIT_C = 200.0
SLENDER_LIMIT_T = 300.0

# NDS reference design values, Douglas fir-larch No. 2, 2 in. nominal
WOOD = dict(Fb=900.0, Fv=180.0, Fc=1350.0, Ft=575.0, E=1.6e6,
            CD=1.0,      # load duration, occupancy live load
            Cr=1.15,     # repetitive member -- only when spacing is 24 in. or less
            note='DF-L No. 2, Fb 900 psi, adjusted by CD, CF and Cr')

#: NDS Supplement Table 4A size factor for bending, 2 in. nominal thickness.
#: It falls as the member gets deeper, so a deeper joist does not gain quite as
#: much capacity as its section modulus suggests.
SIZE_FACTOR_CF = [(3.5, 1.5), (5.5, 1.3), (7.25, 1.2), (9.25, 1.1), (11.25, 1.0)]


def size_factor(depth: float) -> float:
    for d, cf in SIZE_FACTOR_CF:
        if depth <= d + 0.01:
            return cf
    return 0.9


@dataclass
class Check:
    member: str
    basis: str                # 'AISC 360-16 LRFD' | 'NDS ASD'
    dcr: float
    mode: str                 # what governs
    combo: str
    P: float = 0.0            # lb, + tension
    Mz: float = 0.0           # lb-in, strong axis
    My: float = 0.0
    V: float = 0.0
    slenderness: float = 0.0
    phiPn_c: float = 0.0
    phiPn_t: float = 0.0
    phiMn_z: float = 0.0
    phiMn_y: float = 0.0
    flags: tuple = ()


# ---------------------------------------------------------------------------
# steel
# ---------------------------------------------------------------------------

def compression_capacity(sec: sections.Section, Fy_ksi: float, KL: float,
                         axis: str = 'weak') -> float:
    """phi*Pn in kips for flexural buckling about the given axis, AISC E3."""
    r = sec.ry if axis == 'weak' else sec.rz
    if r <= 0 or KL <= 0:
        return PHI_C * Fy_ksi * sec.A
    slr = KL / r
    Fe = math.pi ** 2 * E_STEEL / slr ** 2
    if slr <= 4.71 * math.sqrt(E_STEEL / Fy_ksi):
        Fcr = 0.658 ** (Fy_ksi / Fe) * Fy_ksi
    else:
        Fcr = 0.877 * Fe
    return PHI_C * Fcr * sec.A


def flexural_capacity(sec: sections.Section, Fy_ksi: float, Lb: float,
                      axis: str = 'strong') -> float:
    """phi*Mn in kip-in, AISC F2 (W shapes) / F7 (HSS)."""
    Z = sec.Zz if axis == 'strong' else sec.Zy
    S = sec.Sz if axis == 'strong' else sec.Sy
    Mp = Fy_ksi * Z
    if sec.family == 'HSS':
        if not sec.compact:            # non-compact wall, F7.2(b)
            b_t = (sec.b - 3.0 * sec.t) / sec.t
            Mn = min(Mp, Mp - (Mp - Fy_ksi * S)
                     * (3.57 * b_t * math.sqrt(Fy_ksi / E_STEEL) - 4.0))
        else:
            Mn = Mp
        # A square or rectangular HSS bent about its strong axis is not subject
        # to lateral-torsional buckling at any practical unbraced length.
        return PHI_B * Mn
    if axis == 'weak':
        return PHI_B * min(Mp, 1.6 * Fy_ksi * S)
    # W shape, strong axis, Cb taken as 1.0
    ry, J, Sx = sec.ry, sec.J, sec.Sz
    ho = sec.d - sec.t
    rts = math.sqrt(math.sqrt(sec.Iy * (sec.Iy * ho ** 2 / 4.0)) / Sx) if Sx else ry
    Lp = 1.76 * ry * math.sqrt(E_STEEL / Fy_ksi)
    c = 1.0
    Lr = (1.95 * rts * E_STEEL / (0.7 * Fy_ksi)
          * math.sqrt(J * c / (Sx * ho) + math.sqrt((J * c / (Sx * ho)) ** 2
                      + 6.76 * (0.7 * Fy_ksi / E_STEEL) ** 2)))
    if Lb <= Lp:
        Mn = Mp
    elif Lb <= Lr:
        Mn = min(Mp, Mp - (Mp - 0.7 * Fy_ksi * Sx) * (Lb - Lp) / (Lr - Lp))
    else:
        Fcr = (math.pi ** 2 * E_STEEL / (Lb / rts) ** 2
               * math.sqrt(1.0 + 0.078 * J * c / (Sx * ho) * (Lb / rts) ** 2))
        Mn = min(Mp, Fcr * Sx)
    return PHI_B * Mn


def shear_capacity(sec: sections.Section, Fy_ksi: float) -> float:
    """phi*Vn in kips, AISC G4 (HSS) / G2 (W)."""
    if sec.family == 'HSS':
        Aw = 2.0 * (sec.d - 3.0 * sec.t) * sec.t
    else:
        Aw = sec.d * sec.t if sec.t else sec.A
        Aw = sec.d * 0.245 if sec.name == 'W8X24' else (
             sec.d * 0.170 if sec.name == 'W6X8.5' else Aw)
    return PHI_V * 0.6 * Fy_ksi * Aw


def check_steel(member: str, sec: sections.Section, Fy_psi: float,
                P: float, Mz: float, My: float, V: float,
                Lb: float, combo: str) -> Check:
    """One member against AISC 360-16. Forces in lb and lb-in, lengths in inches."""
    Fy = Fy_psi / 1000.0
    Pk, Mzk, Myk, Vk = abs(P) / 1000.0, abs(Mz) / 1000.0, abs(My) / 1000.0, abs(V) / 1000.0

    phiPn_t = PHI_T * Fy * sec.A
    phiPn_c = min(compression_capacity(sec, Fy, Lb, 'weak'),
                  compression_capacity(sec, Fy, Lb, 'strong'))
    phiMn_z = flexural_capacity(sec, Fy, Lb, 'strong')
    phiMn_y = flexural_capacity(sec, Fy, Lb, 'weak')
    phiVn = shear_capacity(sec, Fy)

    # PyNite reports axial force with compression POSITIVE (a column under a
    # downward load returns +P; see cabinet_frame_study.py, 2026-09-19). The
    # check read it the other way round until then, so every compressed member
    # was measured against tension yield instead of flexural buckling.
    Pc = phiPn_c if P > 0 else phiPn_t
    ratio_P = Pk / Pc if Pc else 0.0
    ratio_M = (Mzk / phiMn_z if phiMn_z else 0.0) + (Myk / phiMn_y if phiMn_y else 0.0)

    if ratio_P >= 0.2:
        dcr = ratio_P + (8.0 / 9.0) * ratio_M
        mode = 'H1-1a combined axial + flexure'
    else:
        dcr = ratio_P / 2.0 + ratio_M
        mode = 'H1-1b combined axial + flexure'
    v_ratio = Vk / phiVn if phiVn else 0.0
    if v_ratio > dcr:
        dcr, mode = v_ratio, 'shear'
    if ratio_M > 0.98 * dcr and ratio_P < 0.05:
        mode = 'flexure'
    elif ratio_P > 0.98 * dcr and ratio_M < 0.05:
        mode = 'compression' if P > 0 else 'tension'

    r_min = min(sec.ry, sec.rz)
    slr = Lb / r_min if r_min else 0.0
    flags = []
    limit = SLENDER_LIMIT_C if P > 0 else SLENDER_LIMIT_T
    if slr > limit:
        flags.append(f'KL/r = {slr:.0f} exceeds {limit:.0f}')
    if not sec.compact:
        flags.append('non-compact HSS wall')

    return Check(member, 'AISC 360-16 LRFD', dcr, mode, combo, P, Mz, My, V,
                 slr, phiPn_c * 1000.0, phiPn_t * 1000.0,
                 phiMn_z * 1000.0, phiMn_y * 1000.0, tuple(flags))


# ---------------------------------------------------------------------------
# wood
# ---------------------------------------------------------------------------

def check_wood(member: str, sec: sections.Section, P: float, Mz: float, My: float,
               V: float, Lb: float, combo: str, span: float,
               deflection: float = 0.0, repetitive: bool = True) -> Check:
    """Sawn joist against NDS allowable stress design, service loads.

    ``repetitive`` carries Cr, which NDS allows only where the members are no
    more than 24 in. apart and share load through the deck. Widening the spacing
    past that loses the 15 % it is worth, which is part of what a spacing study
    has to pay for.
    """
    w = WOOD
    Fb = (w['Fb'] * w['CD'] * size_factor(sec.d)
          * (w['Cr'] if repetitive else 1.0))
    Fv = w['Fv'] * w['CD']
    fb = abs(Mz) / sec.Sz if sec.Sz else 0.0
    fb_y = abs(My) / sec.Sy if sec.Sy else 0.0
    fv = 1.5 * abs(V) / sec.A if sec.A else 0.0
    dcr = max(fb / Fb + fb_y / Fb, fv / Fv)
    mode = 'bending' if fb / Fb >= fv / Fv else 'horizontal shear'

    flags = []
    if span > 0 and deflection > 0:
        allow = span / 360.0
        if deflection > allow:
            flags.append(f'live deflection L/{span / deflection:.0f} exceeds L/360')
    return Check(member, 'NDS ASD', dcr, mode, combo, P, Mz, My, V,
                 Lb / min(sec.ry, sec.rz) if min(sec.ry, sec.rz) else 0.0,
                 0.0, 0.0, Fb * sec.Sz, Fb * sec.Sy, tuple(flags))
