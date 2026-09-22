"""Secondary framing added to complete the load path, as a stated assumption.

The canonical frame model is a primary-structure geometry model: STR-006 records
that it excludes secondary framing, and the open-items register raises the same
omission for the wall girts (ENV-OI-04).  For the walls that omission costs
nothing here, because wall pressure is delivered to the primary frame either way.
For the flat upper roof it is fatal to the analysis: the roof is 20.5 ft by 15.2 ft
and nothing crosses it, so its load can only reach the perimeter, and its southern
edge at the head of the clerestory has no beam at all.

Analysing that literally answers a question nobody asked -- it measures a roof
with no roof framing.  So the run is done twice:

``as_drawn``
    Exactly the members in the COMPAS model.  This is what reports the gap.

``completed``
    Plus the minimum secondary framing that gives the upper roof a load path: a
    clerestory head beam and four purlins.  Every added member is tagged to the
    ``Assumed`` groups so it is visibly an assumption of this analysis and not
    part of the frame model.  Sizing and removal recommendations are drawn from
    this scenario, because it is the only one that represents a structure that
    stands up.

Nothing here is written back to ``frame-models/``.  Promoting any of it is a
design decision for the engineer of record, not an output of this script.
"""
from __future__ import annotations

import copy

import frame as framemod
import sections

HEAD_SECTION = 'HSS6X6X1/4'
PURLIN_SECTION = 'HSS3X3X1/8'
N_PURLIN_BAYS = 5          # four interior purlins between the two roof edges


def completed(base: framemod.Frame, params: dict) -> framemod.Frame:
    """Return a copy of the frame with any missing roof framing added.

    Only the connected-frame lineage needs it.  The beam scheme already carries
    flat rafters across its upper roof and a clerestory head, so there is nothing
    to complete and the frame comes back untouched -- which is itself a finding
    worth recording when the two schemes are compared.
    """
    if not base.schema.startswith('garage.connected-frame'):
        return copy.deepcopy(base)
    needed = ('west_x', 'east_x', 'south_y', 'north_y', 'clerestory_y',
              'bottom_z', 'square_top_z')
    missing = [k for k in needed if k not in params]
    if missing:
        raise ValueError(
            f'this completion is written for the square-upper-west geometry and '
            f'the model is missing {missing}. Another lineage needs its own '
            f'completion, not this one applied to it.')
    f = copy.deepcopy(base)
    wx, ex = params['west_x'], params['east_x']
    cy, ny, tz = params['clerestory_y'], params['north_y'], params['square_top_z']

    _add_member(f, 'A.clerestory.head', 'W.front.top', 'E.front.top',
                HEAD_SECTION, 6.0, 6.0, 'AssumedRoofBeam',
                note='assumed head beam closing the top of the clerestory')

    north = _north_chord(f, ny, tz)
    for k in range(1, N_PURLIN_BAYS):
        x = wx + (ex - wx) * k / N_PURLIN_BAYS
        a = _split(f, 'A.clerestory.head', (x, cy, tz), f'A.head@{k}')
        b = _split(f, north, (x, ny, _z_on(f, north, x)), f'A.tn@{k}')
        _add_member(f, f'A.purlin.{k}', a, b, PURLIN_SECTION, 3.0, 3.0,
                    'AssumedRoofPurlin',
                    note='assumed upper-roof purlin spanning to the north chord')
    return f


def added_members(f: framemod.Frame) -> list[str]:
    return [m for m in f.members if f.group(m).startswith('Assumed')]


# ---------------------------------------------------------------------------

def _north_chord(f: framemod.Frame, ny: float, tz: float) -> str:
    """The north wall's topmost east-west chord, which the purlins land on."""
    best, best_z = None, -1e9
    for m in f.members:
        if f.group(m).startswith('Assumed'):
            continue
        pts = [f.xyz(n) for mm, i, j in f.segments if mm == m for n in (i, j)]
        if not pts or any(abs(p[1] - ny) > 1.0 for p in pts):
            continue
        if max(p[0] for p in pts) - min(p[0] for p in pts) < 100.0:
            continue
        z = sum(p[2] for p in pts) / len(pts)
        if tz - 40.0 < z > best_z:
            best, best_z = m, z
    if best is None:
        raise ValueError('no north upper chord found')
    return best


def _z_on(f: framemod.Frame, member: str, x: float) -> float:
    segs = [(i, j) for m, i, j in f.segments if m == member]
    pts = sorted({f.xyz(n) for s in segs for n in s})
    a, b = pts[0], pts[-1]
    t = (x - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0.0
    return a[2] + t * (b[2] - a[2])


def _add_member(f: framemod.Frame, name: str, a: str, b: str, section_ref: str,
                w: float, d: float, group: str, material: str = 'steel',
                note: str = '') -> None:
    f.members[name] = dict(nodes=[a, b], width=w, depth=d, group=group,
                           material=material, source_name=name,
                           section_reference=section_ref,
                           section_status=f'assumed by structural analysis: {note}')
    f.section_of[name] = framemod.resolve_section(f.members[name])
    f.segments.append((name, a, b))
    for n in (a, b):
        f.nodes[n].setdefault('members', [])
        if name not in f.nodes[n]['members']:
            f.nodes[n]['members'].append(name)


def _split(f: framemod.Frame, member: str, xyz, name: str) -> str:
    """Insert a node into ``member`` at ``xyz`` and split the segment there."""
    for n, v in f.nodes.items():
        if abs(v['x'] - xyz[0]) < 0.5 and abs(v['y'] - xyz[1]) < 0.5 \
           and abs(v['z'] - xyz[2]) < 0.5 and member in v.get('members', []):
            return n
    target = None
    for k, (m, i, j) in enumerate(f.segments):
        if m != member:
            continue
        a, b = f.xyz(i), f.xyz(j)
        if _between(a, b, xyz):
            target = (k, i, j)
            break
    if target is None:
        raise ValueError(f'{xyz} is not on {member}')
    k, i, j = target
    f.nodes[name] = dict(x=xyz[0], y=xyz[1], z=xyz[2], support=False,
                         free_end=False, members=[member])
    f.segments[k] = (member, i, name)
    f.segments.insert(k + 1, (member, name, j))
    return name


def _between(a, b, p, tol: float = 0.75) -> bool:
    ab = [b[k] - a[k] for k in range(3)]
    ap = [p[k] - a[k] for k in range(3)]
    L2 = sum(c * c for c in ab)
    if L2 < 1e-9:
        return False
    t = sum(ab[k] * ap[k] for k in range(3)) / L2
    if not (-1e-6 <= t <= 1.0 + 1e-6):
        return False
    return all(abs(a[k] + t * ab[k] - p[k]) < tol for k in range(3))


# ---------------------------------------------------------------------------
# crossing joints
# ---------------------------------------------------------------------------

def crossing_joints(base: framemod.Frame, tol: float = 1.5
                    ) -> tuple[framemod.Frame, list[dict]]:
    """Connect X-braces where they cross, and report what that changes.

    Six pairs of braces in this frame form an X and pass within a couple of
    inches of each other at mid-length, but the geometry model records the
    crossing as incidental -- the migration notes say so explicitly for the north
    diagonals.  Left unconnected, each brace is unbraced over its whole length,
    which is what drives the slenderness of the roof cap braces.

    Bolting or welding the crossings halves every one of those unbraced lengths.
    It is the cheapest change available to this frame, so it is analysed as its
    own scenario rather than assumed into the baseline.
    """
    f = copy.deepcopy(base)
    found: list[dict] = []
    names = sorted(f.members)
    for a_i in range(len(names)):
        for b_i in range(a_i + 1, len(names)):
            a, b = names[a_i], names[b_i]
            hit = _crossing(f, a, b, tol)
            if hit is None:
                continue
            node = f'X.{len(found) + 1}'
            before = {m: _longest_run(f, m) for m in (a, b)}
            _split(f, a, hit, node)
            _attach(f, b, hit, node)
            found.append(dict(node=node, members=[a, b],
                              at=[round(v, 2) for v in hit],
                              unbraced_before={m: round(v, 1) for m, v in before.items()},
                              unbraced_after={m: round(_longest_run(f, m), 1)
                                              for m in (a, b)}))
    return f, found


def _crossing(f: framemod.Frame, a: str, b: str, tol: float):
    """Midpoint of the shortest link between two members, if they nearly touch."""
    if f.group(a) != f.group(b):
        return None
    linked = {frozenset((i, j)) for i, j, _ in f.links}
    a_nodes = {n for m, i, j in f.segments if m == a for n in (i, j)}
    b_nodes = {n for m, i, j in f.segments if m == b for n in (i, j)}
    if any(pair <= (a_nodes | b_nodes) and pair & a_nodes and pair & b_nodes
           for pair in linked):
        return None                       # already joined by a declared connection
    best = None
    for ma, ia, ja in f.segments:
        if ma != a:
            continue
        p1, p2 = f.xyz(ia), f.xyz(ja)
        for mb, ib, jb in f.segments:
            if mb != b:
                continue
            if {ia, ja} & {ib, jb}:
                return None               # they already share a joint
            q1, q2 = f.xyz(ib), f.xyz(jb)
            d, mid = _closest(p1, p2, q1, q2)
            if d < tol and (best is None or d < best[0]):
                best = (d, mid)
    return best[1] if best else None


def _closest(p1, p2, q1, q2):
    """Distance between two segments and the midpoint of their common normal."""
    u = [p2[k] - p1[k] for k in range(3)]
    v = [q2[k] - q1[k] for k in range(3)]
    w = [p1[k] - q1[k] for k in range(3)]
    a = sum(x * x for x in u)
    b = sum(u[k] * v[k] for k in range(3))
    c = sum(x * x for x in v)
    d = sum(u[k] * w[k] for k in range(3))
    e = sum(v[k] * w[k] for k in range(3))
    den = a * c - b * b
    if abs(den) < 1e-9:
        return 1e9, None
    s = max(0.0, min(1.0, (b * e - c * d) / den))
    t = max(0.0, min(1.0, (a * e - b * d) / den))
    pa = [p1[k] + s * u[k] for k in range(3)]
    qa = [q1[k] + t * v[k] for k in range(3)]
    dist = sum((pa[k] - qa[k]) ** 2 for k in range(3)) ** 0.5
    return dist, tuple((pa[k] + qa[k]) / 2.0 for k in range(3))


def _attach(f: framemod.Frame, member: str, xyz, node: str) -> None:
    """Move the member's nearest split point onto an existing node."""
    for k, (m, i, j) in enumerate(list(f.segments)):
        if m != member:
            continue
        a, b = f.xyz(i), f.xyz(j)
        if _between(a, b, xyz, tol=2.5):
            f.segments[k] = (member, i, node)
            f.segments.insert(k + 1, (member, node, j))
            if member not in f.nodes[node]['members']:
                f.nodes[node]['members'].append(member)
            return
    raise ValueError(f'{xyz} is not on {member}')


def _longest_run(f: framemod.Frame, member: str) -> float:
    import analysis
    return analysis.unbraced_lengths(f).get(member, 0.0)
