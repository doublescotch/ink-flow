# Passation — Ink Flow (VTK/UV CCXL Tattoo Loader)

Créée le 2026-11-01 à 2 h 45 (compartimentage demandé par Hell_Kaiser : chaque projet de création porte sa passation et son journal dans son dossier ; `cp:HANDOVER.md` ne garde qu'un renvoi). Ce fichier ne porte que **l'état vivant** : ce qui est posé, ce qui attend, ce qui n'est pas tranché. Les mesures, décisions et acquis vivent dans `ETUDE.md` ; la chronologie dans `LOG.md`.

**Pas de git tant que le proto ne tient pas** ; l'exe du builder en demandera un, ouvert, pour la confiance.

## Où sont les choses

- Projet (OneDrive) : `cp:__DEV\Projects\Ink Flow\` : `ETUDE.md` (§ 1-12), `tools\inkflow_build.py` (générateur **v0.3**), `tools\rdar.py` (index RDAR sans WolvenKit), `tools\build_canari.py` (figé, canaris v1-v5), `tools\nexus_dl.py`, `templates\` (gabarits JSON), `canari\` (v1-v5).
- Jetable (poste) : `C:\__DEV\cyberpunk\ink_flow\` : `in\` (17 archives VTK de test tirées de `3_Bodies\V's Body.zip` + catalogue `inkflow_slugs.json`), `gen\` (`mesh`, `tex`, `pack`, `out`, `verify`, `head_src` = tête HD extraite), `src\` (copies d'archives du jeu, dont les trois `*_HD_Head*`), `builds\v0\`, `v0.1\`, **`v0.2b\`** (archives posées précédemment), `canari_retire\`.
- Jeu : `archive\pc\mod\Ink_Flow.archive` + `.xl` (écriture = `WRITE_UNLOCK.txt` sur `archive\pc\mod`, 60 min, ou la formule ; jeu fermé).

## État (2026-11-01, 13 h 15)

- ~~Dans le jeu : v0.2b~~ (posée à 2 h 47, SHA-256 `52833f2e…e3bc3f`, QA validée à 2 h 50) → remplacée ; copie dans `builds\v0.2b\`.
- **Dans le jeu : v0.3, posée à 13 h 11** (formule de Hell_Kaiser, jeu fermé, SHA-256 identiques `108c324e…` / `.xl f361f55b…`) = v0.2b + **cible tête** (**127,8 Mo, 101 fichiers**, 17 tatouages dont Kala Japanese Head = tête seule et Garden Bloom = corps + tête ; `.xl` inchangé). Vérifié dépaqueté avant la pose : 22 textures identiques aux sources, coques de tête = copie du maillage HD (1 chunk, 27 591 sommets, 62 matériaux → décal), morphtargets de tête (105 cibles) repointés, `.app` conformes, switchers à 4 uiSlots (ETUDE § 12). **QA partielle par Hell_Kaiser (14 h) : Kala Japanese Head s'affiche bien** (la coque de tête rend, la section corps des infos tête suffit pour l'affichage) ; non rapportés : morphs du visage (preset, nez, mâchoire), animation faciale, cumul, mode photo.

**QA 2 par Hell_Kaiser (01/11, 16 h-17 h, sauvegarde avancée jusqu'à l'appartement H10 : miroir et mode photo disponibles)** : Kala Japanese Head **propre** ; c'est un motif de cou, le seul tatouage de tête VTK de son montage, donc **aucune confirmation visuelle possible des morphs du visage** (preset, nez, mâchoire : il les a changés, rien à voir sur le cou) ; son avis : la recette est bonne. **Les slots Ink Flow n'apparaissent pas dans le modificateur du miroir, seulement dans le créateur de personnage** : c'est voulu par le générateur, qui copie les étiquettes `editTags = [NewGame, Ripperdoc]` du gabarit vanilla des tatouages (`tools/inkflow_build.py`, `tags`) : comme les tatouages vanilla, créateur et charcudoc seulement. Pour les montrer au miroir : lire l'étiquette que porte une option visible au miroir dans un `.inkcharcustomization` vanilla (maquillage, coiffure) et l'ajouter aux nôtres (option du générateur, `--mirror`, une ligne). Mode photo : à regarder (tatouage de tête et de corps présents sur V, de face et en gros plan).

## État (2026-11-01, 17 h 15)

- ~~Dans le jeu : v0.3~~ (13 h 11, SHA-256 `108c324e…`, copie `builds\v0.3\`) → remplacée.
- **Dans le jeu : v0.3b, posée à 17 h 11** (son déverrouillage, jeu fermé, SHA-256 `a30204f80eb93d57…` / `.xl f361f55b…` inchangé ; copie `builds\v0.3b\`) = v0.3 + **`--mirror`** (étiquettes `NewGame`, `HairDresser`, `Ripperdoc` sur les 2 sélecteurs et les 54 options, mesuré dans `gen\verify\v03b`) + **18e tatouage de test : « Finn Face »** (`00_VTK_arcane_finn_tattoo_fem_standalone_head.archive`, Nexus 18402, extrait de `3_Bodies\…zip` dans `in\` **sans entrer dans V's Body** : c'est un vrai tatouage de visage, pour juger les morphs ; slug `arcane_finn_head`). **139,6 Mo, 106 fichiers**, build 123 s ; vérifié dépaqueté : 106/106, texture Finn identique à la source (SHA-256), entrées `inkflow_slot{1,2}_arcane_finn_head_head`.

## État (2026-11-01, 20 h) : builder v0.4, exe bâti et testé

- **Dans le jeu : v0.3b inchangée** (17 h 11, SHA-256 `a30204f8…`), QA 1-3 validées (affichage, miroir, mode photo, cumul tête + visage) ; recette VTK corps / bras / tête **validée par Hell_Kaiser**.
- **Builder v0.4** dans `builder\` (ETUDE § 14) : moteur `inkflow/core.py` (refonte de `tools/inkflow_build.py` v0.3, figé), `env.py`, `gui.py` (Tk), `inkflow_cli.py`, `build_exe.ps1`, `README.md`, `LICENSE` (MIT, **titulaire « Hell_Kaiser » à confirmer**), `tests/gui_capture.py` + capture. Décisions de Hell_Kaiser (19 h) : **interface Tk native**, **pas de git encore**.
- **`InkFlowBuilder.exe` 0.4.0 : `C:\__DEV\cyberpunk\ink_flow\exe\dist\InkFlowBuilder.exe`** (11,4 Mo, PyInstaller un fichier, SHA-256 dans la sortie de `build_exe.ps1`) ; venv dans `exe\venv`, maison de test `exe\home` (`INKFLOW_HOME`, config + catalogue + WolvenKit téléchargé + cache 516 Mo). **Preuves** : moteur CLI = 106/106 entrées identiques à la v0.3b, même taille ; **exe figé, cache vide, mode `INKFLOW_AUTOTEST` : 18 tatouages, 139,6 Mo, 106 fichiers identiques, 201 s** avec le WolvenKit qu'il a téléchargé lui-même (45 Mo, SHA-256 épinglée, vérifiée sur deux téléchargements) ; fenêtre capturée (`builder\tests\gui_main_2026-11-01.png`). Non testé sans clic : bouton Install (déplacement des archives VTK en conflit, sauvegarde), dialogue des doublons de noms, édition des noms (logique simple, à prendre en main par lui).
- L'exe n'est **pas** copié dans OneDrive (binaire de 11 Mo, se rebâtit en 20 s) ; à sa demande seulement.

## État (2026-11-01, 21 h) : exe pris en main, 1.0 décidée, dépôt git ouvert

- **QA 4 de l'exe par Hell_Kaiser (20 h-20 h 30) : validée.** Game folder détecté seul ; Browse vers
  un autre dossier → « CLI WolvenKit non détecté », mappé à la main (le bouton Download n'a pas été
  essayé) ; `in\` ajouté (catalogue : 20 entrées importées de `inkflow_slugs.json`) ; un nom édité à
  la main ; Build ; Install → popup de succès (`Ink_Flow.archive` + `.xl` dans `archive\pc\mod`,
  anciens dans `%LOCALAPPDATA%\InkFlow\backup\2026-11-01_200343`). En jeu : miroir OK, le nom
  édité s'affiche, **le slot actif du personnage a gardé son tatouage** après le build frais
  (slug stable par empreinte de contenu : un joueur qui ajoute des tatouages ne perd pas ses
  réglages). Un seul écart vu : rien.
- **Dans le jeu : build de l'exe 0.4.0** (20 h 03), contenu = v0.3b (18 tatouages, 2 slots,
  miroir, opacité 1,0).
- **Décisions de Hell_Kaiser (21 h)** : **livrer une 1.0 à ce stade** ; **dépôt git `ink-flow`,
  ouvert** (« tout cœur ouvert, les gens doivent pouvoir contrôler ce qu'on a fait ») : initialisé
  **en local** à 21 h 05 à la racine du projet (branche `main`, committer Hell_Kaiser, auteur Claude
  Fable 5.1), contenu = builder + tools + templates + ETUDE, LOG, HANDOVER ; `canari\` exclu
  (textures tierces). ~~Aucun dépôt GitHub créé~~ **En ligne à 21 h 25 sur son go :
  `https://github.com/doublescotch/ink-flow`, public, branche `master`** (règle : tous ses dépôts).
- **Comment l'exe choisit le corps** (question de Hell_Kaiser, réponse lue dans `core.py`,
  `find_owner`) : pour chaque cible (corps, bras G/D, tête), il cherche dans `archive\pc\mod` la
  **première archive dans l'ordre de chargement du jeu** (alphabétique, insensible à la casse) qui
  livre le maillage vanilla (`t0_000_pwa_base__full.mesh`…), sinon le jeu de base ; la coque est
  une copie de CE maillage. Donc même choix que le jeu si plusieurs corps sont chargés ; le journal
  de build l'écrit (`Body : 006_Angel_Body.archive (over …)`). Pas « Angel » en dur : tout corps
  dont le maillage a des matériaux locaux et l'apparence de peau standard passe, sinon erreur
  « unsupported body mod ». Ce qui n'est **pas** supporté : la **famille UV** (texture
  `fullbody_overlay_d01.xbm`, corps Solo), V masculin, FPP. **Conséquence à écrire dans le README** :
  changer de corps après un build = rebâtir (la coque est une copie de l'ancien corps).

## Prochain geste (1.0)

1. **Avant publication** : (a) `env.py` : test du bouton Download par lui ; (b) README : « rebâtir
   après un changement de corps » + ligne sur le slot conservé ; (c) **permissions** : les
   `templates\*.json` viennent du CCXL Tattoo Toolkit (20279) et de Kylin (localisation) : demander
   ou remplacer par des gabarits tirés des fichiers vanilla ; (d) version 1.0.0 dans `gui.py` /
   `build_exe.ps1`, exe rebâti, SHA-256 notée ; ~~(e) création du dépôt GitHub `doublescotch/ink-flow`
   sur son go, push~~ fait (21 h 25) ; (f) page Nexus (texte, captures, faux positifs antivirus annoncés).
2. **Après la 1.0** : famille UV (corps Solo), icônes dans le créateur, FPP, V masculin, poids
   (morphtarget partagé), morph changé au charcudoc (QA non cochée).
3. ~~Prise en main de l'exe par Hell_Kaiser~~ **faite (QA 4)**.
2. ~~Poser la v0.3~~ **posée à 13 h 11**.
2. **QA v0.3 à lui** (liste complète ETUDE § 12) ; les points qui tranchent : (b) la coque de tête **suit les morphs** du visage (preset, nez, mâchoire…) et (a) s'affiche tout court : c'est le seul point non lu de la recette (nos infos tête sont dans la section **corps** du créateur, le vanilla met les siennes dans la section tête). Si (a) ou (b) rate : variante = infos tête dans `headCustomizationOptions` (groupes `TPP`, `character_customization`, `TPP_photomode`) référencées depuis nos switchers du corps ; ≈ 30 lignes.
3. ~~**Décision de Hell_Kaiser (01/11, 16 h) : « on finit Ink Flow après, nouvelle session »** : QA complète de la tête~~ faite (QA 3) ; ~~**exe + interface**~~ livré (v0.4, 20 h). Reste, à son choix : **git** (il a dit « pas encore » ; à ouvrir avant toute publication), **icônes** dans le créateur, **famille UV**, **FPP**, **V masculin**, **poids** (16,4 Mo de morphtarget par tête : morphtarget partagé par dynamic materials), **morph changé au charcudoc** (point de QA non coché, non bloquant), **signature de code / faux positifs antivirus** avant Nexus.

## Décisions du 2026-11-01 (gravées ETUDE § 11-12)

- **Nombre de slots = réglage du mod**, défaut 2 (`--slots`) ; champ `group` du catalogue abandonné.
- **Rien dans le sélecteur vanilla** (`--route1` disponible, non par défaut).
- Noms ≤ 20 caractères, sans auteur, dans le catalogue `in\inkflow_slugs.json` (modifiables par lui, puis rebâtir) ; limite à remesurer avec 24-26 caractères avant de la monter.
- **Tête = même recette que le corps** (copie du maillage actif en décal + copie de son morphtarget), aucun masque de chunk : le maillage HD de tête est tout en peau (mesuré § 12).

## Ouvert (non tranché, non mesuré)

- **Section des infos tête** : corps (choisi, non lu) contre tête (vanilla) ; tranché par la QA (a)/(b).
- **FPP** : aucune coque FPP ; non testable sur sa sauvegarde (créateur seul).
- **Mode photo / miroir** : groupe `TPP_photomode` de la tête non renseigné par nos groupes.
- **Vêtements** : masques de chunks par nom de composant, jamais testé habillé.
- **Corps UV** : coque à la mise à plat UV, dérivable du corps UV (ETUDE § 5.1) ; aucune surface UV sur son montage (§ 10).
- **Couture au cou** : `femv_vtk_headpatch` (xBaebsae) et seamfix d'Angel se dessinent peut-être par-dessus la coque de tête ; à voir en QA (f).
- **Bras gauche plus clair** : vu une fois (v0), jamais revu ; non bloquant.
- **Archives d'origine encore dans le jeu** : détectées par nom de fichier seulement (empreintes d'index possibles en 0,4 s, non fait). Aucune dans le jeu à 13 h.
- **Hook** : cas 204 (listing WolvenKit d'une archive du jeu pris pour une écriture) consigné, à qualifier avec 203 en séance pipeline ; les `.app` vanilla des tatouages faciaux restent non lus.

## Attend Hell_Kaiser

- ~~**Sa QA de la v0.3 en jeu** (liste ETUDE § 12 ; points qui tranchent : la coque de tête s'affiche et suit les morphs du visage).~~ Faite le 01/11 à 16 h-17 h (QA 2 ci-dessus) : affichage OK, morphs non vérifiables sur son montage, miroir sans nos slots (voulu, à ouvrir sur décision), mode photo à regarder.
- ~~**Décision de Hell_Kaiser (01/11, 17 h) : ouvrir le sélecteur au miroir**~~ **fait (v0.3b, 17 h 11)** : étiquette mesurée sur `female_cco` vanilla (`x\van\…\female_cco.inkcharcustomization.json`) : miroir = `HairDresser` (maquillage, cicatrices, ongles, Heterochromia : `NewGame` + `HairDresser` + `Ripperdoc`) ; tatouages vanilla = `NewGame` + `Ripperdoc` seulement.
- ~~**QA v0.3b attendue**~~ **QA v0.3b (Hell_Kaiser, 01/11, 18 h) : « le Finn tattoo apparaît bien, correctement sur le visage, dans le modificateur du miroir, dans l'écran d'inventaire, en mode photo et avec le mod de troisième personne »** → (a) sélecteurs au miroir : OK ; (b) tatouage de visage affiché : OK, **suivi d'un morph changé au miroir : non rapporté, à confirmer** ; (c) mode photo : OK (le groupe `TPP_photomode` non renseigné ne manque donc pas) ; (d) cumul Finn + Kala : non rapporté. Le plantage juste après le mode photo (18 h 03) est celui d'Infinite Randomizer Framework (3e du jour, retiré ensuite), pas Ink Flow.
- ~~**Pour la prochaine séance Ink Flow** : un tatouage de VISAGE VTK (pas de cou) dans `in\` pour juger les morphs : à prendre dans ses archives ou sur Nexus.~~ Fait (Finn Face, v0.3b).
- **QA 3 (Hell_Kaiser, 01/11, 18 h 45) : (d) cumul Kala Japanese Head + Finn Face sur deux slots : les deux ensemble, bien collés à la peau : OK.** (b) suivi d'un morph CHANGÉ : non testable, le miroir n'a pas la sculpture avancée du visage (nez, mâchoire…), il faut le charcudoc, et sa sauvegarde est au début de l'intro. Son argument, que je retiens : son visage n'est pas aux options par défaut, et l'encre de Finn suit les traits autour de l'œil sur ce visage-là ; si la coque de tête ne suivait pas les morphs, on verrait déjà l'écart sur son visage actuel. Donc la copie repointée du morphtarget fonctionne au moins en statique ; le changement au charcudoc reste un point de QA à cocher plus tard, non bloquant. **Verdict de Hell_Kaiser : la recette VTK (corps, bras, tête) est validée ; prochain chantier = premier jet du builder .exe pour les utilisateurs.**
