"""Pure vanilla build (body, arms, head from the base game) with HIS archives and settings, against the fake game tree
(empty archive\\pc\\mod) : nothing is written in his game. Output : gen\\t101\\outD_nofpp."""
import os
_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # Ink Flow project root
_DEPOT = os.environ.get("INKFLOW_DEPOT") or os.path.abspath(os.path.join(_ROOT, "..", "..", ".."))   # mods folder: three levels above the project, or INKFLOW_DEPOT
import os, sys, time
sys.path.insert(0, os.path.join(_ROOT, "builder"))
from inkflow import MOD_NAME, core, env
from inkflow.config import Config

FAKE = r"C:\__DEV\cyberpunk\ink_flow\gen\t101\fakegame"
OUT = r"C:\__DEV\cyberpunk\ink_flow\gen\t101\outD_nofpp"
FOLDER = os.path.join(_DEPOT, r"3_Bodies\__InkFlow")
cfg = Config()
cat = core.Catalogue(env.CATALOGUE_FILE)
files = [os.path.join(FOLDER, f) for f in sorted(os.listdir(FOLDER)) if f.lower().endswith(".archive")]
entries = [e for e in core.scan_files(files) if e.supported and e.id not in set(cfg["unchecked"])]
cat.ensure(entries)
s = core.Settings(game=FAKE, cli=env.find_wolvenkit(cfg["cli"]), work=r"C:\__DEV\cyberpunk\ink_flow\gen\t101\work", out=OUT,
                  name=MOD_NAME, slots=int(cfg["slots"]), slot_title=cfg["slot_title"], max_name=int(cfg["max_name"]),
                  alpha=float(cfg["alpha"]), mirror=bool(cfg["mirror"]), fpp=False)
print(f"settings: {len(entries)} tattoos, slots={s.slots} mirror={s.mirror} fpp={s.fpp}", flush=True)
log = lambda *a: print(" ".join(str(x) for x in a), flush=True)
res = core.run_build(s, entries, cat, log)
print("BUILT", res.archive, res.size, len(res.listing))
