"""Run the whole loft span study and write its outputs.

    python run.py

Produces, in ``output/``:

    span-model.compas.json      the 2-D COMPAS graph of the span, serialised
    results.json                every number this study reports
    elevation.png / .svg        the section drawing
    answer.png / .svg           the sizing chart and the truss comparison

The serialised graph is a single line of framing in the x-z plane, so by the
rule in ``frame-models/README.md`` it stays here beside its viewer rather than
going into the canonical frame-model store.
"""
from __future__ import annotations

import json
from pathlib import Path

from compas.data import json_dump

import cost
import design
import draw
import span_model
import truss

OUT = Path(__file__).resolve().parent / 'output'
TRUSS_DEPTHS = (12.0, 18.0, 24.0, 30.0, 36.0)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    geom, spec = span_model.read_geometry()
    cases = design.build_cases(geom.loft_depth_ft)

    # -- size a beam for every reading of the load ---------------------------
    rows, checks = [], {}
    for case in cases:
        r = design.lightest(case, geom.span_in)
        if r is None:
            raise SystemExit(f'nothing in the W ladder carries {case.label()}')
        checks[case.name] = r
        who, dcr = r.governing
        rows.append(dict(
            case=f'{case.live_psf:.0f} psf live · '
                 f'{"even third" if "even" in case.name else "centre beam"}'
                 f'\n{case.trib_ft:.2f} ft tributary',
            name=case.name, live_psf=case.live_psf, trib_ft=case.trib_ft,
            section=r.section.name, d=r.section.d,
            nominal_depth=r.section.nominal_depth,
            weight_lb=r.section.wt * geom.span_ft,
            wt_plf=r.section.wt,
            wD_plf=case.wD_plf + r.section.wt, wL_plf=case.wL_plf,
            Mu_kipft=r.Mu_kipft, phiMn_kipft=r.section.phiMn_kipft,
            defl_live_in=r.defl_live_in, defl_total_in=r.defl_total_in,
            fn_hz=r.fn_hz, soffit_z=geom.soffit_z(r.section.d),
            fits_budget=r.section.d <= geom.depth_budget_in,
            governing=who, dcr=dcr,
        ))

    # -- what each nominal depth costs, for the two governing cases ----------
    by_depth = {}
    for name in ('L40-interior', 'L125-interior'):
        case = next(c for c in cases if c.name == name)
        by_depth[name] = {
            str(k): dict(section=v.section.name, d=v.section.d, wt_plf=v.section.wt,
                         weight_lb=v.section.wt * geom.span_ft,
                         dcr=v.dcr, governing=v.governing[0])
            for k, v in sorted(design.shallowest_by_depth(case, geom.span_in).items())
        }

    # -- truss alternatives over the same span -------------------------------
    truss_rows = []
    for name in ('L40-interior', 'L125-interior'):
        case = next(c for c in cases if c.name == name)
        for depth in TRUSS_DEPTHS:
            t = truss.best(geom.span_in, depth, case.wD_plf, case.wL_plf)
            if t is None:
                continue
            truss_rows.append(dict(
                case=name, depth=depth, span_over_depth=t.span_over_depth,
                n_panels=t.n_panels, chord=t.chord.name, web=t.web.name,
                weight_lb=t.weight_lb, n_joints=t.n_joints,
                dcr=t.max_dcr, governing=t.governing,
                defl_live_in=t.defl_live_in,
            ))

    # -- does the deck reach between three beams at all? ---------------------
    joists = [design.joist_check(geom.loft_depth_ft / (n - 1), psf)
              for n in (3, 4) for psf in (40.0, 125.0)]

    # -- rolled beams against fabricated trusses, on the project's own rates --
    costs = {}
    for name, depth in (('L40-interior', 18.0), ('L125-interior', 24.0)):
        case = next(c for c in cases if c.name == name)
        t = truss.best(geom.span_in, depth, case.wD_plf, case.wL_plf)
        costs[name] = dict(
            beam=checks[name].section.name, truss_depth=depth,
            truss_chord=t.chord.name, truss_web=t.web.name,
            **cost.compare(3, checks[name].section.wt * geom.span_ft,
                           t.weight_lb, t.n_joints))

    # -- the COMPAS model, drawn for the governing beam ----------------------
    governing = checks['L125-interior']
    graph = span_model.build_graph(geom, governing.section.d, governing.section.name)
    json_dump(graph, OUT / 'span-model.compas.json', pretty=True)

    truss_case = next(c for c in cases if c.name == 'L125-interior')
    t = truss.best(geom.span_in, 24.0, truss_case.wD_plf, truss_case.wL_plf)
    truss_graph = span_model.build_graph(geom, 24.0, t.chord.name,
                                         n_panels=t.n_panels, truss_depth=24.0)
    json_dump(truss_graph, OUT / 'span-model-truss.compas.json', pretty=True)

    # -- drawings -------------------------------------------------------------
    design_case = next(c for c in cases if c.name == 'L40-interior')
    png1 = draw.elevation(geom, span_model.build_graph(
        geom, checks['L40-interior'].section.d, checks['L40-interior'].section.name),
        checks['L40-interior'].section, design_case, checks['L40-interior'],
        OUT / 'elevation')
    png2 = draw.answer(geom, rows, truss_rows, OUT / 'answer')
    png3 = draw.tributary(geom, rows, OUT / 'tributary')

    payload = dict(
        study='loft span W1 -> E-S, three east-west beams',
        geometry=dict(
            west_x=geom.west_x, east_x=geom.east_x,
            span_in=geom.span_in, span_ft=geom.span_ft,
            built_span_in=geom.built_span_in,
            loft_depth_ft=geom.loft_depth_ft, loft_area_ft2=geom.loft_area_ft2,
            floor_z=geom.floor_z, existing_wall_top_z=geom.existing_wall_top_z,
            depth_budget_in=geom.depth_budget_in,
            west_overhang_in=geom.west_overhang_in,
        ),
        load_basis=dict(
            dead_psf=design.LoadCase('x', 0, '', 1.0, '').dead_psf,
            sdl_psf=design.L.DEAD['loft_floor'], joist_psf=design.JOIST_PSF,
            joist=design.JOIST,
            live_cases={k: v for k, v in design.L.LOFT_LIVE_CASES.items()},
            deflection_limits=dict(live='L/360', total='L/240',
                                   source='IBC Table 1604.3'),
            excluded=['roof and solar dead + live (carried by the trusses above)',
                      'the 1000 lb monorail hoist (hung from the roof frame)',
                      'wind and seismic (this is a gravity span study)'],
        ),
        beams=rows, by_nominal_depth=by_depth, trusses=truss_rows,
        joists=joists, cost=costs,
        source=dict(
            geometry='roof-studies/square-upper-west/connected-frame/frame-spec.json',
            existing='roof-studies/square-upper-west/connected-frame/scene-mesh.json',
            loads='structural-analysis-v6/loads.py',
            hss='structural-analysis-v6/sections.py',
            w_shapes='AISC Shapes Database v15.0, transcribed in wshapes.py',
        ),
        caveat='Preliminary sizing study. Not a structural verification. '
               'Connections, columns, foundations and lateral load are outside it. '
               'Requires review and sealing by the responsible California-licensed engineer.',
    )
    (OUT / 'results.json').write_text(json.dumps(payload, indent=2))

    # -- console summary -------------------------------------------------------
    print(f'span  {geom.span_in:.1f} in = {geom.span_ft:.2f} ft   '
          f'loft {geom.loft_area_ft2:.0f} sf   '
          f'depth budget {geom.depth_budget_in:.1f} in\n')
    print(f"{'case':<30}{'section':<10}{'d in':>6}{'lb':>7}{'soffit':>8}"
          f"{'DCR':>6}  governing")
    for r in rows:
        print(f"{r['name']:<30}{r['section']:<10}{r['d']:6.2f}{r['weight_lb']:7.0f}"
              f"{r['soffit_z']:8.1f}{r['dcr']:6.2f}  {r['governing']}")
    print(f"\n2x8 joists at 16 in. o.c., the bay three beams leave "
          f"({geom.loft_depth_ft / 2:.2f} ft):")
    for j in joists[:2]:
        print(f"  {j['live_psf']:>5.0f} psf   DCR {j['dcr']:.2f} on {j['governing']}"
              f"   {'OK' if j['ok'] else 'FAILS'}")

    print('\nrolled beams vs. fabricated trusses, three of each:')
    for name, c in costs.items():
        print(f"  {name:<16} {c['beam']:<8} ${c['beams']['low']:,.0f}-"
              f"${c['beams']['high']:,.0f}   |   {c['truss_depth']:.0f} in truss "
              f"${c['trusses']['low']:,.0f}-${c['trusses']['high']:,.0f} "
              f"({c['trusses']['joints']} joints)")

    print(f'\nwrote {png1.name}, {png2.name}, {png3.name}, results.json, '
          f'span-model.compas.json, span-model-truss.compas.json in {OUT}')


if __name__ == '__main__':
    main()
