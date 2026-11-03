"""Male V build out of game (ETUDE § 19, 2026-11-03). Usage : male_build.py vanilla|gymfiend|mixed
  vanilla  : fake game tree with no mod (body, arms, head = base game), male tattoos only ;
  gymfiend : fake game tree whose archive\\pc\\mod holds Gymfiend VTK 1.4.3 + MV Head VTK, male tattoos only ;
  mixed    : the gymfiend tree + the female VTK tattoos of `__Tattoos` too (both customizations in one build).
Male tattoos : Kala Japanese Faded MV (Nexus 7414, 5 archives), the Gymfiend vanilla tattoo overlays (6423, 8), and
`__Tattoos\\002_Tattoos_Masc_V_VTK_Kala_Japanese_V2`. Catalogue = a copy (his own is never written). Nothing is written
to the game : the fake trees junction the base game's `archive\\pc\\content` (read only)."""
import glob, os, shutil, subprocess, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import MOD_NAME, core, env
from inkflow.config import Config

mode = sys.argv[1]
ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\m103"
CONTENT = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077\archive\pc\content"
DL = r"C:\__DEV\cyberpunk\ink_flow\dl"
TATTOOS = r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\3_Bodies\__Tattoos"
BODY = {"vanilla": [], "gymfiend": [DL + r"\6423_vtk\archive\pc\mod\02_Gymfiend_[VTK]_v.1.4.3.archive",
                                    DL + r"\6423_head\archive\pc\mod\02_MV_Head_[VTK].archive"]}
BODY["mixed"] = BODY["gymfiend"]

game = os.path.join(ROOT, "game_" + ("vanilla" if mode == "vanilla" else "gymfiend"))
if not os.path.isdir(game):
    os.makedirs(os.path.join(game, r"archive\pc\mod"))
    os.makedirs(os.path.join(game, r"bin\x64"))
    open(os.path.join(game, r"bin\x64\Cyberpunk2077.exe"), "w").close()
    subprocess.run(["cmd", "/c", "mklink", "/J", os.path.join(game, r"archive\pc\content"), CONTENT], check=True, capture_output=True)
    for a in BODY[mode]:
        shutil.copy2(a, os.path.join(game, r"archive\pc\mod", os.path.basename(a)))

# Tattoo set (his instruction, 03/11 19 h) : only his `002_Tattoos_Masc_V_*` (confirmed for male V ; the UV ones are
# ignored by the builder) + the female VTK of `__Tattoos` ; no Kala Faded, no Gymfiend vanilla overlays. The canary
# (`gen\m103\canari\arc`, Kala V2 re-encoded by hand) proved the fix and is no longer built : the engine re-encodes.
files = [os.path.join(TATTOOS, f) for f in os.listdir(TATTOOS) if f.startswith("002_Tattoos_Masc_V_")]
files += [os.path.join(TATTOOS, f) for f in os.listdir(TATTOOS) if "_VTK_" in f and "Masc_V" not in f]
cfg = Config()
cat = core.Catalogue(os.path.join(ROOT, "catalogue_copy.json"))
scanned = core.scan_files(files)
for e in scanned:
    print(f"  {'+' if e.supported else '-'} {e.file:70s} {', '.join(e.target_codes) or e.ignored_reason}")
entries = [e for e in scanned if e.supported]
cat.ensure(entries)
s = core.Settings(game=game, cli=env.find_wolvenkit(cfg["cli"]), work=os.path.join(ROOT, "work"), out=os.path.join(ROOT, "out_" + mode),
                  name=MOD_NAME, slots=int(cfg["slots"]), slot_title=cfg["slot_title"], max_name=int(cfg["max_name"]),
                  alpha=float(cfg["alpha"]), mirror=bool(cfg["mirror"]), fpp=bool(cfg["fpp"]))
print(f"{mode}: {len(entries)} tattoos, slots={s.slots} mirror={s.mirror} fpp={s.fpp}", flush=True)
res = core.run_build(s, entries, cat, lambda *a: print(" ".join(str(x) for x in a), flush=True))
print("\nXL:\n" + open(res.xl, encoding="utf-8").read())
