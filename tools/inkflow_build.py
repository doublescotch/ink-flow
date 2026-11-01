"""Ink Flow — VTK/UV CCXL Tattoo Loader : generateur v0.3 (2026-11-01 ; v0 = corps, v0.1 = + bras VTK, v0.2 = entrees sans nom resolu,
v0.3 = + tete VTK ; ETUDE § 9-12).

Construit UNE archive + son .xl qui ajoutent au createur de personnage (V feminine) les tatouages VTK du joueur,
a partir de ses propres .archive de tatouages, choisies sur le disque (dossier --in) :
  - lit l'index de chaque .archive (RDAR, sans WolvenKit) et reconnait les CIBLES par les fichiers qu'elle remplace
    (table TARGETS : corps `v_overlay.xbm`, bras gauche / droit `femme_arm_left|right_01_overlay.xbm`, tete
    `h0_001_pwa_c__basehead_overlay.xbm`) ; le reste (UV, masques de rugosite) est liste « ignore » ;
  - tete (v0.3) : le maillage de peau de la tete est un seul chunk, tout en peau (yeux, dents, cils = autres maillages) ;
    sa coque suit les morphs du visage par une COPIE de son morphtarget (105 cibles) repointee sur la coque, comme
    Heterochromia copie celui des yeux ; le morphtarget n'a pas le radical du maillage (`h0_000_pwa__morphs`) ;
  - trouve chaque maillage actif chez le joueur (premiere archive de `archive\\pc\\mod`, ordre alphabetique, qui le
    livre ; sinon le jeu de base), l'extrait et le serialise avec le CLI WolvenKit (cache) ;
  - par tatouage et par cible : la texture copiee a l'octet, une coque = COPIE DU MAILLAGE ACTIF dont tous les materiaux
    de peau deviennent le materiau decal des coques (DiffuseTexture = la texture, DiffuseAlpha = --alpha), le morphtarget
    du corps repointe ; un .app par (slot, tatouage, cible) ;
  - route 1 (desactivee par defaut, decision de Hell_Kaiser du 2026-11-01 : nos ajouts ne vivent que dans nos slots ;
    --route1 pour la remettre) : une option par tatouage AYANT UN CORPS dans le selecteur vanilla « Body Tattoos » ;
  - route 2 : N selecteurs (--slots, titre --slot-title), chacun avec un uiSlot PAR CIBLE (patron Heterochromia : une
    option active plusieurs infos) ; options Off + un par tatouage ; une cible absente du tatouage recoit l'info « off »
    de ce uiSlot (changer de tatouage ne laisse jamais un bras de l'ancien) ;
  - noms affiches : catalogue `inkflow_slugs.json` dans le dossier d'entree, {fichier: {slug, name}} ; `name` modifiable
    par le joueur (limite --max-name), `slug` ecrit une fois et jamais modifie (les choix du personnage sont stockes
    par nom d'option, donc par slug) ;
  - rien n'est pose dans le jeu : sortie dans --out ; les archives sources encore dans le jeu et le canari sont signales.

Usage :
  python -I inkflow_build.py --in <dossier> [--game "E:\\...\\Cyberpunk 2077"] [--slots 2] [--slot-index 1041]
         [--slot-title "Ink {n}"] [--max-name 20] [--alpha 1.0] [--out ...] [--work ...] [--name Ink_Flow] [--route1] [--list]
"""
import argparse
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rdar  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.normpath(os.path.join(HERE, "..", "templates"))
CLI_DEFAULT = r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\WolvenKit.Console-9.1.0\WolvenKit.CLI.exe"
GAME_DEFAULT = r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077"
WORK_DEFAULT = r"C:\__DEV\cyberpunk\ink_flow\gen"

P = "inkflow"                                   # prefixe des chemins du mod
MESH_APPEARANCE = "01_ca_pale"
BODY_DIR = r"base\characters\common\player_base_bodies\player_female_average"
BASEGAME = r"archive\pc\content\basegame_4_appearance.archive"
DECAL_MI = (r"base\characters\common\skin\character_mat_instance\__parameters\customization__parameters"
            r"\tattoos__parameters\customization_tattoos_01_ca_pale.mi")
ARMS_TEX = r"base\characters\player\femme\body\arms\textures"
HEAD_DIR = r"base\characters\head\player_base_heads\player_female_average"

# Cibles prises en charge : texture remplacee par l'archive de tatouage -> maillage actif a copier, gabarit .app.
# `morph` : morphtarget du maillage (None = composant garment sans morph) ; il peut vivre ailleurs que le maillage.
TARGETS = [
    dict(code="body", label="VTK corps", tex=r"base\v_textures\body\v_overlay.xbm",
         mesh=BODY_DIR + r"\t0_000_pwa_base__full.mesh", morph=BODY_DIR + r"\t0_000_pwa_base__full.morphtarget",
         tpl="chest_tattoo.app.json", keep="w__chest_tattoo", ctype="entMorphTargetSkinnedMeshComponent",
         old=r"your_name\ccxl\chest_tattoo_demo\meshes\chest_tattoo\your_chest_tattoo_pwa.morphtarget", suffix=""),
    dict(code="arm_l", label="VTK bras gauche", tex=ARMS_TEX + r"\femme_arm_left_01_overlay.xbm",
         mesh=BODY_DIR + r"\arms_hq\a0_000_pwa_base_hq__l.mesh", morph=None,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_left", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_left_pwa.mesh", suffix="_arm_l"),
    dict(code="arm_r", label="VTK bras droit", tex=ARMS_TEX + r"\femme_arm_right_01_overlay.xbm",
         mesh=BODY_DIR + r"\arms_hq\a0_000_pwa_base_hq__r.mesh", morph=None,
         tpl="arm_tattoo.app.json", keep="w__arm_tattoo_right", ctype="entGarmentSkinnedMeshComponent",
         old=r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_right_pwa.mesh", suffix="_arm_r"),
    dict(code="head", label="VTK tete", tex=HEAD_DIR + r"\h0_000_pwa_c__basehead\textures\h0_001_pwa_c__basehead_overlay.xbm",
         mesh=HEAD_DIR + r"\h0_000_pwa_c__basehead\h0_000_pwa_c__basehead.mesh", morph=HEAD_DIR + r"\h0_000_pwa__morphs.morphtarget",
         tpl="chest_tattoo.app.json", keep="w__chest_tattoo", ctype="entMorphTargetSkinnedMeshComponent",
         old=r"your_name\ccxl\chest_tattoo_demo\meshes\chest_tattoo\your_chest_tattoo_pwa.morphtarget", suffix="_head"),
]
TARGET_BY_TEX = {t["tex"]: t for t in TARGETS}
# Fichiers connus mais non pris en charge (pour nommer ce qu'on ignore).
KNOWN_OTHER = {
    r"base\4k\common\overlays\fullbody_overlay_d01.xbm": "UV corps+bras",
    r"base\v_textures\body\v_body_rm.xbm": "VTK peau (rugosite), pas un tatouage",
    ARMS_TEX + r"\femme_arm_left_01_roughnessmask.xbm": "VTK bras gauche (rugosite)",
    ARMS_TEX + r"\femme_arm_right_01_roughnessmask.xbm": "VTK bras droit (rugosite)",
}
HASH_PATH = {rdar.fnv1a64(p): p for p in list(TARGET_BY_TEX) + list(KNOWN_OTHER)}
TEX_REGEX = "(" + "|".join(re.escape(os.path.basename(t["tex"])) for t in TARGETS) + r"|\d+\.bin)$"
# `\d+.bin` : le CLI nomme ainsi une entree dont il ne resout pas le chemin (archives anciennes sans table de noms,
# ex. Kala Vale 2023) ; l'empreinte du nom est celle du chemin : on la remet en place (extract_textures).
NAME_PREFIX = re.compile(r"^\d+_Tattoos?_(VTK|UV)_", re.I)
SLUG_TABLE = "inkflow_slugs.json"


# ----------------------------------------------------------------------------- utilitaires
def log(*a):
    print(*a, flush=True)


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
    """Remplace toute valeur de chaine egale a une cle de `table` (sans tenir compte de la casse)."""
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


class Cli:
    def __init__(self, exe):
        if not os.path.isfile(exe):
            sys.exit("CLI WolvenKit introuvable : " + exe)
        self.exe = exe

    def run(self, *args, what=""):
        t = time.time()
        r = subprocess.run([self.exe, *args], capture_output=True, text=True)
        ok = r.returncode == 0 and "Error" not in r.stdout
        log(f"  cli {what or args[0]} : {'OK' if ok else 'ECHEC'} ({time.time() - t:.1f} s)")
        if not ok:
            log(r.stdout[-3000:], r.stderr[-2000:])
            sys.exit(1)
        return r.stdout


# ----------------------------------------------------------------------------- 1. entree
def display_name(stem):
    return NAME_PREFIX.sub("", stem).replace("_", " ").strip() or stem


def make_slug(stem, taken):
    base = re.sub(r"[^a-z0-9]+", "_", NAME_PREFIX.sub("", stem).lower()).strip("_")[:40].strip("_") or "tattoo"
    slug, n = base, 2
    while slug in taken:
        slug, n = f"{base}_{n}", n + 1
    return slug


def scan_inputs(folder):
    """-> liste de dict {file, stem, targets (liste de TARGETS), other (libelles ignores), unknown (compte)}."""
    out = []
    for a in rdar.archives_in(folder):
        hs = rdar.hashes(os.path.join(folder, a))
        paths = {HASH_PATH[h] for h in hs if h in HASH_PATH}
        out.append({"file": a, "stem": os.path.splitext(a)[0], "id": rdar.content_id(os.path.join(folder, a)),
                    "targets": [t for t in TARGETS if t["tex"] in paths],
                    "other": sorted(KNOWN_OTHER[p] for p in paths if p in KNOWN_OTHER),
                    "unknown": len([h for h in hs if h not in HASH_PATH])})
    return out


def slug_table(folder, entries, write):
    """Catalogue fichier -> {slug, name} : le slug d'une entree existante ne change jamais ; `name` est le libelle
    affiche, modifiable par le joueur ; les nouvelles entrees s'ajoutent. Ancien format (fichier -> slug) converti."""
    p = os.path.join(folder, SLUG_TABLE)
    raw = load(p) if os.path.isfile(p) else {}
    table = {}
    for k, v in raw.items():
        table[k] = {"slug": v, "name": display_name(os.path.splitext(k)[0])} if isinstance(v, str) else dict(v)
    before = json.dumps(table, sort_keys=True)
    taken = {v["slug"] for v in table.values()}
    for e in entries:
        if e["file"] not in table:
            # fichier renomme ? meme contenu (id) sous un autre nom : l'entree suit, le slug reste
            old = next((k for k, v in table.items() if v.get("id") == e["id"] and k not in {x["file"] for x in entries}), None)
            if old:
                table[e["file"]] = table.pop(old)
                log(f"  catalogue : « {old} » renomme en « {e['file']} », slug {table[e['file']]['slug']} conserve")
            else:
                s = make_slug(e["stem"], taken)
                table[e["file"]] = {"slug": s, "name": display_name(e["stem"])}
                taken.add(s)
        table[e["file"]].setdefault("name", display_name(e["stem"]))
        table[e["file"]]["id"] = e["id"]
    if json.dumps(table, sort_keys=True) != before and write:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(table, f, indent=2, ensure_ascii=False)
        log(f"  catalogue ecrit : {p} ({len(table)} entrees ; `name` modifiable, `slug` jamais)")
    return table


def option_name(table, file, max_len):
    """Libelle d'une option : le `name` du catalogue, coupe a `max_len` caracteres (le createur n'a pas la place)."""
    name = (table[file].get("name") or "").strip() or display_name(os.path.splitext(file)[0])
    if max_len and len(name) > max_len:
        log(f"  ! nom trop long ({len(name)} > {max_len}), coupe : « {name} » -> « {name[:max_len].rstrip()} »")
        name = name[:max_len].rstrip()
    return name


# ----------------------------------------------------------------------------- 2. maillages actifs
def find_owner(game, path):
    mod = os.path.join(game, r"archive\pc\mod")
    owners = rdar.owners(mod, path) if os.path.isdir(mod) else []
    if owners:
        return os.path.join(mod, owners[0]), owners
    return os.path.join(game, BASEGAME), []


def extract_mesh(cli, game, work, t):
    """Maillage actif d'une cible (+ morphtarget) : extrait et serialise en JSON, cache sur l'archive source."""
    src, owners = find_owner(game, t["mesh"])
    who = owners[0] + (f" (devant {', '.join(owners[1:])})" if len(owners) > 1 else "") if owners else "jeu de base"
    log(f"  {t['label']:16s} : {who}")
    if t["morph"] and rdar.fnv1a64(t["morph"]) not in rdar.hashes(src):
        sys.exit(f"le morphtarget de {t['code']} ({t['morph']}) n'est pas dans la meme archive que le mesh ({src}) : cas non prevu")
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
    # un seul appel de serialisation sur le dossier commun (la tete : maillage dans un sous-dossier, morphtarget au-dessus)
    common = os.path.commonpath([os.path.join(d, os.path.dirname(p)) for p in wanted])
    cli.run("convert", "serialize", common, what=f"serialize {t['code']}")
    for p in (mesh_json, morph_json):
        if p and not os.path.isfile(p):
            sys.exit("fichier attendu absent : " + p)
    with open(marker, "w") as f:
        f.write(key)
    return mesh_json, morph_json


# ----------------------------------------------------------------------------- 3. textures
def extract_textures(cli, archive, slug, work):
    """Toutes les textures de cibles d'une archive de tatouage -> work\\tex\\<slug>\\<chemin du jeu> (cache)."""
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
                log(f"  chemin retabli depuis l'empreinte : {HASH_PATH[int(m.group(1))]}")
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
        self.resource = self.morph if t["morph"] else self.mesh    # ce que le composant du .app reference


def decal_material(tex, alpha):
    """Materiau decal des coques vanilla (gabarit lu dans la coque Angel au canari v5), texture et opacite du fichier."""
    values = [{"$type": "rRef:ITexture", "DiffuseTexture": respath(tex, "Default")}]
    if alpha is not None:
        values.append({"$type": "Float", "DiffuseAlpha": alpha})
    return {"$type": "CMaterialInstance", "audioTag": cname("None"), "baseMaterial": respath(DECAL_MI, "Default"),
            "cookingPlatform": "PLATFORM_None", "enableMask": 0, "metadata": None, "resourceVersion": 4, "values": values}


def shell(active, tex, alpha, what):
    """Coque = copie du maillage actif dont chaque materiau de peau devient le decal (v5)."""
    mesh = copy.deepcopy(active)
    root = mesh["Data"]["RootChunk"]
    mats = root["localMaterialBuffer"]["materials"] if root.get("localMaterialBuffer") else []
    entries = root["materialEntries"]
    if not (len(mats) == len(entries) and mats and all(e["isLocalInstance"] == 1 for e in entries)):
        sys.exit(f"{what} : materiaux non locaux (cas non prevu)")
    if root.get("localMaterialInstances") or root.get("preloadLocalMaterialInstances") or root.get("externalMaterials"):
        sys.exit(f"{what} : materiaux externes (cas non prevu)")
    if not any(e["name"]["$value"] == MESH_APPEARANCE for e in entries):
        sys.exit(f"{what} : pas de materiau {MESH_APPEARANCE}")
    if not any(a["Data"]["name"]["$value"] == MESH_APPEARANCE for a in root["appearances"]):
        sys.exit(f"{what} : pas d'apparence {MESH_APPEARANCE}")
    for i in range(len(mats)):
        mats[i] = decal_material(tex, alpha)
    root["castsRayTracedShadowsFromOriginalGeometry"] = 0
    chunks = root["renderResourceBlob"]["Data"]["header"]["renderChunkInfos"]
    return mesh, len(mats), sum(c["numVertices"] for c in chunks)


def retarget_morph(active_morph, t, new_mesh):
    """Copie du morphtarget du maillage actif, repointee sur la coque (le `baseMesh` seul change : les cibles, le
    baseTexture et les diffs de normales restent ceux du maillage d'origine, de meme geometrie)."""
    morph = copy.deepcopy(active_morph)
    hits = {}
    replace_paths(morph["Data"]["RootChunk"], {t["mesh"]: new_mesh}, hits)
    assert hits.get(t["mesh"], 0) == 1, hits
    return morph, len(morph["Data"]["RootChunk"].get("targets") or [])


def make_app(template, t, resource, comp_name, definition):
    """Gabarit toolkit : une apparence gardee, renommee, repointee sur notre ressource (components + compiledData),
    composant renomme, ombres coupees (le maillage d'origine porte deja l'ombre)."""
    app = copy.deepcopy(template)
    root = app["Data"]["RootChunk"]
    root["appearances"] = [a for a in root["appearances"] if a["Data"]["name"]["$value"] == t["keep"]]
    assert len(root["appearances"]) == 1, t["keep"]
    a = root["appearances"][0]["Data"]
    set_cname(a, "name", definition)
    hits = {}
    replace_paths(a, {t["old"]: resource}, hits)
    assert sum(hits.values()) >= 2, hits
    n = 0
    for comp in a["components"] + a["compiledData"]["Data"]["Chunks"]:
        if comp.get("$type") == t["ctype"]:
            set_cname(comp, "name", comp_name)
            set_cname(comp, "meshAppearance", MESH_APPEARANCE)
            comp["castShadows"] = "Never"
            comp["castLocalShadows"] = "Never"
            n += 1
    assert n == 2, n
    return app


def build(args, cli, items, active):
    """items : liste de dict {slug, name, file, targets, texdir} ; active : code de cible -> (mesh json, morph json)."""
    src = os.path.join(args.work, "pack", args.name)
    shutil.rmtree(src, ignore_errors=True)
    os.makedirs(src)
    os.makedirs(args.out, exist_ok=True)

    def save(rel, j):
        p = os.path.join(src, rel + ".json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(j, f, indent=1)

    meshes = {c: load(m) for c, (m, _) in active.items()}
    morphs = {c: load(mo) for c, (_, mo) in active.items() if mo}
    tpls = {t["tpl"]: load(os.path.join(TEMPLATES, t["tpl"])) for t in TARGETS}
    slots = list(range(1, args.slots + 1))
    expected = []

    for it in items:
        slug = it["slug"]
        parts = []
        for t in it["targets"]:
            pp = Paths(slug, t)
            src_tex = os.path.join(it["texdir"], t["tex"])
            if not os.path.isfile(src_tex):
                sys.exit("texture absente apres extraction : " + src_tex)
            dst = os.path.join(src, pp.tex)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src_tex, dst)
            mesh, nm, nv = shell(meshes[t["code"]], pp.tex, args.alpha, f"[{slug}] {t['code']}")
            save(pp.mesh, mesh)
            expected.append(pp.mesh)
            nt = 0
            if t["morph"]:
                morph, nt = retarget_morph(morphs[t["code"]], t, pp.mesh)
                save(pp.morph, morph)
                expected.append(pp.morph)
            if args.route1 and t["code"] == "body":
                save(pp.app, make_app(tpls[t["tpl"]], t, pp.resource, f"inkflow_{slug}", f"w__{slug}"))
                expected.append(pp.app)
            for n_ in slots:
                save(pp.slot_app(n_), make_app(tpls[t["tpl"]], t, pp.resource, f"inkflow_slot{n_}_{slug}{t['suffix']}", f"w__{slug}{t['suffix']}"))
                expected.append(pp.slot_app(n_))
            parts.append(f"{t['code']} {nv} sommets / {nm} mat." + (f" / {nt} morphs" if nt else ""))
        log(f"  [{slug}] « {it['name']} » : " + " ; ".join(parts))

    # .inkcharcustomization (gabarit toolkit : switcher + off + appearance info)
    cc = load(os.path.join(TEMPLATES, "your_tattoo_pwa.inkcharcustomization.json"))
    root = cc["Data"]["RootChunk"]
    opts = root["bodyCustomizationOptions"]
    tk_switcher = next(h["Data"] for h in opts if h["Data"]["$type"] == "gameuiSwitcherInfo")
    tk_off = next(h["Data"] for h in opts if h["Data"]["name"]["$value"] == "chest_tattoo_off")
    tk_info = next(h["Data"] for h in opts if h["Data"]["name"]["$value"] == "your_chest_tattoo")

    def option(index, loc, names):
        o = copy.deepcopy(tk_switcher["options"][1])
        o["index"] = index
        o["localizedName"] = loc
        o["names"] = [cname(x) for x in names]
        return o

    def info(name, ui_slot, resource, definition, edit_tags):
        d = copy.deepcopy(tk_info)
        set_cname(d, "name", name)
        set_cname(d, "uiSlot", ui_slot)
        d["resource"] = respath(resource)
        set_cname(d["definitions"][0], "name", definition)
        d["editTags"] = list(edit_tags)
        return d

    def off(name, ui_slot):
        d = copy.deepcopy(tk_off)
        set_cname(d, "name", name)
        set_cname(d, "uiSlot", ui_slot)
        d["editTags"] = list(tags)  # tags defini plus bas, lu a l'appel
        return d

    entries, names_all, loc_entries = [], [], []
    for it in items:
        loc_entries.append((f"UI-Customization-inkflow_{it['slug']}", it["name"]))
        if args.route1:
            loc_entries.append((f"UI-Customization-inkflow_{it['slug']}_v", f"{it['name']} (Ink Flow)"))
    # etiquettes d'edition : NewGame + Ripperdoc = tatouages vanilla (createur + charcudoc) ; HairDresser = aussi le
    # miroir de l'appartement (maquillage, cicatrices, Heterochromia). Mesure du 2026-11-01 sur female_cco vanilla.
    tags = ["NewGame", "HairDresser", "Ripperdoc"] if args.mirror else ["NewGame", "Ripperdoc"]
    body_t = TARGETS[0]

    # route 1 : options ajoutees au selecteur vanilla body_tattoo (patron Kylin), tatouages avec un corps seulement.
    with_body = [it for it in items if body_t in it["targets"]]
    if args.route1 and with_body:
        s1 = copy.deepcopy(tk_switcher)
        set_cname(s1, "name", "None")
        set_cname(s1, "link", "body_tattoo")
        s1["index"] = 0
        s1["localizedName"] = ""
        set_cname(s1, "uiSlot", "None")
        s1["uiSlots"] = []
        s1["switchVisibility"] = 0
        s1["editTags"] = []
        s1["options"] = [option(i, f"UI-Customization-inkflow_{it['slug']}_v", [f"inkflow_{it['slug']}"]) for i, it in enumerate(with_body)]
        entries.append(s1)
        for it in with_body:
            entries.append(info(f"inkflow_{it['slug']}", "body_tattoo", Paths(it["slug"], body_t).app, f"w__{it['slug']}", tags))
            names_all.append(f"inkflow_{it['slug']}")

    # route 2 : un selecteur par slot, un uiSlot par cible, une option par tatouage (patron Heterochromia).
    for n_ in slots:
        ui = {t["code"]: f"inkflow_slot{n_}{t['suffix']}" for t in TARGETS}
        off_name = {t["code"]: f"inkflow_slot{n_}_off{t['suffix']}" for t in TARGETS}
        s2 = copy.deepcopy(tk_switcher)
        set_cname(s2, "name", f"inkflow_slot{n_}")
        s2["index"] = args.slot_index + n_ - 1
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
                if t in it["targets"]:
                    nm = f"inkflow_slot{n_}_{it['slug']}{t['suffix']}"
                    infos.append(info(nm, ui[t["code"]], Paths(it["slug"], t).slot_app(n_), f"w__{it['slug']}{t['suffix']}", tags))
                    names.append(nm)
                else:
                    names.append(off_name[t["code"]])
            s2["options"].append(option(i, f"UI-Customization-inkflow_{it['slug']}", names))
        entries += [s2] + offs + infos
        names_all += [f"inkflow_slot{n_}"] + [o["name"]["$value"] for o in offs] + [x["name"]["$value"] for x in infos]
        loc_entries.append((f"UI-Customization-inkflow_slot{n_}", args.slot_title.replace("{n}", str(n_))))

    root["bodyCustomizationOptions"] = [{"HandleId": str(i), "Data": d} for i, d in enumerate(entries)]
    for g in root["bodyGroups"]:
        g["options"] = [cname(x) for x in names_all]
    inkcc = rf"{P}\inkflow_pwa.inkcharcustomization"
    save(inkcc, cc)
    expected.append(inkcc)

    # localisation (JsonResource)
    loc = load(os.path.join(TEMPLATES, "localization.json.json"))
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

    # JSON -> fichiers du jeu (un seul appel sur le dossier), puis retrait des .json
    cli.run("convert", "deserialize", src, what=f"deserialize ({len(expected)} fichiers)")
    missing = [p for p in expected if not os.path.isfile(os.path.join(src, p))]
    if missing:
        sys.exit("fichiers non produits par le CLI : " + ", ".join(missing))
    for d, _, files in os.walk(src):
        for f in files:
            if f.endswith(".json") and not f.endswith("inkflow_en-us.json"):
                os.remove(os.path.join(d, f))
    if os.path.isfile(os.path.join(src, locp + ".json")):
        os.remove(os.path.join(src, locp + ".json"))

    # .xl + pack
    xl = os.path.join(args.out, args.name + ".archive.xl")
    with open(xl, "w", encoding="utf-8", newline="\n") as f:
        f.write("customizations:\n")
        f.write(f"  female: {inkcc}\n")
        f.write("localization:\n  onscreens:\n")
        f.write(f"    en-us: {locp}\n")
    arc = os.path.join(args.out, args.name + ".archive")
    if os.path.isfile(arc):
        os.remove(arc)
    cli.run("pack", src, "-o", args.out, what="pack")
    if not os.path.isfile(arc):
        sys.exit("archive non produite")
    listing = [l for l in cli.run("archive", arc, "-l", what="liste").splitlines() if "\\" in l]
    return arc, xl, listing


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True, help="dossier des .archive de tatouages choisies par le joueur")
    ap.add_argument("--game", default=GAME_DEFAULT, help="dossier du jeu (maillages actifs dans archive\\pc\\mod)")
    ap.add_argument("--cli", default=CLI_DEFAULT, help="WolvenKit.CLI.exe")
    ap.add_argument("--work", default=WORK_DEFAULT, help="dossier de travail (extractions, cache, pack)")
    ap.add_argument("--out", default=None, help="dossier de sortie (defaut : <work>\\out)")
    ap.add_argument("--name", default="Ink_Flow", help="nom de l'archive produite")
    ap.add_argument("--slots", type=int, default=2, help="nombre de selecteurs propres")
    ap.add_argument("--slot-index", type=int, default=1041, help="index du premier selecteur propre (1041 = sous Body Tattoos)")
    ap.add_argument("--slot-title", default="Ink {n}", help="titre des selecteurs propres, {n} = numero (court : la valeur deborde sur le titre)")
    ap.add_argument("--max-name", type=int, default=20, help="longueur maximale d'un libelle d'option (0 = sans limite) ; au-dela : coupe")
    ap.add_argument("--alpha", type=float, default=1.0, help="opacite du decal (vanilla 0,6)")
    ap.add_argument("--mirror", action="store_true", help="selecteurs et options aussi au miroir de l'appartement (etiquette HairDresser ; defaut : createur + charcudoc comme les tatouages vanilla)")
    ap.add_argument("--route1", action="store_true", help="ajoute aussi une option par tatouage (corps) au selecteur vanilla (defaut : non)")
    ap.add_argument("--list", action="store_true", help="analyse seulement : cibles, slugs, maillages actifs ; rien d'ecrit")
    args = ap.parse_args()
    args.out = args.out or os.path.join(args.work, "out")
    if not os.path.isdir(args.inp):
        sys.exit("dossier d'entree introuvable : " + args.inp)
    t0 = time.time()

    log("1. archives de tatouages dans", args.inp)
    entries = scan_inputs(args.inp)
    if not entries:
        sys.exit("aucune .archive dans le dossier d'entree")
    table = slug_table(args.inp, entries, write=not args.list)
    items, ignored = [], []
    for e in entries:
        extra = f"{e['unknown']} fichier(s) inconnu(s)" if e["unknown"] else ""
        ign = ", ".join(x for x in e["other"] + [extra] if x)
        if e["targets"]:
            slug, name = table[e["file"]]["slug"], option_name(table, e["file"], args.max_name)
            cibles = " + ".join(t["label"] for t in e["targets"])
            log(f"  + {e['file']}  ->  {slug}, « {name} » : {cibles}" + (f" (ignore : {ign})" if ign else ""))
            items.append({"slug": slug, "name": name, "file": e["file"], "targets": e["targets"]})
        else:
            log(f"  - {e['file']}  ignore : {ign or 'aucun fichier connu'}")
            ignored.append(e["file"])
    if not items:
        sys.exit("aucune archive de tatouage prise en charge : rien a construire")
    dup = {n for n in (i["name"] for i in items) if [i["name"] for i in items].count(n) > 1}
    if dup:
        log(f"  ! libelles en double apres coupe (a renommer dans {SLUG_TABLE}, champ name) : {', '.join(sorted(dup))}")

    log("2. maillages actifs")
    needed = [t for t in TARGETS if any(t in it["targets"] for it in items)]
    mod = os.path.join(args.game, r"archive\pc\mod")
    in_game = [e["file"] for e in entries if os.path.isfile(os.path.join(mod, e["file"]))]
    canari = [f for f in ("Ink_Flow_Canari.archive", "Ink_Flow_Canari.archive.xl") if os.path.isfile(os.path.join(mod, f))]
    if args.list:
        for t in needed:
            _, owners = find_owner(args.game, t["mesh"])
            log(f"  {t['label']:16s} : {owners[0] if owners else 'jeu de base'}" + (f" (devant {', '.join(owners[1:])})" if len(owners) > 1 else ""))
        log(f"analyse seule : {len(items)} tatouage(s) a construire, {len(ignored)} ignore(s)")
        if in_game:
            log("  presents dans le jeu, a retirer avant la pose :", ", ".join(in_game))
        return

    cli = Cli(args.cli)
    active = {t["code"]: extract_mesh(cli, args.game, args.work, t) for t in needed}

    log("3. textures")
    for it in items:
        it["texdir"] = extract_textures(cli, os.path.join(args.inp, it["file"]), it["slug"], args.work)

    log("4. construction")
    arc, xl, listing = build(args, cli, items, active)

    log(f"\nTERMINE en {time.time() - t0:.0f} s : {arc} ({os.path.getsize(arc) / 1e6:.1f} Mo, {len(listing)} fichiers) + {os.path.basename(xl)}")
    log(f"  {len(items)} tatouage(s), {args.slots} slot(s), route 1 {'presente (corps seulement)' if args.route1 else 'absente'}")
    for it in items:
        log(f"    {it['slug']:40s} « {it['name']} »  [{', '.join(t['code'] for t in it['targets'])}]")
    if ignored:
        log("  ignores :", ", ".join(ignored))
    if in_game:
        log("  A RETIRER de archive\\pc\\mod avant la pose (sinon l'overlay permanent reste) :", ", ".join(in_game))
    if canari:
        log("  A RETIRER aussi (memes noms d'options) :", ", ".join(canari))


if __name__ == "__main__":
    main()
