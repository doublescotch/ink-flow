"""Bisect the FPP shells on the pure vanilla build : keep only the FPP arms (outF_fpparms) or only the FPP body
(outG_fppbody). Same archives, slots and catalogue as build_pure.py."""
import os, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import MOD_NAME, core, env
from inkflow.config import Config

which = sys.argv[1]
keep = {"fpparms": ("fpp_arm_l", "fpp_arm_r"), "fppbody": ("fpp_body",)}[which]
core.FPP_TARGETS[:] = [f for f in core.FPP_TARGETS if f["code"] in keep]
core.FPP_BY_PARENT.clear()
core.FPP_BY_PARENT.update({t["parent"]: t for t in core.FPP_TARGETS})
OUT = {"fpparms": r"C:\__DEV\cyberpunk\ink_flow\gen\t101\outF_fpparms", "fppbody": r"C:\__DEV\cyberpunk\ink_flow\gen\t101\outG_fppbody"}[which]
FAKE = r"C:\__DEV\cyberpunk\ink_flow\gen\t101\fakegame"
FOLDER = r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\3_Bodies\__InkFlow"
cfg = Config()
cat = core.Catalogue(env.CATALOGUE_FILE)
files = [os.path.join(FOLDER, f) for f in sorted(os.listdir(FOLDER)) if f.lower().endswith(".archive")]
entries = [e for e in core.scan_files(files) if e.supported and e.id not in set(cfg["unchecked"])]
cat.ensure(entries)
s = core.Settings(game=FAKE, cli=env.find_wolvenkit(cfg["cli"]), work=r"C:\__DEV\cyberpunk\ink_flow\gen\t101\work", out=OUT,
                  name=MOD_NAME, slots=int(cfg["slots"]), slot_title=cfg["slot_title"], max_name=int(cfg["max_name"]),
                  alpha=float(cfg["alpha"]), mirror=bool(cfg["mirror"]), fpp=True)
log = lambda *a: None
res = core.run_build(s, entries, cat, log)
print(which, "BUILT", res.archive, res.size, len(res.listing), f"{res.seconds:.0f}s", flush=True)
