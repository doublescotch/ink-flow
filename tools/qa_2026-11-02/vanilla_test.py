"""Does the Ink Flow engine accept the BASE GAME meshes (no body mod at all)? Same code path as a player whose
archive\\pc\\mod holds no body archive: find_owner falls back to basegame_4_appearance.archive."""
import os, sys, json
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import core

GAME = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
CLI = os.path.join(os.environ["LOCALAPPDATA"], r"InkFlow\wolvenkit\9.1.0\WolvenKit.CLI.exe")
WORK = r"C:\__DEV\cyberpunk\ink_flow\gen\vanilla_test"
os.makedirs(WORK, exist_ok=True)

core.mod_dir = lambda game: os.path.join(WORK, "no_mod_dir_here")   # pretend archive\pc\mod is absent
log = lambda *a: print(" ".join(str(x) for x in a), flush=True)
cli = core.Cli(CLI, log)

for t in core.TARGETS + [f for f in core.FPP_TARGETS if f["mesh"]]:
    print("\n==", t["code"], t["mesh"])
    try:
        mesh_json, morph_json = core.extract_mesh(cli, GAME, WORK, t, log)
        m = core.load(mesh_json)
        root = m["Data"]["RootChunk"]
        ents = root["materialEntries"]
        print("   materialEntries:", len(ents), "local:", sum(e["isLocalInstance"] == 1 for e in ents),
              "names:", sorted({e["name"]["$value"] for e in ents})[:12])
        print("   appearances:", [a["Data"]["name"]["$value"] for a in root["appearances"]][:12])
        print("   localMaterialBuffer:", len((root.get("localMaterialBuffer") or {}).get("materials") or []),
              "preloadLocal:", len(root.get("preloadLocalMaterialInstances") or []),
              "external:", len(root.get("externalMaterials") or []))
        chunks = root["renderResourceBlob"]["Data"]["header"]["renderChunkInfos"]
        print("   chunks:", len(chunks), "vertices:", sum(c["numVertices"] for c in chunks))
        mesh, nmat, nvert = core.shell(m, r"inkflow\tattoos\x\x.xbm", None, t["code"])
        print("   SHELL OK:", nmat, "materials", nvert, "vertices")
        if morph_json:
            mo = core.load(morph_json)
            r2, n = core.retarget_morph(mo, t, r"inkflow\tattoos\x\x.mesh")
            print("   MORPH OK:", n, "targets")
    except Exception as e:
        print("   FAIL:", type(e).__name__, e)

print("\n== fpp torso mask")
try:
    print("  ", core.fpp_torso_mask(cli, GAME, WORK, log))
except Exception as e:
    print("   FAIL:", type(e).__name__, e)
