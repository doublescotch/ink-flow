"""Body layout of Angel against vanilla, at the shoulders : UV gap in texels per height band and side, and a picture
of where Angel's shoulder triangles land in the Samurai UV body texture (2026-11-04, Fable, read only).

  python seam4.py <out dir>
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree
from seam import VAN, ANG, load
from uvdev import closest_bary

ROOT = r"C:\__DEV\cyberpunk\ink_flow"
Image.MAX_IMAGE_PIXELS = None
SIZE = 8192


def main(out):
    os.makedirs(out, exist_ok=True)
    Pv, Uv = load(VAN, "body"); Pa, Ua = load(ANG, "body")
    Pl, _ = load(VAN, "arm_l")
    print("vanilla arm_l mean x =", round(float(Pl[..., 0].mean()), 3), "(sign of the character's LEFT side)")
    pts = Pa.reshape(-1, 3); uvs = Ua.reshape(-1, 2)
    pts, k = np.unique(np.round(pts, 6), axis=0, return_index=True); uvs = uvs[k]
    sel = pts[:, 2] > 1.20
    pts, uvs = pts[sel], uvs[sel]
    print(f"{len(pts)} Angel body skin vertices above z 1.20")
    tree = cKDTree(Pv.mean(axis=1))
    _, J = tree.query(pts, k=12)
    du = np.zeros(len(pts)); dist = np.zeros(len(pts)); vuv = np.zeros((len(pts), 2))
    for i, (p, uv, js) in enumerate(zip(pts, uvs, J)):
        cand = [(r[0] @ Uv[j], r[1]) for j in js for r in [closest_bary(p, *Pv[j])] if r]
        dmin = min(c[1] for c in cand)
        best = min((c for c in cand if c[1] <= dmin + 3e-4), key=lambda c: np.linalg.norm(c[0] - uv))
        du[i] = np.linalg.norm((best[0] - uv) * SIZE); dist[i] = dmin; vuv[i] = best[0]
    print(f"distance to the vanilla body surface (mm) : median {np.median(dist) * 1e3:.2f}, p99 {np.percentile(dist, 99) * 1e3:.2f}")
    print(f"UV gap at {SIZE} texels, per height band and side (x sign) : median / p90 / % > 32 texels (= 4 mm on an 8K body)")
    for lo in np.arange(1.52, 1.18, -0.04):
        for side, m in (("x<0", pts[:, 0] < 0), ("x>0", pts[:, 0] > 0)):
            b = m & (pts[:, 2] >= lo) & (pts[:, 2] < lo + 0.04)
            if b.sum() > 20:
                print(f"   z {lo:.2f}-{lo + 0.04:.2f} {side} : n={b.sum():5d}  median {np.median(du[b]):7.1f}  p90 {np.percentile(du[b], 90):7.1f}  "
                      f">32 : {(du[b] > 32).mean() * 100:5.1f} %")
    # picture : Samurai UV body texture (u > 0.22), vanilla triangles above z 1.30 in green, Angel's in magenta
    tex = os.path.join(ROOT, r"dl\uv\conv\png\002_Tattoos_UV_Unknown_Samurai__fullbody_overlay_d01\fullbody_overlay_d01.png")
    im = Image.open(tex).convert("RGB").resize((2048, 2048), Image.BILINEAR)
    d = ImageDraw.Draw(im)
    cv = Pv.mean(axis=1)
    for t, cz in zip(Uv, cv[:, 2]):
        if cz > 1.30:
            d.polygon([(float(u) * 2048, float(v) * 2048) for u, v in t], outline=(0, 255, 0))
    ca = Pa.mean(axis=1)
    for t, cz in zip(Ua[::3], ca[::3, 2]):
        if cz > 1.30:
            d.polygon([(float(u) * 2048, float(v) * 2048) for u, v in t], outline=(255, 0, 255))
    im.save(os.path.join(out, "samurai_uv_body_shoulders.png"))
    # far vertices : where do they read in the texture ?
    far = du > 32
    if far.any():
        print(f"far Angel vertices ({far.sum()}) : their own UV u {uvs[far, 0].min():.3f}-{uvs[far, 0].max():.3f} v {uvs[far, 1].min():.3f}-{uvs[far, 1].max():.3f} ;"
              f" vanilla UV at the same place u {vuv[far, 0].min():.3f}-{vuv[far, 0].max():.3f} v {vuv[far, 1].min():.3f}-{vuv[far, 1].max():.3f}")
        tx = np.asarray(Image.open(tex).convert("RGBA"))
        a_own = tx[np.clip((uvs[far, 1] * 8192).astype(int), 0, 8191), np.clip((uvs[far, 0] * 8192).astype(int), 0, 8191), 3]
        a_van = tx[np.clip((vuv[far, 1] * 8192).astype(int), 0, 8191), np.clip((vuv[far, 0] * 8192).astype(int), 0, 8191), 3]
        print(f"   Samurai UV ink at Angel's own UV : {(a_own > 64).mean() * 100:.1f} % ; at the vanilla UV of the same 3D point : {(a_van > 64).mean() * 100:.1f} %")


if __name__ == "__main__":
    main(sys.argv[1])
