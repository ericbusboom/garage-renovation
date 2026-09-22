"""Independent checks on the BEAM-001 COMPAS model.

Re-derives what the model should contain straight from ``geometry.py`` and compares,
rather than trusting the builder that wrote it. Geometry and load bookkeeping only —
nothing here checks a force or a capacity.

Run: /Volumes/Proj/proj/CAD/garage/.venv/bin/python verify.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from compas.data import json_load

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'compas-study'))
sys.path.insert(0, str(ROOT / 'structural-analysis-v6'))
import frame_models                                # noqa: E402
import frame as framemod                           # noqa: E402
import geometry as G                               # noqa: E402

TOL = 1e-6
checks: list[tuple[bool, str, str]] = []


def check(ok, name, detail=''):
    checks.append((bool(ok), name, detail))


def _on_axis(seg, pt, tol=1e-6):
    """Is pt on the segment seg, within tolerance?"""
    a, b = seg
    d = [b[i] - a[i] for i in range(3)]
    L2 = sum(v * v for v in d)
    if L2 < tol:
        return False
    t = sum((pt[i] - a[i]) * d[i] for i in range(3)) / L2
    if not -tol <= t <= 1 + tol:
        return False
    return max(abs(a[i] + t * d[i] - pt[i]) for i in range(3)) <= 1e-5


def main():
    path = frame_models.latest('beam-scheme')
    data = json_load(path)
    spec, graph = data['specification'], data['joint_graph']
    f = framemod.load(path)
    xyz = {n: graph.node_attributes(n, 'xyz') for n in graph.nodes()}
    ends = {m: [xyz[n] for n in r['nodes']] for m, r in spec['members'].items()}

    # ---- every beam is where the plan says, at the one beam plane ------------
    want = {n: ((x1, y, Z), (x2, y, Z)) for n, y, x1, x2, _, _ in G.CROSS_BEAMS
            for Z in (G.BEAM_AXIS_Z,)}
    want |= {n: ((x, y1, Z), (x, y2, Z)) for n, x, y1, y2, _, _ in G.LINE_BEAMS
             for Z in (G.BEAM_AXIS_Z,)}
    for name, (a, b) in want.items():
        got = ends.get(name)
        ok = got and (max(abs(got[0][i] - a[i]) for i in range(3)) < TOL
                      and max(abs(got[1][i] - b[i]) for i in range(3)) < TOL)
        check(ok, f'beam {name} endpoints', f'{a} -> {b}')
    check(all(f.section_of[m].name == G.BEAM_SECTION for m in f.members_in('Beams')),
          f'every beam is a {G.BEAM_SECTION}',
          f'{len(f.members_in("Beams"))} beams')
    zs = {round(p[2], 6) for m in f.members_in('Beams') for p in ends[m]}
    check(zs == {round(G.BEAM_AXIS_Z, 6)}, 'all beams share one plane',
          f'z = {sorted(zs)}')
    check(abs((G.BEAM_AXIS_Z - G.BEAM_D / 2) - G.WALL_TOP_Z) < TOL,
          'beam soffit sits on the existing wall top',
          f'{G.BEAM_AXIS_Z:g} - {G.BEAM_D:g}/2 = {G.BEAM_AXIS_Z - G.BEAM_D/2:g} '
          f'= wall top {G.WALL_TOP_Z:g}')

    # ---- columns -------------------------------------------------------------
    cols = f.members_in('Columns')
    check(len(cols) == len(G.COLUMNS), 'one column per plan column',
          f'{len(cols)} of {len(G.COLUMNS)}')
    check(all(abs(ends[m][0][2]) < TOL for m in cols), 'every column base at z = 0')
    check(all(abs(ends[m][1][2] - G.POST_TOPS.get(m, G.BEAM_AXIS_Z)) < 1e-6
              for m in cols),
          'every column top at the beam plane or its declared envelope height',
          f'{sum(1 for m in cols if m in G.POST_TOPS)} posts extended past the beams')
    check(all(f.section_of[m].b == G.COLUMN_SIZE for m in cols),
          'every column is 4 in', f'{sorted({f.section_of[m].name for m in cols})}')
    check(len(f.supports) == len(G.COLUMNS), 'one pinned base per column',
          f'{len(f.supports)} supports')
    for cid, x, y, size, kind in G.COLUMNS:
        got = ends.get(cid)
        ok = got and abs(got[0][0] - x) < TOL and abs(got[0][1] - y) < TOL
        check(ok, f'column {cid} at ({x:g}, {y:g})')

    # ---- a framing member on every deck edge --------------------------------
    joist_x = {}
    for m in f.members_in('Joists'):
        a, b = ends[m]
        joist_x.setdefault(round(a[1], 4), set()).add(round(a[0], 4))
    beam_x = {round(ends[m][0][0], 4) for m in f.members_in('Beams')
              if abs(ends[m][0][0] - ends[m][1][0]) < TOL}
    for name, x1, x2, y1, y2, rims in G.DECKS:
        here = joist_x.get(round(y1, 4), set())
        for edge, x in (('west', x1), ('east', x2)):
            framed = round(x, 4) in here or round(x, 4) in beam_x
            check(framed, f'{name}: {edge} edge has a framing member',
                  f'x = {x:g}')
        spans = sorted(here | {round(x, 4) for x in (x1, x2) if round(x, 4) in beam_x})
        spans = [s for s in spans if x1 - TOL <= s <= x2 + TOL]
        gaps = [b - a for a, b in zip(spans, spans[1:])]
        check(gaps and max(gaps) <= G.JOIST_SPACING_MAX + 1e-6,
              f'{name}: joist spacing within {G.JOIST_SPACING_MAX:g} in',
              f'max {max(gaps):.2f} in over {len(spans)} lines')

    # ---- the shelf gaps really are open ------------------------------------
    shelf_lines = joist_x.get(round(G.SHELF_SOUTH, 4), set()) | beam_x
    for a, b in G.SHELF_GAPS:
        inside = [x for x in shelf_lines if a + TOL < x < b - TOL]
        check(not inside, f'shelf gap {a:g}..{b:g} carries no framing',
              f'{b - a:g} in clear')

    # ---- truss planes ------------------------------------------------------
    for tag, x in G.TRUSS_PLANES:
        for suffix, (y0, z0), (y1, z1), w, ref, note in G.TRUSS_PLANE:
            mid = f'{tag}.{suffix}'
            got = ends.get(mid)
            ok = got and all(abs(v - q) < TOL for v, q in
                             zip((got[0][0], got[0][1], got[0][2],
                                  got[1][0], got[1][1], got[1][2]),
                                 (x, y0, z0, x, y1, z1)))
            check(ok, f'truss {mid} endpoints', f'({y0:g},{z0:g}) -> ({y1:g},{z1:.2f})')
    check(abs(G.SQUARE_TOP_Z - 228.75) < TOL, 'square top held at z = 228.75')
    check(abs(G.SOLAR_START_Z - 117.0) < TOL, 'solar slope still starts at z = 117')
    check(abs(G.SOLAR_SLOPE - 0.5773502691896256) < 1e-12,
          'solar slope still 30 degrees')
    for post, top in G.POST_TOPS.items():
        got = ends.get(post)
        check(got and abs(got[1][2] - top) < 1e-6, f'post {post} reaches z = {top:.2f}')
    # The slope chord must actually pass through the top of W1 / S3.
    for plane, post in (('W', 'W1'), ('E', 'S3')):
        a, b = ends[f'{plane}.slope']
        t = (ends[post][1][1] - a[1]) / (b[1] - a[1])
        z_on_chord = a[2] + t * (b[2] - a[2])
        check(abs(z_on_chord - ends[post][1][2]) < 1e-6,
              f'{post} top lands on the {plane} slope chord',
              f'chord z {z_on_chord:.3f} vs post top {ends[post][1][2]:.3f}')
    for mid, y, z, note in G.ROOF_BEAMS:
        got = ends.get(mid)
        ok = got and all(abs(v - q) < 1e-6 for v, q in
                         zip(got[0] + got[1], (G.WEST, y, z, G.BE_X, y, z)))
        check(ok, f'roof beam {mid} spans both truss planes at z = {z:.2f}',
              f'y = {y:g}')
        # Both ends must land on a post -- anywhere along it, since the beam now
        # hangs below the chord top rather than sitting on the post head.
        for x in (G.WEST, G.BE_X):
            hosts = [m for m in f.members
                     if f.group(m) in ('Columns', 'Truss')
                     and abs(ends[m][0][0] - x) < 1e-6 and abs(ends[m][1][0] - x) < 1e-6
                     and abs(ends[m][0][1] - y) < 1e-6 and abs(ends[m][1][1] - y) < 1e-6
                     and min(ends[m][0][2], ends[m][1][2]) - 1e-6 <= z
                     <= max(ends[m][0][2], ends[m][1][2]) + 1e-6]
            check(hosts, f'{mid} lands on a post at x = {x:g}', ', '.join(hosts))
    # And no roof beam may poke above the envelope it sits under.
    for mid, y, z, note in G.ROOF_BEAMS:
        top = z + G.BEAM_D / 2
        limit = (G.SQUARE_TOP_FACE_Z if mid != 'R-W1' else G.R_W1_TOP)
        check(top <= limit + 1e-6, f'{mid} top is flush with the chord, not above it',
              f'beam top {top:.2f} vs chord top {limit:.2f}')

    a, b = ends['C-EN']
    check(abs(abs(b[0] - a[0]) - 36.0) < TOL and abs(a[1] - 251.0) < TOL,
          'C-EN is the 36 in E-N tie at y = 251',
          f'{abs(b[0]-a[0]):g} in')

    # ---- north middle post and the cross-braced bays ------------------------
    nm = ends.get('N-M')
    check(nm and abs(nm[0][0] - G.N_MID_X) < TOL and abs(nm[0][1] - G.B_N_Y) < TOL,
          'N-M stands midway between W4 and N2',
          f'x = {G.N_MID_X:g}, {G.N_MID_X - G.WEST:g} in from W4')
    check(nm and abs(nm[0][2] - G.BEAM_AXIS_Z) < TOL,
          'N-M starts at the beam plane, not the ground',
          f'base z = {G.BEAM_AXIS_Z:g}')
    check('N-M' not in f.supports and 'N-M.base' not in f.supports,
          'N-M takes no footing')
    check(f.group('N-M') != 'Columns', 'N-M is a hung vertical, not a column',
          f.group('N-M'))
    check(abs((G.N_MID_X - G.WEST) - (G.BE_X - G.N_MID_X)) < TOL,
          'N-M divides the north wall into two equal bays',
          f'{G.N_MID_X - G.WEST:g} in each side')
    rw4 = [b for b in G.ROOF_BEAMS if b[0] == 'R-W4'][0]
    check(nm and abs(nm[1][2] - rw4[2]) < 1e-6, 'N-M tops out on R-W4',
          f'z = {rw4[2]:.2f}, halving a {G.BE_X - G.WEST:g} in span')
    for bid, axis, fixed, a0, a1, z0, z1, note in G.CROSS_BRACED_BAYS:
        for k, (p0, p1) in enumerate(((a0, a1), (a1, a0)), 1):
            got = ends.get(f'{bid}-{k}')
            ok = got and abs(got[0][2] - z0) < TOL and abs(got[1][2] - z1) < TOL
            check(ok, f'{bid}-{k} rises the full bay height', f'{note}')
        check(f.group(f'{bid}-1') == 'Bracing',
              f'{bid} is in the pin-released Bracing group')

    # ---- light roof framing --------------------------------------------------
    # Straightness is the point of this revision, so it gets checked directly.
    for x in G.rafter_x():
        a, b = ends[f'RS @ {x:.5g}']
        rise, run = b[2] - a[2], b[1] - a[1]
        check(abs(rise / run - G.SOLAR_SLOPE) < 1e-9,
              f'slope rafter at x = {x:.5g} is one straight run at 30 degrees',
              f'{run:.1f} in of run, {rise:.1f} in of rise')
        # And it must clear the top of R-W1 exactly, not cut through it.
        t = (G.B_S_Y - a[1]) / run
        soffit = a[2] + t * rise - G.SLOPE_RAFTER_D / 2
        check(abs(soffit - G.R_W1_TOP) < 1e-9,
              f'slope rafter at x = {x:.5g} runs across the top of R-W1',
              f'soffit {soffit:.3f} = R-W1 top {G.R_W1_TOP:.3f}')
        af, bf = ends[f'RF @ {x:.5g}']
        check(abs(af[2] - bf[2]) < 1e-9,
              f'flat rafter at x = {x:.5g} runs dead level', f'z = {af[2]:g}')
    check(abs(G.CT_TOP_Z - G.FLAT_AXIS_Z) < 1e-9,
          'CT.top shares the roof beams axis so the flat rafters stay level',
          f'z = {G.CT_TOP_Z:g}')
    check(abs(G.R_SO_Z - G.solar_z(G.B_SO_Y)) < 1e-9,
          'R-SO sits on the slope line so the rafters frame into it',
          f'z = {G.R_SO_Z:g}')
    check(abs(G.POST_TOPS['S1'] - G.R_SO_Z) < 1e-9,
          'S1 reaches the eave to halve R-SO', f'z = {G.R_SO_Z:.3f}')
    raf = f.members_in('Rafters')
    check(len(raf) == 1 + 2 * len(G.rafter_x()) + len(G.EAST_RAFTERS),
          'every rafter, the eave and the four east rafters are present',
          f'{len(raf)} members')
    check(G.rafter_x() == G.ct_mullion_x(),
          'rafters sit on the clerestory mullion lines',
          f'{(G.BE_X - G.WEST) / G.CT_PANELS:.2f} in o.c.')
    # Each rafter end has to land on a primary member, at that member's own axis.
    # A rafter end must land on something that is not just the next rafter up
    # the same station, so members sharing its '@ x' suffix do not count.
    for mid in sorted(raf):
        station = mid.split('@')[-1].strip() if '@' in mid else None
        for k, label in ((0, 'low'), (1, 'high')):
            pt = ends[mid][k]
            hosts = [m for m in f.members if m != mid
                     and f.group(m) != 'Joists'
                     and not (station and m.endswith(station))
                     and _on_axis(ends[m], pt)]
            check(hosts, f'{mid} {label} end lands on a supporting member',
                  ', '.join(sorted(hosts)[:2]))
    for mid, a, b, note in G.EAST_RAFTERS:
        got = ends.get(mid)
        ok = got and all(abs(v - q) < 1e-9 for v, q in zip(got[0] + got[1], a + b))
        check(ok, f'east rafter {mid} runs {note}')

    # ---- clerestory truss ---------------------------------------------------
    ct_top, ct_bot = ends.get('CT.top'), ends.get('CT.bottom')
    check(ct_top and abs(ct_top[0][2] - G.CT_TOP_Z) < TOL
          and abs(ct_top[0][0] - G.WEST) < TOL and abs(ct_top[1][0] - G.BE_X) < TOL,
          'CT.top spans both truss planes', f'z = {G.CT_TOP_Z:g}')
    check(G.CT_TOP_Z + G.CT_CHORD_D / 2 <= G.SQUARE_TOP_FACE_Z + TOL,
          'CT.top flange top is at or below the square chord',
          f'{G.CT_TOP_Z + G.CT_CHORD_D / 2:g} vs {G.SQUARE_TOP_FACE_Z:g}')
    check(ct_bot and abs(ct_bot[0][2] - G.solar_z(G.CLERESTORY_Y)) < 1e-9,
          'CT.bottom sits where the slope chords meet the posts',
          f'z = {G.CT_BOTTOM_Z:.3f}')
    for plane, post in (('W', 'W2'), ('E', 'E.clerestory')):
        a, b = ends[f'{plane}.slope']
        check(abs(b[2] - G.CT_BOTTOM_Z) < 1e-9,
              f'{plane}.slope lands on the clerestory bottom chord level')
    mull = G.ct_mullion_x()
    check(len(mull) == G.CT_PANELS - 1,
          f'{G.CT_PANELS} glazed panels needs {G.CT_PANELS - 1} mullions',
          f'{len(mull)} at {(G.BE_X - G.WEST) / G.CT_PANELS:.2f} in centres')
    for i, x in enumerate(mull, 1):
        got = ends.get(f'CT.mullion.{i}')
        check(got and abs(got[0][0] - x) < 1e-6
              and abs(got[0][2] - G.CT_BOTTOM_Z) < 1e-9
              and abs(got[1][2] - G.CT_TOP_Z) < TOL,
              f'CT.mullion.{i} spans the full clerestory height',
              f'x = {x:.2f}')
    check(abs(mull[len(mull) // 2] - G.N_MID_X) < TOL,
          'the centre mullion lines up with N-M', f'both at x = {G.N_MID_X:g}')
    for m in f.members_in('Clerestory'):
        sec = f.section_of[m]
        if sec.family == 'tee':
            check(sec.compact, f'{m} double-angle T is compact', sec.name)

    # ---- the stair well is open ---------------------------------------------
    w = G.STAIR_WELL
    inside = []
    for m in f.members_in('Joists'):
        a, b = ends[m]
        if (w['west'] - TOL < a[0] < w['east'] + TOL
                and min(a[1], b[1]) > w['south'] - TOL
                and max(a[1], b[1]) < w['north'] + TOL):
            inside.append(m)
    check(not inside, 'stair well carries no joists',
          f'{G.stair_well_sf():.1f} sf clear' if not inside else f'{inside}')
    for edge, want in (('west', ('BW',)), ('east', ('BWI-2',)),
                       ('south', ('B-1',)), ('north', ('B-2',))):
        check(all(n in spec['members'] for n in want),
              f'stair well {edge} edge is framed by a beam', ', '.join(want))
    check(not any(d[1] < w['east'] and d[3] >= w['south'] and d[4] <= w['north']
                  for d in [(n, x1, x2, y1, y2) for n, x1, x2, y1, y2, _ in G.DECKS]),
          'no deck is defined inside the stair well')

    # ---- load bookkeeping ---------------------------------------------------
    area = sum(d['area_sf'] for d in spec['decks'])
    check(abs(area - G.deck_area_sf()) < 0.05, 'deck area agrees with the plan',
          f'{area:.1f} sf')
    check(abs(sum((x2 - x1) * (y2 - y1) for _, x1, x2, y1, y2, _ in G.DECKS) / 144.0
              - area) < 0.05, 'deck area recomputed from the plan rectangles')

    # ---- connectivity -------------------------------------------------------
    seen, todo = set(), list(f.supports)
    while todo:
        n = todo.pop()
        if n not in seen:
            seen.add(n)
            todo.extend(graph.neighbors(n))
    check(seen == set(graph.nodes()), 'every joint has a path to a support',
          f'{len(seen)} of {graph.number_of_nodes()}')
    model, index = framemod.build(f)
    check(len(model.nodes) == graph.number_of_nodes(),
          'PyNite node count matches the joint graph', f'{len(model.nodes)} nodes')
    check(len(model.members) == len(f.segments),
          'PyNite element count matches the segments', f'{len(model.members)} elements')

    # ---- bearing reality check ---------------------------------------------
    for wall, t in (('south', G.EX['wall_south']), ('west', G.EX['wall_west']),
                    ('east', G.EX['wall_east'])):
        check(G.BEAM_BF <= t, f'{G.BEAM_SECTION} flange fits the {wall} wall',
              f'{G.BEAM_BF:g} in flange on a {t:g} in wall')

    passed = sum(1 for ok, _, _ in checks if ok)
    print(f'{path.name}\n')
    for ok, name, detail in checks:
        print(f'  {"PASS" if ok else "FAIL"}  {name}' + (f'   [{detail}]' if detail else ''))
    print(f'\n{passed} of {len(checks)} checks passed')
    (HERE / 'verification.json').write_text(json.dumps(dict(
        model=path.name, passed=passed, total=len(checks),
        failures=[n for ok, n, _ in checks if not ok],
        checks=[dict(check=n, result='pass' if ok else 'fail', detail=d)
                for ok, n, d in checks],
        meaning='Geometry and load-area bookkeeping only. No force, capacity, '
                'connection or foundation is verified here.'), indent=2))
    return 0 if passed == len(checks) else 1


if __name__ == '__main__':
    raise SystemExit(main())
