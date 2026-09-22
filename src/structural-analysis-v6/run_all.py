#!/usr/bin/env python
"""Run the whole structural study and write every output.

    python run_all.py [--live L40|L125] [--exposure C|D] [--quick]

Writes to ``results/``: the machine-readable result set, the member schedules,
the figures, and the interactive model.  ``publish.py`` copies the reviewed
package into the report.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from dataclasses import asdict
from pathlib import Path

import analysis
import completion
import frame as framemod
import loads as L
import sections
import studies
import viewer
import visualize
from project_paths import VIZ_DIR

HERE = Path(__file__).resolve().parent
OUT = VIZ_DIR
FIG = OUT / 'figures'

DOWNSIZE_FLOOR = 0.35      # members below this utilisation are downsizing candidates


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--live', default=L.DESIGN_LIVE_CASE,
                    choices=list(L.LOFT_LIVE_CASES))
    ap.add_argument('--exposure', default=L.WIND['exposure'], choices=['B', 'C', 'D'])
    ap.add_argument('--lineage', default=framemod.DEFAULT_LINEAGE,
                    help='which frame-models lineage to analyse')
    ap.add_argument('--quick', action='store_true',
                    help='skip the removal and cumulative studies')
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    t0 = time.time()

    base = framemod.load(lineage=args.lineage)
    params = json.loads(base.path.read_text())['specification']['parameters']
    print(f'frame model   {base.path.name}')
    others = [x for x in framemod.lineages() if x != args.lineage]
    if others:
        print(f'lineage       {args.lineage}  (also present: {", ".join(others)})')
    print(f'              {len(base.members)} members, {len(base.segments)} elements, '
          f'{len(base.supports)} supports, {base.total_weight():,.0f} lb')

    full = completion.completed(base, params)
    added = completion.added_members(full)
    print(f'completion    added {len(added)}: {", ".join(added)}')

    print('\n-- stage 0: exactly as drawn -------------------------------------')
    as_drawn = analysis.run(base, params, args.live, args.exposure)
    _summarise(as_drawn)

    print('\n-- stage 1: upper roof framed ------------------------------------')
    done = analysis.run(full, params, args.live, args.exposure)
    _summarise(done)

    print('\n-- loft live load sensitivity ------------------------------------')
    others = [c for c in L.LOFT_LIVE_CASES if c != args.live]
    runs = {c: analysis.run(full, params, c, args.exposure) for c in others}
    alt = runs[others[-1]]
    loft = [m for m in done.members
            if done.members[m].group in analysis.FLOOR_GROUPS]
    loft_sensitivity = {}
    for tag, r in [(args.live, done)] + [(c, runs[c]) for c in others]:
        who = max((r.members[m] for m in loft if m in r.members),
                  key=lambda m: m.dcr, default=None)
        loft_sensitivity[tag] = dict(
            psf=L.LOFT_LIVE_CASES[tag]['psf'], frame_max_dcr=round(r.max_dcr, 3),
            loft_max_dcr=round(who.dcr, 3) if who else 0.0,
            member=who.member if who else None,
            section=who.section if who else None,
            mode=who.mode if who else None,
            basis=L.LOFT_LIVE_CASES[tag]['basis'])
        print(f'  {tag} ({L.LOFT_LIVE_CASES[tag]["psf"]:>3.0f} psf): frame max DCR '
              f'{r.max_dcr:.2f}; loft framing max DCR '
              f'{loft_sensitivity[tag]["loft_max_dcr"]:.2f}'
              f'{" on " + who.member if who else ""}')

    print('\n-- wind exposure sensitivity -------------------------------------')
    expD = analysis.run(full, params, args.live, 'D')
    print(f'  Exposure {args.exposure}: max DCR {done.max_dcr:.2f}   '
          f'Exposure D: max DCR {expD.max_dcr:.2f}')

    print('\n-- stage 2: X-brace crossings connected --------------------------')
    crossed, crossings = completion.crossing_joints(full)
    cross_r = analysis.run(crossed, params, args.live, args.exposure)
    print(f'  {len(crossings)} crossings joined; unbraced lengths halved on '
          f'{len({m for c in crossings for m in c["members"]})} braces')
    _summarise(cross_r)

    combos = studies.governing_combos(done, args.live)
    print(f'\ncombination pruning  {len(L.strength_combos(args.live))} -> {len(combos)} '
          f'for the member studies')

    # ------------------------------------------------------------------
    # The optimisation studies run on a frame that passes.  Asking which
    # members can be deleted from a frame that is already over capacity
    # answers nothing: the criterion would have to be "no worse than a
    # structure that does not work".  So the frame is first brought up to
    # adequate, and every reduction after that is measured against it.
    # ------------------------------------------------------------------
    print('\n-- stage 3: strengthen to adequate -------------------------------')
    strong = studies.strengthen(crossed, params, args.live, combos)
    for h in strong['rounds']:
        print(f'    round {h["round"]}: {h["over_capacity"]} over capacity '
              f'(max DCR {h["max_dcr"]}), upsized {h["upsized"]}'
              + (f', {h["at_ladder_top"]} at the top of the ladder'
                 if h['at_ladder_top'] else ''))
    print(f'  adequate={strong["adequate"]}  max DCR {strong["result"].max_dcr:.2f}  '
          f'{len(strong["sections"])} sections increased, '
          f'{strong["added_lb"]:+,.0f} lb')
    for m, sec in sorted(strong['sections'].items()):
        print(f'    enlarge  {m:<24}{crossed.section_of[m].name:<22}-> {sec.name}')
    for v in strong.get('deflection_violations') or []:
        print(f'    deflection  {v["member"]}: L/{v["ratio"]:.0f} against '
              f'L/{v["limit"]:.0f} under {v["combo"]}')
    beyond = studies.beyond_ladder(crossed, strong['result'])
    for b in beyond:
        print(f'    beyond the ladder: {b["member"]} ({b["section"]}) '
              f'DCR {b["dcr"]:.2f} — {b["note"]}')
    adequate = strong['result']

    print('\n-- gravity deflection --------------------------------------------')
    for w in _worst_deflections(crossed, adequate, 6):
        print(f'    {w["member"]:<24}span {w["span_in"]:>6.1f} in  '
              f'{w["deflection_in"]:.3f} in  L/{w["ratio"]:.0f}  '
              f'(limit L/{w["limit"]:.0f}) {"ok" if w["passes"] else "FAILS"}')

    print('\n-- stage 4: lighten ----------------------------------------------')
    light = studies.lighten(crossed, params, strong['sections'], args.live, combos)
    for h in light['rounds']:
        print(f'    round {h["round"]}: proposed {h["proposed"]}, accepted '
              f'{h["accepted"]}, max DCR {h["max_dcr"]}'
              + (f', reverted {len(h["reverted"])}' if h.get('reverted') else ''))
    print(f'  {len(light["lighter"])} sections lighter than as drawn, '
          f'{len(light["heavier"])} heavier; net {light["saved_lb"]:+,.0f} lb; '
          f'max DCR {light["max_dcr_after"]}')
    for m in light['lighter']:
        print(f'    lighten  {m:<24}{crossed.section_of[m].name:<22}'
              f'-> {light["sections"][m].name}')

    removal, cumulative = [], {}
    if not args.quick:
        print('\n-- stage 5: removal ----------------------------------------------')
        t = time.time()
        final_sections = light['sections']
        removal = studies.removal_study(crossed, params, light['result'], args.live,
                                        combos, override=final_sections)
        red = [r for r in removal if r.verdict == 'redundant']
        print(f'  {len(removal)} members tested in {time.time() - t:.0f}s: '
              f'{sum(1 for r in removal if r.verdict == "unstable")} critical, '
              f'{sum(1 for r in removal if r.verdict == "overloads")} required, '
              f'{len(red)} individually redundant')
        cumulative = studies.cumulative_removal(
            crossed, params, [r.member for r in red], args.live, combos,
            override=final_sections)
        print(f'  removable together: {len(cumulative["removed"])} members, '
              f'{cumulative["weight_saved_lb"]:,.0f} lb, '
              f'max DCR after {cumulative["max_dcr_after"]}, '
              f'drift H/{cumulative.get("drift_ratio") or 0:.0f}')

    down = dict(lighter=light['lighter'], heavier=light['heavier'],
                sections=light['sections'],
                proposals={m: s.name for m, s in light['sections'].items()},
                weight_saved_lb=light['saved_lb'],
                max_dcr_after=light['max_dcr_after'],
                verified=True, converged=True, rounds=light['rounds'],
                beyond_ladder=beyond,
                strengthen=dict(rounds=strong['rounds'], adequate=strong['adequate'],
                                added_lb=strong['added_lb'],
                                sections={m: x.name for m, x in
                                          strong['sections'].items()},
                                stuck=strong['stuck']))

    categories = _categorise(crossed, adequate, down, removal, added)
    _write_outputs(base, crossed, params, args, as_drawn, done, alt, expD,
                   down, removal, cumulative, categories, combos,
                   cross_r, crossings, adequate, loft_sensitivity,
                   final=light['result'])
    print(f'\nwrote {OUT}  ({time.time() - t0:.0f}s total)')


# ---------------------------------------------------------------------------

def _summarise(r: analysis.Result) -> None:
    if not r.stable:
        print(f'  UNSTABLE: {r.message}')
        return
    over = r.overstressed()
    worst = max(r.equilibrium.values(), key=lambda v: v['relative'], default=None)
    print(f'  max DCR {r.max_dcr:.2f}   {len(over)} members over capacity   '
          f'weight {r.total_weight:,.0f} lb')
    if worst:
        print(f'  vertical equilibrium closes to {worst["relative"]:.1e}')
    if r.drift:
        d = min(v['ratio'] for v in r.drift.values() if v['ratio'])
        print(f'  worst wind drift H/{d:.0f}  (target H/{L.DEFLECTION_LIMITS["drift_wind"]:.0f})')
    for g in r.gaps:
        print(f'  GAP  {g["surface"]}: {g["area_ft2"]} sq ft, '
              f'{g["clear_span_in"]:.0f} in clear, {g["issue"]}')
    for m in over[:5]:
        print(f'    {m.dcr:6.2f}  {m.member:<26}{m.section:<20}{m.mode}  [{m.combo}]')


def _categorise(frame, result, down, removal, added) -> dict[str, str]:
    """One recommended action per member, in priority order.

    Deletion beats resizing: there is no point reporting a lighter section for a
    member the frame does not need at all.
    """
    cumulative = set()
    redundant = {r.member for r in removal if r.verdict == 'redundant'}
    lighter = set(down.get('lighter') or ())
    heavier = set(down.get('heavier') or ())
    cats = {}
    for m in frame.members:
        if m in redundant:
            cats[m] = 'redundant'
        elif m in heavier:
            cats[m] = 'enlarge'
        elif m in added:
            cats[m] = 'assumed'
        elif m in lighter:
            cats[m] = 'downsize'
        else:
            cats[m] = 'keep'
    return cats


def _write_outputs(base, full, params, args, as_drawn, done, alt, expD,
                   down, removal, cumulative, categories, combos,
                   cross_r=None, crossings=None, adequate=None,
                   loft_sensitivity=None, final=None) -> None:
    removed = set(cumulative.get('removed', []))
    downsized = down.get('sections', {}) if down.get('verified') else {}

    # Schedules describe the frame the recommendations apply to -- the adequate
    # frame after resizing -- not the stage-1 model that fails.
    schedule_result = final or adequate or done
    _member_schedule(full, schedule_result, down, removal, categories,
                     OUT / 'member-schedule.csv')
    _load_schedule(schedule_result, OUT / 'load-cases.csv')
    _reaction_schedule(schedule_result, OUT / 'reactions.csv')

    summary = dict(
        generated=time.strftime('%Y-%m-%d %H:%M'),
        frame_model=base.path.name, frame_version=base.version,
        live_case=args.live, exposure=args.exposure,
        software='PyNite 3.2.0 (linear elastic 3-D frame), COMPAS 2.15.1 geometry',
        basis=dict(code=L.SITE['code'], site=L.SITE['address'],
                   risk_category=L.SITE['risk_category'],
                   dead=L.DEAD, roof_live=L.ROOF_LIVE,
                   loft_live={k: v['psf'] for k, v in L.LOFT_LIVE_CASES.items()},
                   hoist=L.HOIST, wind={k: v for k, v in L.WIND.items()},
                   seismic=done.seismic),
        counts=dict(members=len(full.members), elements=len(full.segments),
                    supports=len(full.supports),
                    added=completion.added_members(full),
                    concept_envelope=sum(
                        1 for m in base.members.values()
                        if (m.get('section_reference') or '').strip()
                        == 'concept envelope'),
                    links=[dict(between=[i, j], kind=k) for i, j, k in base.links]),
        loft_sensitivity=loft_sensitivity,
        scenarios=dict(
            as_drawn=_scenario(as_drawn, base), completed=_scenario(done, full),
            live_sensitivity=_scenario(alt, full), exposure_D=_scenario(expD, full),
            crossings_joined=_scenario(cross_r, full) if cross_r else None,
            adequate=_scenario(adequate, full) if adequate else None),
        crossings=dict(joints=crossings or []),
        combinations=dict(total=len(L.strength_combos(args.live)),
                          used_in_studies=sorted(combos)),
        sizing=dict(verified=down.get('verified'),
                    converged=down.get('converged'),
                    still_over_capacity=down.get('still_over_capacity'),
                    weight_saved_lb=down.get('weight_saved_lb'),
                    max_dcr_after=down.get('max_dcr_after'),
                    rounds=down.get('rounds'),
                    lighter=down.get('lighter'), heavier=down.get('heavier'),
                    beyond_ladder=down.get('beyond_ladder'),
                    strengthen=down.get('strengthen'),
                    proposals=down.get('proposals')),
        removal=dict(tested=len(removal),
                     redundant=[r.member for r in removal if r.verdict == 'redundant'],
                     critical=[r.member for r in removal if r.verdict == 'unstable'],
                     cumulative=cumulative),
        totals=_totals(full, downsized, removed),
    )
    (OUT / 'results.json').write_text(json.dumps(summary, indent=2, default=str))

    print('\n-- drawings ------------------------------------------------------')
    stamp = (f'{L.SITE["code"]} · loft live load '
             f'{L.LOFT_LIVE_CASES[args.live]["psf"]:.0f} psf · wind '
             f'{L.WIND["V"]:.0f} mph Exposure {args.exposure}')
    visualize.utilisation_sheet(
        base, as_drawn, FIG / 'utilisation-as-drawn.png',
        'Utilisation of the frame exactly as drawn',
        f'No secondary framing: the upper roof has no load path across it. '
        f'Worst member at {as_drawn.max_dcr:.2f} of capacity · {stamp}')
    visualize.utilisation_sheet(
        full, done, FIG / 'utilisation.png',
        'Utilisation with the upper roof framed, before any correction',
        f'Assumed head beam and purlins added; X-brace crossings still open. '
        f'Worst member at {done.max_dcr:.2f} of capacity · {stamp}')
    if adequate:
        visualize.utilisation_sheet(
            full, adequate, FIG / 'utilisation-adequate.png',
            'Utilisation after the crossings are joined and four members enlarged',
            f'The frame this study\'s reduction recommendations are measured '
            f'against. Worst member at {adequate.max_dcr:.2f} of capacity · {stamp}')
    visualize.opportunity_sheet(
        full, categories, FIG / 'opportunity-map.png',
        'Where material can come out, and where it has to go in',
        f'Verified by re-analysis: {len(removed)} members removed together, '
        f'{len(down.get("lighter") or [])} sections lighter, '
        f'{len(down.get("heavier") or [])} enlarged; all combinations re-solved',
        'Green members were deleted and every load combination re-solved with the '
        'rest of the frame carrying their load; joists and rafters are only '
        'deleted where the deck can still span between the survivors.\n'
        'Blue members verified at the lighter section in the member schedule. Red '
        'members fail at the section as drawn and must be increased.')
    visualize.weight_chart(full, categories, downsized, removed,
                           FIG / 'weight-by-group.png',
                           'Member weight by group, as drawn and after the '
                           'verified reductions')
    visualize.utilisation_histogram(
        final or adequate or done, FIG / 'utilisation-histogram.png',
        'How hard each member is working -- the gap between the bars and 1.00 '
        'is unused material')
    viewer.write(full, final or adequate or done, categories, down, removal,
                 summary, OUT / 'fea-model-3d.html')
    for f in sorted(OUT.rglob('*')):
        if f.is_file():
            print(f'  {f.relative_to(OUT)}  ({f.stat().st_size / 1024:.0f} kB)')


def _worst_deflections(frame, r, n: int = 12) -> list[dict]:
    """The members that sag most under gravity, as a fraction of their span."""
    rows = []
    for member, rec in (r.deflection or {}).items():
        cls = analysis._span_class(frame, member)
        if cls is None:
            continue
        combo, limit = analysis.DEFLECTION_RULE[cls]
        d = rec.get(combo)
        if not d or not d.get('ratio'):
            continue
        rows.append(dict(member=member, group=frame.group(member), rule=cls,
                         span_in=rec['span_in'], combination=combo,
                         deflection_in=abs(d['defl_in']), ratio=d['ratio'],
                         limit=limit, passes=d['ratio'] >= limit))
    return sorted(rows, key=lambda x: x['ratio'])[:n]


def _scenario(r: analysis.Result, frame=None) -> dict:
    return dict(stable=r.stable, max_dcr=round(r.max_dcr, 3),
                deflection_violations=(analysis.deflection_violations(frame, r)
                                       if frame else None),
                worst_deflections=(_worst_deflections(frame, r) if frame else None),
                over_capacity=[dict(member=m.member, section=m.section,
                                    dcr=round(m.dcr, 3), mode=m.mode, combo=m.combo)
                               for m in r.overstressed()],
                equilibrium=r.equilibrium, drift=r.drift, gaps=r.gaps,
                member_weight_lb=round(r.total_weight, 1))


def _totals(frame, downsized, removed) -> dict:
    cur = sum(frame.member_weight(m) for m in frame.members)
    new = sum(0.0 if m in removed else frame.member_weight(m) *
              (downsized[m].weight / frame.section_of[m].weight
               if m in downsized else 1.0) for m in frame.members)
    return dict(baseline_lb=round(cur, 1), after_lb=round(new, 1),
                saved_lb=round(cur - new, 1),
                saved_pct=round(100.0 * (cur - new) / cur, 1) if cur else 0.0,
                basis='completed frame -- the members as drawn plus the assumed '
                      'upper-roof framing; this is the baseline the reductions '
                      'are measured against')


def _member_schedule(frame, result, down, removal, categories, path: Path) -> None:
    verdicts = {r.member: r for r in removal}
    proposals = down.get('sections', {}) if down.get('verified') else {}
    rows = []
    for name in sorted(frame.members):
        m = result.members.get(name)
        sec = frame.section_of[name]
        v = verdicts.get(name)
        p = proposals.get(name)
        rows.append(dict(
            member=name, group=frame.group(name), material=frame.material(name),
            section=sec.name,
            section_source=frame.members[name].get('section_reference', ''),
            length_in=round(frame.member_length(name), 1),
            weight_lb=round(frame.member_weight(name), 1),
            area_in2=round(sec.A, 3), Iz_in4=round(sec.Iz, 3),
            unbraced_in=round(m.Lb, 1) if m else '',
            slenderness_KLr=round(m.slenderness, 0) if m else '',
            dcr=round(m.dcr, 3) if m else '',
            governing_mode=m.mode if m else '',
            governing_combination=m.combo if m else '',
            axial_lb=round(m.P, 0) if m else '',
            moment_strong_lbin=round(m.Mz, 0) if m else '',
            shear_lb=round(m.V, 0) if m else '',
            check_basis=m.basis if m else '',
            flags='; '.join(m.flags) if m and m.flags else '',
            action=categories.get(name, ''),
            removal_verdict=v.verdict if v else '',
            removal_effect=v.detail if v else '',
            proposed_section=p.name if p else '',
            proposed_saving_lb=round(frame.member_weight(name) *
                                     (1 - p.weight / sec.weight), 1) if p else ''))
    _csv(path, rows)


def _load_schedule(result, path: Path) -> None:
    rows = []
    for case, a in sorted(result.applied.items()):
        rows.append(dict(load_case=case,
                         Fx_east_lb=a['fx'], Fz_up_lb=a['fy'], Fy_north_lb=a['fz'],
                         detail='; '.join(f'{k}={v}' for k, v in a.items()
                                          if k not in ('fx', 'fy', 'fz'))))
    _csv(path, rows)


def _reaction_schedule(result, path: Path) -> None:
    rows = [dict(support=k, **v) for k, v in sorted(result.reactions.items())]
    _csv(path, rows)


def _csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == '__main__':
    main()
