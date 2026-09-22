"""Smallest standard beam that works at a given live load.

In a grillage the beams share load through the members that cross them, so making
one lighter pushes work onto its neighbours. A section cannot be chosen from a single
set of forces. This walks the ladder instead: start every beam at the lightest shape
in the catalogue, solve the whole frame, bump anything that fails, and solve again
until a pass changes nothing. What comes back is the lightest self-consistent set.

Two answers are produced, because they are different questions:
  - per beam   -- the lightest shape each member individually needs
  - one size   -- the lightest single shape that works everywhere, which is usually
                  what gets ordered

Run: /Volumes/Proj/proj/CAD/garage/.venv/bin/python size.py [live_psf]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as A                                # noqa: E402
import ladder                                      # noqa: E402
import codecheck                                   # noqa: E402
import frame as framemod                           # noqa: E402
import frame_models                                # noqa: E402
import geometry as G                               # noqa: E402
import simplespan                                  # noqa: E402

LIVE_LIMIT = A.FLOOR_LIVE_DEFL      # L/360
TOTAL_LIMIT = A.FLOOR_TOTAL_DEFL    # L/240
MAX_PASSES = 40


def solve(frame, tribs, live_psf, override):
    """One full analysis with these sections. Returns per-beam outcome."""
    model, index = framemod.build(frame, override=override)
    A.apply_loads(frame, model, index, tribs, live_psf=live_psf, override=override)
    for name, factors in list(A.STRENGTH.items()) + list(A.SERVICE.items()):
        model.add_load_combo(name, dict(factors))
    model.analyze_linear(check_stability=True, check_statics=False, sparse=True)

    Lb = A.unbraced(frame)
    out = {}
    for m in sorted(frame.members):
        sec = override.get(m, frame.section_of[m])
        els = index[m]
        if frame.material(m) == 'wood':
            P, Mz, My, V = A.member_forces(model, els, 'D + L')
            d = A.span_deflection(frame, model, m, els, 'L only')
            c = codecheck.check_wood(m, sec, P, Mz, My, V, Lb[m], 'D + L',
                                     d['span_in'] if d else 0.0,
                                     d['defl_in'] if d else 0.0)
        else:
            c = None
            for combo in A.STRENGTH:
                P, Mz, My, V = A.member_forces(model, els, combo)
                k = codecheck.check_steel(m, sec, 50_000.0, P, Mz, My, V, Lb[m], combo)
                if c is None or k.dcr > c.dcr:
                    c = k
        live = A.span_deflection(frame, model, m, els, 'L only')
        total = A.span_deflection(frame, model, m, els, 'D + L')
        out[m] = dict(section=sec.name, group=frame.group(m), dcr=c.dcr, mode=c.mode,
                      combo=c.combo, weight=frame.member_length(m) * sec.weight / 12.0,
                      live_ratio=live['ratio'] if live else None,
                      total_ratio=total['ratio'] if total else None,
                      span=live['span_in'] if live else None,
                      flags=list(c.flags))
    return out


def fails(r, ss=None):
    """Why this member is not acceptable, or None.

    A section has to satisfy both readings: the grillage, which assumes rigid
    joints, and the simple-span bound, which assumes none. Sizing to only the
    first would bank on continuity that no connection has been designed to give.
    """
    for tag, d, live, total in (
            ('', r['dcr'], r['live_ratio'], r['total_ratio']),
            (' simple-span', (ss or {}).get('dcr'), (ss or {}).get('live_ratio'),
             (ss or {}).get('total_ratio'))):
        if d is not None and d > 1.0:
            return f'DCR {d:.2f}{tag}'
        if live is not None and live < LIVE_LIMIT:
            return f'live L/{live:.0f}{tag}'
        if total is not None and total < TOTAL_LIMIT:
            return f'total L/{total:.0f}{tag}'
    return None


def sections_now(frame, override):
    return {m: override.get(m, frame.section_of[m]) for m in frame.members}


def size_per_beam(frame, tribs, live_psf, beams):
    """Walk every beam up the ladder together until nothing fails."""
    idx = {b: 0 for b in beams}
    history = []
    for p in range(MAX_PASSES):
        override = {b: ladder.SECTIONS[ladder.LADDER[idx[b]]] for b in beams}
        res = solve(frame, tribs, live_psf, override)
        ss = simplespan.check(frame, tribs, live_psf, 8.0, sections_now(frame, override))
        bumped = []
        for b in beams:
            why = fails(res[b], ss.get(b))
            if why and idx[b] < len(ladder.LADDER) - 1:
                idx[b] += 1
                bumped.append((b, why, ladder.LADDER[idx[b]]))
        history.append(dict(pass_no=p + 1, bumped=[(b, w, s) for b, w, s in bumped]))
        if not bumped:
            return override, res, ss, history
    raise RuntimeError('sizing did not converge')


def size_one_section(frame, tribs, live_psf, beams):
    """Lightest single shape that carries every beam."""
    for name in ladder.LADDER:
        override = {b: ladder.SECTIONS[name] for b in beams}
        try:
            res = solve(frame, tribs, live_psf, override)
        except Exception:
            continue
        ss = simplespan.check(frame, tribs, live_psf, 8.0, sections_now(frame, override))
        bad = {b: fails(res[b], ss.get(b)) for b in beams if fails(res[b], ss.get(b))}
        if not bad:
            return name, res, ss
    return None, None, None


def main(live_psf=60.0):
    path = frame_models.latest('beam-scheme')
    frame = framemod.load(path)
    _, index0 = framemod.build(frame)
    surfs = A.deck_surfaces(frame)
    import surfaces as surf
    tribs = {n: surf.tributary(frame, s, index0) for n, s in surfs.items()}
    beams = sorted(frame.members_in('Beams'))

    per, res_per, ss_per, history = size_per_beam(frame, tribs, live_psf, beams)
    one, res_one, ss_one = size_one_section(frame, tribs, live_psf, beams)
    base = solve(frame, tribs, live_psf, {})          # as-drawn W14X22, for comparison

    def tonnage(res):
        return sum(r['weight'] for b, r in res.items() if r['group'] == 'Beams')

    rows = []
    for b in beams:
        rp, rb, sp = res_per[b], base[b], ss_per.get(b, {})
        rows.append(dict(
            ss_dcr=sp.get('dcr'), ss_live=sp.get('live_ratio'),
            ss_span=sp.get('clear_span'), ss_column_supported=sp.get('column_supported'),
            beam=b, span_in=round(rb['span'], 1) if rb['span'] else None,
            as_drawn='W14X22', as_drawn_dcr=round(rb['dcr'], 3),
            smallest=rp['section'],
            dcr=round(rp['dcr'], 3), mode=rp['mode'],
            live=round(rp['live_ratio']) if rp['live_ratio'] else None,
            total=round(rp['total_ratio']) if rp['total_ratio'] else None,
            governed_by=('deflection' if min(
                rp['live_ratio'] or 9e9, sp.get('live_ratio') or 9e9) < LIVE_LIMIT * 1.3
                and max(rp['dcr'], sp.get('dcr') or 0) < 0.85 else 'strength'),
            weight_lb=round(rp['weight'], 1),
            depth_in=ladder.SECTIONS[rp['section']].d,
            flags='; '.join(rp['flags'])))

    joists = {b: r for b, r in res_per.items() if r['group'] == 'Joists'}
    cols = {b: r for b, r in res_per.items() if r['group'] == 'Columns'}
    worst_j = max(joists.items(), key=lambda t: t[1]['dcr'])
    worst_c = max(cols.items(), key=lambda t: t[1]['dcr'])

    out = dict(
        model=path.name, live_psf=live_psf,
        dead_psf=8.0, question=f'smallest standard W shape per beam at {live_psf:g} psf',
        method=('Iterative: every beam starts at the lightest shape in the catalogue, '
                'the whole grillage is solved, anything failing strength or deflection '
                'moves up one shape, repeat until a pass changes nothing.'),
        acceptance=dict(strength='AISC 360-16 LRFD, DCR <= 1.0, 1.4D and 1.2D+1.6L',
                        live_deflection=f'L/{LIVE_LIMIT:g}',
                        total_deflection=f'L/{TOTAL_LIMIT:g}'),
        ladder_source=('loft-span-study/wshapes.py, AISC v15; Sy, Zy, J and rx derived '
                       '— see ladder.validate()'),
        ladder_validation=ladder.validate(),
        passes=len(history), history=history,
        per_beam=rows,
        per_beam_total_lb=round(tonnage(res_per), 1),
        one_section=one,
        one_section_total_lb=round(tonnage(res_one), 1) if one else None,
        as_drawn_total_lb=round(tonnage(base), 1),
        joists=dict(section=worst_j[1]['section'], worst=worst_j[0],
                    dcr=round(worst_j[1]['dcr'], 3),
                    live_ratio=round(worst_j[1]['live_ratio'])
                    if worst_j[1]['live_ratio'] else None,
                    note='joists and columns were not resized; this is what they do '
                         f'at {live_psf:g} psf with the per-beam steel'),
        columns=dict(section=worst_c[1]['section'], worst=worst_c[0],
                     dcr=round(worst_c[1]['dcr'], 3)),
        limits=('Gravity only, linear elastic, pinned bases. No lateral load, no '
                'connection, no footing. Lightest by weight is not the same as '
                'cheapest to fabricate or erect. Requires review and sealing by the '
                'responsible California-licensed engineer.'))
    (HERE / f'sizing-{live_psf:g}psf.json').write_text(json.dumps(out, indent=2))

    print(f'{path.name}   live {live_psf:g} psf + dead 8 psf\n')
    print(f'converged in {len(history)} passes\n')
    print(f'{"beam":<7}{"smallest":>10}{"depth":>7}{"grillage":>19}{"simple span":>20}'
          f'   governed by')
    print(f'{"":<7}{"":>10}{"":>7}{"DCR":>9}{"L/live":>10}{"DCR":>10}{"L/live":>10}')
    for r in rows:
        print(f'{r["beam"]:<7}{r["smallest"]:>10}{r["depth_in"]:>7.1f}'
              f'{r["dcr"]:>9.3f}{r["live"] or "-":>10}'
              f'{(r["ss_dcr"] if r["ss_dcr"] is not None else 0):>10.3f}'
              f'{r["ss_live"] or "-":>10}   {r["governed_by"]}'
              f'{"" if r["ss_column_supported"] else "  [no column either end]"}')
    print(f'\nbeam steel   as drawn (all W14X22) {out["as_drawn_total_lb"]:>8,.0f} lb')
    print(f'             smallest per beam      {out["per_beam_total_lb"]:>8,.0f} lb')
    print(f'             lightest single size   {out["one_section_total_lb"]:>8,.0f} lb'
          f'   ({one} throughout)')
    print(f'\njoists  {worst_j[1]["section"]}  worst DCR {worst_j[1]["dcr"]:.3f} '
          f'({worst_j[0]})')
    print(f'columns {worst_c[1]["section"]}  worst DCR {worst_c[1]["dcr"]:.3f} '
          f'({worst_c[0]})')
    return out


if __name__ == '__main__':
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 60.0)
