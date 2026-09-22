"""What the three beams cost, on the rates this project already established.

Rates are taken verbatim from ``EW-TRUSS-PROCUREMENT.md`` §3, which sourced them
from SteelFlo's 2026 fabrication guides and quoted them for this site and this
tonnage.  Nothing new is assumed here; the point is only to put the rolled-beam
answer and the truss alternative on the same basis, because the choice between
them is not a structural question --- both work --- but a shop-hours question.

The finding that makes this short: a fitted tube end costs 0.20-0.35 shop hours
at $80-110/hr, so each joint is worth $16-39.  A truss that saves 180 lb of steel
(worth about $130) while adding 46 joints (worth $736-1,794) is a worse buy, and
no amount of steel price movement closes that gap.
"""
from __future__ import annotations

from dataclasses import dataclass

# --- rates, EW-TRUSS-PROCUREMENT.md §3.1 and §3.2 -------------------------
W_SHAPE_PER_TON = (1100.0, 1400.0)     # delivered
HSS_PER_TON = (1400.0, 1800.0)         # delivered
SHOP_PER_HOUR = (80.0, 110.0)          # loaded, West Coast
HOURS_PER_JOINT = (0.20, 0.35)         # layout, cut, fit, tack, weld, grind
HOURS_PER_ASSEMBLY = (3.0, 6.0)        # jig, squaring, camber, QC, handling
END_PLATES_PER_BEAM = (48.0, 132.0)    # two ends, shop-welded
GALV_PER_LB = (0.30, 0.50)             # hot dip, 100-500 lb pieces
DETAILING_PER_TON = (100.0, 200.0)


@dataclass
class Estimate:
    what: str
    n: int
    weight_lb: float
    joints: int
    lines: list[tuple[str, float, float]]

    @property
    def total(self) -> tuple[float, float]:
        return (sum(a for _, a, _ in self.lines), sum(b for _, _, b in self.lines))


def _rng(qty: float, rate: tuple[float, float]) -> tuple[float, float]:
    return qty * rate[0], qty * rate[1]


def rolled_beams(n: int, weight_each_lb: float) -> Estimate:
    """Three plain W shapes: material, two end plates apiece, galvanizing."""
    total_lb = n * weight_each_lb
    lines = [
        ('material, W shape delivered', *_rng(total_lb / 2000.0, W_SHAPE_PER_TON)),
        ('end plates, shop welded', *_rng(float(n), END_PLATES_PER_BEAM)),
        ('hot-dip galvanizing', *_rng(total_lb, GALV_PER_LB)),
    ]
    return Estimate('rolled beams', n, total_lb, 0, lines)


def trusses(n: int, weight_each_lb: float, joints_each: int) -> Estimate:
    """Three fabricated Warren trusses: material, fit-up, jig time, detailing, galv."""
    total_lb = n * weight_each_lb
    total_joints = n * joints_each
    fit_lo = total_joints * HOURS_PER_JOINT[0] * SHOP_PER_HOUR[0]
    fit_hi = total_joints * HOURS_PER_JOINT[1] * SHOP_PER_HOUR[1]
    jig_lo = n * HOURS_PER_ASSEMBLY[0] * SHOP_PER_HOUR[0]
    jig_hi = n * HOURS_PER_ASSEMBLY[1] * SHOP_PER_HOUR[1]
    lines = [
        ('material, HSS delivered', *_rng(total_lb / 2000.0, HSS_PER_TON)),
        (f'shop fit-up, {total_joints} fitted tube ends', fit_lo, fit_hi),
        (f'jig layout and QC, {n} assemblies', jig_lo, jig_hi),
        ('detailing', *_rng(total_lb / 2000.0, DETAILING_PER_TON)),
        ('hot-dip galvanizing', *_rng(total_lb, GALV_PER_LB)),
    ]
    return Estimate('fabricated trusses', n, total_lb, total_joints, lines)


def compare(n: int, beam_lb: float, truss_lb: float, truss_joints: int) -> dict:
    b, t = rolled_beams(n, beam_lb), trusses(n, truss_lb, truss_joints)
    return dict(
        beams=dict(weight_lb=b.weight_lb, joints=b.joints,
                   low=b.total[0], high=b.total[1],
                   lines=[dict(item=i, low=lo, high=hi) for i, lo, hi in b.lines]),
        trusses=dict(weight_lb=t.weight_lb, joints=t.joints,
                     low=t.total[0], high=t.total[1],
                     lines=[dict(item=i, low=lo, high=hi) for i, lo, hi in t.lines]),
        steel_saved_lb=b.weight_lb - t.weight_lb,
        premium_low=t.total[0] - b.total[0],
        premium_high=t.total[1] - b.total[1],
    )


if __name__ == '__main__':
    import span_model
    import design
    import truss as trussmod

    geom, _ = span_model.read_geometry()
    for name, depth in (('L40-interior', 18.0), ('L125-interior', 24.0)):
        case = next(c for c in design.build_cases(geom.loft_depth_ft)
                    if c.name == name)
        beam = design.lightest(case, geom.span_in)
        t = trussmod.best(geom.span_in, depth, case.wD_plf, case.wL_plf)
        c = compare(3, beam.section.wt * geom.span_ft, t.weight_lb, t.n_joints)
        print(f'\n{name}: {beam.section.name} vs {depth:.0f} in truss '
              f'({t.chord.name} chords)')
        for side in ('beams', 'trusses'):
            d = c[side]
            print(f"  {side:<10} {d['weight_lb']:6.0f} lb  {d['joints']:3d} joints  "
                  f"${d['low']:,.0f} - ${d['high']:,.0f}")
            for ln in d['lines']:
                print(f"      {ln['item']:<40} ${ln['low']:>7,.0f} - ${ln['high']:>7,.0f}")
        print(f"  truss saves {c['steel_saved_lb']:.0f} lb of steel and costs "
              f"${c['premium_low']:,.0f} - ${c['premium_high']:,.0f} more")
