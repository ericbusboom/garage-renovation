#!/usr/bin/env python
"""Can bracing above the loft replace the ground-floor brace that S1 anchors?

Follows ``column_study``: cutting S1 off at the beam takes ``BR-S-1`` with it
(its footing is S1's), and the frame then fails wind drift by a hair (H/398).
Two places to put the stiffness back, both proposed by the owner:

  A  an X-braced panel between ``B-S`` (z 104.5) and ``R-W1`` (z 147.4) in
     the plane y = 3 -- the 43 in. tall wall under the solar slope
  B  X-bracing in the plane of the solar slope, between the rafters

Each is tried with S1 out, then whichever passes is tried with S1, S2 and S3
all cut off at the beam.  Writes ``results/south-brace-study.json``.
"""
from __future__ import annotations

import copy
import json
import time
from pathlib import Path

import analysis as A
import completion as C
import frame as F
import studies as St
from project_paths import VIZ_DIR
from column_study import (LIVE, cut_ground_floor, fix, judge, recommended,
                          drift_of, _print)

OUT = VIZ_DIR / 'south-brace-study.json'
BRACE = ('HSS2-1/2X2-1/2X1/8', 2.5, 2.5)     # the STR-008 bracing palette


def _node_at(f, x, y, z, member=None):
    for n, v in f.nodes.items():
        if abs(v['x'] - x) < 0.5 and abs(v['y'] - y) < 0.5 and abs(v['z'] - z) < 0.5 \
           and (member is None or member in v.get('members', [])):
            return n
    raise KeyError((x, y, z, member))


def _x(f, tag, a, b, c, d, note):
    """An X: a-d and b-c, where a,b are the bottom corners and c,d the top."""
    sec, w, dd = BRACE
    C._add_member(f, f'{tag}-1', a, d, sec, w, dd, 'Bracing', note=note)
    C._add_member(f, f'{tag}-2', b, c, sec, w, dd, 'Bracing', note=note)
    return [f'{tag}-1', f'{tag}-2']


def brace_bs_rw1(f: F.Frame, bays: str) -> list[str]:
    """X-bracing between B-S and R-W1.  ``bays``: 'ends' or 'all'."""
    xs = [-34.0, 42.7188, 134.781, 211.5]
    if bays == 'truss':
        # the front piece as a truss: B-S the bottom chord, R-W1 the top chord,
        # a vertical at every panel line and an X in every panel
        xs = [-34.0, 12.0312, 58.0625, 104.094, 150.125, 211.5]
    added = []
    sec, w, dd = BRACE
    for k, (x0, x1) in enumerate(zip(xs, xs[1:])):
        if bays == 'ends' and k == 1:
            continue
        if bays == 'truss' and 0 < k:
            a = _node_at(f, x0, 3.0, 104.5, 'B-S')
            c = C._split(f, 'R-W1', (x0, 3.0, 147.355), f'@{x0:g},3,147.355')
            C._add_member(f, f'BR-S1-V{k}', a, c, sec, w, dd, 'Bracing',
                          note='owner proposal: front truss vertical')
            added.append(f'BR-S1-V{k}')
        a = _node_at(f, x0, 3.0, 104.5, 'B-S')
        b = _node_at(f, x1, 3.0, 104.5, 'B-S')
        c = C._split(f, 'R-W1', (x0, 3.0, 147.355), f'@{x0:g},3,147.355')
        d = C._split(f, 'R-W1', (x1, 3.0, 147.355), f'@{x1:g},3,147.355')
        added += _x(f, f'BR-S1-{k}', a, b, c, d,
                    'owner proposal: X-brace between B-S and R-W1 under the slope')
    return added


def brace_slope(f: F.Frame, halves: bool) -> list[str]:
    """X-bracing in the solar-slope plane between neighbouring rafters."""
    rafters = ['W.slope'] + sorted((m for m in f.members if m.startswith('RS @')),
                                   key=lambda m: float(m.split('@')[1])) + ['E.slope']
    eave, top = (-63.0, 112.25), (71.0, 194.365 - 4.75)
    mid = ((eave[0] + top[0]) / 2, (eave[1] + top[1]) / 2)
    added = []
    for k, (r0, r1) in enumerate(zip(rafters, rafters[1:])):
        x0 = f.xyz(_node_at(f, *_any(f, r0), member=r0))[0]
        x1 = f.xyz(_node_at(f, *_any(f, r1), member=r1))[0]
        lo0 = _node_at(f, x0, *eave, r0)
        lo1 = _node_at(f, x1, *eave, r1)
        hi0 = _node_at(f, x0, *top, r0)
        hi1 = _node_at(f, x1, *top, r1)
        if halves:
            m0 = C._split(f, r0, (x0, mid[0], mid[1]), f'@{x0:g},{mid[0]:g},{mid[1]:g}')
            m1 = C._split(f, r1, (x1, mid[0], mid[1]), f'@{x1:g},{mid[0]:g},{mid[1]:g}')
            added += _x(f, f'BR-SL-{k}a', lo0, lo1, m0, m1, 'owner proposal: slope-plane X')
            added += _x(f, f'BR-SL-{k}b', m0, m1, hi0, hi1, 'owner proposal: slope-plane X')
        else:
            added += _x(f, f'BR-SL-{k}', lo0, lo1, hi0, hi1, 'owner proposal: slope-plane X')
    return added


def _any(f, member):
    for m, i, j in f.segments:
        if m == member:
            return f.xyz(i)
    raise KeyError(member)


def run(built, params, combos, base, tag, columns, bracing=None):
    t = time.time()
    g = copy.deepcopy(built)
    added = bracing(g) if bracing else []
    cuts = {c: cut_ground_floor(g, c) for c in columns}
    r = A.run(g, params, LIVE, combos=combos)
    v = dict(tag=tag, columns=list(columns), bracing=added, cuts=cuts,
             judge=judge(g, r, base),
             drift_by_combo={k: d['ratio'] for k, d in r.drift.items()},
             brace_dcr={m: round(r.members[m].dcr, 3) for m in added if m in r.members},
             added_lb=round(sum(g.member_weight(m) for m in added), 1))
    if v['judge']['passes']:
        rf = A.run(g, params, LIVE)
        v['full_combos'] = judge(g, rf, base)
        v['judge']['passes_full'] = v['full_combos']['passes']
    else:
        v['fix'] = fix(g, params, combos)
    _print(tag, v, time.time() - t)
    print(f'   drift by combo: ' + '  '.join(f'{k.split("[")[1][:-1]} H/{d:.0f}'
                                              for k, d in v['drift_by_combo'].items() if d)
          + (f'\n   bracing {len(added)} members, {v["added_lb"]:.0f} lb, DCR '
             f'{max(v["brace_dcr"].values()):.2f} max' if added else ''), flush=True)
    return v


def main() -> None:
    t0 = time.time()
    built, params, final, combos = recommended()
    base = A.run(built, params, LIVE, combos=combos)
    print('baseline drift by combo: ' + '  '.join(
        f'{k.split("[")[1][:-1]} H/{d["ratio"]:.0f}' for k, d in base.drift.items() if d['ratio']))

    configs = {
        'A-ends': lambda g: brace_bs_rw1(g, 'ends'),
        'A-all': lambda g: brace_bs_rw1(g, 'all'),
        'B-full': lambda g: brace_slope(g, halves=False),
        'B-half': lambda g: brace_slope(g, halves=True),
    }
    out = [run(built, params, combos, base, 'S1 (reference)', ['S1'])]
    passing = []
    for name, fn in configs.items():
        v = run(built, params, combos, base, f'S1 + {name}', ['S1'], fn)
        out.append(v)
        if v['judge']['passes']:
            passing.append(name)
    print(f'\npassing bracing configs with S1 out: {passing}')

    out.append(run(built, params, combos, base, 'S1+S2+S3 (no bracing)', ['S1', 'S2', 'S3']))
    for name in passing:
        out.append(run(built, params, combos, base, f'S1+SW0 + {name}', ['S1', 'SW0'], configs[name]))
        out.append(run(built, params, combos, base, f'S1+S2+S3 + {name}', ['S1', 'S2', 'S3'], configs[name]))

    OUT.write_text(json.dumps(dict(generated=time.strftime('%Y-%m-%d %H:%M'),
                                   live_case=LIVE, variants=out), indent=1, default=str))
    print(f'\nwrote {OUT}  ({time.time() - t0:.0f}s total)')


if __name__ == '__main__':
    main()


def brace_floor(f: F.Frame, x_lines=(-34.0, 3.75, 88.75, 150.125, 211.5),
                y_lines=(3.0, 71.0, 128.0, 185.0)) -> list[str]:
    """X-bracing in the loft floor plane (z 104.5) between B-S and B-2.

    Owner proposal: a horizontal truss inside the deck, panel by panel on the
    beam grid, so wind at the loft level reaches the braced north wall through
    the framing instead of through the beams' weak axes.  Panels with no beam on
    one edge (the stair opening) are skipped.
    """
    beam_at = {3.0: 'B-S', 71.0: 'B-1', 128.0: 'B-1A', 185.0: 'B-2'}
    added = []
    for k, (y0, y1) in enumerate(zip(y_lines, y_lines[1:])):
        for j, (x0, x1) in enumerate(zip(x_lines, x_lines[1:])):
            try:
                corners = [C._split(f, beam_at[y], (x, y, 104.5), f'@{x:g},{y:g}')
                           for y in (y0, y1) for x in (x0, x1)]
            except Exception:
                continue          # no beam there to land on
            a, b, c, d = corners  # (x0,y0) (x1,y0) (x0,y1) (x1,y1)
            added += _x(f, f'BR-F-{k}{j}', a, b, c, d,
                        'owner proposal: floor-plane X between B-S and B-2')
    return added


def brace_east(f: F.Frame, y_lines=(3.0, 71.0, 128.0, 185.0, 268.0)) -> list[str]:
    """The east wall as a truss: BE the bottom chord, BE.upper the top chord,
    a vertical at every interior panel line and an X in every panel."""
    sec, w, dd = BRACE
    x = 211.5
    added = []
    for k, (y0, y1) in enumerate(zip(y_lines, y_lines[1:])):
        a = C._split(f, 'BE', (x, y0, 104.5), f'@{x:g},{y0:g}')
        b = C._split(f, 'BE', (x, y1, 104.5), f'@{x:g},{y1:g}')
        c = C._split(f, 'BE.upper', (x, y0, 147.355), f'BE.upper@{y0:g}')
        d = C._split(f, 'BE.upper', (x, y1, 147.355), f'BE.upper@{y1:g}')
        if k > 0:
            C._add_member(f, f'BR-E-V{k}', a, c, sec, w, dd, 'Bracing',
                          note='owner proposal: east truss vertical')
            added.append(f'BR-E-V{k}')
        added += _x(f, f'BR-E-{k}', a, b, c, d, 'owner proposal: X between BE and BE.upper')
    return added


SLOPE = 0.57735    # tan 30, the solar slope


def move_south_line(f: F.Frame, dy: float = 6.0, y_line: float = 3.0) -> dict:
    """Shift the B-S line (B-S, R-W1, the W1 and S3 posts above the beam, the
    slope nodes there) south by ``dy`` so it clears the house.  Nodes above the
    beam ride down the 30-degree slope so the roof plane is not kinked."""
    moved = []
    for n, v in f.nodes.items():
        if abs(v['y'] - y_line) < 0.01:
            v['y'] -= dy
            if v['z'] > 104.6:
                v['z'] -= dy * SLOPE
            moved.append(n)
    return dict(moved=len(moved), new_y=y_line - dy)


def rake_s3(f: F.Frame, section: str = 'HSS5X5X1/4', top: str = '@211.5,3') -> str:
    """S3 as a raking column: from S2's footing up to the B-S / BE / S3U joint."""
    spec = f.members['S2']
    C._add_member(f, 'S3.rake', 'S2.base', top, section, spec['width'], spec['depth'],
                  'Columns', note='owner proposal: S3 raked from the S2 footing')
    return 'S3.rake'


def move_s1(f: F.Frame, dx: float = 24.0, x_old: float = 145.5, y_line: float = -63.0) -> dict:
    """Slide S1 (and the brace ends that share its nodes) east along B-SO."""
    moved = []
    for n, v in f.nodes.items():
        if abs(v['x'] - x_old) < 0.01 and abs(v['y'] - y_line) < 0.01:
            v['x'] += dx
            moved.append(n)
    return dict(moved=moved, new_x=x_old + dx)


def _seg(f, m, i, j):
    f.segments.append((m, i, j))
    for n in (i, j):
        f.nodes[n].setdefault('members', [])
        if m not in f.nodes[n]['members']:
            f.nodes[n]['members'].append(m)


def east_frame(f: F.Frame, wall_x: float = 247.5, post_ys=(-63.0, -6.0, 268.0),
               beam_section: str = 'W14X22', post_section: str = 'HSS5X5X1/4') -> dict:
    """Move BE out to the existing east wall line on new posts, extend the
    floor beams to it, and run E.clerestory and E.W3 down to the deck beams."""
    import owner_revisions as OR
    import sections as S
    beams = ['B-SO', 'B-S', 'B-1', 'B-1A', 'B-2', 'B-N']
    ends = {}
    for b in beams:
        ns = {n for m, i, j in f.segments if m == b for n in (i, j)}
        east = max(ns, key=lambda n: f.xyz(n)[0])
        y = f.xyz(east)[1]
        new = f'EF@{y:g}'
        f.nodes[new] = dict(x=wall_x, y=y, z=104.5, members=[])
        _seg(f, b, east, new)
        ends[y] = new
    OR._drop(f, 'BE')
    chain = [ends[y] for y in sorted(ends)]
    spec = dict(nodes=chain, width=5.0, depth=13.7, group='Beams', material='steel',
                source_name='BE', section_reference=beam_section,
                section_status='owner proposal: BE moved to the east wall line')
    f.members['BE'] = spec
    f.section_of['BE'] = S.get(beam_section)
    for a, b in zip(chain, chain[1:]):
        _seg(f, 'BE', a, b)
    posts = []
    for y in post_ys:
        top = ends.get(y) or min(ends, key=lambda k: abs(k - y))
        top = ends[top] if not isinstance(top, str) else top
        base = f'EF@{y:g}.base'
        f.nodes[base] = dict(x=wall_x, y=y, z=0.0, support=True, members=[])
        name = {-63.0: 'E-S2', -6.0: 'E-S3', 3.0: 'E-S3', 268.0: 'E-N2'}.get(y, f'E@{y:g}')
        C._add_member(f, name, base, top, post_section, 5.0, 5.0, 'Columns',
                      note='owner proposal: east wall post')
        posts.append(name)
    # the upper east truss verticals continue down to the deck beams
    # separate members, so the upper truss verticals can go in before demo
    # while the legs down to the deck beams wait with B-1 and B-2
    for m, low, high in (('E.clerestory', '@211.5,71', 'BE.upper@71'),
                         ('E.W3', '@211.5,185', 'BE.upper@185')):
        sec = f.section_of[m]
        C._add_member(f, m + '.lower', low, high, sec.name, sec.b, sec.d, 'Truss',
                      note='owner proposal: truss vertical carried down to the deck beam')
    return dict(posts=posts, beam_nodes=chain)


def raise_floor(f: F.Frame, dz: float = 8.0, level: float = 104.5) -> int:
    """Lift the loft grillage and everything above it by ``dz``; the
    ground-floor columns simply get taller."""
    n = 0
    for v in f.nodes.values():
        if v['z'] >= level - 0.01:
            v['z'] += dz
            n += 1
    return n


def merge_bwi(f: F.Frame, name: str = 'BWI') -> list[str]:
    """One continuous interior west beam in place of the BWI pieces."""
    parts = sorted(m for m in f.members if m.startswith('BWI'))
    if not parts:
        return []
    spec = dict(f.members[parts[0]])
    sec = f.section_of[parts[0]]
    f.segments[:] = [((name if m in parts else m), i, j) for m, i, j in f.segments]
    for v in f.nodes.values():
        ms = v.get('members', [])
        if any(m in parts for m in ms):
            v['members'] = [m for m in ms if m not in parts] + [name]
    for m in parts:
        f.members.pop(m); f.section_of.pop(m)
    spec['source_name'] = name
    f.members[name] = spec
    f.section_of[name] = sec
    return parts


def south_x_to_wall(f: F.Frame) -> list[str]:
    """Move the south X-brace to the bay between S1 and the east wall post."""
    import owner_revisions as OR
    for m in ('BR-S-1', 'BR-S-2'):
        if m in f.members:
            OR._drop(f, m)
    sec, w, d = BRACE
    s1_beam = next(n for n, v in f.nodes.items()
                   if 'S1' in v.get('members', []) and abs(v['y'] + 63) < 0.01 and v['z'] > 1)
    C._add_member(f, 'BR-S-1', 'S1.base', 'EF@-63', sec, w, d, 'Bracing',
                  note='owner: south X between S1 and the east wall post')
    C._add_member(f, 'BR-S-2', 'EF@-63.base', s1_beam, sec, w, d, 'Bracing',
                  note='owner: south X between S1 and the east wall post')
    return ['BR-S-1', 'BR-S-2']
