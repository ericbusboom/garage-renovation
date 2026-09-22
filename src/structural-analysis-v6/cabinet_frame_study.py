#!/usr/bin/env python
"""Can the east-wall cabinet frames be built into the building under ``BE``?

    python cabinet_frame_study.py [--cache recommended.pkl] [--full]

The cabinet steel is described in ``cabinet-study/cabinet_frames.py``: four
welded 1 x 2 tube side frames, 30 in. deep and 98.5 in. high, at y = 56, 105,
154 and 203, their front legs directly below the inner east beam ``BE``. This
study adds that steel to the STR-008 recommended frame -- the same pipeline
``column_study.recommended`` builds -- joins each front leg to ``BE`` at its
station, and re-analyses. Four questions:

1. **As they stand.** Legs continued to the beam axis, pinned on the slab. What
   load do they attract, and can 11 ga 1 x 2 tube carry it?
2. **Strengthened.** Front legs doubled to a 1 x 4 built-up (the 1 in. face at
   the door line is kept), N-bracing hidden in each side panel, X-bracing in
   the rear plane against the wall. Does that make them adequate columns?
3. **What it buys.** With four more supports under ``BE``, can ``S3`` or ``S2``
   come out? The column study found neither removable on its own.
4. **What goes under them.** Footing reactions at every leg, so a foundation
   can be sized -- the slab was flagged weak at the start of the project.

No strengthening search is run on a failing variant (owner direction: keep
runs short). Writes ``results/cabinet-frame-study.json`` and ``.md``, and the
3-D view ``cabinet-study/cabinet-frames-3d.html``.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import pickle
import sys
import time
from pathlib import Path

import plotly.graph_objects as go

import analysis as A
import column_study as CS
import completion
import frame as F
import sections as S
import studies as St
import visualize
from project_paths import VIZ_DIR, STUDIES_DIR

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CABINET_STUDY = STUDIES_DIR / '20260919.01-cabinet-frame'
sys.path.insert(0, str(CABINET_STUDY))
import cabinet_frames as CAB   # noqa: E402

OUT_JSON = VIZ_DIR / 'cabinet-frame-study.json'
OUT_MD = VIZ_DIR / 'cabinet-frame-study.md'
OUT_3D = CABINET_STUDY / 'cabinet-frames-3d.html'
LIVE = 'L100'
WATCH = ['BE', 'BE.upper', 'B-S', 'B-1', 'B-1A', 'B-2', 'C-EN', 'S2', 'S3', 'N2']
EAST_SUPPORTS = ['S2.base', 'S3.base', 'N2.base']

#: Presumptive allowable bearing, IBC 1806.2 class 4 (sandy clay / silty sand),
#: the default when nothing is known about the soil. ASD, on service load.
BEARING_PSF = 1500.0
#: Strength-level reactions divided by this approximate service load. The
#: gravity combinations are 1.2D + 1.6L; with the loft live load dominating
#: the east line this is close to 1.5, so 1.4 is slightly unconservative and
#: is stated as such.
LRFD_TO_ASD = 1.4


# ---------------------------------------------------------------------------
# sections
# ---------------------------------------------------------------------------

def section_for(tube: CAB.Tube) -> S.Section:
    """A ``Section`` for a tube or a side-by-side welded pair.

    ``sections.hss_rect`` takes the strong direction first (``Iz`` is the
    strong-axis inertia only when ``b >= d``), so the tube's 2 in. side goes in
    as ``b`` and its 1 in. face as ``d``.
    """
    deep = tube.d / tube.count
    single = S.hss_rect(deep, tube.b, tube.t, tube.name if tube.count == 1 else None)
    if tube.count == 1:
        return single
    # Two tubes welded along their 2 in. faces, side by side in the deep
    # direction. Weak axis (bending across the 1 in. face) is unchanged in
    # shape: I and Z double, r is the same. Strong axis: parallel-axis shift of
    # half a tube; the plastic modulus is each tube's area at its centroid.
    e = deep / 2.0
    A1 = single.A
    A = tube.count * A1
    Iz = tube.count * (single.Iz + A1 * e * e)
    Zz = tube.count * A1 * e
    Iy = tube.count * single.Iy
    return S.Section(tube.name, 'HSS', tube.d, tube.b, single.t, A,
                     Iy, Iz, tube.count * single.J,
                     tube.count * single.Zy, Zz,
                     Iy / (tube.b / 2.0), Iz / (tube.d / 2.0),
                     math.sqrt(Iy / A), math.sqrt(Iz / A),
                     tube.count * single.weight, single.compact,
                     note=tube.note)


# ---------------------------------------------------------------------------
# adding the cabinet steel to the frame
# ---------------------------------------------------------------------------

def add_cabinets(base: F.Frame, scheme: str) -> tuple[F.Frame, list[str]]:
    """Return a copy of ``base`` with the cabinet members of ``scheme`` in it."""
    g = copy.deepcopy(base)
    added: list[str] = []
    bases = {tuple(round(c, 3) for c in p): n for n, p in CAB.supports().items()}

    def index() -> dict[tuple, str]:
        return {(round(v['x'], 3), round(v['y'], 3), round(v['z'], 3)): n
                for n, v in g.nodes.items()}

    def node_for(p: tuple, label: str) -> str:
        key = tuple(round(c, 3) for c in p)
        idx = index()
        if key in idx:
            return idx[key]
        if key in bases:
            g.nodes[bases[key]] = dict(x=p[0], y=p[1], z=p[2], support=True,
                                       free_end=False, members=[])
            return bases[key]
        if abs(p[0] - CAB.FRONT_X) < 1e-6 and abs(p[2] - CAB.BEAM_AXIS_Z) < 1e-6:
            return completion._split(g, 'BE', p, label)
        # on a cabinet member already placed? split it there
        for m in added:
            for (mm, i, j) in g.segments:
                if mm == m and completion._between(g.xyz(i), g.xyz(j), p, tol=0.01):
                    return completion._split(g, m, p, label)
        g.nodes[label] = dict(x=p[0], y=p[1], z=p[2], support=False,
                              free_end=False, members=[])
        return label

    for m in CAB.members(scheme):
        if not m.fe:
            continue
        a = node_for(m.a, f'{m.name}.a')
        b = node_for(m.b, f'{m.name}.b')
        completion._add_member(g, m.name, a, b, m.tube.name, m.tube.b, m.tube.d,
                               m.group, 'steel', note=m.note)
        g.section_of[m.name] = section_for(m.tube)
        g.members[m.name]['cabinet'] = m.kind
        g.members[m.name]['frame'] = m.frame
        added.append(m.name)
    _join_crossings(g, added)
    return g, added


def _join_crossings(g: F.Frame, added: list[str]) -> None:
    """Give each rear-plane X one shared node at its centre.

    Both diagonals stay continuous through the joint, so the node has
    rotational stiffness and the pin-ended releases apply only at the corners.
    """
    for x1 in [m for m in added if m.endswith('.rear.X1')]:
        x2 = x1[:-1] + '2'
        if x2 not in g.members:
            continue
        a, b = (g.xyz(n) for n in g.members[x1]['nodes'])
        c = tuple((a[k] + b[k]) / 2.0 for k in range(3))
        n = completion._split(g, x1, c, x1[:-1])
        for k, (mm, i, j) in enumerate(g.segments):
            if mm == x2 and completion._between(g.xyz(i), g.xyz(j), c, tol=0.01):
                g.segments[k] = (x2, i, n)
                g.segments.insert(k + 1, (x2, n, j))
                g.nodes[n]['members'].append(x2)
                break


# ---------------------------------------------------------------------------
# reading a run
# ---------------------------------------------------------------------------

def _mem(r: A.Result, name: str) -> dict | None:
    m = r.members.get(name)
    if m is None:
        return None
    return dict(section=m.section, dcr=round(m.dcr, 3), mode=m.mode, combo=m.combo,
                P_lb=round(m.P), Mz_lbin=round(m.Mz), V_lb=round(m.V),
                Lb_in=round(m.Lb, 1), KLr=round(m.slenderness))


def digest(g: F.Frame, r: A.Result, cabinet: list[str]) -> dict:
    over = [dict(member=m.member, section=m.section, dcr=round(m.dcr, 3),
                 mode=m.mode, combo=m.combo) for m in r.overstressed()]
    cab = {m: _mem(r, m) for m in cabinet if m in r.members}
    legs = {m: v for m, v in cab.items() if m.endswith('.front') or m.endswith('.rear')}
    worst_leg = max(legs.items(), key=lambda t: t[1]['dcr']) if legs else (None, None)
    # ``max_vertical`` is the largest upward reaction over the strength
    # combinations -- the footing load. (``max_compression`` in ``_reactions``
    # is the negated minimum, which is not that.)
    reactions = {n: round(v['max_vertical']) for n, v in r.reactions.items()
                 if n.startswith('CF') or n in EAST_SUPPORTS}
    uplift = {n: round(v['max_uplift']) for n, v in r.reactions.items()
              if (n.startswith('CF') or n in EAST_SUPPORTS) and v['max_uplift'] > 0}
    defl = {}
    for k, v in (r.deflection or {}).items():
        if k in WATCH:
            defl[k] = v
    return dict(stable=r.stable, message=r.message,
                max_dcr=round(r.max_dcr, 3),
                worst=max(r.members.values(), key=lambda m: m.dcr).member if r.members else None,
                drift=CS.drift_of(r),
                passes=St._passes(g, r),
                over=over,
                deflection_violations=A.deflection_violations(g, r),
                watch={m: _mem(r, m) for m in WATCH if m in r.members},
                cabinet=cab,
                worst_leg=dict(member=worst_leg[0], **worst_leg[1]) if worst_leg[0] else None,
                reactions=reactions, uplift=uplift,
                deflection=defl,
                steel_lb=round(sum(g.member_weight(m) for m in cabinet), 1))


def footings(reactions: dict) -> dict:
    """Size a pad under each frame and a strip under the run, at 1.5 ksf."""
    out = dict(bearing_psf=BEARING_PSF, lrfd_to_asd=LRFD_TO_ASD, frames={}, strip={})
    total = 0.0
    for name in CAB.FRAME_NAMES:
        front = reactions.get(f'{name}.front.base', 0.0)
        rear = reactions.get(f'{name}.rear.base', 0.0)
        svc = (front + rear) / LRFD_TO_ASD
        total += svc
        area_sf = svc / BEARING_PSF
        # a pad the depth of the frame (30 in.) and as wide along the wall as needed
        width_in = max(12.0, area_sf * 144.0 / CAB.DEPTH)
        out['frames'][name] = dict(front_lrfd_lb=round(front), rear_lrfd_lb=round(rear),
                                   service_lb=round(svc), pad_sf=round(area_sf, 2),
                                   pad_in=[round(CAB.DEPTH), round(width_in)])
    run_ft = (CAB.RUN_NORTH - CAB.RUN_SOUTH + 2 * 12.0) / 12.0   # a foot past each end
    width_in = max(12.0, total / BEARING_PSF / run_ft * 12.0)
    out['strip'] = dict(service_lb=round(total), length_ft=round(run_ft, 1),
                        width_in=round(width_in), note='continuous under the frame line, '
                        'one foot past each end frame')
    return out


# ---------------------------------------------------------------------------
# the 3-D view
# ---------------------------------------------------------------------------

def view(g: F.Frame, r: A.Result, cabinet: list[str], path: Path, title: str) -> None:
    traces = []

    def lines(names, color, width, label, hover):
        xs, ys, zs, txt = [], [], [], []
        for m in names:
            pts = visualize.member_polyline(g, m)
            if not pts:
                continue
            for p in pts:
                xs.append(p[0]); ys.append(p[1]); zs.append(p[2]); txt.append(hover(m))
            xs.append(None); ys.append(None); zs.append(None); txt.append('')
        traces.append(go.Scatter3d(x=xs, y=ys, z=zs, mode='lines', name=label,
                                   line=dict(color=color, width=width),
                                   text=txt, hoverinfo='text'))

    def hov(m):
        mm = r.members.get(m)
        sec = g.section_of[m].name
        if mm is None:
            return f'{m}<br>{sec}'
        return f'{m}<br>{sec}<br>DCR {mm.dcr:.2f} ({mm.mode})<br>P {mm.P:,.0f} lb'

    building = [m for m in g.members if m not in cabinet and m != 'BE']
    lines(building, '#b8bec6', 2, 'recommended frame', hov)
    lines(['BE'], '#c0392b', 7, 'BE (W12X16)', hov)
    existing = [m for m in cabinet if g.members[m].get('cabinet') == 'existing']
    replaced = [m for m in cabinet if g.members[m].get('cabinet') == 'replaced']
    added = [m for m in cabinet if g.members[m].get('cabinet') == 'added']
    lines(existing, '#2c6fac', 4, 'cabinet steel, existing', hov)
    if replaced:
        lines(replaced, '#e67e22', 7, 'front legs doubled (1 x 4)', hov)
    if added:
        lines(added, '#f1c40f', 4, 'bracing added', hov)

    # supports
    sx, sy, sz, st = [], [], [], []
    for n in g.supports:
        p = g.xyz(n)
        rr = r.reactions.get(n, {}).get('max_vertical', 0.0)
        sx.append(p[0]); sy.append(p[1]); sz.append(p[2])
        st.append(f'{n}<br>{rr:,.0f} lb (LRFD)')
    traces.append(go.Scatter3d(x=sx, y=sy, z=sz, mode='markers', name='footings',
                               marker=dict(size=4, color='#333'), text=st, hoverinfo='text'))

    # existing east wall and the proposed strip footing, as translucent boxes
    def box(x0, x1, y0, y1, z0, z1, color, name, opacity):
        X = [x0, x1, x1, x0, x0, x1, x1, x0]
        Y = [y0, y0, y1, y1, y0, y0, y1, y1]
        Z = [z0, z0, z0, z0, z1, z1, z1, z1]
        I = [0, 0, 4, 4, 0, 0, 1, 1, 2, 2, 3, 3]
        J = [1, 2, 5, 6, 1, 4, 2, 5, 3, 6, 0, 7]
        K = [2, 3, 6, 7, 5, 5, 6, 6, 7, 7, 4, 4]
        traces.append(go.Mesh3d(x=X, y=Y, z=Z, i=I, j=J, k=K, color=color,
                                opacity=opacity, name=name, showlegend=True, hoverinfo='name'))
    box(*CAB.EXISTING_EAST_WALL, 0.0, 249.0, 0.0, 98.5, '#d9d2c5', 'existing east wall', 0.25)
    box(CAB.FRONT_X - 6.0, CAB.REAR_X + 6.0, CAB.RUN_SOUTH - 12.0, CAB.RUN_NORTH + 12.0,
        -12.0, 0.0, '#7f8c8d', 'strip footing (concept)', 0.35)

    fig = go.Figure(data=traces)
    fig.update_layout(title=title, scene=dict(aspectmode='data',
                      xaxis_title='x east (in)', yaxis_title='y north (in)', zaxis_title='z (in)',
                      camera=dict(eye=dict(x=-1.6, y=-1.2, z=0.7))),
                      legend=dict(x=0.01, y=0.99), margin=dict(l=0, r=0, t=40, b=0))
    fig.write_html(str(path), include_plotlyjs='cdn')


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def _h(v):
    return f'H/{v:.0f}' if v else '—'


def write_md(res: dict, path: Path) -> None:
    b = res['variants']
    L = []
    L.append('# Cabinet frames as columns under BE\n')
    L.append(f"**Frame:** {res['frame']}, loft live load {LIVE}. "
             f"**Cabinet geometry:** `cabinet-study/cabinet_frames.py` "
             f"(frames at y = {', '.join(f'{y:g}' for y in CAB.FRAME_Y)}, front legs on x = {CAB.FRONT_X:g}).\n")
    L.append('## 1. Variants\n')
    L.append('| variant | result | max DCR (member) | BE | worst leg | drift | over capacity |')
    L.append('|---|---|---|---|---|---|---|')
    for k, v in b.items():
        d = v['digest']
        be = d['watch'].get('BE')
        leg = d['worst_leg']
        be_s = f"{be['dcr']:.3f}" if be else '—'
        leg_s = (f"{leg['member']} {leg['dcr']:.2f} ({leg['mode']}, Lb {leg['Lb_in']:g} in)"
                 if leg else '—')
        L.append(f"| {v['label']} | {'**PASS**' if d['passes'] else 'FAIL'} | "
                 f"{d['max_dcr']:.3f} ({d['worst']}) | {be_s} | {leg_s} | "
                 f"{_h(d['drift'])} | {len(d['over'])} |")
    L.append('')
    L.append('## 2. What BE and its columns do\n')
    L.append('| member | ' + ' | '.join(v['label'] for v in b.values()) + ' |')
    L.append('|---|' + '---|' * len(b))
    for m in WATCH:
        row = []
        for v in b.values():
            w = v['digest']['watch'].get(m)
            row.append(f"{w['dcr']:.3f}" if w else '—')
        L.append(f'| {m} | ' + ' | '.join(row) + ' |')
    L.append('')
    L.append('## 3. Footing reactions (LRFD, lb, largest downward load over the strength combinations)\n')
    sup = sorted({n for v in b.values() for n in v['digest']['reactions']})
    L.append('| support | ' + ' | '.join(v['label'] for v in b.values()) + ' |')
    L.append('|---|' + '---|' * len(b))
    for n in sup:
        L.append(f'| {n} | ' + ' | '.join(f"{v['digest']['reactions'].get(n, 0):,}"
                                          if n in v['digest']['reactions'] else '—'
                                          for v in b.values()) + ' |')
    L.append('')
    ft = res['footings']
    L.append(f"## 4. Foundations at {ft['bearing_psf']:.0f} psf allowable "
             f"(service = LRFD / {ft['lrfd_to_asd']})\n")
    L.append(f"Sized on the **{res['footing_basis']}** variant.\n")
    L.append('| frame | front (LRFD) | rear (LRFD) | service | pad, 30 in. deep x along wall |')
    L.append('|---|---:|---:|---:|---|')
    for n, f in ft['frames'].items():
        L.append(f"| {n} | {f['front_lrfd_lb']:,} | {f['rear_lrfd_lb']:,} | {f['service_lb']:,} | "
                 f"{f['pad_in'][0]} x {f['pad_in'][1]} in |")
    s = ft['strip']
    L.append(f"\nStrip alternative: {s['service_lb']:,} lb service over {s['length_ft']} ft "
             f"needs a strip **{s['width_in']} in. wide** ({s['note']}).\n")
    L.append('## 5. Notes\n')
    for n in res['notes']:
        L.append(f'- {n}')
    L.append('')
    path.write_text('\n'.join(L))


# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', default=None, help='pickle of (frame, params, combos) from column_study.recommended')
    ap.add_argument('--full', action='store_true', help='also verify the strengthened variant on all 27 combinations')
    args = ap.parse_args()
    t0 = time.time()

    if args.cache and Path(args.cache).exists():
        built, params, combos = pickle.load(open(args.cache, 'rb'))
        print(f'recommended frame from {args.cache}')
    else:
        built, params, _, combos = CS.recommended()

    variants: dict[str, dict] = {}

    def run(key, label, g, cabinet, full=False):
        t = time.time()
        r = A.run(g, params, LIVE, combos=None if full else combos)
        d = digest(g, r, cabinet)
        variants[key] = dict(label=label, digest=d, seconds=round(time.time() - t, 1))
        be = d['watch'].get('BE')
        leg = d['worst_leg']
        print(f"{label:<34} {'PASS' if d['passes'] else 'FAIL'}  max {d['max_dcr']:.3f} ({d['worst']})  "
              f"BE {be['dcr'] if be else float('nan'):.3f}  "
              f"leg {leg['member'] + ' ' + format(leg['dcr'], '.2f') if leg else '—'}  "
              f"drift {_h(d['drift'])}  over {len(d['over'])}  [{time.time() - t:.0f} s]")
        return g, r

    base_g, base_r = run('baseline', 'recommended frame, no cabinets', copy.deepcopy(built), [])

    g1, added1 = add_cabinets(built, 'as-is')
    run('as-is', 'cabinet frames as they stand', g1, added1)

    g2, added2 = add_cabinets(built, 'strengthened')
    g2, r2 = run('strengthened', 'strengthened frames', g2, added2)
    if args.full:
        run('strengthened-full', 'strengthened, all 27 combinations', copy.deepcopy(g2), added2, full=True)

    for col in ('S3', 'S2'):
        g = copy.deepcopy(g2)
        cut = CS.cut_ground_floor(g, col)
        gg, _ = run(f'strengthened-no-{col}', f'strengthened, {col} cut at the beam', g, added2)
        variants[f'strengthened-no-{col}']['cut'] = cut

    g = copy.deepcopy(g2)
    for col in ('S3', 'S2'):
        CS.cut_ground_floor(g, col)
    run('strengthened-no-S2-S3', 'strengthened, S2 and S3 both cut', g, added2)
    if args.full:
        run('strengthened-no-S2-S3-full', 'S2 and S3 cut, all 27 combinations', copy.deepcopy(g), added2, full=True)

    basis = 'strengthened'
    ft = footings(variants[basis]['digest']['reactions'])

    notes = [
        'Frame stations, tube gauge, rail levels and the 98.5 in. height are assumptions '
        'listed in cabinet_frames.py; none has been measured for this study.',
        'The front leg is joined rigidly to BE at its station and its top 6 in. stands in '
        'for the beam half-depth. A real seat would be a cap plate under the bottom flange.',
        'Unbraced lengths are taken between nodes where any member frames in, so a bolted '
        'rail along the wall counts as a brace point in both directions. That is right for the '
        'weak (1 in.) axis and optimistic for the front-to-back axis of an unbraced frame.',
        'Combinations are the pruned governing set from the baseline unless --full is given; '
        'cabinet members could in principle be governed by a combination not in that set.',
        f'Bearing is presumptive ({BEARING_PSF:.0f} psf). Nothing is known about the slab '
        'thickness or the soil; the pads assume the slab is cut out under each frame.',
        'No connection, base plate, anchor, weld or cap plate is designed here.',
    ]
    res = dict(frame=built.version, live=LIVE, schemes=CAB.SCHEMES,
               geometry={s: CAB.summary(s) for s in CAB.SCHEMES},
               sections={t.name: section_for(t).as_dict() for t in (CAB.LEG_AS_IS, CAB.LEG_DOUBLED, CAB.BRACE)},
               variants=variants, footing_basis=basis, footings=ft, notes=notes,
               seconds=round(time.time() - t0))
    OUT_JSON.write_text(json.dumps(res, indent=1, default=str))
    write_md(res, OUT_MD)
    view(g2, r2, added2, OUT_3D, 'Cabinet frames built in under BE — strengthened scheme')
    print(f'\nwrote {OUT_JSON.name}, {OUT_MD.name}, {OUT_3D}  [{time.time() - t0:.0f} s]')


if __name__ == '__main__':
    main()
