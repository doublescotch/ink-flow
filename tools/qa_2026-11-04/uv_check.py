"""Control of a UV build (uv_build.py solo|angel) : the archive unbundled and serialised ; listing by kind ; per .app
the component chunkMask ; per shell mesh the decal texture and the material count ; the switchers and options of the
female .inkcharcustomization (names per option = which targets each tattoo drives). Usage : uv_check.py solo|angel"""
import json, os, re, shutil, subprocess, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import env
from inkflow.config import Config

mode = sys.argv[1]
ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\uv104"
cli = env.find_wolvenkit(Config()["cli"])
d = os.path.join(ROOT, "u_" + mode)
shutil.rmtree(d, ignore_errors=True)
arc = os.path.join(ROOT, rf"out_{mode}\Ink_Flow.archive")
subprocess.run([cli, "unbundle", arc, "-o", d], capture_output=True, check=True)
files = sorted(os.path.relpath(os.path.join(r, f), d) for r, _, fs in os.walk(d) for f in fs)
kinds = {}
for f in files:
    kinds.setdefault(os.path.splitext(f)[1], []).append(f)
print(f"{mode}: {len(files)} files : " + ", ".join(f"{len(v)} {k}" for k, v in sorted(kinds.items())))
print("textures :", [os.path.basename(f) for f in kinds.get(".xbm", [])])
subprocess.run([cli, "convert", "serialize", os.path.join(d, "inkflow")], capture_output=True, check=True)
V = "$value"
# .app : chunk masks
masks = {}
for f in kinds.get(".app", []):
    j = json.load(open(os.path.join(d, f + ".json"), encoding="utf-8"))["Data"]["RootChunk"]
    comps = [c for a in j["appearances"] for c in a["Data"]["components"] if "chunkMask" in c]
    masks.setdefault(str([c["chunkMask"] for c in comps][:1]), []).append(os.path.basename(f))
for m, fs in sorted(masks.items()):
    print(f"chunkMask {m:24s} x{len(fs):3d} : {', '.join(sorted(fs)[:4])}{' …' if len(fs) > 4 else ''}")
# shells : decal texture, material count, vertex count
for f in kinds.get(".mesh", []):
    j = json.load(open(os.path.join(d, f + ".json"), encoding="utf-8"))["Data"]["RootChunk"]
    mats = j["localMaterialBuffer"]["materials"]
    texs = {v["DiffuseTexture"]["DepotPath"][V] for m in mats for v in m["values"] if "DiffuseTexture" in v}
    nv = sum(c["numVertices"] for c in j["renderResourceBlob"]["Data"]["header"]["renderChunkInfos"] if c["lodMask"] == 1)
    print(f"shell {os.path.basename(f):55s} {len(mats):2d} mat. {nv:6d} verts  tex={sorted(os.path.basename(t) for t in texs)}")
# inkcharcustomization : options and their names
for f in kinds.get(".inkcharcustomization", []):
    root = json.load(open(os.path.join(d, f + ".json"), encoding="utf-8"))["Data"]["RootChunk"]
    sw = [h["Data"] for h in root["bodyCustomizationOptions"] if h["Data"]["$type"] == "gameuiSwitcherInfo"]
    print(f"{os.path.basename(f)}: {len(root['bodyCustomizationOptions'])} entries, {len(sw)} switchers, groups "
          + str([(g["name"][V], len(g["options"])) for g in root["bodyGroups"]]))
    for s in sw:
        if s["name"][V].endswith("slot1") or s["name"][V].endswith("slot1_fpp"):
            print(f"   {s['name'][V]} uiSlots={[u[V] for u in s['uiSlots']]}")
            for o in s["options"]:
                names = [n[V] for n in o["names"]]
                print(f"      {o['index']:2d} {o['localizedName']:45s} " + ", ".join(re.sub(r"^inkflow_slot1_", "", n) for n in names))
