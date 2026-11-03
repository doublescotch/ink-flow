"""Control of the mixed build (male_build.py mixed) : both .inkcharcustomization unbundled and serialised ; per gender
the switchers (index, link, linkController, uiSlots), the groups and their option counts ; the male body shell vs the
active Gymfiend body (vertices, decal materials)."""
import json, os, shutil, subprocess, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import env
from inkflow.config import Config

ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\m103"
cli = env.find_wolvenkit(Config()["cli"])
d = os.path.join(ROOT, "u_mixed")
shutil.rmtree(d, ignore_errors=True)
subprocess.run([cli, "unbundle", os.path.join(ROOT, r"out_mixed\Ink_Flow.archive"), "-o", d, "-r",
                r"(\.inkcharcustomization|kala_tattoo_japanesefaded_fullbody_overl_pma_m\.mesh|kala_tattoo_japanesefaded_fullbody_overl_slot1_m\.app)$"],
               capture_output=True, check=True)
subprocess.run([cli, "convert", "serialize", d], capture_output=True, check=True)
V = "$value"
for tag in ("pwa", "pma"):
    root = json.load(open(os.path.join(d, rf"inkflow\inkflow_{tag}.inkcharcustomization.json"), encoding="utf-8"))["Data"]["RootChunk"]
    sw = [h["Data"] for h in root["bodyCustomizationOptions"] if h["Data"]["$type"] == "gameuiSwitcherInfo"]
    print(f"{tag}: {len(root['bodyCustomizationOptions'])} entries, {len(sw)} switchers")
    for s in sw[:3]:
        print(f"   {s['name'][V]:22s} index {s['index']} link {s.get('link', {}).get(V)} ctrl {s.get('linkController')} "
              f"uiSlots {[u[V] for u in s['uiSlots']]} options {len(s['options'])}")
    print("   groups", [(g["name"][V], len(g["options"])) for g in root["bodyGroups"]])
for p, what in ((r"inkflow\tattoos\kala_tattoo_japanesefaded_fullbody_overl\kala_tattoo_japanesefaded_fullbody_overl_pma_m.mesh", "shell"),
                (r"base\characters\common\player_base_bodies\player_man_average\t0_000_pma_base__full.mesh", "gymfiend")):
    f = os.path.join(d if what == "shell" else os.path.join(ROOT, r"work\mesh\m_body"), p + ".json")
    r = json.load(open(f, encoding="utf-8"))["Data"]["RootChunk"]
    ch = r["renderResourceBlob"]["Data"]["header"]["renderChunkInfos"]
    mats = r["localMaterialBuffer"]["materials"]
    print(f"{what}: {len(ch)} chunks, {sum(c['numVertices'] for c in ch)} vertices, {len(mats)} materials, base "
          f"{sorted({m['baseMaterial']['DepotPath'][V].rsplit(chr(92), 1)[-1] for m in mats})[:3]}")
app = json.load(open(os.path.join(d, r"inkflow\tattoos\kala_tattoo_japanesefaded_fullbody_overl\kala_tattoo_japanesefaded_fullbody_overl_slot1_m.app.json"), encoding="utf-8"))
for c in app["Data"]["RootChunk"]["appearances"][0]["Data"]["components"]:
    if "mesh" in c:
        print("app component:", c["$type"], c["name"][V], c["mesh"]["DepotPath"][V])
