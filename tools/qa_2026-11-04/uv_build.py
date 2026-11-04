"""UV support builds out of game (ETUDE § 21, 2026-11-04). Usage : uv_build.py solo|angel
  solo  : fake game tree whose archive\\pc\\mod holds UV Framework Texture 3.2.1 + Solo OG 2.0 (+ .xl) + Solo OG 2.0
          Arms UV (a UV body with UV arms) ;
  angel : fake game tree with 006_Angel_Body (+ .xl) : a VTK body with VTK arms, feet in the UV strip.
Tattoos : the 5 UV archives of `dl\\uv\\` (Bedellia Unrelated, Kala Japanese Sleeve 1 and V2, Pirate Venus, Garden
Bloom = body + head) + 2 VTK (Samurai = body + arms, Kala Japanese Arm Body). Catalogue = a copy (his own is never
written). Nothing is written to the game : the fake trees junction the base game's `archive\\pc\\content` (read only).
Expected : solo = every UV target built, VTK arms skipped ; angel = UV arms skipped, Angel feet masked, VTK whole."""
import glob, os, shutil, subprocess, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import MOD_NAME, core, env
from inkflow.config import Config

mode = sys.argv[1]
ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\uv104"
CONTENT = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077\archive\pc\content"
UV = r"C:\__DEV\cyberpunk\ink_flow\dl\uv"
SRC = r"C:\__DEV\cyberpunk\ink_flow\src"
BODY = {"solo": [UV + r"\011_UV_Framework_Texture_3.2.1.archive", UV + r"\006_Solo_OG_2.0.archive", UV + r"\006_Solo_OG_2.0.xl",
                 UV + r"\005_Solo_OG_2.0_Arms_UV.archive"],
        "angel": [SRC + r"\006_Angel_Body.archive", SRC + r"\006_Angel_Body.xl"],
        # 1.4.0 (ETUDE § 22) : Angel with the UV Framework loaded behind it, as in his game : UV arms converted
        "angelfw": [SRC + r"\006_Angel_Body.archive", SRC + r"\006_Angel_Body.xl", UV + r"\011_UV_Framework_Texture_3.2.1.archive"]}

game = os.path.join(ROOT, "game_" + mode)
if not os.path.isdir(game):
    os.makedirs(os.path.join(game, r"archive\pc\mod"))
    os.makedirs(os.path.join(game, r"bin\x64"))
    open(os.path.join(game, r"bin\x64\Cyberpunk2077.exe"), "w").close()
    subprocess.run(["cmd", "/c", "mklink", "/J", os.path.join(game, r"archive\pc\content"), CONTENT], check=True, capture_output=True)
    for a in BODY[mode]:
        shutil.copy2(a, os.path.join(game, r"archive\pc\mod", os.path.basename(a)))

files = sorted(glob.glob(UV + r"\002_Tattoos_UV_*.archive")) + [SRC + r"\002_Tattoos_VTK_Samurai.archive", SRC + r"\002_Tattoos_VTK_Kala_Japanese_Arm_Body.archive"]
cfg = Config()
cat = core.Catalogue(os.path.join(ROOT, "catalogue_copy.json"))
scanned = core.scan_files(files)
for e in scanned:
    print(f"  {'+' if e.supported else '-'} {e.file:55s} {e.targets_label or e.ignored_reason}")
entries = [e for e in scanned if e.supported]
cat.ensure(entries)
s = core.Settings(game=game, cli=env.find_wolvenkit(cfg["cli"]), work=os.path.join(ROOT, "work_" + mode), out=os.path.join(ROOT, "out_" + mode),
                  name=MOD_NAME, slots=2, slot_title="Ink {n}", max_name=20, alpha=1.0, mirror=True, fpp=True)
print(f"{mode}: {len(entries)} tattoos, slots={s.slots} fpp={s.fpp}", flush=True)
lines = []
def log(*a):
    line = " ".join(str(x) for x in a)
    lines.append(line)
    print(line, flush=True)
res = core.run_build(s, entries, cat, log)
open(os.path.join(ROOT, f"log_{mode}.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("\nXL:\n" + open(res.xl, encoding="utf-8").read())
