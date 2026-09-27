"""Lower one post: fabric slope, ponding area, headroom and Airstream clearance.

P3 is ruled out (electrical connection beside it); P4 is the candidate.

Run from the repository root:
    archive/.venv/bin/python studies/20260927.01-patio-awning/sweep_post.py [POST]
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import awning  # noqa: E402
import patio_site  # noqa: E402

POST = sys.argv[1] if len(sys.argv) > 1 else "P4"
FIG_H = 70  # draw this lowered case in full

rows = []
base = patio_site.POSTS[POST]
for h in (82, 78, 74, 70, 66):
    patio_site.POSTS[POST] = (*base[:4], h)
    Y, T, E, c, nb, res, slope = awning.membrane()
    P = Y[T]
    u, v = P[:, 1, :2] - P[:, 0, :2], P[:, 2, :2] - P[:, 0, :2]
    area = 0.5 * np.abs(u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0])   # plan area
    z = P[:, :, 2].mean(axis=1)
    # T1-P4 fabric edge where it passes the Airstream's front corner
    d = np.array([patio_site.trailer_sdf(x, y) for x, y, _ in Y[:nb]])
    near = d < 12
    A = awning.best_A()
    rows.append({"post": POST, "height_in": h,
                 "slope_min_deg": round(float(slope.min()), 1),
                 "under_3deg_pct": round(float(area[slope < 3].sum() / area.sum() * 100), 1),
                 "under_6ft6_pct": round(float(area[z < 78].sum() / area.sum() * 100), 1),
                 "edge_z_within_1ft_of_trailer_in": round(float(Y[:nb][near, 2].min()), 1),
                 "A_height_in": round(float(A["z"]), 1)})
    print(rows[-1])
patio_site.POSTS[POST] = (*base[:4], FIG_H)
awning.fig_membrane(f"-{POST.lower()}-{FIG_H}")
patio_site.POSTS[POST] = base
(HERE / f"sweep_{POST.lower()}.json").write_text(json.dumps(rows, indent=1))
