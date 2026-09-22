"""Conservative bracket: each beam as a simple span between its supports.

The grillage model joins every member rigidly, so a beam gets end restraint from its
column and from the beams crossing it. That is a connection-design assumption nobody
has made yet -- a beam sitting on a column cap plate behaves much closer to pinned.
This puts the other bracket on the answer without re-modelling anything: take the load
the tributary distribution actually delivers to a beam, and carry it on a simply
supported span between that beam's supports, where a support is a column beneath it or
a perpendicular beam framing into it.

Conservative on continuity, optimistic on the supporting beams' own flexibility, so it
is a bracket rather than a second opinion.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import geometry as G                               # noqa: E402

E_STEEL = 29.0e6


def member_areas(tribs):
    """Deck area landing directly on each member, in^2."""
    area = {}
    for t in tribs.values():
        for st in t.strips:
            area[st.member] = area.get(st.member, 0.0) + st.area_in2
    return area


def beam_loads(frame, tribs, live_psf, dead_psf, section_of):
    """Total service load each beam receives: its own strip plus half of every
    joist that lands on it. The joists are pin-ended, so their reactions are
    statically determinate at half the joist load regardless of how the ends move."""
    area = member_areas(tribs)
    out = {}
    for b in frame.members_in('Beams'):
        wl = area.get(b, 0.0) * live_psf / 144.0
        wd = area.get(b, 0.0) * dead_psf / 144.0 + \
            frame.member_length(b) * section_of[b].weight / 12.0
        out[b] = dict(live=wl, dead=wd)
    for j in frame.members_in('Joists'):
        jl = area.get(j, 0.0) * live_psf / 144.0
        jd = area.get(j, 0.0) * dead_psf / 144.0 + \
            frame.member_length(j) * section_of[j].weight / 12.0
        for n in ends_of(frame, j):
            for host in frame.nodes[n].get('members', []):
                if host != j and frame.group(host) == 'Beams':
                    out[host]['live'] += jl / 2.0
                    out[host]['dead'] += jd / 2.0
                    break
    return out


def ends_of(frame, member):
    counts = {}
    for m, i, j in frame.segments:
        if m == member:
            counts[i] = counts.get(i, 0) + 1
            counts[j] = counts.get(j, 0) + 1
    return [n for n, c in counts.items() if c == 1]


def support_stations(frame, beam, columns_only=True):
    """Distance along the beam of each real support.

    ``columns_only`` counts only a column standing underneath. That is the true
    lower bound: a crossing beam is not a rigid support, it deflects too, and
    treating it as one is what made the first version of this check optimistic.
    A beam with fewer than two columns under it falls back to its own two ends,
    and ``column_supported`` in the result says so.
    """
    nodes = sorted({n for m, i, j in frame.segments if m == beam for n in (i, j)},
                   key=lambda n: frame.xyz(n))
    a = frame.xyz(nodes[0])

    def station(n):
        q = frame.xyz(n)
        return round(sum((q[k] - a[k]) ** 2 for k in range(3)) ** 0.5, 4)

    cols = [station(n) for n in nodes
            if any(frame.group(m) == 'Columns'
                   for m in set(frame.nodes[n].get('members', [])) - {beam})]
    cols = sorted(set(cols))
    if len(cols) >= 2:
        return cols, True
    return [station(nodes[0]), station(nodes[-1])], False


def check(frame, tribs, live_psf, dead_psf, section_of):
    """Per beam: longest clear span, simple-span moment and deflection."""
    loads = beam_loads(frame, tribs, live_psf, dead_psf, section_of)
    out = {}
    for b in frame.members_in('Beams'):
        stations, column_supported = support_stations(frame, b)
        total_len = frame.member_length(b)
        if len(stations) < 2:
            continue
        gaps = [(y - x, x, y) for x, y in zip(stations, stations[1:])]
        span, x0, x1 = max(gaps)
        sec = section_of[b]
        wl = loads[b]['live'] / total_len       # lb/in, smeared over the whole beam
        wd = loads[b]['dead'] / total_len
        Mu = (1.2 * wd + 1.6 * wl) * span ** 2 / 8.0
        phiMn = 0.9 * 50_000.0 * sec.Zz
        d_live = 5 * wl * span ** 4 / (384 * E_STEEL * sec.Iz)
        d_tot = 5 * (wl + wd) * span ** 4 / (384 * E_STEEL * sec.Iz)
        out[b] = dict(section=sec.name, clear_span=round(span, 1),
                      w_live=round(wl, 3), w_dead=round(wd, 3),
                      dcr=round(Mu / phiMn, 3),
                      live_ratio=round(span / d_live) if d_live > 1e-9 else 99999,
                      total_ratio=round(span / d_tot) if d_tot > 1e-9 else 99999,
                      supports=len(stations), column_supported=column_supported)
    return out
