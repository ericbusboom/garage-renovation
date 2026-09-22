"""Sizing the three east-west loft beams over the W1 -> E-S span.

The question this answers is narrow: *how deep does a W shape have to be to carry
the loft across the full 23 ft 5 1/2 in between the W1 column and the E-S column
on the existing east wall?*

Load basis is not invented here.  It is imported from
``structural-analysis-v6/loads.py``, which is the project's design load register
and carries its own sources.  The only thing this module adds is the takedown ---
turning psf on a floor into pounds per foot on one beam --- and the AISC checks.

Three things about the takedown are worth stating plainly, because they are
where the answer actually comes from:

1. **The loft live load is unsettled.**  ASM-006 assumes 40 psf; ASCE 7-16
   Table 4.3-1 puts light storage at 125 psf.  Both are carried the whole way
   through, because the difference is six inches of beam depth.

2. **"Three beams sharing the floor" is not one load case.**  If the three beams
   are equally spaced, the middle one takes half again as much as the average.
   The even-share reading is reported because it is what was asked for; the
   interior-beam reading is reported because it is what has to be built.

3. **Deflection governs, not strength.**  At this span every candidate that
   satisfies IBC Table 1604.3 has a large reserve in bending.  Choosing on
   strength alone would put a beam in that is two sizes too shallow.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'structural-analysis-v6'))

import loads as L          # noqa: E402  the project's design load register
import wshapes             # noqa: E402
from wshapes import E, WShape   # noqa: E402

G = 386.4                  # in/s^2

# ---------------------------------------------------------------------------
# what sits on the floor besides the people and the boxes
# ---------------------------------------------------------------------------

JOIST = dict(b=1.5, d=7.25, spacing=16.0, grade='DF-L No.2')
#: Joist self weight smeared over the floor, psf.  Matches the 2x8 at 16 in. o.c.
#: that ``structural-analysis-v6`` models explicitly.
JOIST_PSF = (JOIST['b'] * JOIST['d'] * 0.0185 * 12.0) / (JOIST['spacing'] / 12.0)

#: Deflection limits, IBC Table 1604.3, floor members supporting non-plaster
#: ceilings.  L/360 on live load, L/240 on dead plus live.
DEFL_LIVE = 360.0
DEFL_TOTAL = 240.0


@dataclass(frozen=True)
class LoadCase:
    """One reading of the floor load, expressed on one beam."""
    name: str
    live_psf: float
    live_basis: str
    trib_ft: float
    trib_basis: str

    @property
    def dead_psf(self) -> float:
        """Superimposed dead plus joists.  Beam self weight is added separately."""
        return L.DEAD['loft_floor'] + JOIST_PSF

    @property
    def wD_plf(self) -> float:
        return self.dead_psf * self.trib_ft

    @property
    def wL_plf(self) -> float:
        return self.live_psf * self.trib_ft

    def label(self) -> str:
        return f'{self.name} · {self.live_psf:.0f} psf live · {self.trib_ft:.2f} ft trib'


@dataclass
class BeamCheck:
    """Result of checking one section against one load case over one span."""
    section: WShape
    case: LoadCase
    span_in: float
    Mu_kipft: float = 0.0
    Vu_kip: float = 0.0
    dcr_flexure: float = 0.0
    dcr_shear: float = 0.0
    defl_live_in: float = 0.0
    defl_total_in: float = 0.0
    dcr_defl_live: float = 0.0
    dcr_defl_total: float = 0.0
    fn_hz: float = 0.0
    notes: list[str] = field(default_factory=list)

    @property
    def span_ft(self) -> float:
        return self.span_in / 12.0

    @property
    def governing(self) -> tuple[str, float]:
        items = [('flexure', self.dcr_flexure), ('shear', self.dcr_shear),
                 ('live deflection L/360', self.dcr_defl_live),
                 ('total deflection L/240', self.dcr_defl_total)]
        return max(items, key=lambda kv: kv[1])

    @property
    def dcr(self) -> float:
        return self.governing[1]

    @property
    def ok(self) -> bool:
        return self.dcr <= 1.0


def check(section: WShape, case: LoadCase, span_in: float) -> BeamCheck:
    """AISC 360-16 LRFD strength plus IBC serviceability, simple span, UDL.

    The compression flange is taken as continuously braced by the plywood deck
    and the joists framing into the beam, so ``Mn = Mp`` and no lateral-torsional
    buckling reduction applies.  That assumption is recorded in the result.
    """
    span_ft = span_in / 12.0
    wD = (case.wD_plf + section.wt) / 1000.0     # klf, beam self weight included
    wL = case.wL_plf / 1000.0

    r = BeamCheck(section, case, span_in)
    wu = 1.2 * wD + 1.6 * wL                     # ASCE 7-16 combination 2
    r.Mu_kipft = wu * span_ft ** 2 / 8.0
    r.Vu_kip = wu * span_ft / 2.0
    r.dcr_flexure = r.Mu_kipft / section.phiMn_kipft
    r.dcr_shear = r.Vu_kip / section.phiVn_kip

    # service deflections, w in kip/in
    k = 5.0 * span_in ** 4 / (384.0 * E * section.Ix)
    r.defl_live_in = k * wL / 12.0
    r.defl_total_in = k * (wD + wL) / 12.0
    r.dcr_defl_live = r.defl_live_in / (span_in / DEFL_LIVE)
    r.dcr_defl_total = r.defl_total_in / (span_in / DEFL_TOTAL)

    # first mode of the bare beam under sustained load, AISC Design Guide 11
    # Eq. 3.3.  Indicative only: a full walking-vibration check needs the deck
    # and joist modes combined with this one.
    d_sustained = k * (wD + 0.25 * wL) / 12.0
    r.fn_hz = 0.18 * math.sqrt(G / d_sustained) if d_sustained > 0 else 0.0

    r.notes.append('compression flange continuously braced by deck and joists')
    if not section.name.startswith(('W6', 'W8')) and section.Iy / section.Ix < 0.02:
        r.notes.append('narrow-flange shape: needs the deck in place before loading')
    return r


def lightest(case: LoadCase, span_in: float,
             ladder: list[WShape] | None = None) -> BeamCheck | None:
    """Lightest catalogue shape that passes every check for this case."""
    for s in (ladder or wshapes.LADDER):
        r = check(s, case, span_in)
        if r.ok:
            return r
    return None


def shallowest_by_depth(case: LoadCase, span_in: float) -> dict[int, BeamCheck]:
    """For each nominal depth, the lightest shape at that depth that passes.

    This is the table the headroom question actually needs: not 'what is the
    lightest beam' but 'what does it cost me to keep the beam shallow'.
    """
    out: dict[int, BeamCheck] = {}
    for depth, group in wshapes.by_nominal_depth().items():
        for s in group:
            r = check(s, case, span_in)
            if r.ok:
                out[depth] = r
                break
    return out


# ---------------------------------------------------------------------------
# the load cases this study carries
# ---------------------------------------------------------------------------

def joist_check(bay_ft: float, live_psf: float) -> dict:
    """Can the 2x8 deck actually reach between the beams that three beams imply?

    Three beams across a 15.24 ft loft means a 7.6 ft joist bay, which is nearly
    double the 4.1 ft bay the two current loft beams leave.  If the joists cannot
    make it, the answer to the beam question changes --- you would be adding a
    fourth beam rather than deepening three.

    NDS ASD on service loads, reference values and adjustment factors taken from
    ``structural-analysis-v6/codecheck.py`` so this matches the project's check.
    """
    import codecheck as cc
    import sections as v6sections

    sec = v6sections.get('2x8 DF')
    w = cc.WOOD
    Fb = w['Fb'] * w['CD'] * w['CF'] * w['Cr']
    Fv = w['Fv'] * w['CD']

    trib_ft = JOIST['spacing'] / 12.0
    span_in = bay_ft * 12.0
    wD = (L.DEAD['loft_floor'] + JOIST_PSF) * trib_ft / 12.0      # lb/in
    wL = live_psf * trib_ft / 12.0

    M = (wD + wL) * span_in ** 2 / 8.0
    V = (wD + wL) * span_in / 2.0
    defl_live = 5.0 * wL * span_in ** 4 / (384.0 * w['E'] * sec.Iz)
    defl_total = 5.0 * (wD + wL) * span_in ** 4 / (384.0 * w['E'] * sec.Iz)

    checks = {
        'bending': (M / sec.Sz) / Fb,
        'horizontal shear': (1.5 * V / sec.A) / Fv,
        'live deflection L/360': defl_live / (span_in / DEFL_LIVE),
        'total deflection L/240': defl_total / (span_in / DEFL_TOTAL),
    }
    mode = max(checks, key=checks.get)
    return dict(section='2x8 DF-L No.2 at 16 in. o.c.', bay_ft=bay_ft,
                live_psf=live_psf, dcr=checks[mode], governing=mode,
                defl_live_in=defl_live, checks=checks, basis='NDS ASD',
                ok=checks[mode] <= 1.0)


def build_cases(loft_depth_ft: float, n_beams: int = 3) -> list[LoadCase]:
    """The four corners of the question: two live loads x two tributary readings.

    ``even`` is the brief as asked --- three beams, each taking a third of the
    floor.  ``interior`` is the same three beams actually placed at equal
    spacing across the loft, where the middle beam's tributary width is the full
    bay rather than the average.
    """
    even_trib = loft_depth_ft / n_beams
    interior_trib = loft_depth_ft / (n_beams - 1)
    cases = []
    for tag, psf in ((k, v['psf']) for k, v in L.LOFT_LIVE_CASES.items()):
        basis = L.LOFT_LIVE_CASES[tag]['basis']
        cases.append(LoadCase(f'{tag}-even', psf, basis, even_trib,
                              f'floor shared equally by {n_beams} beams'))
        cases.append(LoadCase(f'{tag}-interior', psf, basis, interior_trib,
                              f'centre beam of {n_beams} at equal spacing'))
    return cases


if __name__ == '__main__':
    import span_model
    geom, _ = span_model.read_geometry()
    print(f'span {geom.span_in:.1f} in   loft depth {geom.loft_depth_ft:.2f} ft   '
          f'joists {JOIST_PSF:.2f} psf')
    for case in build_cases(geom.loft_depth_ft):
        r = lightest(case, geom.span_in)
        if r is None:
            print(f'{case.label():<46} nothing in the ladder passes')
            continue
        who, dcr = r.governing
        print(f'{case.label():<46} {r.section.name:<8} d={r.section.d:5.2f} '
              f'DCR {dcr:.2f} on {who}')
