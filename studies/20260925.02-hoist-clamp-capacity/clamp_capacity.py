"""Hoist capacity from beam clamps on the loft floor beams (BWI, B-1, B-1A, B-2).

A trolley runway hangs from beam clamps on the bottom flange of the W12x16 loft
beams.  With the trolley directly under a clamp, that one clamp carries the whole
hoisted load, so the question per floor beam is: what rated load W can hang from
a single point at each station along it, on top of the loft's own dead + floor live.

One model, one unit hoist case per station (1,000 lb rated: 1,250 lb vertical with
25 % impact plus 100 lb lateral across the beam, ASCE 7-16 4.6.2 as in loads.HOIST).
Member demands are linear in the loads, so each station's capacity is found by
bisecting the factored hoist multiplier against the full AISC check of every steel
member.  Two end conditions bound the unsized connections: the project model
(beams continuous through their joints) and every floor-beam end pinned.

Run from the repository root:
    archive/.venv/bin/python studies/20260925.02-hoist-clamp-capacity/clamp_capacity.py
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / 'src' / 'structural-analysis-v6'
sys.path.insert(0, str(SRC))

import numpy as np

import analysis as A
import codecheck
import frame as F
import lean_to_rafters as LT
import loadcases
import loads as L

BEAMS = ['BWI', 'B-1', 'B-1A', 'B-2']
FLOOR_LIVE = {'L100': 100.0, 'L40': 40.0, 'L0': 0.0}   # psf present on the loft while lifting
UNIT = 1000.0                                           # lb rated per unit case
ST = A.STATIONS


def stations(f, member):
    """Interior nodes along the member (clamp positions), with position along it."""
    segs = F._ordered(f, [(i, j) for m, i, j in f.segments if m == member])
    chain = [segs[0][0]] + [j for _, j in segs]
    x0 = np.array(f.xyz(chain[0]))
    out = [(n, float(np.linalg.norm(np.array(f.xyz(n)) - x0))) for n in chain[1:-1]]
    return out, f.member_length(member)


def build(pinned):
    f, spec, _ = LT.build()
    if pinned:
        for m in BEAMS:
            segs = F._ordered(f, [(i, j) for mm, i, j in f.segments if mm == m])
            f.pinned_ends += [(m, segs[0][0]), (m, segs[-1][1])]
    return f, spec


def solve(pinned):
    f, spec = build(pinned)
    params = spec['parameters']
    model, index = F.build(f)
    b = loadcases.LoadBuilder(f, model, index, params)
    b.dead()
    b.separate_structure()
    b.roof_live()
    b.loft_live('L100', 100.0)
    pts = {}
    for m in BEAMS:
        st, length = stations(f, m)
        a, c = f.xyz(st[0][0]), f.xyz(st[-1][0])
        along_x = abs(c[0] - a[0]) > abs(c[1] - a[1])
        for n, s in st:
            case = f'H:{n}'
            pts.setdefault(n, dict(beams=[], xyz=f.xyz(n)))['beams'].append((m, s, length))
            if case in b.applied:
                continue
            b._point(n, 'FY', -UNIT * (1 + L.HOIST['impact']), case)
            # lateral across the loaded beam: PyNite Z is -frame y, X is frame x
            b._point(n, 'FZ' if along_x else 'FX', UNIT * L.HOIST['lateral'], case)
            model.add_load_combo(f'U:{n}', {case: 1.0})
    for tag, psf in FLOOR_LIVE.items():
        model.add_load_combo(f'B:{tag}', {'D': 1.2, 'L100': 1.6 * psf / 100.0, 'Lr': 0.5})
        model.add_load_combo(f'S:{tag}', {'D': 1.0, 'L100': psf / 100.0})
    t = time.time()
    model.analyze_linear(check_stability=True, check_statics=False, sparse=True)
    print('solve', round(time.time() - t, 1), 's,', len(pts), 'stations', flush=True)

    Lb = A.unbraced_lengths(f)
    steel = [m for m in index if f.material(m) == 'steel']

    def forces(combo):
        out = {}
        for m in steel:
            for el in index[m]:
                e = model.members[el]
                out[(m, el)] = np.array([e.axial_array(ST, combo)[1], e.moment_array('Mz', ST, combo)[1],
                                         e.moment_array('My', ST, combo)[1], e.shear_array('Fy', ST, combo)[1]])
        return out

    def max_dcr(base, unit, k):
        worst = (0.0, None, None)
        for key, fb in base.items():
            fu = unit[key]
            if not np.any(np.abs(fu[1:3]) > 1.0) and not np.any(np.abs(fu[0]) > 1.0):
                continue            # this member doesn't see the hoist
            m = key[0]
            tot = fb + k * fu
            for s in range(ST):
                c = codecheck.check_steel(m, f.section_of[m], F.MATERIALS['steel']['fy'],
                                          *tot[:, s], Lb.get(m, 1.0), '')
                if c.dcr > worst[0]:
                    worst = (c.dcr, m, c.mode)
        return worst

    def defl(combo, n):
        return model.nodes[n].DY[combo]

    bases = {tag: forces(f'B:{tag}') for tag in FLOOR_LIVE}
    base_dcr = {tag: max_dcr(bases[tag], {k: v * 0 + 2 for k, v in bases[tag].items()}, 0.0)
                for tag in FLOOR_LIVE}
    rows = []
    for n, info in pts.items():
        unit = forces(f'U:{n}')
        row = dict(node=n, xyz=info['xyz'], beams=info['beams'],
                   defl_per_1000=-defl(f'U:{n}', n) / (1 + L.HOIST['impact']))
        for tag in FLOOR_LIVE:
            base = bases[tag]
            d0 = max_dcr(base, unit, 0.0)[0]
            lo, hi = 0.0, 20.0                   # multiples of 1.6 x unit case
            if max_dcr(base, unit, 1.6 * hi)[0] <= 1.0:
                lo = hi
            else:
                for _ in range(24):
                    mid = (lo + hi) / 2
                    (lo, hi) = (mid, hi) if max_dcr(base, unit, 1.6 * mid)[0] <= 1.0 else (lo, mid)
            dcr, gov, mode = max_dcr(base, unit, 1.6 * hi)
            row[tag] = dict(capacity_lb=round(lo * UNIT), base_dcr=round(d0, 3),
                            governs=gov, mode=mode,
                            defl_total_at_capacity=round(-defl(f'S:{tag}', n) + row['defl_per_1000'] * lo, 3))
        rows.append(row)
    return dict(pinned=pinned, base=base_dcr, rows=rows)


if __name__ == '__main__':
    out = {}
    for pinned in (False, True):
        key = 'pinned' if pinned else 'continuous'
        t = time.time()
        out[key] = solve(pinned)
        print(key, 'done', round(time.time() - t, 1), 's', flush=True)
    (HERE / 'clamp_capacity.json').write_text(json.dumps(out, indent=1, default=str))
