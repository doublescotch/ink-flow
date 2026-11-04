"""Minimal bench in Hell_Kaiser's REAL game (his idea, 2026-11-04 20 h 30 : « seulement Ink Flow et le corps, on vire tout »)
to tell a texture defect from memory pressure : every entry of archive\\pc\\mod is moved out except the Solo bench
(Solo OG 2.0 + .xl, Solo arms UV, UV Framework 3.2.1) and Ink_Flow (.archive + .xl). r6, red4ext and CET are left as they
are (no texture there). Same volume, so a move is a rename : instant, nothing copied.
Usage : minimal_bench.py park_all | unpark_all | status   (game closed ; his formula on archive\\pc)
  park_all   : archive\\pc\\mod\\* -> archive\\pc\\mod__parked_2026-11-04\\ (the game never reads that folder)
  unpark_all : everything moved back ; refuses if a name already exists in mod (nothing overwritten)
  status     : what is in mod and in the parked folder, read only"""
import os, shutil, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import core

GAME = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
MOD = os.path.join(GAME, r"archive\pc\mod")
PARK = os.path.join(GAME, r"archive\pc\mod__parked_2026-11-04")
KEEP = {"006_Solo_OG_2.0.archive", "006_Solo_OG_2.0.xl", "005_Solo_OG_2.0_Arms_UV.archive",
        "011_UV_Framework_Texture_3.2.1.archive", "Ink_Flow.archive", "Ink_Flow.archive.xl"}
mode = sys.argv[1]


def status():
    mod = sorted(os.listdir(MOD))
    parked = sorted(os.listdir(PARK)) if os.path.isdir(PARK) else []
    print(f"  mod : {len(mod)} entries")
    for n in mod:
        print("    ", "KEEP" if n in KEEP else "    ", n)
    print(f"  parked : {len(parked)} entries in {PARK}")


if mode == "status":
    status()
    sys.exit(0)
if core.game_running():
    sys.exit("Cyberpunk 2077 is running: close it first")

if mode == "park_all":
    os.makedirs(PARK, exist_ok=True)
    moved = 0
    for n in sorted(os.listdir(MOD)):
        if n in KEEP:
            continue
        dst = os.path.join(PARK, n)
        if os.path.exists(dst):
            sys.exit(f"already in the parked folder, nothing moved further: {n}")
        shutil.move(os.path.join(MOD, n), dst)
        moved += 1
    print(f"  moved {moved} entries to {PARK}")
    status()

elif mode == "unpark_all":
    if not os.path.isdir(PARK):
        sys.exit("nothing parked")
    for n in sorted(os.listdir(PARK)):
        if os.path.exists(os.path.join(MOD, n)):
            sys.exit(f"already in mod, nothing moved: {n}")
    moved = 0
    for n in sorted(os.listdir(PARK)):
        shutil.move(os.path.join(PARK, n), os.path.join(MOD, n))
        moved += 1
    os.rmdir(PARK)
    print(f"  moved {moved} entries back to {MOD}")
    status()
else:
    sys.exit(__doc__)
