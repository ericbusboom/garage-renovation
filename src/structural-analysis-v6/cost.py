"""What a change to the frame costs, in dollars rather than pounds.

Optimising this structure for weight optimises the cheapest line item in it.
Steel is $0.77-0.94/lb delivered, so the 1,088 lb an earlier pass saved is worth
about $900 -- while the shop fabrication minimum alone is $10,000-18,000 and
every fitted tube end costs $16-39 before anyone lifts it. The project's own
procurement note reaches the same conclusion from the other direction:

    "A truss that saves 180 lb of steel (worth about $130) while adding 46 joints
    (worth $736-1,794) is a worse buy, and no amount of steel price movement
    closes that gap."
        -- loft-span-study/cost.py, quoting EW-TRUSS-PROCUREMENT.md Sec. 3

So the quantities that matter are **pieces, joints and distinct sections**, and
this module scores a design on those. Rates are taken from the same source as
``loft-span-study/cost.py`` so the two studies cannot disagree; they are quoted
for this site and this tonnage and are not general-purpose numbers.

Every estimate is a range. Nothing here is a quotation, and the fabrication
minimum means small changes near the bottom of the range may not move a real
invoice at all.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import frame as framemod

# --- rates: EW-TRUSS-PROCUREMENT.md Sec. 3.1 and 3.2 ----------------------
W_SHAPE_PER_TON = (1100.0, 1400.0)     # delivered
HSS_PER_TON = (1400.0, 1800.0)         # delivered
SHOP_PER_HOUR = (80.0, 110.0)          # loaded, West Coast
HOURS_PER_JOINT = (0.20, 0.35)         # layout, cut, fit, tack, weld, grind
END_PLATES_PER_BEAM = (48.0, 132.0)    # two ends, shop-welded
GALV_PER_LB = (0.30, 0.50)             # hot dip, 100-500 lb pieces
DETAILING_PER_TON = (100.0, 200.0)

# --- rates: COST-ESTIMATE.md Sec. D and E ---------------------------------
FIELD_BOLTED_JOINT = (40.0, 80.0)      # per joint, erection
ERECTION_PER_PIECE = (55.0, 95.0)      # handling, hoisting, plumbing per piece
SECTION_SETUP = (150.0, 400.0)         # per distinct section: order, stock, waste

#: Lumber, for the joists.
LUMBER_PER_JOIST = (22.0, 38.0)        # 2x8 DF-L No.2, cut and installed
JOIST_HANGER = (9.0, 16.0)             # per end, hanger plus labour


def _rng(rate, qty):
    return (rate[0] * qty, rate[1] * qty)


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1])


@dataclass
class Quantities:
    """What a design is made of, from the point of view of a fabricator."""
    steel_pieces: int = 0
    timber_pieces: int = 0
    w_shape_lb: float = 0.0
    hss_lb: float = 0.0
    steel_joints: int = 0          # fitted steel member ends
    timber_ends: int = 0           # joist ends needing a hanger
    distinct_sections: int = 0
    beams: int = 0                 # pieces taking shop-welded end plates

    @property
    def steel_lb(self) -> float:
        return self.w_shape_lb + self.hss_lb


@dataclass
class Estimate:
    label: str
    quantities: Quantities
    lines: list[tuple[str, float, float]] = field(default_factory=list)

    @property
    def total(self) -> tuple[float, float]:
        lo = sum(a for _, a, _ in self.lines)
        hi = sum(b for _, _, b in self.lines)
        return (lo, hi)

    @property
    def mid(self) -> float:
        lo, hi = self.total
        return (lo + hi) / 2.0


def measure(frame: framemod.Frame, omit: set[str] = frozenset(),
            override: dict | None = None) -> Quantities:
    """Count what the shop and the erector actually see."""
    override = override or {}
    q = Quantities()
    sections_used: set[str] = set()
    ends_at: dict[str, int] = {}

    for member in frame.members:
        if member in omit:
            continue
        sec = override.get(member, frame.section_of[member])
        weight = frame.member_weight(member) * (
            sec.weight / frame.section_of[member].weight)
        if frame.material(member) == 'wood':
            q.timber_pieces += 1
            q.timber_ends += 2
            continue
        q.steel_pieces += 1
        sections_used.add(sec.name)
        if sec.family == 'W':
            q.w_shape_lb += weight
            q.beams += 1
        else:
            q.hss_lb += weight
        for node in _end_nodes(frame, member):
            ends_at[node] = ends_at.get(node, 0) + 1

    # A fitted end is one that meets something. A free end or a base plate is
    # counted separately in the erection and foundation lines, not here.
    for member in frame.members:
        if member in omit or frame.material(member) == 'wood':
            continue
        for node in _end_nodes(frame, member):
            others = [m for m in frame.nodes[node].get('members', [])
                      if m != member and m not in omit]
            if others:
                q.steel_joints += 1
    q.distinct_sections = len(sections_used)
    return q


def _end_nodes(frame: framemod.Frame, member: str) -> list[str]:
    segs = framemod._ordered(frame, [(i, j) for m, i, j in frame.segments
                                     if m == member])
    return [segs[0][0], segs[-1][1]] if segs else []


def estimate(label: str, q: Quantities) -> Estimate:
    e = Estimate(label, q)
    e.lines.append(('W-shape material, delivered',
                    *_rng(W_SHAPE_PER_TON, q.w_shape_lb / 2000.0)))
    e.lines.append(('HSS material, delivered',
                    *_rng(HSS_PER_TON, q.hss_lb / 2000.0)))
    joint_hours = _rng(HOURS_PER_JOINT, q.steel_joints)
    e.lines.append(('Shop fitting and welding at the joints',
                    joint_hours[0] * SHOP_PER_HOUR[0],
                    joint_hours[1] * SHOP_PER_HOUR[1]))
    e.lines.append(('Shop-welded end plates', *_rng(END_PLATES_PER_BEAM, q.beams)))
    e.lines.append(('Detailing', *_rng(DETAILING_PER_TON, q.steel_lb / 2000.0)))
    e.lines.append(('Hot-dip galvanising', *_rng(GALV_PER_LB, q.steel_lb)))
    e.lines.append(('Field-bolted connections', *_rng(FIELD_BOLTED_JOINT,
                                                      q.steel_joints / 2.0)))
    e.lines.append(('Erection, per piece', *_rng(ERECTION_PER_PIECE, q.steel_pieces)))
    e.lines.append(('Procurement and stocking, per distinct section',
                    *_rng(SECTION_SETUP, q.distinct_sections)))
    e.lines.append(('Joists, material and installation',
                    *_rng(LUMBER_PER_JOIST, q.timber_pieces)))
    e.lines.append(('Joist hangers', *_rng(JOIST_HANGER, q.timber_ends)))
    return e


def compare(base: Estimate, other: Estimate) -> dict:
    d_lo = other.total[0] - base.total[0]
    d_hi = other.total[1] - base.total[1]
    return dict(
        label=other.label,
        total_low=round(other.total[0]), total_high=round(other.total[1]),
        delta_low=round(d_lo), delta_high=round(d_hi),
        delta_mid=round(other.mid - base.mid),
        steel_lb=round(other.quantities.steel_lb),
        steel_lb_delta=round(other.quantities.steel_lb - base.quantities.steel_lb),
        steel_pieces=other.quantities.steel_pieces,
        pieces_delta=other.quantities.steel_pieces - base.quantities.steel_pieces,
        joints=other.quantities.steel_joints,
        joints_delta=other.quantities.steel_joints - base.quantities.steel_joints,
        timber_pieces=other.quantities.timber_pieces,
        timber_delta=other.quantities.timber_pieces - base.quantities.timber_pieces,
        sections=other.quantities.distinct_sections,
        sections_delta=(other.quantities.distinct_sections
                        - base.quantities.distinct_sections))


def report(estimates: list[Estimate]) -> str:
    rows = ['| Option | Steel | Pieces | Joints | Sections | Cost |',
            '|---|---:|---:|---:|---:|---:|']
    for e in estimates:
        q = e.quantities
        rows.append(f'| {e.label} | {q.steel_lb:,.0f} lb | {q.steel_pieces} | '
                    f'{q.steel_joints} | {q.distinct_sections} | '
                    f'${e.total[0]:,.0f}–{e.total[1]:,.0f} |')
    return '\n'.join(rows)


NOTE = (
    'Excludes the shop fabrication minimum of $10,000-18,000, which is a job '
    'charge rather than a quantity, and excludes foundations, cladding, glazing '
    'and everything that is not frame. Differences between options are '
    'meaningful; the absolute totals are not a quotation.')
