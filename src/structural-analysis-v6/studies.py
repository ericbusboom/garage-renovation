"""Where the frame can lose material.

Two questions, answered separately because they have different answers:

**Can this member be smaller?**  For every member, take the demands the baseline
analysis produced and find the lightest section in the HSS ladder that still
checks out with margin.  Proposals are then applied *all at once* and the whole
frame re-analysed, because changing sections changes stiffness and therefore
redistributes force.  Anything that fails the verification run is stepped back up
and the run repeated, so the published lighter frame is one that has actually
been solved, not one assembled from independent per-member arithmetic.

**Can this member go entirely?**  Delete it, rebuild, re-solve, and see what
happens to everything else -- including the unbraced lengths of the members it
used to restrain, which is the effect a by-hand review misses most often.  A
member is called redundant only if the frame stays stable, nothing that was
within capacity goes over it, nothing already over capacity gets worse, and wind
drift stays inside H/400.  Then the redundant set is removed cumulatively,
greedily, and re-verified, because members that are individually removable are
often not removable together.

Both studies run on the completed-framing scenario.  Recommending deletions from
a model whose roof has no load path would be meaningless.
"""
from __future__ import annotations

import copy
import math
import multiprocessing as mp
from dataclasses import dataclass, asdict

import analysis
import codecheck
import completion
import frame as framemod
import loads as L
import sections

DRIFT_LIMIT = L.DEFLECTION_LIMITS['drift_wind']

#: Maximum spacing that may be left between the survivors of a repetitive set.
#:
#: The decking is not in the model -- there are no plates anywhere in this
#: analysis -- so deleting every second joist looks free to a frame solver and is
#: not.  Something has to span between the ones that are left.  These limits are
#: what ordinary sheathing will carry, and they keep the removal study from
#: recommending a floor with nothing to walk on.
#:
#: Keyed by what the member carries, not by what its group is called: the two
#: frame lineages name these groups differently, and in one of them a single
#: group holds rafters running in two directions.  Sets are found geometrically
#: by ``_repetitive_sets`` instead.
SPACING_LIMIT = {
    'floor': (24.0, '23/32 in. OSB floor deck'),
    'roof': (32.0, 'metal roof panel over exposed rafters'),
}
FLOOR_ROLE_GROUPS = ('LoftJoists', 'Joists')
ROOF_ROLE_GROUPS = ('EastRoofRafters', 'Rafters')
DOWNSIZE_TARGET = 0.85      # leave 15 % margin when proposing a lighter section
TOLERANCE = 1.02            # a 2 % rise in an already-overstressed member is noise

_CTX: dict = {}


# ---------------------------------------------------------------------------
# combination pruning
# ---------------------------------------------------------------------------

def governing_combos(result: analysis.Result, live_case: str) -> dict:
    """The combinations that actually govern something, plus the gravity set.

    Running all 27 strength combinations for every one of 135 deletions is most
    of an hour of arithmetic to re-confirm combinations that govern nothing.  The
    combinations that govern a member in the baseline are kept, the three gravity
    combinations are always kept, and the pruning is reported so the reduction is
    visible.
    """
    full = L.strength_combos(live_case)
    keep = {c for c in full if c.startswith(('C1', 'C2', 'C3'))}
    keep |= {m.combo for m in result.members.values() if m.combo in full}
    return {c: f for c, f in full.items() if c in keep}


# ---------------------------------------------------------------------------
# parallel plumbing
# ---------------------------------------------------------------------------

def _init(frame, params, live_case, combos, override):
    _CTX.update(frame=frame, params=params, live_case=live_case, combos=combos,
                override=override or {})


def _run_omit(member: str):
    c = _CTX
    r = analysis.run(c['frame'], c['params'], c['live_case'], omit={member},
                     combos=c['combos'], override=c['override'], with_service=True)
    return member, _digest(r)


def _digest(r: analysis.Result) -> dict:
    worst = max(r.members.values(), key=lambda m: m.dcr, default=None)
    drift = min((v['ratio'] for v in r.drift.values() if v['ratio']), default=None)
    return dict(stable=r.stable, message=r.message,
                max_dcr=round(r.max_dcr, 3),
                worst_member=worst.member if worst else None,
                drift_ratio=drift,
                dcr={m.member: round(m.dcr, 3) for m in r.members.values()})


def _pool(frame, params, live_case, combos, workers=None, override=None):
    workers = workers or max(1, mp.cpu_count() - 1)
    return mp.Pool(workers, initializer=_init,
                   initargs=(frame, params, live_case, combos, override))


# ---------------------------------------------------------------------------
# removal study
# ---------------------------------------------------------------------------

@dataclass
class Removal:
    member: str
    group: str
    section: str
    weight: float
    verdict: str                 # 'unstable' | 'overloads' | 'redundant'
    max_dcr_after: float
    worst_member: str | None
    drift_ratio: float | None
    newly_over: list
    detail: str = ''


def removal_study(frame: framemod.Frame, params: dict, baseline: analysis.Result,
                  live_case: str = 'L40', combos: dict | None = None,
                  workers: int | None = None, skip: set[str] = frozenset(),
                  override: dict | None = None) -> list[Removal]:
    base = {m.member: m.dcr for m in baseline.members.values()}
    base_drift = min((v['ratio'] for v in baseline.drift.values() if v['ratio']),
                     default=None)
    targets = [m for m in frame.members if m not in skip]

    out: list[Removal] = []
    with _pool(frame, params, live_case, combos, workers, override) as pool:
        for member, d in pool.imap_unordered(_run_omit, targets, chunksize=1):
            out.append(_classify(frame, member, d, base, base_drift))
    return sorted(out, key=lambda r: (r.verdict != 'redundant', -r.weight))


def _classify(frame, member, d, base, base_drift) -> Removal:
    sec = frame.section_of[member]
    weight = frame.member_weight(member)
    common = dict(member=member, group=frame.group(member), section=sec.name,
                  weight=weight, max_dcr_after=d['max_dcr'],
                  worst_member=d['worst_member'], drift_ratio=d['drift_ratio'])
    if not d['stable']:
        return Removal(**common, verdict='unstable', newly_over=[],
                       detail='removing this member leaves a mechanism: ' + d['message'])

    newly = []
    for other, after in d['dcr'].items():
        before = base.get(other)
        if before is None:
            continue
        if before <= 1.0 < after:
            newly.append(dict(member=other, before=round(before, 3), after=round(after, 3)))
        elif before > 1.0 and after > before * TOLERANCE:
            newly.append(dict(member=other, before=round(before, 3), after=round(after, 3),
                              note='already over capacity, made worse'))
    drift_bad = (d['drift_ratio'] is not None and base_drift is not None
                 and d['drift_ratio'] < DRIFT_LIMIT <= base_drift)
    if newly or drift_bad:
        detail = ''
        if newly:
            w = max(newly, key=lambda n: n['after'])
            detail = f"{w['member']} goes {w['before']} -> {w['after']}"
        if drift_bad:
            detail += (' ; ' if detail else '') + \
                f"wind drift falls to H/{d['drift_ratio']:.0f}"
        return Removal(**common, verdict='overloads', newly_over=newly, detail=detail)
    return Removal(**common, verdict='redundant', newly_over=[],
                   detail='frame stays stable and within capacity without it')


# ---------------------------------------------------------------------------
# cumulative removal
# ---------------------------------------------------------------------------

def _repetitive_sets(frame: framemod.Frame) -> dict[str, tuple[str, list[str]]]:
    """Groups of parallel members that one sheet of decking spans between.

    A set must be **one deck**, not one group. Splitting only by run direction
    put all 54 of the beam scheme's joists into a single set measured across the
    building, and then deleting every joist in one shelf did not widen that set's
    spacing at all, because joists in the other decks stood at the same stations.
    The check passed a floor with a shelf that had no framing under it.

    So members are keyed by the deck they sit in -- the declared deck rectangle
    where the model has them, the name of their bay where it does not -- and then
    by the direction they run, which keeps the beam scheme's north-south roof
    rafters apart from its east-west canopy rafters.
    """
    out: dict[str, tuple[str, list[str]]] = {}
    for group in FLOOR_ROLE_GROUPS + ROOF_ROLE_GROUPS:
        members = frame.members_in(group)
        if len(members) < 2:
            continue
        role = 'floor' if group in FLOOR_ROLE_GROUPS else 'roof'
        for member in members:
            axis = _run_axis(frame, member)
            if axis is None:
                continue
            deck = _deck_of(frame, member, role == 'floor')
            key = f'{deck}/{"NS" if axis == 1 else "EW"}'
            out.setdefault(key, (role, []))[1].append(member)
    return out


def _deck_of(frame: framemod.Frame, member: str, floor: bool) -> str:
    """Which deck a repetitive member belongs to.

    Declared deck rectangles are matched only for floor members. They carry no
    elevation, so testing a roof rafter against them in plan put the beam
    scheme's flat rafters into a loft bay 10 ft below them.

    Everything else is keyed by the extent it spans, not by where it stands, so
    that a row of parallel rafters crossing the same opening forms one set
    instead of one set each.
    """
    pts = [frame.xyz(n) for m, i, j in frame.segments if m == member for n in (i, j)]
    if floor:
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        for deck in frame.decks:
            x0, x1 = sorted(deck['x'])
            y0, y1 = sorted(deck['y'])
            if x0 - 1.0 <= cx <= x1 + 1.0 and y0 - 1.0 <= cy <= y1 + 1.0:
                return deck['name']
        if ' joist' in member:
            return member.rsplit(' joist', 1)[0]
    axis = _run_axis(frame, member) or 0
    lo = min(p[axis] for p in pts)
    hi = max(p[axis] for p in pts)
    return f'{frame.group(member)} spanning {lo:.0f}-{hi:.0f}'


def _run_axis(frame: framemod.Frame, member: str):
    """0 if the member runs east-west, 1 if north-south, None if neither."""
    pts = [frame.xyz(n) for m, i, j in frame.segments if m == member for n in (i, j)]
    if len(pts) < 2:
        return None
    dx = max(p[0] for p in pts) - min(p[0] for p in pts)
    dy = max(p[1] for p in pts) - min(p[1] for p in pts)
    if max(dx, dy) < 1.0:
        return None
    return 0 if dx > dy else 1


def _max_gap(frame: framemod.Frame, members: list[str],
             bounds: tuple[float, float] | None = None) -> float:
    """Widest unsupported run across a deck, including out to its edges.

    Measuring only between the surviving members is not enough, and quietly
    wrong in the worst way: delete the joists at one end of a shelf and the
    remaining two are still 15 in. apart, so the gap looks fine while three feet
    of deck hangs off the end with nothing under it. The deck's own edges are
    framed -- the beam scheme's owner direction says every shelf panel has a
    member on each edge -- so they bound the span and belong in the measurement.
    """
    if not members:
        return float('inf')
    axis = 1 - (_run_axis(frame, members[0]) or 0)
    pos = sorted(_set_position(frame, m, axis) for m in members)
    if bounds:
        lo, hi = sorted(bounds)
        pos = [lo] + pos + [hi]
    if len(pos) < 2:
        return 0.0
    return max(b - a for a, b in zip(pos, pos[1:]))


def _deck_bounds(frame: framemod.Frame, key: str,
                 members: list[str]) -> tuple[float, float] | None:
    """The framed edges of the deck a set spans, along the spacing axis."""
    name = key.rsplit('/', 1)[0]
    axis = 1 - (_run_axis(frame, members[0]) or 0)
    for deck in frame.decks:
        if deck['name'] == name:
            return tuple(sorted(deck['x' if axis == 0 else 'y']))
    return None


def _spacing_ok(frame: framemod.Frame, omitted: set[str]) -> tuple[bool, str]:
    """Does deleting ``omitted`` leave any deck spanning further than it can?

    Measured deck by deck, against the sheathing limit, with no credit for what
    the design already does. An earlier version tested each set against its own
    as-drawn worst gap, which sounded reasonable and was not: the beam scheme's
    joists contain a 27 in. hole where the walkway runs between two shelves, and
    allowing that as a precedent licensed 27 in. holes in the middle of a floor.
    """
    for key, (role, members) in _repetitive_sets(frame).items():
        limit, reason = SPACING_LIMIT[role]
        left = [m for m in members if m not in omitted]
        if len(left) < len(members) and len(left) < 2:
            return False, (f'{key}: deleting these would leave '
                           f'{len(left)} member(s) carrying the deck')
        if len(left) < 2:
            continue                       # a one-member deck as drawn; not ours
        # Now that a set is one deck, allowing its own as-drawn worst gap is
        # safe and necessary. The beam scheme's four canopy rafters already
        # stand 114 in. apart, which no metal panel spans -- that is a gap in
        # the scheme (see the report), not a licence to open one in a floor.
        # A removal may leave that condition alone; it may not make it worse.
        bounds = _deck_bounds(frame, key, members)
        allowed = max(limit, _max_gap(frame, members, bounds))
        gap = _max_gap(frame, left, bounds)
        if gap > allowed + 0.5:
            return False, (f'{key}: would leave a {gap:.0f} in. gap against the '
                           f'{allowed:.0f} in. already there and the '
                           f'{limit:.0f} in. span of the {reason}')
    return True, ''


def _set_position(frame: framemod.Frame, member: str, axis: int) -> float:
    pts = [frame.xyz(n) for m, i, j in frame.segments if m == member for n in (i, j)]
    return sum(p[axis] for p in pts) / len(pts)


def cumulative_removal(frame: framemod.Frame, params: dict, candidates: list[str],
                       live_case: str = 'L40', combos: dict | None = None,
                       drift_floor: float = DRIFT_LIMIT,
                       override: dict | None = None) -> dict:
    """Greedily delete candidates together, verifying after every addition."""
    kept: list[str] = []
    rejected: list[dict] = []
    order = sorted(candidates, key=lambda m: -frame.member_weight(m))
    current = analysis.run(frame, params, live_case, combos=combos, override=override)
    for member in order:
        trial = set(kept) | {member}
        ok, why = _spacing_ok(frame, trial)
        if not ok:
            rejected.append(dict(member=member, reason=why, check='deck spacing'))
            continue
        r = analysis.run(frame, params, live_case, omit=trial, combos=combos,
                         override=override)
        drift = min((v['ratio'] for v in r.drift.values() if v['ratio']), default=None)
        if (not _passes(frame, r)
                or (drift is not None and drift < drift_floor)):
            rejected.append(dict(member=member, max_dcr=round(r.max_dcr, 3),
                                 stable=r.stable, check='strength and drift',
                                 reason=('leaves a mechanism' if not r.stable else
                                         f'pushes the frame to DCR {r.max_dcr:.2f}'
                                         if r.max_dcr > 1.0 else
                                         f'wind drift falls to H/{drift:.0f}'),
                                 drift=round(drift, 0) if drift else None))
            continue
        kept, current = sorted(trial), r
    saved = sum(frame.member_weight(m) *
                ((override or {}).get(m, frame.section_of[m]).weight
                 / frame.section_of[m].weight) for m in kept)
    return dict(removed=kept, rejected=rejected,
                spacing_rules={role: dict(limit_in=limit, governed_by=reason)
                               for role, (limit, reason) in SPACING_LIMIT.items()},
                spacing_sets={k: dict(role=role, members=len(ms),
                                      max_gap_in=round(_max_gap(
                                          frame, ms, _deck_bounds(frame, k, ms)), 1))
                              for k, (role, ms) in _repetitive_sets(frame).items()},
                weight_saved_lb=round(saved, 1),
                max_dcr_after=round(current.max_dcr, 3),
                stable=current.stable,
                drift_ratio=min((v['ratio'] for v in current.drift.values()
                                 if v['ratio']), default=None))


# ---------------------------------------------------------------------------
# downsizing study
# ---------------------------------------------------------------------------

@dataclass
class Downsize:
    member: str
    group: str
    current: str
    proposed: str
    current_weight: float
    proposed_weight: float
    dcr_before: float
    dcr_after_est: float
    reason: str


def _ladder_up(sec: sections.Section) -> sections.Section | None:
    """The next section up the ladder from ``sec``, or None at the top."""
    for cand in sections.ladder():
        if cand.weight > sec.weight + 1e-6:
            return cand
    return None


def _ladder_down(sec: sections.Section) -> sections.Section | None:
    lighter = [c for c in sections.ladder() if c.weight < sec.weight - 1e-6]
    return lighter[-1] if lighter else None


def _current(frame: framemod.Frame, override: dict) -> dict:
    return {m: override.get(m, frame.section_of[m]) for m in frame.members}


def strengthen(frame: framemod.Frame, params: dict, live_case: str = 'L40',
               combos: dict | None = None, max_rounds: int = 12) -> dict:
    """Step over-capacity members up the ladder until the frame passes.

    One rung per round, then a full re-analysis.  Sizing every member straight to
    what its own demands ask for does not work on a braced frame: stiffening a
    brace makes it attract more load, and a batch of simultaneous changes
    redistributes force so violently that the iteration diverges.  Taking one
    rung at a time keeps each redistribution small, and because sections only
    ever move up, the sequence is monotone on a finite ladder and terminates.

    Wide-flange members and anything the ladder cannot satisfy are left alone and
    reported, rather than silently substituted with a section that does not work.
    """
    override: dict[str, sections.Section] = {}
    history = []
    for rnd in range(max_rounds):
        r = analysis.run(frame, params, live_case, override=override, combos=combos)
        over = [m for m in r.overstressed() if m.material == 'steel']
        drift = min((v['ratio'] for v in (r.drift or {}).values() if v['ratio']),
                    default=None)
        # Drift is nobody's fault in particular, so it cannot be fixed by
        # stepping up whichever member is worst -- there may be no member over
        # capacity at all. Removing the outer east posts left the beam-scheme
        # variant at 0.82 of capacity everywhere and H/382 on drift, and an
        # earlier version of this loop called that adequate and stopped.
        soft = drift is not None and drift < DRIFT_LIMIT
        targets = list(over)
        if soft:
            targets += [m for m in r.members.values()
                        if m.material == 'steel'
                        and m.group in ('Bracing', 'Columns', 'Truss')]
        stuck = []
        changed = 0
        over_names = {m.member for m in over}
        for name in dict.fromkeys(m.member for m in targets):
            cur = override.get(name, frame.section_of[name])
            nxt = _ladder_up(cur)
            if nxt is None:
                if name in over_names:
                    stuck.append(name)
                continue
            override[name] = nxt
            changed += 1
        history.append(dict(round=rnd + 1, over_capacity=len(over),
                            max_dcr=round(r.max_dcr, 3), upsized=changed,
                            drift=round(drift) if drift else None,
                            stiffened_for_drift=soft,
                            at_ladder_top=len(stuck)))
        if (not over and not soft) or changed == 0:
            return dict(sections=override, result=r, rounds=history,
                        adequate=_passes(frame, r),
                        deflection_violations=analysis.deflection_violations(frame, r),
                        stuck=stuck + [m.member for m in r.overstressed()
                                       if m.material != 'steel'],
                        added_lb=_delta(frame, override))
    r = analysis.run(frame, params, live_case, override=override, combos=combos)
    return dict(sections=override, result=r, rounds=history,
                adequate=_passes(frame, r),
                deflection_violations=analysis.deflection_violations(frame, r),
                stuck=[m.member for m in r.overstressed()],
                added_lb=_delta(frame, override))


def lighten(frame: framemod.Frame, params: dict, base: dict[str, sections.Section],
            live_case: str = 'L40', combos: dict | None = None,
            max_rounds: int = 25, limit: float = 0.90, batch: int = 12) -> dict:
    """Step lightly-stressed members down the ladder, verifying every round.

    Members are taken least-stressed first, a dozen at a time.  Small batches
    matter: dropping fifty sections at once redistributes force so far that the
    result says nothing about any individual change, while a dozen moves the
    frame a little and the re-analysis can be believed.

    If a batch fails, the members implicated in the failure are reverted and the
    batch re-solved -- repeatedly, because reverting one set can expose another.
    A batch that still fails after that is abandoned whole and its members are
    frozen, so the search always makes progress and never loops.  Only changes
    that survived a full re-analysis at or under capacity are reported.
    """
    override = dict(base)
    frozen: set[str] = set()
    history = []
    accepted = analysis.run(frame, params, live_case, override=override, combos=combos)
    for rnd in range(max_rounds):
        pool = []
        for m in sorted(accepted.members.values(), key=lambda x: x.dcr):
            if m.material != 'steel' or m.member in frozen or m.dcr > limit:
                continue
            cur = override.get(m.member, frame.section_of[m.member])
            nxt = _ladder_down(cur)
            if nxt is None:
                frozen.add(m.member)
                continue
            slr_limit = (codecheck.SLENDER_LIMIT_C if m.P > 0
                         else codecheck.SLENDER_LIMIT_T)   # PyNite: +P is compression
            c = codecheck.check_steel(m.member, nxt,
                                      framemod.MATERIALS['steel']['fy'],
                                      m.P, m.Mz, m.My, m.V, m.Lb, m.combo)
            if c.dcr > limit or c.slenderness > slr_limit:
                frozen.add(m.member)
                continue
            pool.append((m.member, nxt))
            if len(pool) >= batch:
                break
        if not pool:
            break

        trial = dict(override)
        for member, sec in pool:
            trial[member] = sec
        moved = {m for m, _ in pool}
        r = analysis.run(frame, params, live_case, override=trial, combos=combos)
        reverted: set[str] = set()
        for _ in range(4):
            if _passes(frame, r):
                break
            blame = _blame(frame, r, sorted(moved - reverted))
            if not blame:
                break
            reverted |= blame
            for member in blame:
                trial[member] = override.get(member, frame.section_of[member])
            if reverted >= moved:
                break
            r = analysis.run(frame, params, live_case, override=trial, combos=combos)

        if _passes(frame, r) and reverted < moved:
            override, accepted = trial, r
            frozen |= reverted
            history.append(dict(round=rnd + 1, proposed=len(pool),
                                accepted=len(moved - reverted),
                                reverted=sorted(reverted),
                                max_dcr=round(r.max_dcr, 3)))
        else:
            frozen |= moved
            history.append(dict(round=rnd + 1, proposed=len(pool), accepted=0,
                                reverted=sorted(moved),
                                max_dcr=round(r.max_dcr, 3)))
    return dict(sections=override, result=accepted, rounds=history,
                frozen=sorted(frozen), saved_lb=-_delta(frame, override),
                lighter=sorted(m for m, sec in override.items()
                               if sec.weight < frame.section_of[m].weight - 1e-6),
                heavier=sorted(m for m, sec in override.items()
                               if sec.weight > frame.section_of[m].weight + 1e-6),
                max_dcr_after=round(accepted.max_dcr, 3))


def _passes(frame, result) -> bool:
    """A frame passes only if it is strong enough and stiff enough, both ways.

    Strength alone is not sufficient for this study: the ladder will happily
    trade a W8X24 floor beam for a tube that carries the moment and then sags
    four times as far.  Span deflection is checked on every member that spans.

    Lateral stiffness has to be checked here too, and separately, because it is
    a property of the whole frame rather than of any member in it.  Shaving
    sections one at a time -- each one passing its own check -- softened the beam
    scheme from H/464 to H/307 in an earlier pass without a single member going
    over capacity, and the removal study downstream then had nothing to work
    with because its starting point already failed drift.
    """
    if not (result.stable and result.max_dcr <= 1.0):
        return False
    if analysis.deflection_violations(frame, result):
        return False
    drift = min((v['ratio'] for v in (result.drift or {}).values() if v['ratio']),
                default=None)
    return drift is None or drift >= DRIFT_LIMIT


def _blame(frame, result, moved: list[str]) -> set[str]:
    """Which of this round's changes to revert: the failures, and their neighbours."""
    failing = {m.member for m in result.overstressed()}
    failing |= {v['member'] for v in analysis.deflection_violations(frame, result)}
    if not result.stable:
        return set(moved)
    nodes = {n for m, i, j in frame.segments if m in failing for n in (i, j)}
    touching = {m for m, i, j in frame.segments if i in nodes or j in nodes}
    blame = (failing | touching) & set(moved)
    return blame or set(moved)


def _delta(frame: framemod.Frame, override: dict) -> float:
    return round(sum(frame.member_weight(m) *
                     (override[m].weight / frame.section_of[m].weight - 1.0)
                     for m in override), 1)


def beyond_ladder(frame: framemod.Frame, result: analysis.Result,
                  target: float = DOWNSIZE_TARGET) -> list[dict]:
    """Members no section in the ladder can carry -- they need a real design."""
    ladder = sections.ladder()
    Fy = framemod.MATERIALS['steel']['fy']
    out = []
    for m in result.members.values():
        if m.dcr <= 1.0:
            continue
        if m.material != 'steel':
            out.append(dict(member=m.member, section=m.section, dcr=round(m.dcr, 3),
                            mode=m.mode, combo=m.combo, length_in=round(m.Lb, 1),
                            note='timber member; sizing is outside the steel ladder'))
            continue
        limit = codecheck.SLENDER_LIMIT_C if m.P > 0 else codecheck.SLENDER_LIMIT_T   # +P is compression
        ok = False
        for c in ladder:
            chk = codecheck.check_steel(m.member, c, Fy, m.P, m.Mz, m.My, m.V,
                                        m.Lb, m.combo)
            if chk.dcr <= target and chk.slenderness <= limit:
                ok = True
                break
        if not ok:
            out.append(dict(member=m.member, section=m.section, dcr=round(m.dcr, 3),
                            mode=m.mode, combo=m.combo, length_in=round(m.Lb, 1),
                            note='no square HSS up to HSS6X6X3/8 satisfies this '
                                 'demand; a deeper or built-up section is required'))
    return out


def _base_dcr(baseline: analysis.Result, member: str) -> float:
    m = baseline.members.get(member)
    return m.dcr if m else 0.0


def to_rows(items) -> list[dict]:
    return [asdict(i) for i in items]
