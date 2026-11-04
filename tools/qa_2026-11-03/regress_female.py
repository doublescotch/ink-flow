"""Non-regression of the male V change (ETUDE § 19, 2026-11-03) : the FEMALE tattoos of `3_Bodies\\__Tattoos` built
twice against the fake vanilla game tree of 2026-11-02 (`gen\\t101\\fakegame`), his settings, on a COPY of his
catalogue (his own is never written) : once with the engine of the last commit (`git show HEAD:...` into a temp
folder), once with the working tree. Both archives unbundled and compared file by file (SHA-256), plus the .xl.
Usage : regress_female.py [git ref of the old engine, default HEAD]"""
import hashlib, importlib, os, shutil, subprocess, sys

PROJ = r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow"
ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\m103"
FAKE = r"C:\__DEV\cyberpunk\ink_flow\gen\t101\fakegame"
FOLDER = r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\3_Bodies\__Tattoos"   # ex-__InkFlow (03/11)
CAT = ROOT + r"\catalogue_copy.json"
REF = sys.argv[1] if len(sys.argv) > 1 else "HEAD"

# engine of the last commit, next to its templates (core.templates_dir() = ../../templates)
old = ROOT + r"\head_src"
shutil.rmtree(old, ignore_errors=True)
for rel in ["builder/inkflow/" + f for f in ("__init__.py", "core.py", "env.py", "config.py", "rdar.py", "armconv.py")]:
    r = subprocess.run(["git", "-C", PROJ, "show", REF + ":" + rel], capture_output=True)
    if r.returncode:          # file absent at that ref (armconv.py before 1.4.0)
        continue
    dst = os.path.join(old, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "wb").write(r.stdout)
shutil.copytree(os.path.join(PROJ, "templates"), os.path.join(old, "templates"), dirs_exist_ok=True)


def build(builder, tag):
    for m in [m for m in sys.modules if m == "inkflow" or m.startswith("inkflow.")]:
        del sys.modules[m]
    sys.path.insert(0, builder)
    try:
        inkflow = importlib.import_module("inkflow")
        core, env = importlib.import_module("inkflow.core"), importlib.import_module("inkflow.env")
        cfg = importlib.import_module("inkflow.config").Config()
        if not os.path.isfile(CAT):
            shutil.copyfile(env.CATALOGUE_FILE, CAT)
        cat = core.Catalogue(CAT)
        files = [os.path.join(FOLDER, f) for f in sorted(os.listdir(FOLDER)) if f.lower().endswith(".archive")]
        entries = [e for e in core.scan_files(files) if e.supported and e.id not in set(cfg["unchecked"])
                   and all(t.get("gender", "f") == "f" for t in e.targets)]
        cli = env.find_wolvenkit(cfg["cli"])
        s = core.Settings(game=FAKE, cli=cli, work=r"C:\__DEV\cyberpunk\ink_flow\gen\t101\work", out=os.path.join(ROOT, "out_" + tag),
                          name=inkflow.MOD_NAME, slots=int(cfg["slots"]), slot_title=cfg["slot_title"],
                          max_name=int(cfg["max_name"]), alpha=float(cfg["alpha"]), mirror=bool(cfg["mirror"]), fpp=bool(cfg["fpp"]))
        print(f"[{tag}] {len(entries)} tattoos, slots={s.slots} mirror={s.mirror} fpp={s.fpp}", flush=True)
        res = core.run_build(s, entries, cat, lambda *a: None)
        print(f"[{tag}] {res.size} o, {len(res.listing)} files", flush=True)
        return res, cli
    finally:
        sys.path.remove(builder)


def tree(cli, arc, d):
    shutil.rmtree(d, ignore_errors=True)
    subprocess.run([cli, "unbundle", arc, "-o", d], capture_output=True, check=True)
    out = {}
    for r, _, fs in os.walk(d):
        for f in fs:
            p = os.path.join(r, f)
            out[os.path.relpath(p, d).lower()] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


ra, cli = build(os.path.join(old, "builder"), "head")
rb, _ = build(os.path.join(PROJ, "builder"), "new")
a, b = tree(cli, ra.archive, ROOT + r"\u_head"), tree(cli, rb.archive, ROOT + r"\u_new")
diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
print(f"\nHEAD {len(a)} files, NEW {len(b)} files, different or missing: {len(diff)}")
for k in diff[:20]:
    print("  ", k, "head" if k in a else "-", "new" if k in b else "-")
print("XL identical:", open(ra.xl, "rb").read() == open(rb.xl, "rb").read())
