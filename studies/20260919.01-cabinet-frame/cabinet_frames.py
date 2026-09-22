"""The east-wall cabinet frames, as steel: geometry and the strengthening schemes.

Owner description, 2026-09-19, with five photographs. Three 4 ft bays of
cabinets stand against the east wall of the existing garage. Between and beside
the bays are welded steel side frames of 1 x 2 tube: the 1 in. face shows at
the door line, the 2 in. side runs front to back. Each frame is a plain
rectangle, 30 in. front to back and about 99 in. high. The frames are welded;
the rails that hold them apart -- top rails, the bench-level rails and the
shelf tubes -- are bolted in. One end frame has a cutout in its top corner
around an existing ceiling beam. Under the beam scheme the front face of the
frames lies directly below the inner east beam ``BE``.

Everything in this file is geometry in the project frame (x east, y north,
z up, inches). It knows nothing about analysis; ``structural-analysis-v6/
cabinet_frame_study.py`` turns it into finite elements and
``draw_cabinet_frames.py`` draws it.

Assumptions, each awaiting a tape measure
-----------------------------------------
* Frame stations from the 2026-09-18 cabinet study: uprights centred at
  y = 56, 105, 154, 203 (49 in. pitch: 48 in. bay + 1 in. upright). Measured
  from the outside face of the south wall.
* The front face of the front leg is on the ``BE`` axis, x = 211.5. The frames
  are 30 in. deep, so the rear leg is at x = 241.5, 2 in. clear of the 6 in.
  east wall (inside face x = 243.5).
* Frame height is taken as 98.5 in. -- the existing wall top, which is where
  the beam soffit sits in the beam scheme. The owner's "about 99" will need to
  be trimmed or the beam packed by the difference.
* Tube is 2 x 1 x 11 gauge (0.120 in. nominal wall), which is what the
  earlier study recorded. Not verified by measurement.
* Bolted rails between frames at three levels: the bench / lower-cabinet top
  (z = 40), the upper-cabinet bottom rail (z = 60) and the top (z = 98.5),
  front and rear. Levels are read off the photographs, not measured.
* The cutout is in the north end frame (CF4), which is the frame with the
  pegboard door hinged to it in photograph 4273. Its shape is not modelled.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# the frames as they stand
# --------------------------------------------------------------------------

FRONT_X = 211.5                 # BE axis; front face of the front legs
DEPTH = 30.0                    # front to back
REAR_X = FRONT_X + DEPTH        # 241.5
HEIGHT = 98.5                   # to the beam soffit (owner: "about 99")
BEAM_AXIS_Z = 104.5             # BE axis, W12X16 soffit at 98.5
BAY = 48.0                      # clear bay between frames
FACE = 1.0                      # tube dimension showing at the door line (y)
SIDE = 2.0                      # tube dimension front to back (x)
WALL_T = 0.120                  # 11 gauge, nominal

#: Frame stations, south to north. CF4 is the end frame with the cutout.
FRAME_Y = [56.0, 105.0, 154.0, 203.0]
FRAME_NAMES = ['CF1', 'CF2', 'CF3', 'CF4']
CUTOUT_FRAME = 'CF4'

#: Levels of the bolted rails that hold the frames apart.
BENCH_Z = 40.0
UPPER_SILL_Z = 60.0
RAIL_LEVELS = [BENCH_Z, UPPER_SILL_Z, HEIGHT]

#: Where the frames sit in the existing garage.
EXISTING_SOUTH_WALL = (0.0, 6.0)
EXISTING_NORTH_WALL = (241.0, 249.0)
EXISTING_EAST_WALL = (243.5, 249.5)
RUN_SOUTH = FRAME_Y[0] - FACE / 2       # 55.5
RUN_NORTH = FRAME_Y[-1] + FACE / 2      # 203.5


# --------------------------------------------------------------------------
# sections
# --------------------------------------------------------------------------

@dataclass
class Tube:
    """A rectangular tube or a built-up pair, by outside size and wall."""
    name: str
    b: float            # dimension along y (the door-line face)
    d: float            # dimension along x (front to back)
    t: float            # nominal wall
    count: int = 1      # 2 for two tubes welded side by side along x
    note: str = ''


LEG_AS_IS = Tube('HSS2X1X0.120', FACE, SIDE, WALL_T, note='existing 11 ga leg')
LEG_DOUBLED = Tube('2-HSS2X1X0.120', FACE, 2 * SIDE, WALL_T, count=2,
                   note='second 2x1 tube welded behind the existing leg: 1 x 4 built-up')
RAIL = Tube('HSS2X1X0.120', FACE, SIDE, WALL_T, note='existing rail')
BRACE = Tube('HSS2X1X0.120', FACE, SIDE, WALL_T,
             note='same 2 x 1 stock as the frames; the 1 in. face fits inside the side panel')


# --------------------------------------------------------------------------
# members
# --------------------------------------------------------------------------

@dataclass
class Member:
    name: str
    a: tuple            # (x, y, z)
    b: tuple
    tube: Tube
    group: str          # 'Columns' | 'Beams' | 'Bracing'  (Bracing is pin-ended)
    kind: str           # 'existing' | 'added' | 'replaced'
    frame: str = ''     # CF1..CF4 or '' for something between frames
    fe: bool = True     # carried into the finite-element model
    note: str = ''

    @property
    def length(self) -> float:
        return math.dist(self.a, self.b)


SCHEMES = {
    'as-is': 'the frames as they stand, legs continued up to the BE axis',
    'strengthened': 'front legs doubled to 1 x 4, N-bracing in every side frame, '
                    'X-bracing in the rear plane of every bay, all in the same 2 x 1 stock',
}


def members(scheme: str = 'as-is') -> list[Member]:
    """Every member of the cabinet steel under the given scheme."""
    if scheme not in SCHEMES:
        raise KeyError(f'scheme {scheme!r}; choose from {sorted(SCHEMES)}')
    strong = scheme == 'strengthened'
    out: list[Member] = []

    for name, y in zip(FRAME_NAMES, FRAME_Y):
        leg = LEG_DOUBLED if strong else LEG_AS_IS
        # The front leg is carried up through the beam's half depth to the BE
        # axis so the beam node and the leg share a joint; the extra 6 in. is
        # the beam web, not tube.
        out.append(Member(f'{name}.front', (FRONT_X, y, 0.0), (FRONT_X, y, BEAM_AXIS_Z),
                          leg, 'Columns', 'replaced' if strong else 'existing', name,
                          note='front leg, under BE; top 6 in. is the beam depth'))
        out.append(Member(f'{name}.rear', (REAR_X, y, 0.0), (REAR_X, y, HEIGHT),
                          LEG_AS_IS, 'Columns', 'existing', name, note='rear leg'))
        out.append(Member(f'{name}.top', (FRONT_X, y, HEIGHT), (REAR_X, y, HEIGHT),
                          RAIL, 'Beams', 'existing', name, note='welded top rail'))
        out.append(Member(f'{name}.sill', (FRONT_X, y, 0.0), (REAR_X, y, 0.0),
                          RAIL, 'Beams', 'existing', name, fe=False,
                          note='welded bottom rail, on the slab; both ends are supports'))
        if strong:
            zm = HEIGHT / 2
            out.append(Member(f'{name}.strut', (FRONT_X, y, zm), (REAR_X, y, zm),
                              BRACE, 'Bracing', 'added', name,
                              note='mid-height strut dividing the side frame into two panels'))
            out.append(Member(f'{name}.diag.lower', (FRONT_X, y, 0.0), (REAR_X, y, zm),
                              BRACE, 'Bracing', 'added', name,
                              note='N-brace, lower panel'))
            out.append(Member(f'{name}.diag.upper', (REAR_X, y, zm), (FRONT_X, y, HEIGHT),
                              BRACE, 'Bracing', 'added', name,
                              note='N-brace, upper panel'))

    # bolted rails between adjacent frames, front and rear
    for (na, ya), (nb, yb) in zip(zip(FRAME_NAMES, FRAME_Y), zip(FRAME_NAMES[1:], FRAME_Y[1:])):
        bay = f'{na}-{nb}'
        for z, tag in zip(RAIL_LEVELS, ('bench', 'sill', 'top')):
            out.append(Member(f'{bay}.front.{tag}', (FRONT_X, ya, z), (FRONT_X, yb, z),
                              RAIL, 'Bracing', 'existing', note=f'bolted front rail at z={z:g}'))
            out.append(Member(f'{bay}.rear.{tag}', (REAR_X, ya, z), (REAR_X, yb, z),
                              RAIL, 'Bracing', 'existing', note=f'bolted rear rail at z={z:g}'))
        if strong:
            # The X is joined at its crossing (the study splits both diagonals
            # there), which halves the unbraced length of each one.
            out.append(Member(f'{bay}.rear.X1', (REAR_X, ya, 0.0), (REAR_X, yb, HEIGHT),
                              BRACE, 'Bracing', 'added',
                              note='rear-plane X against the wall, joined at the crossing'))
            out.append(Member(f'{bay}.rear.X2', (REAR_X, yb, 0.0), (REAR_X, ya, HEIGHT),
                              BRACE, 'Bracing', 'added',
                              note='rear-plane X against the wall, joined at the crossing'))
    return out


def supports() -> dict[str, tuple]:
    """Base nodes: every leg foot, pinned on whatever foundation is built."""
    out = {}
    for name, y in zip(FRAME_NAMES, FRAME_Y):
        out[f'{name}.front.base'] = (FRONT_X, y, 0.0)
        out[f'{name}.rear.base'] = (REAR_X, y, 0.0)
    return out


def be_bearing_nodes() -> dict[str, tuple]:
    """Where each front leg meets the BE axis."""
    return {f'{n}.top': (FRONT_X, y, BEAM_AXIS_Z) for n, y in zip(FRAME_NAMES, FRAME_Y)}


def summary(scheme: str = 'as-is') -> dict:
    ms = members(scheme)
    added = [m for m in ms if m.kind != 'existing']
    return dict(scheme=scheme, description=SCHEMES[scheme], members=len(ms),
                added=len(added),
                added_length_ft=round(sum(m.length for m in added) / 12.0, 1),
                frames=dict(zip(FRAME_NAMES, FRAME_Y)))


if __name__ == '__main__':
    for s in SCHEMES:
        print(summary(s))
        for m in members(s):
            print(f'  {m.name:<20} {m.tube.name:<14} {m.group:<8} {m.kind:<9} '
                  f'{m.length:6.1f} in  {m.note}')
