"""Canari FPP (2026-11-05) : the first-person body fix (ETUDE § 26). One tattoo only (his rule) on his CURRENT game (vanilla
body, Load Begone + Ink Flow 1.1 Samurai) : Samurai VTK, 2 slots, mirror, first person. Same setup as the build he saw
the fault on (« FPP tete baissee = manches, rien sur le corps »), so the fix is judged by the same look.
  build   : builds into gen\\uv104\\out_canari_fpp (work cache work_canari_fpp), nothing written to the game
  check   : unbundles the built archive and prints the first-person torso shell (mask, mesh, materials), the legs shell
            and the follower switcher (uiSlots), from the serialised JSON ; read only
  install : installs into the game (game closed, his unlock on archive\\pc\\mod)
Expected in game : tete baissee hors miroir, torse tatoue (chunks 0-4 : torse et cuisses) + mollets (chunks 5-7) ;
bras FPP inchanges ; createur, miroir, mode photo inchanges."""
import glob, json, os, re, subprocess, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import MOD_NAME, core, env
from inkflow.config import Config

GAME = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\uv104"
WORK, OUT = os.path.join(ROOT, "work_canari_fpp"), os.path.join(ROOT, "out_canari_fpp")
TATTOOS = [r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\3_Bodies\__Tattoos\002_Tattoos_VTK_Unknown_Samurai.archive"]
cfg = Config()
CLI = env.find_wolvenkit(cfg["cli"])
mode = sys.argv[1] if len(sys.argv) > 1 else "build"


def log(*a):
    print(" ".join(str(x) for x in a), flush=True)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


if mode == "build":
    cat = core.Catalogue(os.path.join(ROOT, "catalogue_game_copy.json"))
    entries = [e for e in core.scan_files(TATTOOS) if e.supported]
    cat.ensure(entries)
    s = core.Settings(game=GAME, cli=CLI, work=WORK, out=OUT, name=MOD_NAME, slots=2, slot_title=cfg["slot_title"],
                      max_name=int(cfg["max_name"]), alpha=1.0, mirror=True, fpp=True)
    res = core.run_build(s, entries, cat, log)
    log("archive:", res.archive, os.path.getsize(res.archive))

elif mode == "check":
    arc = os.path.join(OUT, MOD_NAME + ".archive")
    v = os.path.join(OUT, "verify")
    if os.path.isdir(v):
        import shutil
        shutil.rmtree(v)
    rx = r"(_fpp_torso\.(mesh|app)|_slot1_fpp\.app|_fpp_arm_l\.mesh|_slot1\.app|\.inkcharcustomization)$"
    subprocess.run([CLI, "unbundle", arc, "-o", v, "-r", rx], check=True, capture_output=True)
    subprocess.run([CLI, "convert", "serialize", os.path.join(v, "inkflow")], check=True, capture_output=True)
    files = sorted(glob.glob(os.path.join(v, "**", "*.json"), recursive=True))
    log("files serialised:", len(files))
    for p in files:
        rel = os.path.relpath(p, v)
        j = load(p)["Data"]["RootChunk"]
        if rel.endswith(".app.json"):
            for a in j["appearances"]:
                d = a["Data"]
                for c in d["components"]:
                    mesh = ((c.get("mesh") or {}).get("DepotPath") or {}).get("$value") or ""
                    log(f"  APP {rel}: {d['name']['$value']} | {c['$type']} {c['name']['$value']} | {mesh} | mask {c.get('chunkMask')}")
        elif rel.endswith(".mesh.json"):
            mats = j["localMaterialBuffer"]["materials"]
            texs = {((val.get("DiffuseTexture") or {}).get("DepotPath") or {}).get("$value") for m in mats for val in m["values"] if "DiffuseTexture" in val}
            chunks = j["renderResourceBlob"]["Data"]["header"]["renderChunkInfos"]
            log(f"  MESH {rel}: {len(chunks)} chunks, {sum(c['numVertices'] for c in chunks)} vertices, {len(mats)} decal materials -> {texs}, "
                f"preload {len(j.get('preloadLocalMaterialInstances') or [])}, base {mats[0]['baseMaterial']['DepotPath']['$value'].split(chr(92))[-1]}")
        elif rel.endswith(".inkcharcustomization.json"):
            for h in j["bodyCustomizationOptions"]:
                d = h["Data"]
                if d["$type"] == "gameuiSwitcherInfo":
                    log(f"  SWITCHER {d['name']['$value']} index {d['index']} link {d['link']['$value']} ctrl {d.get('linkController')} "
                        f"uiSlots {[u['$value'] for u in d['uiSlots']]} options {[[n['$value'] for n in o['names']] for o in d['options']]}")
            for g in j["bodyGroups"]:
                log(f"  GROUP {g['name']['$value']}: {len(g['options'])} -> {[o['$value'] for o in g['options'] if 'fpp' in o['$value']][:6]}")

elif mode == "install":
    if core.game_running():
        sys.exit("Cyberpunk 2077 is running: close it first")

    class R:
        archive = os.path.join(OUT, MOD_NAME + ".archive")
        xl = os.path.join(OUT, MOD_NAME + ".archive.xl")
    assert os.path.isfile(R.archive) and os.path.isfile(R.xl), "build first"
    b = core.install(R, GAME, env.BACKUP_DIR, print)
    print("backup folder:", b)
else:
    sys.exit(__doc__)
