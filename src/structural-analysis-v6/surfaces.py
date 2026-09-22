"""Load surfaces and tributary-area distribution.

The frame model contains no plates, decks or secondary framing, so area loads
have to be resolved onto the line members that are present.  Doing that by hand
means drawing tributary strips and arguing about the edges.  This module does it
geometrically instead, by one rule applied to every surface:

    Sample every member lying in the surface at roughly 8-inch intervals, build a
    Voronoi tessellation of those samples clipped to the surface outline, and give
    each sample the load on its own cell.  A member's samples are then collapsed
    back into a uniform distributed load on each of its segments.

Because a clipped Voronoi diagram partitions the outline exactly, the total load
applied always equals pressure times surface area -- which the analysis checks
explicitly rather than assuming.  Members get real distributed load and therefore
real local bending, and the result adapts on its own when the frame changes,
instead of depending on a hand-written list of which member carries what.

Where a surface has no framing across it, the rule puts the whole load on the
perimeter members, which is the correct statement of the model as drawn: the
secondary framing is not in it.  ``report_gaps`` names those surfaces so the
omission is visible in the report rather than silently absorbed.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import shapely
from shapely.geometry import Polygon, Point

import frame as framemod

SAMPLE_SPACING = 8.0     # in, along-member sampling interval
IN2_PER_FT2 = 144.0


# ---------------------------------------------------------------------------
# surface definition
# ---------------------------------------------------------------------------

@dataclass
class Surface:
    """A planar load surface, with a mapping from model space into its plane."""
    name: str
    kind: str                       # 'roof' | 'floor' | 'wall'
    origin: tuple                   # a point on the plane, model coords
    u: tuple                        # in-plane axis 1 (unit, model coords)
    v: tuple                        # in-plane axis 2 (unit, model coords)
    normal: tuple                   # outward unit normal, model coords
    outline: Polygon                # in (u, v) coordinates, inches
    tolerance: float = 6.0          # how far off-plane a member may sit
    label: str = ''

    def to_uv(self, p) -> tuple[float, float]:
        d = [p[i] - self.origin[i] for i in range(3)]
        return (sum(d[i] * self.u[i] for i in range(3)),
                sum(d[i] * self.v[i] for i in range(3)))

    def offset(self, p) -> float:
        d = [p[i] - self.origin[i] for i in range(3)]
        return sum(d[i] * self.normal[i] for i in range(3))

    @property
    def area_in2(self) -> float:
        return self.outline.area

    @property
    def area_ft2(self) -> float:
        return self.outline.area / IN2_PER_FT2

    @property
    def slope_deg(self) -> float:
        return math.degrees(math.acos(min(1.0, abs(self.normal[2]))))

    @property
    def plan_area_ft2(self) -> float:
        """Horizontal projection, for loads specified on the projected area."""
        return self.area_ft2 * abs(self.normal[2])


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


# ---------------------------------------------------------------------------
# the surfaces of this building, derived from the model's own parameters
# ---------------------------------------------------------------------------

def build_surfaces(frame: framemod.Frame, params: dict) -> dict[str, Surface]:
    """Load surfaces for whichever frame lineage this is.

    The two lineages describe the same building with different structure, so they
    need different surface definitions but the same tributary machinery.
    Dispatch is on the model's own schema string rather than on a guess about
    which parameters are present.
    """
    if frame.schema.startswith('garage.beam-scheme'):
        return _beam_scheme_surfaces(frame, params)
    return _connected_frame_surfaces(frame, params)


def _connected_frame_surfaces(frame: framemod.Frame, params: dict) -> dict[str, Surface]:
    p = params
    wx, ex = p['west_x'], p['east_x']
    sy, ny, cy = p['south_y'], p['north_y'], p['clerestory_y']
    bz, tz, sz = p['bottom_z'], p['square_top_z'], p['solar_start_z']
    slope = p['solar_slope']
    oex, eobz = p['outer_east_x'], p['eob_z']
    ridge_z = sz + slope * (cy - sy)          # top of the solar slope at the clerestory

    S: dict[str, Surface] = {}

    # -- solar roof: 30 deg plane facing south --------------------------------
    n = _unit((0.0, -slope, 1.0))
    S['solar_roof'] = Surface(
        'solar_roof', 'roof', (wx, sy, sz),
        u=(1.0, 0.0, 0.0), v=_unit((0.0, 1.0, slope)), normal=n,
        outline=Polygon([(0, 0), (ex - wx, 0),
                         (ex - wx, (cy - sy) * math.hypot(1, slope)),
                         (0, (cy - sy) * math.hypot(1, slope))]),
        label='South-facing photovoltaic roof, 30 deg')

    # -- upper roof: flat cap over the loft -----------------------------------
    S['upper_roof'] = Surface(
        'upper_roof', 'roof', (wx, cy, tz),
        u=(1.0, 0.0, 0.0), v=(0.0, 1.0, 0.0), normal=(0.0, 0.0, 1.0),
        outline=Polygon([(0, 0), (ex - wx, 0), (ex - wx, ny - cy), (0, ny - cy)]),
        label='Flat upper roof with low hip cap')

    # -- east lean-to roof ----------------------------------------------------
    # Not a plane: the twelve rafters rake between 55 and 74 degrees and their
    # tops land at different heights.  Kept as a 'canopy' so its area is reported,
    # but loaded directly in loadcases.LoadBuilder rather than tessellated.
    S['east_roof'] = Surface(
        'east_roof', 'canopy', (ex, sy, eobz),
        u=(1.0, 0.0, 0.0), v=(0.0, 1.0, 0.0), normal=_unit((-0.6, 0.0, 0.8)),
        outline=Polygon([(0, 0), (oex - ex, 0), (oex - ex, ny - sy), (0, ny - sy)]),
        tolerance=80.0,
        label='East lean-to roof over the side walkway')

    # -- loft floor -----------------------------------------------------------
    S['loft_floor'] = Surface(
        'loft_floor', 'floor', (wx, cy, bz + 1.0),
        u=(1.0, 0.0, 0.0), v=(0.0, 1.0, 0.0), normal=(0.0, 0.0, 1.0),
        outline=Polygon([(0, 0), (ex - wx, 0), (ex - wx, ny - cy), (0, ny - cy)]),
        tolerance=3.0,
        label='Upper storage floor')

    # -- walls ----------------------------------------------------------------
    gable = [(0, 0), (0, sz - 0.0), (cy - sy, ridge_z), (cy - sy, tz),
             (ny - sy, tz), (ny - sy, 0)]
    S['west_wall'] = Surface(
        'west_wall', 'wall', (wx, sy, 0.0),
        u=(0.0, 1.0, 0.0), v=(0.0, 0.0, 1.0), normal=(-1.0, 0.0, 0.0),
        outline=Polygon(gable), label='West wall')
    S['east_wall'] = Surface(
        'east_wall', 'wall', (ex, sy, 0.0),
        u=(0.0, 1.0, 0.0), v=(0.0, 0.0, 1.0), normal=(1.0, 0.0, 0.0),
        outline=Polygon([(y, max(z, 0.0)) for y, z in gable]).intersection(
            Polygon([(0, eobz), (ny - sy, eobz), (ny - sy, tz + 1), (0, tz + 1)])),
        label='East wall above the lean-to roof')
    S['east_outer_wall'] = Surface(
        'east_outer_wall', 'wall', (oex, sy, 0.0),
        u=(0.0, 1.0, 0.0), v=(0.0, 0.0, 1.0), normal=(1.0, 0.0, 0.0),
        outline=Polygon([(0, 0), (ny - sy, 0), (ny - sy, eobz), (0, eobz)]),
        tolerance=3.0, label='Outer east wall below the lean-to roof')
    S['south_wall'] = Surface(
        'south_wall', 'wall', (wx, sy, 0.0),
        u=(1.0, 0.0, 0.0), v=(0.0, 0.0, 1.0), normal=(0.0, -1.0, 0.0),
        outline=Polygon([(0, 0), (ex - wx, 0), (ex - wx, sz), (0, sz)]),
        label='South wall below the solar roof')
    S['north_wall'] = Surface(
        'north_wall', 'wall', (wx, ny, 0.0),
        u=(1.0, 0.0, 0.0), v=(0.0, 0.0, 1.0), normal=(0.0, 1.0, 0.0),
        outline=Polygon([(0, 0), (ex - wx, 0), (ex - wx, tz), (0, tz)]),
        label='North wall with the loading opening')
    S['clerestory'] = Surface(
        'clerestory', 'wall', (wx, cy, 0.0),
        u=(1.0, 0.0, 0.0), v=(0.0, 0.0, 1.0), normal=(0.0, -1.0, 0.0),
        outline=Polygon([(0, ridge_z), (ex - wx, ridge_z), (ex - wx, tz), (0, tz)]),
        tolerance=4.0, label='South-facing clerestory glazing')
    return S


# ---------------------------------------------------------------------------
# tributary distribution
# ---------------------------------------------------------------------------

@dataclass
class Strip:
    """One member segment's share of a surface."""
    member: str
    element: str
    length: float                    # in-plane length of the part inside the outline
    area_in2: float = 0.0            # tributary area, measured in the surface plane
    rake: float = 1.0                # true 3-D length / in-plane length of the segment

    @property
    def true_area(self) -> float:
        """Tributary area on the real surface, not on its projection."""
        return self.area_in2 * self.rake


@dataclass
class Tributary:
    surface: str
    strips: list[Strip] = field(default_factory=list)
    assigned_in2: float = 0.0
    surface_in2: float = 0.0
    members: set[str] = field(default_factory=set)

    @property
    def closure(self) -> float:
        """Assigned area divided by true surface area -- an equilibrium check."""
        return self.assigned_in2 / self.surface_in2 if self.surface_in2 else 0.0


def tributary(frame: framemod.Frame, surf: Surface, index: dict[str, list[str]],
              exclude_groups: set[str] = frozenset(),
              exclude_members: set[str] = frozenset()) -> Tributary:
    """Split ``surf`` among the member segments lying in it.

    Members in ``exclude_groups`` take no area load.  Diagonal bracing is always
    excluded: an in-plane roof or wall brace resists forces in its own plane and
    is not what the deck or purlins bear on, so giving it tributary area would
    load it in a way the detailing never intends.  Its share passes to the real
    framing around it.
    """
    samples: list[tuple[float, float]] = []
    owner: list[tuple[str, str, float, float]] = []   # member, element, sub-length, rake

    for member, elements in index.items():
        if (member in exclude_members or frame.group(member) in exclude_groups
                or frame.group(member) == 'Bracing'):
            continue
        segs = [(i, j) for m, i, j in frame.segments if m == member]
        segs = framemod._ordered(frame, segs)
        for el, (i, j) in zip(elements, segs):
            a, b = frame.xyz(i), frame.xyz(j)
            if abs(surf.offset(a)) > surf.tolerance or abs(surf.offset(b)) > surf.tolerance:
                continue
            ua, ub = surf.to_uv(a), surf.to_uv(b)
            L = math.hypot(ub[0] - ua[0], ub[1] - ua[1])
            if L < 1e-6:
                continue
            rake = frame.segment_length(i, j) / L
            n = max(1, int(round(L / SAMPLE_SPACING)))
            for k in range(n):
                f = (k + 0.5) / n
                pt = (ua[0] + f * (ub[0] - ua[0]), ua[1] + f * (ub[1] - ua[1]))
                if surf.outline.buffer(1.0).contains(Point(pt)):
                    samples.append(pt)
                    owner.append((member, el, L / n, rake))

    trib = Tributary(surface=surf.name, surface_in2=surf.area_in2)
    if not samples:
        return trib

    pts, keep = _dedupe(samples)
    owner = [owner[i] for i in keep]
    cells = _voronoi_areas(pts, surf.outline)

    acc: dict[tuple[str, str], float] = {}
    lengths: dict[tuple[str, str], float] = {}
    rakes: dict[tuple[str, str], float] = {}
    for (member, el, sub, rake), area in zip(owner, cells):
        acc[(member, el)] = acc.get((member, el), 0.0) + area
        lengths[(member, el)] = lengths.get((member, el), 0.0) + sub
        rakes[(member, el)] = rake
    for (member, el), area in sorted(acc.items()):
        trib.strips.append(Strip(member, el, lengths[(member, el)], area,
                                 rakes[(member, el)]))
        trib.members.add(member)
        trib.assigned_in2 += area
    return trib


def _dedupe(pts: list[tuple[float, float]], tol: float = 0.25):
    """Drop coincident samples -- Voronoi needs distinct sites."""
    out, keep, seen = [], [], set()
    for i, p in enumerate(pts):
        key = (round(p[0] / tol), round(p[1] / tol))
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
        keep.append(i)
    return out, keep


def _voronoi_areas(pts: list[tuple[float, float]], outline: Polygon) -> list[float]:
    """Clipped Voronoi cell areas, one per input point, in input order.

    Voronoi cells of nearly-collinear sites can come back with self-touching
    boundaries that GEOS refuses to intersect.  Repairing the cell is enough --
    the areas are unchanged for every well-formed cell, and a cell that cannot be
    repaired is worth no area anyway.
    """
    if len(pts) == 1:
        return [outline.area]
    mp = shapely.MultiPoint(pts)
    env = outline.buffer(max(outline.bounds[2] - outline.bounds[0],
                             outline.bounds[3] - outline.bounds[1]))
    cells = shapely.voronoi_polygons(mp, extend_to=env, ordered=True)
    clean = outline if outline.is_valid else shapely.make_valid(outline)
    areas = []
    for c in cells.geoms:
        try:
            areas.append(max(0.0, c.intersection(clean).area))
        except Exception:
            try:
                areas.append(max(0.0, shapely.make_valid(c).intersection(clean).area))
            except Exception:
                areas.append(0.0)
    return areas


def report_gaps(frame: framemod.Frame, tribs: dict[str, Tributary],
                surfaces: dict[str, Surface]) -> list[dict]:
    """Surfaces whose load lands only on their perimeter -- no framing across them."""
    gaps = []
    for name, t in tribs.items():
        s = surfaces[name]
        if s.kind not in ('roof', 'floor'):   # a canopy has no surface to span
            continue
        span = max(s.outline.bounds[2] - s.outline.bounds[0],
                   s.outline.bounds[3] - s.outline.bounds[1])
        interior = [st for st in t.strips if _crosses(frame, surfaces[name], st.member)]
        if not interior:
            gaps.append(dict(surface=name, label=s.label,
                             area_ft2=round(s.area_ft2, 1),
                             clear_span_in=round(span, 1),
                             members=sorted(t.members),
                             issue='no framing crosses this surface in the model; '
                                   'its secondary framing is not modelled and its '
                                   'load is delivered directly to the perimeter'))
    return gaps


def _crosses(frame: framemod.Frame, surf: Surface, member: str) -> bool:
    """True when some part of the member runs through the interior of the surface.

    Tested at segment midpoints rather than at joints, because a member that
    spans the surface has both of its ends on the perimeter.
    """
    edge = surf.outline.exterior
    for m, i, j in frame.segments:
        if m != member:
            continue
        a, b = surf.to_uv(frame.xyz(i)), surf.to_uv(frame.xyz(j))
        mid = Point((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        if surf.outline.contains(mid) and edge.distance(mid) > 2.0:
            return True
    return False


# ---------------------------------------------------------------------------
# the beam scheme
# ---------------------------------------------------------------------------

def _level(frame: framemod.Frame, y: float, above: float, pick=max,
           tol: float = 1.0) -> float:
    """A characteristic z of the nodes standing on one east-west line."""
    zs = [v['z'] for v in frame.nodes.values()
          if abs(v['y'] - y) < tol and v['z'] > above + tol]
    if not zs:
        raise ValueError(f'no nodes above z={above} on y={y}')
    return pick(zs)


def _beam_scheme_surfaces(frame: framemod.Frame, params: dict) -> dict[str, Surface]:
    """Surfaces for the BEAM-001 grillage.

    Its floor is declared: the model carries six deck rectangles, so the loft
    bays and the shelves are taken straight from the specification instead of
    being inferred from where the joists happen to be.  The roof is not
    declared, but the rafters that form it are in the model and every elevation
    the surfaces need is read back off the geometry rather than hard-coded --
    this scheme has already moved its roof planes once.
    """
    p = params
    wx, ex, oex = p['west_x'], p['be_x'], p['bew_x']
    sy, cy, ny = p['b_so_y'], p['b_1_y'], p['b_n_y']
    floor_z, wall_top = p['beam_axis_z'], p['wall_top_z']

    # Read the actual supporting members. After a floor raise, selecting the
    # lowest node above the OLD beam elevation selects the floor itself as the
    # solar roof. Upper-east beam nodes can likewise masquerade as CT.bottom.
    def member_z(name, fallback, at_y=None):
        zs = [frame.xyz(n)[2] for m, i, j in frame.segments if m == name
              for n in (i, j)
              if at_y is None or abs(frame.xyz(n)[1] - at_y) < 0.01]
        return sum(zs) / len(zs) if zs else fallback()

    floor_z = member_z('B-SO', lambda: floor_z)
    eave_z = member_z('W.slope', lambda: _level(frame, sy, floor_z, min), sy)
    cler_bottom = member_z('CT.bottom', lambda: _level(frame, cy, floor_z, min))
    roof_z = member_z('CT.top', lambda: _level(frame, cy, floor_z, max))
    slope = (cler_bottom - eave_z) / (cy - sy)

    S: dict[str, Surface] = {}
    S['solar_roof'] = Surface(
        'solar_roof', 'roof', (wx, sy, eave_z),
        u=(1.0, 0.0, 0.0), v=_unit((0.0, 1.0, slope)), normal=_unit((0.0, -slope, 1.0)),
        outline=Polygon([(0, 0), (ex - wx, 0),
                         (ex - wx, (cy - sy) * math.hypot(1, slope)),
                         (0, (cy - sy) * math.hypot(1, slope))]),
        label='South-facing photovoltaic roof, 30 deg')
    S['upper_roof'] = Surface(
        'upper_roof', 'roof', (wx, cy, roof_z),
        u=(1.0, 0.0, 0.0), v=(0.0, 1.0, 0.0), normal=(0.0, 0.0, 1.0),
        outline=Polygon([(0, 0), (ex - wx, 0), (ex - wx, ny - cy), (0, ny - cy)]),
        label='Flat upper roof on the flat rafters')
    S['east_roof'] = Surface(
        'east_roof', 'canopy', (ex, sy, floor_z),
        u=(1.0, 0.0, 0.0), v=(0.0, 1.0, 0.0), normal=_unit((-0.6, 0.0, 0.8)),
        outline=Polygon([(0, 0), (oex - ex, 0), (oex - ex, ny - sy), (0, ny - sy)]),
        tolerance=80.0, label='East raking face over the side walkway')

    # -- floor: one surface per declared deck --------------------------------
    for deck in frame.decks:
        x0, x1 = deck['x']
        y0, y1 = deck['y']
        key = deck['name'].replace(' ', '_')
        S[key] = Surface(
            key, 'floor', (x0, y0, floor_z),
            u=(1.0, 0.0, 0.0), v=(0.0, 1.0, 0.0), normal=(0.0, 0.0, 1.0),
            outline=Polygon([(0, 0), (x1 - x0, 0), (x1 - x0, y1 - y0), (0, y1 - y0)]),
            tolerance=8.0,
            label=f"{deck['name']} -- declared deck, {deck['area_sf']:.0f} sq ft")

    # -- walls ----------------------------------------------------------------
    gable = [(0, 0), (0, eave_z), (cy - sy, cler_bottom), (cy - sy, roof_z),
             (ny - sy, roof_z), (ny - sy, 0)]
    S['west_wall'] = Surface(
        'west_wall', 'wall', (wx, sy, 0.0),
        u=(0.0, 1.0, 0.0), v=(0.0, 0.0, 1.0), normal=(-1.0, 0.0, 0.0),
        outline=Polygon(gable), label='West wall')
    S['east_wall'] = Surface(
        'east_wall', 'wall', (ex, sy, 0.0),
        u=(0.0, 1.0, 0.0), v=(0.0, 0.0, 1.0), normal=(1.0, 0.0, 0.0),
        outline=Polygon(gable).intersection(
            Polygon([(0, floor_z), (ny - sy, floor_z),
                     (ny - sy, roof_z + 5.0), (0, roof_z + 5.0)])),
        label='East wall above the raking face')
    S['east_outer_wall'] = Surface(
        'east_outer_wall', 'wall', (oex, sy, 0.0),
        u=(0.0, 1.0, 0.0), v=(0.0, 0.0, 1.0), normal=(1.0, 0.0, 0.0),
        outline=Polygon([(0, 0), (ny - sy, 0), (ny - sy, floor_z), (0, floor_z)]),
        tolerance=4.0, label='Outer east wall below the raking face')
    S['south_wall'] = Surface(
        'south_wall', 'wall', (wx, sy, 0.0),
        u=(1.0, 0.0, 0.0), v=(0.0, 0.0, 1.0), normal=(0.0, -1.0, 0.0),
        outline=Polygon([(0, 0), (ex - wx, 0), (ex - wx, eave_z), (0, eave_z)]),
        label='South wall below the solar roof')
    S['north_wall'] = Surface(
        'north_wall', 'wall', (wx, ny, 0.0),
        u=(1.0, 0.0, 0.0), v=(0.0, 0.0, 1.0), normal=(0.0, 1.0, 0.0),
        outline=Polygon([(0, 0), (ex - wx, 0), (ex - wx, roof_z), (0, roof_z)]),
        label='North wall with the loading opening')
    S['clerestory'] = Surface(
        'clerestory', 'wall', (wx, cy, 0.0),
        u=(1.0, 0.0, 0.0), v=(0.0, 0.0, 1.0), normal=(0.0, -1.0, 0.0),
        outline=Polygon([(0, cler_bottom), (ex - wx, cler_bottom),
                         (ex - wx, roof_z), (0, roof_z)]),
        tolerance=4.0, label='South-facing clerestory glazing')
    return S
