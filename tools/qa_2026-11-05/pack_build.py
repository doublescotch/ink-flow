"""Ink Flow 1.4.0 built on Hell_Kaiser's REAL game (read only : nothing written to the game) from his WHOLE up-to-date
tattoo folder `3_Bodies\\__Tattoos\\*.archive` (his remark of 2026-11-05, 0 h : « pas une ancienne liste des bancs, mon
pack à jour »), with his builder settings (slots, mirror, FPP, alpha) and a COPY of his catalogue. Output in
`gen\\uv104\\out_pack\\`, work cache `gen\\uv104\\work_game\\` (shared with the earlier game builds : textures already
extracted are reused). Install : `pack_build.py install` on his unlock, game closed.
Usage : pack_build.py build | install"""
import glob, os, shutil, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import MOD_NAME, core, env
from inkflow.config import Config

ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\uv104"
PACK = r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\3_Bodies\__Tattoos"
OUT = os.path.join(ROOT, "out_pack")
cfg = Config()
mode = sys.argv[1] if len(sys.argv) > 1 else "build"

if mode == "build":
    CAT = os.path.join(ROOT, "catalogue_game_copy.json")
    if not os.path.isfile(CAT):
        shutil.copyfile(env.CATALOGUE_FILE, CAT)
    cat = core.Catalogue(CAT)
    files = sorted(glob.glob(os.path.join(PACK, "*.archive")))
    scanned = core.scan_files(files)
    for e in scanned:
        print(f"  {'+' if e.supported else '-'} {e.file:60s} {e.targets_label or e.ignored_reason}", flush=True)
    entries = [e for e in scanned if e.supported]
    cat.ensure(entries)
    s = core.Settings(game=cfg["game"], cli=env.find_wolvenkit(cfg["cli"]), work=os.path.join(ROOT, "work_game"), out=OUT,
                      name=MOD_NAME, slots=int(cfg["slots"]), slot_title=cfg["slot_title"], max_name=int(cfg["max_name"]),
                      alpha=float(cfg["alpha"]), mirror=bool(cfg["mirror"]), fpp=bool(cfg["fpp"]))
    print(f"game={s.game}\n{len(files)} archives, {len(entries)} tattoos, slots={s.slots} mirror={s.mirror} fpp={s.fpp}", flush=True)
    lines = []

    def log(*a):
        line = " ".join(str(x) for x in a)
        lines.append(line)
        print(line, flush=True)

    res = core.run_build(s, entries, cat, log)
    open(os.path.join(ROOT, "log_pack.txt"), "w", encoding="utf-8").write("\n".join(lines))
    print("conflicting archives in the game :",
          core.conflicting_archives(s.game, entries, exclude_names=(os.path.basename(res.archive),)), flush=True)
    print("archive:", res.archive, os.path.getsize(res.archive), flush=True)

elif mode == "install":
    if core.game_running():
        sys.exit("Cyberpunk 2077 is running: close it first")

    class R:
        archive = os.path.join(OUT, "Ink_Flow.archive")
        xl = os.path.join(OUT, "Ink_Flow.archive.xl")
    assert os.path.isfile(R.archive) and os.path.isfile(R.xl), "build first"
    b = core.install(R, cfg["game"], env.BACKUP_DIR, print)
    print("backup folder:", b)
else:
    sys.exit(__doc__)
