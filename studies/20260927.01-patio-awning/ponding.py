"""Where does water go, and where will it pool, on the fabric awning?

For the form-found fabric of awning.py (post heights from patio_site.py, ties 8'-5"):

1. Drainage on the unloaded shape: every mesh node sends its tributary
   plan area to its lowest neighbour (steepest descent on the mesh graph).
   Summing along the paths gives flow accumulation; the boundary nodes where
   it leaves the fabric are the drip points.

2. Ponding under rain: a thin rain film is applied as vertical load and the
   fabric re-solved with the same force densities (linear force density,
   fine for small deflection about the prestressed shape). Any dip is then
   filled to its spill level (priority flood from the fabric edge), the
   ponded water added to the load, and the solve repeated until the water
   depth settles or runs away.

Force density in the fabric is set from an assumed prestress: on this mesh
q (lb/in per link) is roughly the fabric tension in lb/in. Results are for
20 lb/ft (a firm tarp) and 8 lb/ft (a slack one).

Two cases: all posts level, and P2 dropped 8 in to give a drain corner.

Run from the repository root:
    archive/.venv/bin/python studies/20260927.01-patio-awning/ponding.py
"""
import heapq
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.sparse import coo_matrix  # noqa: E402
from scipy.sparse.linalg import spsolve  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import awning  # noqa: E402
import patio_site  # noqa: E402
from awning import anchor, draw_site, ftin  # noqa: E402

WATER_PSI_PER_IN = 0.0361      # 1 in of water
RAIN_FILM_IN = 0.1             # water film clinging to the whole sheet
PRESTRESS = {"firm 20 lb/ft": 20 / 12, "slack 8 lb/ft": 8 / 12}   # lb/in
RUNAWAY_IN = 12.0


def tributary(Y, T):
    u, v = Y[T[:, 1], :2] - Y[T[:, 0], :2], Y[T[:, 2], :2] - Y[T[:, 0], :2]
    a = 0.5 * np.abs(u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0])
    w = np.zeros(len(Y))
    for k in range(3):
        np.add.at(w, T[:, k], a / 3)
    return w


def neighbours(n, E):
    nb = [[] for _ in range(n)]
    for i, j in E:
        nb[i].append(j)
        nb[j].append(i)
    return nb


def drainage(Y, E, trib, nbound):
    """Steepest-descent flow accumulation; returns (accum, receiver)."""
    nbr = neighbours(len(Y), E)
    rec = np.full(len(Y), -1)
    for i in range(nbound, len(Y)):                # interior nodes only
        j = min(nbr[i], key=lambda k: Y[k, 2])
        if Y[j, 2] < Y[i, 2]:
            rec[i] = j
    acc = trib.copy()
    for i in np.argsort(-Y[:, 2]):
        if rec[i] >= 0:
            acc[rec[i]] += acc[i]
    return acc, rec


def fill_level(Y, E, nbound):
    """Priority flood from the fabric edge: water surface level at every node."""
    nbr = neighbours(len(Y), E)
    W = Y[:, 2].copy()
    done = np.zeros(len(Y), bool)
    pq = [(Y[i, 2], i) for i in range(nbound)]
    heapq.heapify(pq)
    done[:nbound] = True
    while pq:
        lvl, i = heapq.heappop(pq)
        for j in nbr[i]:
            if not done[j]:
                done[j] = True
                W[j] = max(Y[j, 2], lvl)
                heapq.heappush(pq, (W[j], j))
    return W


def loaded(Y0, E, fixed, q, load):
    """Re-solve heights with vertical nodal load (lb, down +) at fixed q."""
    n, m = len(Y0), len(E)
    C = coo_matrix((np.r_[np.ones(m), -np.ones(m)],
                    (np.r_[np.arange(m), np.arange(m)], np.r_[E[:, 0], E[:, 1]])),
                   shape=(m, n)).tocsr()
    D = (C.T @ coo_matrix((q, (np.arange(m), np.arange(m)))) @ C).tocsr()
    free = ~fixed
    z = Y0[:, 2].copy()
    z[free] = spsolve(D[free][:, free].tocsc(), -D[free][:, fixed] @ Y0[fixed, 2] - load[free])
    Y = Y0.copy()
    Y[:, 2] = z
    return Y


def pond(Y0, T, E, fixed, q, prestress):
    trib = tributary(Y0, T)
    qs = q * prestress                           # q=1 fabric link ~ 1 lb/in
    depth = np.zeros(len(Y0))
    hist, snap = [], None
    for it in range(60):
        load = WATER_PSI_PER_IN * (RAIN_FILM_IN + depth) * trib
        Y = loaded(Y0, E, fixed, qs, load)
        W = fill_level(Y, E, nbound=NB)
        new = W - Y[:, 2]
        hist.append(float(new.max()))
        if snap is None and new.max() > 1.0:
            snap = (Y, new)                      # pond footprint once it is 1 in deep
        if new.max() > RUNAWAY_IN:
            return snap[0], snap[1], hist, "runaway"
        if np.abs(new - depth).max() < 0.01:
            depth = new
            break
        depth = new
    return Y, depth, hist, "stable"


def case(label, heights):
    base = dict(patio_site.POSTS)
    for p, h in heights.items():
        patio_site.POSTS[p] = (*base[p][:4], h)
    Y0, T, E, is_cable, nb, res, slope, fixed, q = awning.membrane(full=True)
    global NB
    NB = nb
    trib = tributary(Y0, T)
    acc, rec = drainage(Y0, E, trib, nb)
    out = {"label": label, "heights": heights, "base": base, "Y0": Y0, "T": T, "nb": nb, "slope": slope, "acc": acc,
           "rec": rec, "ponds": {}}
    # where the water leaves: boundary nodes that receive flow
    total = trib.sum()
    drip = {i: acc[i] / total for i in range(nb) if acc[i] > 0.02 * total}
    out["drip"] = drip
    out["drip_all"] = {i: acc[i] / total for i in range(nb) if acc[i] > 0}
    for name, ps in PRESTRESS.items():
        Y, depth, hist, state = pond(Y0, T, E, fixed, q, ps)
        k = int(np.argmin(Y[nb:, 2])) + nb if nb < len(Y) else 0
        vol = float((depth * trib).sum())          # in^3
        out["ponds"][name] = {"Y": Y, "depth": depth, "state": state, "hist": hist,
                              "max_depth_in": float(depth.max()),
                              "at": Y[int(np.argmax(depth)), :2].tolist(),
                              "gallons": vol / 231.0, "iterations": len(hist),
                              "lowest_interior": Y[k].tolist()}
    for p in heights:
        patio_site.POSTS[p] = base[p]
    return out


NB = 0
EDGES = [("P1", "P2"), ("P2", "P3"), ("P3", "P4"), ("P4", "T1"), ("T2", "P1")]


def edge_shares(c):
    """Share of the roof shed off each fabric edge (nearest chord)."""
    out = {}
    for i, f in c["drip_all"].items():
        x, y = c["Y0"][i, :2]
        best = None
        for a, b in EDGES:
            pa, pb = np.array(anchor(a)[:2]), np.array(anchor(b)[:2])
            t = np.clip(np.dot((x, y) - pa, pb - pa) / np.dot(pb - pa, pb - pa), 0, 1)
            dist = np.linalg.norm(pa + t * (pb - pa) - (x, y))
            if best is None or dist < best[0]:
                best = (dist, f"{a}–{b}")
        out[best[1]] = out.get(best[1], 0) + f
    return out


def draw(ax, c, show):
    for p, h in c["heights"].items():
        patio_site.POSTS[p] = (*c["base"][p][:4], h)
    draw_site(ax)
    for p in c["heights"]:
        patio_site.POSTS[p] = c["base"][p]
    Y0, T, nb = c["Y0"], c["T"], c["nb"]
    ax.tricontourf(Y0[:, 0], Y0[:, 1], T, Y0[:, 2], levels=np.arange(66, 104, 2),
                   cmap="Blues", alpha=0.35, zorder=3)
    cs = ax.tricontour(Y0[:, 0], Y0[:, 1], T, Y0[:, 2], levels=np.arange(74, 102, 2),
                       colors="#1f5fa8", linewidths=0.5, zorder=3)
    ax.clabel(cs, fmt=lambda v: ftin(v), fontsize=6)
    ring = list(range(nb)) + [0]
    ax.plot(Y0[ring, 0], Y0[ring, 1], color="#b3261e", lw=2, zorder=4)
    # flat fabric (<3 deg)
    flat = c["slope"] < 3
    ax.tripcolor(Y0[:, 0], Y0[:, 1], T[flat], facecolors=np.ones(flat.sum()),
                 cmap="Oranges", vmin=0, vmax=2.5, alpha=0.55, zorder=4, edgecolors="none")
    # flow lines: draw receiver links weighted by accumulation
    acc, rec = c["acc"], c["rec"]
    amax = acc.max()
    for i in np.where(rec >= 0)[0]:
        if acc[i] > 0.004 * acc.sum() / 3:
            j = rec[i]
            ax.plot([Y0[i, 0], Y0[j, 0]], [Y0[i, 1], Y0[j, 1]], color="#0b3d91",
                    lw=0.4 + 3.5 * np.sqrt(acc[i] / amax), alpha=0.8, zorder=5)
    for i, f in c["drip"].items():
        ax.plot(Y0[i, 0], Y0[i, 1], "v", color="#0b3d91", ms=4 + 14 * f, zorder=7, mec="white")
    # pond under rain
    p = c["ponds"][show]
    d = p["depth"]
    wet = d > 0.05
    if wet.any():
        Y = p["Y"]
        tw = T[wet[T].all(axis=1)]
        if len(tw):
            ax.tripcolor(Y[:, 0], Y[:, 1], tw, facecolors=d[tw].mean(axis=1),
                         cmap="PuBu", vmin=0, vmax=max(1.0, d.max()), zorder=6, alpha=0.9)
        k = int(np.argmax(d))
        ax.plot(Y[k, 0], Y[k, 1], "X", color="#6a0dad", ms=13, mec="white", zorder=9)
        msg = ("LOW POINT — pond starts here\nslack fabric: keeps deepening"
               if p["state"] == "runaway" else f"low point: pond {d.max():.1f}″ deep")
        ax.annotate(msg, xy=(Y[k, 0], Y[k, 1]), xytext=(Y[k, 0] - 120, Y[k, 1] + 45), fontsize=10,
                    color="#6a0dad", fontweight="bold", zorder=9,
                    arrowprops=dict(arrowstyle="->", color="#6a0dad"))
    else:
        lo = p["lowest_interior"]
        ax.plot(lo[0], lo[1], "o", mfc="none", mec="#6a0dad", ms=16, mew=2, zorder=9)
        ax.annotate("lowest fabric under rain:\nat the P2 corner, drains off",
                    xy=lo[:2], xytext=(lo[0] - 120, lo[1] + 45), fontsize=10,
                    color="#6a0dad", fontweight="bold", zorder=9,
                    arrowprops=dict(arrowstyle="->", color="#6a0dad"))


def main():
    h = patio_site.POSTS["P1"][4]
    drop = h - 8                                  # P2 as the drain corner
    cases = [case(f"All four posts {ftin(h)}", {}),
             case(f"P2 dropped to {ftin(drop)}", {"P2": drop})]
    fig, axs = plt.subplots(1, 2, figsize=(15.5, 9.2))
    summary = []
    for ax, c in zip(axs, cases):
        draw(ax, c, "slack 8 lb/ft")
        f, s = c["ponds"]["firm 20 lb/ft"], c["ponds"]["slack 8 lb/ft"]
        ax.set_title(c["label"], loc="left", fontsize=13, fontweight="bold")
        txt = (f"under 3°: {np.mean(c['slope'] < 3) * 100:.0f}% of fabric (orange)\n"
               f"rain, firm 20 lb/ft: {f['state']}, max {f['max_depth_in']:.1f}″, "
               f"{f['gallons']:.1f} gal\n"
               f"rain, slack 8 lb/ft: {s['state']}, max {s['max_depth_in']:.1f}″, "
               f"{s['gallons']:.1f} gal\n"
               "shed off each edge: " + ", ".join(
                   f"{k} {v * 100:.0f}%" for k, v in sorted(edge_shares(c).items(),
                                                          key=lambda kv: -kv[1])))
        ax.text(0.02, 0.02, txt, transform=ax.transAxes, fontsize=9, family="monospace",
                va="bottom", bbox=dict(fc="white", ec="#ccc"), zorder=10)
        summary.append({"case": c["label"], "under_3deg_pct": round(float(np.mean(c["slope"] < 3) * 100), 1),
                        "edge_share": {k: round(v, 3) for k, v in edge_shares(c).items()},
                        **{k: {kk: (round(vv, 2) if isinstance(vv, float) else vv)
                               for kk, vv in v.items() if kk in ("state", "max_depth_in", "at", "gallons", "iterations")}
                           for k, v in c["ponds"].items()}})
    fig.suptitle("Where the water goes: drainage paths (blue), drip points (▼ share of roof), "
                 "flat fabric < 3° (orange), pond under rain on slack 8 lb/ft fabric (purple ✕)",
                 fontsize=11, x=0.02, ha="left")
    fig.subplots_adjust(left=0.03, right=0.99, top=0.92, bottom=0.04, wspace=0.06)
    fig.savefig(HERE / "awning-4-ponding.png", dpi=120)
    (HERE / "ponding.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
