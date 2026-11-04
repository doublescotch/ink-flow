"""Who reads the top of the body texture (u 0.22-0.56, v 0.03-0.28), where the Samurai UV puts two big hex clusters
that no skin triangle drawn so far reads ?  Scans every mesh of the framework archive, the vanilla and Angel meshes,
ALL chunks of every appearance.  Then draws the full vanilla / Angel body layout over the UV and the VTK Samurai
body textures (2026-11-04, Fable, read only).

  python seam6.py <out dir>
"""
import base64, glob, json, os, struct, sys
import numpy as np
from PIL import Image, ImageDraw

ROOT = r"C:\__DEV\cyberpunk\ink_flow"
Image.MAX_IMAGE_PIXELS = None
REGION = (0.22, 0.56, 0.03, 0.28)


def read_all(path):
    """All LOD-0 chunks : list of (chunk index, material names per appearance, (n,3,3) P, (n,3,2) U)."""
    root = json.load(open(path, encoding="utf-8"))["Data"]["RootChunk"]
    rb = root["renderResourceBlob"]["Data"]; h = rb["header"]
    buf = base64.b64decode(rb["renderBuffer"]["Bytes"])
    qs = h["quantizationScale"]; qo = h["quantizationOffset"]
    scale = np.array([qs["X"], qs["Y"], qs["Z"]]); off = np.array([qo["X"], qo["Y"], qo["Z"]])
    apps = {a["Data"]["name"]["$value"]: [c["$value"] for c in a["Data"]["chunkMaterials"]] for a in root["appearances"]}
    sizes = {"PT_Float16_2": 4, "PT_Float16_4": 8, "PT_Short4N": 8, "PT_UByte4": 4, "PT_UByte4N": 4, "PT_Dec4": 4,
             "PT_Color": 4, "PT_Float32_2": 8, "PT_Float32_3": 12, "PT_Float32_4": 16}
    out = []
    for n, ci in enumerate(h["renderChunkInfos"]):
        if ci["lodMask"] != 1:
            continue
        cv = ci["chunkVertices"]; lay = cv["vertexLayout"]["elements"]["Elements"]; offs = cv["byteOffsets"]["Elements"]
        nv = ci["numVertices"]

        def stream_of(usage):
            e = next(x for x in lay if x["usage"] == usage and x["usageIndex"] == 0)
            st = [x for x in lay if x["streamIndex"] == e["streamIndex"] and x["streamType"] == "ST_PerVertex"]
            return offs[e["streamIndex"]], sum(sizes[x["type"]] for x in st), sum(sizes[x["type"]] for x in st[:st.index(e)])
        b, s, p = stream_of("PS_Position")
        pos = np.array([struct.unpack_from("<hhh", buf, b + i * s + p) for i in range(nv)], dtype=np.float64) / 32767.0 * scale + off
        b, s, p = stream_of("PS_TexCoord")
        uv = np.frombuffer(np.asarray([struct.unpack_from("<HH", buf, b + i * s + p) for i in range(nv)], dtype=np.uint16).tobytes(),
                           dtype=np.float16).astype(np.float64).reshape(nv, 2)
        idx = np.array(struct.unpack_from("<%dH" % ci["numIndices"], buf, h["indexBufferOffset"] + ci["chunkIndices"]["teOffset"]), dtype=np.int64)
        idx = idx[:len(idx) // 3 * 3].reshape(-1, 3)
        out.append((n, {a: m[n] if n < len(m) else "?" for a, m in apps.items()}, pos[idx], uv[idx]))
    return out


def in_region(U):
    c = U.mean(axis=1)
    return (c[:, 0] > REGION[0]) & (c[:, 0] < REGION[1]) & (c[:, 1] > REGION[2]) & (c[:, 1] < REGION[3])


def main(out):
    os.makedirs(out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(ROOT, r"dl\uv\x\011_UV_Framework_Texture_3.2.1", "**", "*.mesh.json"), recursive=True))
    files += [os.path.join(ROOT, r"gen\vanilla_test\mesh\body\base\characters\common\player_base_bodies\player_female_average\t0_000_pwa_base__full.mesh.json"),
              os.path.join(ROOT, r"gen\uv104\work_angel\mesh\body\base\characters\common\player_base_bodies\player_female_average\t0_000_pwa_base__full.mesh.json"),
              os.path.join(ROOT, r"gen\uv104\work_angel\mesh\arm_l\base\characters\common\player_base_bodies\player_female_average\arms_hq\a0_000_pwa_base_hq__l.mesh.json")]
    print(f"{len(files)} meshes scanned for triangles reading u {REGION[0]}-{REGION[1]}, v {REGION[2]}-{REGION[3]}")
    for f in files:
        try:
            chunks = read_all(f)
        except Exception as e:
            print("  !", os.path.relpath(f, ROOT)[-90:], "->", type(e).__name__); continue
        hits = [(n, mats, m.sum(), P[m].mean(axis=1)) for n, mats, P, U in chunks for m in [in_region(U)] if m.any()]
        if hits:
            print(" ", os.path.relpath(f, ROOT)[-100:])
            for n, mats, k, c in hits:
                mat = mats.get("01_ca_pale") or next(iter(mats.values()))
                print(f"     chunk {n:2d} ({mat}) : {k} triangles in the region, z {c[:, 2].min():.3f}-{c[:, 2].max():.3f}, x {c[:, 0].min():.3f}-{c[:, 0].max():.3f}")
    # full body layout over both Samurai body textures
    van = read_all(files[-3]); ang = read_all(files[-2])
    for name, rel in (("uv", r"dl\uv\conv\png\002_Tattoos_UV_Unknown_Samurai__fullbody_overlay_d01\fullbody_overlay_d01.png"),
                      ("vtk", r"dl\uv\png\samurai_body\v_overlay.png")):
        im = Image.open(os.path.join(ROOT, rel)).convert("RGB").resize((2048, 2048), Image.BILINEAR)
        d = ImageDraw.Draw(im)
        for n, mats, P, U in van:
            for t in U:
                d.polygon([(float(u) * 2048, float(v) * 2048) for u, v in t], outline=(0, 255, 0))
        for n, mats, P, U in ang:
            for t in U[::6]:
                d.polygon([(float(u) * 2048, float(v) * 2048) for u, v in t], outline=(255, 0, 255))
        im.crop((int(0.20 * 2048), 0, int(0.60 * 2048), 1024)).save(os.path.join(out, f"samurai_{name}_body_top_layout.png"))
    print("pictures in", out)


if __name__ == "__main__":
    main(sys.argv[1])
