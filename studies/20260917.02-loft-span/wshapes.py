"""Wide-flange candidates for the loft span.

``structural-analysis-v6/sections.py`` carries only the two W shapes the current
frame model uses (W6X8.5 and W8X24).  Sizing a 23 ft span needs a ladder, so the
relevant part of the AISC Shapes Database v15.0 is transcribed here: every W6
through W21 shape that could plausibly carry this floor, ordered by weight.

Only strong-axis bending properties matter for a floor beam whose compression
flange is held by the deck, so the table is deliberately narrow: area, depth,
flange width, web and flange thickness, Ix, Sx, Zx, Iy, ry and weight.  Values
are as published [P]; nothing here is computed.
"""
from __future__ import annotations

from dataclasses import dataclass

FY = 50.0        # ksi, A992
E = 29000.0      # ksi


@dataclass(frozen=True)
class WShape:
    name: str
    wt: float        # lb/ft
    A: float         # in^2
    d: float         # in, overall depth
    bf: float        # in
    tw: float        # in
    tf: float        # in
    Ix: float        # in^4, strong axis
    Sx: float        # in^3
    Zx: float        # in^3
    Iy: float        # in^4
    ry: float        # in

    @property
    def nominal_depth(self) -> int:
        """The 'W12' part of the name --- what the architect actually cares about."""
        return int(self.name.split('X')[0][1:])

    @property
    def Mp_kipft(self) -> float:
        """Plastic moment, AISC 360-16 Eq. F2-1."""
        return FY * self.Zx / 12.0

    @property
    def phiMn_kipft(self) -> float:
        """Design flexural strength with the compression flange fully braced."""
        return 0.90 * self.Mp_kipft

    @property
    def phiVn_kip(self) -> float:
        """Design shear, AISC 360-16 Sec. G2.1 with Cv = 1.0 for rolled I shapes."""
        return 1.00 * 0.6 * FY * self.d * self.tw


#: name -> (wt, A, d, bf, tw, tf, Ix, Sx, Zx, Iy, ry)
_TABLE = {
    'W6X8.5': (8.5, 2.52, 5.83, 3.94, 0.170, 0.195, 14.9, 5.10, 5.73, 1.99, 0.890),
    'W6X9':   (9.0, 2.68, 5.90, 3.94, 0.170, 0.215, 16.4, 5.56, 6.23, 2.19, 0.905),
    'W6X12':  (12.0, 3.55, 6.03, 4.00, 0.230, 0.280, 22.1, 7.31, 8.30, 2.99, 0.918),
    'W6X16':  (16.0, 4.74, 6.28, 4.03, 0.260, 0.405, 32.1, 10.2, 11.7, 4.43, 0.967),
    'W8X10':  (10.0, 2.96, 7.89, 3.94, 0.170, 0.205, 30.8, 7.81, 8.87, 2.09, 0.841),
    'W8X13':  (13.0, 3.84, 7.99, 4.00, 0.230, 0.255, 39.6, 9.91, 11.4, 2.73, 0.843),
    'W8X15':  (15.0, 4.44, 8.11, 4.015, 0.245, 0.315, 48.0, 11.8, 13.6, 3.41, 0.876),
    'W8X18':  (18.0, 5.26, 8.14, 5.25, 0.230, 0.330, 61.9, 15.2, 17.0, 7.97, 1.23),
    'W8X21':  (21.0, 6.16, 8.28, 5.27, 0.250, 0.400, 75.3, 18.2, 20.4, 9.77, 1.26),
    'W8X24':  (24.0, 7.08, 7.93, 6.50, 0.245, 0.400, 82.7, 20.9, 23.1, 18.3, 1.61),
    'W10X12': (12.0, 3.54, 9.87, 3.96, 0.190, 0.210, 53.8, 10.9, 12.6, 2.18, 0.785),
    'W10X15': (15.0, 4.41, 9.99, 4.00, 0.230, 0.270, 68.9, 13.8, 16.0, 2.89, 0.810),
    'W10X17': (17.0, 4.99, 10.1, 4.01, 0.240, 0.330, 81.9, 16.2, 18.7, 3.56, 0.845),
    'W10X19': (19.0, 5.62, 10.2, 4.02, 0.250, 0.395, 96.3, 18.8, 21.6, 4.29, 0.874),
    'W10X22': (22.0, 6.49, 10.2, 5.75, 0.240, 0.360, 118.0, 23.2, 26.0, 11.4, 1.33),
    'W10X26': (26.0, 7.61, 10.3, 5.77, 0.260, 0.440, 144.0, 27.9, 31.3, 14.1, 1.36),
    'W12X14': (14.0, 4.16, 11.9, 3.97, 0.200, 0.225, 88.6, 14.9, 17.4, 2.36, 0.753),
    'W12X16': (16.0, 4.71, 12.0, 3.99, 0.220, 0.265, 103.0, 17.1, 20.1, 2.82, 0.773),
    'W12X19': (19.0, 5.57, 12.2, 4.01, 0.235, 0.350, 130.0, 21.3, 24.7, 3.76, 0.822),
    'W12X22': (22.0, 6.48, 12.3, 4.03, 0.260, 0.425, 156.0, 25.4, 29.3, 4.66, 0.848),
    'W12X26': (26.0, 7.65, 12.2, 6.49, 0.230, 0.380, 204.0, 33.4, 37.2, 17.3, 1.51),
    'W12X30': (30.0, 8.79, 12.3, 6.52, 0.260, 0.440, 238.0, 38.6, 43.1, 20.3, 1.52),
    'W14X22': (22.0, 6.49, 13.7, 5.00, 0.230, 0.335, 199.0, 29.0, 33.2, 7.00, 1.04),
    'W14X26': (26.0, 7.69, 13.9, 5.03, 0.255, 0.420, 245.0, 35.3, 40.2, 8.91, 1.08),
    'W14X30': (30.0, 8.85, 13.8, 6.73, 0.270, 0.385, 291.0, 42.0, 47.3, 19.6, 1.49),
    'W16X26': (26.0, 7.68, 15.7, 5.50, 0.250, 0.345, 301.0, 38.4, 44.2, 9.59, 1.12),
    'W16X31': (31.0, 9.13, 15.9, 5.53, 0.275, 0.440, 375.0, 47.2, 54.0, 12.4, 1.17),
    'W18X35': (35.0, 10.3, 17.7, 6.00, 0.300, 0.425, 510.0, 57.6, 66.5, 15.3, 1.22),
    'W18X40': (40.0, 11.8, 17.9, 6.02, 0.315, 0.525, 612.0, 68.4, 78.4, 19.1, 1.27),
    'W21X44': (44.0, 13.0, 20.7, 6.50, 0.350, 0.450, 843.0, 81.6, 95.4, 20.7, 1.26),
}

CATALOG: dict[str, WShape] = {
    n: WShape(n, *vals) for n, vals in _TABLE.items()
}

#: Every candidate, lightest first --- the order a sizing search should walk.
LADDER: list[WShape] = sorted(CATALOG.values(), key=lambda s: (s.wt, s.d))


def get(name: str) -> WShape:
    return CATALOG[name]


def by_nominal_depth() -> dict[int, list[WShape]]:
    """Candidates grouped by nominal depth, each group lightest first."""
    out: dict[int, list[WShape]] = {}
    for s in LADDER:
        out.setdefault(s.nominal_depth, []).append(s)
    return out


if __name__ == '__main__':
    print(f"{'shape':<10}{'lb/ft':>7}{'d':>7}{'Ix':>8}{'Sx':>7}{'Zx':>7}"
          f"{'phiMn':>9}{'phiVn':>8}")
    print(f"{'':<10}{'':>7}{'in':>7}{'in^4':>8}{'in^3':>7}{'in^3':>7}"
          f"{'k-ft':>9}{'kip':>8}")
    for s in LADDER:
        print(f'{s.name:<10}{s.wt:7.1f}{s.d:7.2f}{s.Ix:8.1f}{s.Sx:7.1f}{s.Zx:7.1f}'
              f'{s.phiMn_kipft:9.1f}{s.phiVn_kip:8.1f}')
