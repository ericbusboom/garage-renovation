"""How far apart the joists can go, and what that is worth.

At the owner's 100 psf the beam scheme's joists run at a demand-capacity ratio of
0.19 to 0.58 and deflect L/960 against an L/360 limit. They are not working, and
the reason is that their spacing was never a structural decision -- it is 16 in.
because that is what joists are.

Widening them is the clearest cost reduction available in this frame, because a
joist is not really a piece of lumber: it is two hangers, two fixings and a
handling operation. What stops it is the deck, not the joist. The deck is not in
the structural model, so this module carries its span limits explicitly rather
than letting the frame solver conclude that joists are free to delete.
"""
from __future__ import annotations

from dataclasses import dataclass

import analysis
import cost
import frame as framemod

#: What each deck product will span, at 100 psf, with the panel continuous over
#: two or more spans.  These are ordinary sheathing span ratings, not a design.
DECK_OPTIONS = [
    (16.0, '19/32 in. OSB or plywood', 2.0),
    (19.2, '23/32 in. OSB', 2.4),
    (24.0, '23/32 in. OSB -- the current specification', 2.4),
    (32.0, '1-1/8 in. OSB single-layer, or two layers of 23/32 in.', 3.6),
    (48.0, 'structural panel over sleepers, or steel deck with topping', 5.0),
]


def deck_for(spacing: float) -> tuple[str, float]:
    for limit, product, psf in DECK_OPTIONS:
        if spacing <= limit + 0.01:
            return product, psf
    return 'not achievable with sheathing; needs a framed or composite deck', 8.0


@dataclass
class SpacingCase:
    spacing: float
    kept: int
    dropped: int
    deck: str
    deck_psf: float
    max_joist_dcr: float
    worst_joist: str
    min_joist_ratio: float
    max_frame_dcr: float
    stable: bool
    adequate: bool
    cost_low: float
    cost_high: float


def joist_sets(frame: framemod.Frame) -> dict[str, list[str]]:
    """Joists grouped by the deck they sit in, ordered across the span."""
    out: dict[str, list[str]] = {}
    for member in frame.members:
        if frame.material(member) != 'wood':
            continue
        deck = member.rsplit(' joist', 1)[0]
        out.setdefault(deck, []).append(member)
    for deck, members in out.items():
        out[deck] = sorted(members, key=lambda m: _across(frame, m))
    return out


def _across(frame: framemod.Frame, member: str) -> float:
    pts = [frame.xyz(n) for m, i, j in frame.segments if m == member for n in (i, j)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    # joists run along whichever axis varies; they are spaced along the other
    return sum(ys) / len(ys) if max(xs) - min(xs) > max(ys) - min(ys) else sum(xs) / len(xs)


def current_spacing(frame: framemod.Frame) -> float:
    sets = joist_sets(frame)
    gaps = []
    for members in sets.values():
        pos = [_across(frame, m) for m in members]
        gaps += [b - a for a, b in zip(pos, pos[1:])]
    return sum(gaps) / len(gaps) if gaps else 0.0


def thin_by(frame: framemod.Frame, every: int) -> set[str]:
    """Drop joists so only every ``every``-th one is kept, edges retained.

    Deletion can only reach integer multiples of the spacing already drawn. From
    15.4 in. that is 30.8 or 46.2 -- there is no way to delete your way to 24.
    Reaching an arbitrary spacing means re-spacing, which is ``respace`` below
    and is a design change rather than a deletion.
    """
    if every <= 1:
        return set()
    drop: set[str] = set()
    for members in joist_sets(frame).values():
        for k, member in enumerate(members):
            if k in (0, len(members) - 1):
                continue                       # keep the edge joists
            if k % every:
                drop.add(member)
    return drop


def respace(base: framemod.Frame, spacing: float, section_name: str,
            depth: float) -> framemod.Frame:
    """Rebuild every deck's joists at ``spacing``, in a new section.

    The old joists are removed and new ones are laid out across each deck at the
    target spacing, landing on new nodes cut into the same supporting members
    the originals used. Widening the spacing without deepening the joist does
    not work at this load, so the section comes with it.
    """
    import completion
    f = _copy(base)
    for deck, members in joist_sets(base).items():
        pos = [_across(base, m) for m in members]
        lo, hi = min(pos), max(pos)
        ends = {m: _ends(base, m) for m in members}
        run_axis = _run_axis(base, members[0])
        supports = _supports(base, members)
        if len(supports) != 2:
            continue                           # leave anything unusual alone
        n = max(2, int(round((hi - lo) / spacing)) + 1)
        stations = [lo + (hi - lo) * k / (n - 1) for k in range(n)]
        for m in members:
            _remove(f, m)
        for k, at in enumerate(stations):
            nodes = []
            for support, coord in supports:
                xyz = list(coord)
                xyz[1 - run_axis] = at
                nodes.append(completion._split(
                    f, support, tuple(xyz), f'{deck}.R{k}.{support}'))
            completion._add_member(
                f, f'{deck} joist R{k + 1}', nodes[0], nodes[1], section_name,
                1.5, depth, 'Joists', 'wood',
                note=f'respaced to {spacing:.0f} in. centres by the spacing study')
    return f


def _copy(frame: framemod.Frame) -> framemod.Frame:
    import copy
    return copy.deepcopy(frame)


def _ends(frame: framemod.Frame, member: str):
    segs = framemod._ordered(frame, [(i, j) for m, i, j in frame.segments
                                     if m == member])
    return (segs[0][0], segs[-1][1]) if segs else (None, None)


def _run_axis(frame: framemod.Frame, member: str) -> int:
    a, b = (frame.xyz(n) for n in _ends(frame, member))
    return 0 if abs(b[0] - a[0]) > abs(b[1] - a[1]) else 1


def _supports(frame: framemod.Frame, members: list[str]):
    """The two members every joist in this deck lands on, with a point on each."""
    tally: dict[str, tuple] = {}
    counts: dict[str, int] = {}
    for m in members:
        for node in _ends(frame, m):
            for other in frame.nodes[node].get('members', []):
                if other == m or frame.material(other) == 'wood':
                    continue
                counts[other] = counts.get(other, 0) + 1
                tally.setdefault(other, frame.xyz(node))
    best = sorted(counts, key=lambda k: -counts[k])[:2]
    return [(k, tally[k]) for k in best]


def _remove(frame: framemod.Frame, member: str) -> None:
    frame.members.pop(member, None)
    frame.section_of.pop(member, None)
    frame.segments[:] = [t for t in frame.segments if t[0] != member]
    for v in frame.nodes.values():
        if member in v.get('members', []):
            v['members'] = [m for m in v['members'] if m != member]


def study(frame: framemod.Frame, params: dict, live_case: str,
          spacings: list[float], combos: dict | None = None) -> list[SpacingCase]:
    out = []
    for spacing in spacings:
        drop = thin_to(frame, spacing)
        r = analysis.run(frame, params, live_case, omit=drop, combos=combos)
        joists = [m for m in r.members.values() if m.material == 'wood']
        worst = max(joists, key=lambda m: m.dcr, default=None)
        ratios = [v['S2 D+L']['ratio'] for k, v in (r.deflection or {}).items()
                  if 'joist' in k and v.get('S2 D+L', {}).get('ratio')]
        deck, deck_psf = deck_for(spacing)
        q = cost.measure(frame, omit=drop)
        e = cost.estimate(f'{spacing:.0f} in. centres', q)
        out.append(SpacingCase(
            spacing=spacing, kept=len(joists), dropped=len(drop),
            deck=deck, deck_psf=deck_psf,
            max_joist_dcr=round(worst.dcr, 3) if worst else 0.0,
            worst_joist=worst.member if worst else '',
            min_joist_ratio=round(min(ratios), 0) if ratios else 0.0,
            max_frame_dcr=round(r.max_dcr, 3), stable=r.stable,
            adequate=bool(r.stable and r.max_dcr <= 1.0
                          and not analysis.deflection_violations(frame, r)),
            cost_low=e.total[0], cost_high=e.total[1]))
    return out


def report(cases: list[SpacingCase], base_psf: float) -> str:
    rows = ['| Spacing | Joists | Worst joist | Deflection | Frame | Deck required | Frame cost |',
            '|---:|---:|---:|---:|---:|---|---:|']
    for c in cases:
        ok = '' if c.adequate else ' ⚠'
        rows.append(
            f'| {c.spacing:.0f} in. | {c.kept} | {c.max_joist_dcr:.2f} | '
            f'L/{c.min_joist_ratio:.0f} | {c.max_frame_dcr:.2f}{ok} | {c.deck} | '
            f'${c.cost_low:,.0f}–{c.cost_high:,.0f} |')
    return '\n'.join(rows)
