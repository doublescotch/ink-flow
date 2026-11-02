"""Build Ink Flow avec SA configuration (%LOCALAPPDATA%\\InkFlow\\config.json : ses archives, ses slots) sur le jeu tel
qu'il est (Angel posé), puis installation. Usage :
  angel_build.py build     : bâtit dans %LOCALAPPDATA%\\InkFlow\\out (jeu ouvert ou fermé, rien d'écrit dans le jeu)
  angel_build.py install   : copie le résultat dans archive\\pc\\mod (jeu fermé), l'ancien part dans backup\\<horodatage>
Sœur de tools\\qa_2026-11-02\\vanilla_in_game.py, sans parquer Angel."""
import hashlib, os, sys, time
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import APP_NAME, MOD_NAME, VERSION, core, env
from inkflow.config import Config

GAME = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
step = sys.argv[1] if len(sys.argv) > 1 else "build"
cfg = Config()


def log(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    logf.write(line + "\n")
    logf.flush()


if step == "build":
    cat = core.Catalogue(env.CATALOGUE_FILE)
    files = [p for p in cfg["files"] if os.path.isfile(p)]
    entries = [e for e in core.scan_files(files) if e.supported and e.id not in set(cfg["unchecked"])]
    cat.ensure(entries)
    s = core.Settings(game=GAME, cli=env.find_wolvenkit(cfg["cli"]), work=env.WORK_DIR, out=env.OUT_DIR, name=MOD_NAME,
                      slots=int(cfg["slots"]), slot_title=cfg["slot_title"], max_name=int(cfg["max_name"]),
                      alpha=float(cfg["alpha"]), mirror=bool(cfg["mirror"]), fpp=bool(cfg["fpp"]))
    print(f"settings: {len(entries)} tattoos, slots={s.slots} mirror={s.mirror} fpp={s.fpp} alpha={s.alpha} cli={s.cli}")
    logf = open(env.LOG_FILE, "w", encoding="utf-8")
    logf.write(f"{APP_NAME} {VERSION}  {time.strftime('%Y-%m-%d %H:%M:%S')}  (angel_build.py, linkController test)\n"
               f"game: {GAME}\ncli: {s.cli}\nout: {s.out}\nsettings: slots={s.slots} mirror={s.mirror} fpp={s.fpp} alpha={s.alpha}\n"
               f"tattoos: {len(entries)}\n\n")
    t0 = time.time()
    res = core.run_build(s, entries, cat, log)
    logf.close()
    h = hashlib.sha256(open(res.archive, "rb").read()).hexdigest()
    print(f"\nBUILT {res.archive} ({res.size} bytes, {len(res.listing)} files, {time.time() - t0:.0f} s, SHA-256 {h[:16]}...)")
elif step == "install":
    if core.game_running():
        sys.exit("Cyberpunk 2077 is running: close it first")
    archive = os.path.join(env.OUT_DIR, MOD_NAME + ".archive")
    if not os.path.isfile(archive):
        sys.exit("nothing built: " + archive)
    logf = open(env.LOG_FILE, "a", encoding="utf-8")
    res = core.BuildResult(archive, archive + ".xl", [], [], 0.0, os.path.getsize(archive))
    backup = core.install(res, GAME, env.BACKUP_DIR, log)
    logf.close()
    print("installed ; previous files moved to:", backup)
    print("archive\\pc\\mod now:", sorted(os.listdir(core.mod_dir(GAME))))
else:
    sys.exit("unknown step")
