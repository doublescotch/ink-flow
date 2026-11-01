"""Ink Flow engine (v0.4, 2026-11-01) : the generator of `tools/inkflow_build.py` v0.3 turned into a library.

Same recipe, same output (ETUDE § 8-13) :
  - every tattoo .archive chosen by the player is indexed (RDAR, no WolvenKit) and its TARGETS recognised by the files
    it replaces (body `v_overlay.xbm`, arms `femme_arm_left|right_01_overlay.xbm`, head `h0_001_pwa_c__basehead_overlay.xbm`) ;
  - for every target the ACTIVE mesh of the player (first archive of `archive\\pc\\mod` that ships it, else the base
    game) is extracted and serialised with WolvenKit CLI (cached) ;
  - per tattoo and target : the texture copied byte for byte, a shell = COPY OF THE ACTIVE MESH whose skin materials
    become the vanilla tattoo decal material, the mesh morphtarget (body, head) re-pointed to the shell, one .app per
    (slot, tattoo, target) ;
  - N switchers (route 2, Heterochromia pattern : one option drives one uiSlot per target), options Off + one per
    tattoo ; route 1 (an option in the vanilla « Body Tattoos » switcher) is off by default ;
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
    def __init__(self, exe, log):
        if not exe or not os.path.isfile(exe):
            raise BuildError("WolvenKit CLI not found: " + str(exe))
        self.exe = exe
        self.log = log

    def run(self, *args, what=""):
        t = time.time()
        try:
            r = subprocess.run([self.exe, *args], capture_output=True, text=True, creationflags=NO_WINDOW)
        except OSError as e:
            raise BuildError(f"cannot start WolvenKit CLI: {e}") from e
        ok = r.returncode == 0 and "Error" not in r.stdout
        self.log(f"  cli {what or args[0]}: {'OK' if ok else 'FAILED'} ({time.time() - t:.1f} s)")
        if not ok:
            raise BuildError(f"WolvenKit CLI failed ({what or args[0]}, exit {r.returncode}):\n"
                             + r.stdout[-3000:] + r.stderr[-2000:])
        return r.stdout

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
def mod_dir(game):
    return os.path.join(game, r"archive\pc\mod")


def find_owner(game, path):
    mod = mod_dir(game)
    owners = rdar.owners(mod, path) if os.path.isdir(mod) else []
    if owners:
        return os.path.join(mod, owners[0]), owners
    return os.path.join(game, BASEGAME), []


def active_owners(game, codes):
    """code -> (owner label, list of archives shipping the mesh). For the UI and the log."""
    out = {}
    for c in codes:
        t = TARGET_BY_CODE[c]
        _, owners = find_owner(game, t["mesh"])
        who = owners[0] + (f" (over {', '.join(owners[1:])})" if len(owners) > 1 else "") if owners else "base game"
        out[c] = (who, owners)
    return out


def extract_mesh(cli, game, work, t, log):
    """Active mesh of a target (+ morphtarget) : extracted and serialised to JSON, cached on the source archive."""
    src, owners = find_owner(game, t["mesh"])
    who = owners[0] + (f" (over {', '.join(owners[1:])})" if len(owners) > 1 else "") if owners else "base game"
    log(f"  {t['label']:6s}: {who}")
    if not os.path.isfile(src):
        raise BuildError("base game archive not found: " + src)
    if t["morph"] and rdar.fnv1a64(t["morph"]) not in rdar.hashes(src):
        raise BuildError(f"the morphtarget of {t['code']} ({t['morph']}) is not in the same archive as the mesh ({src}): unsupported layout")
    d = os.path.join(work, "mesh", t["code"])
    marker = os.path.join(d, ".src")
    key = stamp(src) + "|" + t["mesh"]
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


def shell(active, tex, alpha, what):
    """Shell = copy of the active mesh whose every skin material becomes the decal (canary v5)."""
    mesh = copy.deepcopy(active)
    root = mesh["Data"]["RootChunk"]
    mats = root["localMaterialBuffer"]["materials"] if root.get("localMaterialBuffer") else []
    entries = root["materialEntries"]
    if not (len(mats) == len(entries) and mats and all(e["isLocalInstance"] == 1 for e in entries)):
        raise BuildError(f"{what}: non-local materials in the active mesh (unsupported body mod)")
    if root.get("localMaterialInstances") or root.get("preloadLocalMaterialInstances") or root.get("externalMaterials"):
        raise BuildError(f"{what}: external materials in the active mesh (unsupported body mod)")
    if not any(e["name"]["$value"] == MESH_APPEARANCE for e in entries):
        raise BuildError(f"{what}: no material {MESH_APPEARANCE} in the active mesh")
    if not any(a["Data"]["name"]["$value"] == MESH_APPEARANCE for a in root["appearances"]):
        raise BuildError(f"{what}: no appearance {MESH_APPEARANCE} in the active mesh")
    for i in range(len(mats)):
        mats[i] = decal_material(tex, alpha)
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


def make_app(template, t, resource, comp_name, definition):
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


def build_archive(s, cli, items, active, log):
    """items: list of Item ; active: target code -> (mesh json, morph json). -> (archive, xl, listing)."""
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

    entries, names_all, loc_entries = [], [], []
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

    root["bodyCustomizationOptions"] = [{"HandleId": str(i), "Data": d} for i, d in enumerate(entries)]
    for g in root["bodyGroups"]:
        g["options"] = [cname(x) for x in names_all]
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


def run_build(s, entries, catalogue, log, progress=None):
    """Whole build : entries (supported, selected) -> BuildResult. `progress(step, total, text)` is optional."""
    t0 = time.time()
    items = [e for e in entries if e.supported]
    if not items:
        raise BuildError("no supported tattoo selected: nothing to build")
    if s.slots < 1:
        raise BuildError("at least one slot is needed")
    if not os.path.isdir(s.game):
        raise BuildError("game folder not found: " + s.game)
    catalogue.ensure(items)
    cli = Cli(s.cli, log)
    total = 3 + len(items)

    def step(i, text):
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

    log("3. textures")
    for i, it in enumerate(built):
        step(2 + i, f"Extracting texture {i + 1}/{len(built)}: {it.name}")
        it.texdir = extract_textures(cli, it.entry.path, it.slug, s.work, log)

    step(2 + len(built), "Building the archive")
    log("4. build")
    arc, xl, listing = build_archive(s, cli, built, active, log)
    catalogue.save()
    size = os.path.getsize(arc)
    log(f"\nDONE in {time.time() - t0:.0f} s: {arc} ({size / 1e6:.1f} MB, {len(listing)} files) + {os.path.basename(xl)}")
    log(f"  {len(built)} tattoo(s), {s.slots} slot(s), mirror {'on' if s.mirror else 'off'}")
    for it in built:
        log(f"    {it.slug:40s} \"{it.name}\"  [{', '.join(it.entry.target_codes)}]")
    step(total, "Done")
    return BuildResult(arc, xl, listing, built, time.time() - t0, size)


# ----------------------------------------------------------------------------- 5. the player's game
def conflicting_archives(game, selected=(), exclude_names=()):
    """VTK tattoo archives still in `archive\\pc\\mod` : they paint a permanent overlay in the skin, under Ink Flow's
    layers. Two criteria, both by content (never by file name) :
      - PURE tattoo archive : every entry is a known overlay / roughness texture (body mods such as Angel also ship
        `v_overlay.xbm`, with 100+ other files : they are NOT flagged, moving them would break the body) ;
      - same content as one of the `selected` inputs (size, then SHA-256).
    ~0.4 s for 600 archives (index only). Returns sorted file names."""
    mod = mod_dir(game)
    if not os.path.isdir(mod):
        return []
    by_size = {}
    for e in selected:
        try:
            by_size.setdefault(os.path.getsize(e.path), []).append(e.id)
        except OSError:
            continue
    out = []
    for a in rdar.archives_in(mod):
        if a in exclude_names or a in CANARI:
            continue
        p = os.path.join(mod, a)
        try:
            hs = rdar.hashes(p)
            if hs and hs <= set(HASH_PATH) and hs & TARGET_HASHES:
                out.append(a)
            elif os.path.getsize(p) in by_size and rdar.content_id(p) in by_size[os.path.getsize(p)]:
                out.append(a)
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
    """Copy the archive + .xl into `archive\\pc\\mod`. Anything replaced, and the conflicting archives asked for, go to
    `backup_dir\\<timestamp>\\`. Returns the backup folder (or None if nothing was backed up)."""
    mod = mod_dir(game)
    if not os.path.isdir(mod):
        raise BuildError("game mod folder not found: " + mod)
    if game_running():
        raise BuildError("Cyberpunk 2077 is running: close the game first")
    stamp_dir = os.path.join(backup_dir, time.strftime("%Y-%m-%d_%H%M%S"))
    backed = False

    def backup(name):
        nonlocal backed
        p = os.path.join(mod, name)
        if os.path.isfile(p):
            os.makedirs(stamp_dir, exist_ok=True)
            shutil.move(p, os.path.join(stamp_dir, name))
            backed = True
            log(f"  moved to backup: {name}")

    for src in (result.archive, result.xl):
        backup(os.path.basename(src))
    for name in CANARI:
        backup(name)
    for name in move_conflicts:
        backup(name)
    for src in (result.archive, result.xl):
        shutil.copy2(src, os.path.join(mod, os.path.basename(src)))
        log(f"  installed: {os.path.basename(src)}")
    return stamp_dir if backed else None
