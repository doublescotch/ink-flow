"""Same author, two files : pixel difference between the VTK body texture (v_overlay) and the body part of the UV
texture (fullbody_overlay_d01), which share the vanilla body layout (ETUDE 21), and between the VTK arm texture and
the UV arm converted to the vanilla arm layout.  Where does the VTK version carry ink that the UV one has not, in 3D
(height bands of the vanilla body / arm) ?  (2026-11-04, Fable, read only.)

  python seam7.py <name> <vtk body png> <uv body png> <out dir> [<vtk arm_l png> <converted uv arm_l png>]
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from seam import VAN, load

Image.MAX_IMAGE_PIXELS = None
N = 2048


def alpha(path):
    im = Image.open(path).convert("RGBA").resize((N, N), Image.BILINEAR)
    return np.asarray(im)[:, :, 3] > 64


def bands_report(P, U, A_vtk, A_uv, label, lo_z, hi_z, step=0.02):
    c = P.mean(axis=1); uv = U.mean(axis=1)
    x = np.clip((uv[:, 0] * N).astype(int), 0, N - 1); y = np.clip((uv[:, 1] * N).astype(int), 0, N - 1)
    v, u = A_vtk[y, x], A_uv[y, x]
    print(f"{label} : per height band, % of skin triangles inked in the VTK file / in the UV file / VTK only / UV only")
    for lo in np.arange(hi_z, lo_z, -step):
        m = (c[:, 2] >= lo) & (c[:, 2] < lo + step)
        if m.sum() > 5:
            print(f"   z {lo:.2f}-{lo + step:.2f} (n={m.sum():5d}) : VTK {v[m].mean() * 100:5.1f}  UV {u[m].mean() * 100:5.1f}  "
                  f"VTK only {(v[m] & ~u[m]).mean() * 100:5.1f}  UV only {(u[m] & ~v[m]).mean() * 100:5.1f}")
    both = (v & u).sum(); print(f"   whole mesh : VTK {v.mean() * 100:.1f} %, UV {u.mean() * 100:.1f} %, agreement on inked triangles "
                                f"{both / max(1, (v | u).sum()) * 100:.1f} % (Jaccard)")


def diff_picture(A_vtk, A_uv, U, out_path, crop=None):
    img = np.zeros((N, N, 3), dtype=np.uint8)
    img[A_vtk & A_uv] = (235, 235, 235); img[A_vtk & ~A_uv] = (255, 40, 40); img[~A_vtk & A_uv] = (40, 120, 255)
    im = Image.fromarray(img); d = ImageDraw.Draw(im)
    for t in U:
        d.polygon([(float(a) * N, float(b) * N) for a, b in t], outline=(0, 160, 0))
    if crop:
        im = im.crop(crop)
    im.save(out_path)


def main(argv):
    name, vtk_body, uv_body, out = argv[:4]
    os.makedirs(out, exist_ok=True)
    Av, Au = alpha(vtk_body), alpha(uv_body)
    Au[:, :int(0.22 * N)] = False                      # the strip is not body
    Pb, Ub = load(VAN, "body")
    print(f"== {name} : body (vanilla layout, {N}) ==")
    bands_report(Pb, Ub, Av, Au, "body", 0.90, 1.54)
    diff_picture(Av, Au, Ub, os.path.join(out, f"{name}_body_diff.png"), crop=(int(0.20 * N), 0, N, N))
    if len(argv) >= 6:
        Aav, Aau = alpha(argv[4]), alpha(argv[5])
        Pa, Ua = load(VAN, "arm_l")
        print(f"== {name} : left arm (vanilla arm layout, VTK file against the converted UV strip) ==")
        bands_report(Pa, Ua, Aav, Aau, "arm_l", 1.00, 1.54)
        diff_picture(Aav, Aau, Ua, os.path.join(out, f"{name}_arm_l_diff.png"))
    print("pictures in", out)


if __name__ == "__main__":
    main(sys.argv[1:])
