"""Where is the body / arm seam on a VTK body (Angel) compared with vanilla, and where does a UV tattoo put the
shoulder ink ? (2026-11-04, Fable, read only.)

For each vanilla arm skin triangle : which Angel surface is closest, the Angel arm or the Angel body ?  If the
shoulder cap of the vanilla arm is owned by the Angel BODY, a UV tattoo (shoulder painted in the arm strip) loses
that ink on Angel : the converted arm texture carries it but Angel's arm has no triangle there, and Angel's body
reads the body texture where the UV painter never painted.

  python seam.py
"""
import glob, os, sys
import numpy as np
from scipy.spatial import cKDTree
from uvconv import read

ROOT = r"C:\__DEV\cyberpunk\ink_flow"
VAN = os.path.join(ROOT, r"gen\vanilla_test\mesh")
ANG = os.path.join(ROOT, r"gen\uv104\work_angel\mesh")
FW = os.path.join(ROOT, r"dl\uv\x\011_UV_Framework_Texture_3.2.1\base\characters\common\player_base_bodies\player_female_average\arms_hq")
PWA = r"base\characters\common\player_base_bodies\player_female_average"
FILES = {"arm_l": PWA + r"\arms_hq\a0_000_pwa_base_hq__l.mesh.json",
         "arm_r": PWA + r"\arms_hq\a0_000_pwa_base_hq__r.mesh.json",
         "body": PWA + r"\t0_000_pwa_base__full.mesh.json"}


def samples(P, n=5):
    """Points spread on every triangle (barycentric grid) : a cheap surface for distance queries."""
    pts = []
    for i in range(n + 1):
        for j in range(n + 1 - i):
            a, b = i / n, j / n
            pts.append(P[:, 0] * (1 - a - b) + P[:, 1] * a + P[:, 2] * b)
    return np.concatenate(pts)


def area(P):
    return 0.5 * np.linalg.norm(np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]), axis=1)


def load(base, key):
    P, U = read(os.path.join(base, key, FILES[key]))
    return P, U


def main():
    van = {k: load(VAN, k) for k in FILES}
    ang = {k: load(ANG, k) for k in FILES}
    for k in FILES:
        for name, d in (("vanilla", van), ("Angel", ang)):
            P = d[k][0]
            print(f"{name:8s} {k:6s} : {len(P):6d} skin triangles, z {P[..., 2].min():.3f} - {P[..., 2].max():.3f}, "
                  f"area {area(P).sum() * 1e4:.0f} cm2")
    print()
    trees = {("Angel", k): cKDTree(samples(ang[k][0])) for k in FILES}
    trees.update({("vanilla", k): cKDTree(samples(van[k][0])) for k in FILES})

    def owner(P, who, side):
        """For triangles P : distance to `who`'s arm (side) and body ; owner = the closer one."""
        c = P.mean(axis=1)
        da, _ = trees[(who, side)].query(c)
        db, _ = trees[(who, "body")].query(c)
        return da, db

    for side in ("arm_l", "arm_r"):
        P = van[side][0]; A = area(P)
        da, db = owner(P, "Angel", side)
        body_owned = db < da - 0.002            # Angel body is clearly closer than Angel arm (2 mm margin)
        far = np.minimum(da, db) > 0.01
        print(f"vanilla {side} on Angel : {body_owned.sum()} triangles ({A[body_owned].sum() / A.sum() * 100:.1f} % of the "
              f"skin area) are closer to the ANGEL BODY than to the Angel arm ; {far.sum()} more than 1 cm from any Angel surface")
        if body_owned.any():
            z = P[body_owned].mean(axis=1)[:, 2]
            print(f"   those triangles : z {z.min():.3f} - {z.max():.3f} ; Angel arm distance median "
                  f"{np.median(da[body_owned]) * 1e3:.1f} mm, body distance median {np.median(db[body_owned]) * 1e3:.1f} mm")
            # height histogram, 2 cm bins, top of the arm
            zs = P.mean(axis=1)[:, 2]
            for lo in np.arange(np.floor(zs.max() * 50) / 50, zs.max() - 0.16, -0.02):
                m = (zs >= lo) & (zs < lo + 0.02)
                if m.any():
                    print(f"   z {lo:.2f}-{lo + 0.02:.2f} : {A[m & body_owned].sum() / A[m].sum() * 100:5.1f} % of the area owned by the Angel body")
        # the other way : Angel arm triangles closer to the vanilla body than to the vanilla arm
        Pa = ang[side][0]; Aa = area(Pa)
        da2, db2 = owner(Pa, "vanilla", side)
        bo2 = db2 < da2 - 0.002
        print(f"Angel {side} on vanilla : {bo2.sum()} triangles ({Aa[bo2].sum() / Aa.sum() * 100:.1f} % of the area) closer to the "
              f"VANILLA BODY than to the vanilla arm" + (f" ; z {Pa[bo2].mean(axis=1)[:, 2].min():.3f} - {Pa[bo2].mean(axis=1)[:, 2].max():.3f}" if bo2.any() else ""))
        print()

    # Where does the Samurai UV texture put ink, on the framework arm (strip) by height ?
    pngs = glob.glob(os.path.join(ROOT, r"dl\uv\conv\png\002_Tattoos_UV_Unknown_Samurai__fullbody_overlay_d01", "**", "*.png"), recursive=True)
    if not pngs:
        print("no Samurai UV png"); return
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = np.asarray(Image.open(pngs[0]).convert("RGBA"))
    H, W = im.shape[:2]
    print(f"Samurai UV texture {pngs[0]} : {W} x {H}")
    for side, f in (("arm_l", "a0_000_pwa_base_hq__l.mesh.json"), ("arm_r", "a0_000_pwa_base_hq__r.mesh.json")):
        Pf, Uf = read(os.path.join(FW, f))
        c = Pf.mean(axis=1); uv = Uf.mean(axis=1)
        x = np.clip((uv[:, 0] * W).astype(int), 0, W - 1); y = np.clip((uv[:, 1] * H).astype(int), 0, H - 1)
        alpha = im[y, x, 3]
        print(f"framework {side} : z {c[:, 2].min():.3f} - {c[:, 2].max():.3f} ; ink (alpha > 64) by height band :")
        for lo in np.arange(np.floor(c[:, 2].max() * 50) / 50, c[:, 2].max() - 0.20, -0.02):
            m = (c[:, 2] >= lo) & (c[:, 2] < lo + 0.02)
            if m.any():
                print(f"   z {lo:.2f}-{lo + 0.02:.2f} : {(alpha[m] > 64).mean() * 100:5.1f} % of the triangles inked (n={m.sum()})")
    # and on the vanilla body, near the shoulder (u > 0.22) : does the UV painter put ink there ?
    Pb, Ub = van["body"]
    c = Pb.mean(axis=1); uv = Ub.mean(axis=1)
    x = np.clip((uv[:, 0] * W).astype(int), 0, W - 1); y = np.clip((uv[:, 1] * H).astype(int), 0, H - 1)
    alpha = im[y, x, 3]
    top = c[:, 2] > 1.35
    print(f"vanilla body triangles above z 1.35 (shoulders, neck) : {top.sum()}, inked {(alpha[top] > 64).mean() * 100:.1f} %")


if __name__ == "__main__":
    main()
