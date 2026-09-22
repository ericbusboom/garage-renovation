"""Bake the owner revisions into a canonical COMPAS model.

Why this exists
---------------
The revisions the owner asked for -- the south slope seated on ``B-SO``, the
``BE.upper`` beam, the east side rebuilt in wood, the stairwell moved south,
``BWI-2``/``BWI-3`` merged, the ``N-M2`` post, and the braces the study found
redundant -- were written as code in ``owner_revisions.py`` and replayed on
every run. That was right while they were proposals: each one could be applied
or not, and a variant could be analysed against its alternative by flipping a
flag. It stopped being right once they were settled, because it left the stored
model describing a frame nobody intends to build. Anything reading the JSON --
Blender, a viewer, an engineer, the next session -- got the old frame.

This script replays the revisions once and writes the result as a new canonical
model, so the store holds the design rather than its starting point. It uses the
same writer ``beam-design/build_frame.py`` uses, so the output is a COMPAS model
and not a hand-rolled imitation of one.

Run: /Volumes/Proj/proj/CAD/garage/.venv/bin/python bake.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from compas.data import json_dump, json_load
from compas.datastructures import Graph
from compas_model.models import Model

import cabinets as CB
import frame as framemod
import owner_revisions as OR
from project_paths import PROJECT_ROOT as ROOT, STUDIES_DIR

sys.path.insert(0, str(STUDIES_DIR / '20260917.01-compas-frame'))
from geometry_types import MemberElement           # noqa: E402
import frame_models                                # noqa: E402

#: Braces the study verified as removable; see STR-008 section 3. They are
#: deleted here rather than omitted at run time, for the same reason as the
#: rest: the model should be the frame that gets built.
REMOVED = ('E.rear.brace', 'E.square.brace', 'BR-NU-2', 'BR-W-1', 'W.square.brace')


#: Written into the spec of anything this script produces. ``base()`` refuses to
#: bake one of its own outputs: the revisions are not idempotent -- replaying
#: ``move_stair_south`` on a model whose stair has already moved would cut a beam
#: that is no longer there -- so a second bake would quietly corrupt the frame.
BAKED_KEY = 'baked_from'


def base() -> Path:
    """The newest model that has not been baked, i.e. the one to bake from."""
    import json
    paths = sorted(frame_models.DIR.glob('frame-*-beam-scheme.compas.json'))
    for path in reversed(paths):
        spec = json.loads(path.read_text())['specification']
        if BAKED_KEY not in spec:
            return path
    raise SystemExit('every beam-scheme model is already baked; nothing to do')


def revised(path: Path | None = None) -> tuple[framemod.Frame, list[str], dict]:
    """The frame as the owner has directed it, the log, and the side data.

    The east lean-to is wood, bears on the existing east wall and is analysed as
    a separate structure, so it is not in the frame. Its geometry is still drawn
    on the model and the plan, so it has to be stored with them.
    """
    f = framemod.load(path or base())
    log = [f'base {f.path.name}']

    f, note = OR.seat_slope_on_south_beam(f)
    log.append(f'{note["deleted"]} deleted, solar slope dropped '
               f'{note["slope_drop_in"]} in onto B-SO, {note["bearing_links"]} '
               f'bearing links')
    f, upper = OR.add_upper_east_beam(f)
    log.append(f'{OR.UPPER_EAST} added at z={upper["level_z"]:.3f}, '
               f'{upper["span_in"]:.0f} in span; shortened {upper["shortened"]}')
    f, lean = OR.east_lean_to_separate(f)
    log.append(f'east side rebuilt in wood: {len(lean["removed"])} steel members '
               f'out ({lean["removed_steel_lb"]:.0f} lb), lean-to analysed '
               f'separately and carried as line loads')
    f, stair = OR.move_stair_south(f)
    log.append(f'stair moved south: {stair["cut"]} cut to x={stair["cut_back_to"]:g}, '
               f'{stair["extended"]} run west to x={stair["extended_to"]:g}, '
               f'{stair["merged"][0]} absorbed {stair["merged"][1]}, '
               f'joists {stair["joists_pulled"]} out, {stair["joists_added"]} in')
    f, npost = OR.add_north_post(f)
    log.append(f'{npost["post"]} added at x={npost["x"]:g}, loading opening '
               f'{npost["was_open_in"]:g} -> {npost["open_bay_in"]:g} in')

    gone = [m for m in REMOVED if m in f.members]
    for member in gone:
        OR._drop(f, member)
    log.append(f'redundant bracing deleted: {gone}')
    return f, log, dict(lean_to=lean)


def compile_model(f: framemod.Frame, src: Path):
    """Rebuild the COMPAS graph, element model and specification from a Frame."""
    coord = {n: f.xyz(n) for n in f.nodes}
    chains = {m: framemod._ordered(f, [(i, j) for mm, i, j in f.segments if mm == m])
              for m in f.members}

    model, graph = Model(), Graph()
    graph.update_default_node_attributes(x=0.0, y=0.0, z=0.0)
    incidence: dict[str, set] = {n: set() for n in coord}
    for mid, rec in f.members.items():
        segs = chains[mid]
        nodes = [segs[0][0]] + [j for _, j in segs]
        for n in nodes:
            incidence[n].add(mid)
        a, b = coord[nodes[0]], coord[nodes[-1]]
        el = MemberElement(list(a), list(b), rec['width'], rec['depth'], name=mid)
        mesh = el.compute_elementgeometry()
        if not mesh.is_valid() or not mesh.is_closed():
            raise ValueError(f'{mid}: invalid member solid')
        model.add_element(el)
        rec = dict(rec)
        rec['nodes'] = [nodes[0], nodes[-1]]
        f.members[mid] = rec

    for n, p in coord.items():
        v = f.nodes[n]
        graph.add_node(n, x=p[0], y=p[1], z=p[2],
                       support=bool(v.get('support')),
                       free_end=bool(v.get('free_end')),
                       members=sorted(incidence[n]))
    edges: dict[tuple[str, str], list[str]] = {}
    for mid, u, v in f.segments:
        edges.setdefault((u, v), []).append(mid)
    for (u, v), mids in edges.items():
        graph.add_edge(u, v, members=sorted(mids), kind='member segment')
    for i, j, kind in f.links:
        if not graph.has_edge((i, j), directed=False):
            graph.add_edge(i, j, members=[], kind=kind)

    import json as _json
    base_spec = _json.loads(src.read_text())['specification']
    spec = dict(
        schema=base_spec['schema'], units=base_spec['units'],
        parameters=dict(base_spec['parameters']),
        nodes={n: dict(xyz=list(p), support=bool(f.nodes[n].get('support')))
               for n, p in coord.items()},
        members={mid: dict(rec) for mid, rec in f.members.items()},
        decks=[dict(d) for d in f.decks],
        extra_loads=[list(x) for x in f.extra_loads],
        intent=base_spec['intent'],
        joint_policy=base_spec['joint_policy'],
        owner_direction=list(base_spec.get('owner_direction', [])),
    )
    return spec, graph, model, coord


def main() -> None:
    src = base()
    f, log, side = revised(src)
    print('replayed:')
    for line in log:
        print('  -', line)

    spec, graph, model, coord = compile_model(f, src)
    spec[BAKED_KEY] = src.name
    spec['revisions'] = log[1:]
    spec['lean_to'] = side['lean_to']

    # The loft layout travels with the frame. It is stored, not owned: the
    # editing surface is still cabinets.py, and this is a snapshot of what that
    # produced, so a reader of the model sees the room as well as the frame.
    spec['loft'] = dict(
        source='src/structural-analysis-v6/cabinets.py',
        storage_density_pcf=CB.STORAGE_DENSITY,
        deck_top_z=CB.floor_top(f),
        items=[{k: r[k] for k in ('n', 'kind', 'what', 'w', 'd', 'h', 'x0', 'x1',
                                  'y0', 'y1', 'z0', 'top', 'weight', 'mount',
                                  'shape', 'clear_in', 'fits')}
               for r in CB.report(f)],
        walkway=[{k: t[k] for k in ('n', 'run', 'note', 'x0', 'x1', 'y0', 'y1')}
                 for t in CB.tiles(f)])

    dest = frame_models.allocate('beam-scheme')
    json_dump({'specification': spec, 'joint_graph': graph, 'model': model}, dest)
    print(f'\nwrote {dest.name}')

    # Save / reload round trip, the same check build_frame.py makes.
    rt = json_load(dest)
    assert rt['joint_graph'].number_of_nodes() == graph.number_of_nodes()
    assert rt['joint_graph'].number_of_edges() == graph.number_of_edges()
    saved = {el.name: el for el in rt['model'].elements()}
    assert set(saved) == set(spec['members']), 'element set differs from the spec'
    for mid, el in saved.items():
        a, b = [coord[n] for n in spec['members'][mid]['nodes']]
        assert max(abs(list(el.start)[i] - a[i]) for i in range(3)) < 1e-9
        assert max(abs(list(el.end)[i] - b[i]) for i in range(3)) < 1e-9
    print('round trip: nodes, edges and every member endpoint verified')

    g = framemod.load(dest)
    print(f'reloads as {len(g.members)} members, {len(g.segments)} segments, '
          f'{len(g.decks)} decks, {len(g.links)} links')


if __name__ == '__main__':
    main()
