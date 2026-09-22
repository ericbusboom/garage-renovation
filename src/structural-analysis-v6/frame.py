"""Load the canonical COMPAS frame model and build a PyNite finite-element model.

The COMPAS file already carries everything a frame analysis needs: a joint graph
whose nodes have resolved coordinates and support flags, and whose edges are
member segments between consecutive joints.  That is a finite-element mesh in all
but name -- 160 nodes and 261 beam elements -- so no re-meshing is done here.  The
elements are the segments the geometry model already declares, which keeps the
analysis traceable back to the drawing.

Axis convention
---------------
The project model is Z-up, in inches.  PyNite is Y-up.  The mapping used
throughout is a right-handed rotation::

    PyNite X =  model x        (east)
    PyNite Y =  model z        (up)
    PyNite Z = -model y        (south)

``to_fe`` and ``to_model`` convert vectors and points in both directions.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from Pynite import FEModel3D

import sections
from project_paths import PROJECT_ROOT as ROOT, FRAME_DIR

#: The lineage this analysis is built for.
#:
#: ``frame-models/`` holds more than one live lineage, and an unqualified
#: "newest model" resolves across all of them -- its README says so explicitly.
#: The completion and load-surface geometry here is written against the
#: ``square-upper-west`` parameter set, so the lineage is named rather than
#: inferred.  Pointing this at another lineage needs matching work in
#: ``completion.py`` and ``surfaces.py``, not just a different default.
DEFAULT_LINEAGE = 'square-upper-west'

# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------

MATERIALS = {
    # name        E (ksi->psi)   G          nu     rho lb/in^3   Fy psi
    'steel': dict(E=29.0e6, G=11.2e6, nu=0.30, rho=0.2836, fy=50_000.0,
                  spec='ASTM A500 Gr. C (HSS) / A992 (W-shapes), Fy = 50 ksi'),
    'wood':  dict(E=1.6e6,  G=0.10e6, nu=0.30, rho=0.0185, fy=900.0,
                  spec='Douglas fir-larch No. 2, E = 1,600 ksi, Fb = 900 psi'),
}
# The COMPAS model tags the east roof rafters with their own material name; they
# are steel tubes like everything else in that group.
MATERIAL_ALIAS = {'rafter': 'steel'}

#: Members modelled with end moment releases -- discrete braces, pinned by intent.
PIN_ENDED_GROUPS = {'Bracing', 'Joists', 'Rafters'}


# ---------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------

def to_fe(p) -> tuple[float, float, float]:
    """Model (x, y, z) -> PyNite (X, Y, Z)."""
    return (p[0], p[2], -p[1])


def to_model(p) -> tuple[float, float, float]:
    """PyNite (X, Y, Z) -> model (x, y, z)."""
    return (p[0], -p[2], p[1])


@dataclass
class Frame:
    """The frame geometry, decoupled from any analysis package."""
    path: Path
    version: str
    nodes: dict[str, dict]                 # name -> {x, y, z, support, free_end, members}
    segments: list[tuple[str, str, str]]   # (member, node_i, node_j)
    members: dict[str, dict]               # member -> specification record
    links: list[tuple[str, str, str]] = field(default_factory=list)
    section_of: dict[str, sections.Section] = field(default_factory=dict)
    schema: str = ''
    decks: list = field(default_factory=list)
    #: Line loads applied to a member that stand in for structure analysed
    #: separately: (member, load case, lb per inch, description).
    extra_loads: list = field(default_factory=list)
    #: Moment releases at one end of a member: (member, node).  A beam pinned
    #: to a column carries its shear into the column and no moment.
    pinned_ends: list = field(default_factory=list)
    # Conservative, explicitly assessed lengths when a new in-plane joint must
    # not be credited as lateral/torsional restraint.
    unbraced_length_overrides: dict[str, float] = field(default_factory=dict)

    # -- derived views ----------------------------------------------------
    @property
    def supports(self) -> list[str]:
        return [n for n, v in self.nodes.items() if v.get('support')]

    def xyz(self, name: str) -> tuple[float, float, float]:
        v = self.nodes[name]
        return (v['x'], v['y'], v['z'])

    def group(self, member: str) -> str:
        return self.members[member]['group']

    def members_in(self, *groups: str) -> list[str]:
        g = set(groups)
        return [m for m, v in self.members.items() if v['group'] in g]

    def nodes_of(self, members) -> list[str]:
        want = set(members)
        return [n for n, v in self.nodes.items() if want.intersection(v.get('members', []))]

    def segment_length(self, i: str, j: str) -> float:
        a, b = self.xyz(i), self.xyz(j)
        return sum((b[k] - a[k]) ** 2 for k in range(3)) ** 0.5

    def member_length(self, member: str) -> float:
        return sum(self.segment_length(i, j)
                   for m, i, j in self.segments if m == member)

    def member_weight(self, member: str) -> float:
        """Self weight of one whole member, pounds."""
        s = self.section_of[member]
        rho = MATERIALS[self.material(member)]['rho']
        return s.A * rho * self.member_length(member)

    def material(self, member: str) -> str:
        m = self.members[member]['material']
        return MATERIAL_ALIAS.get(m, m)

    def total_weight(self) -> float:
        return sum(self.member_weight(m) for m in self.members)


# ---------------------------------------------------------------------------
# section resolution
# ---------------------------------------------------------------------------

_HSS_RE = re.compile(r'^HSS([\d\-/]+)X([\d\-/]+)X([\d\-/]+)$', re.I)


def _dim(token: str) -> float:
    """'3-1/2' -> 3.5, '3/16' -> 0.1875, '4' -> 4.0"""
    token = token.strip()
    if '-' in token:
        whole, frac = token.split('-', 1)
        return float(whole) + _dim(frac)
    if '/' in token:
        n, d = token.split('/')
        return float(n) / float(d)
    return float(token)


def resolve_section(spec: dict) -> sections.Section:
    """Pick a section for one member record from the COMPAS specification.

    An explicit AISC designation is honoured.  A nominal ``concept envelope`` is
    resolved to the lightest standard wall for that outside dimension, which is
    the conservative reading and the one that makes the downsizing study honest.
    """
    ref = (spec.get('section_reference') or '').strip()
    w, d = float(spec['width']), float(spec['depth'])

    if spec['material'] == 'wood':
        return sections.sawn_lumber(f'{w:g}x{d:g} DF-L No.2', w, d)

    m = _HSS_RE.match(ref)
    if m:
        return sections.hss_rect(_dim(m.group(1)), _dim(m.group(2)), _dim(m.group(3)), ref)
    if ref in sections.W_SHAPES or ref in sections.TEE_SHAPES:
        return sections.get(ref)
    if abs(w - 3.94) < 0.01 and abs(d - 5.83) < 0.01:
        return sections.get('W6X8.5')
    if abs(w - 6.5) < 0.01 and abs(d - 7.93) < 0.01:
        return sections.get('W8X24')

    t = sections.DEFAULT_WALL.get(round(w, 2)) or sections.DEFAULT_WALL[
        min(sections.DEFAULT_WALL, key=lambda k: abs(k - w))]
    s = sections.hss_rect(w, d, t)
    return sections.Section(**{**s.as_dict(),
                               'note': f'assumed lightest wall for {w:g} in. envelope'})


# ---------------------------------------------------------------------------
# loading the COMPAS file
# ---------------------------------------------------------------------------

def lineages() -> list[str]:
    pat = re.compile(r'^frame-(\d{8})\.(\d{2})-([a-z0-9-]+)\.compas\.json$')
    return sorted({m.group(3) for p in FRAME_DIR.iterdir()
                   if (m := pat.match(p.name))})


def latest_path(description: str | None = DEFAULT_LINEAGE) -> Path:
    """Newest model of one lineage. Pass ``None`` to search across all of them."""
    pat = re.compile(r'^frame-(\d{8})\.(\d{2})-([a-z0-9-]+)\.compas\.json$')
    found = sorted((m.groups() + (p,)) for p in FRAME_DIR.iterdir()
                   if (m := pat.match(p.name)) and
                   (description is None or m.group(3) == description))
    if not found:
        raise FileNotFoundError(
            f'no frame model for lineage {description!r} in {FRAME_DIR} '
            f'(present: {", ".join(lineages()) or "none"})')
    return found[-1][3]


def load(path: Path | None = None, lineage: str | None = DEFAULT_LINEAGE) -> Frame:
    path = Path(path) if path else latest_path(lineage)
    raw = json.loads(path.read_text())
    spec, graph = raw['specification'], raw['joint_graph']['data']

    nodes = {k.strip("'"): dict(v) for k, v in graph['node'].items()}
    segments: list[tuple[str, str, str]] = []
    links: list[tuple[str, str, str]] = []
    for u, nbrs in graph['edge'].items():
        for v, attr in nbrs.items():
            i, j = u.strip("'"), v.strip("'")
            members_here = attr.get('members', ())
            for member in members_here:
                segments.append((member, i, j))
            if not members_here:
                # A joint the geometry model declares but carries on no member --
                # the one case today is the eccentric bearing where the optional
                # east mid column meets E-OB one inch off its axis.  Dropping it
                # would leave that column attached to nothing, so it is carried
                # into the analysis as a rigid link and disclosed as such.
                links.append((i, j, attr.get('kind', 'declared joint')))

    members = {k: dict(v) for k, v in spec['members'].items()}
    frame = Frame(path=path,
                  version=re.search(r'frame-(\d{8}\.\d{2})', path.name).group(1),
                  nodes=nodes, segments=segments, members=members, links=links,
                  schema=spec.get('schema', ''), decks=spec.get('decks', []),
                  # Line loads standing in for structure analysed separately --
                  # the east lean-to handing its share to BE.upper. These were
                  # only ever set by the code that created them, so a model that
                  # stored them loaded back lighter than it was written, and
                  # every member came out slightly under-stressed.
                  extra_loads=[tuple(x) for x in spec.get('extra_loads', [])])
    frame.section_of = {m: resolve_section(v) for m, v in members.items()}

    missing = {m for m, _, _ in segments} - set(members)
    if missing:
        raise ValueError(f'joint graph references unknown members: {sorted(missing)}')
    orphan = set(members) - {m for m, _, _ in segments}
    if orphan:
        raise ValueError(f'members with no segment in the joint graph: {sorted(orphan)}')
    return frame


# ---------------------------------------------------------------------------
# PyNite assembly
# ---------------------------------------------------------------------------

def build(frame: Frame, omit: set[str] | None = None,
          override: dict[str, sections.Section] | None = None) -> tuple[FEModel3D, dict]:
    """Assemble a PyNite model.

    ``omit`` drops whole members, which is how the redundancy study asks "what
    happens without this one".  ``override`` swaps sections, which is how the
    downsizing study asks "is a lighter one still enough".  Returns the model and
    an index mapping member name -> list of element names, in order along the
    member, so results can be gathered per member rather than per element.
    """
    omit = omit or set()
    override = override or {}
    m = FEModel3D()

    for name, p in MATERIALS.items():
        m.add_material(name, p['E'], p['G'], p['nu'], p['rho'], p['fy'])

    live_segments = [(mem, i, j) for mem, i, j in frame.segments if mem not in omit]
    used_nodes = {n for _, i, j in live_segments for n in (i, j)}
    # A support whose only column has been deleted is not a support any more --
    # leaving it in gives an isolated node and a spurious instability warning.
    used_nodes |= {n for n in frame.supports if n in used_nodes}

    for name in sorted(used_nodes):
        m.add_node(name, *to_fe(frame.xyz(name)))

    for name in frame.supports:
        if name not in used_nodes:
            continue        # its column was deleted by the redundancy study
        if frame.nodes[name].get('bearing'):
            # A member bearing on an existing wall is held up, not held still.
            # Restraining it horizontally would hand the frame a lateral support
            # that a seat on a wall top does not provide, and would quietly
            # credit the existing masonry with bracing the new structure.
            m.def_support(name, False, True, False, False, False, False)
        else:
            # Pinned bases: translation held, rotation free.  No moment is
            # assumed at any footing because no foundation has been designed
            # (ASM-005 is open).
            m.def_support(name, True, True, True, False, False, False)

    index: dict[str, list[str]] = {}
    seen_sections: set[str] = set()
    for mem in sorted({mem for mem, _, _ in live_segments}):
        sec = override.get(mem, frame.section_of[mem])
        key = f'{mem}::{sec.name}'
        if key not in seen_sections:
            m.add_section(key, sec.A, sec.Iy, sec.Iz, sec.J)
            seen_sections.add(key)
        mat = frame.material(mem)
        segs = _ordered(frame, [(i, j) for mm, i, j in live_segments if mm == mem])
        names = []
        for k, (i, j) in enumerate(segs):
            el = f'{mem}#{k}'
            m.add_member(el, i, j, mat, key)
            names.append(el)
        # def_releases replaces all flags on an element. Accumulate releases
        # first so setting its j end cannot erase an earlier i-end pin.
        release_flags = {el: {} for el in names}
        if frame.group(mem) in PIN_ENDED_GROUPS and names:
            release_flags[names[0]].update(Ryi=True, Rzi=True)
            release_flags[names[-1]].update(Ryj=True, Rzj=True, Rxj=True)
        for pm, pn in getattr(frame, 'pinned_ends', ()):
            if pm != mem:
                continue
            for el, (i, j) in zip(names, segs):
                if i == pn:
                    release_flags[el].update(Ryi=True, Rzi=True)
                elif j == pn:
                    release_flags[el].update(Ryj=True, Rzj=True)
        for el, flags in release_flags.items():
            if flags:
                m.def_releases(el, **flags)
        index[mem] = names

    if frame.links:
        # Rigid link: stiff enough to transfer force and moment across the joint
        # without adding flexibility, light enough to add no weight.
        m.add_material('link', 29.0e6, 11.2e6, 0.30, 0.0, 50_000.0)
        m.add_section('link', 100.0, 1000.0, 1000.0, 1000.0)
        for k, (i, j, kind) in enumerate(frame.links):
            if i in used_nodes and j in used_nodes:
                m.add_member(f'LINK#{k}', i, j, 'link', 'link')

    return m, index


def _ordered(frame: Frame, pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Order a member's segments head-to-tail along its own axis."""
    if len(pairs) <= 1:
        return pairs
    pts = {n: frame.xyz(n) for p in pairs for n in p}
    ends = [n for n in pts if sum(n in p for p in pairs) == 1]
    origin = pts[min(ends, key=lambda n: pts[n])] if ends else min(pts.values())
    return sorted(pairs,
                  key=lambda p: min(_d2(pts[p[0]], origin), _d2(pts[p[1]], origin)))


def _d2(a, b) -> float:
    return sum((a[k] - b[k]) ** 2 for k in range(3))


if __name__ == '__main__':
    f = load()
    print(f'model     {f.path.name}  (version {f.version})')
    print(f'nodes     {len(f.nodes)}   supports {len(f.supports)}')
    print(f'members   {len(f.members)}   segments {len(f.segments)}')
    print(f'self wt   {f.total_weight():,.0f} lb  ({f.total_weight()/2000:.2f} tons)')
    by = {}
    for mem in f.members:
        by.setdefault(f.group(mem), [0, 0.0])
        by[f.group(mem)][0] += 1
        by[f.group(mem)][1] += f.member_weight(mem)
    print(f'\n{"group":<20}{"n":>4}{"weight lb":>12}')
    for g, (n, w) in sorted(by.items(), key=lambda t: -t[1][1]):
        print(f'{g:<20}{n:>4}{w:>12,.0f}')
    model, idx = build(f)
    print(f'\nPyNite: {len(model.nodes)} nodes, {len(model.members)} elements')
