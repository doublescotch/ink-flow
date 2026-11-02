"""Sonde InkFlow_Probe : pose / retrait dans SON jeu, collecte des journaux. Jeu fermé, déverrouillage actif.
Usage :
  pose_probe.py check    : état (Redscript posé ? sonde posée ? journaux présents ?), n'écrit rien
  pose_probe.py pose     : extrait Redscript 0.5.32 (zip de 1_Core\\__WOLVENKIT) si absent, copie la sonde dans r6\\scripts
  pose_probe.py remove   : retire r6\\scripts\\InkFlow_Probe (Redscript reste en place)
  pose_probe.py logs     : copie dans logs\\<horodatage>\\ tout journal qui cite InkFlowProbe + redscript_rCURRENT.log
Chemins en dur du poste (même convention que tools\\qa_2026-11-02\\game_step.py)."""
import os, shutil, subprocess, sys, time, zipfile

GAME = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
ZIP = r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\1_Core\__WOLVENKIT\Red Script-1511-0-5-32-1792693776.zip"
HERE = os.path.dirname(os.path.abspath(__file__))
PROBE_SRC = os.path.join(HERE, "InkFlow_Probe", "InkFlow_Probe.reds")
PROBE_DST_DIR = os.path.join(GAME, "r6", "scripts", "InkFlow_Probe")
REDSCRIPT_FILES = ["engine/config/base/scripts.ini", "engine/tools/scc.exe", "engine/tools/scc_lib.dll",
                   "r6/config/cybercmd/scc.toml"]
# ModLog écrit dans le journal du jeu, que CET recopie dans bin\x64\plugins\cyber_engine_tweaks\gamelog.log (mesuré le 02/11).
LOG_DIRS = [os.path.join(GAME, "r6", "logs"), os.path.join(GAME, "red4ext", "logs"),
            os.path.join(GAME, "red4ext", "plugins", "Codeware"), os.path.join(GAME, "r6", "cache", "modded"),
            os.path.join(GAME, "bin", "x64", "plugins", "cyber_engine_tweaks")]


def game_running():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Cyberpunk2077.exe"], capture_output=True, text=True).stdout
    return "Cyberpunk2077.exe" in out


def check():
    print("game   :", GAME)
    for rel in REDSCRIPT_FILES:
        p = os.path.join(GAME, *rel.split("/"))
        print(("  ok   " if os.path.isfile(p) else "  MISSING ") + rel)
    for odd in ("engine/tools/scc", "engine/tools/libscc_lib.dylib"):
        p = os.path.join(GAME, *odd.split("/"))
        if os.path.exists(p):
            print("  note : fichier macOS présent, inutile sous Windows :", odd)
    print("probe  :", "posée" if os.path.isfile(os.path.join(PROBE_DST_DIR, "InkFlow_Probe.reds")) else "absente",
          "->", PROBE_DST_DIR)
    scripts = os.path.join(GAME, "r6", "scripts")
    if os.path.isdir(scripts):
        print("r6\\scripts :", sorted(os.listdir(scripts)))
    else:
        print("r6\\scripts : absent")
    for d in LOG_DIRS:
        if os.path.isdir(d):
            for n in sorted(os.listdir(d)):
                if n.lower().endswith(".log"):
                    print("  log  :", os.path.join(d, n), os.path.getsize(os.path.join(d, n)), "o")


def pose():
    if game_running():
        sys.exit("Cyberpunk 2077 is running: close it first")
    with zipfile.ZipFile(ZIP) as z:
        for rel in REDSCRIPT_FILES:
            dst = os.path.join(GAME, *rel.split("/"))
            if os.path.isfile(dst):
                print("kept   :", rel)
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with z.open(rel) as src, open(dst, "wb") as out:
                shutil.copyfileobj(src, out)
            print("posed  :", rel, os.path.getsize(dst), "o")
    os.makedirs(PROBE_DST_DIR, exist_ok=True)
    dst = os.path.join(PROBE_DST_DIR, "InkFlow_Probe.reds")
    shutil.copy2(PROBE_SRC, dst)
    print("posed  :", dst, os.path.getsize(dst), "o")


def remove():
    if game_running():
        sys.exit("Cyberpunk 2077 is running: close it first")
    if os.path.isdir(PROBE_DST_DIR):
        shutil.rmtree(PROBE_DST_DIR)
        print("removed:", PROBE_DST_DIR)
    else:
        print("absent :", PROBE_DST_DIR)


def logs():
    out = os.path.join(HERE, "logs", time.strftime("%Y-%m-%d_%H%M%S"))
    os.makedirs(out, exist_ok=True)
    n = 0
    for d in LOG_DIRS:
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            p = os.path.join(d, name)
            if not (os.path.isfile(p) and name.lower().endswith(".log")):
                continue
            keep = name.startswith("redscript") or name.startswith("InkFlowProbe")
            if not keep:
                try:
                    with open(p, "rb") as f:
                        keep = b"InkFlowProbe" in f.read()
                except OSError:
                    keep = False
            if keep:
                shutil.copy2(p, os.path.join(out, name))
                n += 1
                print("copied :", p)
    print("logs   :", out, "(", n, "fichiers )")


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "check"
    {"check": check, "pose": pose, "remove": remove, "logs": logs}[step]()
