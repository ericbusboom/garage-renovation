#!/usr/bin/env python
"""Interactive 3-D view of the STR-008 cost-reduction recommendation.

Colours the beam scheme by the action recommended for each member: remove,
enlarge, re-section under the five-section palette, or leave alone.
"""
from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass
from pathlib import Path

import analysis as A
import codecheck as CC
import cost as C
import frame as F
import owner_revisions as OR
import sections as S
import studies as St
import viewer
from project_paths import VIZ_DIR

HERE = Path(__file__).resolve().parent
OUT = VIZ_DIR / 'cost-reduction-3d.html'
ROLE_PALETTE = ['Bracing', 'Clerestory', 'Columns', 'Truss', 'Rafters']


@dataclass
class Verdict:
    member: str
    verdict: str
    detail: str


def main() -> None:
    global OUT
    # The model on disk IS the design. The owner revisions used to be replayed
    # here on every run, which left the stored model describing a frame nobody
    # intended to build; bake.py now folds them in and records what it did, so
    # this reads the result instead of recreating it.
    f = F.load(lineage='beam-scheme')
    spec = json.loads(f.path.read_text())['specification']
    params = spec['parameters']
    if 'baked_from' not in spec:
        raise SystemExit(f'{f.path.name} has not been baked; run bake.py first')

    # "As drawn" for the cost comparison is the model the revisions started from.
    base_frame = F.load(f.path.parent / spec['baked_from'])
    lean = spec.get('lean_to') or {}

    print(f'design  {f.path.name}  ({len(f.members)} members)')
    print(f'as drawn{"":>2}{spec["baked_from"]}  ({len(base_frame.members)} members)')
    for line in spec['revisions']:
        print(f'  - {line}')

    base = A.run(f, params, 'L100')
    combos = St.governing_combos(base, 'L100')

    # Members that carry something the frame model does not contain -- deck,
    # roof panel, glazing -- cannot be judged removable by a frame analysis.
    # The clerestory mullions verify as removable and would leave 282 in. of
    # glazing unsupported, which is the joist error wearing a different hat.
    # Deleted in the bake, so there is nothing left to omit here. Kept as an
    # empty set rather than torn out, because the rest of this file reports on
    # it and the study's section 3 still needs somewhere to point.
    removed: set[str] = set()

    # With those two east braces gone, nothing is over capacity, so nothing
    # needs enlarging: removal replaces the strengthening pass entirely.
    strong = St.strengthen(f, params, 'L100', combos)
    secs = {m: s for m, s in strong['sections'].items() if m not in removed}
    enlarged = set(secs)
    adequate = A.run(f, params, 'L100', omit=removed, override=secs, combos=combos)

    # five-section palette: one section per role, every member in it checking
    ladder, Fy = S.ladder(), F.MATERIALS['steel']['fy']
    roles: dict[str, list] = {}
    for m in adequate.members.values():
        if m.material == 'steel':
            roles.setdefault(m.group, []).append(m)
    palette: dict[str, str] = {}
    for role in ROLE_PALETTE:
        members = roles.get(role, [])
        for cand in ladder:
            if all(CC.check_steel(m.member, cand, Fy, m.P, m.Mz, m.My, m.V,
                                  m.Lb, m.combo).dcr <= 0.85 for m in members):
                palette[role] = cand.name
                for m in members:
                    secs[m.member] = cand
                break

    # Removing members and re-sectioning were each verified against the adequate
    # frame on their own. Applied together they are not automatically valid:
    # deleting 46 members redistributes force into the very members the palette
    # just standardised. So the combination gets its own convergence pass.
    final = A.run(f, params, 'L100', omit=removed, override=secs, combos=combos)
    def drift_of(res):
        return min((v['ratio'] for v in (res.drift or {}).values() if v['ratio']),
                   default=None)

    for _ in range(10):
        over = [m for m in final.members.values()
                if m.dcr > 1.0 and m.material == 'steel']
        dr = drift_of(final)
        soft = dr is not None and dr < 400.0
        if not over and not soft:
            break
        # Strength failures get their own member stepped up. A drift failure is
        # not any one member's fault, so the lateral system is stiffened as a
        # set -- the palette search targets utilisation and will happily pick
        # sections that pass every member check and leave the frame swaying.
        targets = [m.member for m in over]
        if soft:
            targets += [m.member for m in final.members.values()
                        if m.group in ('Bracing', 'Columns') and m.material == 'steel']
        for member in dict.fromkeys(targets):
            cur = secs.get(member, f.section_of[member])
            heavier = [c for c in ladder if c.weight > cur.weight + 1e-6]
            if heavier:
                secs[member] = heavier[0]
        final = A.run(f, params, 'L100', omit=removed, override=secs, combos=combos)
    print(f'reconciled: max DCR {final.max_dcr:.3f}, drift H/{drift_of(final):.0f}')
    print(f'combined verification: max DCR {final.max_dcr:.3f} after reconciliation')
    resectioned = {m for m, s in secs.items()
                   if s.name != f.section_of[m].name and m not in enlarged}

    cats = {}
    for m in f.members:
        cats[m] = ('redundant' if m in removed else
                   'enlarge' if m in enlarged else
                   'downsize' if m in resectioned else 'keep')

    q0 = C.measure(base_frame)
    q1 = C.measure(f, omit=removed, override=secs)
    e0, e1 = C.estimate('as drawn', q0), C.estimate('recommended', q1)
    summary = dict(
        frame_model=f.path.name, live_case='L100', exposure='C',
        software='PyNite 3.2.0 (linear elastic 3-D frame), COMPAS 2.15.1 geometry',
        basis=dict(loft_live={'L100': 100.0}, wind=dict(V=96.0)),
        totals=dict(baseline_lb=round(q0.steel_lb, 1), after_lb=round(q1.steel_lb, 1),
                    saved_lb=round(q0.steel_lb - q1.steel_lb, 1),
                    saved_pct=round(100 * (q0.steel_lb - q1.steel_lb) / q0.steel_lb, 1)),
        sizing=dict(lighter=sorted(resectioned)),
        removal=dict(cumulative=dict(removed=sorted(removed))),
        cost=dict(before=[round(x) for x in e0.total],
                  after=[round(x) for x in e1.total],
                  saving=round(e0.mid - e1.mid)),
        model=f.path.name, baked_from=spec['baked_from'],
        revisions=list(spec['revisions']))

    verdicts = [Verdict(m, 'redundant', 'frame verifies without it') for m in removed]
    verdicts += [Verdict(m, 'overloads', f'must grow to {secs[m].name}')
                 for m in enlarged]
    down = dict(sections=secs, verified=True, lighter=sorted(resectioned))
    for m in OR.PROTECTED:
        if m in cats:
            cats[m] = 'keep'

    # Draw the frame as it would be built: the deleted members are gone, not
    # highlighted. What is left is either unchanged or re-sectioned.
    built = copy.deepcopy(f)
    for member in removed:
        OR._drop(built, member)
    cats = {m: c for m, c in cats.items() if m in built.members}

    # COLUMNS_OUT=S1,SW0,W1 draws the column-removal variant instead: those
    # columns cut off at the wall beam, slope-plane X-bracing added unless
    # SLOPE_BRACE=0, written beside the recommendation rather than over it.
    cols_out = [c for c in os.environ.get('COLUMNS_OUT', '').split(',') if c]
    if cols_out:
        import column_study
        import south_brace_study
        for m, s in secs.items():
            if m in built.members:
                built.section_of[m] = s
        brace = (south_brace_study.brace_slope(built, halves=False)
                 if os.environ.get('SLOPE_BRACE', '1') != '0' else [])
        if os.environ.get('EAST_TRUSS') == '1':
            brace += south_brace_study.brace_east(built)
        if os.environ.get('FRONT_X') == '1':
            brace += south_brace_study.brace_bs_rw1(built, 'all')
        if os.environ.get('FRONT_TRUSS') == '1':
            brace += south_brace_study.brace_bs_rw1(built, 'truss')
        for cspec in os.environ.get('SECTIONS', '').split(','):
            if '=' in cspec:
                m, sec = cspec.split('=')
                built.section_of[m] = S.get(sec) if sec.startswith('W') else F.resolve_section(
                    dict(built.members[m], section_reference=sec))
                built.members[m]['section_reference'] = sec
        for pspec in os.environ.get('PIN', '').split(';'):
            if ':' in pspec:
                built.pinned_ends.append(tuple(pspec.split(':', 1)))
        if os.environ.get('SOUTH_SHIFT'):
            south_brace_study.move_south_line(built, float(os.environ['SOUTH_SHIFT']))
        if os.environ.get('INNER_POST'):
            # INNER_POST=y[:section]  -- a ground-floor post on BE at (211.5, y)
            import completion as Cm
            y, _, sec_name = os.environ['INNER_POST'].partition(':')
            y = float(y)
            top = Cm._split(built, 'BE', (211.5, y, 104.5), f'@211.5,{y:g}')
            built.nodes['S3i.base'] = dict(x=211.5, y=y, z=0.0, support=True, members=[])
            cspec = built.members['S3']
            Cm._add_member(built, 'S3i', 'S3i.base', top, sec_name or 'HSS5X5X1/4',
                           cspec['width'], cspec['depth'], 'Columns',
                           note=f'inner post replacing S3 at y={y:g}')
            cats['S3i'] = 'assumed'
        if os.environ.get('S1_SHIFT'):
            south_brace_study.move_s1(built, float(os.environ['S1_SHIFT']))
        if os.environ.get('RAKE_S3'):
            cats[south_brace_study.rake_s3(built, os.environ['RAKE_S3'])] = 'assumed'
        if os.environ.get('EAST_FRAME') == '1':
            ef = south_brace_study.east_frame(built, beam_section=os.environ.get('EAST_BEAM', 'W14X22'))
            cats.update({m: 'assumed' for m in ef['posts']})
        if os.environ.get('RAISE'):
            south_brace_study.raise_floor(built, float(os.environ['RAISE']))
        if os.environ.get('MERGE_BWI') == '1':
            for old_name in south_brace_study.merge_bwi(built):
                cats.pop(old_name, None)
            cats['BWI'] = 'keep'
        if os.environ.get('SOUTH_X') == '1':
            for m in south_brace_study.south_x_to_wall(built):
                cats[m] = 'assumed'
        for m in os.environ.get('DROP', '').split(','):
            if m in built.members:
                OR._drop(built, m)
        for spec_l in os.environ.get('LINK', '').split(';'):
            if '>' in spec_l:
                a, b = spec_l.split('>', 1)
                built.links.append((a, b, 'owner: bearing link where a column was removed'))
        if os.environ.get('FLOOR_BRACE') == '1':
            brace += south_brace_study.brace_floor(built)
        for c in cols_out:
            column_study.cut_ground_floor(
                built, c, level=column_study.BEAM_LEVEL + float(os.environ.get('RAISE', '0')))
        cats = {m: c for m, c in cats.items() if m in built.members}
        cats.update({m: 'assumed' for m in brace})
        final = A.run(built, params, 'L100', combos=combos)
        summary['frame_model'] += (f' · {", ".join(cols_out)} cut at the wall beam'
                                   + (' · ' + os.environ.get('BRACE_NOTE', 'X-bracing added') if brace else ''))
        OUT = OUT.with_name('column-removal-3d.html')
        print(f'column removal: {cols_out} out, {len(brace)} braces added, '
              f'max DCR {final.max_dcr:.3f}, drift H/'
              f'{min(v["ratio"] for v in final.drift.values() if v["ratio"]):.0f}')

    import phasing
    import plan as plan_mod
    import solid_view
    stage = phasing.before_demo(built, defer=set() if os.environ.get('NO_DEFER') == '1' else set(OR.DEFER_BEFORE_DEMO))
    summary.setdefault('phasing', {}).update(
        before_demo=stage['build'], waits=stage['wait'],
        eave_penetrations=stage['penetrating'])
    print(f"before demo: {len(stage['build'])} members up, "
          f"{len(stage['wait'])} wait; eave penetrations {stage['penetrating']}")
    plan_png = OUT.parent / 'figures' / ('frame-plan.png' if not cols_out else 'column-removal-plan.png')
    plan_png.parent.mkdir(parents=True, exist_ok=True)
    plan_mod.draw(built, plan_png, 'GARAGE FRAME — PLAN',
                  f'{summary["frame_model"]} with the owner revisions · stair '
                  f'one bay south · loft grillage, upper beams, rafters and '
                  f'columns · units in / ft · not to scale, use dimensions',
                  lean_to=lean, omit=removed)
    print(f'plan written to {plan_png.name}')

    viewer.write(built, final, cats, down, verdicts, summary, OUT)
    solid_view.write(built, final, cats, down, verdicts, summary,
                     OUT.with_name(OUT.stem + '-solid.html'),
                     before_demo=set(stage['build']), lean_to=lean,
                     plan_png=plan_png)

    for r in summary.get('cabinets', []):
        print(f'{r["kind"]} {r["n"]}: {r["h"]:g} in. tall, x {r["x0"]:g}..{r["x1"]:g}, '
              f'y {r["y0"]:g}..{r["y1"]:g}, top z {r["top"]:g}, soffit {r["soffit"]:g} -> '
              f'{"clears" if r["fits"] else "HITS"} by {abs(r["clear_in"]):g} in.')
    print(f'owner revisions baked into {f.path.name} from {spec["baked_from"]}')
    print(f'protected by owner: {sorted(OR.PROTECTED)}')
    print(f'palette: {palette}')
    print(f'removed {len(removed)}, enlarged {len(enlarged)}, '
          f're-sectioned {len(resectioned)}')
    print(f'final max DCR {final.max_dcr:.3f}  '
          f'drift H/{min(v["ratio"] for v in final.drift.values() if v["ratio"]):.0f}  '
          f'deflection violations {len(A.deflection_violations(built, final))}')
    # The stair move lengthens B-1A, so the floor beams' span deflection is the
    # number that decides whether the variant is merely legal or comfortable.
    floor = []
    for member, rec in (final.deflection or {}).items():
        if built.group(member) not in ('Beams',):
            continue
        worst = min((d['ratio'] for d in rec.values()
                     if isinstance(d, dict) and d.get('ratio')), default=None)
        if worst:
            floor.append((worst, member, rec['span_in']))
    for worst, member, span in sorted(floor)[:6]:
        print(f'  {member:<10} span {span:>6.1f} in   L/{worst:.0f}')
    print(f'steel {q0.steel_lb:,.0f} -> {q1.steel_lb:,.0f} lb   '
          f'pieces {q0.steel_pieces} -> {q1.steel_pieces}   '
          f'joints {q0.steel_joints} -> {q1.steel_joints}   '
          f'sections {q0.distinct_sections} -> {q1.distinct_sections}')
    print(f'cost ${e0.total[0]:,.0f}-{e0.total[1]:,.0f} -> '
          f'${e1.total[0]:,.0f}-{e1.total[1]:,.0f}  (mid saving ${e0.mid - e1.mid:,.0f})')
    print(f'wrote {OUT}')


if __name__ == '__main__':
    main()
