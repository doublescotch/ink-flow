"""Canari Ink Flow (VTK/UV CCXL Tattoo Loader) — construit une archive qui ajoute des tatouages VTK
au créateur de personnage (V féminine, corps Angel) :
  - route 1 : une option de plus dans le sélecteur vanilla `body_tattoo` (patron Kylin : switcher sans nom, link=body_tattoo),
    pour le PREMIER fichier seulement ;
  - route 2 : N sélecteurs propres « Ink Flow - Slot n » (patron CCXL Tattoo Toolkit 20279, index 3350 + n - 1),
    chacun avec une option par fichier (Off / Samurai / Kala…).
Rien n'est posé dans le jeu : sortie dans build\out[\<tag>].

v2 (2026-10-31 soir, après la première QA) :
  - chaque slot a SON .app et SON nom de composant (v1 : même .app, même composant `inkflow_samurai` pour les deux
    sélecteurs -> désactiver le slot custom retirait aussi la coque du sélecteur vanilla, « inversion » vue en jeu) ;
  - opacité du décal réglable (ALPHA) : v1 gardait le 0,6 vanilla, jugé gris pour une coque seule ; 1,0 par défaut ;
  - route 1 sans coque FPP par défaut (FPP = True pour la remettre) : en v1 l'option vanilla empilait TPP + FPP
    dans le créateur (deux coques = « bien noir »), à confirmer en jeu.
v3 (2026-10-31, après la QA v2 validée) : N fichiers (table FILES, `--files`) et N slots (`--slots`, 2 par défaut) :
  une texture + une coque TPP/FPP + un morphtarget PAR FICHIER (la coque porte le renvoi vers la texture), un .app
  PAR (slot, fichier) (le nom du composant doit être unique). But : deux slots avec deux fichiers différents, pour
  juger le chevauchement réel (Samurai 8192² BC7 + Kala 2048² TrueColor, sans mips).

v4 (2026-10-31, 22 h) : `--slot-index 1041` : sélecteurs propres juste sous « Body Tattoos » (vu en jeu).
v5 (2026-11-01, GO de Hell_Kaiser, ETUDE § 8 piste A) : `--shell body` : la coque TPP n'est plus la coque de tatouage
  d'Angel (12 589 sommets, maillage à part qui passe sous la peau : escalier et z-fighting vus en jeu) mais une COPIE DU
  CORPS ACTIF (t0_000_pwa_base__full.mesh + .morphtarget d'Angel, 91 360 sommets, mêmes poids, même cible breast_big)
  dont les 12 matériaux de peau sont remplacés par le matériau décal des coques (customization_tattoos_01_ca_pale.mi,
  DiffuseTexture = la texture, DiffuseAlpha = ALPHA). Coque = corps à l'identique : rien ne peut passer dessous.
  Ombres coupées sur ce composant (le corps les porte déjà). La coque FPP reste celle d'Angel (hors v5).

Sources (déjà extraites dans x\) :
  - coque Angel tx_000_pwa_base__full_tattoo_01 (.mesh + .morphtarget) et sa coque FPP ;
  - corps Angel t0_000_pwa_base__full (.mesh + .morphtarget, chemins vanilla, tirés de 006_Angel_Body.archive) ;
  - textures VTK base\v_textures\body\v_overlay.xbm de 002_Tattoos_VTK_Samurai et 002_Tattoos_VTK_Kala_Japanese_Arm_Body ;
  - gabarits : toolkit chest_tattoo.app / arm_tattoo.app / your_tattoo_pwa.inkcharcustomization, Kylin k3_ponytail_wa__local.json.

Usage : python -I build_canari.py [--alpha 0.6] [--fpp] [--files samurai,kala] [--slots 2] [--slot-index 1041] [--shell body] [--tag v5]
"""
import argparse, copy, json, os, shutil, subprocess, sys

ROOT = r"C:\__DEV\cyberpunk\ink_flow"
X = os.path.join(ROOT, "x")
TK = os.path.join(ROOT, r"dl\20279\unz")
CLI = r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\WolvenKit.Console-9.1.0\WolvenKit.CLI.exe"
BUILD = os.path.join(ROOT, "build")
ARCHIVE_NAME = "Ink_Flow_Canari"
SRC = os.path.join(BUILD, ARCHIVE_NAME)          # racine packée (= archive\pc\mod\<nom>.archive)
OUT = os.path.join(BUILD, "out")

P = "inkflow"                                     # préfixe de chemins du mod
INKCC = rf"{P}\inkflow_pwa.inkcharcustomization"
LOC = rf"{P}\localization\inkflow_en-us.json"
XL = "Ink_Flow_Canari.archive.xl"

# slug -> (texture VTK source, nom affiché) ; le slug sert de nom de dossier et de composant
FILES = {
    "samurai": (os.path.join(X, r"samurai\base\v_textures\body\v_overlay.xbm"), "Samurai"),
    "kala": (os.path.join(X, r"kala\base\v_textures\body\v_overlay.xbm"), "Kala"),
}

ANGEL_MESH = os.path.join(X, r"angel\base\characters\common\player_base_bodies\player_female_average\tattoos\tx_000_pwa_base__full_tattoo_01.mesh.json")
ANGEL_MORPH = os.path.join(X, r"angel\base\characters\common\player_base_bodies\player_female_average\tattoos\tx_000_pwa_base__full_tattoo_01.morphtarget.json")
ANGEL_FPP = os.path.join(X, r"angel\base\characters\common\player_base_bodies\player_female_average\fpp\tattoos\tx_000_pwa_fpp__full_tattoo_01.mesh.json")
ANGEL_BODY_MESH = os.path.join(X, r"angel\base\characters\common\player_base_bodies\player_female_average\t0_000_pwa_base__full.mesh.json")
ANGEL_BODY_MORPH = os.path.join(X, r"angel\base\characters\common\player_base_bodies\player_female_average\t0_000_pwa_base__full.morphtarget.json")
BODY_MESH = r"base\characters\common\player_base_bodies\player_female_average\t0_000_pwa_base__full.mesh"   # baseMesh du morphtarget du corps
TK_CHEST_APP = os.path.join(TK, r"Chest Tattoo\source\archive\your_name\ccxl\chest_tattoo_demo\appearances\chest_tattoo.app.json")
TK_ARM_APP = os.path.join(TK, r"Arm Tattoo\source\archive\your_name\ccxl\arm_tattoo_demo\appearances\arm_tattoo.app.json")
TK_INKCC = os.path.join(TK, r"Chest Tattoo\source\archive\your_name\ccxl\chest_tattoo_demo\inkcc\your_tattoo_pwa.inkcharcustomization.json")
KYLIN_LOC = os.path.join(X, r"kylin\kylin\ccxl\k3_ponytail_wa\localization\k3_ponytail_wa__local.json.json")
TK_CHEST_MORPH = r"your_name\ccxl\chest_tattoo_demo\meshes\chest_tattoo\your_chest_tattoo_pwa.morphtarget"
TK_ARM_MESH = r"your_name\ccxl\arm_tattoo_demo\meshes\arm_tattoo\your_arm_tattoo_left_pwa.mesh"

VANILLA_TEX = r"base\characters\common\character_customisation_items\tattoos\body\textures\tattoo_body__customisation_01_d02.xbm"
VANILLA_MESH = r"base\characters\common\player_base_bodies\player_female_average\tattoos\tx_000_pwa_base__full_tattoo_01.mesh"
MESH_APPEARANCE = "01_ca_pale"      # appearance de la coque Angel utilisée (teint pâle : même décal, seul l'alpha du .mi varie)

SLOT_INDEX = 3350                   # premier slot ; hors de la plage 3300-3309 réservée au toolkit (wiki)


class Paths:
    """Chemins d'un fichier de tatouage dans l'archive."""
    def __init__(self, slug):
        d = rf"{P}\tattoos\{slug}"
        self.tex = rf"{d}\{slug}.xbm"
        self.mesh = rf"{d}\{slug}_pwa.mesh"
        self.morph = rf"{d}\{slug}_pwa.morphtarget"
        self.mesh_fpp = rf"{d}\{slug}_fpp_pwa.mesh"
        self.app = rf"{d}\{slug}.app"              # route 1, TPP
        self.app_fpp = rf"{d}\{slug}_fpp.app"      # route 1, FPP
        self.slot_app = lambda n: rf"{d}\{slug}_slot{n}.app"   # route 2


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(rel, j):
    p = os.path.join(SRC, rel + ".json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(j, f, indent=2)
    return p


def replace_paths(o, table, hits):
    """Remplace toute valeur de chaîne égale à une clé de `table` (sans tenir compte de la casse)."""
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


def cname(v):
    return {"$type": "CName", "$storage": "string", "$value": v}


def respath(v, flags="Soft"):
    return {"DepotPath": {"$type": "ResourcePath", "$storage": "string", "$value": v}, "Flags": flags}


def set_cname(o, key, v):
    o[key] = cname(v)


def retexture_mesh(src_json, tex, alpha):
    """Mesh Angel : chaque DiffuseTexture -> la texture du fichier ; opacité du décal forcée si alpha donné."""
    mesh = load(src_json)
    hits = {}
    replace_paths(mesh["Data"]["RootChunk"], {VANILLA_TEX: tex}, hits)
    n = hits.get(VANILLA_TEX, 0)
    assert n >= 1
    na = 0
    if alpha is not None:
        for m in mesh["Data"]["RootChunk"]["localMaterialBuffer"]["materials"]:
            if any("DiffuseTexture" in v for v in m["values"]):
                m["values"] = [v for v in m["values"] if "DiffuseAlpha" not in v]
                m["values"].append({"$type": "Float", "DiffuseAlpha": alpha})
                na += 1
    return mesh, n, na


def body_shell(body_json, shell_json, tex, alpha):
    """v5 : coque = copie du corps Angel ; ses 12 matériaux de peau (un par teint, 8 chunks chacun) deviennent le matériau
    décal de la coque Angel (gabarit : son matériau `01_ca_pale`), DiffuseTexture = la texture du fichier, DiffuseAlpha = alpha.
    Noms de matériaux, materialEntries et appearances inchangés (le .app vise l'appearance 01_ca_pale)."""
    mesh = load(body_json)
    root = mesh["Data"]["RootChunk"]
    shell = load(shell_json)["Data"]["RootChunk"]
    decal = next(m for i, m in enumerate(shell["localMaterialBuffer"]["materials"])
                 if shell["materialEntries"][i]["name"]["$value"] == MESH_APPEARANCE)
    assert decal["values"] == [{"$type": "rRef:ITexture", "DiffuseTexture": respath(VANILLA_TEX, "Default")}], decal["values"]
    mats = root["localMaterialBuffer"]["materials"]
    assert len(mats) == len(root["materialEntries"]) == 12 and all(e["isLocalInstance"] == 1 for e in root["materialEntries"])
    assert not root["localMaterialInstances"] and not root["preloadLocalMaterialInstances"] and not root["externalMaterials"]
    for i in range(len(mats)):
        m = copy.deepcopy(decal)
        m["values"] = [{"$type": "rRef:ITexture", "DiffuseTexture": respath(tex, "Default")}]
        if alpha is not None:
            m["values"].append({"$type": "Float", "DiffuseAlpha": alpha})
        mats[i] = m
    root["castsRayTracedShadowsFromOriginalGeometry"] = 0      # comme la coque Angel
    chunks = root["renderResourceBlob"]["Data"]["header"]["renderChunkInfos"]
    return mesh, len(mats), sum(c["numVertices"] for c in chunks)


def make_app(template_json, keep_appearance, old_path, new_path, comp_type, comp_name, definition, no_shadows=False):
    """Gabarit toolkit : une seule apparence, renommée w__<slug>, repointée (components + compiledData), composant renommé.
    no_shadows : castShadows / castLocalShadows = Never (coque copie du corps : le corps porte déjà l'ombre)."""
    app = load(template_json)
    root = app["Data"]["RootChunk"]
    root["appearances"] = [a for a in root["appearances"] if a["Data"]["name"]["$value"] == keep_appearance]
    assert len(root["appearances"]) == 1
    a = root["appearances"][0]["Data"]
    set_cname(a, "name", definition)
    hits = {}
    replace_paths(a, {old_path: new_path}, hits)
    assert sum(hits.values()) >= 2, hits        # components + compiledData (+ resolvedDependencies)
    n = 0
    for comp in a["components"] + a["compiledData"]["Data"]["Chunks"]:
        if comp.get("$type") == comp_type:
            set_cname(comp, "name", comp_name)
            set_cname(comp, "meshAppearance", MESH_APPEARANCE)
            if no_shadows:
                comp["castShadows"] = "Never"
                comp["castLocalShadows"] = "Never"
            n += 1
    assert n == 2, n
    return app, sum(hits.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alpha", type=float, default=1.0, help="opacité du décal (vanilla 0,6)")
    ap.add_argument("--fpp", action="store_true", help="remettre la coque FPP dans l'option du sélecteur vanilla")
    ap.add_argument("--no-route1", action="store_true", help="sans l'option ajoutée au sélecteur vanilla")
    ap.add_argument("--no-route2", action="store_true", help="sans les sélecteurs propres Ink Flow - Slot n")
    ap.add_argument("--files", default=",".join(FILES), help="slugs des fichiers, dans l'ordre (le premier va aussi en route 1)")
    ap.add_argument("--slots", type=int, default=2, help="nombre de sélecteurs propres")
    ap.add_argument("--slot-index", type=int, default=SLOT_INDEX,
                    help="index du premier sélecteur propre ; 3350 = en bas de la liste (v3) ; 1041 = juste sous body_tattoo (1040) "
                         "si l'ordre à l'écran suit l'index (v4, à mesurer) ; 1041-1049 libres avant fpp_body_tattoo (1050)")
    ap.add_argument("--shell", choices=["angel_tattoo", "body"], default="angel_tattoo",
                    help="coque TPP : angel_tattoo = coque de tatouage d'Angel (v1-v4) ; body = copie du corps Angel en matériau décal (v5)")
    ap.add_argument("--tag", default="", help="sous-dossier de sortie build\\out\\<tag>")
    args = ap.parse_args()
    alpha = args.alpha
    body = args.shell == "body"
    slugs = [s.strip() for s in args.files.split(",") if s.strip()]
    assert slugs and all(s in FILES for s in slugs), slugs
    slots = list(range(1, args.slots + 1)) if not args.no_route2 else []
    global OUT
    OUT = os.path.join(BUILD, "out", args.tag) if args.tag else OUT

    if os.path.isdir(SRC):
        shutil.rmtree(SRC)
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(SRC)
    os.makedirs(OUT)

    paths = {s: Paths(s) for s in slugs}
    for s in slugs:
        pp = paths[s]
        # 1. Texture : copie à l'octet (le chemin n'est pas stocké dans le fichier).
        dst = os.path.join(SRC, pp.tex)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(FILES[s][0], dst)

        # 2. Coques TPP et FPP, renvoyant vers la texture du fichier.
        if body:
            mesh, n, nv = body_shell(ANGEL_BODY_MESH, ANGEL_MESH, pp.tex, alpha)
            print(f"[{s}] mesh TPP = copie du corps Angel : {n} matériaux de peau -> décal (DiffuseAlpha = {alpha}), {nv} sommets")
        else:
            mesh, n, na = retexture_mesh(ANGEL_MESH, pp.tex, alpha)
            print(f"[{s}] mesh TPP : {n} DiffuseTexture remplacées, {na} DiffuseAlpha = {alpha}")
        save(pp.mesh, mesh)
        fpp, n, na = retexture_mesh(ANGEL_FPP, pp.tex, alpha)
        print(f"[{s}] mesh FPP : {n} DiffuseTexture remplacées, {na} DiffuseAlpha = {alpha}")
        save(pp.mesh_fpp, fpp)

        # 3. Morphtarget Angel (coque de tatouage, ou corps en v5) : baseMesh -> la coque du fichier.
        morph = load(ANGEL_BODY_MORPH if body else ANGEL_MORPH)
        base_mesh = BODY_MESH if body else VANILLA_MESH
        hits = {}
        replace_paths(morph["Data"]["RootChunk"], {base_mesh: pp.mesh}, hits)
        assert hits.get(base_mesh, 0) == 1, hits
        assert morph["Data"]["RootChunk"]["targets"][0]["name"]["$value"] == "breast_big"
        save(pp.morph, morph)

        # 4. .app : route 1 TPP + FPP (premier fichier), puis un par slot (son propre composant).
        d = f"w__{s}"
        if s == slugs[0] and not args.no_route1:
            app, h = make_app(TK_CHEST_APP, "w__chest_tattoo", TK_CHEST_MORPH, pp.morph, "entMorphTargetSkinnedMeshComponent", f"inkflow_{s}", d, body)
            print(f"[{s}] .app TPP :", h, "chemins repointés"); save(pp.app, app)
            app, h = make_app(TK_ARM_APP, "w__arm_tattoo_left", TK_ARM_MESH, pp.mesh_fpp, "entGarmentSkinnedMeshComponent", f"inkflow_{s}_fpp", d)
            print(f"[{s}] .app FPP :", h, "chemins repointés"); save(pp.app_fpp, app)
        for n_ in slots:
            app, h = make_app(TK_CHEST_APP, "w__chest_tattoo", TK_CHEST_MORPH, pp.morph, "entMorphTargetSkinnedMeshComponent", f"inkflow_slot{n_}_{s}", d, body)
            print(f"[{s}] .app slot{n_} :", h, "chemins repointés"); save(pp.slot_app(n_), app)

    # 5. .inkcharcustomization : gabarit toolkit (switcher + off + appearance info).
    cc = load(TK_INKCC)
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

    entries, names_tpp, names_fpp, loc_keys = [], [], [], []

    # route 1 : option ajoutée au sélecteur vanilla body_tattoo (patron Kylin), premier fichier.
    if not args.no_route1:
        s = slugs[0]
        pp = paths[s]
        s1 = copy.deepcopy(tk_switcher)
        set_cname(s1, "name", "None")
        set_cname(s1, "link", "body_tattoo")
        s1["index"] = 0
        s1["localizedName"] = ""
        set_cname(s1, "uiSlot", "None")
        s1["uiSlots"] = []
        s1["switchVisibility"] = 0
        s1["editTags"] = []
        names1 = [f"inkflow_{s}"] + ([f"inkflow_{s}_fpp"] if args.fpp else [])
        s1["options"] = [option(0, f"UI-Customization-inkflow_{s}", names1)]
        entries += [s1, info(f"inkflow_{s}", "body_tattoo", pp.app, f"w__{s}", ["NewGame", "Ripperdoc"])]
        names_tpp.append(f"inkflow_{s}")
        if args.fpp:
            entries.append(info(f"inkflow_{s}_fpp", "fpp_body_tattoo", pp.app_fpp, f"w__{s}", ["NewGame"]))
            names_fpp.append(f"inkflow_{s}_fpp")

    # route 2 : un sélecteur propre par slot (patron toolkit), une option par fichier, un .app par (slot, fichier).
    for n_ in slots:
        s2 = copy.deepcopy(tk_switcher)
        set_cname(s2, "name", f"inkflow_slot{n_}")
        s2["index"] = args.slot_index + n_ - 1
        s2["localizedName"] = f"UI-Customization-inkflow_slot{n_}"
        set_cname(s2, "uiSlot", f"inkflow_slot{n_}_switcher")
        s2["uiSlots"] = [cname(f"inkflow_slot{n_}")]
        s2["options"] = [copy.deepcopy(tk_switcher["options"][0])]
        s2["options"][0]["names"] = [cname(f"inkflow_slot{n_}_off")]
        off = copy.deepcopy(tk_off)
        set_cname(off, "name", f"inkflow_slot{n_}_off")
        set_cname(off, "uiSlot", f"inkflow_slot{n_}")
        infos = []
        for i, s in enumerate(slugs, 1):
            s2["options"].append(option(i, f"UI-Customization-inkflow_{s}", [f"inkflow_slot{n_}_{s}"]))
            infos.append(info(f"inkflow_slot{n_}_{s}", f"inkflow_slot{n_}", paths[s].slot_app(n_), f"w__{s}", ["NewGame", "Ripperdoc"]))
        entries += [s2, off] + infos
        n2 = [f"inkflow_slot{n_}", f"inkflow_slot{n_}_off"] + [f"inkflow_slot{n_}_{s}" for s in slugs]
        names_tpp += n2
        names_fpp += n2
        loc_keys.append((f"UI-Customization-inkflow_slot{n_}", f"Ink Flow - Slot {n_}"))

    assert entries, "au moins une route"

    def handle(i, d):
        return {"HandleId": str(i), "Data": d}

    root["bodyCustomizationOptions"] = [handle(i, d) for i, d in enumerate(entries)]
    for g in root["bodyGroups"]:
        g["options"] = [cname(x) for x in (names_fpp if g["name"]["$value"] == "FPP_Body" else names_tpp)]
    save(INKCC, cc)

    # 6. Localisation (JsonResource, gabarit Kylin) : un libellé par fichier, un par slot.
    loc = load(KYLIN_LOC)
    lentries = loc["Data"]["RootChunk"]["root"]["Data"]["entries"]
    tpl = copy.deepcopy(lentries[0])
    lentries.clear()
    for key, text in [(f"UI-Customization-inkflow_{s}", f"{FILES[s][1]} (Ink Flow)") for s in slugs] + loc_keys:
        e = copy.deepcopy(tpl)
        e["secondaryKey"] = key
        e["femaleVariant"] = text
        e["maleVariant"] = text
        lentries.append(e)
    save(LOC, loc)

    # 7. Désérialisation JSON -> fichiers du jeu, puis retrait des .json.
    jsons = []
    for d, _, files in os.walk(SRC):
        jsons += [os.path.join(d, f) for f in files if f.endswith(".json")]
    for p in sorted(jsons):
        r = subprocess.run([CLI, "convert", "deserialize", p], capture_output=True, text=True)
        ok = "Success" in r.stdout and os.path.isfile(p[:-5])
        print(("OK   " if ok else "ECHEC") + " " + os.path.relpath(p[:-5], SRC))
        if not ok:
            print(r.stdout[-2000:], r.stderr[-2000:])
            sys.exit(1)
        os.remove(p)

    # 8. .xl à côté de l'archive.
    with open(os.path.join(OUT, XL), "w", encoding="utf-8", newline="\n") as f:
        f.write("customizations:\n")
        f.write(f"  female: {INKCC}\n")
        f.write("localization:\n  onscreens:\n")
        f.write(f"    en-us: {LOC}\n")

    # 9. Pack.
    r = subprocess.run([CLI, "pack", SRC, "-o", OUT], capture_output=True, text=True)
    arc = os.path.join(OUT, ARCHIVE_NAME + ".archive")
    if not os.path.isfile(arc):
        print("ECHEC pack", r.stdout[-1500:], r.stderr[-2000:])
        sys.exit(1)
    r = subprocess.run([CLI, "archive", arc, "-l"], capture_output=True, text=True)
    print("\n".join(l for l in r.stdout.splitlines() if "\\" in l))
    print("Archive :", arc, os.path.getsize(arc), "octets")


if __name__ == "__main__":
    main()
