"""Parallel-chord truss alternatives for the same span, solved rather than estimated.

A truss is the obvious answer to a long span, but the two things that decide
whether it is the *right* answer here are both quantitative: how much shallower
it lets the framing be for the same stiffness, and how many fitted joints it
costs.  ``EW-TRUSS-PROCUREMENT.md`` established that on this project joints, not
pounds, drive the price --- a 187 lb truss with 22 joints quotes higher than a
491 lb rolled beam with none.  So both numbers are reported.

The truss is analysed as a plane pin-jointed assembly by direct stiffness.  That
is the right model for a Warren truss with a deck on the top chord: loads land
at panel points, and the axial deformations that the solve captures are the
whole of the deflection apart from a small chord-bending term.  Sizing then
walks the project's own HSS ladder from ``structural-analysis-v6/sections.py``,
so the sections offered here are sections the rest of the project already uses.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'structural-analysis-v6'))

import sections as v6sections      # noqa: E402  the project's HSS library
from wshapes import E, FY          # noqa: E402

PHI_T = 0.90      # AISC 360-16 D2, tension yielding
PHI_C = 0.90      # AISC 360-16 E1, compression
K = 1.0           # effective length factor, pinned-pinned web and chord panels


@dataclass
class TrussResult:
    depth_in: float
    n_panels: int
    chord: object                  # sections.Section
    web: object
    span_in: float
    forces: dict[str, float] = field(default_factory=dict)   # lb, + tension
    defl_live_in: float = 0.0
    defl_total_in: float = 0.0
    weight_lb: float = 0.0
    n_joints: int = 0
    max_dcr: float = 0.0
    governing: str = ''

    @property
    def span_over_depth(self) -> float:
        return self.span_in / self.depth_in


def _solve(nodes: np.ndarray, bars: list[tuple[int, int]], areas: np.ndarray,
           fixed: dict[int, tuple[bool, bool]], loads: dict[int, tuple[float, float]]):
    """Plane pin-jointed direct stiffness.  Returns (displacements, bar forces).

    ``nodes`` is (n, 2) in inches, ``areas`` in in^2, loads in kips, E in ksi.
    """
    n = len(nodes)
    Kg = np.zeros((2 * n, 2 * n))
    lengths = np.zeros(len(bars))
    cosines = np.zeros((len(bars), 2))
    for b, (i, j) in enumerate(bars):
        d = nodes[j] - nodes[i]
        Lb = float(np.hypot(*d))
        lengths[b] = Lb
        c, s = d / Lb
        cosines[b] = (c, s)
        k = E * areas[b] / Lb
        T = np.array([-c, -s, c, s])
        dof = [2 * i, 2 * i + 1, 2 * j, 2 * j + 1]
        Kg[np.ix_(dof, dof)] += k * np.outer(T, T)

    F = np.zeros(2 * n)
    for node, (fx, fz) in loads.items():
        F[2 * node] += fx
        F[2 * node + 1] += fz

    free = np.ones(2 * n, dtype=bool)
    for node, (rx, rz) in fixed.items():
        if rx:
            free[2 * node] = False
        if rz:
            free[2 * node + 1] = False

    u = np.zeros(2 * n)
    u[free] = np.linalg.solve(Kg[np.ix_(free, free)], F[free])

    forces = np.zeros(len(bars))
    for b, (i, j) in enumerate(bars):
        c, s = cosines[b]
        du = np.array([u[2 * i], u[2 * i + 1], u[2 * j], u[2 * j + 1]])
        forces[b] = E * areas[b] / lengths[b] * float(np.array([-c, -s, c, s]) @ du)
    return u, forces, lengths


def _geometry(span_in: float, depth_in: float, n_panels: int):
    """Warren truss, top chord at the floor line, verticals at every panel point.

    Top chord nodes 0..n_panels, bottom chord nodes offset half a panel so the
    diagonals rake symmetrically.  Bottom chord is one panel shorter than the top,
    which is what a Warren with the deck on top actually looks like.
    """
    step = span_in / n_panels
    top = [(i * step, 0.0) for i in range(n_panels + 1)]
    bot = [((i + 0.5) * step, -depth_in) for i in range(n_panels)]
    nodes = np.array(top + bot, dtype=float)
    nt = len(top)

    bars: list[tuple[int, int]] = []
    kinds: list[str] = []
    for i in range(n_panels):
        bars.append((i, i + 1)); kinds.append('top chord')
    for i in range(n_panels - 1):
        bars.append((nt + i, nt + i + 1)); kinds.append('bottom chord')
    for i in range(n_panels):
        bars.append((i, nt + i)); kinds.append('diagonal')
        bars.append((nt + i, i + 1)); kinds.append('diagonal')
    return nodes, bars, kinds, nt


def analyse(span_in: float, depth_in: float, n_panels: int,
            wD_plf: float, wL_plf: float,
            chord, web) -> TrussResult:
    """Run one truss: service deflections, factored forces, weight, joint count."""
    nodes, bars, kinds, nt = _geometry(span_in, depth_in, n_panels)
    areas = np.array([chord.A if k.endswith('chord') else web.A for k in kinds])

    # self weight, smeared as an extra line load on the top chord
    total_len = sum(float(np.hypot(*(nodes[j] - nodes[i]))) for i, j in bars)
    sw_plf = sum(
        (chord.weight if k.endswith('chord') else web.weight)
        * float(np.hypot(*(nodes[j] - nodes[i]))) / 12.0
        for (i, j), k in zip(bars, kinds)
    ) / (span_in / 12.0)

    supports = {0: (True, True), n_panels: (False, True)}

    def run(w_plf: float):
        w = w_plf / 1000.0 * span_in / 12.0 / n_panels      # kip per panel
        loads = {i: (0.0, -w * (0.5 if i in (0, n_panels) else 1.0))
                 for i in range(nt)}
        return _solve(nodes, bars, areas, supports, loads)

    mid = nt // 2 if n_panels % 2 == 0 else None
    def midspan_drop(u):
        if mid is not None:
            return -u[2 * mid + 1]
        a, b = (n_panels - 1) // 2, (n_panels + 1) // 2
        return -(u[2 * a + 1] + u[2 * b + 1]) / 2.0

    uL, _, _ = run(wL_plf)
    uT, _, _ = run(wD_plf + sw_plf + wL_plf)
    _, fU, lengths = run(1.2 * (wD_plf + sw_plf) + 1.6 * wL_plf)

    r = TrussResult(depth_in, n_panels, chord, web, span_in)
    r.defl_live_in = midspan_drop(uL)
    r.defl_total_in = midspan_drop(uT)
    r.weight_lb = sum(
        (chord.weight if k.endswith('chord') else web.weight) * Lb / 12.0
        for Lb, k in zip(lengths, kinds)
    )
    r.n_joints = 2 * len(bars) - 2 * n_panels      # fitted tube ends, chords run through

    for b, (kind, f, Lb) in enumerate(zip(kinds, fU, lengths)):
        sec = chord if kind.endswith('chord') else web
        if f >= 0:
            cap = PHI_T * FY * sec.A
        else:
            lam = K * Lb / sec.rz
            Fe = math.pi ** 2 * E / lam ** 2
            Fcr = (0.658 ** (FY / Fe)) * FY if lam <= 4.71 * math.sqrt(E / FY) else 0.877 * Fe
            cap = PHI_C * Fcr * sec.A
        dcr = abs(f) / (cap * 1000.0)
        r.forces[f'{kind} {b}'] = f * 1000.0
        if dcr > r.max_dcr:
            r.max_dcr = dcr
            r.governing = f'{kind}, {"tension" if f >= 0 else "compression"}'

    # Top chord local bending.  The joists land at 16 in. o.c., not at the panel
    # points, so the top chord also spans between them as a continuous beam.  A
    # coarse panel layout hides a real demand if this is left out.
    panel_in = span_in / n_panels
    wu_plf = 1.2 * (wD_plf + sw_plf) + 1.6 * wL_plf
    Mu_local = wu_plf / 1000.0 / 12.0 * panel_in ** 2 / 10.0        # kip-in, continuous
    Pu_chord = max(-f for f in fU[:n_panels])                       # kip, compression
    phiPn = PHI_C * FY * chord.A
    phiMn = 0.90 * FY * chord.Zz
    ratio = Pu_chord / phiPn
    h1 = (ratio + 8.0 / 9.0 * Mu_local / phiMn) if ratio >= 0.2 else \
         (ratio / 2.0 + Mu_local / phiMn)
    if h1 > r.max_dcr:
        r.max_dcr, r.governing = h1, 'top chord, axial + local bending (H1-1)'

    for limit, d, tag in ((360.0, r.defl_live_in, 'live deflection L/360'),
                          (240.0, r.defl_total_in, 'total deflection L/240')):
        dcr = d / (span_in / limit)
        if dcr > r.max_dcr:
            r.max_dcr, r.governing = dcr, tag
    return r


def size(span_in: float, depth_in: float, n_panels: int,
         wD_plf: float, wL_plf: float) -> TrussResult | None:
    """Lightest chord/web pair off the project HSS ladder that passes everything."""
    ladder = v6sections.ladder()
    for chord in ladder:
        for web in ladder:
            if web.weight > chord.weight:
                break
            r = analyse(span_in, depth_in, n_panels, wD_plf, wL_plf, chord, web)
            if r.max_dcr <= 1.0:
                return r
    return None


#: Panel counts worth trying.  Fewer panels means fewer joints but a longer
#: unbraced top-chord run between them; more panels means the opposite.
PANEL_OPTIONS = (4, 6, 8, 10, 12)


def best(span_in: float, depth_in: float, wD_plf: float, wL_plf: float,
         panels: tuple[int, ...] = PANEL_OPTIONS) -> TrussResult | None:
    """Lightest passing truss at this depth, searching over panel count too.

    Weight alone would always favour the coarsest layout; joints are what cost
    money here, so ties on weight break toward fewer joints.
    """
    found = [r for n in panels
             if (r := size(span_in, depth_in, n, wD_plf, wL_plf)) is not None]
    return min(found, key=lambda r: (round(r.weight_lb), r.n_joints)) if found else None


if __name__ == '__main__':
    import span_model
    import design

    geom, _ = span_model.read_geometry()
    for name in ('L40-interior', 'L125-interior'):
        case = [c for c in design.build_cases(geom.loft_depth_ft)
                if c.name == name][0]
        print(f'\nspan {geom.span_in:.1f} in   {case.label()}')
        print(f"{'depth':>6}{'L/d':>7}{'panels':>8}  {'chord':<22}{'web':<22}"
              f"{'lb':>7}{'joints':>8}{'DCR':>6}  governing")
        for depth in (12.0, 18.0, 24.0, 30.0, 36.0):
            r = best(geom.span_in, depth, case.wD_plf, case.wL_plf)
            if r:
                print(f'{depth:6.0f}{r.span_over_depth:7.1f}{r.n_panels:8d}  '
                      f'{r.chord.name:<22}{r.web.name:<22}{r.weight_lb:7.0f}'
                      f'{r.n_joints:8d}{r.max_dcr:6.2f}  {r.governing}')
