"""UV coverage of the SKIN chunks only (chunks whose material in appearance `01_ca_pale` is a skin tint material), 64x64 mask ;
containment matrix ; share of the skin cells in the left strip (u < 0.22) ; maps at 1/32."""
import json, base64, struct, sys, os, math, re
SZ = {"PT_Float16_2": 4, "PT_Float16_4": 8, "PT_Short4N": 8, "PT_UByte4": 4, "PT_UByte4N": 4, "PT_Dec4": 4, "PT_Color": 4, "PT_Float32_2": 8, "PT_Float32_3": 12, "PT_Float32_4": 16, "PT_UShort2": 4, "PT_UByte1": 1, "PT_UInt1": 4}
SKIN = re.compile(r"^0[1-6]_(ca|bl)_[a-z]+(_body)?$")
def half(h):
    s = (h >> 15) & 1; e = (h >> 10) & 0x1f; f = h & 0x3ff
    if e == 0: v = (f / 1024.0) * 2.0 ** -14
    elif e == 31: v = float("nan")
    else: v = (1 + f / 1024.0) * 2.0 ** (e - 15)
    return -v if s else v
def tris(path):
    d = json.load(open(path, encoding="utf-8"))["Data"]["RootChunk"]
    rb = d["renderResourceBlob"]["Data"]; h = rb["header"]
    buf = base64.b64decode(rb["renderBuffer"]["Bytes"]); ib = h["indexBufferOffset"]
    app = next((a["Data"] for a in d["appearances"] if a["Data"]["name"]["$value"] == "01_ca_pale"), d["appearances"][0]["Data"])
    cm = [c["$value"] for c in app["chunkMaterials"]]
    out = []; kept = []; dropped = []
    for n, ci in enumerate(h["renderChunkInfos"]):
        if ci["lodMask"] != 1: continue
        mat = cm[n] if n < len(cm) else "?"
        if not SKIN.match(mat): dropped.append((n, mat, ci["numVertices"])); continue
        kept.append((n, mat, ci["numVertices"]))
        cv = ci["chunkVertices"]; lay = cv["vertexLayout"]["elements"]["Elements"]; offs = cv["byteOffsets"]["Elements"]
        tex = next(e for e in lay if e["usage"] == "PS_TexCoord" and e["usageIndex"] == 0); st = tex["streamIndex"]
        stream = [e for e in lay if e["streamIndex"] == st and e["streamType"] == "ST_PerVertex"]
        stride = sum(SZ[e["type"]] for e in stream); pos = sum(SZ[e["type"]] for e in stream[:stream.index(tex)])
        base = offs[st]; uv = []
        for i in range(ci["numVertices"]):
            a, b = struct.unpack_from("<HH", buf, base + i * stride + pos); uv.append((half(a), half(b)))
        idx = struct.unpack_from("<%dH" % ci["numIndices"], buf, ib + ci["chunkIndices"]["teOffset"])
        for k in range(0, len(idx) - 2, 3): out.append((uv[idx[k]], uv[idx[k+1]], uv[idx[k+2]]))
    return out, kept, dropped
def mask(tr, G):
    m = [[0]*G for _ in range(G)]
    wrap = lambda x: x - math.floor(x)
    for (a, b, c) in tr:
        pts = [(wrap(p[0]) * G, wrap(p[1]) * G) for p in (a, b, c)]
        if any(q != q for p in pts for q in p): continue
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, x1 = max(0, int(min(xs))), min(G - 1, int(max(xs))); y0, y1 = max(0, int(min(ys))), min(G - 1, int(max(ys)))
        (ax, ay), (bx, by), (cx, cy) = pts; det = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if det == 0: m[y][x] = 1; continue
                px, py = x + 0.5, y + 0.5
                l1 = ((bx - px) * (cy - py) - (cx - px) * (by - py)) / det; l2 = ((cx - px) * (ay - py) - (ax - px) * (cy - py)) / det
                if l1 >= -0.02 and l2 >= -0.02 and 1 - l1 - l2 >= -0.02: m[y][x] = 1
        for (x, y) in pts: m[min(G-1, int(y))][min(G-1, int(x))] = 1
    return m
G = 64
M = {}
for extra in sys.argv[1:]:
    k, v = extra.split("=", 1); M[k] = v
res = {}
for k, p in M.items():
    if not os.path.isfile(p): print(f"{k}: ABSENT {p}"); continue
    tr, kept, dropped = tris(p); m = mask(tr, G); cells = sum(map(sum, m))
    strip = sum(m[y][x] for y in range(G) for x in range(int(0.22 * G)))
    res[k] = m
    print(f"{k:18s} skin tris={len(tr):7d} cells={cells:5d}  strip(u<0.22)={strip/cells*100:5.1f}%  kept={[(n,v) for n,_,v in kept]}  dropped={[(n,mt,v) for n,mt,v in dropped]}")
keys = list(res)
print("\nA in B (fraction of A's skin cells also covered by B's skin) :")
print(" " * 18 + "".join(f"{k[:9]:>10s}" for k in keys))
for a in keys:
    ma = res[a]; na = sum(map(sum, ma)); row = f"{a:18s}"
    for b in keys:
        mb = res[b]; row += f"{sum(1 for y in range(G) for x in range(G) if ma[y][x] and mb[y][x])/na:10.2f}"
    print(row)
maps = {}
for k in keys:
    m = res[k]; maps[k] = ["".join("#" if any(m[y+dy][x+dx] for dy in range(2) for dx in range(2)) else "." for x in range(0, G, 2)) for y in range(0, G, 2)]
for i in range(0, len(keys), 3):
    grp = keys[i:i+3]; print(); print("   ".join(f"{n:34s}" for n in grp))
    for r in range(32): print("   ".join(f"{maps[n][r]:34s}" for n in grp))
