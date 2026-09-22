"""Owner-directed corrections to the BEAM-001 cost-reduction recommendation.

Reviewing the removable set, the owner ruled four of them back in and directed
one change the analysis had not seen. Each is recorded here rather than folded
silently into the study, so the reasoning stays attached to the geometry.

**Kept, against the analysis.** ``BW`` reads as redundant because nothing frames
into it, but it is the west edge of the structure and part of the design intent.
``RE-S`` and ``RE-N`` carry no frame load but do carry roof panel and the purlins
spanning between them -- secondary framing that is not in the model, which is the
same blind spot that produced the joist error. ``RF @ 170.58`` is structurally
removable and stays for symmetry: a roof with one rafter missing for reasons
nobody can reconstruct is a defect, not a saving.

**R-SO deleted, B-SO raised.** The analysis wanted R-SO enlarged. It is the south
eave, an HSS3-1/2X3-1/2X1/8 carrying the whole solar slope, and it sits 12.5 in.
above B-SO -- a W12X16 running the same line and carrying nothing at all, because
the decks begin at y = 3 and no joist frames into it. Raising B-SO onto the eave
line deletes a member and resolves the overload with steel that is already bought:
W12X16 has seven times the plastic modulus and twenty-five times the stiffness of
the tube it replaces. Its new line is the tops of SW0, S1 and S2, which already
stand at z = 117, so the columns are unchanged.
"""
from __future__ import annotations

import copy

import completion
import frame as framemod
import sections

#: Removable by analysis, retained by owner direction, with the reason.
PROTECTED = {
    'BW': 'west edge of the structure; design intent, not a load path',
    'RE-S': 'carries roof panel and the purlins spanning to RE-M1',
    'RE-N': 'carries roof panel and the purlins spanning to RE-M',
    'RF @ 170.58': 'retained for symmetry of the rafter set',
}

EAVE_MEMBER = 'R-SO'
RAISED_BEAM = 'B-SO'

#: Held out of the pre-demolition stage by owner direction, not by geometry.
#:
#: ``B-S`` and ``BEW`` foul the existing eave by 1.6 and 1.0 in. and would
#: otherwise qualify as a trim. The owner has ruled them out of the early stage.
#:
#: The four east posts follow them, and that is arithmetic rather than a second
#: decision: ``BEW`` is the only thing tying their tops north-to-south. The
#: raking ``RE-`` rafters hold them east-west and nothing holds them the other
#: way, so with ``BEW`` deferred each one is a pinned-base cantilever with a free
#: top and the stage is a mechanism. A post cannot be stood and left untied.
DEFER_BEFORE_DEMO = {
    'B-S': 'owner direction',
    'BEW': 'owner direction',
    'E-S': 'tied only by BEW; follows it',
    'E-N': 'tied only by BEW; follows it',
    'E-M/B': 'tied only by BEW; follows it',
    'E-M1/B': 'tied only by BEW; follows it',
}


def raise_south_beam(base: framemod.Frame) -> tuple[framemod.Frame, dict]:
    """Delete the eave tube and run the south floor beam along its line instead."""
    f = copy.deepcopy(base)
    if EAVE_MEMBER not in f.members or RAISED_BEAM not in f.members:
        return f, {'applied': False, 'reason': 'members not present in this lineage'}

    eave_chain = _chain(f, EAVE_MEMBER)
    before = dict(
        eave_section=f.section_of[EAVE_MEMBER].name,
        eave_z=round(f.nodes[eave_chain[0]]['z'], 1),
        beam_section=f.section_of[RAISED_BEAM].name,
        beam_z=round(f.nodes[_chain(f, RAISED_BEAM)[0]]['z'], 1),
        beam_nodes=len(_chain(f, RAISED_BEAM)))

    spec = dict(f.members[RAISED_BEAM])
    for member in (EAVE_MEMBER, RAISED_BEAM):
        _drop(f, member)

    f.members[RAISED_BEAM] = spec
    f.section_of[RAISED_BEAM] = framemod.resolve_section(spec)
    for a, b in zip(eave_chain, eave_chain[1:]):
        f.segments.append((RAISED_BEAM, a, b))
    for node in eave_chain:
        f.nodes[node].setdefault('members', [])
        if RAISED_BEAM not in f.nodes[node]['members']:
            f.nodes[node]['members'].append(RAISED_BEAM)

    return f, dict(applied=True, before=before,
                   after=dict(beam_section=spec['section_reference'],
                              beam_z=round(f.nodes[eave_chain[0]]['z'], 1),
                              beam_nodes=len(eave_chain)),
                   deleted=EAVE_MEMBER)


def _chain(f: framemod.Frame, member: str) -> list[str]:
    segs = framemod._ordered(f, [(i, j) for m, i, j in f.segments if m == member])
    return [segs[0][0]] + [j for _, j in segs] if segs else []


def _drop(f: framemod.Frame, member: str) -> None:
    f.members.pop(member, None)
    f.section_of.pop(member, None)
    f.segments[:] = [t for t in f.segments if t[0] != member]
    for v in f.nodes.values():
        if member in v.get('members', []):
            v['members'] = [m for m in v['members'] if m != member]


# ---------------------------------------------------------------------------
# the upper east beam
# ---------------------------------------------------------------------------

UPPER_EAST = 'BE.upper'


def add_upper_east_beam(base: framemod.Frame, section: str = 'W12X16'
                        ) -> tuple[framemod.Frame, dict]:
    """Run an east beam at R-W1's level and land the east verticals on it.

    Owner proposal, and it solves a problem the phasing study had run into rather
    than merely adding a member. ``E.clerestory`` and ``E.W3`` both start on the
    floor grillage at z = 104.5, which is below the existing roof, so both wait
    for the demolition -- and with them go ``CT.top`` and ``R-W3``, which have
    nothing to land on at their east ends without them. Four members of the new
    roof were stuck behind the old roof for want of a support.

    A beam at z = 147.355, the same axis as ``R-W1``, spans S3 to N2 along
    x = 211.5. The existing hip reaches only 116.78 in. on that line, so the
    beam's soffit clears it by just under two feet, and the two east verticals
    can start from it instead of from the floor.
    """
    import completion
    f = copy.deepcopy(base)
    z = _rw1_level(f)
    x = _east_line(f)
    stations = [3.0, 71.0, 185.0, 268.0]

    nodes = []
    for y in stations:
        host = _member_at(f, x, y, z)
        if host is None:
            return f, {'applied': False, 'reason': f'nothing to land on at y={y}'}
        nodes.append(completion._split(f, host, (x, y, z), f'{UPPER_EAST}@{y:g}'))

    spec = dict(f.members['BE'])
    spec.update(section_reference=section, width=3.99, depth=12.0,
                group='Beams', source_name=UPPER_EAST,
                section_status='owner proposal: east beam at the R-W1 level so the '
                               'east verticals clear the existing roof')
    f.members[UPPER_EAST] = spec
    f.section_of[UPPER_EAST] = framemod.resolve_section(spec)
    for a, b in zip(nodes, nodes[1:]):
        f.segments.append((UPPER_EAST, a, b))
    for n in nodes:
        f.nodes[n].setdefault('members', [])
        if UPPER_EAST not in f.nodes[n]['members']:
            f.nodes[n]['members'].append(UPPER_EAST)

    shortened = []
    for member in ('E.clerestory', 'E.W3'):
        if _truncate_below(f, member, z):
            shortened.append(member)

    return f, dict(applied=True, level_z=round(z, 3), east_x=x,
                   span_in=round(stations[-1] - stations[0], 1),
                   section=section, landed_on=nodes,
                   shortened=shortened,
                   roof_below_max=round(float(__import__('existing').roof_z(x, 125.0)), 2))


def _rw1_level(f: framemod.Frame) -> float:
    zs = [f.xyz(n)[2] for m, i, j in f.segments if m == 'R-W1' for n in (i, j)]
    return sum(zs) / len(zs)


def _east_line(f: framemod.Frame) -> float:
    zs = [f.xyz(n)[0] for m, i, j in f.segments if m == 'BE' for n in (i, j)]
    return max(set(zs), key=zs.count)


def _member_at(f: framemod.Frame, x: float, y: float, z: float) -> str | None:
    """A member whose axis passes through this point, preferring a column."""
    import completion
    best = None
    for member in f.members:
        for m, i, j in f.segments:
            if m != member:
                continue
            if completion._between(f.xyz(i), f.xyz(j), (x, y, z), tol=1.0):
                if f.group(member) == 'Columns':
                    return member
                best = best or member
    return best


def _truncate_below(f: framemod.Frame, member: str, z: float) -> bool:
    """Cut a vertical member off below ``z`` and drop the part underneath."""
    import completion
    pts = [f.xyz(n) for m, i, j in f.segments if m == member for n in (i, j)]
    if not pts or min(p[2] for p in pts) >= z - 0.01:
        return False
    x, y = pts[0][0], pts[0][1]
    node = completion._split(f, member, (x, y, z), f'{member}@{z:.3f}')
    keep = [(m, i, j) for m, i, j in f.segments
            if m != member or min(f.xyz(i)[2], f.xyz(j)[2]) >= z - 0.01]
    f.segments[:] = keep
    for v in f.nodes.values():
        if member in v.get('members', []) and v['z'] < z - 0.01:
            v['members'] = [q for q in v['members'] if q != member]
    return True


# ---------------------------------------------------------------------------
# the south eave, second revision
# ---------------------------------------------------------------------------

SLOPE_DROP = 4.75


def seat_slope_on_south_beam(base: framemod.Frame) -> tuple[framemod.Frame, dict]:
    """Delete R-SO, leave B-SO at floor level, and sit the slope on top of it.

    Supersedes ``raise_south_beam``. That version put B-SO's *axis* where R-SO's
    axis had been, which is wrong by half a beam: R-SO was a 3-1/2 in. tube and
    B-SO is twelve inches deep, so the slope rafters ran through the middle of it
    rather than over it, and the beam stood proud of the floor plane for no
    reason. B-SO belongs at 104.5 with BW and the rest of the grillage.

    So the slope comes down to meet it instead. The rafters bear on the top
    flange at 110.5, which puts their axis at 112.25 -- a 4.75 in. drop, with the
    30 degree plane preserved, so the clerestory grows from 30.9 to 35.6 in. and
    the solar array keeps both its angle and its area.

    The five rafters that land between columns are tied down to B-SO by short
    bearing links, the same device the model already uses where the optional east
    column meets E-OB. Seven and three quarter inches from beam axis to rafter
    axis is not a gap; it is half of each section.
    """
    f = copy.deepcopy(base)
    if EAVE_MEMBER not in f.members:
        return f, {'applied': False, 'reason': f'{EAVE_MEMBER} is not in this model'}

    eave_chain = _chain(f, EAVE_MEMBER)
    eave_y = f.xyz(eave_chain[0])[1]
    old_eave_z = f.xyz(eave_chain[0])[2]
    _drop(f, EAVE_MEMBER)

    # bring the whole 30-degree plane down, hinging about nothing -- it is a
    # rigid translation, so the angle is untouched
    moved = 0
    for name, v in f.nodes.items():
        if _on_slope(f, v, old_eave_z, eave_y):
            v['z'] -= SLOPE_DROP
            moved += 1

    import completion
    links = []
    for node in eave_chain:
        v = f.nodes[node]
        if not v.get('members'):
            continue
        host = _member_at(f, v['x'], v['y'], 104.5)
        if host is None:
            continue
        seat = completion._split(f, host, (v['x'], v['y'], 104.5),
                                 f'B-SO.seat@{v["x"]:.4g}')
        if seat == node:
            continue
        # A column already ties its own top to the beam it passes through, so a
        # link there would be a second rigid path between the same two points.
        if set(f.nodes[node].get('members', ())) & set(f.nodes[seat].get('members', ())):
            continue
        f.links.append((node, seat, 'rafter bearing on the beam top flange'))
        links.append((node, seat))

    return f, dict(applied=True, deleted=EAVE_MEMBER,
                   slope_drop_in=SLOPE_DROP,
                   eave_axis_z=round(old_eave_z - SLOPE_DROP, 2),
                   beam_axis_z=104.5, nodes_moved=moved,
                   bearing_links=len(links))


def _on_slope(f, v, eave_z: float, eave_y: float) -> bool:
    """Is this node on the south solar plane, at or above the eave line?"""
    if v['y'] > 72.0 or v['y'] < eave_y - 0.5:
        return False
    # the plane runs from (eave_y, eave_z) at 30 degrees
    z_here = eave_z + 0.57735 * (v['y'] - eave_y)
    return abs(v['z'] - z_here) < 0.6


# ---------------------------------------------------------------------------
# east side in wood
# ---------------------------------------------------------------------------

EAST_STEEL = ['BEW', 'C-EN', 'E-S', 'E-N', 'E-M/B', 'E-M1/B',
              'RE-S', 'RE-M1', 'RE-M', 'RE-N']
EAST_RAFTER_SPACING = 24.0
EAST_RAFTER = '2x10 DF-L No.2'
EAST_RAFTER_DEPTH = 9.25


def east_side_in_wood(base: framemod.Frame, wall_x: float = 247.5,
                      wall_top: float = 98.5) -> tuple[framemod.Frame, dict]:
    """Replace the outer east steel with wood rafters bearing on the old wall.

    Owner variant. The four posts on the x = 247.5 line, the beam over them and
    the four steel rafters all come out. In their place a run of wood rafters
    spans from the existing east wall top up to ``BE.upper`` -- 36 in. out and
    48.9 in. up, a 60.7 in. rake, which is nothing for a 2x10 at 24 in. centres.

    This is the cheapest thing anyone has proposed for this frame, and it is the
    only one that changes what the building depends on. Every other reduction has
    kept the new structure standing clear of the old one. This puts the east edge
    of the roof on the existing east wall, which decision DEC-005 explicitly
    refused to rely on. That is not an objection to it -- it may well be the
    right trade -- but it is a different kind of decision and it needs the
    existing wall assessed before it can be taken.
    """
    f = copy.deepcopy(base)
    if UPPER_EAST not in f.members:
        return f, {'applied': False,
                   'reason': f'{UPPER_EAST} must exist first; the rafters land on it'}

    gone = [m for m in EAST_STEEL if m in f.members]
    saved = sum(f.member_weight(m) for m in gone)
    for m in gone:
        _drop(f, m)

    import completion
    chain = _chain(f, UPPER_EAST)
    ys = [f.xyz(n)[1] for n in chain]
    lo, hi = min(ys), max(ys)
    n = max(2, int(round((hi - lo) / EAST_RAFTER_SPACING)) + 1)
    added = []
    for k in range(n):
        y = lo + (hi - lo) * k / (n - 1)
        top = completion._split(f, UPPER_EAST, (f.xyz(chain[0])[0], y, f.xyz(chain[0])[2]),
                                f'E.wood@{y:.4g}.top')
        foot = f'E.wood@{y:.4g}.foot'
        # Vertical bearing on the existing wall top, not a foundation. The
        # ``bearing`` flag keeps the analysis from crediting the old masonry
        # with restraining the new frame sideways.
        f.nodes[foot] = dict(x=wall_x, y=y, z=wall_top, support=True,
                             bearing=True, free_end=False, members=[])
        name = f'East wood rafter {k + 1}'
        spec = dict(nodes=[foot, top], width=1.5, depth=EAST_RAFTER_DEPTH,
                    group='Rafters', material='wood', source_name=name,
                    section_reference=EAST_RAFTER,
                    section_status='owner variant: wood lean-to bearing on the '
                                   'existing east wall')
        f.members[name] = spec
        f.section_of[name] = framemod.resolve_section(spec)
        f.segments.append((name, foot, top))
        for node in (foot, top):
            f.nodes[node].setdefault('members', [])
            f.nodes[node]['members'].append(name)
        added.append(name)

    # A rafter simply set on a wall is a pendulum: vertical bearing holds it up
    # and nothing holds it still, and the first analysis of this variant came
    # back singular for exactly that reason. Real lean-tos have a ledger or rim
    # at the wall, so BEW is not deleted so much as demoted -- from a W12X16 to
    # a piece of timber.
    feet = [f'E.wood@{f.xyz(_chain(f, m)[0])[1]:.4g}.foot' for m in added]
    ledger = 'East wall ledger'
    spec = dict(nodes=[feet[0], feet[-1]], width=1.5, depth=EAST_RAFTER_DEPTH,
                group='Rafters', material='wood', source_name=ledger,
                section_reference=EAST_RAFTER,
                section_status='owner variant: ledger tying the wood rafter feet '
                               'along the existing east wall')
    f.members[ledger] = spec
    f.section_of[ledger] = framemod.resolve_section(spec)
    for a, b in zip(feet, feet[1:]):
        f.segments.append((ledger, a, b))
    for node in feet:
        f.nodes[node]['members'].append(ledger)
    added.append(ledger)

    return f, dict(applied=True, removed=gone, removed_steel_lb=round(saved, 1),
                   ledger=ledger,
                   added=added, spacing_in=round((hi - lo) / (n - 1), 1),
                   section=EAST_RAFTER, bearing_on='existing east wall top',
                   rake_in=round(((wall_x - f.xyz(chain[0])[0]) ** 2
                                  + (f.xyz(chain[0])[2] - wall_top) ** 2) ** 0.5, 1),
                   conflicts_with='DEC-005 (no reliance on existing walls)')


def east_lean_to_separate(base: framemod.Frame, wall_x: float = 247.5,
                          wall_top: float = 98.5, spacing: float = 24.0
                          ) -> tuple[framemod.Frame, dict]:
    """Strip the outer east steel and hand the lean-to over as a reaction.

    The east lean-to is a wood roof spanning the existing wall top to
    ``BE.upper``. It is not modelled inside the steel frame, because doing that
    lets the frame find a load path down the rafters into the old masonry --
    which is exactly what nobody wants. The rafters float: they carry their own
    strip of roof, hand half of it to ``BE.upper`` and half to the wall, and the
    steel frame never leans on the wall at all.

    So the steel model gets a line load on ``BE.upper`` equal to the lean-to's
    reaction, and the lean-to itself is checked separately as a simple span.
    """
    import loads as L
    f = copy.deepcopy(base)
    if UPPER_EAST not in f.members:
        return f, {'applied': False, 'reason': f'{UPPER_EAST} must exist first'}

    gone = [m for m in EAST_STEEL if m in f.members]
    saved = sum(f.member_weight(m) for m in gone)
    for m in gone:
        _drop(f, m)

    chain = _chain(f, UPPER_EAST)
    beam_x, beam_z = f.xyz(chain[0])[0], f.xyz(chain[0])[2]

    # The floor beams reached out to BEW at x = 247.5. With BEW and its posts
    # gone they would cantilever three feet into the lean-to zone with nothing
    # on the end, and BE would carry the moment -- which is what pushed BE past
    # HSS6X6X3/8, the top of the ladder, in the first run of this variant. The
    # floor now stops at the frame line and the east three feet is roof.
    trimmed = []
    for member in list(f.members):
        if f.group(member) not in ('Beams', 'Joists'):
            continue
        xs = [f.xyz(n)[0] for m, i, j in f.segments if m == member for n in (i, j)]
        if not xs or max(xs) <= beam_x + 0.5:
            continue
        if min(xs) >= beam_x - 0.5:
            _drop(f, member)               # lives entirely in the lean-to zone
            trimmed.append((member, 'removed'))
        else:
            keep = [(m, i, j) for m, i, j in f.segments
                    if m != member or max(f.xyz(i)[0], f.xyz(j)[0]) <= beam_x + 0.5]
            f.segments[:] = keep
            for v in f.nodes.values():
                if member in v.get('members', ()) and v['x'] > beam_x + 0.5:
                    v['members'] = [q for q in v['members'] if q != member]
            trimmed.append((member, f'trimmed to x={beam_x:g}'))
    run = abs(wall_x - beam_x)
    rise = beam_z - wall_top
    rake = (run ** 2 + rise ** 2) ** 0.5

    rafter = sections.sawn_lumber('2x10 DF-L No.2', 1.5, EAST_RAFTER_DEPTH)
    self_w = rafter.weight / 12.0                      # lb per inch of rafter
    dead_psf = L.DEAD['east_roof']
    live_psf = L.ROOF_LIVE

    # per inch along BE.upper, carrying half of each rafter's strip
    dead = 0.5 * (dead_psf / 144.0 * run + self_w * rake / spacing)
    live = 0.5 * (live_psf / 144.0 * run)
    f.extra_loads.append((UPPER_EAST, 'D', dead, 'east lean-to dead reaction'))
    f.extra_loads.append((UPPER_EAST, 'Lr', live, 'east lean-to roof live reaction'))

    # The shelf in the lean-to zone stops being floor when the posts under it
    # go: its joists were removed above, and leaving the deck declared would
    # have the plan hatch it as an opening in a floor that no longer exists.
    f.decks[:] = [d for d in f.decks if min(d['x']) < beam_x - 0.5]

    # BE now carries the whole east edge of the floor over the 22 ft between S3
    # and N2, because the beams that used to hand their east reactions to the
    # posts land on it instead. No square HSS covers that -- HSS6X6X3/8, the top
    # of the ladder, still runs at 1.04 -- so BE goes to a deeper wide flange.
    # W14X22 is the section the model's own owner_direction names for all beams.
    if 'BE' in f.members:
        f.members['BE']['section_reference'] = 'W14X22'
        f.members['BE']['section_status'] = (
            'owner variant: deepened because BE carries the east floor edge '
            'once the outer posts are removed')
        f.section_of['BE'] = framemod.resolve_section(f.members['BE'])

    # Geometry only, for the drawing. These rafters are deliberately not frame
    # members -- putting them in would give the steel a path into the old wall.
    lo = min(f.xyz(n)[1] for n in chain)
    hi = max(f.xyz(n)[1] for n in chain)
    n_raf = max(2, int(round((hi - lo) / spacing)) + 1)
    geometry = []
    for k in range(n_raf):
        y = lo + (hi - lo) * k / (n_raf - 1)
        geometry.append(((wall_x, y, wall_top), (beam_x, y, beam_z)))
    ledger = ((wall_x, lo, wall_top), (wall_x, hi, wall_top))

    length = abs(f.xyz(chain[-1])[1] - f.xyz(chain[0])[1])
    return f, dict(applied=True, removed=gone, removed_steel_lb=round(saved, 1),
                   geometry=geometry, ledger=ledger, rafter_depth=EAST_RAFTER_DEPTH,
                   trimmed=trimmed, be_section='W14X22',
                   rake_in=round(rake, 1), spacing_in=spacing,
                   rafter=rafter.name, n_rafters=int(round(length / spacing)) + 1,
                   dead_lb_per_in=round(dead, 4), live_lb_per_in=round(live, 4),
                   handed_to_beam_lb=round((dead + live) * length, 0),
                   handed_to_wall_lb=round((dead + live) * length, 0),
                   note='rafters float: half to BE.upper, half to the wall; the '
                        'steel frame takes no support from the existing wall')


# ---------------------------------------------------------------------------
# the stairwell, moved south
# ---------------------------------------------------------------------------

STAIR_BEAM_EXTENDED = 'B-1A'
STAIR_BEAM_CUT = 'B-1'
#: The two west-wall beams the cut leaves spliced in the open; they become one.
STAIR_WEST_BEAM = 'BWI-2'
STAIR_WEST_BEAM_ABSORBED = 'BWI-3'
WEST_INNER_X = 3.75
WEST_INFILL_DECK = 'west strip infill'
#: Span of the 23/32 in. OSB deck, the rule §3 of STR-008 measures against.
OSB_SPAN_IN = 24.0


def move_stair_south(base: framemod.Frame) -> tuple[framemod.Frame, dict]:
    """Slide the west-strip stair opening one bay south.

    Owner variant. The stair sits in the strip between BW and the inner west
    beams, and as drawn it occupies the bay from y = 71 to y = 185 -- the middle
    of three. Reaching it means walking the length of the loft.

    Two moves shift it. ``B-1A`` runs west to BW instead of stopping at the
    inner line, closing the strip at y = 128; and ``B-1`` gives up its length
    west of the inner line, opening the strip at y = 71. What was open from 71
    to 185 is now open from 3 to 128, so the stair arrives near the south wall
    and still lands under cover.

    The deck follows: the shelf gives up its west end and the strip between
    y = 128 and 185 is decked, which is the old stair's north half.
    """
    import completion
    f = copy.deepcopy(base)
    for member in (STAIR_BEAM_EXTENDED, STAIR_BEAM_CUT):
        if member not in f.members:
            return f, {'applied': False, 'reason': f'{member} is not in this model'}

    west_x = min(f.xyz(n)[0] for m, i, j in f.segments if m == 'BW' for n in (i, j))
    y_ext = f.xyz(_chain(f, STAIR_BEAM_EXTENDED)[0])[1]
    y_cut = f.xyz(_chain(f, STAIR_BEAM_CUT)[0])[1]

    # -- B-1A west to BW ---------------------------------------------------
    inner = [n for n in _chain(f, STAIR_BEAM_EXTENDED)
             if abs(f.xyz(n)[0] - WEST_INNER_X) < 0.5][0]
    landing = completion._split(f, 'BW', (west_x, y_ext, f.xyz(inner)[2]),
                                f'BW@{y_ext:g}')
    f.segments.append((STAIR_BEAM_EXTENDED, landing, inner))
    f.nodes[landing].setdefault('members', [])
    if STAIR_BEAM_EXTENDED not in f.nodes[landing]['members']:
        f.nodes[landing]['members'].append(STAIR_BEAM_EXTENDED)

    # -- B-1 back to the inner line ---------------------------------------
    dropped = [(i, j) for m, i, j in f.segments if m == STAIR_BEAM_CUT
               and max(f.xyz(i)[0], f.xyz(j)[0]) <= WEST_INNER_X + 0.5]
    f.segments[:] = [t for t in f.segments
                     if not (t[0] == STAIR_BEAM_CUT
                             and max(f.xyz(t[1])[0], f.xyz(t[2])[0])
                             <= WEST_INNER_X + 0.5)]
    for node, v in f.nodes.items():
        if (STAIR_BEAM_CUT in v.get('members', ())
                and v['x'] < WEST_INNER_X - 0.5):
            v['members'] = [q for q in v['members'] if q != STAIR_BEAM_CUT]

    # -- the joists in the new opening go with it --------------------------
    # The shelf ran west to BW and its joists spanned from B-S up to B-1. With
    # B-1 cut back, the two westernmost were left hanging at their north end --
    # the analysis said so before the drawing would have. They stand in the
    # stair opening now, so they come out.
    pulled = []
    for member in list(f.members):
        if f.material(member) != 'wood':
            continue
        pts = [f.xyz(n) for m, i, j in f.segments if m == member for n in (i, j)]
        if not pts:
            continue
        cx = sum(q[0] for q in pts) / len(pts)
        ylo, yhi = min(q[1] for q in pts), max(q[1] for q in pts)
        if cx < WEST_INNER_X - 0.5 and ylo >= 2.0 and yhi <= y_ext + 0.5:
            _drop(f, member)
            pulled.append(member)

    # -- the deck follows ---------------------------------------------------
    for deck in f.decks:
        if deck['name'].startswith('shelf SH') and deck['x'][0] < WEST_INNER_X:
            deck['x'] = [WEST_INNER_X, deck['x'][1]]
            deck['area_sf'] = ((deck['x'][1] - deck['x'][0])
                               * (deck['y'][1] - deck['y'][0]) / 144.0)
    f.decks.append(dict(name=WEST_INFILL_DECK, x=[west_x, WEST_INNER_X],
                        y=[y_ext, 185.0], rims=[],
                        area_sf=(WEST_INNER_X - west_x) * (185.0 - y_ext) / 144.0))

    # -- and the infill gets joists ----------------------------------------
    # Declaring the deck is not framing it. Without this the tributary
    # machinery hands the infill's floor load straight to the four beams
    # around it, which can carry it, so the frame verifies over a bay with
    # nothing for the sheathing to land on -- the same blind spot that put 33
    # joists on the chopping block in revision 0.
    added = _infill_joists(f, west_x, y_ext, 185.0)

    # -- BWI-2 and BWI-3 become one piece ----------------------------------
    # They were split at y = 71 because B-1 crossed there and ran on west to
    # BW. B-1 stops at this line now, so the splice sits in the middle of the
    # free edge of the stair opening, which is the last place to put one. The
    # node stays -- B-1 still frames into the side of the beam -- but the beam
    # runs through it.
    merged = _merge_members(f, STAIR_WEST_BEAM, STAIR_WEST_BEAM_ABSORBED,
                            note=f'on the existing west wall, B-S -> B-2, '
                                 f'continuous past B-1 at y={y_cut:g}')

    opening = ((WEST_INNER_X - west_x) * (y_ext - 3.0) / 144.0)
    return f, dict(applied=True,
                   extended=STAIR_BEAM_EXTENDED, extended_to=round(west_x, 2),
                   cut=STAIR_BEAM_CUT, cut_back_to=WEST_INNER_X,
                   segments_removed=len(dropped),
                   stair_was=[y_cut, 185.0], stair_now=[3.0, y_ext],
                   joists_pulled=pulled,
                   joists_added=added,
                   merged=([STAIR_WEST_BEAM, STAIR_WEST_BEAM_ABSORBED]
                           if merged else []),
                   opening_sf=round(opening, 1),
                   was_sf=round((WEST_INNER_X - west_x) * (185.0 - y_cut) / 144.0, 1))


def _infill_joists(f: framemod.Frame, west_x: float, y0: float,
                   y1: float) -> list[str]:
    """Frame the bay the stair has vacated, on the lines already in the strip.

    The joists take their x stations from the bay immediately north rather
    than from a fresh division of the width, so the lines run through across
    ``B-2`` instead of stopping and restarting a few inches over.
    """
    lines = sorted({round(f.xyz(n)[0], 4)
                    for m, i, j in f.segments if f.material(m) == 'wood'
                    for n in (i, j)
                    if f.xyz(n)[0] < WEST_INNER_X - 0.5
                    and f.xyz(n)[1] >= y1 - 0.5})
    if not lines:
        return []
    z = f.xyz(_chain(f, STAIR_BEAM_EXTENDED)[0])[2]
    south = _member_spanning(f, y0)
    north = _member_spanning(f, y1)
    if south is None or north is None:
        return []
    added = []
    for k, x in enumerate(lines, start=1):
        a = completion._split(f, south, (x, y0, z), f'@{x:g},{y0:g}')
        b = completion._split(f, north, (x, y1, z), f'@{x:g},{y1:g}')
        name = f'{WEST_INFILL_DECK} joist {k}'
        completion._add_member(f, name, a, b, '2x8 DF-L No.2', 1.5, 7.25,
                               'Joists', 'wood',
                               note=f'{WEST_INFILL_DECK}, on the loft bay 3 '
                                    f'joist line at x={x:g}')
        f.members[name]['note'] = WEST_INFILL_DECK
        added.append(name)
    _check_deck_span(f, west_x, lines)
    return added


def _check_deck_span(f: framemod.Frame, west_x: float,
                     lines: list[float]) -> None:
    """The deck has to reach from edge to edge, not just between joists.

    Measured out to the framed edges of the strip, which is the fix revision 1
    had to make three times over before it stuck.
    """
    stations = [west_x] + list(lines) + [WEST_INNER_X]
    gaps = [b - a for a, b in zip(stations, stations[1:])]
    worst = max(gaps)
    if worst > OSB_SPAN_IN:
        raise ValueError(
            f'{WEST_INFILL_DECK}: widest gap {worst:.1f} in. exceeds the '
            f'{OSB_SPAN_IN:g} in. span of the deck; stations {stations}')


def _member_spanning(f: framemod.Frame, y: float) -> str | None:
    """The east-west floor beam on this line that reaches west of the strip."""
    best = None
    for member in f.members:
        if f.group(member) != 'Beams':
            continue
        pts = [f.xyz(n) for m, i, j in f.segments if m == member for n in (i, j)]
        if not pts or max(abs(q[1] - y) for q in pts) > 0.5:
            continue
        if min(q[0] for q in pts) < WEST_INNER_X - 1.0:
            best = member
    return best


def _merge_members(f: framemod.Frame, keep: str, absorb: str,
                   note: str = '') -> bool:
    """Make two collinear beams a single piece, keeping the node between them.

    The node is what lets a third member frame into the side of the run, so it
    stays; what goes is the splice, and with it one piece and two fitted ends.
    """
    if keep not in f.members or absorb not in f.members:
        return False
    f.segments[:] = [(keep if m == absorb else m, i, j)
                     for m, i, j in f.segments]
    for v in f.nodes.values():
        ms = v.get('members')
        if not ms or absorb not in ms:
            continue
        out = []
        for q in ms:
            q = keep if q == absorb else q
            if q not in out:
                out.append(q)
        v['members'] = out
    f.extra_loads[:] = [((keep,) + tuple(rest)) if rest0 == absorb else
                        ((rest0,) + tuple(rest))
                        for rest0, *rest in f.extra_loads]
    pts = [f.xyz(n) for m, i, j in f.segments if m == keep for n in (i, j)]
    ends = sorted({(round(q[0], 4), round(q[1], 4), round(q[2], 4)) for q in pts})
    f.members[keep]['nodes'] = [f'@{ends[0][0]:g},{ends[0][1]:g}',
                                f'@{ends[-1][0]:g},{ends[-1][1]:g}']
    if note:
        f.members[keep]['note'] = note
    f.members.pop(absorb, None)
    f.section_of.pop(absorb, None)
    return True


# ---------------------------------------------------------------------------
# the north wall: a second upper post, and a wall where the bay used to be
# ---------------------------------------------------------------------------

NORTH_POST = 'N-M2'
NORTH_POST_PARENT = 'N-M'
NORTH_BEAM = 'B-N'
NORTH_ROOF_BEAM = 'R-W4'
#: The open bay the owner is keeping, measured west from N-M.
NORTH_BAY_OPEN_IN = 72.0


def add_north_post(base: framemod.Frame) -> tuple[framemod.Frame, dict]:
    """Halve the open bay in the upper north wall with a second post.

    Above the loft the north wall has posts at W4, N-M and N2. The bay from W4
    to N-M is 122.75 in. of nothing -- the loading opening. The owner wants the
    opening cut to 6 ft, measured west from N-M, and the rest of the run walled,
    which needs a post at the 6 ft mark for the wall to end on.

    The new post is N-M's twin in every respect: same section, same group, it
    stands on ``B-N`` and carries ``R-W4`` over the same 120.75 in.

    Nothing here changes the dead load. ``surfaces`` already models the north
    wall as a solid rectangle from sill to roof -- the opening lives in the
    label, not in the outline -- so the cladding over this bay has been carried
    in the analysis all along. Walling it is load the frame was already
    designed for, and the post is a pure addition.
    """
    f = copy.deepcopy(base)
    for member in (NORTH_POST_PARENT, NORTH_BEAM, NORTH_ROOF_BEAM):
        if member not in f.members:
            return f, {'applied': False, 'reason': f'{member} is not in this model'}

    ends = sorted((f.xyz(n) for m, i, j in f.segments if m == NORTH_POST_PARENT
                   for n in (i, j)), key=lambda p: p[2])
    (px, py, z_bot), (_, _, z_top) = ends[0], ends[-1]
    x = px - NORTH_BAY_OPEN_IN

    west_x = min(f.xyz(n)[0] for m, i, j in f.segments if m == NORTH_ROOF_BEAM
                 for n in (i, j))
    if x <= west_x:
        return f, {'applied': False,
                   'reason': f'a post {NORTH_BAY_OPEN_IN:g} in. west of '
                             f'{NORTH_POST_PARENT} lands at x={x:g}, past the '
                             f'west line at x={west_x:g}'}

    bottom = completion._split(f, NORTH_BEAM, (x, py, z_bot), f'@{x:g},{py:g}')
    top = completion._split(f, NORTH_ROOF_BEAM, (x, py, z_top),
                            f'@{x:g},{py:g},{z_top:g}')
    spec = f.members[NORTH_POST_PARENT]
    completion._add_member(
        f, NORTH_POST, bottom, top, spec['section_reference'],
        spec['width'], spec['depth'], spec['group'], f.material(NORTH_POST_PARENT),
        note=f'owner: second north wall post, {NORTH_BAY_OPEN_IN:g} in. west of '
             f'{NORTH_POST_PARENT}, cutting the loading opening to '
             f'{NORTH_BAY_OPEN_IN / 12:g} ft')
    f.members[NORTH_POST]['note'] = (
        f'north wall post, second floor only, stands on {NORTH_BEAM} and '
        f'carries {NORTH_ROOF_BEAM}')
    return f, dict(applied=True, post=NORTH_POST, x=round(x, 2),
                   y=round(py, 2), z=[round(z_bot, 2), round(z_top, 2)],
                   section=spec['section_reference'],
                   open_bay_in=NORTH_BAY_OPEN_IN,
                   walled_in=round(x - west_x, 2),
                   was_open_in=round(px - west_x, 2))
