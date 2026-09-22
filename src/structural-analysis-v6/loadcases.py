"""Apply the design load basis to a PyNite model of the frame.

Every area load becomes a distributed load on real members through
``surfaces.tributary``, and every case records what it applied so the run can
check that the total load reaching the model equals the load the basis calls for.

The east canopy is the one surface handled outside the tributary machinery.  Its
twelve rafters rake between 55 and 74 degrees from horizontal and are not
coplanar, so there is no surface to tessellate.  They are evenly spaced and
explicitly modelled, so each one is loaded directly over its own tributary width
and, being closer to vertical than to horizontal, takes wall pressure
coefficients under wind.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import frame as framemod
import loads as L
import surfaces as surf

IN2_PER_FT2 = 144.0

#: Parameter names differ between the two frame lineages; these are the ones the
#: load code needs, mapped to what each schema calls them.
PARAM_ALIAS = {
    'east_x': ('east_x', 'be_x'),
    'outer_east_x': ('outer_east_x', 'bew_x'),
    'west_x': ('west_x',),
    'south_y': ('south_y', 'b_so_y'),
    'north_y': ('north_y', 'b_n_y'),
    'top_z': ('square_top_z', 'beam_axis_z'),
}


def param(params: dict, name: str) -> float:
    for key in PARAM_ALIAS[name]:
        if key in params:
            return params[key]
    raise KeyError(f'{name}: none of {PARAM_ALIAS[name]} in the model parameters')


@dataclass
class Applied:
    """A tally of what one load case actually put into the model."""
    case: str
    fx: float = 0.0
    fy: float = 0.0          # model z, positive up
    fz: float = 0.0
    detail: dict = field(default_factory=dict)


class LoadBuilder:
    def __init__(self, frame: framemod.Frame, model, index: dict[str, list[str]],
                 params: dict, exposure: str | None = None):
        self.frame, self.model, self.index = frame, model, index
        self.params = params
        self.exposure = exposure or L.WIND['exposure']
        self.surfaces = surf.build_surfaces(frame, params)
        # Canopy members are loaded directly, so they must not also pick up
        # tributary area from any surface they happen to pass through.
        self._canopy_set = set(self._canopy_members())
        self.trib = {name: surf.tributary(frame, s, index,
                                          exclude_members=self._canopy_set)
                     for name, s in self.surfaces.items()}
        self.applied: dict[str, Applied] = {}
        self.node_weight: dict[str, float] = {}

    # -- primitives --------------------------------------------------------

    def _dist(self, element: str, direction: str, w: float, case: str):
        """Uniform load on one element. Direction is a PyNite global axis."""
        if abs(w) < 1e-9:
            return
        self.model.add_member_dist_load(element, direction, w, w, case=case)
        a = self.applied.setdefault(case, Applied(case))
        seg = self.model.members[element]
        Lp = seg.L()
        total = w * Lp
        if direction == 'FX':
            a.fx += total
        elif direction == 'FY':
            a.fy += total
        elif direction == 'FZ':
            a.fz -= total          # PyNite +Z is model -y

    def _point(self, node: str, direction: str, P: float, case: str):
        if abs(P) < 1e-9:
            return
        self.model.add_node_load(node, direction, P, case=case)
        a = self.applied.setdefault(case, Applied(case))
        if direction == 'FX':
            a.fx += P
        elif direction == 'FY':
            a.fy += P
        elif direction == 'FZ':
            a.fz -= P

    def _strip_true_area(self, strip: surf.Strip, s: surf.Surface) -> float:
        """Convert an in-plane tributary area to true surface area."""
        return strip.true_area

    # -- east canopy -------------------------------------------------------

    def _canopy_members(self) -> list[str]:
        """The steeply raking members bridging the two east column lines.

        Found by geometry, not by group name: the two lineages put these members
        in differently-named groups, and in the beam scheme the same group also
        holds the roof rafters.  A canopy member runs between the outer east line
        and the inner one and climbs further than it reaches, which is what makes
        it behave like a wall under wind rather than like a roof.
        """
        ex = param(self.params, 'east_x')
        oex = param(self.params, 'outer_east_x')
        reach = abs(oex - ex)
        out = []
        for member in self.frame.members:
            pts = [self.frame.xyz(n) for m, i, j in self.frame.segments
                   if m == member for n in (i, j)]
            xs = [q[0] for q in pts]
            if min(xs) < min(ex, oex) - 1.0:
                continue
            dx = max(xs) - min(xs)
            dz = max(q[2] for q in pts) - min(q[2] for q in pts)
            if abs(dx - reach) < 2.0 and dz > dx:
                out.append(member)
        return out

    def _canopy(self):
        """Canopy members with the tributary width each one carries."""
        rafters = sorted(self._canopy_members(), key=lambda m: self._rafter_y(m))
        if len(rafters) < 2:
            return [(m, 0.0) for m in rafters]
        ys = [self._rafter_y(m) for m in rafters]
        widths = []
        for k, y in enumerate(ys):
            lo = (y + ys[k - 1]) / 2 if k else y - (ys[1] - ys[0]) / 2
            hi = (y + ys[k + 1]) / 2 if k < len(ys) - 1 else y + (ys[-1] - ys[-2]) / 2
            widths.append(hi - lo)
        # Bevel-cut members may have a roof edge extending beyond the
        # analytical cut-face centroids. Preserve that explicitly stated area.
        return [(m,w*self.frame.members[m].get('canopy_area_factor',1.0))
                for m,w in zip(rafters,widths)]

    def _rafter_y(self, member: str) -> float:
        pts = [self.frame.xyz(n) for m, i, j in self.frame.segments
               if m == member for n in (i, j)]
        return sum(p[1] for p in pts) / len(pts)

    def _rafter_geometry(self, member: str):
        """(true length, horizontal run, unit normal in the x-z plane)."""
        segs = [(i, j) for m, i, j in self.frame.segments if m == member]
        a, b = self.frame.xyz(segs[0][0]), self.frame.xyz(segs[-1][1])
        dx, dz = b[0] - a[0], b[2] - a[2]
        Ltrue = math.hypot(dx, dz)
        n = (dz / Ltrue, 0.0, -dx / Ltrue)
        return Ltrue, abs(dx), (n if n[0] > 0 else (-n[0], 0.0, -n[2]))

    # -- gravity -----------------------------------------------------------

    def dead(self, case: str = 'D'):
        """Frame self weight plus superimposed dead load on every surface."""
        self.model.add_member_self_weight('FY', -1.0, case=case)
        sw = sum(self.frame.section_of[n.rsplit('#', 1)[0]].A
                 * framemod.MATERIALS[self.frame.material(n.rsplit('#', 1)[0])]['rho']
                 * el.L() for n, el in self.model.members.items()
                 if not n.startswith('LINK#'))
        a = self.applied.setdefault(case, Applied(case))
        a.fy -= sw
        a.detail['self_weight_lb'] = round(sw, 1)

        mapping = {}
        for name, srf in self.surfaces.items():
            if srf.kind == 'canopy':
                continue                       # loaded on its own members below
            if srf.kind == 'roof':
                mapping[name] = L.DEAD.get(name, L.DEAD['upper_roof'])
            elif srf.kind == 'floor':
                mapping[name] = L.DEAD['loft_floor']
            else:
                mapping[name] = L.DEAD['wall']
        for name, psf in mapping.items():
            s, t = self.surfaces[name], self.trib[name]
            total = 0.0
            for st in t.strips:
                area = self._strip_true_area(st, s)
                total += area
                w = psf / IN2_PER_FT2 * area / self.model.members[st.element].L()
                self._dist(st.element, 'FY', -w, case)
            a.detail[f'{name}_ft2'] = round(total / IN2_PER_FT2, 1)

        # east canopy: dead on the true raked area
        psf = L.DEAD['east_roof']
        for member, width in self._canopy():
            Ltrue, run, _ = self._rafter_geometry(member)
            w = psf / IN2_PER_FT2 * width          # lb per inch along the rafter
            for el in self.index.get(member, []):
                self._dist(el, 'FY', -w, case)
        a.detail['east_canopy_ft2'] = round(
            sum(self._rafter_geometry(m)[0] * wd for m, wd in self._canopy())
            / IN2_PER_FT2, 1)

    def separate_structure(self):
        """Loads handed over by structure that is analysed on its own.

        The east lean-to is a wood roof spanning the existing wall to
        ``BE.upper``. Modelling it inside the steel frame lets the frame lean on
        the old wall through it, which is the opposite of the intent, so it is
        analysed separately and only its reaction is applied here.
        """
        for member, case, w, _why in getattr(self.frame, 'extra_loads', ()):
            for el in self.index.get(member, []):
                self._dist(el, 'FY', -w, case)

    def roof_live(self, case: str = 'Lr'):
        """ASCE 7-16 Lr, on the horizontal projection of every roof."""
        psf = L.ROOF_LIVE
        for name in [n for n, x in self.surfaces.items() if x.kind == 'roof']:
            s, t = self.surfaces[name], self.trib[name]
            cos = abs(s.normal[2])
            for st in t.strips:
                plan = self._strip_true_area(st, s) * cos
                w = psf / IN2_PER_FT2 * plan / self.model.members[st.element].L()
                self._dist(st.element, 'FY', -w, case)
        for member, width in self._canopy():
            Ltrue, run, _ = self._rafter_geometry(member)
            plan = run * width
            w = psf / IN2_PER_FT2 * plan / Ltrue
            for el in self.index.get(member, []):
                self._dist(el, 'FY', -w, case)

    def loft_live(self, case: str, psf: float):
        """Storage live load on every floor surface the model declares."""
        for name in [n for n, x in self.surfaces.items() if x.kind == 'floor']:
            for st in self.trib[name].strips:
                w = psf / IN2_PER_FT2 * st.area_in2 / self.model.members[st.element].L()
                self._dist(st.element, 'FY', -w, case)

    def hoist(self, node: str, case: str = 'H'):
        """1,000 lb lifted load with 25 % vertical impact and 10 % lateral."""
        self._point(node, 'FY', -L.HOIST['factored'], case)
        self._point(node, 'FX', L.HOIST['capacity'] * L.HOIST['lateral'], case)

    # -- wind ---------------------------------------------------------------

    def wind(self, direction: tuple[float, float], tag: str, gcpi_sign: float):
        """ASCE 7-16 Ch. 27 directional pressures for one wind direction.

        ``direction`` is the direction the wind blows, in model (x, y).
        """
        case = f'{tag}.{"pi" if gcpi_sign > 0 else "ni"}'
        d = (direction[0], direction[1], 0.0)
        h_ft = self._mean_roof_height() / 12.0
        qh = L.qz(h_ft, self.exposure)
        B, Lp = self._plan_dims(d)
        cp_lee = L.cp_leeward_wall(Lp / B)
        gcpi = gcpi_sign * L.WIND['GCpi']
        G = L.WIND['G']

        for name, s in self.surfaces.items():
            t = self.trib[name]
            if not t.strips or s.kind == 'canopy':
                continue      # the canopy is loaded on its own rafters, below
            dot = sum(s.normal[i] * d[i] for i in range(3))
            for st in t.strips:
                area = self._strip_true_area(st, s)
                el = self.model.members[st.element]
                z_ft = self._element_height(st.element) / 12.0
                if s.kind == 'wall':
                    if dot < -0.5:
                        p = L.qz(z_ft, self.exposure) * G * L.CP_WALL_WINDWARD - qh * gcpi
                    elif dot > 0.5:
                        p = qh * G * cp_lee - qh * gcpi
                    else:
                        p = qh * G * L.CP_WALL_SIDE - qh * gcpi
                else:
                    p = qh * G * self._roof_cp(s, st, d, h_ft) - qh * gcpi
                self._apply_pressure(st.element, s.normal, p, area, case)

        # east canopy: raked face, wall coefficients on its own normal
        for member, width in self._canopy():
            Ltrue, run, n = self._rafter_geometry(member)
            area = Ltrue * width
            dot = sum(n[i] * d[i] for i in range(3))
            if dot < -0.5:
                z_ft = self._member_height(member) / 12.0
                p = L.qz(z_ft, self.exposure) * G * L.CP_WALL_WINDWARD - qh * gcpi
            elif dot > 0.5:
                p = qh * G * cp_lee - qh * gcpi
            else:
                p = qh * G * L.CP_WALL_SIDE - qh * gcpi
            for el in self.index.get(member, []):
                frac = self.model.members[el].L() / Ltrue
                self._apply_pressure(el, n, p, area * frac, case)

    def _mean_roof_height(self) -> float:
        """Highest roof elevation in the model, used as h for the wind pressures."""
        return max((v['z'] for v in self.frame.nodes.values()), default=1.0)

    def _roof_cp(self, s: surf.Surface, st: surf.Strip, d, h_ft: float) -> float:
        """Roof Cp for this strip, given the wind direction."""
        theta = s.slope_deg
        span_dir = (0.0, 1.0, 0.0)            # the solar roof slopes north-south
        along = abs(sum(span_dir[i] * d[i] for i in range(3)))
        hL = h_ft / self._plan_dims(d)[1]
        if theta < 10.0 or along < 0.5:
            edge = self._distance_from_windward_edge(st, d) / 12.0
            return L.cp_roof_parallel(edge, h_ft, hL)
        slope_faces = -s.normal[1]            # +1 if the roof faces south
        windward = (slope_faces * d[1]) < 0
        if windward:
            return L.cp_roof_windward(theta, hL)[0]
        return L.cp_roof_leeward(theta, hL)

    def _apply_pressure(self, element: str, normal, p: float, area: float, case: str):
        """Net pressure ``p`` in psf (inward positive) on ``area`` in square inches."""
        F = p / IN2_PER_FT2 * area
        el = self.model.members[element]
        Lp = el.L()
        # inward is -normal in model coordinates; convert to PyNite axes
        vec = framemod.to_fe((-normal[0] * F, -normal[1] * F, -normal[2] * F))
        for axis, comp in zip(('FX', 'FY', 'FZ'), vec):
            self._dist(element, axis, comp / Lp, case)

    def _plan_dims(self, d) -> tuple[float, float]:
        """(B across the wind, L along the wind) in feet."""
        wx, ex = param(self.params, 'west_x'), param(self.params, 'outer_east_x')
        sy, ny = param(self.params, 'south_y'), param(self.params, 'north_y')
        x_ft, y_ft = (ex - wx) / 12.0, (ny - sy) / 12.0
        return (y_ft, x_ft) if abs(d[0]) > abs(d[1]) else (x_ft, y_ft)

    def _distance_from_windward_edge(self, st: surf.Strip, d) -> float:  # noqa: C901
        el = self.model.members[st.element]
        mid = framemod.to_model((
            (el.i_node.X + el.j_node.X) / 2.0,
            (el.i_node.Y + el.j_node.Y) / 2.0,
            (el.i_node.Z + el.j_node.Z) / 2.0))
        if d[0] > 0.5:
            return mid[0] - param(self.params, 'west_x')
        if d[0] < -0.5:
            return param(self.params, 'outer_east_x') - mid[0]
        if d[1] > 0.5:
            return mid[1] - param(self.params, 'south_y')
        return param(self.params, 'north_y') - mid[1]

    def _element_height(self, element: str) -> float:
        el = self.model.members[element]
        return max(1.0, (el.i_node.Y + el.j_node.Y) / 2.0)

    def _member_height(self, member: str) -> float:
        els = self.index.get(member, [])
        return max(1.0, sum(self._element_height(e) for e in els) / len(els)) if els else 1.0

    # -- seismic ------------------------------------------------------------

    def seismic(self, axis: str, sign: float, weights: dict[str, float]):
        """ASCE 7-16 equivalent lateral force, distributed by nodal weight and height."""
        s = L.seismic_coefficient()
        W = sum(weights.values())
        V = s['Cs'] * W
        k = s['k']
        denom = sum(w * (self.model.nodes[n].Y / 12.0) ** k
                    for n, w in weights.items() if self.model.nodes[n].Y > 0)
        case = f'E{axis}{"+" if sign > 0 else "-"}'
        direction = 'FX' if axis == 'X' else 'FZ'
        for n, w in weights.items():
            h = self.model.nodes[n].Y / 12.0
            if h <= 0 or denom <= 0:
                continue
            self._point(n, direction, sign * V * w * h ** k / denom, case)
        self.applied.setdefault(case, Applied(case)).detail.update(
            base_shear_lb=round(V, 1), seismic_weight_lb=round(W, 1), Cs=round(s['Cs'], 4))
        return V, W

    def nodal_weights(self) -> dict[str, float]:
        """Effective seismic weight at each node: dead load lumped half to each end."""
        w: dict[str, float] = {n: 0.0 for n in self.model.nodes}
        for name, el in self.model.members.items():
            # PyNite stores self weight as a 'D' distributed load, so the loop
            # below already includes it -- do not add it a second time.
            for dl in el.DistLoads:
                if dl[0] == 'FY' and dl[5] == 'D':
                    q = -(dl[1] + dl[2]) / 2.0 * el.L()
                    w[el.i_node.name] += q / 2.0
                    w[el.j_node.name] += q / 2.0
        return {n: v for n, v in w.items() if v > 0}
