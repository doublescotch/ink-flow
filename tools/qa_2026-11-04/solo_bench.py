"""Solo 2.0 bench in Hell_Kaiser's REAL game (ETUDE § 23, his decision of 2026-11-04 18 h 35 : « UV on the native
framework body FIRST, then UV on VTK »). Unlock : WRITE_UNLOCK.txt on the game folder (his, 17 h 33) + « unlock ».
Usage : solo_bench.py park|build|install|restore|status
  park    : Angel (archive, .xl, vanilla refits) moved to `parked\\2026-11-04_angel\\` ; Solo OG 2.0 (archive + .xl) and
            Solo OG 2.0 Arms UV copied from `dl\\uv\\` into archive\\pc\\mod. UV Framework 3.2.1 is already his.
  build   : Ink Flow 1.4.0 on the game as it stands (Solo), his builder settings and tattoo list + the 16 UV archives of
            `dl\\uv\\tattoos\\`, catalogue = `gen\\uv104\\catalogue_game_copy.json` (his own is never written).
            Output `gen\\uv104\\out_solo_game\\`, log `log_solo_game.txt`. Nothing written to the game.
  install : `core.install` of that build (old Ink_Flow -> %LOCALAPPDATA%\\InkFlow\\backup\\<stamp>).
  restore : Solo files removed, Angel put back from the parked folder. Ink_Flow is NOT restored here (the builder's
            backup folder holds the Angel build of 16 h 16 : copy it back by hand or rebuild).
  status  : what is in archive\\pc\\mod for bodies, read only.
Refuses to write while the game is running. Every file written or removed is printed."""
import glob, os, shutil, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import MOD_NAME, core, env
from inkflow.config import Config

GAME = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
MOD = os.path.join(GAME, r"archive\pc\mod")
UV = r"C:\__DEV\cyberpunk\ink_flow\dl\uv"
ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\uv104"
PARK = r"C:\__DEV\cyberpunk\ink_flow\parked\2026-11-04_angel"
ANGEL = ["006_Angel_Body.archive", "006_Angel_Body.xl", "006_Angel_Body_Vanilla_Refits_xBaebsae.archive"]
SOLO = ["006_Solo_OG_2.0.archive", "006_Solo_OG_2.0.xl", "005_Solo_OG_2.0_Arms_UV.archive"]
FRAMEWORK = "011_UV_Framework_Texture_3.2.1.archive"
OUT = os.path.join(ROOT, "out_solo_game")
mode = sys.argv[1]


def status():
    for n in ANGEL + SOLO + [FRAMEWORK, "Ink_Flow.archive", "Ink_Flow.archive.xl"]:
        p = os.path.join(MOD, n)
        print(f"  {'IN ' if os.path.isfile(p) else '---'} {n}" + (f"  {os.path.getsize(p)}" if os.path.isfile(p) else ""))
    print("  parked:", sorted(os.listdir(PARK)) if os.path.isdir(PARK) else "(none)")


if mode == "status":
    status()
    sys.exit(0)
if mode in ("park", "install", "restore") and core.game_running():
    sys.exit("Cyberpunk 2077 is running: close it first")

if mode == "park":
    assert os.path.isfile(os.path.join(MOD, FRAMEWORK)), "UV Framework 3.2.1 missing in the game"
    os.makedirs(PARK, exist_ok=True)
    for n in ANGEL:
        p = os.path.join(MOD, n)
        if os.path.isfile(p):
            shutil.move(p, os.path.join(PARK, n))
            print("  parked ", n)
    for n in SOLO:
        dst = os.path.join(MOD, n)
        shutil.copy2(os.path.join(UV, n), dst)
        print("  posed  ", dst, os.path.getsize(dst))
    status()

elif mode == "restore":
    for n in SOLO:
        p = os.path.join(MOD, n)
        if os.path.isfile(p):
            os.remove(p)
            print("  removed", p)
    for n in ANGEL:
        src = os.path.join(PARK, n)
        if os.path.isfile(src):
            shutil.move(src, os.path.join(MOD, n))
            print("  restored", n)
    status()

elif mode == "build":
    cfg = Config()
    assert os.path.normcase(cfg["game"]) == os.path.normcase(GAME), cfg["game"]
    cat = core.Catalogue(os.path.join(ROOT, "catalogue_game_copy.json"))
    files = list(cfg["files"]) + sorted(glob.glob(UV + r"\tattoos\002_Tattoos_UV_*.archive"))
    unchecked = set(cfg["unchecked"])
    scanned = core.scan_files(files)
    entries = [e for e in scanned if e.supported and e.id not in unchecked]
    cat.ensure(entries)
    s = core.Settings(game=GAME, cli=env.find_wolvenkit(cfg["cli"]), work=os.path.join(ROOT, "work_solo_game"), out=OUT,
                      name=MOD_NAME, slots=int(cfg["slots"]), slot_title=cfg["slot_title"], max_name=int(cfg["max_name"]),
                      alpha=float(cfg["alpha"]), mirror=bool(cfg["mirror"]), fpp=bool(cfg["fpp"]))
    print(f"game={s.game}\n{len(entries)} tattoos, slots={s.slots} mirror={s.mirror} fpp={s.fpp}", flush=True)
    lines = []

    def log(*a):
        line = " ".join(str(x) for x in a)
        lines.append(line)
        print(line, flush=True)
    res = core.run_build(s, entries, cat, log)
    open(os.path.join(ROOT, "log_solo_game.txt"), "w", encoding="utf-8").write("\n".join(lines))
    print("archive:", res.archive, os.path.getsize(res.archive))
    print("conflicting archives in the game :", core.conflicting_archives(GAME, entries, exclude_names=(os.path.basename(res.archive),)))

elif mode == "install":
    class R:  # what core.install reads from a build result
        archive = os.path.join(OUT, "Ink_Flow.archive")
        xl = os.path.join(OUT, "Ink_Flow.archive.xl")
    assert os.path.isfile(R.archive) and os.path.isfile(R.xl), "build first"
    b = core.install(R, GAME, env.BACKUP_DIR, print)
    print("backup folder:", b)
    status()
