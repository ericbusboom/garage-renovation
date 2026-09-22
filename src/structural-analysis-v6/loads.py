"""Design load basis for the garage frame.

Every number here is a documented input, not a result.  Sources are named in the
``SOURCES`` table and reproduced in the issued report.  Units are inches, pounds,
and pounds per square foot unless a name says otherwise.

Governing documents
-------------------
2022 California Building Code, which adopts ASCE/SEI 7-16 for loads.  ASCE 7-22
values are quoted where they differ materially, because the next code cycle will
move the project onto them.

The one load that is *not* settled by code alone is the loft live load.

ASCE 7-16 Table 4.3-1 gives 40 psf for "all other areas" of a dwelling, which is
an ordinary residential floor, and 125 psf for a light storage *warehouse*, which
is a commercial occupancy this building is not.  Neither describes a backyard
workshop loft holding equipment and served by a 1,000 lb hoist.  The code numbers
are minimums, not targets, and for a floor carrying dense point loads the uniform
figure is the wrong thing to reason about on its own.

The project therefore designs to 75 psf by owner decision (DEC-008), and 40 and
125 psf are retained as analysis cases so the cost of the choice stays visible.
See ``LOFT_LIVE_CASES``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# site
# ---------------------------------------------------------------------------

SITE = dict(
    address='1370 Wilbur Avenue, San Diego, CA 92109',
    risk_category='II',
    code='2022 CBC / ASCE 7-16',
    ground_snow_pg=0.0,          # psf -- no snow load in coastal San Diego
)

# ---------------------------------------------------------------------------
# gravity -- superimposed dead load (frame self weight is computed, not assumed)
# ---------------------------------------------------------------------------

#: Superimposed dead load, psf.  Frame self weight is computed from the assigned
#: sections and is never included here.
#:
#: The cladding is aluminium by owner direction.  Aluminium weighs 169 pcf
#: against steel's 490, so a panel of the same gauge is roughly a third of the
#: weight -- the build-ups below are light on purpose and are not a place to
#: find savings.  Every line is a component, not a rounded allowance, so that a
#: change to the specification can be traced to a change in the number.
DEAD_BUILDUP = {
    'solar_roof': [
        ('photovoltaic modules, framed crystalline', 2.8),
        ('module rails and clamps', 1.2),
        ('aluminium standing-seam roof panel, 0.032 in.', 0.9),
        ('purlins and clips', 2.5),
        ('fasteners, flashing, miscellaneous', 0.6),
    ],
    'upper_roof': [
        ('aluminium standing-seam roof panel, 0.032 in.', 0.9),
        ('rigid insulation, 2 in. polyisocyanurate', 0.6),
        ('purlins and clips', 3.0),
        ('low hip cap framing', 2.0),
        ('membrane, flashing, fasteners, miscellaneous', 1.5),
    ],
    'east_roof': [
        ('aluminium panel on exposed rafters, no ceiling', 0.9),
        ('clips, flashing, fasteners', 0.6),
        ('miscellaneous', 0.5),
    ],
    'loft_floor': [
        ('23/32 in. OSB structural deck', 2.4),
        ('underlayment and finish', 1.7),
        ('lighting, conduit, small services', 1.5),
        ('miscellaneous and construction tolerance', 2.4),
    ],
    'wall': [
        ('aluminium wall panel, 0.040 in. profiled', 1.2),
        ('sub-girts and hat channel', 2.0),
        ('insulation, weather barrier, fasteners', 1.0),
        ('miscellaneous', 0.8),
    ],
}

DEAD = {k: round(sum(w for _, w in items), 1) for k, items in DEAD_BUILDUP.items()}

#: The deck alternatives, for the record.  OSB is the heavier of the two and is
#: what ``DEAD_BUILDUP`` carries, so the floor is checked on the heavier option.
DECK_OPTIONS = {
    '23/32 in. OSB': 2.4,
    '3/4 in. plywood': 2.3,
}

MATERIAL_DENSITY = {
    'aluminium': 169.0,      # pcf
    'steel': 490.0,
    'douglas fir-larch': 32.0,
    'plywood': 36.0,
    'osb': 40.0,
}


# ---------------------------------------------------------------------------
# gravity -- live
# ---------------------------------------------------------------------------

ROOF_LIVE = 20.0         # psf, ASCE 7-16 Table 4.3-1, Lr on horizontal projection,
                         # taken unreduced (R1 reduction for At ~ 240-310 sf would
                         # give ~18 psf; the 2 psf is left in as margin)

#: Readings of "storage", all analysed.  ``DESIGN_LIVE_CASE`` is the one the
#: design is carried out against; the others are retained for comparison.
DESIGN_LIVE_CASE = 'L100'

LOFT_LIVE_CASES = {
    'L40': dict(
        psf=40.0,
        basis='ASCE 7-16 Table 4.3-1, dwelling "all other areas" -- an ordinary '
              'residential floor; the value previously assumed in ASM-006',
        status='code minimum for a dwelling floor; light for an equipment loft',
    ),
    'L75': dict(
        psf=75.0,
        basis='Intermediate equipment-loft value considered before DEC-014',
        status='superseded by the 100 psf owner direction; retained for comparison',
    ),
    'L100': dict(
        psf=100.0,
        basis='Owner direction, carried in the BEAM-001 model as design_live_psf; '
              'adopted for both schemes so they compare on one basis (DEC-014)',
        status='design value',
    ),
    'L125': dict(
        psf=125.0,
        basis='ASCE 7-16 Table 4.3-1, "Storage warehouses, light" -- a commercial '
              'warehouse occupancy, retained as an upper bound',
        status='upper bound; applies only if the space is classified as a storage '
               'occupancy, which is not expected for a residential accessory building',
    ),
}

#: Monorail hoist, owner requirement.
HOIST = dict(
    capacity=1000.0,        # lb
    impact=0.25,            # ASCE 7-16 Sec. 4.6.2, monorail crane vertical impact
    lateral=0.10,           # 10 % of lifted load, applied laterally
    factored=1250.0,        # capacity * (1 + impact)
)

# ---------------------------------------------------------------------------
# wind -- ASCE 7-16 Chapter 27, Directional Procedure, Part 1
# ---------------------------------------------------------------------------

WIND = dict(
    V=96.0,              # mph, 3-s gust, Risk Category II, San Diego
    exposure='C',        # primary case; 'D' run as a sensitivity
    Kd=0.85,             # Table 26.6-1, main wind force resisting system
    Kzt=1.0,             # flat site, no topographic speed-up
    Ke=1.0,              # ground elevation factor, sea level
    G=0.85,              # rigid building gust-effect factor, Sec. 26.11.1
    GCpi=0.18,           # enclosed building, Table 26.13-1, applied both signs
    enclosure='enclosed',
)

#: Terrain exponents, ASCE 7-16 Table 26.11-1.
EXPOSURE = {'B': (7.0, 1200.0), 'C': (9.5, 900.0), 'D': (11.5, 700.0)}


def Kz(z_ft: float, exposure: str = 'C') -> float:
    """Velocity pressure exposure coefficient, ASCE 7-16 Table 26.10-1."""
    alpha, zg = EXPOSURE[exposure]
    z = max(z_ft, 15.0 if exposure == 'B' else 15.0)
    return 2.01 * (z / zg) ** (2.0 / alpha)


def qz(z_ft: float, exposure: str | None = None, V: float | None = None) -> float:
    """Velocity pressure in psf, ASCE 7-16 Eq. 26.10-1."""
    exposure = exposure or WIND['exposure']
    V = V or WIND['V']
    return 0.00256 * Kz(z_ft, exposure) * WIND['Kzt'] * WIND['Kd'] * WIND['Ke'] * V ** 2


# --- external pressure coefficients, ASCE 7-16 Fig. 27.3-1 -----------------

def cp_leeward_wall(L_over_B: float) -> float:
    """Leeward wall Cp, interpolated on L/B."""
    pts = [(0.0, -0.5), (1.0, -0.5), (2.0, -0.3), (4.0, -0.2), (99.0, -0.2)]
    return _interp(L_over_B, pts)


CP_WALL_WINDWARD = 0.8
CP_WALL_SIDE = -0.7

#: Windward roof Cp for wind normal to the ridge, keyed by h/L then by slope.
#: Each entry is (negative case, positive case); the positive case is None where
#: the figure gives only one value.
_CP_ROOF_WW = {
    0.25: [(10, -0.7, -0.18), (15, -0.5, 0.0), (20, -0.3, 0.2), (25, -0.2, 0.3),
           (30, -0.2, 0.3), (35, 0.0, 0.4), (45, 0.4, 0.4), (60, 0.6, 0.6)],
    0.50: [(10, -0.9, -0.18), (15, -0.7, -0.18), (20, -0.4, 0.0), (25, -0.3, 0.2),
           (30, -0.2, 0.2), (35, -0.2, 0.3), (45, 0.0, 0.4), (60, 0.6, 0.6)],
    1.00: [(10, -1.3, -0.18), (15, -1.0, -0.18), (20, -0.7, -0.18), (25, -0.5, 0.0),
           (30, -0.3, 0.2), (35, -0.2, 0.2), (45, 0.0, 0.3), (60, 0.6, 0.6)],
}

#: Leeward roof Cp for wind normal to the ridge.
_CP_ROOF_LW = {
    0.25: [(10, -0.3), (15, -0.5), (20, -0.6), (90, -0.6)],
    0.50: [(10, -0.5), (15, -0.5), (20, -0.6), (90, -0.6)],
    1.00: [(10, -0.7), (15, -0.6), (20, -0.6), (90, -0.6)],
}


def cp_roof_windward(theta_deg: float, h_over_L: float) -> tuple[float, float]:
    """(uplift case, downward case) windward roof Cp, wind normal to the ridge."""
    keys = sorted(_CP_ROOF_WW)
    lo, hi = _bracket(h_over_L, keys)
    a = (_interp(theta_deg, [(t, n) for t, n, _ in _CP_ROOF_WW[lo]]),
         _interp(theta_deg, [(t, p) for t, _, p in _CP_ROOF_WW[lo]]))
    b = (_interp(theta_deg, [(t, n) for t, n, _ in _CP_ROOF_WW[hi]]),
         _interp(theta_deg, [(t, p) for t, _, p in _CP_ROOF_WW[hi]]))
    f = 0.0 if hi == lo else (h_over_L - lo) / (hi - lo)
    return (a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1]))


def cp_roof_leeward(theta_deg: float, h_over_L: float) -> float:
    keys = sorted(_CP_ROOF_LW)
    lo, hi = _bracket(h_over_L, keys)
    a = _interp(theta_deg, _CP_ROOF_LW[lo])
    b = _interp(theta_deg, _CP_ROOF_LW[hi])
    f = 0.0 if hi == lo else (h_over_L - lo) / (hi - lo)
    return a + f * (b - a)


def cp_roof_parallel(dist_from_edge_ft: float, h_ft: float, h_over_L: float) -> float:
    """Roof Cp for wind parallel to the ridge, or any roof with theta < 10 deg.

    Returns the uplift (negative) branch; the figure's -0.18 branch never governs
    a frame that is also carrying gravity load.
    """
    d = dist_from_edge_ft
    if h_over_L <= 0.5:
        if d <= h_ft:
            return -0.9
        if d <= 2.0 * h_ft:
            return -0.5
        return -0.3
    if d <= h_ft / 2.0:
        return -1.3
    return -0.7


def _interp(x: float, pts: list[tuple[float, float]]) -> float:
    pts = sorted(pts)
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 if x1 == x0 else y0 + (x - x0) * (y1 - y0) / (x1 - x0)
    return pts[-1][1]


def _bracket(x: float, keys: list[float]) -> tuple[float, float]:
    lo = max([k for k in keys if k <= x], default=keys[0])
    hi = min([k for k in keys if k >= x], default=keys[-1])
    return lo, hi


# ---------------------------------------------------------------------------
# seismic -- ASCE 7-16 Chapter 12, equivalent lateral force (screening only)
# ---------------------------------------------------------------------------

SEISMIC = dict(
    Ss=1.00, S1=0.37,        # mapped accelerations, coastal San Diego
    site_class='D',          # default where no geotechnical investigation exists
    Fa=1.0, Fv=1.66,         # Tables 11.4-1 / 11.4-2
    R=3.25,                  # ordinary concentrically braced frame, Table 12.2-1
    Ie=1.0, Ct=0.02, x=0.75,
    sdc='D',
    note='Screening check only. Not a seismic design, and the system has not been '
         'detailed or qualified as an OCBF.',
)


def seismic_coefficient() -> dict:
    s = SEISMIC
    SDS = (2.0 / 3.0) * s['Fa'] * s['Ss']
    SD1 = (2.0 / 3.0) * s['Fv'] * s['S1']
    h_ft = 228.75 / 12.0
    Ta = s['Ct'] * h_ft ** s['x']
    Cs = SDS / (s['R'] / s['Ie'])
    Cs_max = SD1 / (Ta * (s['R'] / s['Ie']))
    Cs_min = max(0.044 * SDS * s['Ie'], 0.01)
    Cs = max(min(Cs, Cs_max), Cs_min)
    return dict(SDS=SDS, SD1=SD1, Ta=Ta, Cs=Cs, Cs_max=Cs_max, Cs_min=Cs_min, k=1.0)


# ---------------------------------------------------------------------------
# load combinations -- ASCE 7-16 Sec. 2.3 (strength) and 2.4 / App. C (service)
# ---------------------------------------------------------------------------

WIND_DIRS = ['WX+', 'WX-', 'WY+', 'WY-']
WIND_IP = ['pi', 'ni']              # internal pressure sign, +GCpi / -GCpi
SEISMIC_DIRS = ['EX+', 'EX-', 'EY+', 'EY-']


def strength_combos(live_case: str = 'L40') -> dict[str, dict[str, float]]:
    """ASCE 7-16 LRFD combinations 1 through 7, expanded over wind/seismic cases."""
    L = live_case
    c: dict[str, dict[str, float]] = {
        'C1 1.4D': {'D': 1.4},
        'C2 1.2D+1.6L+0.5Lr': {'D': 1.2, L: 1.6, 'H': 1.6, 'Lr': 0.5},
        'C3 1.2D+1.6Lr+1.0L': {'D': 1.2, 'Lr': 1.6, L: 1.0, 'H': 1.0},
    }
    for d in WIND_DIRS:
        for ip in WIND_IP:
            w = f'{d}.{ip}'
            c[f'C4 1.2D+1.0W+1.0L+0.5Lr [{w}]'] = {'D': 1.2, w: 1.0, L: 1.0, 'H': 1.0, 'Lr': 0.5}
            c[f'C5 0.9D+1.0W [{w}]'] = {'D': 0.9, w: 1.0}
    for e in SEISMIC_DIRS:
        c[f'C6 1.2D+1.0E+1.0L [{e}]'] = {'D': 1.2, e: 1.0, L: 1.0}
        c[f'C7 0.9D+1.0E [{e}]'] = {'D': 0.9, e: 1.0}
    return c


def service_combos(live_case: str = 'L40') -> dict[str, dict[str, float]]:
    """Unfactored combinations used for deflection, ASCE 7-16 App. C."""
    L = live_case
    c = {
        'S1 D': {'D': 1.0},
        'S2 D+L': {'D': 1.0, L: 1.0, 'H': 1.0},
        'S3 D+Lr': {'D': 1.0, 'Lr': 1.0},
        'S4 D+0.75L+0.75Lr': {'D': 1.0, L: 0.75, 'H': 0.75, 'Lr': 0.75},
    }
    for d in WIND_DIRS:
        c[f'S5 D+0.6W [{d}.pi]'] = {'D': 1.0, f'{d}.pi': 0.6}
    return c


#: Serviceability limits, IBC Table 1604.3 and common practice.
DEFLECTION_LIMITS = {
    'roof_live': 240.0,       # L/240 for Lr on members supporting a non-plaster ceiling
    'roof_total': 180.0,      # L/180 total load
    'floor_live': 360.0,      # L/360 for L
    'floor_total': 240.0,     # L/240 total load
    'drift_wind': 400.0,      # H/400, wind drift, common serviceability target
    'drift_seismic': 50.0,    # H/50, ASCE 7-16 Table 12.12-1 allowable story drift, Risk II
}

SOURCES = [
    ('Basic wind speed 96 mph, Risk Category II, San Diego',
     'ASCE 7-16 Fig. 26.5-1A as adopted by 2022 CBC; ASCE 7-22 places coastal San '
     'Diego in the 95-100 mph band for Risk Category II.'),
    ('Roof live load 20 psf', 'ASCE 7-16 Table 4.3-1'),
    ('Light storage live load 125 psf', 'ASCE 7-16 Table 4.3-1'),
    ('Loft live load 100 psf (design value)',
     'Owner direction DEC-014, matching design_live_psf in the BEAM-001 model; '
     'above the ASCE 7-16 dwelling minimum of 40 psf and '
     'below the 125 psf light-storage-warehouse value, neither of which describes '
     'an equipment loft. Code values are minimums, not targets.'),
    ('Concentrated equipment loads',
     'ASCE 7-16 Sec. 4.4 requires a concentrated load check where it governs. A '
     'dense item on a small footprint can exceed any of these uniform values '
     'locally; the heavy items and their footprints must be scheduled by the owner.'),
    ('Hoist 1,000 lb with 25 % vertical impact',
     'Owner requirement; impact per ASCE 7-16 Sec. 4.6.2'),
    ('No snow load', 'ASCE 7-16 Fig. 7.2-1, pg = 0 for coastal San Diego'),
    ('Aluminium cladding and roof panel',
     'Owner direction. Aluminium at 169 pcf; 0.032-0.040 in. sheet with sub-girts. '
     'Component build-ups are in DEAD_BUILDUP.'),
    ('23/32 in. OSB floor deck at 2.4 psf',
     'OSB at 40 pcf. The 3/4 in. plywood alternative is 2.3 psf; the heavier of '
     'the two is carried so the floor is checked on the governing option.'),
    ('Seismic Ss = 1.00 g, S1 = 0.37 g, Site Class D',
     'Screening values for coastal San Diego; site-specific values and a site class '
     'from a geotechnical investigation are required before design.'),
]
