"""How far a VTK arm (Angel) is from the vanilla arm layout, in texels : each skin vertex of the VTK arm is projected
on the closest vanilla skin triangle, the vanilla UV there is compared with the VTK vertex's own UV (2026-11-04, Opus).

  python uvdev.py <vanilla arm mesh.json> <VTK arm mesh.json> [--size 4096]
"""
import sys
import numpy as np
from scipy.spatial import cKDTree
from uvconv import read


def closest_bary(p, a, b, c):
    """Barycentric coordinates of the point of triangle abc closest to p (clamped to the triangle)."""
    ab, ac = b - a, c - a
    n = np.cross(ab, ac)
    nn = (n * n).sum()
    if nn < 1e-20:
        return None
    q = p - ((p - a) @ n) / nn * n
    v2 = q - a
    d00, d01, d11 = ab @ ab, ab @ ac, ac @ ac
    d20, d21 = v2 @ ab, v2 @ ac
    den = d00 * d11 - d01 * d01
    l2 = (d11 * d20 - d01 * d21) / den
    l3 = (d00 * d21 - d01 * d20) / den
    w = np.clip(np.array([1 - l2 - l3, l2, l3]), 0, None)
    return w / w.sum(), np.linalg.norm(p - (w / w.sum()) @ np.array([a, b, c]))


def main(argv):
    size = 4096
    if "--size" in argv:
        i = argv.index("--size"); size = int(argv[i + 1]); del argv[i:i + 2]
    Pv, Uv = read(argv[0]); Pa, Ua = read(argv[1])
    pts = Pa.reshape(-1, 3); uvs = Ua.reshape(-1, 2)
    pts, k = np.unique(np.round(pts, 6), axis=0, return_index=True)
    uvs = uvs[k]
    tree = cKDTree(Pv.mean(axis=1))
    _, J = tree.query(pts, k=12)
    du, dist = [], []
    for p, uv, js in zip(pts, uvs, J):
        # On a UV seam the same 3D point has two UVs : among the triangles touching the closest point (within
        # 0.3 mm of it), the one on the vertex's side of the seam is kept.
        cand = [(r[0] @ Uv[j], r[1]) for j in js for r in [closest_bary(p, *Pv[j])] if r]
        dmin = min(c[1] for c in cand)
        best = min((c for c in cand if c[1] <= dmin + 3e-4), key=lambda c: np.linalg.norm(c[0] - uv))
        du.append(np.linalg.norm((best[0] - uv) * size)); dist.append(dmin)
    du, dist = np.array(du), np.array(dist)
    print(f"{len(pts)} VTK skin vertices ; distance to the vanilla surface (mm) median {np.median(dist) * 1e3:.2f}, "
          f"p99 {np.percentile(dist, 99) * 1e3:.2f}, max {dist.max() * 1e3:.2f}")
    print(f"UV gap in texels at {size} : median {np.median(du):.2f}, p90 {np.percentile(du, 90):.2f}, "
          f"p99 {np.percentile(du, 99):.2f}, max {du.max():.1f} ; > 8 texels : {(du > 8).mean() * 100:.2f} %")
    far = du > 8
    if far.any():
        print("far vertices : z (height) range", np.round(pts[far][:, 2].min(), 3), "-", np.round(pts[far][:, 2].max(), 3),
              "; their distance to the vanilla surface (mm) median", round(float(np.median(dist[far])) * 1e3, 2))


if __name__ == "__main__":
    main(sys.argv[1:])
