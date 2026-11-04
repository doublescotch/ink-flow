"""Shoulder cap of the UV Framework arm : where do its UVs point, and which UV tattoos ink it ?  Draws the layout
over the Samurai UV texture and over the converted arm texture (2026-11-04, Fable, read only).

  python seam2.py <out dir>
"""
import glob, os, sys
import numpy as np
from PIL import Image, ImageDraw
from uvconv import read

ROOT = r"C:\__DEV\cyberpunk\ink_flow"
FW = os.path.join(ROOT, r"dl\uv\x\011_UV_Framework_Texture_3.2.1\base\characters\common\player_base_bodies\player_female_average\arms_hq")
VAN_L = os.path.join(ROOT, r"gen\vanilla_test\mesh\arm_l\base\characters\common\player_base_bodies\player_female_average\arms_hq\a0_000_pwa_base_hq__l.mesh.json")
Image.MAX_IMAGE_PIXELS = None
TEX = {"samurai": r"dl\uv\conv\png\002_Tattoos_UV_Unknown_Samurai__fullbody_overlay_d01\fullbody_overlay_d01.png",
       "bedellia": r"dl\uv\png\bedellia\fullbody_overlay_d01.png",
       "garden": r"dl\uv\png\garden_body\fullbody_overlay_d01.png",
       "kala_sleeve1": r"dl\uv\png\kala_sleeve1\fullbody_overlay_d01.png",
       "kala_v2": r"dl\uv\png\kala_v2\kala_v2_fullbody_overlay_d01.png",
       "fw_skin": r"dl\uv\png\fw_skin\d02_naked.png"}


def bands(c, step=0.02, depth=0.20):
    top = np.floor(c[:, 2].max() * 50) / 50
    for lo in np.arange(top, c[:, 2].max() - depth, -step):
        m = (c[:, 2] >= lo) & (c[:, 2] < lo + step)
        if m.any():
            yield lo, m


def main(out):
    os.makedirs(out, exist_ok=True)
    Pf, Uf = read(os.path.join(FW, "a0_000_pwa_base_hq__l.mesh.json"))
    c = Pf.mean(axis=1); uv = Uf.mean(axis=1)
    print("framework arm_l : UV range per height band")
    for lo, m in bands(c):
        print(f"   z {lo:.2f}-{lo + 0.02:.2f} : u {uv[m, 0].min():.3f}-{uv[m, 0].max():.3f}  v {uv[m, 1].min():.3f}-{uv[m, 1].max():.3f}  (n={m.sum()})")
    print()
    tex = {}
    for name, rel in TEX.items():
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print("missing", p); continue
        im = Image.open(p).convert("RGBA")
        tex[name] = np.asarray(im)
    print("ink (alpha > 64) on the framework LEFT arm per height band, per UV texture (fw_skin = luminance > 32) :")
    names = list(tex)
    print("   band       " + "".join(f"{n:>13s}" for n in names))
    for lo, m in bands(c, depth=0.30):
        row = []
        for n in names:
            im = tex[n]; H, W = im.shape[:2]
            x = np.clip((uv[m, 0] * W).astype(int), 0, W - 1); y = np.clip((uv[m, 1] * H).astype(int), 0, H - 1)
            px = im[y, x]
            val = (px[:, :3].max(axis=1) > 32) if n == "fw_skin" else (px[:, 3] > 64)
            row.append(f"{val.mean() * 100:12.1f}%")
        print(f"   z {lo:.2f}-{lo + 0.02:.2f}" + "".join(row))

    # picture 1 : Samurai UV texture (strip part, left arm = v < 0.5) with the framework arm layout, shoulder cap in cyan
    im = Image.fromarray(tex["samurai"]).resize((2048, 2048), Image.BILINEAR)
    crop = im.crop((0, 0, int(0.25 * 2048), 1024)).convert("RGB")       # u < 0.25, v < 0.5
    sx, sy = crop.size[0] / 0.25, crop.size[1] / 0.5
    big = crop.resize((crop.size[0] * 2, crop.size[1] * 2), Image.NEAREST)
    d = ImageDraw.Draw(big)
    for t, cz in zip(Uf, c[:, 2]):
        col = (0, 255, 255) if cz > 1.42 else ((255, 255, 0) if cz > 1.32 else (0, 110, 0))
        pts = [(float(u) * sx * 2, float(v) * sy * 2) for u, v in t]
        d.polygon(pts, outline=col)
    big.save(os.path.join(out, "samurai_uv_strip_left_layout.png"))
    # picture 2 : converted left arm texture (vanilla layout) with vanilla arm triangles, shoulder cap in cyan
    conv = os.path.join(ROOT, r"dl\uv\conv\out\samurai_arm_l.png")
    if os.path.exists(conv):
        Pv, Uv = read(VAN_L); cv = Pv.mean(axis=1)
        im2 = Image.open(conv).convert("RGB").resize((1024, 1024), Image.BILINEAR)
        d = ImageDraw.Draw(im2)
        for t, cz in zip(Uv, cv[:, 2]):
            col = (0, 255, 255) if cz > 1.42 else ((255, 255, 0) if cz > 1.32 else (0, 110, 0))
            d.polygon([(float(u) * 1024, float(v) * 1024) for u, v in t], outline=col)
        im2.save(os.path.join(out, "samurai_conv_left_layout.png"))
    # picture 3 : the VTK Samurai left arm texture with the same vanilla layout
    vtk = glob.glob(os.path.join(ROOT, r"dl\uv\conv\png\002_Tattoos_VTK_Unknown_Samurai__femme_arm_left_01_overlay", "**", "*.png"), recursive=True)
    if vtk:
        Pv, Uv = read(VAN_L); cv = Pv.mean(axis=1)
        im3 = Image.open(vtk[0]).convert("RGB").resize((1024, 1024), Image.BILINEAR)
        d = ImageDraw.Draw(im3)
        for t, cz in zip(Uv, cv[:, 2]):
            col = (0, 255, 255) if cz > 1.42 else ((255, 255, 0) if cz > 1.32 else (0, 110, 0))
            d.polygon([(float(u) * 1024, float(v) * 1024) for u, v in t], outline=col)
        im3.save(os.path.join(out, "samurai_vtk_left_layout.png"))
    print("pictures in", out)


if __name__ == "__main__":
    main(sys.argv[1])
