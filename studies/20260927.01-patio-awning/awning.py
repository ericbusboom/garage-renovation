"""Awning form-finding and cable-junction equilibrium for the work patio.

Two figures:

  awning-2-membrane.png  -- the fabric as a six-corner tensioned sheet,
      T1-P4-P3-P2-P1-T2, clamped straight along the pillar face T2-T1, with
      a cable sewn into each free edge. Form-found by the force density
      method (Schek 1974): every fabric link carries force density q_m, each
      edge cable q_c. Under uniform fabric pull an edge cable takes a
      circular arc (radius R = cable tension / fabric tension per length);
      q_c is tuned per edge so each arc sags a set fraction of its chord.

  awning-3-junctions.png -- a straight-cable support net with three-way
      junctions: T1, P3, P4 meet at node A; T2 pulls the P1-P2 cable at one
      node B, or at two nodes B1, B2; T3-P1 is a plain cable. For a node
      held only by cables, equilibrium fixes the ratio of the cable
      tensions from the plan position alone, and puts the node in the plane
      of its anchors (for a 3-way node). Positions are searched on a grid
      for the most even tensions (max/min), inside the limits Eric set:
      A 3-4 ft off the fence with the T1 leg along the patio front, and the
      P1-P2 cable kept near the north line, its junction(s) mid-span.

Prestress only: no wind, rain or self weight. Tensions are ratios.

Run from the repository root:
    archive/.venv/bin/python studies/20260927.01-patio-awning/awning.py
"""

import json
import sys
from itertools import product
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyBboxPatch, PathPatch, Rectangle  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
from scipy.sparse import coo_matrix  # noqa: E402
from scipy.sparse.linalg import spsolve  # noqa: E402
from scipy.spatial import Delaunay  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from patio_site import (PATIO_N, PILLAR, POSTS, TIES, TRAILER_R,  # noqa: E402
                        TRAILER_W, TRAILER_X0, TRAILER_Y0, anchor, trailer_sdf)

FENCE_X = 174
SAG_RATIO = 0.10      # edge-cable sag / chord, a usual starting point for fabric
MESH = 6.0            # fabric mesh spacing, in


def ftin(n):
    f, i = divmod(round(n), 12)
    return f"{f}′-{i}″"


# ---------------------------------------------------------------- site plot

def draw_site(ax, posts=("P1", "P2", "P3", "P4"), ties=("T1", "T2")):
    ax.add_patch(Rectangle((0, 0), FENCE_X, PATIO_N, fc="#f6f1e7", ec="#999",
                           ls="--", lw=0.8, zorder=0))
    ax.plot([FENCE_X, FENCE_X], [-6, 216], color="#7a5a33", lw=2, zorder=1)
    ax.text(FENCE_X + 4, 40, "fence (west line)", rotation=90, fontsize=8,
            color="#7a5a33", va="bottom")
    ax.add_patch(Rectangle((PILLAR[0], PILLAR[2]), PILLAR[1] - PILLAR[0],
                           PILLAR[3] - PILLAR[2], fc="#bbb", ec="#666", zorder=2))
    # Airstream front with its 2 ft corner fillets, running off the top
    ax.add_patch(FancyBboxPatch((TRAILER_X0 + TRAILER_R, TRAILER_Y0 + TRAILER_R),
                                TRAILER_W - 2 * TRAILER_R, 200,
                                boxstyle=f"round,pad={TRAILER_R}", fc="#dde3ea",
                                ec="#556", lw=1.2, zorder=1))
    ax.text(TRAILER_X0 + TRAILER_W / 2, TRAILER_Y0 + 40, "Airstream",
            ha="center", color="#334", fontsize=10)
    for name in posts:
        x, y, w, d, h = POSTS[name]
        ax.add_patch(Rectangle((x - w / 2, y - d / 2), w, d, fc="#ab7942", ec="k", zorder=5))
        ax.text(x + (8 if x > 87 else -8), y - 12 if y < 50 else y + 6,
                f"{name}\n{ftin(h)}", ha="left" if x > 87 else "right",
                fontsize=9, fontweight="bold", zorder=6)
    for name in ties:
        x, y, z = anchor(name)
        ax.plot(x, y, "o", color="#1f5fa8", ms=6, zorder=6, mec="white")
        ax.text(x - 3, y + (5 if name == "T1" else -12), name, ha="right",
                fontsize=9, fontweight="bold", color="#1f5fa8", zorder=6)
    ax.annotate("S", xy=(-30, 250), xytext=(-30, 225), ha="center", fontsize=12,
                fontweight="bold", arrowprops=dict(arrowstyle="-|>", color="k"))
    ax.set_aspect("equal")
    ax.set_xlim(-45, 215)
    ax.set_ylim(-25, 262)
    ax.set_xticks(range(0, 181, 24))
    ax.set_yticks(range(0, 241, 24))
    ax.set_xticklabels([f"{t // 12}′" for t in range(0, 181, 24)], fontsize=7)
    ax.set_yticklabels([f"{t // 12}′" for t in range(0, 241, 24)], fontsize=7)
    ax.grid(color="#eee", lw=0.6)
    ax.set_axisbelow(True)


# ------------------------------------------------------------ force density

def fdm(X, fixed, edges, q):
    """Force density solve. X (n,3) start/anchor coords; edges (m,2); q (m,)."""
    n, m = len(X), len(edges)
    C = coo_matrix((np.r_[np.ones(m), -np.ones(m)],
                    (np.r_[np.arange(m), np.arange(m)], np.r_[edges[:, 0], edges[:, 1]])),
                   shape=(m, n)).tocsr()
    D = (C.T @ coo_matrix((q, (np.arange(m), np.arange(m)))) @ C).tocsr()
    free = ~fixed
    Dff, Dfx = D[free][:, free], D[free][:, fixed]
    Y = X.copy()
    for k in range(3):
        Y[free, k] = spsolve(Dff.tocsc(), -Dfx @ X[fixed, k])
    return Y


# ------------------------------------------------- image 2: fabric membrane

CORNERS = ["T1", "P4", "P3", "P2", "P1", "T2"]
CLAMPED = ("T2", "T1")                          # straight along the pillar face


def membrane():
    pts, fixed, edge_of = [], [], []            # boundary nodes first
    ring = CORNERS + [CORNERS[0]]
    for a, b in zip(ring[:-1], ring[1:]):
        pa, pb = np.array(anchor(a), float), np.array(anchor(b), float)
        n = max(2, int(np.ceil(np.linalg.norm(pb[:2] - pa[:2]) / MESH)))
        for i in range(n):
            pts.append(pa + (pb - pa) * i / n)
            fixed.append(i == 0 or (a, b) == CLAMPED)
            edge_of.append(f"{a}-{b}")
    nb = len(pts)
    poly = MPath(np.array([anchor(c)[:2] for c in CORNERS]))
    gx, gy = np.meshgrid(np.arange(-6, 190, MESH), np.arange(-6, 220, MESH))
    cand = np.c_[gx.ravel(), gy.ravel()]
    inside = poly.contains_points(cand, radius=-MESH * 0.7) | poly.contains_points(
        cand, radius=MESH * 0.7)
    bnd = np.array(pts)[:, :2]
    far = np.min(np.linalg.norm(cand[:, None] - bnd[None], axis=2), axis=1) > 0.6 * MESH
    cand = cand[inside & far & poly.contains_points(cand)]
    X = np.vstack([np.array(pts), np.c_[cand, np.full(len(cand), 90.0)]])
    fixed = np.r_[fixed, np.zeros(len(cand), bool)]
    tri = Delaunay(X[:, :2])
    keep = poly.contains_points(X[tri.simplices, :2].mean(axis=1))
    T = tri.simplices[keep]
    E = {tuple(sorted(e)) for t in T for e in ((t[0], t[1]), (t[1], t[2]), (t[0], t[2]))}
    E = np.array(sorted(E))
    # boundary links (consecutive boundary nodes) are edge cable, rest fabric
    nxt = {i: (i + 1) % nb for i in range(nb)}
    def link_edge(i, j):
        if i >= nb or j >= nb:
            return ""
        if j == nxt[i]:
            return edge_of[i]
        if i == nxt[j]:
            return edge_of[j]
        return ""
    cable_edge = np.array([link_edge(i, j) for i, j in E])
    is_cable = cable_edge != ""
    names = [f"{a}-{b}" for a, b in zip(ring[:-1], ring[1:]) if (a, b) != CLAMPED]
    qc = {nm: 20.0 for nm in names}

    def solve():
        q = np.ones(len(E))
        for nm in names:
            q[cable_edge == nm] = qc[nm]
        return fdm(X, fixed, E, q), q

    def sags(Y):
        out = {}
        for nm in names:
            a, b = nm.split("-")
            pa, pb = np.array(anchor(a)[:2]), np.array(anchor(b)[:2])
            idx = [i for i in range(nb) if edge_of[i] == nm and not fixed[i]]
            u = (pb - pa) / np.linalg.norm(pb - pa)
            nrm = np.array([-u[1], u[0]])
            off = (Y[idx, :2] - pa) @ nrm
            out[nm] = (float(np.max(np.abs(off))), float(np.linalg.norm(pb - pa)))
        return out

    for _ in range(40):                         # tune each edge to the target sag
        Y, q = solve()
        s = sags(Y)
        err = max(abs(v[0] / v[1] - SAG_RATIO) for v in s.values())
        if err < 0.002:
            break
        for nm, (sg, c) in s.items():
            qc[nm] *= (sg / c / SAG_RATIO) ** 0.9
    Y, q = solve()
    s = sags(Y)
    # edge-cable tension relative to fabric: circular-arc radius, R = c^2/8s + s/2
    res = {}
    for nm, (sg, c) in s.items():
        R = c * c / (8 * sg) + sg / 2
        res[nm] = {"chord_in": round(c, 1), "sag_in": round(sg, 1), "radius_in": round(R, 1)}
    # fabric slope (drainage)
    P = Y[T]
    nrm = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    nrm /= np.linalg.norm(nrm, axis=1)[:, None]
    slope = np.degrees(np.arccos(np.abs(nrm[:, 2])))
    return Y, T, E, is_cable, nb, res, slope


def fig_membrane():
    Y, T, E, is_cable, nb, res, slope = membrane()
    fig = plt.figure(figsize=(13, 8.2))
    ax = fig.add_axes([0.03, 0.06, 0.52, 0.84])
    draw_site(ax)
    tc = ax.tricontourf(Y[:, 0], Y[:, 1], T, Y[:, 2], levels=np.arange(70, 104, 2),
                        cmap="Blues", alpha=0.55, zorder=3)
    cs = ax.tricontour(Y[:, 0], Y[:, 1], T, Y[:, 2], levels=np.arange(72, 102, 4),
                       colors="#1f5fa8", linewidths=0.6, zorder=3)
    ax.clabel(cs, fmt=lambda v: ftin(v), fontsize=7)
    ring = list(range(nb)) + [0]
    ax.plot(Y[ring, 0], Y[ring, 1], color="#b3261e", lw=2.2, zorder=4)
    for nm, r in res.items():
        a, b = nm.split("-")
        pa, pb = np.array(anchor(a)[:2]), np.array(anchor(b)[:2])
        ax.plot(*np.c_[pa, pb], color="#b3261e", lw=0.7, ls=":", zorder=4)
    fig.colorbar(tc, ax=ax, shrink=0.5, pad=0.01, label="fabric height, in")
    ax.set_title("2 · Fabric awning with sewn-in edge cables (plan)", loc="left",
                 fontsize=12, fontweight="bold")
    # 3-D view
    ax3 = fig.add_axes([0.56, 0.36, 0.43, 0.56], projection="3d")
    ax3.plot_trisurf(Y[:, 0], Y[:, 1], Y[:, 2], triangles=T, cmap="Blues",
                     alpha=0.85, lw=0.1, edgecolor="#7aa")
    ax3.plot(Y[ring, 0], Y[ring, 1], Y[ring, 2], color="#b3261e", lw=2)
    for name in ("P1", "P2", "P3", "P4"):
        x, y, z = anchor(name)
        ax3.plot([x, x], [y, y], [0, z], color="#ab7942", lw=4)
        ax3.text(x, y, z + 6, name, fontsize=8)
    ax3.bar3d(PILLAR[0], PILLAR[2], 0, 13, 48, 110, color="#bbb", alpha=0.6)
    ax3.set_box_aspect((174, 208, 110))
    ax3.view_init(elev=24, azim=-120)
    ax3.set_axis_off()
    ax3.set_title("view from the north-east, looking over P1", fontsize=9)
    # notes
    lines = ["Edge cables (sag = 10 % of chord):"]
    for nm, r in res.items():
        lines.append(f"  {nm.replace('-', '–'):7s} chord {ftin(r['chord_in']):>7s}  "
                     f"sag {r['sag_in']:4.0f}″   R {ftin(r['radius_in'])}")
    d = np.array([trailer_sdf(x, y) for x, y, _ in Y[:nb]])
    k = int(np.argmin(d))
    lines += [f"T1–P4 edge passes {max(d[k], 0):.0f}″ (plan) from the Airstream's",
              f"  front corner, at {ftin(Y[k, 2])} high: as tight as the old T2–P4 line.",
              "", "Cable tension = fabric prestress × R.",
              "e.g. 20 lb/ft prestress on T1–P4 (R ≈ "
              f"{res['T1-P4']['radius_in'] / 12:.0f} ft) ≈ {20 * res['T1-P4']['radius_in'] / 12:.0f} lb.",
              f"Fabric slope: min {slope.min():.1f}°, median {np.median(slope):.1f}°.",
              "No interior low point; water runs to P1/P2,",
              "but the fabric is nearly flat by P2: ponding risk.",
              "T2–T1 clamped straight to the pillar face."]
    fig.text(0.58, 0.05, "\n".join(lines), fontsize=9, family="monospace", va="bottom")
    out = HERE / "awning-2-membrane.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return {"edges": res, "trailer_plan_gap_in": round(float(d[k]), 1),
            "edge_height_at_trailer_in": round(float(Y[k, 2]), 1), "slope_min_deg": round(float(slope.min()), 2),
            "slope_median_deg": round(float(np.median(slope)), 2)}


# ----------------------------------------- image 3: three-way cable junctions

def junction_net(nodes, links):
    """Inverse force density for straight-cable nodes at given plan positions.

    nodes: {name: (x, y)} free nodes; links: [(a, b)] between free nodes and
    anchors. Solves plan equilibrium for force densities (a 1-D null space
    when the layout is feasible), then heights from vertical equilibrium.
    Returns (tensions {link: T}, heights {node: z}) with min tension = 1, or
    None if any cable would have to push.
    """
    names = list(nodes)
    A = np.zeros((2 * len(names), len(links)))
    pos = {**{k: np.array(v, float) for k, v in nodes.items()}}
    anc = {}
    for k, (a, b) in enumerate(links):
        for s, t in ((a, b), (b, a)):
            if s in nodes:
                other = pos[t] if t in nodes else np.array(anchor(t)[:2], float)
                i = names.index(s)
                A[2 * i:2 * i + 2, k] += other - pos[s]
        for e in (a, b):
            if e not in nodes:
                anc[e] = anchor(e)
    _, sv, vt = np.linalg.svd(A)
    q = vt[-1]
    if np.abs(A @ q).max() > 1e-8 * np.abs(A).max():
        return None
    q = q if q.sum() > 0 else -q
    if q.min() <= 1e-9:
        return None
    # heights: sum_k q_k (z_other - z_i) = 0 for each free node (linear)
    n = len(names)
    M, rhs = np.zeros((n, n)), np.zeros(n)
    for k, (a, b) in enumerate(links):
        for s, t in ((a, b), (b, a)):
            if s in nodes:
                i = names.index(s)
                M[i, i] -= q[k]
                if t in nodes:
                    M[i, names.index(t)] += q[k]
                else:
                    rhs[i] -= q[k] * anc[t][2]
    z = dict(zip(names, np.linalg.solve(M, rhs)))
    P = {**{k: (*nodes[k], z[k]) for k in names}, **anc}
    T = {}
    for k, (a, b) in enumerate(links):
        T[(a, b)] = q[k] * np.linalg.norm(np.subtract(P[a], P[b]))
    m = min(T.values())
    return {k: v / m for k, v in T.items()}, z


def spread(T):
    return max(T.values()) / min(T.values())


def best_A():
    """Node A (T1, P3, P4): 36-48 in east of the fence, T1 leg near the patio front."""
    best, table = None, []
    for off, y in product(np.arange(36, 48.1, 1), np.arange(138, 162.1, 1)):
        r = junction_net({"A": (FENCE_X - off, y)}, [("T1", "A"), ("A", "P3"), ("A", "P4")])
        if r is None:
            continue
        T, z = r
        p = (FENCE_X - off, y)
        clr = min(trailer_sdf(*(np.array(p) + t * (np.array(anchor("P4")[:2]) - p)))
                  for t in np.linspace(0, 1, 200))
        s = spread(T)
        table.append((off, y, s))
        if clr > 2 and (best is None or s < best[0]):
            best = (s, off, y, T, z, clr)
    s, off, y, T, z, clr = best
    return {"pos": (FENCE_X - off, y), "fence_offset_in": off, "T": T, "z": z["A"],
            "spread": s, "trailer_clear_in": clr, "table": table}


def best_B(dmax):
    """Single node B on the P1-P2 cable, pulled by T2, within dmax of the north line.

    B is kept in the middle third of P1-P2 so it actually holds the fabric
    edge up mid-span; left free, the most even layout slides B into the P1
    corner, where it does nothing.
    """
    best = None
    for x, d in product(np.arange(58, 117, 2), np.arange(4, dmax + 0.1, 1)):
        r = junction_net({"B": (x, d)}, [("P1", "B"), ("B", "P2"), ("T2", "B")])
        if r and (best is None or spread(r[0]) < best[0]):
            best = (spread(r[0]), (x, d), *r)
    s, p, T, z = best
    return {"pos": p, "T": T, "z": z, "spread": s}


def best_B2(dmax):
    """Two nodes B1, B2 on the P1-P2 cable, each pulled by its own leg from T2.

    B1 near the first third point of P1-P2, B2 near the second.
    """
    best = None
    for x1, x2, d1, d2 in product(np.arange(36, 73, 3), np.arange(102, 139, 3),
                                  np.arange(4, dmax + 0.1, 2), np.arange(4, dmax + 0.1, 2)):
        if x2 - x1 < 24:
            continue
        r = junction_net({"B1": (x1, d1), "B2": (x2, d2)},
                         [("P1", "B1"), ("B1", "B2"), ("B2", "P2"), ("T2", "B1"), ("T2", "B2")])
        if r and (best is None or spread(r[0]) < best[0]):
            best = (spread(r[0]), {"B1": (x1, d1), "B2": (x2, d2)}, *r)
    s, p, T, z = best
    return {"pos": p, "T": T, "z": z, "spread": s}


def tradeoff():
    """How hard the P1-P2 cable works as its junction is held nearer the line."""
    rows = []
    for d in (6, 9, 12, 18, 24, 36, 48):
        b = best_B(d)
        T = b["T"]
        rows.append({"dmax_in": d, "B": b["pos"], "spread": round(b["spread"], 2),
                     "P_over_T2": round(max(T[("P1", "B")], T[("B", "P2")]) / T[("T2", "B")], 2)})
    return rows


def fig_junctions(dmax=24):
    A, B, B2, trade = best_A(), best_B(dmax), best_B2(dmax), tradeoff()
    fig, axs = plt.subplots(1, 2, figsize=(15, 8.4))
    for ax, (title, Bres) in zip(axs, (("3a · one junction on P1–P2", B),
                                       ("3b · two T2 legs on P1–P2", B2))):
        draw_site(ax, ties=("T1", "T2", "T3"))
        P = {"A": (*A["pos"], A["z"])}
        if "B" in Bres["pos"] or isinstance(Bres["pos"], tuple):
            pass
        if isinstance(Bres["pos"], tuple):
            P["B"] = (*Bres["pos"], Bres["z"]["B"])
        else:
            for k, v in Bres["pos"].items():
                P[k] = (*v, Bres["z"][k])
        links = {**{k: v for k, v in A["T"].items()}, **Bres["T"]}
        allT = list(links.values())
        tmax = max(allT)

        def xyz(n):
            return P[n] if n in P else anchor(n)
        for (a, b), t in links.items():
            pa, pb = xyz(a), xyz(b)
            ax.plot([pa[0], pb[0]], [pa[1], pb[1]], color="#1f5fa8",
                    lw=1.2 + 2.8 * t / tmax, zorder=4, solid_capstyle="round")
            mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
            ax.text(mx, my, f"{t:.2f}", fontsize=8, color="#123", ha="center", va="center",
                    zorder=7, bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))
        pa, pb = anchor("T3"), anchor("P1")
        ax.plot([pa[0], pb[0]], [pa[1], pb[1]], color="#1f5fa8", lw=2, ls="--", zorder=4)
        for n, p in P.items():
            ax.plot(p[0], p[1], "o", color="#b3261e", ms=7, zorder=8, mec="white")
            ax.text(p[0] + 4, p[1] + (6 if n == "A" else 5), f"{n}\n{ftin(p[2])} high",
                    fontsize=8, color="#b3261e", zorder=8, fontweight="bold")
        ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
    # A dimension to fence
    note = [
        f"A: {A['fence_offset_in']:.0f}″ off the fence, {ftin(A['pos'][1])} from the north line "
        f"(on the patio front), {ftin(A['z'])} high;",
        f"   T1:P3:P4 legs = {A['T'][('T1', 'A')]:.2f} : {A['T'][('A', 'P3')]:.2f} : "
        f"{A['T'][('A', 'P4')]:.2f};  A–P4 clears the trailer by {A['trailer_clear_in']:.0f}″ in plan.",
        f"3a  B at {B['pos'][0]:.0f}″ from P1, {B['pos'][1]:.0f}″ in from the P1–P2 line "
        f"(limit {dmax}″); P1–P2 segments {max(B['T'][('P1', 'B')], B['T'][('B', 'P2')]) / B['T'][('T2', 'B')]:.1f}× the T2 leg.",
        f"3b  B1 {B2['pos']['B1'][0]:.0f}″/{B2['pos']['B1'][1]:.0f}″, B2 {B2['pos']['B2'][0]:.0f}″/"
        f"{B2['pos']['B2'][1]:.0f}″ (from P1 / in from line);  max/min tension {B2['spread']:.1f} "
        f"vs {B['spread']:.1f} for 3a.",
        "Numbers on cables: prestress tension relative to the lightest cable in that group. "
        "Line weight ∝ tension. T3–P1 (dashed) is independent.",
        "Pulling the P1–P2 junction closer to the line (limit d):  " + ",  ".join(
            f"d≤{r['dmax_in']}″ → {r['P_over_T2']}×" for r in trade) + "  (P1–P2 tension ÷ T2 leg)",
    ]
    fig.text(0.02, 0.015, "\n".join(note), fontsize=9, va="bottom", family="monospace")
    fig.subplots_adjust(left=0.03, right=0.99, top=0.95, bottom=0.2, wspace=0.05)
    out = HERE / "awning-3-junctions.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)

    def jt(T):
        return {f"{a}-{b}": round(v, 3) for (a, b), v in T.items()}
    return {"A": {"pos": A["pos"], "z": round(A["z"], 1), "tensions": jt(A["T"]),
                  "spread": round(A["spread"], 2), "trailer_clear_in": round(A["trailer_clear_in"], 1)},
            "B_single": {"pos": B["pos"], "z": round(B["z"]["B"], 1), "tensions": jt(B["T"]),
                         "spread": round(B["spread"], 2)},
            "B_double": {"pos": B2["pos"], "z": {k: round(v, 1) for k, v in B2["z"].items()},
                         "tensions": jt(B2["T"]), "spread": round(B2["spread"], 2)},
            "dmax_in": dmax, "tradeoff": trade}


if __name__ == "__main__":
    res = {"membrane": fig_membrane(), "junctions": fig_junctions()}
    (HERE / "awning.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))
