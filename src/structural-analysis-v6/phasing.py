"""What can be erected before the existing roof comes off.

Two rules, and the second one is the owner's not the solver's:

* Anything that never touches the existing roof goes in. That is the whole new
  roof -- cap, rafters, clerestory and their bracing -- which clears the old
  hip by more than five feet, plus the outer beams and every joist outside the
  footprint.
* Every column goes in too, including the three the clash test flags. ``S3``,
  ``E-M1/B`` and ``E-M/B`` stand in or against the existing walls, where the hip
  is within an inch or two of the wall top, so each one needs a hole at the eave
  rather than an opening in the roof field.

What waits is the loft floor: the beams that cross the middle of the hip and the
joists between them.

Nothing here says the partial frame is stable while it stands alone -- that is
what ``standalone`` tests, and it is the question that decides whether this
sequence is buildable or merely drawable.
"""
from __future__ import annotations

import math

import existing as EX
import frame as framemod

ALWAYS_BUILD_GROUPS = ('Columns',)

#: A member whose deepest interference with the existing roof is no more than
#: this is treated as buildable. At the eave the hip is within an inch or two of
#: the wall top, so ``BEW``, ``B-S`` and the three ``BWI`` beams foul it by 1.0
#: to 1.8 in. -- a trimmed rafter tail and a patched edge, not an opening. This
#: is the same judgement the owner already made about the three columns that
#: stand in the walls.
TRIM_TOLERANCE = 3.0


def interference(frame: framemod.Frame, member: str) -> float:
    """How far this member's soffit sits below the existing roof, in inches."""
    sec = frame.section_of[member]
    half = max(sec.d, sec.b) / 2.0
    worst = 0.0
    for m, i, j in frame.segments:
        if m != member:
            continue
        a, b = frame.xyz(i), frame.xyz(j)
        n = max(2, int(math.dist(a, b) / 1.0))
        for k in range(n + 1):
            t = k / n
            px = a[0] + t * (b[0] - a[0])
            py = a[1] + t * (b[1] - a[1])
            pz = a[2] + t * (b[2] - a[2])
            if EX.inside(px, py):
                worst = max(worst, float(EX.roof_z(px, py)) - (pz - half))
    return worst


def clashes(frame: framemod.Frame, member: str) -> bool:
    """Does this member foul the existing roof by more than a trim?"""
    return interference(frame, member) > TRIM_TOLERANCE


def before_demo(frame: framemod.Frame, omit: set[str] = frozenset(),
                defer: set[str] = frozenset(),
                include: set[str] = frozenset()) -> dict:
    """Split the frame into what goes up first and what waits for the demolition.

    Clearing the roof is necessary but not sufficient. A member also has to have
    something to sit on: the first pass through this put four shelf joists in the
    early stage because they happen to fall west of the existing building, while
    both beams they span between were waiting for the demolition. They would have
    been hanging in the air, and the analysis said so -- unstable nodes at their
    ends. ``_prune`` drops anything that is not connected back to a foundation
    through other members of the same stage.
    """
    build, wait, penetrating = [], [], []
    for member in sorted(frame.members):
        if member in omit:
            continue
        if member in include:
            # An explicit erection decision can override the conservative clash
            # screen.  It still goes through the support-chain pruning below,
            # so an asserted member cannot remain floating by itself.
            build.append(member)
            if interference(frame, member) > 0:
                penetrating.append(member)
            continue
        if member in defer:
            # Held back by owner direction rather than by geometry.
            wait.append(member)
            continue
        depth = interference(frame, member)
        hits = depth > TRIM_TOLERANCE
        if frame.group(member) in ALWAYS_BUILD_GROUPS:
            build.append(member)
            if depth > 0:
                penetrating.append(member)
        elif 0 < depth <= TRIM_TOLERANCE:
            build.append(member)
            penetrating.append(member)
        elif hits:
            wait.append(member)
        else:
            build.append(member)

    kept, dropped = _prune(frame, set(build))
    return dict(build=sorted(kept), wait=sorted(set(wait) | dropped),
                penetrating=penetrating,
                unsupported=sorted(dropped))


def _prune(frame: framemod.Frame, build: set[str]) -> tuple[set[str], set[str]]:
    """Keep only members that reach a foundation and are held at both ends.

    Connectivity alone is not enough either. Two loft joists survived the first
    version because they reach ground through the north beam they sit on, while
    the beam at their other end was waiting -- each one a cantilever with its far
    end hanging in mid-air. The eigenvalue solver found them before a drawing
    would have. So a member is also dropped if either end has nothing else in
    this stage attached to it.
    """
    original = set(build)
    build = set(build)
    while True:
        dangling = {m for m in build if _has_free_end(frame, m, build)}
        if not dangling:
            break
        build -= dangling
    edges = {}
    for m, i, j in frame.segments:
        if m in build:
            edges.setdefault(i, set()).add(m)
            edges.setdefault(j, set()).add(m)
    seen: set[str] = set()
    stack = [m for n in frame.supports for m in edges.get(n, ())]
    while stack:
        member = stack.pop()
        if member in seen:
            continue
        seen.add(member)
        for mm, i, j in frame.segments:
            if mm != member:
                continue
            for node in (i, j):
                stack.extend(x for x in edges.get(node, ()) if x not in seen)
    # Everything the cascade shed has to come back as "waits", not disappear.
    # An earlier version returned only what the connectivity walk rejected, so
    # members dropped for dangling ends were in neither list -- and therefore
    # were never omitted from the model either. They stayed in the analysis with
    # their supports gone, which is exactly the mechanism this is meant to stop.
    return seen, original - seen


def _has_free_end(frame: framemod.Frame, member: str, build: set[str]) -> bool:
    """True if this member is not held by enough of the rest of the stage.

    The test counts attachment points along the whole member, not just its two
    extreme ends. An earlier version looked only at the ends and pruned column
    S1, whose top carries nothing now that R-SO is gone but which is tied to
    B-SO seven inches below it -- a post with a short stub above its connection,
    not a floating member.

    Two attachment points hold a member. One holds it only if that point is a
    foundation, which makes it a cantilever off the ground rather than a piece
    hanging in the air; whether such a post then stands on its own is a question
    for the stability solver, not for this rule.
    """
    segs = framemod._ordered(frame, [(i, j) for m, i, j in frame.segments
                                     if m == member])
    if not segs:
        return True
    linked = _link_partners(frame)
    nodes = [segs[0][0]] + [j for _, j in segs]
    held, grounded = 0, False
    for node in nodes:
        if frame.nodes[node].get('support'):
            held += 1
            grounded = True
            continue
        others = {m for m in frame.nodes[node].get('members', [])
                  if m != member and m in build}
        for partner in linked.get(node, ()):
            others |= {m for m in frame.nodes[partner].get('members', [])
                       if m != member and m in build}
        if others:
            held += 1
    if held >= 2:
        return False
    return not (held == 1 and grounded)


def _link_partners(frame: framemod.Frame) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for i, j, _ in getattr(frame, 'links', ()):
        out.setdefault(i, set()).add(j)
        out.setdefault(j, set()).add(i)
    return out
