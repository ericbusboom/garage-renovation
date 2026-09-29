"""Parallel tarp cables from the outbuilding roof edge to a fence cable.

Roof edge (Eric, 2026-09-29): the outbuilding roof overhangs the pillar by
10 in to the south and 11 in to the west and runs 8 ft south-to-north, so
its west edge is the line x = 24 from y = 160 (R1, south end) to y = 64
(R3, north end), with R2 at the middle, y = 112. Page up is south.

A cable runs P4 -> P3 -> P2 along the fence. Cables from R1, R2, R3 run
west and clip to it at N1, N2, N3. For each R cable to run due west
(parallel, for a square-cornered tarp laid over them), its fence node must
sit at the same y as its R point. The R cables then load the fence cable
at right angles to the fence, like point loads on a string: the component
of fence-cable tension along the fence, H, is constant in each span
(P4-P3 and P3-P2), and the fence cable bows east by d = M / H, where M is
the moment of those point loads on a simple span. So:

  * the clip points go on the fence cable at the R points' y; and
  * H sets how far the clips bow in off the fence; choose H for the bow you
    will accept. A tighter fence cable keeps the tarp closer to the fence.

Equal H in both spans leaves P3 with no pull along the fence, only
sideways; the end posts P4 and P2 take H along the fence line.

Heights: posts 7'-0" (patio_site.py). R height is not yet given: R_Z below
is assumed and only moves node heights, not the plan answer. Heights come
from vertical equilibrium with the same force densities (tension/plan
length) as the plan solve.

Run from the repository root:
    archive/.venv/bin/python studies/20260927.01-patio-awning/tarp_cables.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from awning import draw_site, ftin  # noqa: E402
from patio_site import PILLAR, anchor, trailer_sdf  # noqa: E402

ROOF_X = PILLAR[1] + 11                      # west edge of the roof
ROOF_Y1 = PILLAR[3] + 10                     # south end
ROOF_Y0 = ROOF_Y1 - 96                       # 8 ft long
R = {"R1": (ROOF_X, ROOF_Y1), "R2": (ROOF_X, (ROOF_Y0 + ROOF_Y1) / 2), "R3": (ROOF_X, ROOF_Y0)}
R_Z = 101.0                                  # ASSUMED roof-edge attachment height, in
FENCE_X = 174
SPANS = [("P4", "P3", ["R1", "R2"]), ("P3", "P2", ["R3"])]


def solve(bow, direct_r2=False):
    """Fence nodes and tensions for a given largest bow (in) off the fence line.

    Tensions are per unit tension T in each R cable. direct_r2 ties R2
    straight to P3 instead of a clip on the fence cable.
    """
    nodes, segs, H = {}, [], {}
    for a, b, loads in SPANS:
        loads = [r for r in loads if not (direct_r2 and r == "R2")]
        ya, yb = anchor(a)[1], anchor(b)[1]
        L = ya - yb
        pts = sorted(((ya - R[r][1], r) for r in loads))      # distance from a
        # simple-span moment from unit loads, then H for the target bow
        def M(s):
            ra = sum(1 * (L - p) / L for p, _ in pts)
            return ra * s - sum(1 * (s - p) for p, _ in pts if s > p)
        Mmax = max(M(p) for p, _ in pts)
        H[f"{a}-{b}"] = Mmax / bow
        chain = [(a, anchor(a)[:2])]
        for p, r in pts:
            n = "N" + r[1]
            nodes[n] = (FENCE_X - M(p) / H[f"{a}-{b}"], ya - p)
            chain.append((n, nodes[n]))
        chain.append((b, anchor(b)[:2]))
        for (n1, p1), (n2, p2) in zip(chain[:-1], chain[1:]):
            dy = abs(p1[1] - p2[1])
            Lp = np.hypot(p1[0] - p2[0], p1[1] - p2[1])
            segs.append((n1, n2, H[f"{a}-{b}"] * Lp / dy, Lp))   # plan tension, length
    for r in R:
        end = "P3" if (direct_r2 and r == "R2") else "N" + r[1]
        pe = anchor(end)[:2] if end in ("P3",) else nodes[end]
        Lp = np.hypot(R[r][0] - pe[0], R[r][1] - pe[1])
        segs.append((r, end, 1.0, Lp))
    # heights: vertical equilibrium, q = plan tension / plan length
    fixedz = {**{r: R_Z for r in R}, **{p: anchor(p)[2] for p in ("P2", "P3", "P4")}}
    names = list(nodes)
    A, rhs = np.zeros((len(names), len(names))), np.zeros(len(names))
    for n1, n2, t, Lp in segs:
        q = t / Lp
        for s, o in ((n1, n2), (n2, n1)):
            if s in names:
                i = names.index(s)
                A[i, i] -= q
                if o in names:
                    A[i, names.index(o)] += q
                else:
                    rhs[i] -= q * fixedz[o]
    z = dict(zip(names, np.linalg.solve(A, rhs))) if names else {}
    return nodes, z, segs, H


def draw(ax, bow, direct_r2, title):
    nodes, z, segs, H = solve(bow, direct_r2)
    draw_site(ax, ties=())
    # roof edge
    ax.plot([ROOF_X, ROOF_X], [ROOF_Y0, ROOF_Y1], color="#333", lw=3, zorder=6)
    ax.plot([PILLAR[0], ROOF_X, ROOF_X, PILLAR[0]], [ROOF_Y1, ROOF_Y1, ROOF_Y0, ROOF_Y0],
            color="#333", lw=1, ls="--", zorder=6)
    ax.text(ROOF_X - 3, ROOF_Y0 - 10, "roof edge", ha="right", fontsize=8)
    # tarp footprint between R1 and R3 lines
    tarp = [R["R1"], (nodes["N1"][0], R["R1"][1]), (nodes["N3"][0], R["R3"][1]), R["R3"]]
    ax.add_patch(Polygon(tarp, fc="#6aa84f", alpha=0.18, zorder=3))

    def xy(n):
        return R[n] if n in R else nodes[n] if n in nodes else anchor(n)[:2]
    tmax = max(t for *_, t, _ in segs)
    for n1, n2, t, _ in segs:
        p1, p2 = xy(n1), xy(n2)
        col = "#1f5fa8" if n1 in R else "#b3261e"
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=col, lw=1.2 + 2.5 * t / tmax, zorder=5)
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ax.text(mx, my, f"{t:.1f}T", fontsize=8, ha="center", va="center", zorder=8,
                bbox=dict(fc="white", ec="none", pad=0.5, alpha=0.85))
    for r, p in R.items():
        ax.plot(*p, "s", color="#333", ms=6, zorder=9)
        ax.text(p[0] - 4, p[1] + 4, r, ha="right", fontsize=9, fontweight="bold", zorder=9)
    for n, p in nodes.items():
        ax.plot(*p, "o", color="#b3261e", ms=6, mec="white", zorder=9)
        ax.text(p[0] - 5, p[1] - 11, f"{n}  {FENCE_X - p[0]:.1f}″ off fence\n{ftin(z[n])} high",
                ha="right", fontsize=8, color="#b3261e", zorder=9)
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    return nodes, z, segs, H


def main():
    rows = []
    for bow in (3, 6, 9, 12, 18):
        for d in (False, True):
            nodes, z, segs, H = solve(bow, d)
            fence_max = max(t for n1, n2, t, _ in segs if n1 not in R)
            rows.append({"bow_in": bow, "R2_to_P3": d,
                         "H_over_T": {k: round(v, 2) for k, v in H.items()},
                         "fence_cable_max_over_T": round(fence_max, 2),
                         "nodes": {n: [round(p[0], 1), round(p[1], 1), round(z[n], 1)]
                                   for n, p in nodes.items()}})
    fig, axs = plt.subplots(1, 2, figsize=(15, 8.6))
    draw(axs[0], 6, False, "A · three clips on the fence cable (6″ largest bow)")
    draw(axs[1], 6, True, "B · R2 straight to P3, two clips (6″ largest bow)")
    lines = ["Numbers on cables: tension as a multiple of T, the pull set in each R cable. "
             "R cables run due west (parallel). Green: tarp footprint.",
             "Fence cable tension along the fence, H, vs the largest bow of the clips off the fence:"]
    for bow in (3, 6, 9, 12, 18):
        a = next(r for r in rows if r["bow_in"] == bow and not r["R2_to_P3"])
        b = next(r for r in rows if r["bow_in"] == bow and r["R2_to_P3"])
        lines.append(f"   bow {bow:2d}″:  A  H = {a['H_over_T']['P4-P3']:.1f}T / {a['H_over_T']['P3-P2']:.1f}T"
                     f"    B  H = {b['H_over_T']['P4-P3']:.1f}T / {b['H_over_T']['P3-P2']:.1f}T"
                     "   (P4–P3 span / P3–P2 span)")
    lines.append(f"R points at {ftin(R_Z)} ASSUMED (roof-edge height not given); "
                 "posts 7′-0″. In B, R2–P3 is 8″ off parallel over its length (≈3°).")
    fig.text(0.02, 0.01, "\n".join(lines), fontsize=9, family="monospace", va="bottom")
    fig.subplots_adjust(left=0.03, right=0.99, top=0.95, bottom=0.2, wspace=0.05)
    fig.savefig(HERE / "tarp-cables.png", dpi=120)
    (HERE / "tarp_cables.json").write_text(json.dumps(rows, indent=1))
    clr = min(trailer_sdf(x, R["R1"][1]) for x in np.linspace(ROOF_X, FENCE_X, 200))
    print(json.dumps(rows[2:4], indent=1), "\nR1 line clearance to trailer (plan):", round(clr, 1))


if __name__ == "__main__":
    main()
