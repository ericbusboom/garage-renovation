#!/usr/bin/env python
"""Follow-up to south_brace_study: the other column sets under the two brace
schemes that rescued S1, S2 and S3 one at a time, and lighter slope bracing."""
from __future__ import annotations

import json
import time
from pathlib import Path

import analysis as A
import completion as C
import south_brace_study as SB
from column_study import LIVE, recommended
from project_paths import VIZ_DIR

OUT = VIZ_DIR / 'south-brace-followup.json'


def slope_ends(g):
    """Slope-plane X in the two end bays only (against W.slope and E.slope)."""
    added = SB.brace_slope(g, halves=False)
    keep = [m for m in added if m.startswith(('BR-SL-0-', 'BR-SL-5-'))]
    import owner_revisions as OR
    for m in added:
        if m not in keep:
            OR._drop(g, m)
    return keep


def a_ends_heavy(g):
    SB.BRACE = ('HSS2-1/2X2-1/2X3/16', 2.5, 2.5)
    try:
        return SB.brace_bs_rw1(g, 'ends')
    finally:
        SB.BRACE = ('HSS2-1/2X2-1/2X1/8', 2.5, 2.5)


def slope_light(g):
    SB.BRACE = ('HSS2X2X1/8', 2.0, 2.0)
    try:
        return SB.brace_slope(g, halves=False)
    finally:
        SB.BRACE = ('HSS2-1/2X2-1/2X1/8', 2.5, 2.5)


def main():
    t0 = time.time()
    built, params, final, combos = recommended()
    base = A.run(built, params, LIVE, combos=combos)
    B = lambda g: SB.brace_slope(g, halves=False)
    Aends = lambda g: SB.brace_bs_rw1(g, 'ends')
    plan = [
        ('S1 + A-ends 3/16', ['S1'], a_ends_heavy),
        ('S1 + B-ends', ['S1'], slope_ends),
        ('S1 + B-full HSS2X2', ['S1'], slope_light),
        ('S1+W1 + B-full', ['S1', 'W1'], B),
        ('S1+W2 + B-full', ['S1', 'W2'], B),
        ('S1+SW0+W1 + B-full', ['S1', 'SW0', 'W1'], B),
        ('S1+SW0+W2 + B-full', ['S1', 'SW0', 'W2'], B),
        ('S1+W1+W2 + B-full', ['S1', 'W1', 'W2'], B),
        ('S1+W1 + A-ends', ['S1', 'W1'], Aends),
        ('S1+W2 + A-ends', ['S1', 'W2'], Aends),
        ('S1+W1+W2 + A-ends', ['S1', 'W1', 'W2'], Aends),
        ('S1+S2 + B-full', ['S1', 'S2'], B),
        ('S1+S3 + B-full', ['S1', 'S3'], B),
        ('S3 alone', ['S3'], None),
        ('S2 alone', ['S2'], None),
    ]
    out = [SB.run(built, params, combos, base, tag, cols, fn) for tag, cols, fn in plan]
    OUT.write_text(json.dumps(dict(generated=time.strftime('%Y-%m-%d %H:%M'),
                                   live_case=LIVE, variants=out), indent=1, default=str))
    print(f'\nwrote {OUT}  ({time.time() - t0:.0f}s total)')


if __name__ == '__main__':
    main()
