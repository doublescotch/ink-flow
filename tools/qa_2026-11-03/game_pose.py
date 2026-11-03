"""Male V QA in his game (ETUDE § 19, 2026-11-03, his go : « charge ce dont tu as besoin pour les tests vanilla /
gymfiend masc V », instance reset to stacks 1 and 2). Usage : game_pose.py check|vanilla|gymfiend|remove
  check    : which archive of his game ships the male meshes (read only) ;
  vanilla  : Ink_Flow (male build on the base game body, gen\\m103\\out_vanilla) into archive\\pc\\mod ;
  gymfiend : + Gymfiend VTK 1.4.3 (archive + .xl) + MV Head VTK, Ink_Flow replaced by gen\\m103\\out_gymfiend ;
  remove   : everything this script posed is taken out (Ink_Flow, Gymfiend, MV Head) ; his files are never touched.
Refuses to run while the game is running. Every file written or removed is printed."""
import os, shutil, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import core

GAME = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
MOD = os.path.join(GAME, r"archive\pc\mod")
M103 = r"C:\__DEV\cyberpunk\ink_flow\gen\m103"
DL = r"C:\__DEV\cyberpunk\ink_flow\dl"
GYM = [DL + r"\6423_vtk\archive\pc\mod\02_Gymfiend_[VTK]_v.1.4.3.archive",
       DL + r"\6423_vtk\archive\pc\mod\02_Gymfiend_[VTK]_v.1.4.3_AXL_BodyTag.xl",
       DL + r"\6423_head\archive\pc\mod\02_MV_Head_[VTK].archive"]
INK = ("Ink_Flow.archive", "Ink_Flow.archive.xl")
mode = sys.argv[1]

if mode == "check":
    for t in core.TARGETS:
        if t["gender"] == "m":
            print(f"{t['label']:8s}", core.who_ships([core.short_label(l) for l, _ in core.owners_of(GAME, t["mesh"])]))
    sys.exit(0)
if core.game_running():
    sys.exit("Cyberpunk 2077 is running: close it first")


def put(src, name=None):
    dst = os.path.join(MOD, name or os.path.basename(src))
    shutil.copy2(src, dst)
    print("  posed  ", dst, os.path.getsize(dst))


def take(name):
    p = os.path.join(MOD, name)
    if os.path.isfile(p):
        os.remove(p)
        print("  removed", p)


if mode in ("remove", "vanilla", "gymfiend"):
    for n in INK + tuple(os.path.basename(g) for g in GYM):
        take(n)
if mode == "vanilla":
    for n in INK:
        put(os.path.join(M103, "out_vanilla", n))
elif mode == "gymfiend":
    for g in GYM:
        put(g)
    for n in INK:
        put(os.path.join(M103, "out_gymfiend", n))
