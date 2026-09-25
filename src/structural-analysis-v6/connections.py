"""Physical connections: join members that touch, and schedule every joint.

The analytical frame joins members only where the geometry model declares a
shared node or an offset link. A few members were drawn so that they touch, or
pass straight through one another, without any such joint -- a brace running
through a beam web, a solar rafter seat landing on a column stub, two X-braces
crossing at mid-length. On the drawings those read as members that should be
welded or bolted together and are not.

``connect`` applies one rule to the current frame: if the end of a member is in
contact with another member, or two members cross through each other, they are
connected. Ends are joined with a short rigid link to the nearest point on the
other member; crossings get a shared node. Pin-group members (braces, rafters,
joists) passing through a new crossing node are released there, so a bolted
gusset does not quietly become a moment connection.

``schedule`` then lists every physical joint -- a node, together with any nodes
linked to it -- and says what kind of connection the analysis assumes there:

``welded``  every attaching member end is moment-continuous in the solver.
``pinned``  every attaching member end is released: bolted gusset, seat, clip
            or hanger.
``mixed``   a moment-continuous joint with pinned attachments on it, such as a
            welded beam-column joint that also receives a bolted brace.
``base``    a pinned column base on a foundation.

"Welded" is what the solver assumes, not a designed weld; see the amber
members in the moment-frame view for joints whose lateral role is unassigned.
"""
from __future__ import annotations

import math

import completion as C
import frame as framemod

#: An end is "in contact" when its section reaches within this many inches of
#: another member's solid.
END_TOL = 0.5
#: Two centerlines passing within this distance of each other cross.
CROSS_TOL = 1.5
#: Two members that already bear on a common carrier within this distance of
#: the contact point are joined through that carrier (two joists hung back to
#: back on one beam, two roof beams capped on one column).
CARRIER_TOL = 4.5

KINDS = {
    'welded': ('#c83e4d', 'Welded — moment-continuous'),
    'mixed': ('#8e44ad', 'Welded joint with pinned attachments'),
    'pinned': ('#377eb8', 'Pinned — bolted, seated or hung'),
    'base': ('#22262b', 'Pinned base — anchor rods'),
}


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------

def _sub(a, b):
    return [a[k] - b[k] for k in range(3)]


def _dot(a, b):
    return sum(a[k] * b[k] for k in range(3))


def _point_on_segment(p, a, b):
    ab = _sub(b, a)
    L2 = _dot(ab, ab) or 1e-12
    t = max(0.0, min(1.0, _dot(_sub(p, a), ab) / L2))
    q = [a[k] + t * ab[k] for k in range(3)]
    return math.dist(p, q), t, q


def _box_distance(p, a, b, sec) -> float:
    """Distance from a point to the solid prism drawn for one member segment."""
    import solid_view as SV
    ex, ey, ez = SV._axes(a, b)
    v = _sub(p, a)
    L = math.dist(a, b)
    u = (_dot(v, ex), _dot(v, ey), _dot(v, ez))
    dx = max(0.0, -u[0], u[0] - L)
    dy = max(0.0, abs(u[1]) - sec.b / 2)
    dz = max(0.0, abs(u[2]) - sec.d / 2)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def _segment_closest(p1, p2, q1, q2):
    """Distance, parameters and points of closest approach of two segments."""
    d1, d2, r = _sub(p2, p1), _sub(q2, q1), _sub(p1, q1)
    a, e, f = _dot(d1, d1), _dot(d2, d2), _dot(d2, r)
    c, b = _dot(d1, r), _dot(d1, d2)
    den = a * e - b * b
    s = max(0.0, min(1.0, (b * f - c * e) / den)) if den > 1e-9 else 0.0
    t = (b * s + f) / e
    if t < 0:
        t, s = 0.0, max(0.0, min(1.0, -c / a))
    elif t > 1:
        t, s = 1.0, max(0.0, min(1.0, (b - c) / a))
    c1 = [p1[k] + s * d1[k] for k in range(3)]
    c2 = [q1[k] + t * d2[k] for k in range(3)]
    return math.dist(c1, c2), c1, c2


# --------------------------------------------------------------------------
# topology
# --------------------------------------------------------------------------

def _clusters(f: framemod.Frame) -> dict[str, int]:
    """Node -> joint id, merging nodes tied together by offset links."""
    parent = {n: n for n in f.nodes}

    def find(n):
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n
    for i, j, _ in f.links:
        if i in parent and j in parent:
            parent[find(i)] = find(j)
    roots = {}
    return {n: roots.setdefault(find(n), len(roots)) for n in f.nodes}


def _member_nodes(f):
    out = {}
    for m, i, j in f.segments:
        out.setdefault(m, set()).update((i, j))
    return out


def _joined(f, cluster, member_nodes, a, b) -> bool:
    ca = {cluster[n] for n in member_nodes[a]}
    return bool(ca & {cluster[n] for n in member_nodes[b]})


def _ends(f, member):
    segs = framemod._ordered(f, [(i, j) for m, i, j in f.segments if m == member])
    return segs[0][0], segs[-1][1]


def _share_carrier(f, member_nodes, a, b, point) -> bool:
    """Do a and b both attach to some third member close to ``point``?"""
    def carriers(m):
        return {c for n in member_nodes[m] if math.dist(f.xyz(n), point) <= CARRIER_TOL
                for c in f.nodes[n].get('members', ()) if c not in (a, b)}
    return bool(carriers(a) & carriers(b))


def _segment_near(f, member, point):
    best = None
    for m, i, j in f.segments:
        if m != member:
            continue
        d, t, q = _point_on_segment(point, f.xyz(i), f.xyz(j))
        if best is None or d < best[0]:
            best = (d, q)
    return best[1]


def _node_at(f, member, point, name):
    """An existing node of ``member`` within 2 in. of point, or a new split."""
    own = [n for m, i, j in f.segments if m == member for n in (i, j)]
    close = min(own, key=lambda n: math.dist(f.xyz(n), point))
    if math.dist(f.xyz(close), point) <= 2.0:
        return close
    return C._split(f, member, tuple(point), name)


# --------------------------------------------------------------------------
# connecting
# --------------------------------------------------------------------------

def find_contacts(f: framemod.Frame) -> tuple[list, list]:
    """Unjoined end contacts and centerline crossings in the current frame."""
    cluster = _clusters(f)
    member_nodes = _member_nodes(f)
    members = sorted(f.members)
    ends, crosses = [], []
    for m in members:
        if f.group(m) == 'Joists':
            continue            # hung in hangers; every joist end already bears
        sec = f.section_of[m]
        for n in _ends(f, m):
            p = f.xyz(n)
            for o in members:
                if o == m or _joined(f, cluster, member_nodes, m, o):
                    continue
                so = f.section_of[o]
                d = min(_box_distance(p, f.xyz(i), f.xyz(j), so)
                        for oo, i, j in f.segments if oo == o)
                if d - min(sec.b, sec.d) / 2 > END_TOL:
                    continue
                if _share_carrier(f, member_nodes, m, o, p):
                    continue
                ends.append(dict(member=m, node=n, other=o, at=p,
                                 gap=round(d - min(sec.b, sec.d) / 2, 2)))
    for x, a in enumerate(members):
        for b in members[x + 1:]:
            if {f.group(a), f.group(b)} == {'Joists'}:
                continue
            if _joined(f, cluster, member_nodes, a, b):
                continue
            best = None
            for _, i, j in [s for s in f.segments if s[0] == a]:
                for _, k, l in [s for s in f.segments if s[0] == b]:
                    r = _segment_closest(f.xyz(i), f.xyz(j), f.xyz(k), f.xyz(l))
                    if best is None or r[0] < best[0]:
                        best = r
            if best is None or best[0] > CROSS_TOL:
                continue
            mid = [(best[1][k] + best[2][k]) / 2 for k in range(3)]
            # A crossing near either member's end is an end contact, not a
            # crossing; those are handled above.
            if any(math.dist(mid, f.xyz(e)) < 3.0 for mm in (a, b) for e in _ends(f, mm)):
                continue
            crosses.append(dict(members=[a, b], at=mid, gap=round(best[0], 2)))
    return ends, crosses


def connect(f: framemod.Frame) -> list[dict]:
    """Join every touching-but-unjoined pair in place; return what was added."""
    added = []
    ends, crosses = find_contacts(f)
    member_nodes = _member_nodes(f)
    for k, c in enumerate(crosses):
        a, b = c['members']
        node = f'JOIN.X{k + 1}'
        # One shared node: split the first member there (or reuse a node of
        # its own within 2 in.) and thread the second member through it.
        na = _node_at(f, a, c['at'], node)
        if na not in {n for s in f.segments if s[0] == b for n in s[1:]}:
            C._attach(f, b, f.xyz(na), na)
        nb = na
        pins = [m for m in (a, b) if f.group(m) in framemod.PIN_ENDED_GROUPS]
        # Release pin-group members at the crossing. If both are, keep one
        # continuous so the joint still has rotational stiffness.
        if len(pins) == 2:
            pins = pins[1:]
        for m in pins:
            f.pinned_ends.append((m, na if m == a else nb))
        added.append(dict(kind='crossing', members=[a, b],
                          at=[round(v, 2) for v in c['at']],
                          released=pins, gap=c['gap'], nodes=[na]))
    # End contacts: link the end to the nearest point of the other member,
    # once per pair of joints.
    done = set()
    for k, c in enumerate(ends):
        cluster = _clusters(f)
        member_nodes = _member_nodes(f)
        if _joined(f, cluster, member_nodes, c['member'], c['other']):
            continue
        q = _segment_near(f, c['other'], c['at'])
        target = _node_at(f, c['other'], q, f'JOIN.E{k + 1}')
        pair = frozenset((c['node'], target))
        if pair in done:
            continue
        done.add(pair)
        f.links.append((c['node'], target,
                        f'contact joint: {c["member"]} end on {c["other"]}'))
        added.append(dict(kind='end contact', members=[c['member'], c['other']],
                          at=[round(v, 2) for v in c['at']], gap=c['gap'],
                          nodes=[c['node'], target],
                          length=round(math.dist(f.xyz(c['node']), f.xyz(target)), 2)))
    for n, v in f.nodes.items():
        v['members'] = sorted({m for m, i, j in f.segments if n in (i, j)})
    return added


# --------------------------------------------------------------------------
# the schedule
# --------------------------------------------------------------------------

def schedule(f: framemod.Frame, added: list | None = None) -> list[dict]:
    """One row per physical joint, with the connection the analysis assumes."""
    cluster = _clusters(f)
    groups: dict[int, list[str]] = {}
    for n, c in cluster.items():
        groups.setdefault(c, []).append(n)
    ends = {m: _ends(f, m) for m in f.members}
    pinned = set(map(tuple, f.pinned_ends))
    added_nodes = {n for a in added or [] for n in a['nodes']}
    rows = []
    for c, nodes in groups.items():
        attach = []
        for n in nodes:
            for m in f.nodes[n].get('members', ()):
                if m not in f.members:
                    continue
                at_end = n in ends[m]
                released = (m, n) in pinned or (
                    at_end and f.group(m) in framemod.PIN_ENDED_GROUPS)
                attach.append(dict(member=m, node=n, end=at_end, released=released))
        members = {a['member'] for a in attach}
        support = any(f.nodes[n].get('support') for n in nodes)
        if len(members) < 2 and not support:
            continue
        if support:
            kind = 'base'
        else:
            # A member running through the joint is continuous and is not the
            # connection; the attaching ends (and any released run) are.
            conn = [a for a in attach if a['end'] or a['released']]
            if not conn:
                conn = attach
            free = [a for a in conn if a['released']]
            kind = ('pinned' if len(free) == len(conn)
                    else 'welded' if not free else 'mixed')
        pts = [f.xyz(n) for n in nodes if f.nodes[n].get('members')] or \
              [f.xyz(n) for n in nodes]
        # Put the dot at the node where the most members meet.
        at = max(nodes, key=lambda n: len(f.nodes[n].get('members', ())))
        xyz = f.xyz(at)
        rows.append(dict(
            joint=at, kind=kind, at=[round(v, 2) for v in xyz],
            members=sorted(members),
            detail=[f'{a["member"]} {"end" if a["end"] else "through"}'
                    f'{" — pinned" if a["released"] else ""}' for a in attach],
            added=bool(added_nodes.intersection(nodes)),
            spread=round(max(math.dist(a, b) for a in pts for b in pts), 2)))
    rows.sort(key=lambda r: (r['kind'], r['at']))
    return rows
