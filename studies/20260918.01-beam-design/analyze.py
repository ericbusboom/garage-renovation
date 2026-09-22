"""Gravity analysis of the BEAM-001 frame at the owner's 100 psf.

Reuses structural-analysis-v6 wholesale: its COMPAS loader and PyNite assembly
(``frame``), its AISC 360-16 and NDS checks (``codecheck``), its section library
(``sections``), its load basis (``loads``), and its Voronoi tributary distribution
(``surfaces``). Only two things are new here: the load surfaces are this scheme's
six deck rectangles rather than the truss model's roofs and walls, and the combos
are gravity only.

Gravity only, and deliberately so: this scheme has no roof, no cladding and no
lateral system yet, so there is no enclosure to put wind or seismic on. That is a
gap in the scheme, not a result.

Run: /Volumes/Proj/proj/CAD/garage/.venv/bin/python analyze.py
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'compas-study'))
sys.path.insert(0, str(ROOT / 'structural-analysis-v6'))
import frame_models                                # noqa: E402
import frame as framemod                           # noqa: E402
import sections                                    # noqa: E402
import codecheck                                   # noqa: E402
import loads as L                                  # noqa: E402
import surfaces as surf                            # noqa: E402
import geometry as G                               # noqa: E402

IN2_PER_FT2 = 144.0

# Gravity strength combinations, ASCE 7-16 2.3.1. No Lr: there is no roof in this
# scheme yet. No W or E: there is no enclosure to load.
STRENGTH = {
    '1.4D':          {'D': 1.4},
    '1.2D + 1.6L':   {'D': 1.2, 'L': 1.6},
}
SERVICE = {
    'D + L':         {'D': 1.0, 'L': 1.0},
    'L only':        {'L': 1.0},
}
FLOOR_LIVE_DEFL = 360.0      # L/360 on live, IBC Table 1604.3
FLOOR_TOTAL_DEFL = 240.0     # L/240 on dead plus live


def deck_surfaces(frame):
    """One floor Surface per deck rectangle, in the single beam plane."""
    out = {}
    for name, x1, x2, y1, y2, rims in G.DECKS:
        out[name] = surf.Surface(
            name, 'floor', (x1, y1, G.BEAM_AXIS_Z),
            u=(1.0, 0.0, 0.0), v=(0.0, 1.0, 0.0), normal=(0.0, 0.0, 1.0),
            outline=Polygon([(0, 0), (x2 - x1, 0), (x2 - x1, y2 - y1), (0, y2 - y1)]),
            tolerance=1.0, label=name)
    return out


def apply_loads(frame, model, index, tribs, live_psf=None, override=None):
    """Dead and live onto the members lying in each deck. Returns the tallies."""
    live_psf = G.DESIGN_LIVE_PSF if live_psf is None else live_psf
    override = override or {}
    tally = {'D': dict(fy=0.0, detail={}), 'L': dict(fy=0.0, detail={})}

    model.add_member_self_weight('FY', -1.0, case='D')
    sw = sum((override.get(n.rsplit('#', 1)[0]) or frame.section_of[n.rsplit('#', 1)[0]]).A
             * framemod.MATERIALS[frame.material(n.rsplit('#', 1)[0])]['rho'] * el.L()
             for n, el in model.members.items())
    tally['D']['fy'] -= sw
    tally['D']['detail']['self_weight_lb'] = round(sw, 1)

    for case, psf in (('D', L.DEAD['loft_floor']), ('L', live_psf)):
        for name, t in tribs.items():
            area = 0.0
            for st in t.strips:
                area += st.area_in2
                Lel = model.members[st.element].L()
                w = psf / IN2_PER_FT2 * st.area_in2 / Lel
                model.add_member_dist_load(st.element, 'FY', -w, -w, case=case)
                tally[case]['fy'] -= w * Lel
            tally[case]['detail'][f'{name}_ft2'] = round(area / IN2_PER_FT2, 1)
    return tally


def unbraced(frame):
    """Compression-flange bracing: joists at <=16 in o.c. hold every beam top.

    A beam carrying a nailed deck through joists at 16 in centres is braced at
    those centres, so Lb is the joist spacing, not the span. Columns take their
    full height, and joists take their own span.
    """
    out = {}
    # Roof beams and clerestory chords are braced the same way the floor beams
    # are -- at every joint along them. Leaving them out gave R-W4 its full
    # 245.5 in as an unbraced length even though N-M holds it at midspan.
    SEGMENT_BRACED = {'Beams', 'Roof', 'Clerestory'}
    for m in frame.members:
        g = frame.group(m)
        if g in SEGMENT_BRACED:
            gaps = [frame.segment_length(i, j) for mm, i, j in frame.segments if mm == m]
            out[m] = max(gaps) if gaps else frame.member_length(m)
        else:
            out[m] = frame.member_length(m)
    return out


def member_forces(model, elements, combo):
    """Worst axial, both moments and shear over one member's elements."""
    P = Mz = My = V = 0.0
    for el in elements:
        m = model.members[el]
        P = max(P, abs(m.max_axial(combo)), abs(m.min_axial(combo)), key=abs)
        Mz = max(Mz, abs(m.max_moment('Mz', combo)), abs(m.min_moment('Mz', combo)))
        My = max(My, abs(m.max_moment('My', combo)), abs(m.min_moment('My', combo)))
        V = max(V, abs(m.max_shear('Fy', combo)), abs(m.min_shear('Fy', combo)))
    return P, Mz, My, V


def span_deflection(frame, model, member, elements, combo):
    """Sag at the worst point, measured against the chord between the member's own ends.

    Two parts have to be added. Nodal displacement gives the sag at each interior
    joint, which is all a beam split by joist landings needs. But a joist is a single
    element with no interior joint, so its nodal sag is zero by construction; the
    curvature lives inside the element and comes from PyNite's chord-relative
    deflection. Adding both makes the two cases comparable.
    """
    node_names = set()
    for el in elements:
        m = model.members[el]
        node_names |= {m.i_node.name, m.j_node.name}
    counts = {n: 0 for n in node_names}
    for el in elements:
        m = model.members[el]
        counts[m.i_node.name] += 1
        counts[m.j_node.name] += 1
    ends = [n for n, c in counts.items() if c == 1]
    if len(ends) != 2:
        return None
    a, b = sorted(ends, key=lambda n: frame.xyz(n))
    span = frame.segment_length(a, b)
    if span < 24.0:
        return None

    def dy(n):
        return model.nodes[n].DY[combo]

    def along(n):
        return frame.segment_length(a, n)

    worst = 0.0
    for el in elements:
        m = model.members[el]
        si, sj = along(m.i_node.name), along(m.j_node.name)
        di, dj = dy(m.i_node.name), dy(m.j_node.name)
        rel = m.rel_deflection_array('dy', 9, combo)
        for k in range(rel.shape[1]):
            t = rel[0, k] / m.L() if m.L() else 0.0
            s = si + t * (sj - si)
            chord = dy(a) + (s / span) * (dy(b) - dy(a))
            actual = di + t * (dj - di) + rel[1, k]
            sag = chord - actual
            if abs(sag) > abs(worst):
                worst = sag
    ratio = span / abs(worst) if abs(worst) > 1e-6 else 99999.0
    return dict(span_in=span, defl_in=abs(worst), ratio=min(ratio, 99999.0))


def main():
    path = frame_models.latest('beam-scheme')
    frame = framemod.load(path)
    model, index = framemod.build(frame)

    surfs = deck_surfaces(frame)
    tribs = {n: surf.tributary(frame, s, index) for n, s in surfs.items()}
    tally = apply_loads(frame, model, index, tribs)

    for name, factors in list(STRENGTH.items()) + list(SERVICE.items()):
        model.add_load_combo(name, dict(factors))
    model.analyze_linear(check_stability=True, check_statics=False, sparse=True)

    Lb = unbraced(frame)
    fy = {m: framemod.MATERIALS[frame.material(m)]['fy'] for m in frame.members}

    rows, worst = [], {}
    for m in sorted(frame.members):
        sec = frame.section_of[m]
        els = index[m]
        best = None
        for combo in STRENGTH:
            P, Mz, My, V = member_forces(model, els, combo)
            if frame.material(m) == 'wood':
                continue
            c = codecheck.check_steel(m, sec, fy[m], P, Mz, My, V, Lb[m], combo)
            if best is None or c.dcr > best.dcr:
                best = c
        if frame.material(m) == 'wood':
            # NDS is allowable stress: service loads, not factored.
            P, Mz, My, V = member_forces(model, els, 'D + L')
            d = span_deflection(frame, model, m, els, 'L only')
            best = codecheck.check_wood(m, sec, P, Mz, My, V, Lb[m], 'D + L',
                                        d['span_in'] if d else 0.0,
                                        d['defl_in'] if d else 0.0)
        defl = {c: span_deflection(frame, model, m, els, c) for c in SERVICE}
        rows.append(dict(
            member=m, group=frame.group(m), section=sec.name,
            length_in=round(frame.member_length(m), 1),
            weight_lb=round(frame.member_weight(m), 1),
            Lb_in=round(Lb[m], 1), dcr=round(best.dcr, 3), mode=best.mode,
            combo=best.combo, P_lb=round(best.P, 1), Mz_lbin=round(best.Mz, 1),
            V_lb=round(best.V, 1),
            phiMn_lbin=round(best.phiMn_z, 1),
            span_in=round(defl['D + L']['span_in'], 1) if defl['D + L'] else '',
            defl_total_in=round(defl['D + L']['defl_in'], 4) if defl['D + L'] else '',
            ratio_total=round(defl['D + L']['ratio']) if defl['D + L'] else '',
            defl_live_in=round(defl['L only']['defl_in'], 4) if defl['L only'] else '',
            ratio_live=round(defl['L only']['ratio']) if defl['L only'] else '',
            flags='; '.join(best.flags)))
        g = frame.group(m)
        if g not in worst or best.dcr > worst[g]['dcr']:
            worst[g] = rows[-1]
    return path, frame, model, tribs, tally, rows, worst, index


def report():
    path, frame, model, tribs, tally, rows, worst, index = main()

    # --- equilibrium: applied load must equal the sum of the reactions --------
    eq = {}
    for combo, factors in STRENGTH.items():
        applied = sum(tally[c]['fy'] * f for c, f in factors.items())
        react = sum(model.nodes[n].RxnFY[combo] for n in frame.supports)
        eq[combo] = dict(applied_lb=round(applied, 1), reactions_lb=round(react, 1),
                         closure=round(abs(react + applied) / abs(applied), 6)
                         if applied else 0.0)

    closure = {n: round(t.closure, 4) for n, t in tribs.items()}
    area = sum(t.surface_in2 for t in tribs.values()) / IN2_PER_FT2

    by_group = {}
    for r in rows:
        g = r['group']
        by_group.setdefault(g, []).append(r)

    defl_fail = [r for r in rows
                 if r['ratio_live'] != '' and
                 (r['ratio_live'] < FLOOR_LIVE_DEFL or r['ratio_total'] < FLOOR_TOTAL_DEFL)]
    over = [r for r in rows if r['dcr'] > 1.0]

    out = dict(
        model=path.name,
        basis=dict(
            live_psf=G.DESIGN_LIVE_PSF,
            live_basis='owner direction; ASCE 7-16 Table 4.3-1 "light storage" is 125 psf',
            dead_floor_psf=L.DEAD['loft_floor'],
            dead_basis=('3/4 in plywood 2.3 + underlayment/finish 1.7 + services and '
                        'misc 4.0; joists and steel are modelled explicitly'),
            deck_area_sf=round(area, 1),
            self_weight_lb=tally['D']['detail']['self_weight_lb'],
            beam_section=G.BEAM_SECTION, column_section=G.COLUMN_SECTION,
            joist_section=G.JOIST_SECTION,
            strength_combos=STRENGTH, service_combos=SERVICE,
            deflection_limits=dict(floor_live=f'L/{FLOOR_LIVE_DEFL:g}',
                                   floor_total=f'L/{FLOOR_TOTAL_DEFL:g}'),
            steel='AISC 360-16 LRFD, Fy = 50 ksi', wood='NDS ASD, DF-L No.2',
            lateral='NOT ANALYSED — this scheme has no roof, cladding or lateral '
                    'system yet, so there is no enclosure to load with wind or seismic'),
        loads={c: dict(total_fy_lb=round(v['fy'], 1), **v['detail'])
               for c, v in tally.items()},
        equilibrium=eq,
        tributary_closure=closure,
        worst_by_group={g: dict(member=r['member'], section=r['section'],
                                dcr=r['dcr'], mode=r['mode'], combo=r['combo'])
                        for g, r in worst.items()},
        beams=sorted([dict(member=r['member'], dcr=r['dcr'], mode=r['mode'],
                           combo=r['combo'], span_in=r['span_in'],
                           ratio_live=r['ratio_live'], ratio_total=r['ratio_total'],
                           Lb_in=r['Lb_in'], flags=r['flags'])
                      for r in by_group['Beams']], key=lambda r: -r['dcr']),
        over_capacity=[dict(member=r['member'], group=r['group'], dcr=r['dcr'],
                            mode=r['mode'], combo=r['combo']) for r in over],
        deflection_over_limit=[dict(member=r['member'], group=r['group'],
                                    span_in=r['span_in'],
                                    ratio_live=r['ratio_live'],
                                    ratio_total=r['ratio_total']) for r in defl_fail],
        verdict=('W14X22 is adequate for gravity at this load'
                 if not over and not defl_fail else 'see over_capacity / deflection'),
        limits=('Gravity only. Linear elastic. Pinned bases, no foundation designed. '
                'No connection is designed or checked. Lateral load is absent from '
                'this model entirely. Requires review and sealing by the responsible '
                'California-licensed engineer.'),
    )
    (HERE / 'analysis-results.json').write_text(json.dumps(out, indent=2))
    with (HERE / 'member-schedule.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: -r['dcr']))

    print(f'{path.name}\n')
    print(f'deck {area:,.0f} sf · live {G.DESIGN_LIVE_PSF:g} psf · '
          f'dead {L.DEAD["loft_floor"]:g} psf + {tally["D"]["detail"]["self_weight_lb"]:,.0f} lb self')
    for c, v in tally.items():
        print(f'  applied {c:<2} {abs(v["fy"]):>10,.0f} lb')
    print()
    for combo, v in eq.items():
        print(f'  equilibrium {combo:<14} applied {abs(v["applied_lb"]):>9,.0f} lb   '
              f'reactions {v["reactions_lb"]:>9,.0f} lb   closure {v["closure"]:.2e}')
    print(f'  tributary closure {min(closure.values()):.4f} to {max(closure.values()):.4f}')
    print(f'\n{"member":<22}{"section":<12}{"Lb":>6}{"DCR":>7}  {"mode":<34}'
          f'{"span":>7}{"L/live":>8}{"L/tot":>7}')
    for r in sorted(by_group['Beams'], key=lambda r: -r['dcr']):
        print(f'{r["member"]:<22}{r["section"]:<12}{r["Lb_in"]:>6.1f}{r["dcr"]:>7.3f}  '
              f'{r["mode"]:<34}{r["span_in"] or "-":>7}'
              f'{r["ratio_live"] or "-":>8}{r["ratio_total"] or "-":>7}')
    print(f'\n{"group":<12}{"worst member":<24}{"DCR":>7}  mode')
    for g, r in sorted(worst.items(), key=lambda t: -t[1]['dcr']):
        print(f'{g:<12}{r["member"]:<24}{r["dcr"]:>7.3f}  {r["mode"]}')
    print(f'\nover capacity: {len(over)}   over deflection limit: {len(defl_fail)}')
    for r in over + defl_fail:
        print(f'   {r["member"]:<24} DCR {r["dcr"] if "dcr" in r else "-"} '
              f'L/live {r.get("ratio_live", "-")}')
    return out


if __name__ == '__main__':
    report()
