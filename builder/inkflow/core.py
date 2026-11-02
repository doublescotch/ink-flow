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
    `fpp_body_tattoo` -> `body_tattoo` pattern) drives FPP shells : the body shell again, shown through the chunk mask
    of the active FPP torso, and copies of the active FPP arm meshes ; listed in the `FPP_Body` group only ;
  - names shown in game come from the Catalogue (player-editable `name`, immutable `slug`) ;
  - nothing is written to the game by the engine ; `install()` does it on demand.

Differences with the v0.3 script : no `sys.exit` (BuildError), no `print` (log callback), templates resolved from the
PyInstaller bundle when frozen, catalogue keyed by CONTENT id (SHA-256) so a renamed file keeps its slug and the
player's saved character keeps its tattoos.
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field

from . import rdar

P = "inkflow"                                   # path prefix of everything the mod ships
MESH_APPEARANCE = "01_ca_pale"
BODY_DIR = r"base\characters\common\player_base_bodies\player_female_average"
BASEGAME = r"archive\pc\content\basegame_4_appearance.archive"
DECAL_MI = (r"base\characters\common\skin\character_mat_instance\__parameters\customization__parameters"
            r"\tattoos__parameters\customization_tattoos_01_ca_pale.mi")
ARMS_TEX = r"base\characters\player\femme\body\arms\textures"
HEAD_DIR = r"base\characters\head\player_base_heads\player_female_average"
FPP_DIR = BODY_DIR + r"\fpp"
FPP_APP = r"base\characters\common\player_base_bodies\appearances\l0_000_fpp__full.app"
FPP_TORSO_MESH = FPP_DIR + r"\t0_000_pwa_fpp__torso.mesh"
FPP_TORSO_MASK = "18446744073709551584"     # 0xFFFFFFFFFFFFFFE0 : body chunks 5-7, what the vanilla/Angel FPP app shows (measured 2026-11-01)
FPP_INDEX_OFFSET = 25                       # follower switchers at 1066-1074 : free in vanilla (1065 = last body_scars entry, 1090 = genitals)

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
]
TARGET_BY_CODE = {t["code"]: t for t in TARGETS}
# First person (ETUDE § 16). What V sees of herself in first person : the FPP torso, a byte-identical copy of the TPP
# body mesh shown through a chunk mask (so the body shell is reused, masked the same way), and two dedicated FPP arm
# meshes (copied as decals like the TPP arms). The head is never seen in first person. `parent` = the target whose
# texture (and, for the body, whose shell) the companion uses.
FPP_TARGETS = [
    dict(code="fpp_body", label="FPP body", parent="body", mesh=None, morph=None,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_left", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_left_pwa.mesh", suffix="_fpp"),
    dict(code="fpp_arm_l", label="FPP arm L", parent="arm_l", mesh=FPP_DIR + r"\a0_000_pwa_fpp__full_l.mesh", morph=None,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_left", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_left_pwa.mesh", suffix="_fpp_arm_l"),
    dict(code="fpp_arm_r", label="FPP arm R", parent="arm_r", mesh=FPP_DIR + r"\a0_000_pwa_fpp__full_r.mesh", morph=None,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_right", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_right_pwa.mesh", suffix="_fpp_arm_r"),
]
FPP_BY_PARENT = {t["parent"]: t for t in FPP_TARGETS}
TARGET_BY_TEX = {t["tex"]: t for t in TARGETS}
KNOWN_OTHER = {
    r"base\4k\common\overlays\fullbody_overlay_d01.xbm": "UV body+arms (not supported yet)",
    r"base\v_textures\body\v_body_rm.xbm": "VTK skin roughness (not a tattoo)",
    ARMS_TEX + r"\femme_arm_left_01_roughnessmask.xbm": "VTK arm L roughness",
    ARMS_TEX + r"\femme_arm_right_01_roughnessmask.xbm": "VTK arm R roughness",
}
HASH_PATH = {rdar.fnv1a64(p): p for p in list(TARGET_BY_TEX) + list(KNOWN_OTHER)}
TARGET_HASHES = {rdar.fnv1a64(t["tex"]) for t in TARGETS}
TEX_REGEX = "(" + "|".join(re.escape(os.path.basename(t["tex"])) for t in TARGETS) + r"|\d+\.bin)$"
NAME_PREFIX = re.compile(r"^\d+_Tattoos?_(VTK|UV)_", re.I)
LEGACY_TABLE = "inkflow_slugs.json"             # v0.1-v0.3 catalogue, next to the archives : imported once
CANARI = ("Ink_Flow_Canari.archive", "Ink_Flow_Canari.archive.xl")


class BuildError(Exception):
    """Anything that stops a build, with a message meant for the player."""


class Cancelled(Exception):
    """The player pressed Cancel. Not a BuildError : no fallback (`fpp_torso_mask`) may swallow it."""


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

    @property
    def supported(self):
        return bool(self.targets)

    @property
    def target_codes(self):
        return [t["code"] for t in self.targets]

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
        out.append(Entry(path=p, file=os.path.basename(p), stem=os.path.splitext(os.path.basename(p))[0],
                         id=rdar.content_id(p),
                         targets=[t for t in TARGETS if t["tex"] in found],
                         other=sorted(KNOWN_OTHER[x] for x in found if x in KNOWN_OTHER),
                         unknown=len([h for h in hs if h not in HASH_PATH])))
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
    if t["morph"] and rdar.fnv1a64(t["morph"]) not in rdar.index(src):
        raise BuildError(f"the morphtarget of {t['code']} ({t['morph']}) is not in the same archive as the mesh ({src}): unsupported layout")
    d = os.path.join(work, "mesh", t["code"])
    marker = os.path.join(d, ".src")
    key = stamp(src) + "|" + src.lower() + "|" + t["mesh"]
    mesh_json = os.path.join(d, t["mesh"] + ".json")
    morph_json = os.path.join(d, t["morph"] + ".json") if t["morph"] else None
    if cached(marker, key) and os.path.isfile(mesh_json) and (not morph_json or os.path.isfile(morph_json)):
        return mesh_json, morph_json
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    wanted = [t["mesh"]] + ([t["morph"]] if t["morph"] else [])
    rx = "(" + "|".join(re.escape("\\" + os.path.basename(p)) for p in wanted) + ")$"
    cli.run("unbundle", src, "-o", d, "-r", rx, what=f"unbundle {t['code']}")
    common = os.path.commonpath([os.path.join(d, os.path.dirname(p)) for p in wanted])
    cli.run("convert", "serialize", common, what=f"serialize {t['code']}")
    for p in (mesh_json, morph_json):
        if p and not os.path.isfile(p):
            raise BuildError("expected file missing after extraction: " + p)
    with open(marker, "w") as f:
        f.write(key)
    return mesh_json, morph_json


def fpp_torso_mask(cli, game, work, log):
    """Chunk mask of the FPP torso in the active FPP body .app : what the game shows of the body mesh in first person.
    The FPP body shell gets the same mask. Cached on the source archive ; the measured vanilla/Angel value is the
    fallback (the app may live elsewhere than the mesh, or not be readable)."""
    src, owners = find_owner(game, FPP_APP)
    who = who_ships(owners)
    try:
        if not os.path.isfile(src) or rdar.fnv1a64(FPP_APP) not in rdar.index(src):
            log(f"  FPP app: not found ({who}), default mask {FPP_TORSO_MASK}")
            return FPP_TORSO_MASK
        d = os.path.join(work, "mesh", "fpp_app")
        marker = os.path.join(d, ".src")
        key = stamp(src) + "|" + src.lower() + "|" + FPP_APP
        app_json = os.path.join(d, FPP_APP + ".json")
        if not (cached(marker, key) and os.path.isfile(app_json)):
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d)
            cli.run("unbundle", src, "-o", d, "-r", re.escape("\\" + os.path.basename(FPP_APP)) + "$", what="unbundle fpp app")
            cli.run("convert", "serialize", os.path.join(d, os.path.dirname(FPP_APP)), what="serialize fpp app")
            if not os.path.isfile(app_json):
                raise BuildError("expected file missing after extraction: " + app_json)
            with open(marker, "w") as f:
                f.write(key)
        for a in load(app_json)["Data"]["RootChunk"]["appearances"]:
            for c in a["Data"]["components"]:
                mesh = ((c.get("mesh") or {}).get("DepotPath") or {}).get("$value") or ""
                if mesh.lower() == FPP_TORSO_MESH.lower() and c.get("chunkMask") is not None:
                    log(f"  FPP app: {who}, torso mask {c['chunkMask']}")
                    return c["chunkMask"]
        log(f"  ! FPP app: {who}, no torso component: default mask {FPP_TORSO_MASK}")
    except (BuildError, OSError, ValueError, KeyError, TypeError) as e:
        log(f"  ! FPP app: {who}, not readable ({e}): default mask {FPP_TORSO_MASK}")
    return FPP_TORSO_MASK


# ----------------------------------------------------------------------------- 3. textures
def extract_textures(cli, archive, slug, work, log):
    """All target textures of one tattoo archive -> work\\tex\\<slug>\\<game path> (cached)."""
    d = os.path.join(work, "tex", slug)
    marker = os.path.join(d, ".src")
    key = stamp(archive) + "|" + TEX_REGEX
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
        with open(marker, "w") as f:
            f.write(key)
    return d


# ----------------------------------------------------------------------------- 4. construction
class Paths:
    def __init__(self, slug, t):
        d = rf"{P}\tattoos\{slug}"
        s = t["suffix"]
        self.tex = rf"{d}\{slug}{s}.xbm"
        self.mesh = rf"{d}\{slug}_pwa{s}.mesh"
        self.morph = rf"{d}\{slug}_pwa{s}.morphtarget"
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

    @property
    def targets(self):
        return self.entry.targets


@dataclass
class BuildResult:
    archive: str
    xl: str
    listing: list
    items: list
    seconds: float
    size: int


def build_archive(s, cli, items, active, log, fpp_mask=None):
    """items: list of Item ; active: target code -> (mesh json, morph json) ; fpp_mask: chunk mask of the FPP body shell
    (`fpp_torso_mask`, when `s.fpp`). -> (archive, xl, listing)."""
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
        parts = []
        for t in it.targets:
            pp = Paths(slug, t)
            src_tex = os.path.join(it.texdir, t["tex"])
            if not os.path.isfile(src_tex):
                raise BuildError("texture missing after extraction: " + src_tex)
            dst = os.path.join(src, pp.tex)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src_tex, dst)
            mesh, nm, nv = shell(meshes[t["code"]], pp.tex, s.alpha, f"[{slug}] {t['code']}")
            save(pp.mesh, mesh)
            expected.append(pp.mesh)
            nt = 0
            if t["morph"]:
                morph, nt = retarget_morph(morphs[t["code"]], t, pp.mesh)
                save(pp.morph, morph)
                expected.append(pp.morph)
            if s.route1 and t["code"] == "body":
                save(pp.app, make_app(tpls[t["tpl"]], t, pp.resource, f"inkflow_{slug}", f"w__{slug}"))
                expected.append(pp.app)
            for n_ in slots:
                save(pp.slot_app(n_), make_app(tpls[t["tpl"]], t, pp.resource, f"inkflow_slot{n_}_{slug}{t['suffix']}", f"w__{slug}{t['suffix']}"))
                expected.append(pp.slot_app(n_))
            parts.append(f"{t['code']} {nv} vertices / {nm} mat." + (f" / {nt} morphs" if nt else ""))
        if s.fpp:
            for t in it.targets:
                f = FPP_BY_PARENT.get(t["code"])
                if not f:
                    continue
                pt, pf = Paths(slug, t), Paths(slug, f)
                if f["mesh"]:
                    mesh, nm, nv = shell(meshes[f["code"]], pt.tex, s.alpha, f"[{slug}] {f['code']}")
                    save(pf.mesh, mesh)
                    expected.append(pf.mesh)
                    resource, mask = pf.mesh, None
                    parts.append(f"{f['code']} {nv} vertices / {nm} mat.")
                else:
                    resource, mask = pt.mesh, fpp_mask
                    parts.append(f"{f['code']} = body shell, mask {mask}")
                for n_ in slots:
                    save(pf.slot_app(n_), make_app(tpls[f["tpl"]], f, resource, f"inkflow_slot{n_}_{slug}{f['suffix']}", f"w__{slug}{f['suffix']}", mask))
                    expected.append(pf.slot_app(n_))
        log(f"  [{slug}] \"{it.name}\": " + " ; ".join(parts))

    cc = load(os.path.join(tdir, "your_tattoo_pwa.inkcharcustomization.json"))
    root = cc["Data"]["RootChunk"]
    opts = root["bodyCustomizationOptions"]
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

    entries, names_all, names_fpp, loc_entries = [], [], [], []
    for it in items:
        loc_entries.append((f"UI-Customization-inkflow_{it.slug}", it.name))
        if s.route1:
            loc_entries.append((f"UI-Customization-inkflow_{it.slug}_v", f"{it.name} (Ink Flow)"))
    body_t = TARGETS[0]

    with_body = [it for it in items if body_t in it.targets]
    if s.route1 and with_body:
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
        ui = {t["code"]: f"inkflow_slot{n_}{t['suffix']}" for t in TARGETS}
        off_name = {t["code"]: f"inkflow_slot{n_}_off{t['suffix']}" for t in TARGETS}
        s2 = copy.deepcopy(tk_switcher)
        set_cname(s2, "name", f"inkflow_slot{n_}")
        s2["index"] = s.slot_index + n_ - 1
        s2["localizedName"] = f"UI-Customization-inkflow_slot{n_}"
        set_cname(s2, "uiSlot", f"inkflow_slot{n_}_switcher")
        s2["editTags"] = list(tags)
        s2["uiSlots"] = [cname(ui[t["code"]]) for t in TARGETS]
        s2["options"] = [copy.deepcopy(tk_switcher["options"][0])]
        s2["options"][0]["names"] = [cname(off_name[t["code"]]) for t in TARGETS]
        offs = [off(off_name[t["code"]], ui[t["code"]]) for t in TARGETS]
        infos = []
        for i, it in enumerate(items, 1):
            names = []
            for t in TARGETS:
                if t in it.targets:
                    nm = f"inkflow_slot{n_}_{it.slug}{t['suffix']}"
                    infos.append(info(nm, ui[t["code"]], Paths(it.slug, t).slot_app(n_), f"w__{it.slug}{t['suffix']}"))
                    names.append(nm)
                else:
                    names.append(off_name[t["code"]])
            s2["options"].append(option(i, f"UI-Customization-inkflow_{it.slug}", names))
        entries += [s2] + offs + infos
        names_all += [f"inkflow_slot{n_}"] + [o["name"]["$value"] for o in offs] + [x["name"]["$value"] for x in infos]
        loc_entries.append((f"UI-Customization-inkflow_slot{n_}", s.slot_title.replace("{n}", str(n_))))
        if s.fpp:
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
                    if TARGET_BY_CODE[f["parent"]] in it.targets:
                        nm = f"inkflow_slot{n_}_{it.slug}{f['suffix']}"
                        finfos.append(info(nm, fui[f["code"]], Paths(it.slug, f).slot_app(n_), f"w__{it.slug}{f['suffix']}"))
                        names.append(nm)
                    else:
                        names.append(foff[f["code"]])
                s3["options"].append(option(i, f"UI-Customization-inkflow_{it.slug}", names))
            entries += [s3] + foffs + finfos
            names_fpp += [f"inkflow_slot{n_}_fpp"] + [o["name"]["$value"] for o in foffs] + [x["name"]["$value"] for x in finfos]

    root["bodyCustomizationOptions"] = [{"HandleId": str(i), "Data": d} for i, d in enumerate(entries)]
    for g in root["bodyGroups"]:
        fpp_group = s.fpp and g["name"]["$value"] == "FPP_Body"
        g["options"] = [cname(x) for x in (names_fpp if fpp_group else names_all)]
    inkcc = rf"{P}\inkflow_pwa.inkcharcustomization"
    save(inkcc, cc)
    expected.append(inkcc)

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
        f.write(f"  female: {inkcc}\n")
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
        log(f"  + {e.file}  ->  {catalogue.slug(e)}, \"{label}\": {' + '.join(t['label'] for t in e.targets)}"
            + (f"  (ignored: {e.ignored_reason})" if e.other or e.unknown else ""))
        built.append(Item(e, catalogue.slug(e), label))
    dup = {n: f for n, f in names_seen.items() if len(f) > 1}
    if dup:
        log("  ! duplicate labels (rename them): " + "; ".join(f"\"{n}\" = {', '.join(f)}" for n, f in dup.items()))

    step(1, "Extracting the active body meshes")
    log("2. active meshes")
    needed = [t for t in TARGETS if any(t in it.targets for it in built)]
    active = {t["code"]: extract_mesh(cli, s.game, s.work, t, log) for t in needed}
    fpp_mask = None
    if s.fpp:
        log("2b. first person")
        for f in FPP_TARGETS:
            if f["mesh"] and TARGET_BY_CODE[f["parent"]] in needed:
                active[f["code"]] = extract_mesh(cli, s.game, s.work, f, log)
        if TARGET_BY_CODE["body"] in needed:
            fpp_mask = fpp_torso_mask(cli, s.game, s.work, log)

    log("3. textures")
    for i, it in enumerate(built):
        step(2 + i, f"Extracting texture {i + 1}/{len(built)}: {it.name}")
        it.texdir = extract_textures(cli, it.entry.path, it.slug, s.work, log)

    step(2 + len(built), "Building the archive")
    log("4. build")
    try:
        arc, xl, listing = build_archive(s, cli, built, active, log, fpp_mask)
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
        log(f"    {it.slug:40s} \"{it.name}\"  [{', '.join(it.entry.target_codes)}]")
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
