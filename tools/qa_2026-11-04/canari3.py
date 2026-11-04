"""Canari 3 (2026-11-04, 21 h) : the texture header fault. Kala's `Kala Japanese V2` textures (VTK and UV) carry a header
that says « 4096 x 4096, 1 mip, 1 398 128 bytes » over a buffer holding the full 13-mip chain (22 369 648 bytes) ; the
engine copies the 4096 mip from a 1.4 MB buffer and crashes (ReportQueue 18 h 34 / 20 h 14 / 20 h 30 : read 1.44 MB past
the source). Two tattoos only (his rule) on his MINIMAL game (Solo bench + Ink Flow, 420 archives parked) :
  Kala Japanese V2 (UV, header faulty, copied byte for byte on Solo) + Samurai VTK (control, converted arms).
Run 1 = current engine : expected to crash at the mirror or on a save load (reproduction).
Run 2 = engine with the header check + re-import : expected clean.
Usage : canari3.py build | install        (install : game closed, his formula on archive\\pc\\mod)"""
import os, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import MOD_NAME, core, env
from inkflow.config import Config

GAME = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\uv104"
WORK, OUT = os.path.join(ROOT, "work_canari3"), os.path.join(ROOT, "out_canari3")
TATTOOS = [r"C:\__DEV\cyberpunk\ink_flow\dl\uv\tattoos\002_Tattoos_UV_Kala_Japanese_V2.archive",
           r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\3_Bodies\__Tattoos\002_Tattoos_VTK_Unknown_Samurai.archive"]
cfg = Config()
CLI = env.find_wolvenkit(cfg["cli"])
mode = sys.argv[1]


def log(*a):
    print(" ".join(str(x) for x in a), flush=True)


if mode == "build":
    cat = core.Catalogue(os.path.join(ROOT, "catalogue_game_copy.json"))
    entries = [e for e in core.scan_files(TATTOOS) if e.supported]
    cat.ensure(entries)
    s = core.Settings(game=GAME, cli=CLI, work=WORK, out=OUT, name=MOD_NAME, slots=2, slot_title=cfg["slot_title"],
                      max_name=int(cfg["max_name"]), alpha=1.0, mirror=True, fpp=True)
    res = core.run_build(s, entries, cat, log)
    log("archive:", res.archive, os.path.getsize(res.archive))

elif mode == "install":
    if core.game_running():
        sys.exit("Cyberpunk 2077 is running: close it first")

    class R:
        archive = os.path.join(OUT, "Ink_Flow.archive")
        xl = os.path.join(OUT, "Ink_Flow.archive.xl")
    assert os.path.isfile(R.archive) and os.path.isfile(R.xl), "build first"
    b = core.install(R, GAME, env.BACKUP_DIR, print)
    print("backup folder:", b)
else:
    sys.exit(__doc__)
