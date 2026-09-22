#!/usr/bin/env python
"""Which ground-floor interior columns can come out of the beam scheme?

    python column_study.py [--columns S1,SW0,W1,W2] [--full]

Runs on the STR-008 recommended frame -- the same pipeline ``make_view`` builds
(owner revisions, strengthen, the five removed braces, the role palette, the
reconciliation pass) -- and then, for every subset of the candidate columns,
deletes the **ground-floor segment** of each one: the run from the footing up
to the wall-beam level at z = 104.5.  Whatever the column does above that
level stays, standing on the beam.  The footing goes with the segment, and so
does any brace that had nothing else to land on.

Each variant is re-analysed and judged by the same rule as the removal study:
stable, nothing over capacity, no span-deflection violation, wind drift inside
H/400.  A variant that fails is then handed to ``studies.strengthen`` to find
out what it would cost to make it pass, and if a wide-flange beam is what
fails -- the HSS ladder cannot help a W12X16 -- the beam is stepped to W14X22
and the strengthening repeated.

Writes ``results/column-study.json`` and prints a summary.
"""
from __future__ import annotations

import argparse
import copy
import itertools
import json
import time
from pathlib import Path

import analysis as A
import codecheck as CC
import frame as F
import loads as L
import owner_revisions as OR
import sections as S
import studies as St
from project_paths import VIZ_DIR

HERE = Path(__file__).resolve().parent
OUT = VIZ_DIR / 'column-study.json'
LIVE = 'L100'
BEAM_LEVEL = 104.5            # axis of the wall-beam grillage
HEAVIER_W = 'W14X22'          # the only heavier wide flange transcribed
ROLE_PALETTE = ['Bracing', 'Clerestory', 'Columns', 'Truss', 'Rafters']
REMOVED_BRACES = {'E.rear.brace', 'E.square.brace', 'BR-NU-2', 'BR-W-1',
                  'W.square.brace'}


def drift_of(res) -> float | None:
    return min((v['ratio'] for v in (res.drift or {}).values() if v['ratio']),
               default=None)


# ---------------------------------------------------------------------------
# the recommended frame, exactly as make_view builds it
# ---------------------------------------------------------------------------

def recommended() -> tuple[F.Frame, dict, A.Result, dict]:
    base = F.load(lineage='beam-scheme')
    params = json.loads(base.path.read_text())['specification']['parameters']
    f, _ = OR.seat_slope_on_south_beam(base)
    f, _ = OR.add_upper_east_beam(f)
    f, _ = OR.east_lean_to_separate(f)
    f, _ = OR.move_stair_south(f)
    f, _ = OR.add_north_post(f)

    first = A.run(f, params, LIVE)
    combos = St.governing_combos(first, LIVE)
    removed = {m for m in REMOVED_BRACES if m in f.members}
    strong = St.strengthen(f, params, LIVE, combos)
    secs = {m: s for m, s in strong['sections'].items() if m not in removed}
    adequate = A.run(f, params, LIVE, omit=removed, override=secs, combos=combos)

    ladder, Fy = S.ladder(), F.MATERIALS['steel']['fy']
    roles: dict[str, list] = {}
    for m in adequate.members.values():
        if m.material == 'steel':
            roles.setdefault(m.group, []).append(m)
    palette = {}
    for role in ROLE_PALETTE:
        members = roles.get(role, [])
        for cand in ladder:
            if all(CC.check_steel(m.member, cand, Fy, m.P, m.Mz, m.My, m.V,
                                  m.Lb, m.combo).dcr <= 0.85 for m in members):
                palette[role] = cand.name
                for m in members:
                    secs[m.member] = cand
                break

    final = A.run(f, params, LIVE, omit=removed, override=secs, combos=combos)
    for _ in range(10):
        over = [m for m in final.members.values() if m.dcr > 1.0 and m.material == 'steel']
        dr = drift_of(final)
        soft = dr is not None and dr < St.DRIFT_LIMIT
        if not over and not soft:
            break
        targets = [m.member for m in over]
        if soft:
            targets += [m.member for m in final.members.values()
                        if m.group in ('Bracing', 'Columns') and m.material == 'steel']
        for member in dict.fromkeys(targets):
            cur = secs.get(member, f.section_of[member])
            heavier = [c for c in ladder if c.weight > cur.weight + 1e-6]
            if heavier:
                secs[member] = heavier[0]
        final = A.run(f, params, LIVE, omit=removed, override=secs, combos=combos)

    # bake it: the removed braces gone, the chosen sections in the frame itself,
    # so the variants below need no omit/override bookkeeping of their own
    built = copy.deepcopy(f)
    for member in removed:
        OR._drop(built, member)
    for m, s in secs.items():
        if m in built.members:
            built.section_of[m] = s
            built.members[m]['section_reference'] = s.name
    print(f'recommended frame: {len(built.members)} members, palette {palette}, '
          f'max DCR {final.max_dcr:.3f}, drift H/{drift_of(final):.0f}')
    return built, params, final, combos


# ---------------------------------------------------------------------------
# cutting a column off at the beam
# ---------------------------------------------------------------------------

def cut_ground_floor(f: F.Frame, column: str, level: float = BEAM_LEVEL) -> dict:
    """Delete the column's run below ``level`` and its footing; keep the rest.

    Returns what else had to go: braces whose only anchor was that footing.
    """
    segs = [(m, i, j) for m, i, j in f.segments if m == column]
    if not segs:
        raise KeyError(column)
    lower = [t for t in segs if max(f.xyz(t[1])[2], f.xyz(t[2])[2]) <= level + 0.01]
    if not lower:
        raise ValueError(f'{column}: no segments below cut level {level:g}; '
                         'check the current beam elevation before removing a column')
    upper = [t for t in segs if t not in lower]
    f.segments[:] = [t for t in f.segments if t not in lower]

    gone_nodes = {n for _, i, j in lower for n in (i, j) if f.xyz(n)[2] < level - 0.01}
    collateral = []
    for n in sorted(gone_nodes):
        others = [m for m in f.nodes[n].get('members', []) if m != column]
        for m in others:
            if m in f.members:
                collateral.append(m)
                OR._drop(f, m)
        del f.nodes[n]
    if not upper:
        f.members.pop(column, None)
        f.section_of.pop(column, None)
        for v in f.nodes.values():
            if column in v.get('members', []):
                v['members'] = [m for m in v['members'] if m != column]
    return dict(segments_cut=len(lower), stub_segments=len(upper),
                footing_removed=sorted(gone_nodes), collateral=collateral)


# ---------------------------------------------------------------------------
# judging a variant
# ---------------------------------------------------------------------------

def judge(g: F.Frame, r: A.Result, base: A.Result) -> dict:
    before = {m.member: m.dcr for m in base.members.values()}
    over = [dict(member=m.member, section=m.section, dcr=round(m.dcr, 3),
                 mode=m.mode, combo=m.combo) for m in r.overstressed()]
    newly = [o for o in over if before.get(o['member'], 0.0) <= 1.0]
    defl = A.deflection_violations(g, r)
    # the members that moved most, over capacity or not
    moved = sorted(((m.dcr - before.get(m.member, m.dcr), m) for m in r.members.values()),
                   key=lambda t: -t[0])[:5]
    return dict(stable=r.stable, message=r.message,
                max_dcr=round(r.max_dcr, 3),
                worst=max(r.members.values(), key=lambda m: m.dcr).member if r.members else None,
                over=over, newly_over=newly,
                drift_ratio=drift_of(r),
                deflection_violations=defl,
                passes=St._passes(g, r),
                biggest_rises=[dict(member=m.member, section=m.section,
                                    before=round(before.get(m.member, 0.0), 3),
                                    after=round(m.dcr, 3)) for d, m in moved if d > 0.02],
                gaps=r.gaps,
                reactions={n: v['max_compression'] for n, v in r.reactions.items()})


def fix(g: F.Frame, params: dict, combos: dict) -> dict:
    """What it takes to make a failing variant pass."""
    strong = St.strengthen(g, params, LIVE, combos)
    out = dict(adequate=strong['adequate'], added_lb=strong['added_lb'],
               rounds=len(strong['rounds']),
               sections={m: s.name for m, s in strong['sections'].items()},
               stuck=strong['stuck'],
               deflection_violations=strong['deflection_violations'],
               max_dcr=round(strong['result'].max_dcr, 3),
               drift_ratio=drift_of(strong['result']))
    if strong['adequate']:
        return out

    # a wide flange the ladder cannot touch: step the beam and try again
    beams = {v['member'] for v in strong['deflection_violations']}
    beams |= {m for m in strong['stuck'] if g.section_of[m].name.startswith('W')}
    beams = {m for m in beams if g.section_of[m].name.startswith('W12')}
    if not beams:
        return out
    h = copy.deepcopy(g)
    heavier = S.get(HEAVIER_W)
    for m in beams:
        h.section_of[m] = heavier
        h.members[m]['section_reference'] = HEAVIER_W
    again = St.strengthen(h, params, LIVE, combos)
    out['beam_upgrade'] = dict(
        beams={m: HEAVIER_W for m in sorted(beams)},
        adequate=again['adequate'],
        added_lb=round(again['added_lb'] + sum(
            g.member_length(m) * (heavier.weight - g.section_of[m].weight) / 12.0
            for m in beams), 1),
        sections={m: s.name for m, s in again['sections'].items()},
        stuck=again['stuck'],
        deflection_violations=again['deflection_violations'],
        max_dcr=round(again['result'].max_dcr, 3),
        drift_ratio=drift_of(again['result']))
    return out


# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--columns', default='S1,SW0,W1,W2')
    ap.add_argument('--full', action='store_true',
                    help='verify passing variants against all 27 strength combinations')
    args = ap.parse_args()
    cols = [c.strip() for c in args.columns.split(',') if c.strip()]
    t0 = time.time()

    built, params, final, combos = recommended()
    base = A.run(built, params, LIVE, combos=combos)
    print(f'baked baseline: max DCR {base.max_dcr:.3f} (make_view final '
          f'{final.max_dcr:.3f}), drift H/{drift_of(base):.0f}, '
          f'passes={St._passes(built, base)}')
    for c in cols:
        ns = list(dict.fromkeys(n for m, i, j in built.segments if m == c for n in (i, j)))
        print(f'  {c:<4} {built.section_of[c].name:<14} footing {base.reactions[c + ".base"]["max_compression"]:>7,.0f} lb   '
              + '  '.join(f'{n}@{built.xyz(n)[2]:.1f}:{[m for m in built.nodes[n]["members"] if m != c]}' for n in ns))

    variants = []
    for k in range(1, len(cols) + 1):
        for subset in itertools.combinations(cols, k):
            t = time.time()
            g = copy.deepcopy(built)
            cuts = {c: cut_ground_floor(g, c) for c in subset}
            r = A.run(g, params, LIVE, combos=combos)
            v = dict(columns=list(subset), cuts=cuts, judge=judge(g, r, base))
            tag = '+'.join(subset)
            j = v['judge']
            if j['passes'] and args.full:
                rf = A.run(g, params, LIVE)
                v['full_combos'] = judge(g, rf, base)
                j['passes_full'] = v['full_combos']['passes']
            if not j['passes']:
                v['fix'] = fix(g, params, combos)
            variants.append(v)
            _print(tag, v, time.time() - t)

    OUT.write_text(json.dumps(dict(
        generated=time.strftime('%Y-%m-%d %H:%M'), live_case=LIVE,
        frame_model=built.path.name, candidates=cols,
        baseline=dict(max_dcr=round(base.max_dcr, 3), drift_ratio=drift_of(base),
                      reactions={n: v['max_compression'] for n, v in base.reactions.items()}),
        variants=variants), indent=1, default=str))
    print(f'\nwrote {OUT}  ({time.time() - t0:.0f}s total)')


def _print(tag: str, v: dict, secs: float) -> None:
    j = v['judge']
    coll = [m for c in v['cuts'].values() for m in c['collateral']]
    line = (f'\n== {tag:<14} {"PASS" if j["passes"] else "FAIL"}  max DCR {j["max_dcr"]:.3f} '
            f'({j["worst"]})  drift H/{j["drift_ratio"] or 0:.0f}  '
            f'{len(j["over"])} over, {len(j["deflection_violations"])} deflection  '
            f'[{secs:.0f}s]')
    if coll:
        line += f'\n   also removed (lost their footing): {coll}'
    if not j['stable']:
        line += f'\n   UNSTABLE: {j["message"]}'
    for o in j['newly_over'][:6]:
        line += f'\n   over    {o["member"]:<22}{o["section"]:<16}{o["dcr"]:.2f}  {o["mode"]}  [{o["combo"]}]'
    for d in j['deflection_violations'][:6]:
        line += (f'\n   deflect {d["member"]:<22}span {d["span_in"]:.0f} in  '
                 f'L/{d["ratio"]:.0f} against L/{d["limit"]:.0f}')
    for b in j['biggest_rises'][:4]:
        line += f'\n   rise    {b["member"]:<22}{b["section"]:<16}{b["before"]:.2f} -> {b["after"]:.2f}'
    if 'passes_full' in j:
        fc = v['full_combos']
        line += (f'\n   all 27 combos: {"PASS" if fc["passes"] else "FAIL"}  max DCR '
                 f'{fc["max_dcr"]:.3f} ({fc["worst"]})  drift H/{fc["drift_ratio"] or 0:.0f}')
    if 'fix' in v:
        x = v['fix']
        line += (f'\n   fix: strengthen -> {"adequate" if x["adequate"] else "NOT adequate"}, '
                 f'{len(x["sections"])} sections up, {x["added_lb"]:+,.0f} lb, '
                 f'max DCR {x["max_dcr"]:.3f}, drift H/{x["drift_ratio"] or 0:.0f}'
                 + (f', stuck {x["stuck"]}' if x['stuck'] else ''))
        for m, s in sorted(x['sections'].items())[:8]:
            line += f'\n        {m:<22}-> {s}'
        if 'beam_upgrade' in x:
            b = x['beam_upgrade']
            line += (f'\n   fix: with {b["beams"]} -> '
                     f'{"adequate" if b["adequate"] else "NOT adequate"}, '
                     f'{len(b["sections"])} sections up, {b["added_lb"]:+,.0f} lb, '
                     f'max DCR {b["max_dcr"]:.3f}, drift H/{b["drift_ratio"] or 0:.0f}'
                     + (f', stuck {b["stuck"]}' if b['stuck'] else ''))
            for d in b['deflection_violations'][:4]:
                line += (f'\n        deflect {d["member"]:<18}L/{d["ratio"]:.0f} '
                         f'against L/{d["limit"]:.0f}')
    print(line, flush=True)


if __name__ == '__main__':
    main()
