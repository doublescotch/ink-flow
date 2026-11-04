"""Canari 2 (2026-11-04, after canari_swap proved the converted texture is the fault) : which part of the conversion ?
Minimal build on his game (Solo posed) with TWO tattoos only (his rule : only what is tested) : Samurai VTK + Unknown
Samurai UV. Then the Samurai VTK arm textures are replaced :
  arm L  <- V1 : the artist's UV texture content, pushed through OUR pipeline at 8K (WolvenKit export -> RGBA8 DDS ->
               import `--keep` on a copy of the VTK arm source) : tests the 8K import path with known-good content ;
  arm R  <- V2 : the real conversion of the VTK right arm, capped at 4K instead of 8K : tests the size.
Reading in game, Samurai VTK : left sleeve visible => the 8K import path is fine, the converted CONTENT is the fault ;
left sleeve absent => the 8K import path (or the --keep template) is the fault ; right sleeve visible => 8K is the fault.
Usage : canari2.py build | variants | install        (install : game closed, his unlock)"""
import glob, os, shutil, subprocess, sys
import numpy as np
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import MOD_NAME, armconv, core, env
from inkflow.config import Config

GAME = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
ROOT = r"C:\__DEV\cyberpunk\ink_flow\gen\uv104"
WORK, OUT = os.path.join(ROOT, "work_canari2"), os.path.join(ROOT, "out_canari2")
TATTOOS = [r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\3_Bodies\__Tattoos\002_Tattoos_VTK_Unknown_Samurai.archive",
           r"C:\__DEV\cyberpunk\ink_flow\dl\uv\tattoos\002_Tattoos_UV_Unknown_Samurai.archive"]
UV_DDS = os.path.join(os.environ["TEMP"], r"claude\d--OneDrive---NS2I-Serveurs\a4a06752-455f-4174-958c-186639a4eeda\scratchpad\diag\uv\unknown_samurai_2_uv_pwa.dds")
cfg = Config()
CLI = env.find_wolvenkit(cfg["cli"])
mode = sys.argv[1]


def log(*a):
    print(" ".join(str(x) for x in a), flush=True)


def run(*a, what=""):
    r = subprocess.run([CLI, *a], capture_output=True, text=True)
    ok = r.returncode == 0 and "Error" not in r.stdout
    log(f"  cli {what or a[0]}: {'OK' if ok else 'FAILED'}")
    if not ok:
        print(r.stdout[-1500:])
        sys.exit(1)


if mode == "build":
    cat = core.Catalogue(os.path.join(ROOT, "catalogue_game_copy.json"))
    entries = [e for e in core.scan_files(TATTOOS) if e.supported]
    cat.ensure(entries)
    s = core.Settings(game=GAME, cli=CLI, work=WORK, out=OUT, name=MOD_NAME, slots=2, slot_title=cfg["slot_title"],
                      max_name=int(cfg["max_name"]), alpha=1.0, mirror=True, fpp=True)
    res = core.run_build(s, entries, cat, log)
    log("archive:", res.archive, os.path.getsize(res.archive))

elif mode == "variants":
    # ORIENTATION canari (second design, after the out-of-game proof that the converted texture is pixel-exact in
    # image space) : BOTH arm textures of Samurai VTK <- the artist's UV texture with everything cleared except the
    # image-space TOP-LEFT quarter-strip (u < 0.22, v < 0.5 = the left arm's half as WolvenKit shows it), pushed
    # through our import path. Left sleeve on, right off => the game reads the image as WolvenKit shows it (then the
    # converted content itself is the fault). Right sleeve on, left off => the game reads the imported buffer upside
    # down relative to WolvenKit's picture : every converted texture is vertically flipped in game (a UV texture
    # hides it : its right arm is the vertical mirror of its left arm). Neither => still unexplained.
    pack = os.path.join(WORK, "pack", MOD_NAME, "inkflow", "tattoos", "unknown_samurai")
    tex_base = os.path.join(WORK, "tex", "unknown_samurai", "base")
    srcs = [p for p in glob.glob(tex_base + r"\**\*.xbm", recursive=True)]
    log("VTK Samurai source textures:", [os.path.relpath(p, tex_base) for p in srcs])
    arm_l_src = next(p for p in srcs if "arm" in os.path.basename(p).lower() and ("_l" in os.path.basename(p).lower() or "left" in os.path.basename(p).lower()))
    tmp = os.path.join(WORK, "canari2.tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    d1 = os.path.join(tmp, "v1")
    os.makedirs(d1)
    import struct
    data = bytearray(open(UV_DDS, "rb").read())
    h, w = struct.unpack_from("<II", data, 12)
    mips = struct.unpack_from("<I", data, 28)[0]
    off = 148
    for level in range(mips):
        lw, lh = max(1, w >> level), max(1, h >> level)
        keep_cols, keep_rows = max(1, int(armconv.STRIP_U * lw)), max(1, lh // 2)
        a = np.frombuffer(data, dtype=np.uint8, count=lw * lh * 4, offset=off).reshape(lh, lw, 4).copy()
        a[keep_rows:, :, :] = 0
        a[:, keep_cols:, :] = 0
        data[off:off + lw * lh * 4] = a.tobytes()
        off += lw * lh * 4
    open(os.path.join(d1, "arm_l.dds"), "wb").write(data)
    log(f"V1': UV texture {w}x{h}, {mips} mips, kept image-space top-left quarter-strip only")
    shutil.copyfile(arm_l_src, os.path.join(d1, "arm_l.xbm"))
    run("import", os.path.join(d1, "arm_l.dds"), "-o", d1, "--keep", what="import V1' (UV left half, 8K, our path)")
    v1 = os.path.join(d1, "arm_l.xbm")
    for name in ("unknown_samurai_arm_l_conv.xbm", "unknown_samurai_arm_r_conv.xbm"):
        dst = os.path.join(pack, name)
        assert os.path.isfile(dst), dst
        shutil.copyfile(v1, dst)
        log("  replaced", name, os.path.getsize(dst))
    arc = os.path.join(OUT, MOD_NAME + ".archive")
    os.remove(arc)
    run("pack", os.path.join(WORK, "pack", MOD_NAME), "-o", OUT, what="pack")
    log("canari 2:", arc, os.path.getsize(arc))

elif mode == "install":
    class R:
        archive = os.path.join(OUT, MOD_NAME + ".archive")
        xl = os.path.join(OUT, MOD_NAME + ".archive.xl")
    b = core.install(R, GAME, env.BACKUP_DIR, print)
    print("backup:", b)
