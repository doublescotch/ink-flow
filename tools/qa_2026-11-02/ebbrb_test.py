"""Same engine code path as a player whose archive\\pc\\mod holds EBBRB 5.0.0 only : which meshes does it ship, and does
shell() accept them ?"""
import os, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import core, rdar

GAME = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
CLI = os.path.join(os.environ["LOCALAPPDATA"], r"InkFlow\wolvenkit\9.1.0\WolvenKit.CLI.exe")
MOD = r"C:\__DEV\cyberpunk\ink_flow\dl\4654\ebbrb\archive\pc\mod"
WORK = r"C:\__DEV\cyberpunk\ink_flow\gen\ebbrb_test"
os.makedirs(WORK, exist_ok=True)
core.mod_dir = lambda game: MOD
log = lambda *a: print(" ".join(str(x) for x in a), flush=True)
cli = core.Cli(CLI, log)

arc = os.path.join(MOD, "05_Hyst_Refit_ForcedBigBreastsBooty.archive")
hs = rdar.hashes(arc)
print("entries in EBBRB archive:", len(hs))
paths = [t["mesh"] for t in core.TARGETS] + [t["morph"] for t in core.TARGETS if t["morph"]] \
        + [f["mesh"] for f in core.FPP_TARGETS if f["mesh"]] + [core.FPP_APP, core.FPP_TORSO_MESH] \
        + [t["tex"] for t in core.TARGETS] + list(core.KNOWN_OTHER)
for p in paths:
    print("  ", "SHIPS " if rdar.fnv1a64(p) in hs else "  -   ", p)

for t in core.TARGETS + [f for f in core.FPP_TARGETS if f["mesh"]]:
    print("\n==", t["code"])
    try:
        mesh_json, morph_json = core.extract_mesh(cli, GAME, WORK, t, log)
        m = core.load(mesh_json)
        root = m["Data"]["RootChunk"]
        ents = root["materialEntries"]
        print("   entries:", len(ents), "localBuffer:", len((root.get("localMaterialBuffer") or {}).get("materials") or []),
              "preload:", len(root.get("preloadLocalMaterialInstances") or []), "external:", len(root.get("externalMaterials") or []))
        print("   appearances:", [a["Data"]["name"]["$value"] for a in root["appearances"]][:8])
        chunks = root["renderResourceBlob"]["Data"]["header"]["renderChunkInfos"]
        print("   chunks:", len(chunks), "vertices:", sum(c["numVertices"] for c in chunks))
        mesh, nmat, nvert = core.shell(m, r"inkflow\tattoos\x\x.xbm", None, t["code"])
        print("   SHELL OK:", nmat, "materials", nvert, "vertices")
        if morph_json:
            r2, n = core.retarget_morph(core.load(morph_json), t, r"inkflow\tattoos\x\x.mesh")
            print("   MORPH OK:", n, "targets")
    except Exception as e:
        print("   FAIL:", type(e).__name__, e)
print("\n== fpp torso mask:", core.fpp_torso_mask(cli, GAME, WORK, log))
