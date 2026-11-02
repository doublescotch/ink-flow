"""Steps in HIS game folder (unlock active, game closed). Usage :
  game_step.py isolate   : park the 4 VTK head archives next to Angel, move Ink_Flow.archive + .xl to the backup folder
  game_step.py install   : copy gen\\t101\\outC\\Ink_Flow.archive + .xl into archive\\pc\\mod (previous ones to backup)
  game_step.py restore   : put Angel + heads back from the park folder (Ink Flow left as is)"""
import os, shutil, sys, time
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import core, env

GAME = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
PARK = r"C:\__DEV\cyberpunk\ink_flow\parked\2026-11-02_angel"
OUTC = r"C:\__DEV\cyberpunk\ink_flow\gen\t101\outC"
HEADS = ["006_VTK_Vanilla_HD_Extra_Textures.archive", "006_VTK_Vanilla_HD_Head_Textures.archive",
         "006_VTK_Vanilla_HD_Head_xBaebsae.archive", "007_VTK_Vanilla_HD_Head.archive"]
INK = ["Ink_Flow.archive", "Ink_Flow.archive.xl"]
mod = core.mod_dir(GAME)
if core.game_running():
    sys.exit("Cyberpunk 2077 is running: close it first")
step = sys.argv[1]
stamp = os.path.join(env.BACKUP_DIR, time.strftime("%Y-%m-%d_%H%M%S"))


def move(name, dst_dir):
    p = os.path.join(mod, name)
    if os.path.isfile(p):
        os.makedirs(dst_dir, exist_ok=True)
        shutil.move(p, os.path.join(dst_dir, name))
        print("moved:", name, "->", dst_dir)


if step == "isolate":
    for n in HEADS:
        move(n, PARK)
    for n in INK:
        move(n, stamp)
elif step == "install":
    for n in INK:
        move(n, stamp)
    for n in INK:
        shutil.copy2(os.path.join(OUTC, n), os.path.join(mod, n))
        print("installed:", n, os.path.getsize(os.path.join(mod, n)), "bytes")
elif step in ("angelbuild", "embed", "nofpp", "fpparms", "fppbody"):
    # A/B at the mirror : the Ink Flow built last night ON ANGEL (QA validated), or one of today's variants
    src = {"angelbuild": os.path.join(env.BACKUP_DIR, r"2026-11-02_143536\archive\pc\mod"),
           "embed": r"C:\__DEV\cyberpunk\ink_flow\gen\t101\outE_embed",
           "nofpp": r"C:\__DEV\cyberpunk\ink_flow\gen\t101\outD_nofpp",
           "fpparms": r"C:\__DEV\cyberpunk\ink_flow\gen\t101\outF_fpparms",
           "fppbody": r"C:\__DEV\cyberpunk\ink_flow\gen\t101\outG_fppbody"}[step]
    for n in INK:
        move(n, stamp)
    for n in INK:
        shutil.copy2(os.path.join(src, n), os.path.join(mod, n))
        print("installed from", src, ":", n, os.path.getsize(os.path.join(mod, n)), "bytes")
elif step == "restore":
    for n in os.listdir(PARK):
        shutil.move(os.path.join(PARK, n), os.path.join(mod, n))
        print("restored:", n)
else:
    sys.exit("unknown step")
print("archive\\pc\\mod now:", sorted(os.listdir(mod)))
