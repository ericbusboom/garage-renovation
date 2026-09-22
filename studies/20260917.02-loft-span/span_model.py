"""The W1 -> E-S east-west span, as a two-dimensional COMPAS model.

The built frame carries the loft on east-west members that stop at the *inner*
east column line (``east_x`` = 211.5).  This study asks a different question:
what if the frame came down on the columns that are actually there --- W1 on the
west and E-S standing on the existing east wall --- so that one member runs the
whole way across?

Geometry is read from ``frame-spec.json`` rather than restated, so the span this
module reports is the span the project model actually has.  The model built here
is a *plane* model in the x-z plane: the span is east-west, the drawing looks
north, and every y coordinate is dropped.  It is a study of one line of framing,
not a frame model, so under the rule in ``frame-models/README.md`` it is
serialised beside its viewer and not into the canonical store.

Units are inches and pounds throughout, matching the rest of the project.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from compas.data import json_dump
from compas.datastructures import Graph
from compas.geometry import Line, Point

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'roof-studies/square-upper-west/connected-frame/frame-spec.json'
OUT = Path(__file__).resolve().parent / 'output'

#: Columns that define the two ends of the study span.
WEST_COLUMN = 'W.W1'          # frame-spec member; base node W.W1.base
EAST_COLUMN = 'E-S'           # frame-spec member; base node E-S.base


@dataclass(frozen=True)
class SpanGeometry:
    """The one-dimensional facts the whole study rests on."""
    west_x: float             # in, plan x of the W1 column axis
    east_x: float             # in, plan x of the E-S column axis
    inner_east_x: float       # in, plan x of the column line the built frame uses
    floor_z: float            # in, top of the loft floor structure
    loft_south_y: float       # in, south edge of the loft floor
    loft_north_y: float       # in, north edge of the loft floor
    existing_west_x: float    # in, outside face of the existing west wall
    existing_east_x: float    # in, outside face of the existing east wall
    existing_wall_top_z: float   # in, top of the existing wall plate
    garage_door_head_z: float    # in, head of the existing north garage door

    @property
    def depth_budget_in(self) -> float:
        """How deep a beam can be before its soffit drops past the existing wall top.

        This is the real constraint on depth, and it is a generous one: the loft
        floor sits 17-1/2 in. above the plate of the wall the E-S column stands
        on, so anything shallower than that passes over the existing structure
        without touching it.
        """
        return self.floor_z - self.existing_wall_top_z

    @property
    def west_overhang_in(self) -> float:
        """How far the W1 column line stands outside the existing west wall."""
        return self.existing_west_x - self.west_x

    def soffit_z(self, beam_depth: float) -> float:
        """Underside of the beam, with top of steel set at the loft floor line."""
        return self.floor_z - beam_depth

    @property
    def span_in(self) -> float:
        """Centre-to-centre span, W1 axis to E-S axis."""
        return self.east_x - self.west_x

    @property
    def span_ft(self) -> float:
        return self.span_in / 12.0

    @property
    def built_span_in(self) -> float:
        """The span the current frame's loft beams actually have."""
        return self.inner_east_x - self.west_x

    @property
    def loft_depth_in(self) -> float:
        """North-south dimension of the loft floor."""
        return self.loft_north_y - self.loft_south_y

    @property
    def loft_depth_ft(self) -> float:
        return self.loft_depth_in / 12.0

    @property
    def loft_area_ft2(self) -> float:
        """Plan area of the loft if it is taken out to the E-S column line."""
        return self.span_ft * self.loft_depth_ft


def _resolve(spec: dict, node_name: str) -> list[float]:
    """Return the xyz of a frame-spec node, substituting named parameters."""
    p = spec['parameters']
    raw = spec['nodes'][node_name]['xyz']
    return [p[v] if isinstance(v, str) else float(v) for v in raw]


def read_geometry(spec_path: Path = SPEC) -> tuple[SpanGeometry, dict]:
    """Pull the study geometry out of the project's frame specification."""
    spec = json.loads(spec_path.read_text())
    p = spec['parameters']
    west = _resolve(spec, spec['members'][WEST_COLUMN]['nodes'][0])
    east = _resolve(spec, spec['members'][EAST_COLUMN]['nodes'][0])
    geom = SpanGeometry(
        west_x=west[0],
        east_x=east[0],
        inner_east_x=p['east_x'],
        floor_z=116.0,               # loft floor line; frame-spec loft beams sit here
        loft_south_y=p['clerestory_y'],
        loft_north_y=p['north_y'],
        # the existing garage, from scene-mesh.json's ExistingGarage group
        existing_west_x=0.0,
        existing_east_x=249.5,
        existing_wall_top_z=98.5,
        garage_door_head_z=86.0,
    )
    return geom, spec


# ---------------------------------------------------------------------------
# the plane model
# ---------------------------------------------------------------------------

def build_graph(geom: SpanGeometry, beam_depth: float, beam_label: str,
                n_panels: int = 0, truss_depth: float = 0.0) -> Graph:
    """A COMPAS Graph of one east-west line of framing, in the x-z plane.

    With ``n_panels == 0`` the span is a single flexural member and the graph has
    one edge between the two column heads.  With ``n_panels > 0`` the span is a
    parallel-chord Warren truss of ``truss_depth`` and the graph carries its
    chords, verticals and diagonals, so the same drawing code serves both.

    Node attributes carry ``x``/``z`` (``y`` is zero: this is a plane model) plus
    a ``kind``.  Edge attributes carry ``role`` and the section label.
    """
    g = Graph(name=f'W1-ES span · {beam_label}')
    g.update_default_node_attributes(kind='joint', label='')
    g.update_default_edge_attributes(role='member', section='', depth=0.0)

    base_z, head_z = 0.0, geom.floor_z
    w_base = g.add_node(x=geom.west_x, y=0.0, z=base_z, kind='support', label='W1 base')
    e_base = g.add_node(x=geom.east_x, y=0.0, z=base_z, kind='support', label='E-S base')
    w_head = g.add_node(x=geom.west_x, y=0.0, z=head_z, kind='bearing', label='W1 head')
    e_head = g.add_node(x=geom.east_x, y=0.0, z=head_z, kind='bearing', label='E-S head')

    g.add_edge(w_base, w_head, role='column', section='HSS4X4X3/16', depth=4.0)
    g.add_edge(e_base, e_head, role='column', section='HSS4X4 (concept)', depth=4.0)

    if n_panels == 0:
        g.add_edge(w_head, e_head, role='beam', section=beam_label, depth=beam_depth)
        return g

    # --- parallel-chord Warren truss, top chord at the floor line ------------
    step = geom.span_in / n_panels
    top = [w_head] + [
        g.add_node(x=geom.west_x + step * i, y=0.0, z=head_z, kind='panel',
                   label=f'top {i}')
        for i in range(1, n_panels)
    ] + [e_head]
    bot = [
        g.add_node(x=geom.west_x + step * (i + 0.5), y=0.0, z=head_z - truss_depth,
                   kind='panel', label=f'bottom {i}')
        for i in range(n_panels)
    ]
    for a, b in zip(top, top[1:]):
        g.add_edge(a, b, role='top chord', section=beam_label, depth=truss_depth)
    for a, b in zip(bot, bot[1:]):
        g.add_edge(a, b, role='bottom chord', section=beam_label, depth=truss_depth)
    for i, n in enumerate(bot):
        g.add_edge(top[i], n, role='diagonal', section=beam_label, depth=truss_depth)
        g.add_edge(n, top[i + 1], role='diagonal', section=beam_label, depth=truss_depth)
    return g


def beam_line(geom: SpanGeometry) -> Line:
    """The study beam as a COMPAS Line, for anything that wants pure geometry."""
    return Line(Point(geom.west_x, 0.0, geom.floor_z),
                Point(geom.east_x, 0.0, geom.floor_z))


def dump(payload: dict, name: str) -> Path:
    """Serialise a study object through COMPAS into ``output/``."""
    OUT.mkdir(exist_ok=True)
    path = OUT / name
    json_dump(payload, path, pretty=True)
    return path


if __name__ == '__main__':
    g, _ = read_geometry()
    print(f'W1 axis          x = {g.west_x:>8.1f} in')
    print(f'E-S axis         x = {g.east_x:>8.1f} in')
    print(f'study span           {g.span_in:>8.1f} in = {g.span_ft:.2f} ft')
    print(f'built frame span     {g.built_span_in:>8.1f} in = {g.built_span_in / 12:.2f} ft')
    print(f'loft depth N-S       {g.loft_depth_in:>8.1f} in = {g.loft_depth_ft:.2f} ft')
    print(f'loft plan area       {g.loft_area_ft2:>8.1f} sf')
    print(f'W1 outside the wall  {g.west_overhang_in:>8.1f} in')
    print(f'depth budget         {g.depth_budget_in:>8.1f} in '
          f'(floor {g.floor_z:.1f} - existing plate {g.existing_wall_top_z:.1f})')
