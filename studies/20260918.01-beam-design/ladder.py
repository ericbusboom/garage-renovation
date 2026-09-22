"""The W-shape sizing ladder, as ``sections.Section`` objects.

``loft-span-study/wshapes.py`` already carries 30 AISC v15 shapes for this project,
but deliberately only the strong-axis properties a floor beam needs. The analysis
code wants four more: Sy, Zy, J and rx. Rather than transcribe another table from
somewhere else, those four are derived from the published dimensions:

    Sy = Iy / (bf/2)                                    exact for an I shape
    Zy = tf*bf^2/2 + (d - 2tf)*tw^2/4                   ignores the fillets, ~0.5% low
    J  = (2*bf*tf^3 + (d - 2tf)*tw^3) / 3               ignores the fillets, ~10% low
    rx = sqrt(Ix / A)                                   exact

``validate()`` checks all four against the two shapes that appear in both this
project's tables with published values, W8X24 and W14X22. J comes out low, which is
the conservative direction for lateral-torsional buckling, so it is left alone.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'loft-span-study'))
sys.path.insert(0, str(ROOT / 'structural-analysis-v6'))
import wshapes                                     # noqa: E402
import sections                                    # noqa: E402


def derive(w) -> dict:
    return dict(
        A=w.A, d=w.d, bf=w.bf, tw=w.tw, tf=w.tf, Ix=w.Ix, Iy=w.Iy,
        Zx=w.Zx, Sx=w.Sx, ry=w.ry, wt=w.wt,
        Sy=w.Iy / (w.bf / 2.0),
        Zy=w.tf * w.bf ** 2 / 2.0 + (w.d - 2 * w.tf) * w.tw ** 2 / 4.0,
        J=(2 * w.bf * w.tf ** 3 + (w.d - 2 * w.tf) * w.tw ** 3) / 3.0,
        rx=(w.Ix / w.A) ** 0.5,
    )


def section(name: str) -> sections.Section:
    return sections.wide_flange(name, **derive(wshapes.get(name)))


#: Every candidate, lightest first — the order a sizing search walks.
LADDER = [s.name for s in wshapes.LADDER]
SECTIONS = {n: section(n) for n in LADDER}


def validate() -> list[dict]:
    """Derived vs published, for the shapes carried in both project tables."""
    out = []
    for name in ('W8X24', 'W14X22'):
        pub = sections.W_SHAPES[name]
        got = derive(wshapes.get(name))
        for key in ('Sy', 'Zy', 'J', 'rx'):
            err = (got[key] - pub[key]) / pub[key] * 100.0
            out.append(dict(shape=name, property=key, published=pub[key],
                            derived=round(got[key], 4), error_pct=round(err, 2)))
    return out


if __name__ == '__main__':
    print(f'{"shape":<10}{"property":<10}{"published":>11}{"derived":>10}{"error %":>9}')
    for r in validate():
        print(f'{r["shape"]:<10}{r["property"]:<10}{r["published"]:>11}'
              f'{r["derived"]:>10}{r["error_pct"]:>9}')
    print(f'\n{len(LADDER)} shapes, lightest first:')
    print(f'{"shape":<10}{"lb/ft":>7}{"d":>7}{"Iz":>8}{"Zz":>7}  compact')
    for n in LADDER:
        s = SECTIONS[n]
        print(f'{s.name:<10}{s.weight:7.1f}{s.d:7.2f}{s.Iz:8.1f}{s.Zz:7.1f}  '
              f'{"Y" if s.compact else "N"}')
