"""Canari v4 « etats des pieds » (2026-11-05, ETUDE § 28) : same two tattoos as canari v3 (Samurai VTK + Bedellia body)
on his CURRENT game (vanilla body). New in v4 : third-person body shell = chunks 0-4 (the game's body option), lifted-legs
shell (the body morphtarget, chunks 5-7, named like the game's body) listed in `character_creation` + `lifted_feet`,
flat-legs shell listed in `flat_feet` only ; first person unchanged. Output in out_canari_feet (v3 kept in out_canari_fpp).
  build | check | install  (same as canari_fpp.py)
Expected in game : creator / apartment mirror : shins clean from the front (lifted feet), no moving holes ; in game
(photo, inventory, FPP) unchanged from v3 ; with shoes : to look at."""
import glob, json, os, re, subprocess, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import MOD_NAME, core, env
from inkflow.config import Config

GAME = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\uv104"
WORK, OUT = os.path.join(ROOT, "work_canari_fpp"), os.path.join(ROOT, "out_canari_feet")
TATTOOS = [r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\3_Bodies\__Tattoos\002_Tattoos_VTK_Unknown_Samurai.archive",
           # run 2 (15 h 40) : Bedellia body added for the first-person torso (the Samurai texture has no chest ink, his
           # QA of 15 h 30) ; the lower-legs fix (§ 27 bis : chunks 6-7 hidden, flat-foot legs shell) is in this run too.
           r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\3_Bodies\__Tattoos\002_Tattoos_VTK_Bedellia_Unrelated_Body.archive"]
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
    rx = r"(_slot1\.app|_slot1_legs\.app|_slot1_legs_up\.app|_slot1_fpp\.app|_slot1_fpp_legs\.app|_slot1_fpp_torso\.app|\.inkcharcustomization)$"
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
                opts = [o['$value'] for o in g['options']]
                legs = [o for o in opts if o.endswith(('_legs', '_legs_up'))]
                log(f"  GROUP {g['name']['$value']}: {len(opts)} options, legs shells {legs}")

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
