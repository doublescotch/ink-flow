"""Ink Flow 1.3.0 built on Hell_Kaiser's REAL game (read only : nothing written to the game) with his builder settings and
tattoo list PLUS the 5 UV archives of `dl\\uv\\`, on a COPY of his catalogue. Output in `gen\\uv104\\out_game\\` ; install
by hand (or `core.install`) on his unlock. Usage : game_build.py"""
import glob, os, shutil, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import MOD_NAME, core, env
from inkflow.config import Config

ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\uv104"
UV = r"C:\__DEV\cyberpunk\ink_flow\dl\uv"
cfg = Config()
CAT = os.path.join(ROOT, "catalogue_game_copy.json")
if not os.path.isfile(CAT):
    shutil.copyfile(env.CATALOGUE_FILE, CAT)
cat = core.Catalogue(CAT)
files = list(cfg["files"]) + sorted(glob.glob(UV + r"\tattoos\002_Tattoos_UV_*.archive"))   # the 16 UV of V's Body.zip
unchecked = set(cfg["unchecked"])
scanned = core.scan_files(files)
for e in scanned:
    print(f"  {'+' if e.supported and e.id not in unchecked else '-'} {e.file:55s} {e.targets_label or e.ignored_reason}")
entries = [e for e in scanned if e.supported and e.id not in unchecked]
cat.ensure(entries)
s = core.Settings(game=cfg["game"], cli=env.find_wolvenkit(cfg["cli"]), work=os.path.join(ROOT, "work_game"), out=os.path.join(ROOT, "out_game"),
                  name=MOD_NAME, slots=int(cfg["slots"]), slot_title=cfg["slot_title"], max_name=int(cfg["max_name"]),
                  alpha=float(cfg["alpha"]), mirror=bool(cfg["mirror"]), fpp=bool(cfg["fpp"]))
print(f"game={s.game}\n{len(entries)} tattoos, slots={s.slots} mirror={s.mirror} fpp={s.fpp}", flush=True)
lines = []
def log(*a):
    line = " ".join(str(x) for x in a)
    lines.append(line)
    print(line, flush=True)
res = core.run_build(s, entries, cat, log)
open(os.path.join(ROOT, "log_game.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("conflicting archives in the game :", core.conflicting_archives(s.game, entries, exclude_names=(os.path.basename(res.archive),)))
