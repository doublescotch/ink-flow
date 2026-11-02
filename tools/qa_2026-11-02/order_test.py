"""Load-order resolution of core 1.0.1 on a fake game tree : legacy archive\\pc\\mod with modlist.txt, REDmod folder
with MO_REDmod_load_order.txt, base game fallback, pure tattoo detection, conflicts labels."""
import os, shutil, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import core, rdar

T = r"C:\__DEV\cyberpunk\ink_flow\gen\t101"
G = os.path.join(T, "fakegameB")
EBBRB = r"C:\__DEV\cyberpunk\ink_flow\dl\4654\ebbrb\archive\pc\mod\05_Hyst_Refit_ForcedBigBreastsBooty.archive"
TAT = r"C:\__DEV\cyberpunk\ink_flow\in\002_Tattoos_VTK_Unknown_Samurai.archive"
TAT2 = r"C:\__DEV\cyberpunk\ink_flow\in\002_Tattoos_VTK_Kala_Japanese_Arm_Left.archive"
BODY = core.TARGET_BY_CODE["body"]["mesh"]

shutil.rmtree(G, ignore_errors=True)
mod = os.path.join(G, r"archive\pc\mod")
os.makedirs(mod)
os.makedirs(os.path.join(G, r"bin\x64"))
open(os.path.join(G, r"bin\x64\Cyberpunk2077.exe"), "wb").close()
# the base game archive is only needed as a path (no extraction here)
os.makedirs(os.path.join(G, r"archive\pc\content"))
open(os.path.join(G, r"archive\pc\content\basegame_4_appearance.archive"), "wb").close()

def link(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)

def body_owner():
    src, owners = core.find_owner(G, BODY)
    return core.who_ships(owners), os.path.relpath(src, G)

print("A. empty mod folder, no REDmod       ->", body_owner())

link(TAT, os.path.join(mod, "zz_samurai.archive"))
link(TAT2, os.path.join(mod, "aa_kala_arm.archive"))
print("B. two tattoo archives, alphabetical ->", [l for l, _ in core.game_archives(G)])
with open(os.path.join(mod, "modlist.txt"), "w") as f:
    f.write("# MO2 order\nzz_samurai.archive\n")
print("C. modlist.txt puts zz first         ->", [l for l, _ in core.game_archives(G)])
print("   tattoos found                     ->", [l for l, _ in core.find_tattoo_archives(G)])
print("   body still                        ->", body_owner())

rm = os.path.join(G, r"mods\HystEBBRB\archives")
link(EBBRB, os.path.join(rm, "05_Hyst_Refit_ForcedBigBreastsBooty.archive"))
rm2 = os.path.join(G, r"mods\AAA_other\archives")
link(TAT, os.path.join(rm2, "samurai_redmod.archive"))
print("D. REDmod EBBRB + AAA_other          ->", body_owner())
print("   order                             ->", [l for l, _ in core.game_archives(G)])
os.makedirs(os.path.join(G, r"r6\cache\modded"))
with open(os.path.join(G, r"r6\cache\modded\MO_REDmod_load_order.txt"), "w") as f:
    f.write("HystEBBRB\nAAA_other\n")
print("E. MO_REDmod_load_order HystEBBRB 1st->", [l for l, _ in core.game_archives(G)][-2:])

link(EBBRB, os.path.join(mod, "006_Angel_Like_Legacy.archive"))
print("F. legacy body too                   ->", body_owner())
print("   active_owners                     ->", {c: w for c, (w, _) in core.active_owners(G, ["body", "arm_l", "head"]).items()})

class E:  # minimal stand-in for an Entry
    def __init__(self, p): self.path, self.id = p, rdar.content_id(p)
print("G. conflicts (selected = samurai)    ->", core.conflicting_archives(G, [E(TAT)], exclude_names=("Ink_Flow.archive",)))
print("   is_pure EBBRB / samurai           ->", core.is_pure_tattoo(EBBRB), core.is_pure_tattoo(TAT))
print("H. index cache entries               ->", len(rdar._INDEX))
