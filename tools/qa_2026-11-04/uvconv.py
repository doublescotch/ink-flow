"""Arm conversion UV -> vanilla layout, measurement only (ETUDE § 21, point 4 ; 2026-11-04, Opus).

Two meshes with the same arm geometry and two UV layouts : the vanilla arm (its own texture, `femme_arm_*_overlay`)
and the UV Framework arm (the strip u < 0.22 of the body texture). Each vanilla skin triangle is paired with the
framework triangle at the same 3D place ; every texel of the vanilla layout gets the framework UV at the same
barycentric point ; the UV body texture is sampled there. Then compared with the VTK version of the same tattoo.

  python uvconv.py <vanilla arm mesh.json> <framework arm mesh.json> <UV body png> <out png> [<VTK arm png>] [--size N]
"""
import base64, json, math, struct, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree

Image.MAX_IMAGE_PIXELS = None
SKIN = ("01_ca_pale",)          # prefix of the skin tints in appearance 01_ca_pale (vanilla arms : chunks 0-2)


def half(a):
    return np.frombuffer(np.asarray(a, dtype=np.uint16).tobytes(), dtype=np.float16).astype(np.float64)


def read(path):
    """Skin triangles of LOD 0 : (n, 3, 3) positions, (n, 3, 2) UVs."""
    root = json.load(open(path, encoding="utf-8"))["Data"]["RootChunk"]
    rb = root["renderResourceBlob"]["Data"]
    h = rb["header"]
    buf = base64.b64decode(rb["renderBuffer"]["Bytes"])
    qs = h["quantizationScale"]; qo = h["quantizationOffset"]
    scale = np.array([qs["X"], qs["Y"], qs["Z"]]); off = np.array([qo["X"], qo["Y"], qo["Z"]])
    app = next(a["Data"] for a in root["appearances"] if a["Data"]["name"]["$value"] == "01_ca_pale")
    mats = [c["$value"] for c in app["chunkMaterials"]]
    sizes = {"PT_Float16_2": 4, "PT_Float16_4": 8, "PT_Short4N": 8, "PT_UByte4": 4, "PT_UByte4N": 4, "PT_Dec4": 4,
             "PT_Color": 4, "PT_Float32_2": 8, "PT_Float32_3": 12, "PT_Float32_4": 16}
    P, U = [], []
    for n, ci in enumerate(h["renderChunkInfos"]):
        if ci["lodMask"] != 1 or not mats[n].startswith(SKIN):
            continue
        cv = ci["chunkVertices"]
        lay = cv["vertexLayout"]["elements"]["Elements"]
        offs = cv["byteOffsets"]["Elements"]
        nv = ci["numVertices"]

        def stream_of(usage):
            e = next(x for x in lay if x["usage"] == usage and x["usageIndex"] == 0)
            st = [x for x in lay if x["streamIndex"] == e["streamIndex"] and x["streamType"] == "ST_PerVertex"]
            stride = sum(sizes[x["type"]] for x in st)
            pos = sum(sizes[x["type"]] for x in st[:st.index(e)])
            return offs[e["streamIndex"]], stride, pos
        b, s, p = stream_of("PS_Position")
        raw = np.array([struct.unpack_from("<hhh", buf, b + i * s + p) for i in range(nv)], dtype=np.float64)
        pos = raw / 32767.0 * scale + off
        b, s, p = stream_of("PS_TexCoord")
        uv = half([struct.unpack_from("<HH", buf, b + i * s + p) for i in range(nv)]).reshape(nv, 2)
        idx = np.array(struct.unpack_from("<%dH" % ci["numIndices"], buf, h["indexBufferOffset"] +
                                          ci["chunkIndices"]["teOffset"]), dtype=np.int64)
        idx = idx[:len(idx) // 3 * 3].reshape(-1, 3)
        P.append(pos[idx]); U.append(uv[idx])
    return np.concatenate(P), np.concatenate(U)


def pair(Pv, Pf):
    """For each vanilla triangle : index of the framework triangle at the same place, and the corner order."""
    tree = cKDTree(Pf.mean(axis=1))
    d, j = tree.query(Pv.mean(axis=1), k=4)
    best = np.full(len(Pv), -1); order = np.zeros((len(Pv), 3), dtype=np.int64); err = np.full(len(Pv), np.inf)
    for t in range(len(Pv)):
        for jj in j[t]:
            dd = np.linalg.norm(Pv[t][:, None, :] - Pf[jj][None, :, :], axis=2)      # 3 x 3 corner distances
            o = dd.argmin(axis=1)
            e = dd[np.arange(3), o].max()
            if len(set(o)) == 3 and e < err[t]:
                err[t], best[t], order[t] = e, jj, o
    return best, order, err


def raster(Uv, Uf, best, order, size, tol):
    """Per texel of the vanilla layout : framework UV (float32 x2) and coverage."""
    M = np.full((size, size, 2), np.nan, dtype=np.float32)
    for t in np.nonzero(best >= 0)[0]:
        a = Uv[t] * size                       # pixel coords (x = u, y = v), same convention on both sides
        src = Uf[best[t]][order[t]]
        x0, y0 = np.floor(a.min(axis=0)).astype(int); x1, y1 = np.ceil(a.max(axis=0)).astype(int)
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, size - 1), min(y1, size - 1)
        if x1 < x0 or y1 < y0:
            continue
        ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
        px, py = xs + 0.5, ys + 0.5
        (ax, ay), (bx, by), (cx, cy) = a
        det = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
        if abs(det) < 1e-12:
            continue
        l1 = ((bx - px) * (cy - py) - (cx - px) * (by - py)) / det
        l2 = ((cx - px) * (ay - py) - (ax - px) * (cy - py)) / det
        l3 = 1 - l1 - l2
        inside = (l1 >= -tol) & (l2 >= -tol) & (l3 >= -tol)
        if not inside.any():
            continue
        su = l1 * src[0, 0] + l2 * src[1, 0] + l3 * src[2, 0]
        sv = l1 * src[0, 1] + l2 * src[1, 1] + l3 * src[2, 1]
        M[ys[inside], xs[inside], 0] = su[inside]
        M[ys[inside], xs[inside], 1] = sv[inside]
    return M


def dilate(M, px):
    """Uncovered texels within `px` of an island take the nearest covered value (mip / filtering seams)."""
    hole = np.isnan(M[..., 0])
    d, (iy, ix) = ndimage.distance_transform_edt(hole, return_indices=True)
    near = hole & (d <= px)
    M[near] = M[iy[near], ix[near]]
    return M


def sample(img, M):
    H, W = img.shape[:2]
    ok = ~np.isnan(M[..., 0])
    out = np.zeros(M.shape[:2] + (img.shape[2],), dtype=np.uint8)
    u = np.where(ok, M[..., 0], 0); v = np.where(ok, M[..., 1], 0)
    u = u - np.floor(u); v = v - np.floor(v)
    coords = [v * H - 0.5, u * W - 0.5]
    for c in range(img.shape[2]):
        out[..., c] = np.clip(ndimage.map_coordinates(img[..., c], coords, order=1, mode="nearest"), 0, 255)
    out[~ok] = 0
    return out


def main(argv):
    size = 4096
    if "--size" in argv:
        i = argv.index("--size"); size = int(argv[i + 1]); del argv[i:i + 2]
    van, fw, body, out = argv[:4]
    vtk = argv[4] if len(argv) > 4 else None
    t0 = time.time()
    Pv, Uv = read(van); Pf, Uf = read(fw)
    print(f"vanilla skin tris {len(Pv)}, framework skin tris {len(Pf)} ; framework u max {np.nanmax(Uf[..., 0] % 1):.3f}")
    best, order, err = pair(Pv, Pf)
    ok = best >= 0
    print(f"paired {ok.sum()}/{len(Pv)} ; corner error (m) median {np.median(err[ok]):.2e}, p99 {np.percentile(err[ok], 99):.2e}, "
          f"max {err[ok].max():.2e} ; > 1 mm : {(err > 1e-3).sum()}   ({time.time() - t0:.1f} s)")
    M = raster(Uv, Uf, best, order, size, tol=1e-4)
    cov = (~np.isnan(M[..., 0])).mean()
    M = dilate(M, 8)
    print(f"raster {size}: coverage {cov * 100:.1f} % of the texture ; framework u range "
          f"{np.nanmin(M[..., 0]):.3f}-{np.nanmax(M[..., 0]):.3f}, v {np.nanmin(M[..., 1]):.3f}-{np.nanmax(M[..., 1]):.3f}"
          f"   ({time.time() - t0:.1f} s)")
    img = np.asarray(Image.open(body).convert("RGBA"))
    conv = sample(img, M)
    Image.fromarray(conv).save(out)
    print(f"converted -> {out}   ({time.time() - t0:.1f} s)")
    if vtk:
        ref = np.asarray(Image.open(vtk).convert("RGBA").resize((size, size), Image.BILINEAR))
        a, b = conv[..., 3].astype(np.float64), ref[..., 3].astype(np.float64)
        isl = ~np.isnan(M[..., 0])
        a, b = a[isl], b[isl]
        corr = np.corrcoef(a, b)[0, 1]
        ia, ib = a > 64, b > 64
        iou = (ia & ib).sum() / max(1, (ia | ib).sum())
        print(f"vs VTK ({vtk.split('/')[-1]}) on the islands : alpha correlation {corr:.3f}, ink IoU (alpha > 64) {iou:.3f}, "
              f"ink share converted {ia.mean() * 100:.1f} % / VTK {ib.mean() * 100:.1f} %, "
              f"mean |d alpha| {np.abs(a - b).mean():.1f}")
        sm = 1024
        pair_img = Image.new("RGBA", (sm * 2, sm), (40, 40, 40, 255))
        for k, im in enumerate((conv, ref)):
            bg = Image.new("RGBA", (sm, sm), (200, 190, 180, 255))
            bg.alpha_composite(Image.fromarray(im).resize((sm, sm), Image.BILINEAR))
            pair_img.paste(bg, (k * sm, 0))
        pair_img.save(out.replace(".png", "_vs_vtk.png"))


if __name__ == "__main__":
    main(sys.argv[1:])
