"""Arm texture conversion between the two arm layouts (ETUDE § 22, measured 2026-11-04).

The vanilla arm (base game) and the UV Framework's copy of it are the same geometry with two UV layouts : the vanilla
arm layout (a texture of its own, what every VTK arm uses, Angel's within a texel) and the UV strip (u < 0.22 of the
body texture : left arm in v < 0.5, right arm in v > 0.5). Each skin triangle of one is paired with the triangle at
the same 3D place in the other ; every texel of the destination layout gets the source UV at the same barycentric
point ; the source texture is read there. Two directions :
  "full"  : a UV tattoo's arm (strip of its body texture) -> a vanilla-layout arm texture, for VTK / vanilla arms ;
  "strip" : a VTK arm texture -> a body-sized texture with only that arm's strip filled, for UV arms (Solo, Songbird).
Textures go through DDS (RGBA8, what WolvenKit exports) : read and written here, numpy only.
"""
import base64
import json
import struct

import numpy as np

VTX_SIZE = {"PT_Float16_2": 4, "PT_Float16_4": 8, "PT_Short4N": 8, "PT_UByte4": 4, "PT_UByte4N": 4, "PT_Dec4": 4,
            "PT_Color": 4, "PT_Float32_2": 8, "PT_Float32_3": 12, "PT_Float32_4": 16, "PT_UShort2": 4, "PT_UByte1": 1,
            "PT_UInt1": 4, "PT_Float32_1": 4, "PT_Float16_1": 2, "PT_Float16_3": 6, "PT_Short4": 8, "PT_Short2": 4}
PAIR_TOL = 1e-3          # metres : two triangles are "the same" when every corner is within 1 mm (measured : 14-50 µm)
PAIR_MIN = 0.98          # share of the destination triangles that must pair, else the two meshes are not the same arm
DILATE = 8               # texels around each island filled with the nearest value (filtering and mip seams)
STRIP_U = 0.25           # destination region of a "strip" texture : u < 0.25 (the strip is u < 0.22), half the height


class ConvError(Exception):
    pass


# ----------------------------------------------------------------------------- meshes
def skin_tris(mesh_json, is_skin, appearance):
    """Skin triangles of LOD 0 : positions (n, 3, 3) and UVs (n, 3, 2), from a serialised mesh."""
    with open(mesh_json, encoding="utf-8") as f:
        root = json.load(f)["Data"]["RootChunk"]
    rb = root["renderResourceBlob"]["Data"]
    h = rb["header"]
    buf = base64.b64decode(rb["renderBuffer"]["Bytes"])
    qs, qo = h["quantizationScale"], h["quantizationOffset"]
    scale = np.array([qs["X"], qs["Y"], qs["Z"]])
    off = np.array([qo["X"], qo["Y"], qo["Z"]])
    app = next((a["Data"] for a in root.get("appearances", []) if a["Data"]["name"]["$value"] == appearance), None)
    mats = [c["$value"] for c in app["chunkMaterials"]] if app else []
    P, U = [], []
    for n, ci in enumerate(h["renderChunkInfos"]):
        if ci["lodMask"] != 1 or (n < len(mats) and not is_skin(mats[n])):
            continue
        cv = ci["chunkVertices"]
        lay = cv["vertexLayout"]["elements"]["Elements"]
        offs = cv["byteOffsets"]["Elements"]
        nv = ci["numVertices"]

        def column(usage, kind, dtype):
            e = next((x for x in lay if x["usage"] == usage and x["usageIndex"] == 0), None)
            if e is None or e["type"] != kind:
                raise ConvError(f"{mesh_json}: chunk {n}: {usage} missing or not {kind}")
            st = [x for x in lay if x["streamIndex"] == e["streamIndex"] and x["streamType"] == "ST_PerVertex"]
            stride = sum(VTX_SIZE.get(x["type"], 4) for x in st)
            pos = sum(VTX_SIZE.get(x["type"], 4) for x in st[:st.index(e)])
            size = VTX_SIZE[kind]
            raw = np.frombuffer(buf, dtype=np.uint8, count=stride * (nv - 1) + size, offset=offs[e["streamIndex"]] + pos)
            rows = np.lib.stride_tricks.as_strided(raw, shape=(nv, size), strides=(stride, 1))
            return np.ascontiguousarray(rows).view(dtype)
        pos = column("PS_Position", "PT_Short4N", "<i2").astype(np.float64)[:, :3] / 32767.0 * scale + off
        uv = column("PS_TexCoord", "PT_Float16_2", "<f2").astype(np.float64)
        idx = np.frombuffer(buf, dtype="<u2", count=ci["numIndices"], offset=h["indexBufferOffset"] + ci["chunkIndices"]["teOffset"])
        idx = idx[:len(idx) // 3 * 3].astype(np.int64).reshape(-1, 3)
        P.append(pos[idx])
        U.append(uv[idx])
    if not P:
        raise ConvError(f"{mesh_json}: no skin triangle")
    return np.concatenate(P), np.concatenate(U)


def pair(Pd, Ps, k=4, chunk=512):
    """For every destination triangle : the source triangle at the same place (-1 if none within PAIR_TOL) and the
    source corner matching each destination corner. Brute force on centroids, by chunks (9 000 x 9 000 : ~1 s)."""
    cd, cs = Pd.mean(axis=1), Ps.mean(axis=1)
    best = np.full(len(Pd), -1)
    order = np.zeros((len(Pd), 3), dtype=np.int64)
    err = np.full(len(Pd), np.inf)
    for a in range(0, len(Pd), chunk):
        d2 = ((cd[a:a + chunk, None, :] - cs[None, :, :]) ** 2).sum(axis=2)
        cand = np.argpartition(d2, k, axis=1)[:, :k]                                         # (c, k)
        corners = np.linalg.norm(Pd[a:a + chunk, None, :, None, :] - Ps[cand][:, :, None, :, :], axis=4)  # (c, k, 3, 3)
        o = corners.argmin(axis=3)                                                            # (c, k, 3)
        e = np.take_along_axis(corners, o[..., None], axis=3)[..., 0].max(axis=2)             # (c, k)
        distinct = (o[..., 0] != o[..., 1]) & (o[..., 1] != o[..., 2]) & (o[..., 0] != o[..., 2])
        e = np.where(distinct, e, np.inf)
        j = e.argmin(axis=1)
        r = np.arange(len(j))
        ok = e[r, j] < PAIR_TOL
        sel = np.nonzero(ok)[0]
        best[a + sel] = cand[sel, j[sel]]
        order[a + sel] = o[sel, j[sel]]
        err[a + sel] = e[sel, j[sel]]
    return best, order, err


def pairing(dst_mesh, src_mesh, is_skin, appearance):
    """-> (destination UV triangles, matching source UV triangles, share paired). Raises ConvError below PAIR_MIN."""
    Pd, Ud = skin_tris(dst_mesh, is_skin, appearance)
    Ps, Us = skin_tris(src_mesh, is_skin, appearance)
    best, order, _ = pair(Pd, Ps)
    ok = best >= 0
    share = ok.mean()
    if share < PAIR_MIN:
        raise ConvError(f"the two arm meshes do not match ({share:.1%} of the triangles paired)")
    src = np.take_along_axis(Us[best[ok]], order[ok][..., None], axis=1)
    return Ud[ok], src, share


# ----------------------------------------------------------------------------- raster
def uv_map(dst_uv, src_uv, size, region):
    """Per texel of the destination region (x0, y0, w, h in texels of a `size` texture) : the source UV (float32 x2),
    NaN where no triangle covers it ; then `DILATE` texels around the islands."""
    x0, y0, w, h = region
    M = np.full((h, w, 2), np.nan, dtype=np.float32)
    tol = 1e-4
    for a, src in zip(dst_uv * size, src_uv):
        lo = np.floor(a.min(axis=0)).astype(int)
        hi = np.ceil(a.max(axis=0)).astype(int)
        bx0, by0 = max(lo[0], x0), max(lo[1], y0)
        bx1, by1 = min(hi[0], x0 + w - 1), min(hi[1], y0 + h - 1)
        if bx1 < bx0 or by1 < by0:
            continue
        (ax, ay), (bx, by), (cx, cy) = a
        det = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
        if abs(det) < 1e-12:
            continue
        ys, xs = np.mgrid[by0:by1 + 1, bx0:bx1 + 1]
        px, py = xs + 0.5, ys + 0.5
        l1 = ((bx - px) * (cy - py) - (cx - px) * (by - py)) / det
        l2 = ((cx - px) * (ay - py) - (ax - px) * (cy - py)) / det
        l3 = 1 - l1 - l2
        ins = (l1 >= -tol) & (l2 >= -tol) & (l3 >= -tol)
        if not ins.any():
            continue
        yy, xx = ys[ins] - y0, xs[ins] - x0
        M[yy, xx, 0] = l1[ins] * src[0, 0] + l2[ins] * src[1, 0] + l3[ins] * src[2, 0]
        M[yy, xx, 1] = l1[ins] * src[0, 1] + l2[ins] * src[1, 1] + l3[ins] * src[2, 1]
    for _ in range(DILATE):                      # grow the islands by one texel (4 neighbours), nearest-like fill
        hole = np.isnan(M[..., 0])
        if not hole.any():
            break
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = np.full_like(M, np.nan)
            nb[max(dy, 0):h + min(dy, 0), max(dx, 0):w + min(dx, 0)] = M[max(-dy, 0):h + min(-dy, 0), max(-dx, 0):w + min(-dx, 0)]
            fill = hole & ~np.isnan(nb[..., 0])
            M[fill] = nb[fill]
            hole &= ~fill
    return M


def sample(img, M, crop):
    """Bilinear read of `img` (h, w, 4 uint8 : the cropped source, `crop` = its x0, y0 and the full source size) at the
    UVs of M ; 0 (transparent) where M is NaN."""
    cx0, cy0, W, H = crop
    ok = ~np.isnan(M[..., 0])
    u = np.where(ok, M[..., 0], 0.0)
    v = np.where(ok, M[..., 1], 0.0)
    u -= np.floor(u)
    v -= np.floor(v)
    x = u * W - 0.5 - cx0
    y = v * H - 0.5 - cy0
    hh, ww = img.shape[:2]
    x = np.clip(x, 0, ww - 1)
    y = np.clip(y, 0, hh - 1)
    xa = np.floor(x).astype(np.int64)
    ya = np.floor(y).astype(np.int64)
    xb, yb = np.minimum(xa + 1, ww - 1), np.minimum(ya + 1, hh - 1)
    fx, fy = (x - xa)[..., None], (y - ya)[..., None]
    f = img.astype(np.float32)
    out = (f[ya, xa] * (1 - fx) * (1 - fy) + f[ya, xb] * fx * (1 - fy) + f[yb, xa] * (1 - fx) * fy + f[yb, xb] * fx * fy)
    out = np.clip(np.rint(out), 0, 255).astype(np.uint8)
    out[~ok] = 0
    return out


# ----------------------------------------------------------------------------- DDS
def dds_top(path):
    """Top mip of an RGBA8 DDS written by WolvenKit (DX10 header, DXGI 28 / 29) : a read-only (h, w, 4) memmap."""
    with open(path, "rb") as f:
        head = f.read(148)
    if head[:4] != b"DDS ":
        raise ConvError("not a DDS file: " + path)
    h, w = struct.unpack_from("<II", head, 12)
    if head[84:88] == b"DX10":
        if struct.unpack_from("<I", head, 128)[0] not in (28, 29):
            raise ConvError("DDS not RGBA8: " + path)
        off = 148
    elif struct.unpack_from("<I", head, 88)[0] == 32 and struct.unpack_from("<I", head, 92)[0] == 0xFF:
        off = 128
    else:
        raise ConvError("DDS not RGBA8: " + path)
    return np.memmap(path, dtype=np.uint8, mode="r", offset=off, shape=(h, w, 4))


def _half(a):
    """2 x 2 box filter, colour weighted by alpha (so transparent texels do not darken the ink)."""
    h, w = max(1, a.shape[0] // 2), max(1, a.shape[1] // 2)
    q = a[:h * 2, :w * 2].astype(np.float32).reshape(h, a.shape[0] // h, w, a.shape[1] // w, 4)
    al = q[..., 3:4].sum(axis=(1, 3))
    b = q.mean(axis=(1, 3))
    rgb = (q[..., :3] * q[..., 3:4]).sum(axis=(1, 3))
    b[..., :3] = np.where(al > 0, rgb / np.maximum(al, 1e-9), b[..., :3])
    return np.clip(np.rint(b), 0, 255).astype(np.uint8)


def write_dds(path, size, region, img):
    """Square RGBA8 DDS of `size` with a full mip chain ; `img` fills `region` (x0, y0, w, h), the rest is transparent.
    The region is power-of-two aligned, so its mips stay aligned ; written level by level, row blocks of zeros."""
    x0, y0, w, h = region
    levels = size.bit_length()
    flags = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000 | 0x20000
    head = struct.pack("<4sIIIIIII44x", b"DDS ", 124, flags, size, size, size * 4, 0, levels)
    pf = struct.pack("<II4sIIIII", 32, 0x4, b"DX10", 0, 0, 0, 0, 0)
    caps = struct.pack("<IIIII", 0x1000 | 0x8 | 0x400000, 0, 0, 0, 0)
    dx10 = struct.pack("<IIIII", 28, 3, 0, 1, 0)
    with open(path, "wb") as f:
        f.write(head + pf + caps + dx10)
        cur, full = img, None
        for lv in range(levels):
            s = max(1, size >> lv)
            if full is None and (s <= 256 or cur.shape[0] < 2 or cur.shape[1] < 2):
                full = np.zeros((s, s, 4), dtype=np.uint8)
                rx, ry = x0 >> lv, y0 >> lv
                full[ry:ry + cur.shape[0], rx:rx + cur.shape[1]] = cur
            if full is not None:
                f.write(full.tobytes())
                if s > 1:
                    full = _half(full)
                continue
            rx, ry = x0 >> lv, y0 >> lv
            block = 256
            for r0 in range(0, s, block):
                rows = np.zeros((min(block, s - r0), s, 4), dtype=np.uint8)
                a, b = max(r0, ry), min(r0 + len(rows), ry + cur.shape[0])
                if a < b:
                    rows[a - r0:b - r0, rx:rx + cur.shape[1]] = cur[a - ry:b - ry]
                f.write(rows.tobytes())
            cur = _half(cur)


# ----------------------------------------------------------------------------- one conversion
def convert(direction, van_mesh, strip_mesh, src_dds, out_dds, is_skin, appearance):
    """`direction` "full" : UV body texture (src) -> vanilla-layout arm texture ; "strip" : VTK arm texture (src) ->
    body-sized texture with the arm in its strip. Writes `out_dds`. -> dict(size, share, ink) ; ink = share of the
    arm's texels with alpha > 16 (0 : nothing to show on this arm)."""
    img = dds_top(src_dds)
    H, W = img.shape[:2]
    if direction == "full":
        dst_uv, src_uv, share = pairing(van_mesh, strip_mesh, is_skin, appearance)
    else:
        dst_uv, src_uv, share = pairing(strip_mesh, van_mesh, is_skin, appearance)
    # Image rows run the other way than mesh v : in the picture WolvenKit exports and imports, row y of a texture of
    # height h is mesh v = 1 - y / h (in-game canari of 2026-11-04 : a texture painted in the picture's top half, where
    # the left arm's v < 0.5 would sit with v = y / h, rendered on the RIGHT arm). Both the source read and the
    # destination write go through the picture, so both UV sets are flipped here ; a UV tattoo hid the mistake
    # (its right arm is the vertical mirror of its left arm), a converted arm showed up on no arm at all.
    dst_uv, src_uv = dst_uv.copy(), src_uv.copy()
    dst_uv[..., 1] = 1.0 - dst_uv[..., 1]
    src_uv[..., 1] = 1.0 - src_uv[..., 1]
    if direction == "full":
        size = max(1024, W // 2)                    # the arm takes ~8 % of a UV texture, ~50 % of an arm texture
        region = (0, 0, size, size)
        top = src_uv[..., 1].mean() < 0.5
        crop = (0, 0 if top else H // 2, W // 4, H // 2)                # the arm's half of the strip, u < 0.25
    else:
        size = min(8192, W * 2)
        top = dst_uv[..., 1].mean() < 0.5
        if dst_uv[..., 0].max() > STRIP_U:
            raise ConvError(f"UV arm outside the strip (u max {dst_uv[..., 0].max():.3f})")
        region = (0, 0 if top else size // 2, int(size * STRIP_U), size // 2)
        crop = (0, 0, W, H)
    cx0, cy0, cw, ch = crop
    src = np.asarray(img[cy0:cy0 + ch, cx0:cx0 + cw])
    M = uv_map(dst_uv, src_uv, size, region)
    out = sample(src, M, (cx0, cy0, W, H))
    covered = ~np.isnan(M[..., 0])
    ink = float((out[..., 3][covered] > 16).mean()) if covered.any() else 0.0
    write_dds(out_dds, size, region, out)
    return dict(size=size, share=float(share), ink=ink)
