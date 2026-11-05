"""Ink Flow engine (v0.4, 2026-11-01 ; 1.0.1, 2026-11-02) : the generator of `tools/inkflow_build.py` v0.3 turned into a library.

Same recipe, same output (ETUDE § 8-13) :
  - every tattoo .archive chosen by the player is indexed (RDAR, no WolvenKit) and its TARGETS recognised by the files
    it replaces (body `v_overlay.xbm`, arms `femme_arm_left|right_01_overlay.xbm`, head `h0_001_pwa_c__basehead_overlay.xbm`) ;
  - for every target the ACTIVE mesh of the player (first archive in the game's load order that ships it : `archive\\pc\\mod`
    with `modlist.txt` if present, then REDmod `mods\\*\\archives`, else the base game ; `game_archives`) is extracted
    and serialised with WolvenKit CLI (cached) ;
  - per tattoo and target : the texture copied byte for byte, a shell = COPY OF THE ACTIVE MESH whose skin materials
    become the vanilla tattoo decal material, the mesh morphtarget (body, head) re-pointed to the shell, one .app per
    (slot, tattoo, target) ;
  - N switchers (route 2, Heterochromia pattern : one option drives one uiSlot per target), options Off + one per
    tattoo ; route 1 (an option in the vanilla « Body Tattoos » switcher) is off by default ;
  - first person (default on) : per slot a hidden follower switcher linked to the slot's switcher (vanilla
    `fpp_body_tattoo` -> `body_tattoo` pattern) drives FPP shells : a copy of the active FPP torso mesh through the
    mask of the FPP torso appearance, the body shell again through the mask of the FPP legs appearance, and copies of
    the active FPP arm meshes ; listed in the `FPP_Body` group only ;
  - names shown in game come from the Catalogue (player-editable `name`, immutable `slug`) ;
  - nothing is written to the game by the engine ; `install()` does it on demand.

Differences with the v0.3 script : no `sys.exit` (BuildError), no `print` (log callback), templates resolved from the
PyInstaller bundle when frozen, catalogue keyed by CONTENT id (SHA-256) so a renamed file keeps its slug and the
player's saved character keeps its tattoos.
"""
import base64
import copy
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import time
from dataclasses import dataclass, field

from . import armconv, rdar

P = "inkflow"                                   # path prefix of everything the mod ships
MESH_APPEARANCE = "01_ca_pale"
BODY_DIR = r"base\characters\common\player_base_bodies\player_female_average"
BASEGAME = r"archive\pc\content\basegame_4_appearance.archive"
DECAL_MI = (r"base\characters\common\skin\character_mat_instance\__parameters\customization__parameters"
            r"\tattoos__parameters\customization_tattoos_01_ca_pale.mi")
ARMS_TEX = r"base\characters\player\femme\body\arms\textures"
HEAD_DIR = r"base\characters\head\player_base_heads\player_female_average"
FPP_DIR = BODY_DIR + r"\fpp"
FPP_TORSO_MESH = FPP_DIR + r"\t0_000_pwa_fpp__torso.mesh"
# What female V sees of her body in first person (ETUDE § 16, § 26 ; measured 2026-11-05 in the base game, Angel and the
# probe logs) : the FPP torso mesh (same chunk layout as the full body mesh, 8 chunks head to feet) drawn by TWO
# appearances with complementary masks. The torso app shows chunks 0-4 (torso and thighs, 0.51-1.53 m) ; the legs app
# shows chunks 5-7 (calves and feet, 0.01-0.53 m). Body mods ship the legs app and their own FPP torso mesh (Angel, Solo,
# Songbird) and leave the torso app to the base game. Until 1.4.0 the body had ONE first-person shell, the body shell
# through the legs mask : calves and feet only, nothing on the torso (two users reported it ; measured 2026-11-05).
FPP_TORSO_APP = r"base\characters\common\player_base_bodies\appearances\t0_000_fpp__full.app"
FPP_LEGS_APP = r"base\characters\common\player_base_bodies\appearances\l0_000_fpp__full.app"
FPP_TORSO_MASK = "18446744073709551391"     # 0xFFFFFFFFFFFFFF1F : chunks 0-4, fallback when the torso app is not readable
FPP_LEGS_MASK = "18446744073709551584"      # 0xFFFFFFFFFFFFFFE0 : chunks 5-7, fallback for the legs app
FPP_INDEX_OFFSET = 25                       # follower switchers at 1066-1074 : free in vanilla (1065 = last body_scars entry, 1090 = genitals)
# Male V (ETUDE § 19, measured 2026-11-03 in the base game, Gymfiend VTK 1.4.3 and MV Head VTK) : other paths, a body
# WITHOUT morphtarget (plain garment component), and no dedicated FPP meshes : the FPP apps show the TPP body (no
# mask) and the HQ arms, and `male_cco` lists the same `body_tattoo` options in FPP_Body, TPP_Body and
# character_creation. So the male shells are listed in every group and need no follower. Slot indexes 1041-1049 are
# free in `male_cco` too (its switchers : 1020, 1040, 1060, 1090...).
M_BODY_DIR = r"base\characters\common\player_base_bodies\player_man_average"
M_ARMS_TEX = r"base\characters\player\masculine\body\arms\textures"
M_HEAD_DIR = r"base\characters\head\player_base_heads\player_man_average"
GENDERS = (("f", "female", "pwa"), ("m", "male", "pma"))   # code, ArchiveXL customization key, file tag
GENDER_TAG = {g: tag for g, _, tag in GENDERS}

TARGETS = [
    dict(code="body", label="Body", tex=r"base\v_textures\body\v_overlay.xbm",
         mesh=BODY_DIR + r"\t0_000_pwa_base__full.mesh", morph=BODY_DIR + r"\t0_000_pwa_base__full.morphtarget",
         tpl="chest_tattoo.app.json", keep="w__chest_tattoo", ctype="entMorphTargetSkinnedMeshComponent",
         old=r"your_name\ccxl\chest_tattoo_demo\meshes\chest_tattoo\your_chest_tattoo_pwa.morphtarget", suffix=""),
    dict(code="arm_l", label="Arm L", tex=ARMS_TEX + r"\femme_arm_left_01_overlay.xbm",
         mesh=BODY_DIR + r"\arms_hq\a0_000_pwa_base_hq__l.mesh", morph=None,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_left", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_left_pwa.mesh", suffix="_arm_l"),
    dict(code="arm_r", label="Arm R", tex=ARMS_TEX + r"\femme_arm_right_01_overlay.xbm",
         mesh=BODY_DIR + r"\arms_hq\a0_000_pwa_base_hq__r.mesh", morph=None,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_right", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_right_pwa.mesh", suffix="_arm_r"),
    dict(code="head", label="Head", tex=HEAD_DIR + r"\h0_000_pwa_c__basehead\textures\h0_001_pwa_c__basehead_overlay.xbm",
         mesh=HEAD_DIR + r"\h0_000_pwa_c__basehead\h0_000_pwa_c__basehead.mesh", morph=HEAD_DIR + r"\h0_000_pwa__morphs.morphtarget",
         tpl="chest_tattoo.app.json", keep="w__chest_tattoo", ctype="entMorphTargetSkinnedMeshComponent",
         old=r"your_name\ccxl\chest_tattoo_demo\meshes\chest_tattoo\your_chest_tattoo_pwa.morphtarget", suffix="_head"),
    dict(code="m_body", gender="m", label="M body", tex=r"base\v_textures\body\v_masc_overlay.xbm",
         mesh=M_BODY_DIR + r"\t0_000_pma_base__full.mesh", morph=None,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_left", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_left_pwa.mesh", suffix="_m"),
    dict(code="m_arm_l", gender="m", label="M arm L", tex=M_ARMS_TEX + r"\masculine_arm_left_01_overlay.xbm",
         mesh=M_BODY_DIR + r"\arms_hq\a0_000_pma_base_hq__l.mesh", morph=None,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_left", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_left_pwa.mesh", suffix="_m_arm_l"),
    dict(code="m_arm_r", gender="m", label="M arm R", tex=M_ARMS_TEX + r"\masculine_arm_right_01_overlay.xbm",
         mesh=M_BODY_DIR + r"\arms_hq\a0_000_pma_base_hq__r.mesh", morph=None,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_right", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_right_pwa.mesh", suffix="_m_arm_r"),
    dict(code="m_head", gender="m", label="M head", tex=M_HEAD_DIR + r"\h0_000_pma_c__basehead\textures\h0_001_pma_c__basehead_overlay.xbm",
         mesh=M_HEAD_DIR + r"\h0_000_pma_c__basehead\h0_000_pma_c__basehead.mesh", morph=M_HEAD_DIR + r"\h0_000_pma__morphs.morphtarget",
         tpl="chest_tattoo.app.json", keep="w__chest_tattoo", ctype="entMorphTargetSkinnedMeshComponent",
         old=r"your_name\ccxl\chest_tattoo_demo\meshes\chest_tattoo\your_chest_tattoo_pwa.morphtarget", suffix="_m_head"),
]
for _t in TARGETS:
    _t.setdefault("gender", "f")
TARGET_BY_CODE = {t["code"]: t for t in TARGETS}
# First person (ETUDE § 16, § 26). What V sees of herself in first person : the FPP torso mesh through the torso app's
# mask (chunks 0-4 : a dedicated shell, copy of that mesh), the same mesh through the legs app's mask (chunks 5-7 : the
# body shell again, the FPP torso mesh having the body's chunk layout), and two dedicated FPP arm meshes (copied as
# decals like the TPP arms). The head is never seen in first person. `parent` = the target whose texture (and, for the
# legs, whose shell) the companion uses ; `app` + `default_mask` = where its chunk mask is read (`fpp_app_mask`).
FPP_TARGETS = [
    dict(code="fpp_torso", label="FPP torso", parent="body", mesh=FPP_TORSO_MESH, morph=None, is_body=True,
         app=FPP_TORSO_APP, default_mask=FPP_TORSO_MASK,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_left", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_left_pwa.mesh", suffix="_fpp_torso"),
    dict(code="fpp_body", label="FPP legs", parent="body", mesh=None, morph=None, is_body=True,
         app=FPP_LEGS_APP, default_mask=FPP_LEGS_MASK,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_left", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_left_pwa.mesh", suffix="_fpp"),
    dict(code="fpp_arm_l", label="FPP arm L", parent="arm_l", mesh=FPP_DIR + r"\a0_000_pwa_fpp__full_l.mesh", morph=None,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_left", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_left_pwa.mesh", suffix="_fpp_arm_l"),
    dict(code="fpp_arm_r", label="FPP arm R", parent="arm_r", mesh=FPP_DIR + r"\a0_000_pwa_fpp__full_r.mesh", morph=None,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_right", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_right_pwa.mesh", suffix="_fpp_arm_r"),
]
FPP_BY_PARENT = {}                              # parent target code -> its FPP companions (the body has two)
for _f in FPP_TARGETS:
    FPP_BY_PARENT.setdefault(_f["parent"], []).append(_f)
TARGET_BY_TEX = {t["tex"]: t for t in TARGETS}
# UV Framework family (ETUDE § 21, measured 2026-11-04). ONE texture for body + both arms, drawn in the vanilla body
# layout (skin in u > 0.22) with the UV arms re-unwrapped into the left strip (u < 0.22 : left arm in v < 0.5, right
# arm in v > 0.5) ; the head overlay apart, on the vanilla head layout (the one the VTK head overlay uses too). The
# UV bodies (Solo, Songbird, the framework's own copies of the vanilla meshes) keep the vanilla body layout, so a
# shell copied from them reads a UV texture correctly by construction. VTK / vanilla arms keep the vanilla ARM layout
# in a texture of their own : a UV texture on them, or a VTK arm texture on UV arms, would be garbage, so
# `mesh_layout` tells the two apart and `run_build` converts the mismatched arm textures to the active arm layout
# (`armconv`, ETUDE § 22 : needs the UV Framework's arm mesh in the game), or skips them. Angel unwraps its feet and
# ankles into the strip (never painted by VTK textures) : under a UV texture those chunks are masked (`strip_mask`).
UV_BODY_TEX = {"f": r"base\4k\common\overlays\fullbody_overlay_d01.xbm", "m": r"base\4k\common\overlays\ma_fullbody_overlay_d01.xbm"}
UV_HEAD_TEX = {"f": r"base\4k\common\overlays\wa_head_overlay_d01.xbm", "m": r"base\4k\common\overlays\ma_head_overlay_d01.xbm"}
UV_STRIP = 0.22                                 # u below which the body texture belongs to the UV arms
ARM_CODES = ("arm_l", "arm_r", "m_arm_l", "m_arm_r")
BODY_CODES = ("body", "m_body")
# texture path -> [(target code, family)] ; "vtk" = the overlay slot of the mesh itself, "uv" = UV Framework layout
TEX_TARGETS = {t["tex"]: [(t["code"], "vtk")] for t in TARGETS}
TEX_TARGETS[UV_BODY_TEX["f"]] = [("body", "uv"), ("arm_l", "uv"), ("arm_r", "uv")]
TEX_TARGETS[UV_BODY_TEX["m"]] = [("m_body", "uv"), ("m_arm_l", "uv"), ("m_arm_r", "uv")]
TEX_TARGETS[UV_HEAD_TEX["f"]] = [("head", "uv")]
TEX_TARGETS[UV_HEAD_TEX["m"]] = [("m_head", "uv")]
KNOWN_OTHER = {
    r"base\v_textures\body\v_body_rm.xbm": "VTK skin roughness (not a tattoo)",
    ARMS_TEX + r"\femme_arm_left_01_roughnessmask.xbm": "VTK arm L roughness",
    ARMS_TEX + r"\femme_arm_right_01_roughnessmask.xbm": "VTK arm R roughness",
    r"base\4k\common\overlays\glow_overlay_d01.xbm": "UV glow (not a tattoo)",
    r"base\4k\common\overlays\ma_glow_overlay_d01.xbm": "UV glow (not a tattoo)",
    r"base\4k\common\overlays\wa_head_glow_d01.xbm": "UV head glow (not a tattoo)",
    r"base\4k\common\overlays\ma_head_glow_overlay_d01.xbm": "UV head glow (not a tattoo)",
    r"base\4k\common\overlays\normals\fullbody_overlay_n01.xbm": "UV normal map (ignored)",
    r"base\4k\common\overlays\normals\ma_fullbody_overlay_n01.xbm": "UV normal map (ignored)",
    r"base\4k\common\overlays\normals\wa_head_overlay_n01.xbm": "UV head normal map (ignored)",
    r"base\4k\common\overlays\normals\ma_head_overlay_n01.xbm": "UV head normal map (ignored)",
}
HASH_PATH = {rdar.fnv1a64(p): p for p in list(TEX_TARGETS) + list(KNOWN_OTHER)}
TARGET_HASHES = {rdar.fnv1a64(p) for p in TEX_TARGETS}
TEX_REGEX = "(" + "|".join(sorted({re.escape(os.path.basename(p)) for p in TEX_TARGETS})) + r"|\d+\.bin)$"
# `002_Tattoos_VTK_`, and the male forms `002_Tattoos_Masc_V_VTK_`, `00_MV_[VTK]_` (Gymfiend family) : same slugs as
# 1.0.1 for every name the old pattern matched
NAME_PREFIX = re.compile(r"^\d+_(Tattoos?_(Masc_V_)?|MV_\[)(VTK|UV)\]?_", re.I)
LEGACY_TABLE = "inkflow_slugs.json"             # v0.1-v0.3 catalogue, next to the archives : imported once
CANARI = ("Ink_Flow_Canari.archive", "Ink_Flow_Canari.archive.xl")


class BuildError(Exception):
    """Anything that stops a build, with a message meant for the player."""


class Cancelled(Exception):
    """The player pressed Cancel. Not a BuildError : no fallback (`fpp_app_mask`) may swallow it."""


def templates_dir():
    """Templates ship next to the package in dev (`Projects/Ink Flow/templates`) and inside the bundle when frozen."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "templates")  # noqa: SLF001
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "templates"))


# ----------------------------------------------------------------------------- helpers
def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def cname(v):
    return {"$type": "CName", "$storage": "string", "$value": v}


def respath(v, flags="Soft"):
    return {"DepotPath": {"$type": "ResourcePath", "$storage": "string", "$value": v}, "Flags": flags}


def set_cname(o, key, v):
    o[key] = cname(v)


def replace_paths(o, table, hits):
    """Replace every string value equal (case-insensitive) to a key of `table`."""
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str):
                for old, new in table.items():
                    if v.lower() == old.lower():
                        o[k] = new
                        hits[old] = hits.get(old, 0) + 1
            else:
                replace_paths(v, table, hits)
    elif isinstance(o, list):
        for v in o:
            replace_paths(v, table, hits)


def stamp(path):
    st = os.stat(path)
    return f"{os.path.basename(path)}|{st.st_size}:{st.st_mtime_ns}"


def cached(marker, key):
    return os.path.isfile(marker) and open(marker).read() == key


def display_name(stem):
    return NAME_PREFIX.sub("", stem).replace("_", " ").strip() or stem


def make_slug(stem, taken):
    base = re.sub(r"[^a-z0-9]+", "_", NAME_PREFIX.sub("", stem).lower()).strip("_")[:40].strip("_") or "tattoo"
    slug, n = base, 2
    while slug in taken:
        slug, n = f"{base}_{n}", n + 1
    return slug


# ----------------------------------------------------------------------------- WolvenKit CLI
class Cli:
    def __init__(self, exe, log, cancel=None):
        if not exe or not os.path.isfile(exe):
            raise BuildError("WolvenKit CLI not found: " + str(exe))
        self.exe = exe
        self.log = log
        self.cancel = cancel         # threading.Event : set = kill the running CLI and raise Cancelled

    def run(self, *args, what=""):
        t = time.time()
        try:
            p = subprocess.Popen([self.exe, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=NO_WINDOW)
        except OSError as e:
            raise BuildError(f"cannot start WolvenKit CLI: {e}") from e
        try:
            while True:
                try:
                    out, err = p.communicate(timeout=0.25)
                    break
                except subprocess.TimeoutExpired:
                    if self.cancel is not None and self.cancel.is_set():
                        raise Cancelled() from None
        except BaseException:        # Cancel, Ctrl+C : never leave a WolvenKit process behind
            p.kill()
            p.communicate()
            raise
        ok = p.returncode == 0 and "Error" not in out
        self.log(f"  cli {what or args[0]}: {'OK' if ok else 'FAILED'} ({time.time() - t:.1f} s)")
        if not ok:
            raise BuildError(f"WolvenKit CLI failed ({what or args[0]}, exit {p.returncode}):\n"
                             + out[-3000:] + err[-2000:])
        return out

    def version(self):
        """Self-test : the CLI starts (the .NET runtime it needs is present)."""
        try:
            r = subprocess.run([self.exe, "--version"], capture_output=True, text=True, timeout=60, creationflags=NO_WINDOW)
        except (OSError, subprocess.TimeoutExpired) as e:
            return False, str(e)
        out = (r.stdout + r.stderr).strip()
        return r.returncode == 0, out[-800:]


NO_WINDOW = 0x08000000 if os.name == "nt" else 0


# ----------------------------------------------------------------------------- 1. inputs
@dataclass
class Entry:
    path: str
    file: str
    stem: str
    id: str
    targets: list = field(default_factory=list)   # TARGETS dicts
    other: list = field(default_factory=list)     # ignored, known labels
    unknown: int = 0
    tex: dict = field(default_factory=dict)       # target code -> texture path inside the archive
    family: dict = field(default_factory=dict)    # target code -> "vtk" | "uv"

    @property
    def supported(self):
        return bool(self.targets)

    @property
    def target_codes(self):
        return [t["code"] for t in self.targets]

    @property
    def targets_label(self):
        """`Body + Arm L + Arm R`, the UV Framework targets tagged `(UV)`."""
        return " + ".join(t["label"] + (" (UV)" if self.family.get(t["code"]) == "uv" else "") for t in self.targets)

    @property
    def ignored_reason(self):
        extra = f"{self.unknown} unknown file(s)" if self.unknown else ""
        return ", ".join(x for x in self.other + [extra] if x) or "no known file"


def scan_files(paths):
    """Index .archive files (RDAR). Order = game load order (alphabetical, case-insensitive)."""
    out = []
    for p in sorted(paths, key=lambda x: os.path.basename(x).lower()):
        if not p.lower().endswith(".archive") or not os.path.isfile(p):
            continue
        try:
            hs = rdar.hashes(p)
        except (ValueError, OSError, Exception) as e:  # noqa: BLE001
            out.append(Entry(p, os.path.basename(p), os.path.splitext(os.path.basename(p))[0], "", [], [f"unreadable: {e}"], 0))
            continue
        found = {HASH_PATH[h] for h in hs if h in HASH_PATH}
        tex, fam = {}, {}
        for path in sorted(found):
            for code, family in TEX_TARGETS.get(path, []):
                if code not in tex or (fam[code] == "uv" and family == "vtk"):   # the mesh's own slot wins over UV
                    tex[code], fam[code] = path, family
        out.append(Entry(path=p, file=os.path.basename(p), stem=os.path.splitext(os.path.basename(p))[0],
                         id=rdar.content_id(p),
                         targets=[t for t in TARGETS if t["code"] in tex],
                         other=sorted(KNOWN_OTHER[x] for x in found if x in KNOWN_OTHER),
                         unknown=len([h for h in hs if h not in HASH_PATH]), tex=tex, family=fam))
    return out


def scan_folder(folder):
    return scan_files([os.path.join(folder, f) for f in os.listdir(folder)])


# ----------------------------------------------------------------------------- catalogue
class Catalogue:
    """Content id -> {slug, name, file}. `slug` is written once and never changes (the game stores the character's
    choices by option name, hence by slug) ; `name` is the label the player edits ; `file` is the last file name
    seen. Stored as one JSON file (app data). A legacy `inkflow_slugs.json` next to the archives is imported."""

    def __init__(self, path):
        self.path = path
        self.data = {}
        if path and os.path.isfile(path):
            try:
                self.data = load(path)
            except (OSError, ValueError):
                self.data = {}

    def slugs(self):
        return {v["slug"] for v in self.data.values()}

    def import_legacy(self, folder, entries, log):
        p = os.path.join(folder, LEGACY_TABLE)
        if not os.path.isfile(p):
            return 0
        try:
            raw = load(p)
        except (OSError, ValueError):
            return 0
        by_file = {e.file: e for e in entries}
        n = 0
        for fname, v in raw.items():
            v = {"slug": v} if isinstance(v, str) else dict(v)
            cid = v.get("id") or (by_file[fname].id if fname in by_file else None)
            if not cid or cid in self.data or v.get("slug") in self.slugs():
                continue
            self.data[cid] = {"slug": v["slug"], "name": v.get("name") or display_name(os.path.splitext(fname)[0]), "file": fname}
            n += 1
        if n:
            log(f"  catalogue: {n} entries imported from {p}")
        return n

    def ensure(self, entries):
        """Every entry gets a slug (new ones derived from the file name) ; `file` follows renames."""
        taken = self.slugs()
        for e in entries:
            if not e.id:
                continue
            if e.id not in self.data:
                s = make_slug(e.stem, taken)
                taken.add(s)
                self.data[e.id] = {"slug": s, "name": display_name(e.stem), "file": e.file}
            else:
                self.data[e.id]["file"] = e.file
                self.data[e.id].setdefault("name", display_name(e.stem))

    def slug(self, e):
        return self.data[e.id]["slug"]

    def name(self, e):
        return (self.data.get(e.id, {}).get("name") or "").strip() or display_name(e.stem)

    def set_name(self, e, name):
        self.data[e.id]["name"] = name.strip()

    def alpha(self, e):
        """Opacity of this tattoo's shells, or None = the build's default (`Settings.alpha`)."""
        a = self.data.get(e.id, {}).get("alpha")
        return float(a) if isinstance(a, (int, float)) else None

    def set_alpha(self, e, alpha):
        if alpha is None:
            self.data[e.id].pop("alpha", None)
        else:
            self.data[e.id]["alpha"] = round(float(alpha), 2)

    def save(self):
        if not self.path:
            return
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, self.path)


def option_label(name, max_len):
    """Label shown in game : cut to `max_len` characters (the creator has no room). -> (label, was_cut)."""
    name = name.strip()
    if max_len and len(name) > max_len:
        return name[:max_len].rstrip(), True
    return name, False


# ----------------------------------------------------------------------------- 2. active meshes
LEGACY_DIR = r"archive\pc\mod"
LEGACY_LIST = "modlist.txt"                                  # optional, written by MO2 : the game follows it
REDMOD_DIR = "mods"                                          # REDmod : mods\<name>\archives\*.archive
REDMOD_LIST = r"r6\cache\modded\MO_REDmod_load_order.txt"   # optional (MO2) ; else ASCII order of the folder names
BASE_GAME = "base game"


def mod_dir(game):
    return os.path.join(game, LEGACY_DIR)


def _read_list(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return [l.strip() for l in f if l.strip() and not l.lstrip().startswith("#")]
    except OSError:
        return []


def _ordered(names, listed):
    """`names` in the game's order : those named in `listed` first, in that order (with or without extension, any
    case), then the others alphabetically (case-insensitive, the game's default)."""
    low = {}
    for n in names:
        low[n.lower()] = n
        low[os.path.splitext(n)[0].lower()] = n
    out, seen = [], set()
    for l in listed:
        n = low.get(l.lower())
        if n and n not in seen:
            out.append(n)
            seen.add(n)
    return out + [n for n in sorted(names, key=str.lower) if n not in seen]


def game_archives(game):
    """Every mod .archive the game loads, in LOAD ORDER (the first that ships a path wins) : `archive\\pc\\mod`
    (`modlist.txt` if present, else alphabetical), then the REDmod folders `mods\\<name>\\archives` (MO2's
    `MO_REDmod_load_order.txt` if present, else alphabetical by folder ; legacy archives load before REDmods).
    -> list of (label, full path) ; label = path relative to the game folder, `\\` separated."""
    out = []
    mod = mod_dir(game)
    if os.path.isdir(mod):
        names = [f for f in os.listdir(mod) if f.lower().endswith(".archive")]
        for n in _ordered(names, _read_list(os.path.join(mod, LEGACY_LIST))):
            out.append((LEGACY_DIR + "\\" + n, os.path.join(mod, n)))
    rm = os.path.join(game, REDMOD_DIR)
    if os.path.isdir(rm):
        folders = [d for d in os.listdir(rm) if os.path.isdir(os.path.join(rm, d, "archives"))]
        for d in _ordered(folders, _read_list(os.path.join(game, REDMOD_LIST))):
            ad = os.path.join(rm, d, "archives")
            for n in rdar.archives_in(ad):
                out.append((f"{REDMOD_DIR}\\{d}\\archives\\{n}", os.path.join(ad, n)))
    return out


def short_label(label):
    """What the log and the window show : `006_Angel_Body.archive` for a legacy archive, `mods\\x\\archives\\y.archive
    (REDmod)` otherwise."""
    if label.lower().startswith(LEGACY_DIR.lower() + "\\"):
        return label[len(LEGACY_DIR) + 1:]
    return label + " (REDmod)"


def owners_of(game, path):
    """(label, full path) of every mod archive shipping `path`, in load order."""
    h = rdar.fnv1a64(path)
    out = []
    for label, full in game_archives(game):
        try:
            if h in rdar.index(full):
                out.append((label, full))
        except (ValueError, OSError):
            continue
    return out


def find_owner(game, path):
    """-> (archive to extract from, short labels of every mod archive shipping `path`, first = the game's choice)."""
    o = owners_of(game, path)
    if o:
        return o[0][1], [short_label(l) for l, _ in o]
    return os.path.join(game, BASEGAME), []


def who_ships(owners):
    return owners[0] + (f" (over {', '.join(owners[1:])})" if len(owners) > 1 else "") if owners else BASE_GAME


def active_owners(game, codes):
    """code -> (owner label, list of archives shipping the mesh). For the UI and the log."""
    out = {}
    for c in codes:
        t = TARGET_BY_CODE[c]
        _, owners = find_owner(game, t["mesh"])
        out[c] = (who_ships(owners), owners)
    return out


def extract_mesh(cli, game, work, t, log):
    """Active mesh of a target (+ morphtarget) : extracted and serialised to JSON, cached on the source archive."""
    src, owners = find_owner(game, t["mesh"])
    log(f"  {t['label']:6s}: {who_ships(owners)}")
    if not os.path.isfile(src):
        raise BuildError("base game archive not found: " + src)
    msrc = None
    if t["morph"]:
        if rdar.fnv1a64(t["morph"]) in rdar.index(src):
            msrc = src
        else:
            # The morphtarget may be shipped apart from the mesh : UV Framework 3.2.1 ships the vanilla head mesh and
            # leaves its morphtarget to the base game (ETUDE § 21). The game pairs them the same way we do here :
            # the morphtarget the game loads, from whichever archive wins it.
            msrc, mowners = find_owner(game, t["morph"])
            log(f"  {'':6s}  morphtarget: {who_ships(mowners)}")
            if not os.path.isfile(msrc):
                raise BuildError("base game archive not found: " + msrc)
    d = os.path.join(work, "mesh", t["code"])
    marker = os.path.join(d, ".src")
    key = stamp(src) + "|" + src.lower() + "|" + t["mesh"] + ("" if msrc in (None, src) else "|" + stamp(msrc) + "|" + msrc.lower())
    mesh_json = os.path.join(d, t["mesh"] + ".json")
    morph_json = os.path.join(d, t["morph"] + ".json") if t["morph"] else None
    if cached(marker, key) and os.path.isfile(mesh_json) and (not morph_json or os.path.isfile(morph_json)):
        return mesh_json, morph_json
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    wanted = [t["mesh"]] + ([t["morph"]] if t["morph"] else [])
    same = [p for p in wanted if p == t["mesh"] or msrc == src]
    rx = "(" + "|".join(re.escape("\\" + os.path.basename(p)) for p in same) + ")$"
    cli.run("unbundle", src, "-o", d, "-r", rx, what=f"unbundle {t['code']}")
    if t["morph"] and msrc != src:
        cli.run("unbundle", msrc, "-o", d, "-r", re.escape("\\" + os.path.basename(t["morph"])) + "$", what=f"unbundle {t['code']} morphtarget")
    common = os.path.commonpath([os.path.join(d, os.path.dirname(p)) for p in wanted])
    cli.run("convert", "serialize", common, what=f"serialize {t['code']}")
    for p in (mesh_json, morph_json):
        if p and not os.path.isfile(p):
            raise BuildError("expected file missing after extraction: " + p)
    with open(marker, "w") as f:
        f.write(key)
    return mesh_json, morph_json


def fpp_app_mask(cli, game, work, f, log):
    """Chunk mask of the FPP torso mesh in the active FPP appearance `f["app"]` (torso app or legs app) : what the game
    shows of that mesh in first person through this appearance. The companion shell `f` gets the same mask. Cached on
    the source archive ; `f["default_mask"]` (the measured vanilla value) is the fallback (the app may not be readable)."""
    app, default, what = f["app"], f["default_mask"], f["label"] + " app"
    src, owners = find_owner(game, app)
    who = who_ships(owners)
    try:
        if not os.path.isfile(src) or rdar.fnv1a64(app) not in rdar.index(src):
            log(f"  {what}: not found ({who}), default mask {default}")
            return default
        d = os.path.join(work, "mesh", "fpp_app_" + f["code"])
        marker = os.path.join(d, ".src")
        key = stamp(src) + "|" + src.lower() + "|" + app
        app_json = os.path.join(d, app + ".json")
        if not (cached(marker, key) and os.path.isfile(app_json)):
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d)
            cli.run("unbundle", src, "-o", d, "-r", re.escape("\\" + os.path.basename(app)) + "$", what=f"unbundle {f['code']} app")
            cli.run("convert", "serialize", os.path.join(d, os.path.dirname(app)), what=f"serialize {f['code']} app")
            if not os.path.isfile(app_json):
                raise BuildError("expected file missing after extraction: " + app_json)
            with open(marker, "w") as fh:
                fh.write(key)
        for a in load(app_json)["Data"]["RootChunk"]["appearances"]:
            for c in a["Data"].get("components") or []:
                mesh = ((c.get("mesh") or {}).get("DepotPath") or {}).get("$value") or ""
                if mesh.lower() == FPP_TORSO_MESH.lower() and c.get("chunkMask") is not None:
                    log(f"  {what}: {who}, mask {c['chunkMask']}")
                    return c["chunkMask"]
        log(f"  ! {what}: {who}, no component on the FPP torso mesh: default mask {default}")
    except (BuildError, OSError, ValueError, KeyError, TypeError) as e:
        log(f"  ! {what}: {who}, not readable ({e}): default mask {default}")
    return default


# ----------------------------------------------------------------------------- 2c. UV layouts (ETUDE § 21)
VTX_SIZE = {"PT_Float16_2": 4, "PT_Float16_4": 8, "PT_Short4N": 8, "PT_UByte4": 4, "PT_UByte4N": 4, "PT_Dec4": 4,
            "PT_Color": 4, "PT_Float32_2": 8, "PT_Float32_3": 12, "PT_Float32_4": 16, "PT_UShort2": 4, "PT_UByte1": 1,
            "PT_UInt1": 4, "PT_Float32_1": 4, "PT_Float16_1": 2, "PT_Float16_3": 6, "PT_Short4": 8, "PT_Short2": 4}
# The 12 skin tints and their variants : `01_ca_pale`, `01_ca_pale_body` (FPP arm R), `01_ca_pale_d01` (Leon Face male head),
# `01_ca_pale_muscularity` (vanilla body)… : a prefix match. Anything else (`personal_link`, `npc_05_plastic_white`,
# Songbird's `songbird_cyber_maskset`…) is not skin.
SKIN_MAT = re.compile(r"^0[1-6]_(ca|bl)_[a-z]+")
TEMPLATE_MASK = (1 << 63) - 1                               # `chunkMask` of the toolkit templates : every chunk shown
ALL_CHUNKS = (1 << 64) - 1


def _half(h):
    s, e, f = (h >> 15) & 1, (h >> 10) & 0x1f, h & 0x3ff
    v = (f / 1024.0) * 2.0 ** -14 if e == 0 else (float("nan") if e == 31 else (1 + f / 1024.0) * 2.0 ** (e - 15))
    return -v if s else v


def mesh_layout(mesh_json):
    """What a shell copied from this mesh needs to know (serialised mesh JSON, vertex based, a fraction of a second) :
      skin_mask   : chunk mask hiding every chunk whose material in the `01_ca_pale` appearance is not a skin tint
                    (the arms' personal link port, Songbird's cyber plates…) : a tattoo is skin only ;
      strip_mask  : chunk mask hiding the skin chunks mostly (> 50 % of their vertices) unwrapped in the UV strip
                    u < 0.22 (Angel's feet and ankles) : for body shells under a UV texture, which keeps the arms there ;
      arms        : "strip" when the skin UVs (LOD 0) stay under u 0.22 = UV Framework arms, else "full" = the vanilla
                    arm layout (vanilla, VTK) ;
      u_max, strip_share, hidden, strip_chunks : the figures behind it, for the log."""
    root = load(mesh_json)["Data"]["RootChunk"]
    rb = root["renderResourceBlob"]["Data"]
    header = rb["header"]
    buf = base64.b64decode(rb["renderBuffer"]["Bytes"])
    app = next((a["Data"] for a in root.get("appearances", []) if a["Data"]["name"]["$value"] == MESH_APPEARANCE), None)
    chunk_mats = [c["$value"] for c in app["chunkMaterials"]] if app else []
    skin_mask, strip_mask = ALL_CHUNKS, ALL_CHUNKS
    hidden, strip_chunks = [], []
    u_max, n_strip, n_all = 0.0, 0, 0
    for n, ci in enumerate(header["renderChunkInfos"]):
        mat = chunk_mats[n] if n < len(chunk_mats) else "01_ca_pale"
        if not SKIN_MAT.match(mat):
            skin_mask &= ~(1 << n)
            hidden.append(f"{n}:{mat}")
            continue
        cv = ci["chunkVertices"]
        lay = cv["vertexLayout"]["elements"]["Elements"]
        tex = next((e for e in lay if e["usage"] == "PS_TexCoord" and e["usageIndex"] == 0), None)
        if tex is None:
            continue
        stream = [e for e in lay if e["streamIndex"] == tex["streamIndex"] and e["streamType"] == "ST_PerVertex"]
        stride = sum(VTX_SIZE.get(e["type"], 4) for e in stream)
        pos = sum(VTX_SIZE.get(e["type"], 4) for e in stream[:stream.index(tex)])
        base = cv["byteOffsets"]["Elements"][tex["streamIndex"]]
        nv = ci["numVertices"]
        in_strip = 0
        for i in range(nv):
            u = _half(struct.unpack_from("<H", buf, base + i * stride + pos)[0])
            if u != u:
                continue
            u -= math.floor(u)
            if u < UV_STRIP:
                in_strip += 1
            elif ci["lodMask"] == 1 and u > u_max:
                u_max = u
        if nv and in_strip * 2 > nv:
            strip_mask &= ~(1 << n)
            strip_chunks.append(n)
        if ci["lodMask"] == 1:
            n_strip += in_strip
            n_all += nv
    if n_all == 0:
        # No skin chunk recognised at all (material names we do not know) : never hand out an empty shell. Everything
        # is shown and the layout is taken as the vanilla one.
        skin_mask, strip_mask, strip_chunks = ALL_CHUNKS, ALL_CHUNKS, []
        hidden = ["(none recognised as skin, every chunk kept: " + ", ".join(hidden) + ")"] if hidden else []
        u_max = 1.0
    return dict(skin_mask=skin_mask, strip_mask=strip_mask, arms="strip" if u_max <= UV_STRIP + 0.03 else "full",
                u_max=u_max, strip_share=(n_strip / n_all) if n_all else 0.0, hidden=hidden, strip_chunks=strip_chunks)


def blank_uv_strip(cli, game, src_xbm, dst_xbm, tmp, log, keep=True):
    """Copy of a UV body texture whose arm strip (u < UV_STRIP) is cleared at every mip level : for the body shell of
    a mesh that unwraps some of its skin into the strip (Angel's feet and ankles), so the shell shows the body ink
    and nothing on those parts, instead of hiding whole chunks (QA Hell_Kaiser 2026-11-04 : the ankle ring was
    lost). WolvenKit export (DDS, uncompressed RGBA8, DX10 header) -> bytes cleared in place -> import (`--keep`
    on a copy of the original keeps its texture setup). ~10 s for a 4K, ~3 min for an 8K ; cached by the caller."""
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    try:
        cli.run("export", src_xbm, "-o", tmp, "-gp", game, what="export UV texture (strip)")
        dds = next((os.path.join(r, f) for r, _, fs in os.walk(tmp) for f in fs if f.lower().endswith(".dds")), None)
        if not dds:
            raise BuildError("UV texture not exported: " + src_xbm)
        with open(dds, "rb") as f:
            data = bytearray(f.read())
        h, w = struct.unpack_from("<II", data, 12)
        mips = max(1, struct.unpack_from("<I", data, 28)[0])
        dx10 = data[84:88] == b"DX10"
        off = 148 if dx10 else 128
        if dx10:
            dxgi = struct.unpack_from("<I", data, 128)[0]
            if dxgi not in (28, 29):            # R8G8B8A8_UNORM / _SRGB : what WolvenKit writes for colour textures
                raise BuildError(f"UV texture exported in an unexpected DDS format (DXGI {dxgi}): " + src_xbm)
        elif struct.unpack_from("<I", data, 88)[0] != 32:
            raise BuildError("UV texture exported in an unexpected DDS format (not 32 bpp): " + src_xbm)
        for level in range(mips):
            lw, lh = max(1, w >> level), max(1, h >> level)
            cols = min(lw, math.ceil(UV_STRIP * lw))
            zero = bytes(cols * 4)
            for row in range(lh):
                start = off + row * lw * 4
                data[start:start + cols * 4] = zero
            off += lw * lh * 4
        if off > len(data):
            raise BuildError("UV texture DDS shorter than its header says: " + src_xbm)
        with open(dds, "wb") as f:
            f.write(data)
        out = os.path.join(tmp, "import")
        os.makedirs(out)
        if keep:
            shutil.copyfile(src_xbm, os.path.join(out, os.path.basename(src_xbm)))
        cli.run("import", dds, "-o", out, *(["--keep"] if keep else []), what="import UV texture (strip cleared)")
        new = os.path.join(out, os.path.basename(src_xbm))
        if not os.path.isfile(new):
            raise BuildError("strip-cleared texture not produced: " + new)
        os.makedirs(os.path.dirname(dst_xbm), exist_ok=True)
        shutil.move(new, dst_xbm)
        log(f"  UV texture copied with the arm strip cleared ({w}x{h}, {mips} mips): {os.path.basename(src_xbm)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def blanked_texture(cli, s, slug, src_xbm, log):
    """`blank_uv_strip` cached in work\\tex\\<slug>\\blank\\ (key : source texture stamp + strip width)."""
    d = os.path.join(s.work, "tex", slug, "blank")
    dst = os.path.join(d, os.path.basename(src_xbm))
    marker = os.path.join(d, ".src")
    key = stamp(src_xbm) + f"|{UV_STRIP}|keep"
    if not (cached(marker, key) and os.path.isfile(dst)):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        blank_uv_strip(cli, s.game, src_xbm, dst, d + ".tmp", log)
        with open(marker, "w") as f:
            f.write(key)
    return dst


def extract_ref(cli, archive, work, sub, mesh_path):
    """One mesh of one given archive (not necessarily the winner) serialised to JSON, cached in work\\mesh\\<sub>."""
    d = os.path.join(work, "mesh", sub)
    marker = os.path.join(d, ".src")
    key = stamp(archive) + "|" + archive.lower() + "|" + mesh_path
    mesh_json = os.path.join(d, mesh_path + ".json")
    if cached(marker, key) and os.path.isfile(mesh_json):
        return mesh_json
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    cli.run("unbundle", archive, "-o", d, "-r", re.escape("\\" + os.path.basename(mesh_path)) + "$", what=f"unbundle {sub}")
    cli.run("convert", "serialize", os.path.join(d, os.path.dirname(mesh_path)), what=f"serialize {sub}")
    if not os.path.isfile(mesh_json):
        raise BuildError("expected file missing after extraction: " + mesh_json)
    with open(marker, "w") as f:
        f.write(key)
    return mesh_json


def arm_refs(cli, game, work, t, log):
    """The two meshes an arm conversion pairs (ETUDE § 22) : the vanilla arm (base game) and a copy of it unwrapped
    into the UV strip, i.e. the first mod archive in load order shipping this arm with the strip layout AND the vanilla
    geometry (the UV Framework ; Solo's or Songbird's own UV arms are other shapes and are passed over).
    -> (vanilla json, strip json, owner label) ; BuildError with the reason when there is none."""
    base = os.path.join(game, BASEGAME)
    if not os.path.isfile(base):
        raise BuildError("base game archive not found: " + base)
    van = extract_ref(cli, base, work, f"ref_{t['code']}_vanilla", t["mesh"])
    tried = []
    for n, (label, full) in enumerate(owners_of(game, t["mesh"])):
        js = extract_ref(cli, full, work, f"ref_{t['code']}_{n}", t["mesh"])
        if mesh_layout(js)["arms"] != "strip":
            continue
        try:
            armconv.pairing(van, js, SKIN_MAT.match, MESH_APPEARANCE)
        except armconv.ConvError as e:
            tried.append(f"{short_label(label)}: {e}")
            continue
        log(f"  {t['label']:6s}: UV strip arm for conversions: {short_label(label)}")
        return van, js, short_label(label)
    raise BuildError("no UV Framework arm mesh in the game" + (f" ({'; '.join(tried)})" if tried else ""))


def converted_textures(cli, s, it, refs, log):
    """Arm textures of one tattoo converted to the active arm layout (`it.conv` : code -> "full" | "strip"), cached in
    work\\tex\\<slug>\\conv\\<code>\\. The source DDS is exported once per source texture. Fills `it.conv_tex`
    (code -> local .xbm) ; an arm with no ink after conversion is dropped (-> list of the dropped codes)."""
    dropped = []
    by_src = {}
    for code in it.conv:
        by_src.setdefault(os.path.join(it.texdir, it.entry.tex[code]), []).append(code)
    for src_xbm, codes in by_src.items():
        todo = []
        for code in codes:
            d = os.path.join(s.work, "tex", it.slug, "conv", code)
            ra, rb = refs[code][0], refs[code][1]
            key = "|".join([stamp(src_xbm), stamp(ra), stamp(rb), it.conv[code], "v2"])
            marker = os.path.join(d, ".src")
            if cached(marker, key + "|empty"):
                dropped.append(code)
            elif cached(marker, key) and os.path.isfile(os.path.join(d, code + ".xbm")):
                it.conv_tex[code] = os.path.join(d, code + ".xbm")
            else:
                todo.append((code, d, marker, key))
        if not todo:
            continue
        tmp = os.path.join(s.work, "tex", it.slug, "conv.tmp")
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp)
        try:
            cli.run("export", src_xbm, "-o", tmp, "-gp", s.game, what="export texture (arm conversion)")
            dds = next((os.path.join(r, f) for r, _, fs in os.walk(tmp) for f in fs if f.lower().endswith(".dds")), None)
            if not dds:
                raise BuildError("texture not exported for the arm conversion: " + src_xbm)
            for code, d, marker, key in todo:
                t0 = time.time()
                t = TARGET_BY_CODE[code]
                out = os.path.join(tmp, "import")
                shutil.rmtree(out, ignore_errors=True)
                os.makedirs(out)
                try:
                    r = armconv.convert(it.conv[code], refs[code][0], refs[code][1], dds, os.path.join(out, code + ".dds"),
                                        SKIN_MAT.match, MESH_APPEARANCE)
                except armconv.ConvError as e:
                    raise BuildError(f"[{it.slug}] {t['label']}: arm conversion failed: {e}") from e
                shutil.rmtree(d, ignore_errors=True)
                os.makedirs(d)
                what = "to the vanilla arm layout" if it.conv[code] == "full" else "into the UV strip"
                if r["ink"] == 0:
                    with open(marker, "w") as f:
                        f.write(key + "|empty")
                    dropped.append(code)
                    log(f"  [{it.slug}] {t['label']}: no ink on this arm, left out")
                    continue
                # `--keep` on a copy of the source keeps its texture setup (BC7 for the UV packs) at the new size
                shutil.copyfile(src_xbm, os.path.join(out, code + ".xbm"))
                cli.run("import", os.path.join(out, code + ".dds"), "-o", out, "--keep", what=f"import converted {code}")
                new = os.path.join(out, code + ".xbm")
                if not os.path.isfile(new):
                    raise BuildError("converted texture not produced: " + new)
                shutil.move(new, os.path.join(d, code + ".xbm"))
                with open(marker, "w") as f:
                    f.write(key)
                it.conv_tex[code] = os.path.join(d, code + ".xbm")
                log(f"  [{it.slug}] {t['label']}: converted {what} ({r['size']}x{r['size']}, {r['ink']:.0%} of the arm "
                    f"inked, {r['share']:.1%} paired, {time.time() - t0:.0f} s)")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return dropped


def shell_mask(layouts, code, family, is_body, base=TEMPLATE_MASK):
    """`chunkMask` (string) of a shell component, or None when the template's own mask already fits."""
    lay = layouts.get(code)
    m = base
    if lay:
        m &= lay["skin_mask"]
        if is_body and family == "uv":
            m &= lay["strip_mask"]
    return None if m == base else str(m)


# ----------------------------------------------------------------------------- 3. textures
def dds_mips(path):
    """(width, height, mip count) of a DDS file header."""
    with open(path, "rb") as f:
        head = f.read(32)
    h, w = struct.unpack_from("<II", head, 12)
    return w, h, max(1, struct.unpack_from("<I", head, 28)[0])


def texture_headers(cli, d):
    """{xbm path: (width, height, mipCount, textureDataSize, mip table entries, buffer bytes)} of every .xbm under
    `d`, read from WolvenKit's serialization (one CLI call, the JSON files removed afterwards). The buffer length is
    taken from the base64 string without decoding it (an 8K texture serializes to 120 MB of JSON)."""
    xbms = [os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs if f.endswith(".xbm")]
    if not xbms:
        return {}
    cli.run("convert", "serialize", d, what="serialize textures (header check)")
    out = {}
    for x in xbms:
        js = x + ".json"
        if not os.path.isfile(js):
            raise BuildError("texture not serialized for the header check: " + x)
        try:
            with open(js, encoding="utf-8") as f:
                blob = json.load(f)["Data"]["RootChunk"]["renderTextureResource"]["renderResourceBlobPC"]["Data"]
            info, size = blob["header"]["textureInfo"], blob["header"]["sizeInfo"]
            b = blob["textureData"]["Bytes"]
            buf = len(b) * 3 // 4 - b[-2:].count("=")
            out[x] = (size["width"], size["height"], info["mipCount"], info["textureDataSize"],
                      len(blob["header"]["mipMapInfo"]), buf)
        except (KeyError, TypeError, ValueError) as e:
            raise BuildError(f"texture header unreadable ({e!r}): " + x)
        finally:
            os.remove(js)
    return out


def normalize_textures(cli, game, d, log):
    """Every extracted texture is checked and rebuilt when its header cannot be trusted :
    (a) header inconsistent with its data : mip count != mip table, declared data size != buffer. Kala's Japanese V2
        (VTK and UV) say « 4096 x 4096, 1 mip, 1 398 128 bytes » over a full 13-mip buffer of 22 369 648 bytes ; the
        engine copies the 4096 mip out of a 1.4 MB buffer and crashes (ReportQueue 2026-11-04 18 h 34, 20 h 14, 20 h 30 :
        read 1.44 MB past the source ; ETUDE § 25). Angel never crashed because its strip-cleared copy had been rebuilt ;
    (b) mip chain stopping before 1x1 (11 levels on a 4096 : the male Kala / Gymfiend packs) : stripes or nothing
        through the decal material (QA Hell_Kaiser 2026-11-03, 14 textures out of 14, canary ETUDE § 19).
    Rebuild = WolvenKit export (top mip, RGBA8) -> full alpha-weighted box-filtered chain (`armconv.write_dds`) ->
    import `--keep` on a copy of the original, which keeps its texture setup : BC7 stays BC7 (22 MB of video memory
    for a 4K, not the 85 MB of the uncompressed re-encode of 1.1.0). A texture that is not square or not a power of two
    takes the plain import instead (full chain, uncompressed). Healthy textures are left byte for byte."""
    headers = texture_headers(cli, d)
    if not headers:
        return
    tmp = d + ".dds"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    try:
        cli.run("export", d, "-o", tmp, "-gp", game, what="export textures (mip check)")
        for x, (hw, hh, hmips, hsize, hmm, hbuf) in headers.items():
            dds = os.path.join(tmp, os.path.relpath(x, d))[:-4] + ".dds"
            if not os.path.isfile(dds):
                raise BuildError("texture not exported for the mip check: " + x)
            w, h, mips = dds_mips(dds)
            full = max(w, h).bit_length()
            reasons = []
            if hmips != hmm or hsize != hbuf:
                reasons.append(f"header says {hmips} mip(s) / {hsize} bytes, data holds {hmm} mip(s) / {hbuf} bytes")
            if mips not in (1, full):
                reasons.append(f"mip chain stops at {mips} of {full} levels")
            if not reasons:
                continue
            out = os.path.join(tmp, "import")
            shutil.rmtree(out, ignore_errors=True)
            os.makedirs(out)
            if w == h and w & (w - 1) == 0:
                src = os.path.join(tmp, "full", os.path.basename(x)[:-4] + ".dds")
                os.makedirs(os.path.dirname(src), exist_ok=True)
                armconv.write_dds(src, w, (0, 0, w, h), armconv.np.array(armconv.dds_top(dds)))
                shutil.copyfile(x, os.path.join(out, os.path.basename(x)))
                cli.run("import", src, "-o", out, "--keep", what="rebuild texture (keep setup)")
                how = f"full chain of {full}, setup kept"
            else:
                cli.run("import", dds, "-o", out, what="rebuild texture")
                how = "plain import"
            new = os.path.join(out, os.path.basename(x))
            if not os.path.isfile(new):
                raise BuildError("rebuilt texture not produced: " + new)
            shutil.move(new, x)
            log(f"  texture rebuilt ({w}x{h}, {'; '.join(reasons)} -> {how}): {os.path.relpath(x, d)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def extract_textures(cli, game, archive, slug, work, log):
    """All target textures of one tattoo archive -> work\\tex\\<slug>\\<game path> (cached), untrustworthy headers and
    truncated mip chains rebuilt (`normalize_textures`)."""
    d = os.path.join(work, "tex", slug)
    marker = os.path.join(d, ".src")
    key = stamp(archive) + "|" + TEX_REGEX + "|mips2"
    if not cached(marker, key):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        cli.run("unbundle", archive, "-o", d, "-r", TEX_REGEX, what=f"unbundle {slug}")
        for f in os.listdir(d):
            m = re.fullmatch(r"(\d+)\.bin", f)
            if m and int(m.group(1)) in HASH_PATH:
                dst = os.path.join(d, HASH_PATH[int(m.group(1))])
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(os.path.join(d, f), dst)
                log(f"  path restored from its hash: {HASH_PATH[int(m.group(1))]}")
        normalize_textures(cli, game, d, log)
        with open(marker, "w") as f:
            f.write(key)
    return d


# ----------------------------------------------------------------------------- 4. construction
class Paths:
    def __init__(self, slug, t, family="vtk"):
        d = rf"{P}\tattoos\{slug}"
        s = t["suffix"]
        tag = GENDER_TAG[t.get("gender", "f")]
        if family == "uv":      # one UV texture serves body + both arms : copied once, shared by their shells
            self.tex = rf"{d}\{slug}_uv_{tag}" + ("_head" if t["code"] in ("head", "m_head") else "") + ".xbm"
        else:
            self.tex = rf"{d}\{slug}{s}.xbm"
        self.mesh = rf"{d}\{slug}_{tag}{s}.mesh"
        self.morph = rf"{d}\{slug}_{tag}{s}.morphtarget"
        self.app = rf"{d}\{slug}{s}.app"                           # route 1
        self.slot_app = lambda n: rf"{d}\{slug}_slot{n}{s}.app"    # route 2
        self.resource = self.morph if t["morph"] else self.mesh


def decal_material(tex, alpha):
    values = [{"$type": "rRef:ITexture", "DiffuseTexture": respath(tex, "Default")}]
    if alpha is not None:
        values.append({"$type": "Float", "DiffuseAlpha": alpha})
    return {"$type": "CMaterialInstance", "audioTag": cname("None"), "baseMaterial": respath(DECAL_MI, "Default"),
            "cookingPlatform": "PLATFORM_None", "enableMask": 0, "metadata": None, "resourceVersion": 4, "values": values}


def material_stores(root):
    """Where a mesh keeps its local materials, every non-empty store : `localMaterialBuffer.materials` (body mods,
    vanilla body and head : a list of CMaterialInstance), `preloadLocalMaterialInstances` or `localMaterialInstances`
    (vanilla arm meshes : a list of {HandleId, Data: CMaterialInstance}). -> [(kind, list)], kind "buffer", "preload"
    or "local"."""
    found = []
    for kind, lst in (("buffer", (root.get("localMaterialBuffer") or {}).get("materials")),
                      ("preload", root.get("preloadLocalMaterialInstances")),
                      ("local", root.get("localMaterialInstances"))):
        if lst:
            found.append((kind, lst))
    return found


def shell(active, tex, alpha, what):
    """Shell = copy of the active mesh whose every skin material becomes the decal (canary v5). Works on the three
    material stores (`material_stores`) : the vanilla arms keep theirs in `preloadLocalMaterialInstances` (measured
    2026-11-02, ETUDE § 17), body mods and the vanilla body / head in `localMaterialBuffer`."""
    mesh = copy.deepcopy(active)
    root = mesh["Data"]["RootChunk"]
    entries = root["materialEntries"]
    stores = material_stores(root)
    kind, mats = stores[0] if len(stores) == 1 else (None, [])
    if root.get("externalMaterials") or root.get("preloadExternalMaterials"):
        raise BuildError(f"{what}: external materials in the active mesh (unsupported body mod)")
    if not (kind and len(mats) == len(entries) and all(e["isLocalInstance"] == 1 for e in entries)):
        raise BuildError(f"{what}: non-local or mixed materials in the active mesh (unsupported body mod ; stores "
                         f"{[k for k, _ in stores] or 'none'}, {len(mats)} materials for {len(entries)} entries)")
    if not any(e["name"]["$value"].startswith(MESH_APPEARANCE) for e in entries):   # FPP arm R names them `01_ca_pale_body`
        raise BuildError(f"{what}: no material {MESH_APPEARANCE}* in the active mesh")
    if not any(a["Data"]["name"]["$value"] == MESH_APPEARANCE for a in root["appearances"]):
        raise BuildError(f"{what}: no appearance {MESH_APPEARANCE} in the active mesh")
    # The decal instances always go into the EMBEDDED buffer, whatever store the source used : the vanilla arms keep
    # theirs in `preloadLocalMaterialInstances`, and a shell left that way renders when the entity is loaded with the
    # save but not when the slot is changed at the mirror (QA Hell_Kaiser 2026-11-02, ETUDE § 17). Body mods embed.
    new = [decal_material(tex, alpha) for _ in mats]
    buf = root.get("localMaterialBuffer") or {"$type": "meshMeshMaterialBuffer", "materials": [], "rawData": None, "rawDataHeaders": []}
    buf["materials"] = new
    root["localMaterialBuffer"] = buf
    root["preloadLocalMaterialInstances"] = []
    root["localMaterialInstances"] = []
    mats = new
    root["castsRayTracedShadowsFromOriginalGeometry"] = 0
    chunks = root["renderResourceBlob"]["Data"]["header"]["renderChunkInfos"]
    return mesh, len(mats), sum(c["numVertices"] for c in chunks)


def retarget_morph(active_morph, t, new_mesh):
    morph = copy.deepcopy(active_morph)
    hits = {}
    replace_paths(morph["Data"]["RootChunk"], {t["mesh"]: new_mesh}, hits)
    if hits.get(t["mesh"], 0) != 1:
        raise BuildError(f"morphtarget of {t['code']}: baseMesh reference not found exactly once ({hits})")
    return morph, len(morph["Data"]["RootChunk"].get("targets") or [])


def make_app(template, t, resource, comp_name, definition, chunk_mask=None):
    app = copy.deepcopy(template)
    root = app["Data"]["RootChunk"]
    root["appearances"] = [a for a in root["appearances"] if a["Data"]["name"]["$value"] == t["keep"]]
    if len(root["appearances"]) != 1:
        raise BuildError("template appearance missing: " + t["keep"])
    a = root["appearances"][0]["Data"]
    set_cname(a, "name", definition)
    hits = {}
    replace_paths(a, {t["old"]: resource}, hits)
    if sum(hits.values()) < 2:
        raise BuildError(f"template {t['tpl']}: resource path not found ({hits})")
    n = 0
    for comp in a["components"] + a["compiledData"]["Data"]["Chunks"]:
        if comp.get("$type") == t["ctype"]:
            set_cname(comp, "name", comp_name)
            set_cname(comp, "meshAppearance", MESH_APPEARANCE)
            comp["castShadows"] = "Never"
            comp["castLocalShadows"] = "Never"
            if chunk_mask is not None:
                comp["chunkMask"] = chunk_mask
            n += 1
    if n != 2:
        raise BuildError(f"template {t['tpl']}: {n} components of type {t['ctype']} (expected 2)")
    return app


@dataclass
class Settings:
    game: str
    cli: str
    work: str
    out: str
    name: str = "Ink_Flow"
    slots: int = 2
    slot_index: int = 1041
    slot_title: str = "Ink {n}"
    max_name: int = 20
    alpha: float = 1.0
    mirror: bool = True
    fpp: bool = True
    route1: bool = False


@dataclass
class Item:
    entry: Entry
    slug: str
    name: str
    texdir: str = ""
    alpha: float = None          # per-tattoo opacity (catalogue) ; None = Settings.alpha
    targets: list = None         # TARGETS dicts built for this item : entry.targets minus the arms `run_build` skips
    skipped: list = field(default_factory=list)   # "Arm L: UV tattoo on VTK / vanilla arms"…, for the log
    no_fpp: set = field(default_factory=set)      # FPP companion codes skipped (first-person arm layout mismatch)
    blanked: set = field(default_factory=set)     # body codes whose shell reads the UV texture with the arm strip cleared
    conv: dict = field(default_factory=dict)      # arm code -> "full" | "strip" : texture converted to that arm layout
    conv_tex: dict = field(default_factory=dict)  # arm code -> converted local .xbm (`converted_textures`)
    texpath: dict = field(default_factory=dict)   # target code -> texture path in the archive (set by `build_archive`)

    def __post_init__(self):
        if self.targets is None:
            self.targets = list(self.entry.targets)

    def family(self, t):
        return self.entry.family.get(t["code"], "vtk")


@dataclass
class BuildResult:
    archive: str
    xl: str
    listing: list
    items: list
    seconds: float
    size: int


def gender_customization(s, tpl_cc, tk_switcher, gender, items, slots, tags, option, info, off):
    """The .inkcharcustomization (JSON) of one gender : per slot a switcher driving one uiSlot per target of that
    gender, options Off + one per tattoo ; V female with first person : a hidden follower per slot (ETUDE § 16, 18) ;
    route 1 (female only). Male V needs no follower : its FPP shows the TPP meshes (§ 19)."""
    cc = copy.deepcopy(tpl_cc)
    root = cc["Data"]["RootChunk"]
    targets = [t for t in TARGETS if t["gender"] == gender]
    followers = s.fpp and gender == "f"
    entries, names_all, names_fpp = [], [], []
    body_t = TARGETS[0]

    with_body = [it for it in items if body_t in it.targets]
    if s.route1 and gender == "f" and with_body:
        s1 = copy.deepcopy(tk_switcher)
        set_cname(s1, "name", "None")
        set_cname(s1, "link", "body_tattoo")
        s1["index"] = 0
        s1["localizedName"] = ""
        set_cname(s1, "uiSlot", "None")
        s1["uiSlots"] = []
        s1["switchVisibility"] = 0
        s1["editTags"] = []
        s1["options"] = [option(i, f"UI-Customization-inkflow_{it.slug}_v", [f"inkflow_{it.slug}"]) for i, it in enumerate(with_body)]
        entries.append(s1)
        for it in with_body:
            entries.append(info(f"inkflow_{it.slug}", "body_tattoo", Paths(it.slug, body_t).app, f"w__{it.slug}"))
            names_all.append(f"inkflow_{it.slug}")

    for n_ in slots:
        ui = {t["code"]: f"inkflow_slot{n_}{t['suffix']}" for t in targets}
        off_name = {t["code"]: f"inkflow_slot{n_}_off{t['suffix']}" for t in targets}
        s2 = copy.deepcopy(tk_switcher)
        set_cname(s2, "name", f"inkflow_slot{n_}")
        s2["index"] = s.slot_index + n_ - 1
        s2["localizedName"] = f"UI-Customization-inkflow_slot{n_}"
        set_cname(s2, "uiSlot", f"inkflow_slot{n_}_switcher")
        s2["editTags"] = list(tags)
        s2["uiSlots"] = [cname(ui[t["code"]]) for t in targets]
        s2["options"] = [copy.deepcopy(tk_switcher["options"][0])]
        s2["options"][0]["names"] = [cname(off_name[t["code"]]) for t in targets]
        offs = [off(off_name[t["code"]], ui[t["code"]]) for t in targets]
        infos = []
        for i, it in enumerate(items, 1):
            names = []
            for t in targets:
                if t in it.targets:
                    nm = f"inkflow_slot{n_}_{it.slug}{t['suffix']}"
                    infos.append(info(nm, ui[t["code"]], Paths(it.slug, t).slot_app(n_), f"w__{it.slug}{t['suffix']}"))
                    names.append(nm)
                else:
                    names.append(off_name[t["code"]])
            s2["options"].append(option(i, f"UI-Customization-inkflow_{it.slug}", names))
        entries += [s2] + offs + infos
        names_all += [f"inkflow_slot{n_}"] + [o["name"]["$value"] for o in offs] + [x["name"]["$value"] for x in infos]
        if followers:
            # Follower switcher : same link key as the slot's switcher (vanilla `nipples` / `fpp_nipples` share
            # "nipples type", `fpp_body_tattoo` links to `body_tattoo`), same option indexes, one FPP uiSlot per
            # companion ; listed in the FPP_Body group only, so the creator never draws the FPP shells.
            set_cname(s2, "link", f"inkflow_slot{n_}")
            # The slot's switcher drives the link (vanilla : `body_tattoo` linkController 1, `fpp_body_tattoo` 0).
            # Measured in game on 2026-11-02 with both at 0 (toolkit template) : the follower stays Off, the FPP
            # shells are never requested and the TPP arm shells are drawn over the FPP arms (holes).
            s2["linkController"] = 1
            fui = {f["code"]: f"inkflow_slot{n_}{f['suffix']}" for f in FPP_TARGETS}
            foff = {f["code"]: f"inkflow_slot{n_}_off{f['suffix']}" for f in FPP_TARGETS}
            s3 = copy.deepcopy(tk_switcher)
            set_cname(s3, "name", f"inkflow_slot{n_}_fpp")
            set_cname(s3, "link", f"inkflow_slot{n_}")
            s3["linkController"] = 0
            s3["index"] = s.slot_index + FPP_INDEX_OFFSET + n_ - 1
            s3["localizedName"] = f"UI-Customization-inkflow_slot{n_}"
            set_cname(s3, "uiSlot", f"inkflow_slot{n_}_fpp_switcher")
            s3["editTags"] = list(tags)
            s3["uiSlots"] = [cname(fui[f["code"]]) for f in FPP_TARGETS]
            s3["options"] = [copy.deepcopy(tk_switcher["options"][0])]
            s3["options"][0]["names"] = [cname(foff[f["code"]]) for f in FPP_TARGETS]
            foffs = [off(foff[f["code"]], fui[f["code"]]) for f in FPP_TARGETS]
            finfos = []
            for i, it in enumerate(items, 1):
                names = []
                for f in FPP_TARGETS:
                    if TARGET_BY_CODE[f["parent"]] in it.targets and f["code"] not in it.no_fpp:
                        nm = f"inkflow_slot{n_}_{it.slug}{f['suffix']}"
                        finfos.append(info(nm, fui[f["code"]], Paths(it.slug, f).slot_app(n_), f"w__{it.slug}{f['suffix']}"))
                        names.append(nm)
                    else:
                        names.append(foff[f["code"]])
                s3["options"].append(option(i, f"UI-Customization-inkflow_{it.slug}", names))
            entries += [s3] + foffs + finfos
            names_fpp += [f"inkflow_slot{n_}_fpp"] + [o["name"]["$value"] for o in foffs] + [x["name"]["$value"] for x in finfos]

    root["bodyCustomizationOptions"] = [{"HandleId": str(i), "Data": d} for i, d in enumerate(entries)]
    for grp in root["bodyGroups"]:
        fpp_group = followers and grp["name"]["$value"] == "FPP_Body"
        grp["options"] = [cname(x) for x in (names_fpp if fpp_group else names_all)]
    return cc



def build_archive(s, cli, items, active, log, fpp_masks=None, layouts=None):
    """items: list of Item ; active: target code -> (mesh json, morph json) ; fpp_masks: FPP companion code -> chunk mask
    read in its FPP appearance (`fpp_app_mask`, when `s.fpp`) ; layouts: target code -> `mesh_layout` (chunk masks).
    -> (archive, xl, listing)."""
    layouts, fpp_masks = layouts or {}, fpp_masks or {}
    tdir = templates_dir()
    src = os.path.join(s.work, "pack", s.name)
    shutil.rmtree(src, ignore_errors=True)
    os.makedirs(src)
    os.makedirs(s.out, exist_ok=True)

    def save(rel, j):
        p = os.path.join(src, rel + ".json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(j, f, indent=1)

    meshes = {c: load(m) for c, (m, _) in active.items()}
    morphs = {c: load(mo) for c, (_, mo) in active.items() if mo}
    tpls = {t["tpl"]: load(os.path.join(tdir, t["tpl"])) for t in TARGETS}
    slots = list(range(1, s.slots + 1))
    expected = []

    for it in items:
        slug = it.slug
        alpha = s.alpha if it.alpha is None else it.alpha
        parts = []
        for t in it.targets:
            fam = it.family(t)
            pp = Paths(slug, t, fam)
            src_tex = os.path.join(it.texdir, it.entry.tex.get(t["code"], t["tex"]))
            if not os.path.isfile(src_tex):
                raise BuildError("texture missing after extraction: " + src_tex)
            if t["code"] in it.conv:
                # Arm texture converted to the active arm layout (ETUDE § 22) : one texture per arm
                src_tex = it.conv_tex[t["code"]]
                pp.tex = rf"{P}\tattoos\{slug}\{slug}{t['suffix']}_conv.xbm"
            elif fam == "uv" and t["code"] in BODY_CODES and layouts.get(t["code"], {}).get("strip_chunks"):
                # The body unwraps skin into the arm strip (Angel's feet) : the body shell reads a copy of the UV
                # texture with the strip cleared, and keeps every chunk (ETUDE § 21, QA of the ankles).
                src_tex = blanked_texture(cli, s, slug, src_tex, log)
                pp.tex = pp.tex[:-4] + "_noarms.xbm"
                it.blanked.add(t["code"])
            it.texpath[t["code"]] = pp.tex
            dst = os.path.join(src, pp.tex)
            if not os.path.isfile(dst):            # a UV texture is shared by the body and arm shells : one copy
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(src_tex, dst)
            mesh, nm, nv = shell(meshes[t["code"]], pp.tex, alpha, f"[{slug}] {t['code']}")
            save(pp.mesh, mesh)
            expected.append(pp.mesh)
            nt = 0
            if t["morph"]:
                morph, nt = retarget_morph(morphs[t["code"]], t, pp.mesh)
                save(pp.morph, morph)
                expected.append(pp.morph)
            mask = shell_mask(layouts, t["code"], "vtk" if t["code"] in it.blanked else fam, t["code"] in BODY_CODES)
            if s.route1 and t["code"] == "body":
                save(pp.app, make_app(tpls[t["tpl"]], t, pp.resource, f"inkflow_{slug}", f"w__{slug}", mask))
                expected.append(pp.app)
            for n_ in slots:
                save(pp.slot_app(n_), make_app(tpls[t["tpl"]], t, pp.resource, f"inkflow_slot{n_}_{slug}{t['suffix']}", f"w__{slug}{t['suffix']}", mask))
                expected.append(pp.slot_app(n_))
            parts.append(f"{t['code']}{' (UV)' if fam == 'uv' else ''}{' strip cleared' if t['code'] in it.blanked else ''}"
                         f"{' converted to ' + it.conv[t['code']] if t['code'] in it.conv else ''} {nv} vertices / {nm} mat."
                         + (f" / {nt} morphs" if nt else "") + (f" / mask {mask}" if mask else ""))
        if s.fpp:
            for t in it.targets:
                for f in FPP_BY_PARENT.get(t["code"], []):
                    if f["code"] in it.no_fpp:
                        continue
                    fam = it.family(t)
                    pt, pf = Paths(slug, t, fam), Paths(slug, f)
                    pt.tex = it.texpath[t["code"]]      # the parent's texture : as copied, cleared strip or converted arm
                    if t["code"] in it.blanked:
                        fam = "vtk"                 # the strip is cleared in the texture : no strip mask needed
                    # The mask the game applies to this companion's mesh in first person (`fpp_app_mask`) when it was
                    # read ; the template's full mask otherwise (the arms : the whole FPP arm mesh).
                    read = f["code"] in fpp_masks
                    base = int(fpp_masks[f["code"]]) if read else TEMPLATE_MASK
                    if f["mesh"]:
                        mesh, nm, nv = shell(meshes[f["code"]], pt.tex, alpha, f"[{slug}] {f['code']}")
                        save(pf.mesh, mesh)
                        expected.append(pf.mesh)
                        resource = pf.mesh
                        mask = shell_mask(layouts, f["code"], fam, f.get("is_body", False), base) or (str(base) if read else None)
                        parts.append(f"{f['code']} {nv} vertices / {nm} mat." + (f" / mask {mask}" if mask else ""))
                    else:
                        resource = pt.mesh
                        mask = shell_mask(layouts, t["code"], fam, True, base) or (str(base) if read else None)
                        parts.append(f"{f['code']} = body shell, mask {mask}")
                    for n_ in slots:
                        save(pf.slot_app(n_), make_app(tpls[f["tpl"]], f, resource, f"inkflow_slot{n_}_{slug}{f['suffix']}", f"w__{slug}{f['suffix']}", mask))
                        expected.append(pf.slot_app(n_))
        log(f"  [{slug}] \"{it.name}\" (opacity {alpha:g}): " + " ; ".join(parts))

    tpl_cc = load(os.path.join(tdir, "your_tattoo_pwa.inkcharcustomization.json"))
    opts = tpl_cc["Data"]["RootChunk"]["bodyCustomizationOptions"]
    tk_switcher = next(h["Data"] for h in opts if h["Data"]["$type"] == "gameuiSwitcherInfo")
    tk_off = next(h["Data"] for h in opts if h["Data"]["name"]["$value"] == "chest_tattoo_off")
    tk_info = next(h["Data"] for h in opts if h["Data"]["name"]["$value"] == "your_chest_tattoo")
    tags = ["NewGame", "HairDresser", "Ripperdoc"] if s.mirror else ["NewGame", "Ripperdoc"]

    def option(index, loc, names):
        o = copy.deepcopy(tk_switcher["options"][1])
        o["index"] = index
        o["localizedName"] = loc
        o["names"] = [cname(x) for x in names]
        return o

    def info(name, ui_slot, resource, definition):
        d = copy.deepcopy(tk_info)
        set_cname(d, "name", name)
        set_cname(d, "uiSlot", ui_slot)
        d["resource"] = respath(resource)
        set_cname(d["definitions"][0], "name", definition)
        d["editTags"] = list(tags)
        return d

    def off(name, ui_slot):
        d = copy.deepcopy(tk_off)
        set_cname(d, "name", name)
        set_cname(d, "uiSlot", ui_slot)
        d["editTags"] = list(tags)
        return d

    loc_entries = []
    for it in items:
        loc_entries.append((f"UI-Customization-inkflow_{it.slug}", it.name))
        if s.route1:
            loc_entries.append((f"UI-Customization-inkflow_{it.slug}_v", f"{it.name} (Ink Flow)"))
    for n_ in slots:
        loc_entries.append((f"UI-Customization-inkflow_slot{n_}", s.slot_title.replace("{n}", str(n_))))

    customizations = []      # (ArchiveXL key, path) : one .inkcharcustomization per gender that has tattoos
    for gender, key, tag in GENDERS:
        g_items = [it for it in items if any(t["gender"] == gender for t in it.targets)]
        if g_items:
            inkcc = rf"{P}\inkflow_{tag}.inkcharcustomization"
            save(inkcc, gender_customization(s, tpl_cc, tk_switcher, gender, g_items, slots, tags, option, info, off))
            expected.append(inkcc)
            customizations.append((key, inkcc))

    loc = load(os.path.join(tdir, "localization.json.json"))
    lentries = loc["Data"]["RootChunk"]["root"]["Data"]["entries"]
    tpl = copy.deepcopy(lentries[0])
    lentries.clear()
    for key, text in loc_entries:
        e = copy.deepcopy(tpl)
        e["secondaryKey"] = key
        e["femaleVariant"] = text
        e["maleVariant"] = text
        lentries.append(e)
    locp = rf"{P}\localization\inkflow_en-us.json"
    save(locp, loc)
    expected.append(locp)

    cli.run("convert", "deserialize", src, what=f"deserialize ({len(expected)} files)")
    missing = [p for p in expected if not os.path.isfile(os.path.join(src, p))]
    if missing:
        raise BuildError("files not produced by the CLI: " + ", ".join(missing))
    for d, _, files in os.walk(src):
        for f in files:
            if f.endswith(".json") and not f.endswith("inkflow_en-us.json"):
                os.remove(os.path.join(d, f))
    if os.path.isfile(os.path.join(src, locp + ".json")):
        os.remove(os.path.join(src, locp + ".json"))

    xl = os.path.join(s.out, s.name + ".archive.xl")
    with open(xl, "w", encoding="utf-8", newline="\n") as f:
        f.write("customizations:\n")
        for key, path in customizations:
            f.write(f"  {key}: {path}\n")
        f.write("localization:\n  onscreens:\n")
        f.write(f"    en-us: {locp}\n")
    arc = os.path.join(s.out, s.name + ".archive")
    if os.path.isfile(arc):
        os.remove(arc)
    cli.run("pack", src, "-o", s.out, what="pack")
    if not os.path.isfile(arc):
        raise BuildError("archive not produced by the CLI")
    listing = [l for l in cli.run("archive", arc, "-l", what="list").splitlines() if "\\" in l]
    return arc, xl, listing


def run_build(s, entries, catalogue, log, progress=None, cancel=None):
    """Whole build : entries (supported, selected) -> BuildResult. `progress(step, total, text)` is optional ;
    `cancel` (threading.Event) set = Cancelled at the next step or CLI poll. The cache stays valid (each marker is
    written after its extraction), a half-written archive in the output folder is removed."""
    t0 = time.time()
    items = [e for e in entries if e.supported]
    if not items:
        raise BuildError("no supported tattoo selected: nothing to build")
    if s.slots < 1:
        raise BuildError("at least one slot is needed")
    if not os.path.isdir(s.game):
        raise BuildError("game folder not found: " + s.game)
    catalogue.ensure(items)
    cli = Cli(s.cli, log, cancel)
    total = 3 + len(items)

    def step(i, text):
        if cancel is not None and cancel.is_set():
            raise Cancelled()
        if progress:
            progress(i, total, text)

    step(0, "Checking tattoos")
    log("1. tattoos")
    built = []
    names_seen = {}
    for e in items:
        label, cut = option_label(catalogue.name(e), s.max_name)
        if cut:
            log(f"  ! name too long ({len(catalogue.name(e))} > {s.max_name}), cut: \"{catalogue.name(e)}\" -> \"{label}\"")
        names_seen.setdefault(label, []).append(e.file)
        a = catalogue.alpha(e)
        log(f"  + {e.file}  ->  {catalogue.slug(e)}, \"{label}\": {e.targets_label}"
            + (f", opacity {a:g}" if a is not None else "")
            + (f"  (ignored: {e.ignored_reason})" if e.other or e.unknown else ""))
        built.append(Item(e, catalogue.slug(e), label, alpha=a))
    dup = {n: f for n, f in names_seen.items() if len(f) > 1}
    if dup:
        log("  ! duplicate labels (rename them): " + "; ".join(f"\"{n}\" = {', '.join(f)}" for n, f in dup.items()))

    step(1, "Extracting the active body meshes")
    log("2. active meshes")
    needed = [t for t in TARGETS if any(t in it.targets for it in built)]
    active = {t["code"]: extract_mesh(cli, s.game, s.work, t, log) for t in needed}
    # UV layouts (ETUDE § 21) : arm targets whose texture family does not match the active arm mesh are skipped
    layouts = {c: mesh_layout(m) for c, (m, _) in active.items()}
    for c, lay in layouts.items():
        log(f"  {TARGET_BY_CODE[c]['label']:6s}: {'UV' if lay['arms'] == 'strip' else 'vanilla / VTK'} layout "
            f"(u max {lay['u_max']:.2f}, {lay['strip_share']:.0%} of the skin in the UV strip)"
            + (f", non-skin chunks hidden in the shells: {', '.join(lay['hidden'])}" if lay["hidden"] else "")
            + (f", chunks in the strip (hidden under a UV texture): {lay['strip_chunks']}" if lay["strip_chunks"] and c in BODY_CODES else ""))
    refs = {}                                   # arm code -> (vanilla json, strip json, owner) | BuildError (reason)
    for it in built:
        keep = []
        for t in it.targets:
            fam = it.family(t)
            arms = layouts.get(t["code"], {}).get("arms")
            if t["code"] in ARM_CODES and arms != ("strip" if fam == "uv" else "full"):
                # The other arm layout : the texture is converted to the active one (ETUDE § 22) when the game has
                # the UV Framework's arm mesh to pair with the vanilla arm, else the arm is skipped.
                if t["code"] not in refs:
                    try:
                        refs[t["code"]] = arm_refs(cli, s.game, s.work, t, log)
                    except BuildError as e:
                        refs[t["code"]] = e
                        log(f"  ! {t['label']}: no arm conversion possible: {e}")
                if isinstance(refs[t["code"]], BuildError):
                    it.skipped.append(f"{t['label']}: {'UV' if fam == 'uv' else 'VTK'} tattoo on "
                                      f"{'UV Framework' if fam != 'uv' else 'vanilla / VTK'} arms (other layout, "
                                      f"{refs[t['code']]})")
                    continue
                it.conv[t["code"]] = arms
            keep.append(t)
        it.targets = keep
        if it.skipped:
            log(f"  ! [{it.slug}] skipped: " + " ; ".join(it.skipped) + ("" if keep else " : nothing left, tattoo left out"))
    built = [it for it in built if it.targets]
    if not built:
        raise BuildError("no tattoo left to build: every target was skipped (see the arm layouts above)")
    needed = [t for t in TARGETS if any(t in it.targets for it in built)]
    fpp_masks = {}                              # FPP companion code -> chunk mask read in its FPP appearance
    if s.fpp:
        log("2b. first person")
        for f in FPP_TARGETS:
            if TARGET_BY_CODE[f["parent"]] not in needed:
                continue
            if f["mesh"]:
                active[f["code"]] = extract_mesh(cli, s.game, s.work, f, log)
                layouts[f["code"]] = lay = mesh_layout(active[f["code"]][0])
                log(f"  {f['label']:9s}: {'UV' if lay['arms'] == 'strip' else 'vanilla / VTK'} layout (u max {lay['u_max']:.2f})"
                    + (f", non-skin chunks hidden: {', '.join(lay['hidden'])}" if lay["hidden"] else "")
                    + (f", chunks in the strip (hidden under a UV texture): {lay['strip_chunks']}" if lay["strip_chunks"] and f.get("is_body") else ""))
                if f["parent"] in ARM_CODES:
                    for it in built:
                        fam = it.entry.family.get(f["parent"], "vtk")
                        want = it.conv.get(f["parent"]) or ("strip" if fam == "uv" else "full")   # a converted arm : its new layout
                        if TARGET_BY_CODE[f["parent"]] in it.targets and lay["arms"] != want:
                            it.no_fpp.add(f["code"])
                            log(f"  ! [{it.slug}] {f['label']} skipped: first-person arms have the other layout")
            if f.get("app"):
                fpp_masks[f["code"]] = fpp_app_mask(cli, s.game, s.work, f, log)

    log("3. textures")
    for i, it in enumerate(built):
        step(2 + i, f"Extracting texture {i + 1}/{len(built)}: {it.name}")
        it.texdir = extract_textures(cli, s.game, it.entry.path, it.slug, s.work, log)
        if it.conv:
            step(2 + i, f"Converting arm textures {i + 1}/{len(built)}: {it.name}")
            for code in converted_textures(cli, s, it, refs, log):
                it.skipped.append(f"{TARGET_BY_CODE[code]['label']}: no ink on this arm")
                it.targets = [t for t in it.targets if t["code"] != code]
                del it.conv[code]
    empty = [it for it in built if not it.targets]
    for it in empty:
        log(f"  ! [{it.slug}] nothing left to build, tattoo left out")
    built = [it for it in built if it.targets]
    if not built:
        raise BuildError("no tattoo left to build: every target was skipped")

    step(2 + len(built), "Building the archive")
    log("4. build")
    try:
        arc, xl, listing = build_archive(s, cli, built, active, log, fpp_masks, layouts)
    except Cancelled:
        for p in (os.path.join(s.out, s.name + ".archive"), os.path.join(s.out, s.name + ".archive.xl")):
            if os.path.isfile(p):
                os.remove(p)
        raise
    catalogue.save()
    size = os.path.getsize(arc)
    log(f"\nDONE in {time.time() - t0:.0f} s: {arc} ({size / 1e6:.1f} MB, {len(listing)} files) + {os.path.basename(xl)}")
    log(f"  {len(built)} tattoo(s), {s.slots} slot(s), mirror {'on' if s.mirror else 'off'}, first person {'on' if s.fpp else 'off'}")
    for it in built:
        log(f"    {it.slug:40s} \"{it.name}\"  [{', '.join(t['code'] + ('/uv' if it.family(t) == 'uv' else '') for t in it.targets)}]"
            + (f"  opacity {it.alpha:g}" if it.alpha is not None else "") + (f"  skipped: {' ; '.join(it.skipped)}" if it.skipped else ""))
    step(total, "Done")
    return BuildResult(arc, xl, listing, built, time.time() - t0, size)


# ----------------------------------------------------------------------------- 5. the player's game
def is_pure_tattoo(archive):
    """PURE VTK tattoo archive : every entry is a known overlay / roughness texture and at least one is a target.
    Body mods such as Angel also ship `v_overlay.xbm`, with 100+ other files : they are NOT pure."""
    hs = rdar.index(archive)
    return bool(hs) and hs <= set(HASH_PATH) and bool(hs & TARGET_HASHES)


def find_tattoo_archives(game):
    """The pure VTK tattoo archives the game currently loads (`archive\\pc\\mod` and REDmod), in load order :
    (label, full path). What the "Scan game folder" button imports. ~0.4 s for 600 archives (index only)."""
    out = []
    for label, full in game_archives(game):
        if os.path.basename(full) in CANARI:
            continue
        try:
            if is_pure_tattoo(full):
                out.append((label, full))
        except (ValueError, OSError):
            continue
    return out


def conflicting_archives(game, selected=(), exclude_names=()):
    """VTK tattoo archives still loaded by the game (`archive\\pc\\mod` and REDmod) : they paint a permanent overlay
    in the skin, under Ink Flow's layers. Two criteria, both by content (never by file name) :
      - PURE tattoo archive (`is_pure_tattoo`) ;
      - same content as one of the `selected` inputs (size, then SHA-256) : a copy imported by "Scan game folder".
    Returns labels = paths relative to the game folder, in load order (what `install(move_conflicts)` takes)."""
    by_size = {}
    for e in selected:
        try:
            by_size.setdefault(os.path.getsize(e.path), []).append(e.id)
        except OSError:
            continue
    out = []
    for label, full in game_archives(game):
        name = os.path.basename(full)
        if name in exclude_names or name in CANARI:
            continue
        try:
            if is_pure_tattoo(full):
                out.append(label)
            elif os.path.getsize(full) in by_size and rdar.content_id(full) in by_size[os.path.getsize(full)]:
                out.append(label)
        except (ValueError, OSError):
            continue
    return out


def game_running():
    """True when Cyberpunk2077.exe is running (Windows only)."""
    if os.name != "nt":
        return False
    try:
        r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Cyberpunk2077.exe", "/NH"], capture_output=True, text=True,
                           timeout=15, creationflags=NO_WINDOW)
        return "Cyberpunk2077.exe" in r.stdout
    except (OSError, subprocess.TimeoutExpired):
        return False


def install(result, game, backup_dir, log, move_conflicts=()):
    """Copy the archive + .xl into `archive\\pc\\mod`. Anything replaced, and the conflicting archives asked for
    (labels relative to the game folder, from `conflicting_archives`), go to `backup_dir\\<timestamp>\\<same relative
    path>`. Returns the backup folder (or None if nothing was backed up)."""
    mod = mod_dir(game)
    if not os.path.isdir(mod):
        raise BuildError("game mod folder not found: " + mod)
    if game_running():
        raise BuildError("Cyberpunk 2077 is running: close the game first")
    stamp_dir = os.path.join(backup_dir, time.strftime("%Y-%m-%d_%H%M%S"))
    backed = False

    def backup(rel):
        nonlocal backed
        p = os.path.join(game, rel)
        if os.path.isfile(p):
            dst = os.path.join(stamp_dir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(p, dst)
            backed = True
            log(f"  moved to backup: {rel}")

    for src in (result.archive, result.xl):
        backup(LEGACY_DIR + "\\" + os.path.basename(src))
    for name in CANARI:
        backup(LEGACY_DIR + "\\" + name)
    for rel in move_conflicts:
        backup(rel)
    for src in (result.archive, result.xl):
        shutil.copy2(src, os.path.join(mod, os.path.basename(src)))
        log(f"  installed: {os.path.basename(src)}")
    return stamp_dir if backed else None
