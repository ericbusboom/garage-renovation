"""Compile the BEAM-001 scheme into a COMPAS frame model.

The plan in ``geometry.py`` is the input. Everything here is mechanical: put the
beams on one plane at the existing wall top, stand a column under every support
point, lay joists across each deck, then find every place two members touch and
split them there so the result is a finite-element mesh rather than a picture.

Output is a canonical COMPAS model in ``frame-models/`` with the same schema the
truss lineage uses, so ``structural-analysis-v6`` can load it unchanged.

Run: /Volumes/Proj/proj/CAD/garage/.venv/bin/python build_frame.py
"""
from __future__ import annotations

import json
import math
import sys
from itertools import combinations
from pathlib import Path

from compas.data import json_dump, json_load
from compas.datastructures import Graph
from compas_model.models import Model

import geometry as G

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'compas-study'))
from geometry_types import MemberElement          # noqa: E402
import frame_models                                # noqa: E402

TOL = 1e-6
Z = G.BEAM_AXIS_Z


# ---------------------------------------------------------------------------
# the member set
# ---------------------------------------------------------------------------

def member_set():
    """Every member as (id, start, end, record). Coordinates are explicit."""
    out = []

    def add(mid, a, b, group, material, section, w, d, note):
        out.append((mid, tuple(map(float, a)), tuple(map(float, b)), dict(
            group=group, material=material, section_reference=section,
            width=w, depth=d, source_name=mid, note=note,
            section_status='owner-directed section; connection design unverified')))

    for name, y, x1, x2, on_wall, note in G.CROSS_BEAMS:
        add(name, (x1, y, Z), (x2, y, Z), 'Beams', 'steel', G.BEAM_SECTION,
            G.BEAM_BF, G.BEAM_D, note)
    for name, x, y1, y2, on_wall, note in G.LINE_BEAMS:
        add(name, (x, y1, Z), (x, y2, Z), 'Beams', 'steel', G.BEAM_SECTION,
            G.BEAM_BF, G.BEAM_D, note)
    for cid, x, y, size, kind in G.COLUMNS:
        top = G.POST_TOPS.get(cid, Z)
        note = 'bolted base plate to a concrete pier; pinned in analysis'
        if top > Z:
            note += f'; extended to z = {top:g} in the {"west" if x == G.WEST else "east"} truss plane'
        add(cid, (x, y, 0.0), (x, y, top), 'Columns', 'steel', G.COLUMN_SECTION,
            G.COLUMN_SIZE, G.COLUMN_SIZE, note)

    for mid, x, y, z0, z1, w, ref, note in G.HUNG_VERTICALS:
        add(mid, (x, y, z0), (x, y, z1), 'Truss', 'steel', ref, w, w, note)

    for mid, y, z, note in G.ROOF_BEAMS:
        add(mid, (G.WEST, y, z), (G.BE_X, y, z), 'Roof', 'steel',
            G.ROOF_BEAM_SECTION, G.BEAM_BF, G.BEAM_D, note)

    # Ground-level cross bracing: an X in the plane of the wall.
    for bid, axis, fixed, a0, a1, z0, z1, note in G.CROSS_BRACED_BAYS:
        def pt(a, z):
            return (fixed, a, z) if axis == 'x' else (a, fixed, z)
        add(f'{bid}-1', pt(a0, z0), pt(a1, z1), 'Bracing', 'steel',
            G.BRACE_SECTION, 2.5, 2.5, f'{note}, rising')
        add(f'{bid}-2', pt(a1, z0), pt(a0, z1), 'Bracing', 'steel',
            G.BRACE_SECTION, 2.5, 2.5, f'{note}, falling')

    # Light roof framing: the eave, the rafters in both roof planes, and the
    # four east lean-to rafters.
    add('R-SO', (G.WEST, G.B_SO_Y, G.R_SO_Z), (G.BE_X, G.B_SO_Y, G.R_SO_Z),
        'Rafters', 'steel', G.EAVE_SECTION, 3.5, 3.5,
        'south eave, top flush with the slope surface; S1 holds it at midspan')
    for x in G.rafter_x():
        for prefix, (y0, z0), (y1, z1) in G.SLOPE_RAFTERS:
            add(f'{prefix} @ {x:.5g}', (x, y0, z0), (x, y1, z1), 'Rafters', 'steel',
                G.SLOPE_RAFTER_SECTION, G.SLOPE_RAFTER_D, G.SLOPE_RAFTER_D,
                f'slope rafter at x = {x:.5g}, one piece over the top of R-W1')
        for prefix, (y0, z0), (y1, z1) in G.FLAT_RAFTERS:
            add(f'{prefix} @ {x:.5g}', (x, y0, z0), (x, y1, z1), 'Rafters', 'steel',
                G.RAFTER_SECTION, 2.5, 2.5,
                f'flat rafter at x = {x:.5g}, level, split where it crosses R-W3')
    for mid, a, b, note in G.EAST_RAFTERS:
        add(mid, a, b, 'Rafters', 'steel', G.RAFTER_SECTION, 2.5, 2.5,
            f'east lean-to rafter, {note}')

    # Clerestory truss, in the y = CLERESTORY_Y plane. Replaces R-W2.
    cy = G.CLERESTORY_Y
    add('CT.top', (G.WEST, cy, G.CT_TOP_Z), (G.BE_X, cy, G.CT_TOP_Z),
        'Clerestory', 'steel', G.CT_CHORD, G.CT_CHORD_B, G.CT_CHORD_D,
        'top chord, flange top flush with the square chord at 231.25')
    add('CT.bottom', (G.WEST, cy, G.CT_BOTTOM_Z), (G.BE_X, cy, G.CT_BOTTOM_Z),
        'Clerestory', 'steel', G.CT_CHORD, G.CT_CHORD_B, G.CT_CHORD_D,
        'bottom chord, where the slope chords meet the posts')
    mull = G.ct_mullion_x()
    for i, x in enumerate(mull, 1):
        add(f'CT.mullion.{i}', (x, cy, G.CT_BOTTOM_Z), (x, cy, G.CT_TOP_Z),
            'Clerestory', 'steel', G.CT_MULLION, G.CT_MULLION_B, G.CT_MULLION_D,
            f'window mullion {i} of {len(mull)}')
    for tag, base_x, head_x in (('W', G.WEST, mull[0]), ('E', G.BE_X, mull[-1])):
        add(f'CT.diag.{tag}', (base_x, cy, G.CT_BOTTOM_Z), (head_x, cy, G.CT_TOP_Z),
            'Clerestory', 'steel', G.CT_DIAGONAL, 2.0, 2.0,
            f'end-panel diagonal, {tag} bay is a spandrel not glazing')

    for tag, x in G.TRUSS_PLANES:
        for suffix, (y0, z0), (y1, z1), w, ref, note in G.TRUSS_PLANE:
            add(f'{tag}.{suffix}', (x, y0, z0), (x, y1, z1), 'Truss', 'steel',
                ref, w, w, note)

    for name, x1, x2, y1, y2, rims in G.DECKS:
        for i, x in enumerate(joist_lines(x1, x2, rims)):
            add(f'{name} joist {i + 1}', (x, y1, Z), (x, y2, Z), 'Joists', 'wood',
                G.JOIST_SECTION, G.JOIST_W, G.JOIST_D,
                f'{name}; rim' if x in (x1, x2) else name)
    return out


def joist_lines(x1, x2, rims):
    """Joist x-positions at or under the maximum spacing, rims only where asked."""
    n = max(1, math.ceil((x2 - x1) / G.JOIST_SPACING_MAX))
    xs = [x1 + (x2 - x1) * i / n for i in range(n + 1)]
    if 'west' not in rims:
        xs = xs[1:]
    if 'east' not in rims:
        xs = xs[:-1]
    return xs


# ---------------------------------------------------------------------------
# joints: endpoints, plus every crossing of a north-south and an east-west run
# ---------------------------------------------------------------------------

def axis_of(a, b):
    if abs(a[2] - b[2]) > TOL:
        return 'V'
    return 'EW' if abs(a[1] - b[1]) < TOL else 'NS'


def joint_points(members):
    pts = {}

    def key(p):
        return tuple(round(v, 6) for v in p)

    for mid, a, b, rec in members:
        pts.setdefault(key(a), a)
        pts.setdefault(key(b), b)

    ew = [(m, a, b) for m, a, b, _ in members if axis_of(a, b) == 'EW']
    ns = [(m, a, b) for m, a, b, _ in members if axis_of(a, b) == 'NS']
    vert = [(m, a, b) for m, a, b, _ in members if axis_of(a, b) == 'V']
    for _, ea, eb in ew:
        y, x_lo, x_hi = ea[1], min(ea[0], eb[0]), max(ea[0], eb[0])
        for _, na, nb in ns:
            # Both runs are horizontal, so they only meet if they share an
            # elevation. Without this the roof beams pick up a phantom joint
            # wherever a floor-level beam passes beneath them in plan.
            if abs(na[2] - ea[2]) > TOL:
                continue
            x, y_lo, y_hi = na[0], min(na[1], nb[1]), max(na[1], nb[1])
            if x_lo - TOL <= x <= x_hi + TOL and y_lo - TOL <= y <= y_hi + TOL:
                pts.setdefault(key((x, y, ea[2])), (x, y, ea[2]))
    # A post that grows past the beam plane still has to be split where each
    # horizontal member crosses its axis.
    for _, va, vb in vert:
        z_lo, z_hi = min(va[2], vb[2]), max(va[2], vb[2])
        for _, ha, hb in ew + ns:
            if not (z_lo - TOL <= ha[2] <= z_hi + TOL):
                continue
            inside = (min(ha[0], hb[0]) - TOL <= va[0] <= max(ha[0], hb[0]) + TOL
                      and min(ha[1], hb[1]) - TOL <= va[1] <= max(ha[1], hb[1]) + TOL)
            if inside:
                pts.setdefault(key((va[0], va[1], ha[2])), (va[0], va[1], ha[2]))
    return pts


def name_joints(pts, members):
    """Readable, stable joint names: column ends win, then plan coordinates."""
    names = {}
    for mid, a, b, rec in members:
        if rec['group'] != 'Columns':
            continue
        names[tuple(round(v, 6) for v in a)] = f'{mid}.base'
        names[tuple(round(v, 6) for v in b)] = f'{mid}.top'
    for k, p in pts.items():
        if k not in names:
            names[k] = f'@{p[0]:g},{p[1]:g}' + ('' if abs(p[2] - Z) < TOL else f',{p[2]:g}')
    return names


# ---------------------------------------------------------------------------
# compile
# ---------------------------------------------------------------------------

def compile_frame():
    members = member_set()
    pts = joint_points(members)
    names = name_joints(pts, members)
    coord = {names[k]: p for k, p in pts.items()}

    supports = {names[tuple(round(v, 6) for v in a)]
                for mid, a, b, rec in members if rec['group'] == 'Columns'}
    # BEW overhangs its end posts by 2 in at each end, as the truss scheme did.
    free = set()
    for mid, a, b, rec in members:
        if mid == 'BEW':
            for p in (a, b):
                free.add(names[tuple(round(v, 6) for v in p)])

    graph = Graph(name='BEAM-001 joints')
    model = Model(name='BEAM-001 beam-scheme frame')
    incidence = {n: set() for n in coord}
    elements, rows, segments = {}, [], []

    for mid, a, b, rec in members:
        axis = [b[i] - a[i] for i in range(3)]
        length = math.sqrt(sum(v * v for v in axis))
        on = []
        for n, p in coord.items():
            t = sum((p[i] - a[i]) * axis[i] for i in range(3)) / length ** 2
            if -TOL <= t <= 1 + TOL:
                near = [a[i] + t * axis[i] for i in range(3)]
                if max(abs(near[i] - p[i]) for i in range(3)) <= 1e-5:
                    on.append((t, n))
        on.sort()
        chain = [n for _, n in on]
        if len(chain) < 2:
            raise ValueError(f'{mid}: fewer than two joints on the member')
        for n in chain:
            incidence[n].add(mid)
        for u, v in zip(chain, chain[1:]):
            segments.append((mid, u, v))
        el = MemberElement(list(a), list(b), rec['width'], rec['depth'], name=mid)
        mesh = el.compute_elementgeometry()
        if not mesh.is_valid() or not mesh.is_closed():
            raise ValueError(f'{mid}: invalid member solid')
        model.add_element(el)
        elements[mid] = el
        rec['_chain'] = chain

    for n, p in coord.items():
        graph.add_node(n, x=p[0], y=p[1], z=p[2], support=n in supports,
                       free_end=n in free, members=sorted(incidence[n]))
    edges = {}
    for mid, u, v in segments:
        edges.setdefault((u, v), []).append(mid)
    for (u, v), mids in edges.items():
        graph.add_edge(u, v, members=mids, kind='member segment')

    # Every member end is either shared with another member, a ground support,
    # or a declared overhang. Anything else is a modelling error.
    for mid, a, b, rec in members:
        for end, p in (('start', a), ('end', b)):
            n = names[tuple(round(v, 6) for v in p)]
            others = sorted(incidence[n] - {mid})
            status = ('connected' if others else
                      'ground support' if n in supports else
                      'declared overhang' if n in free else 'DISCONNECTED')
            if status == 'DISCONNECTED':
                raise ValueError(f'unconnected end: {mid} / {end} / {n}')
            rows.append(dict(member=mid, end=end, joint=n, status=status,
                             connected_to='; '.join(others), group=rec['group']))

    linked = set()
    for n, group in incidence.items():
        for x, y in combinations(sorted(group), 2):
            if (x, y) not in linked:
                model.add_interaction(elements[x], elements[y])
                linked.add((x, y))

    seen, todo = set(), list(supports)
    while todo:
        n = todo.pop()
        if n not in seen:
            seen.add(n)
            todo.extend(graph.neighbors(n))
        stranded = set(graph.nodes()) - seen
    if stranded:
        raise ValueError(f'joints with no path to a support: {sorted(stranded)[:8]}')

    spec = dict(
        schema='garage.beam-scheme/1', units='inches',
        parameters=dict(
            west_x=G.WEST, be_x=G.BE_X, bew_x=G.BEW_X, bwi_x=G.BWI_X,
            b_so_y=G.B_SO_Y, b_s_y=G.B_S_Y, b_1_y=G.B_1_Y, b_1a_y=G.B_1A_Y,
            b_2_y=G.B_2_Y, b_n_y=G.B_N_Y,
            wall_top_z=G.WALL_TOP_Z, beam_axis_z=Z, beam_depth=G.BEAM_D,
            design_live_psf=G.DESIGN_LIVE_PSF),
        nodes={n: dict(xyz=list(p), support=n in supports) for n, p in coord.items()},
        members={mid: {k: v for k, v in rec.items() if k != '_chain'}
                 | dict(nodes=[rec['_chain'][0], rec['_chain'][-1]])
                 for mid, _, _, rec in members},
        decks=[dict(name=n, x=[x1, x2], y=[y1, y2], rims=list(r),
                    area_sf=(x2 - x1) * (y2 - y1) / 144.0)
               for n, x1, x2, y1, y2, r in G.DECKS],
        intent='Single-level beam grillage for stiffness and loading analysis. '
               'Not a connection, foundation or fabrication model.',
        joint_policy='All beams share one plane at the existing wall top. Joints are '
                     'member endpoints plus every crossing of an east-west and a '
                     'north-south run. BEW carries two declared 2 in overhangs.',
        owner_direction=[
            'All beams sit on top of the existing walls and are W14X22.',
            'All columns are 4 in, bolted to concrete piers (pinned in analysis).',
            'Joists and deck applied; design live load 100 psf.',
            'Every shelf panel has a framing member on each edge.'],
    )
    return spec, graph, model, rows, len(linked), coord, segments


def main():
    spec, graph, model, rows, interactions, coord, segments = compile_frame()
    data = {'specification': spec, 'joint_graph': graph, 'model': model}
    dest = frame_models.allocate('beam-scheme')
    json_dump(data, dest)

    # Save / reload round trip: the stored file is the model, not a copy of it.
    rt = json_load(dest)
    assert rt['joint_graph'].number_of_nodes() == graph.number_of_nodes()
    assert rt['joint_graph'].number_of_edges() == graph.number_of_edges()
    saved = {el.name: el for el in rt['model'].elements()}
    assert set(saved) == set(spec['members'])
    for mid, el in saved.items():
        a, b = [coord[n] for n in spec['members'][mid]['nodes']]
        assert max(abs(list(el.start)[i] - a[i]) for i in range(3)) < 1e-9
        assert max(abs(list(el.end)[i] - b[i]) for i in range(3)) < 1e-9

    groups = {}
    for mid, rec in spec['members'].items():
        groups.setdefault(rec['group'], 0)
        groups[rec['group']] += 1
    audit = dict(
        model=dest.name,
        members=len(spec['members']), member_groups=groups,
        segments=len(segments), joints=graph.number_of_nodes(),
        graph_edges=graph.number_of_edges(), element_interactions=interactions,
        supports=sum(1 for n in graph.nodes() if graph.node_attribute(n, 'support')),
        declared_overhangs=sum(1 for n in graph.nodes()
                               if graph.node_attribute(n, 'free_end')),
        disconnected_ends=sum(1 for r in rows if r['status'] == 'DISCONNECTED'),
        all_joints_reach_a_support=True,
        deck_area_sf=round(sum(d['area_sf'] for d in spec['decks']), 1),
        beam_axis_z=Z, wall_top_z=G.WALL_TOP_Z,
        round_trip='save/reload verified: node count, edge count and every member '
                   'endpoint match to 1e-9 in',
        meaning='Geometric connectivity and regeneration checks only. No forces, '
                'capacities, joints or foundations are verified here.')
    (Path(__file__).parent / 'frame-audit.json').write_text(json.dumps(audit, indent=2))
    import csv
    with (Path(__file__).parent / 'member-end-audit.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(audit, indent=2))
    return dest


if __name__ == '__main__':
    main()
