"""Build, solve and check the frame.

One ``run`` assembles the model, applies every load case from ``loads.py``,
solves all ASCE 7-16 combinations, and returns per-member demand-capacity ratios
together with the equilibrium and serviceability checks.  The same function does
the work for the intact frame, for a frame with a member deleted, and for a frame
with sections swapped, which is what lets the redundancy and downsizing studies
compare like with like.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

import codecheck
import frame as framemod
import loadcases
import loads as L
import sections
import surfaces

STATIONS = 7          # sampling points per element for the interaction check


@dataclass
class MemberOutcome:
    member: str
    group: str
    material: str
    section: str
    length: float
    weight: float
    dcr: float
    mode: str
    combo: str
    P: float
    Mz: float
    My: float
    V: float
    slenderness: float
    Lb: float
    basis: str
    flags: tuple = ()


@dataclass
class Result:
    frame_version: str
    live_case: str
    exposure: str
    members: dict[str, MemberOutcome] = field(default_factory=dict)
    equilibrium: dict = field(default_factory=dict)
    applied: dict = field(default_factory=dict)
    reactions: dict = field(default_factory=dict)
    drift: dict = field(default_factory=dict)
    deflection: dict = field(default_factory=dict)
    seismic: dict = field(default_factory=dict)
    gaps: list = field(default_factory=list)
    stable: bool = True
    message: str = ''

    @property
    def max_dcr(self) -> float:
        return max((m.dcr for m in self.members.values()), default=0.0)

    @property
    def total_weight(self) -> float:
        return sum(m.weight for m in self.members.values())

    def overstressed(self, limit: float = 1.0) -> list[MemberOutcome]:
        return sorted((m for m in self.members.values() if m.dcr > limit),
                      key=lambda m: -m.dcr)


# ---------------------------------------------------------------------------
# unbraced lengths
# ---------------------------------------------------------------------------

def unbraced_lengths(frame: framemod.Frame, omit: set[str] = frozenset()) -> dict[str, float]:
    """Longest run of a member between joints where something else frames in.

    A node counts as a brace point only if a member other than this one, and not
    itself deleted, connects there.  Supports always count.  The result is the
    unbraced length used for both buckling and lateral-torsional checks, which is
    why the redundancy study has to recompute it: deleting a brace lengthens the
    member it used to restrain.
    """
    out: dict[str, float] = {}
    for member in frame.members:
        if member in omit:
            continue
        segs = framemod._ordered(frame, [(i, j) for m, i, j in frame.segments
                                         if m == member])
        if not segs:
            continue
        chain = [segs[0][0]] + [j for _, j in segs]
        run, longest = 0.0, 0.0
        for k in range(len(segs)):
            run += frame.segment_length(*segs[k])
            node = chain[k + 1]
            others = {m for m in frame.nodes[node].get('members', [])
                      if m != member and m not in omit}
            braced = bool(others) or frame.nodes[node].get('support')
            if braced or k == len(segs) - 1:
                longest = max(longest, run)
                run = 0.0
        out[member] = max(longest, 1.0)
    for member, length in frame.unbraced_length_overrides.items():
        if member in out:
            out[member] = max(out[member], length)
    return out


# ---------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------

def run(frame: framemod.Frame, params: dict, live_case: str = 'L40',
        exposure: str | None = None, omit: set[str] | None = None,
        override: dict[str, sections.Section] | None = None,
        hoist_node: str | None = None, combos: dict | None = None,
        with_service: bool = True, second_order: bool = False) -> Result:
    omit = set(omit or ())
    exposure = exposure or L.WIND['exposure']
    res = Result(frame.version, live_case, exposure)

    model, index = framemod.build(frame, omit=omit, override=override)
    b = loadcases.LoadBuilder(frame, model, index, params, exposure)

    b.dead()
    b.separate_structure()
    b.roof_live()
    b.loft_live(live_case, L.LOFT_LIVE_CASES[live_case]['psf'])
    if hoist_node and hoist_node in model.nodes:
        b.hoist(hoist_node)

    for tag, d in (('WX+', (1.0, 0.0)), ('WX-', (-1.0, 0.0)),
                   ('WY+', (0.0, 1.0)), ('WY-', (0.0, -1.0))):
        for sign in (1.0, -1.0):
            b.wind(d, tag, sign)

    weights = b.nodal_weights()
    V = W = 0.0
    for axis in ('X', 'Z'):
        for sign in (1.0, -1.0):
            V, W = b.seismic(axis, sign, weights)
    res.seismic = dict(base_shear_lb=round(V, 1), seismic_weight_lb=round(W, 1),
                       **{k: round(v, 4) for k, v in L.seismic_coefficient().items()})

    strength = combos or L.strength_combos(live_case)
    service = L.service_combos(live_case) if with_service else {}
    # seismic cases are named EX+/EX-/EY+/EY- in the basis but EZ in PyNite axes
    rename = {'EY+': 'EZ-', 'EY-': 'EZ+'}
    for name, factors in list(strength.items()) + list(service.items()):
        model.add_load_combo(name, {rename.get(k, k): v for k, v in factors.items()})

    try:
        if second_order:
            model.analyze_PDelta(check_stability=True, sparse=True)
        else:
            model.analyze_linear(check_stability=True, check_statics=False, sparse=True)
    except Exception as exc:                       # singular stiffness matrix
        res.stable = False
        res.message = f'{type(exc).__name__}: {exc}'
        return res

    res.applied = {c: dict(fx=round(a.fx, 1), fy=round(a.fy, 1), fz=round(a.fz, 1),
                           **a.detail) for c, a in b.applied.items()}
    res.equilibrium = _equilibrium(model, b, strength)
    res.gaps = surfaces.report_gaps(frame, b.trib, b.surfaces)

    Lb = unbraced_lengths(frame, omit)
    res.members = _check_members(frame, model, index, Lb, list(strength),
                                 list(service), override)
    if service:
        res.drift, res.deflection = _serviceability(frame, model, index, params, service)
    res.reactions = _reactions(model, strength)
    if any(not math.isfinite(m.dcr) for m in res.members.values()):
        res.stable = False
        res.message = 'non-finite result'
    return res


def _joist_spacing(frame, member: str) -> float:
    """Centre-to-centre spacing of the repetitive set this member belongs to."""
    import spacing as _sp
    try:
        members = _sp.joist_sets(frame).get(member.rsplit(' joist', 1)[0], [])
        if len(members) < 2:
            return 99.0
        pos = sorted(_sp._across(frame, m) for m in members)
        return min(b - a for a, b in zip(pos, pos[1:]))
    except Exception:
        return 99.0


def _check_members(frame, model, index, Lb_map, strength, service, override):
    out: dict[str, MemberOutcome] = {}
    override = override or {}
    for member, elements in index.items():
        sec = override.get(member, frame.section_of[member])
        mat = frame.material(member)
        Fy = framemod.MATERIALS[mat]['fy']
        Lb = Lb_map.get(member, 1.0)
        is_wood = mat == 'wood'
        repetitive = is_wood and _joist_spacing(frame, member) <= 24.01
        combos = service if is_wood else strength
        best = None
        for el in elements:
            m = model.members[el]
            for combo in combos:
                P = m.axial_array(STATIONS, combo)[1]
                Mz = m.moment_array('Mz', STATIONS, combo)[1]
                My = m.moment_array('My', STATIONS, combo)[1]
                Vy = m.shear_array('Fy', STATIONS, combo)[1]
                for k in range(len(P)):
                    if is_wood:
                        c = codecheck.check_wood(member, sec, P[k], Mz[k], My[k],
                                                 Vy[k], Lb, combo, m.L(),
                                                 repetitive=repetitive)
                    else:
                        c = codecheck.check_steel(member, sec, Fy, P[k], Mz[k],
                                                  My[k], Vy[k], Lb, combo)
                    if best is None or c.dcr > best.dcr:
                        best = c
        if best is None:
            continue
        out[member] = MemberOutcome(
            member, frame.group(member), mat, sec.name,
            frame.member_length(member),
            sec.A * framemod.MATERIALS[mat]['rho'] * frame.member_length(member),
            best.dcr, best.mode, best.combo, best.P, best.Mz, best.My, best.V,
            best.slenderness, Lb, best.basis, best.flags)
    return out


def _equilibrium(model, builder, strength) -> dict:
    """Applied load against summed reactions, for every gravity combination."""
    checks = {}
    for combo in ('C1 1.4D', 'C2 1.2D+1.6L+0.5Lr', 'C3 1.2D+1.6Lr+1.0L'):
        if combo not in strength:
            continue
        applied = 0.0
        for case, factor in strength[combo].items():
            a = builder.applied.get(case)
            if a:
                applied += factor * a.fy
        reaction = sum(model.nodes[n].RxnFY[combo] for n in model.nodes
                       if model.nodes[n].support_DY)
        checks[combo] = dict(applied_lb=round(applied, 1),
                             reaction_lb=round(reaction, 1),
                             residual_lb=round(applied + reaction, 3),
                             relative=round(abs(applied + reaction) /
                                            max(abs(applied), 1.0), 8))
    return checks


def _reactions(model, strength) -> dict:
    out = {}
    for n in model.nodes.values():
        if not n.support_DY:
            continue
        rows = {c: dict(FX=round(n.RxnFX[c], 1), FY=round(n.RxnFY[c], 1),
                        FZ=round(n.RxnFZ[c], 1)) for c in strength}
        uplift = min(r['FY'] for r in rows.values())
        out[n.name] = dict(
            max_compression=round(max(0.0, max(r['FY'] for r in rows.values())), 1),
            max_uplift=round(max(0.0, -uplift), 1),
            max_vertical=round(max(r['FY'] for r in rows.values()), 1),
            max_shear=round(max(math.hypot(r['FX'], r['FZ']) for r in rows.values()), 1))
    return out


#: Span-deflection limits: (service combination, denominator of L/n).
DEFLECTION_RULE = {
    'floor': ('S2 D+L', DEFLECTION_LIMITS_FLOOR := 240.0),
    'roof': ('S3 D+Lr', DEFLECTION_LIMITS_ROOF := 180.0),
}
FLOOR_GROUPS = {'LoftJoists', 'LoftSteel', 'Joists', 'Beams'}


def _span_class(frame, member: str) -> str | None:
    """Which deflection rule applies, or None for a member that does not span."""
    if frame.group(member) in FLOOR_GROUPS:
        return 'floor'
    pts = [frame.xyz(n) for m, i, j in frame.segments if m == member for n in (i, j)]
    if len(pts) < 2:
        return None
    rise = max(p[2] for p in pts) - min(p[2] for p in pts)
    run = max(math.dist((p[0], p[1]), (q[0], q[1])) for p in pts for q in pts)
    if run < 36.0 or rise > 0.5 * run:
        return None                      # a column or a short member has no span
    return 'roof'


def deflection_violations(frame, result) -> list[dict]:
    """Members whose span deflection exceeds its limit."""
    out = []
    for member, rec in (result.deflection or {}).items():
        cls = _span_class(frame, member)
        if cls is None:
            continue
        combo, denom = DEFLECTION_RULE[cls]
        d = rec.get(combo)
        if not d or not d.get('ratio'):
            continue
        if d['ratio'] < denom:
            out.append(dict(member=member, group=frame.group(member), rule=cls,
                            span_in=rec['span_in'], combo=combo,
                            deflection_in=d['defl_in'], ratio=d['ratio'],
                            limit=denom))
    return sorted(out, key=lambda v: v['ratio'])


def _serviceability(frame, model, index, params, service) -> tuple[dict, dict]:
    """Wind drift at the roof, and span deflections of the floor and roof beams.

    Deflection is measured against the chord between the member's own two end
    joints, not element by element.  A floor beam with joists framing into it is
    split into a dozen elements, and each one looks almost straight relative to
    its own ends while the beam as a whole sags.
    """
    # Drift is measured at the top of the structure, which each lineage names
    # differently; read it off the model instead of a parameter.
    h = max((n.Y for n in model.nodes.values()), default=1.0)
    drift = {}
    for combo in service:
        if not combo.startswith('S5'):
            continue
        worst = 0.0
        for n in model.nodes.values():
            if n.Y < h - 6.0:
                continue
            worst = max(worst, math.hypot(n.DX[combo], n.DZ[combo]))
        drift[combo] = dict(drift_in=round(worst, 4),
                            ratio=round(h / worst, 0) if worst > 1e-6 else None)

    defl = {}
    for member, elements in index.items():
        span = frame.member_length(member)
        if span < 36.0 or not elements:
            continue
        ends = (model.members[elements[0]].i_node, model.members[elements[-1]].j_node)
        chord = math.dist((ends[0].X, ends[0].Y, ends[0].Z),
                          (ends[1].X, ends[1].Y, ends[1].Z))
        if chord < 1e-6:
            continue
        run = 0.0
        stations = []
        for el in elements:
            m = model.members[el]
            for f in (0.0, 0.25, 0.5, 0.75):
                stations.append((el, f, (run + f * m.L()) / chord))
            run += m.L()
        for combo in service:
            if combo.startswith('S5'):
                continue
            a, b = ends[0].DY[combo], ends[1].DY[combo]
            worst = 0.0
            for el, f, t in stations:
                m = model.members[el]
                y = m.deflection_array('dy', 5, combo)[1][int(round(f * 4))]
                worst = min(worst, y - (a + t * (b - a)))
            rec = defl.setdefault(member, dict(span_in=round(span, 1)))
            rec[combo] = dict(defl_in=round(worst, 4),
                              ratio=round(span / abs(worst), 0)
                              if abs(worst) > 1e-6 else None)
    return drift, defl
