"""Canari « texture ou câblage ? » for the Solo bench (his QA 2026-11-04 : Samurai VTK = body OK, NO sleeves on Solo ;
Unknown Samurai UV = body + arms OK). Out of game everything is identical (headers, meshes, materials, customization,
bytes in the archive) : only the texture CONTENT differs. So : same build, the two textures swapped by name.
  Samurai (VTK)         : its two `_conv.xbm` now hold the bytes of the UV Samurai texture (8K, strip painted by the artist) ;
  Unknown Samurai (UV)  : its `_uv_pwa.xbm` now holds the bytes of the converted left arm texture (strip top only).
Expected if the converted texture is the fault : Samurai gets its sleeves ; Unknown Samurai loses body and right arm,
keeps the left sleeve. Expected if the fault is elsewhere : Samurai still bare ; Unknown Samurai body gone, left sleeve.
Output : gen\\uv104\\out_canari_swap\\Ink_Flow.archive (+ .xl). Nothing written to the game here (solo_bench-like install
by hand : core.install). Usage : canari_swap.py"""
import os, shutil, subprocess, sys
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import env
from inkflow.config import Config

ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\uv104"
SRC = os.path.join(ROOT, r"work_solo_game\pack\Ink_Flow")
WORK = os.path.join(ROOT, r"work_canari_swap\Ink_Flow")
OUT = os.path.join(ROOT, "out_canari_swap")
T = r"inkflow\tattoos"
CONV = [os.path.join(T, "unknown_samurai", "unknown_samurai_arm_l_conv.xbm"), os.path.join(T, "unknown_samurai", "unknown_samurai_arm_r_conv.xbm")]
UV = os.path.join(T, "unknown_samurai_2", "unknown_samurai_2_uv_pwa.xbm")
CLI = env.find_wolvenkit(Config()["cli"])

shutil.rmtree(os.path.dirname(WORK), ignore_errors=True)
shutil.copytree(SRC, WORK)
uv_bytes = open(os.path.join(SRC, UV), "rb").read()
conv_l_bytes = open(os.path.join(SRC, CONV[0]), "rb").read()
for rel in CONV:
    open(os.path.join(WORK, rel), "wb").write(uv_bytes)
    print("  swapped", rel, "<- UV texture", len(uv_bytes))
open(os.path.join(WORK, UV), "wb").write(conv_l_bytes)
print("  swapped", UV, "<- converted left arm texture", len(conv_l_bytes))
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
r = subprocess.run([CLI, "pack", WORK, "-o", OUT], capture_output=True, text=True)
print(r.stdout[-600:])
arc = os.path.join(OUT, "Ink_Flow.archive")
assert os.path.isfile(arc) and "Error" not in r.stdout, "pack failed"
shutil.copyfile(os.path.join(ROOT, r"out_solo_game\Ink_Flow.archive.xl"), arc + ".xl")
print("canari:", arc, os.path.getsize(arc))
