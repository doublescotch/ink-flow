"""QA corps vanilla (demande de Hell_Kaiser, 2026-11-02) : parquer Angel hors du jeu, bâtir Ink Flow 1.0.1 avec SA
configuration (ses archives, ses slots) sur le corps vanilla, installer. Une seule commande, jeu fermé.
Usage : python vanilla_in_game.py <game> <park dir>"""
import hashlib, os, shutil, sys, time
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import APP_NAME, MOD_NAME, VERSION, core, env
from inkflow.config import Config

game, park = sys.argv[1], sys.argv[2]
ANGEL = ["006_Angel_Body.archive", "006_Angel_Body.xl", "006_Angel_Body_Vanilla_Refits_xBaebsae.archive"]

if core.game_running():
    sys.exit("Cyberpunk 2077 is running: close it first")
mod = core.mod_dir(game)
os.makedirs(park, exist_ok=True)
for n in ANGEL:
    p = os.path.join(mod, n)
    if os.path.isfile(p):
        shutil.move(p, os.path.join(park, n))
        print("parked:", n, "->", park)
print("archive\\pc\\mod now:", sorted(os.listdir(mod)))

cfg = Config()                                   # his %LOCALAPPDATA%\InkFlow\config.json
cat = core.Catalogue(env.CATALOGUE_FILE)
files = [p for p in cfg["files"] if os.path.isfile(p)]
if len(sys.argv) > 3:                            # his archives moved : take this folder and remember it in his config
    folder = sys.argv[3]
    files = [os.path.join(folder, f) for f in sorted(os.listdir(folder)) if f.lower().endswith(".archive")]
    cfg["files"], cfg["last_dir"] = files, folder
    cfg.save()
    print(f"config files -> {len(files)} archives from {folder}")
entries = [e for e in core.scan_files(files) if e.supported and e.id not in set(cfg["unchecked"])]
cat.ensure(entries)
s = core.Settings(game=game, cli=env.find_wolvenkit(cfg["cli"]), work=env.WORK_DIR, out=env.OUT_DIR, name=MOD_NAME,
                  slots=int(cfg["slots"]), slot_title=cfg["slot_title"], max_name=int(cfg["max_name"]),
                  alpha=float(cfg["alpha"]), mirror=bool(cfg["mirror"]), fpp=bool(cfg["fpp"]))
print(f"settings: {len(entries)} tattoos, slots={s.slots} mirror={s.mirror} fpp={s.fpp} alpha={s.alpha} cli={s.cli}")

logf = open(env.LOG_FILE, "w", encoding="utf-8")
logf.write(f"{APP_NAME} {VERSION}  {time.strftime('%Y-%m-%d %H:%M:%S')}  (vanilla QA build, CLI script)\n"
           f"game: {game}\ncli: {s.cli}\nout: {s.out}\nsettings: slots={s.slots} mirror={s.mirror} fpp={s.fpp} alpha={s.alpha}\n"
           f"tattoos: {len(entries)}\n\n")


def log(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    logf.write(line + "\n")
    logf.flush()


res = core.run_build(s, entries, cat, log)
backup = core.install(res, game, env.BACKUP_DIR, log)
logf.close()
h = hashlib.sha256(open(res.archive, "rb").read()).hexdigest()
print(f"\nINSTALLED {os.path.basename(res.archive)} ({res.size} bytes, {len(res.listing)} files, SHA-256 {h[:16]}...)")
print("previous files moved to:", backup)
print("archive\\pc\\mod now:", sorted(os.listdir(mod)))
