"""Software render of the shoulders, three ways, to tell a painting difference from a pipeline defect
(2026-11-04, Fable, read only) :
  A. Samurai VTK on Angel        (body v_overlay + VTK arm textures, Angel meshes)        = his capture 1
  B. Samurai UV on Angel         (UV body texture + converted arm textures, Angel meshes) = his capture 2
  C. Samurai UV on the framework (UV body texture on the vanilla body + strip on the framework arms) = painter's intent
Points are sampled on the skin triangles, textured, projected on the front and back views with a depth buffer.

  python seam5.py <out dir>
"""
import glob, os, sys
import numpy as np
from PIL import Image
from seam import VAN, ANG, load, area
from uvconv import read

ROOT = r"C:\__DEV\cyberpunk\ink_flow"
FW = os.path.join(ROOT, r"dl\uv\x\011_UV_Framework_Texture_3.2.1\base\characters\common\player_base_bodies\player_female_average\arms_hq")
Image.MAX_IMAGE_PIXELS = None
SKIN = np.array([205, 165, 135], dtype=np.float64)
PIX = 0.0015                       # m per pixel
X0, X1, Z0, Z1 = -0.42, 0.42, 1.22, 1.58


def tex(path):
    return np.asarray(Image.open(path).convert("RGBA"))


def sample(P, U, n):
    pts, uvs = [], []
    for i in range(n + 1):
        for j in range(n + 1 - i):
            a, b = i / n, j / n
            w = np.array([1 - a - b, a, b])
            pts.append(np.einsum("k,nkd->nd", w, P)); uvs.append(np.einsum("k,nkd->nd", w, U))
    return np.concatenate(pts), np.concatenate(uvs)


def colour(uv, im):
    H, W = im.shape[:2]
    x = np.clip((uv[:, 0] * W).astype(int), 0, W - 1); y = np.clip((uv[:, 1] * H).astype(int), 0, H - 1)
    px = im[y, x].astype(np.float64)
    a = px[:, 3:4] / 255.0
    return SKIN * (1 - a) + px[:, :3] * a


def render(layers, front_sign, out_path):
    """layers = [(points, colours)] ; view along y : pixels keep the point with the largest y * front_sign."""
    W = int((X1 - X0) / PIX); H = int((Z1 - Z0) / PIX)
    img = np.full((H, W, 3), 30, dtype=np.uint8)
    pts = np.concatenate([l[0] for l in layers]); col = np.concatenate([l[1] for l in layers])
    px = ((pts[:, 0] - X0) / PIX).astype(int); py = ((Z1 - pts[:, 2]) / PIX).astype(int)
    ok = (px >= 0) & (px < W) & (py >= 0) & (py < H)
    px, py, depth, col = px[ok], py[ok], pts[ok, 1] * front_sign, col[ok]
    order = np.lexsort((-depth, py * W + px))            # per pixel, front-most first
    key = (py * W + px)[order]
    first = np.ones(len(key), dtype=bool); first[1:] = key[1:] != key[:-1]
    sel = order[first]
    img[py[sel], px[sel]] = np.clip(col[sel], 0, 255).astype(np.uint8)
    im = Image.fromarray(img[:, ::-1] if front_sign > 0 else img)   # mirror so the character's left is on the viewer's right in the front view
    im = im.resize((W * 3, H * 3), Image.NEAREST)
    im.save(out_path)


def main(out):
    os.makedirs(out, exist_ok=True)
    ang = {k: load(ANG, k) for k in ("body", "arm_l", "arm_r")}
    van = {k: load(VAN, k) for k in ("body", "arm_l", "arm_r")}
    fw = {"arm_l": read(os.path.join(FW, "a0_000_pwa_base_hq__l.mesh.json")),
          "arm_r": read(os.path.join(FW, "a0_000_pwa_base_hq__r.mesh.json"))}
    # which way is the front : the breasts (z 1.15-1.30, |x| < 0.15) bulge towards it
    Pb = van["body"][0].reshape(-1, 3)
    m = (Pb[:, 2] > 1.15) & (Pb[:, 2] < 1.30) & (np.abs(Pb[:, 0]) < 0.15)
    front = 1.0 if abs(Pb[m, 1].max()) > abs(Pb[m, 1].min()) else -1.0
    print("front = +y" if front > 0 else "front = -y")

    T = {"vtk_body": tex(os.path.join(ROOT, r"dl\uv\png\samurai_body\v_overlay.png")),
         "vtk_arm_l": tex(glob.glob(os.path.join(ROOT, r"dl\uv\conv\png\002_Tattoos_VTK_Unknown_Samurai__femme_arm_left_01_overlay\**\*.png"), recursive=True)[0]),
         "vtk_arm_r": tex(glob.glob(os.path.join(ROOT, r"dl\uv\conv\png\002_Tattoos_VTK_Unknown_Samurai__femme_arm_right_01_overlay\**\*.png"), recursive=True)[0]),
         "uv_body": tex(os.path.join(ROOT, r"dl\uv\conv\png\002_Tattoos_UV_Unknown_Samurai__fullbody_overlay_d01\fullbody_overlay_d01.png")),
         "conv_arm_l": tex(os.path.join(ROOT, r"dl\uv\conv\out\samurai_arm_l.png")),
         "conv_arm_r": tex(os.path.join(ROOT, r"dl\uv\conv\out\samurai_arm_r.png"))}
    for k, v in T.items():
        print(k, v.shape[1])
    # the body part of the UV texture, as the body shell reads it on Angel : strip blanked
    uv_body_noarms = T["uv_body"].copy(); uv_body_noarms[:, :int(0.22 * uv_body_noarms.shape[1])] = 0

    S = {}
    for k, n in (("body", 4), ("arm_l", 6), ("arm_r", 6)):
        S[("ang", k)] = sample(*ang[k], n)
    for k, n in (("body", 14), ("arm_l", 10), ("arm_r", 10)):
        S[("van", k)] = sample(*van[k], n)
    for k in ("arm_l", "arm_r"):
        S[("fw", k)] = sample(*fw[k], 10)

    scenes = {
        "A_vtk_on_angel": [(S[("ang", "body")][0], colour(S[("ang", "body")][1], T["vtk_body"])),
                           (S[("ang", "arm_l")][0], colour(S[("ang", "arm_l")][1], T["vtk_arm_l"])),
                           (S[("ang", "arm_r")][0], colour(S[("ang", "arm_r")][1], T["vtk_arm_r"]))],
        "B_uv_on_angel": [(S[("ang", "body")][0], colour(S[("ang", "body")][1], uv_body_noarms)),
                          (S[("ang", "arm_l")][0], colour(S[("ang", "arm_l")][1], T["conv_arm_l"])),
                          (S[("ang", "arm_r")][0], colour(S[("ang", "arm_r")][1], T["conv_arm_r"]))],
        "C_uv_on_framework": [(S[("van", "body")][0], colour(S[("van", "body")][1], T["uv_body"])),
                              (S[("fw", "arm_l")][0], colour(S[("fw", "arm_l")][1], T["uv_body"])),
                              (S[("fw", "arm_r")][0], colour(S[("fw", "arm_r")][1], T["uv_body"]))],
    }
    for name, layers in scenes.items():
        render(layers, front, os.path.join(out, f"{name}_front.png"))
        render(layers, -front, os.path.join(out, f"{name}_back.png"))
        print("rendered", name)


if __name__ == "__main__":
    main(sys.argv[1])
