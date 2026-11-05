# Journal — Ink Flow

Une entrée par séance ou par jalon, la plus récente en bas. Le détail (mesures, chiffres, QA) est dans `ETUDE.md` au paragraphe cité ; l'état courant dans `HANDOVER.md`.

## 2026-10-31 — Étude et canaris

- Demande de Hell_Kaiser : un sélecteur de tatouages UV/VTK dans le créateur de personnage (CCXL). Lecture des archives de tatouages, du créateur, des frameworks (ETUDE § 1-5). Nom du projet donné par lui : **Ink Flow — VTK/UV CCXL Tattoo Loader**. Forme de livraison retenue : builder complet chez le joueur, modèle Lethal Curves (§ 4 bis).
- Canaris v1 à v4 jugés en jeu : slots propres OK sous « Body Tattoos », mais la coque de tatouage passe sous la peau d'Angel. Cause mesurée : VTK affiche son calque **dans** le matériau de peau, un seul à la fois (§ 7).

## 2026-11-01 — Du canari v5 au générateur

- 0 h 30 : **canari v5** (coque = copie du corps Angel en matériau décal) validé en jeu : forme retenue (§ 8).
- 1 h 04 : **générateur v0** (`tools\inkflow_build.py`, 8 tatouages VTK corps depuis ses archives, 71,2 Mo) ; 1 h 14 posé à la place du canari ; 1 h 20 QA : le proto tient (bras gauche clair vu une fois, disparu au rechargement) (§ 9).
- 1 h 40 : mesure des bras : aucun Songbird dans le jeu, bras VTK d'Angel actifs ; devis bras (§ 10).
- 1 h 50 : **v0.1** par cible (corps, bras G, bras D ; catalogue par SHA-256 ; titres « Ink {n} » ; noms ≤ 20) posée ; 2 h 05 QA validée.
- 2 h 20 : **v0.2** : jeu de test rechargé depuis `V's Body.zip` (17 archives, 16 tatouages, renommages suivis par SHA-256), noms courts posés dans le catalogue, correctif pour les archives de 2023 dont le CLI ne résout pas le chemin (`<empreinte>.bin`) ; posée ; 2 h 35 QA validée (§ 11).
- 2 h 40 : décisions de Hell_Kaiser : nombre de slots = réglage (défaut 2), sélecteur vanilla retiré. **v0.2b** bâtie et vérifiée (91 fichiers, sans route 1), pose en attente (déverrouillage expiré) ; **posée à 2 h 47** après re-sauvegarde du déverrouillage par lui.
- 2 h 47 : v0.2b posée ; 2 h 50 **QA validée** (sélecteur vanilla vide d'Ink Flow, Ink 1 / Ink 2 normaux). Séance close sur « ça suffira pour ce soir ».
- 2 h 45 : passation et journal propres au projet créés (compartimentage demandé par lui) ; `cp:HANDOVER.md` ne garde qu'un renvoi.
- Question notée pour plus tard (Hell_Kaiser) : existe-t-il un outil communautaire de conversion UV ↔ VTK, ou faisable en CLI ? Non cherché ce soir ; le wiki cité en Sources documente une conversion manuelle entre frameworks (page « converting between tattoo frameworks »).

## 2026-11-01 (midi) — Tête VTK, v0.3

- 12 h 30 : « Reprends » ; chantier choisi par Hell_Kaiser (question in-prompt) : **tête**. Mesure du maillage de tête actif (`006_VTK_Vanilla_HD_Head_xBaebsae`) : **1 chunk, 27 591 sommets, 62 matériaux tous de peau** ; prémisse « chunks non-peau à masquer » tuée ; morphs du visage = `h0_000_pwa__morphs.morphtarget` (105 cibles, 16,4 Mo) à copier et repointer, patron Heterochromia (ETUDE § 12).
- Hook : listing de `basegame_4_appearance.archive` refusé (cas **204** consigné dans `pipeline:hooks/cas/REGISTRE.md` + `hook_cas.json`, même famille que 203) ; les `.app` vanilla des tatouages faciaux restent non lus.
- 12 h 45 : **générateur v0.3** (cible `head`, extraction à deux radicaux, `retarget_morph`) ; build 160 s, **127,8 Mo, 101 fichiers**, 17 tatouages (Kala Japanese Head = tête seule, Garden Bloom = corps + tête) ; vérifié dépaqueté (22 textures identiques, coques et morphtargets de tête conformes, options à 4 cibles). ~~**Non posée** : déverrouillage expiré~~ ; v0.2b du jeu copiée dans `builds\v0.2b\`.
- 13 h 11 : **v0.3 posée** sur sa formule (jeu fermé, SHA-256 identiques). 14 h : **QA partielle validée** (« le Kala Japanese Head fonctionne, ça s'affiche bien ») ; morphs du visage non rapportés.
- 16 h-17 h : **QA 2** (sauvegarde avancée jusqu'à l'appartement, miroir et mode photo accessibles) : Kala Japanese Head propre (motif de cou : morphs du visage sans confirmation visuelle possible) ; **slots absents du miroir** (étiquettes `NewGame` + `Ripperdoc` du gabarit vanilla, voulu : créateur + charcudoc) ; mode photo à regarder. Consigné dans `HANDOVER.md`.
- 17 h 00-17 h 11 : décision « ouvre-moi le sélecteur au miroir » ; étiquette mesurée sur le `female_cco` vanilla (`HairDresser`) ; option `--mirror` du générateur (sélecteurs, options et « off ») ; tatouage de visage de test ajouté à `in\` (VTK Arcane Finn 18402, « Finn Face », hors V's Body) ; **v0.3b** bâtie (123 s, 139,6 Mo, 106 fichiers), vérifiée dépaquetée (`gen\verify\v03b` : 56 entrées à 3 étiquettes, texture Finn identique), **posée à 17 h 11** (déverrouillage, jeu fermé, SHA-256 `a30204f8…`). QA à lui : miroir, morphs sur Finn, mode photo, cumul.
- 18 h : **QA v0.3b validée par Hell_Kaiser** : Finn Face correct sur le visage au miroir, inventaire, mode photo, troisième personne ; sélecteurs présents au miroir. Plantage à la sortie du mode photo = Infinite Randomizer Framework (`+0x24040`, 3e du jour), retiré du jeu à 18 h 31 ; pas Ink Flow. Reste à confirmer : suivi des morphs, cumul de deux têtes.
- 18 h 45 : **QA 3** : cumul Kala Japanese Head + Finn Face sur deux slots OK, tout collé à la peau ; morph changé non testable (sculpture avancée au charcudoc seulement, sauvegarde au début de l'intro) mais l'encre suit déjà un visage hors défauts : recette VTK **validée par Hell_Kaiser**. Chantier suivant choisi par lui : **premier jet du builder .exe**.

## 2026-11-01 (soir) — Builder v0.4, exe

- 19 h : devis présenté, go de Hell_Kaiser (question in-prompt) : **interface Tk native, pas de git encore**. Mesures préalables : WolvenKit Console 9.1.0 = zip GitHub de 45 Mo **dépendant du runtime .NET 10** ; PyInstaller dans un venv `C:\__DEV\cyberpunk\ink_flow\exe\venv` avec le Python 3.11 du Store fonctionne (exe Tk de 11 Mo).
- 19 h-19 h 30 : `builder\` écrit : `inkflow/core.py` (refonte de la v0.3 : exceptions, journal par rappel, catalogue par empreinte de contenu), `env.py` (jeu Steam/GOG/Epic, ArchiveXL par `version.dll`, `dotnet --list-runtimes`, téléchargement épinglé taille + SHA-256, `INKFLOW_HOME`), `config.py`, `gui.py` (Tk), `inkflow_cli.py`, `build_exe.ps1`, `README.md`, `LICENSE`. **Preuve moteur** : 18 tatouages de `in\` → 106/106 entrées identiques à la v0.3b, même taille.
- Piège mesuré : détecter les archives VTK restées dans le jeu par « livre une texture cible » attrape `006_Angel_Body` et les textures de tête HD ; retenu : archives « pures » (toutes les entrées = textures de calque connues) ou contenu identique à un tatouage choisi (ETUDE § 14).
- 19 h 40 : exe bâti (11,4 Mo), fenêtre capturée (18 tatouages, 4 voyants verts) ; **19 h 55 : exe figé testé sans clic (`INKFLOW_AUTOTEST`), cache vide, WolvenKit téléchargé par l'outil : 139,6 Mo, 106 fichiers identiques, 201 s**. SHA-256 du zip WolvenKit épinglée après deux téléchargements concordants.
- En parallèle (demande de Hell_Kaiser, hors Ink Flow) : retrait du jeu des mods `5_Visuals` + `16_World` pour son test de perf (`cp:ETAT_2.5.md`).

## 2026-11-01 (20 h-21 h 30) — QA 4 de l'exe, 1.0 décidée, dépôt git

- 20 h-20 h 30 : **QA 4 par Hell_Kaiser** : exe lancé tel quel, jeu détecté, Browse vers un autre
  dossier → « CLI non détecté », mappé à la main (Download non essayé) ; `in\` ajouté (20 entrées de
  catalogue importées), un nom édité, Build, Install (popup : archives posées, anciennes dans
  `backup\2026-11-01_200343`). En jeu : miroir OK, nom édité affiché, **slot actif conservé** après
  le build frais. Validé.
- 21 h : décisions : **1.0 à livrer**, **dépôt `ink-flow` ouvert** (« tout cœur ouvert »). Dépôt
  initialisé en local (Fable) : premier commit = builder, tools, templates, ETUDE, LOG, HANDOVER ;
  `canari\` exclu après un premier essai qui l'avait pris (commentaire en fin de ligne dans
  `.gitignore` : non supporté par git, corrigé, commit réécrit avant tout push) ; `.gitattributes`
  LF. Réponse à « comment l'exe choisit le corps » gravée dans `HANDOVER.md` (lue dans `core.py`).
- 21 h 20 : go de Hell_Kaiser pour la mise en ligne, **branche `master`** (règle : tous ses dépôts).

## 2026-11-01 (21 h 10-21 h 45) — 1.0.0 : gabarits, README, exe, page Nexus

- 21 h 10 : « Reprends » ; passations lues ; provenance des gabarits mesurée : toolkit 20279 = « template
  resource » (description Nexus par l'API ; page refusée hors navigateur, boîte Permissions non lue).
- 21 h 15 : décisions de Hell_Kaiser (question in-prompt) : **garder + créditer** ; **go sur tout le lot**
  (b, c, d, f), le test du bouton Download reste à lui.
- 21 h 15-21 h 30 : gabarits nettoyés (en-têtes sans chemin local, localisation neutre) ; `VERSION =
  "1.0.0"` ; README (rebâtir après changement de corps, slot conservé, choix du corps, limites, crédits) ;
  `NEXUS.md` (brouillon de page, anglais) ; exe rebâti (SHA-256 `13c14eaa…`) ; **autotest : 106 fichiers,
  0 octet différent hors index contre la v0.3b**, `.xl` identique ; zip d'upload `InkFlowBuilder-1.0.0.zip`
  (SHA-256 `35b5bf52…`). Jeu non touché (le build 0.4.0 posé est identique hors index). ETUDE § 15.
- 22 h : **bouton Download testé par Hell_Kaiser** sur une maison vierge (`%LOCALAPPDATA%\InkFlow` supprimé) : WolvenKit téléchargé dans `InkFlow\wolvenkit`, lié ; le jeu a été retrouvé seul (registre Steam + `libraryfolders.vdf`, `env.find_game_candidates`). Sa question sur les slots : réglage du builder (1 à 9), pas de Mod Settings ; plafond 9 = index 1041-1049 libres sous `body_tattoo` (1040), `fpp_body_tattoo` à 1050. Résumé Nexus et README reformulés (« Ink 1 to Ink 9, you choose how many »).

## 2026-11-01 (23 h → 23 h 45) — Première personne ajoutée à la 1.0.0

- 23 h : question de Hell_Kaiser sur la limite « no first-person shells » de `NEXUS.md` ; réponse
  anchrée (canari v1, QA v0, sauvegarde du début, `link` non lu) ; décision in-prompt : **ajouter la FPP
  avant l'upload**.
- 23 h 05-23 h 15 : mesures (ETUDE § 16) : `link` = clé partagée maître / suiveur ; torse FPP d'Angel
  = corps TPP octet pour octet ; masque `0xFFFFFFFFFFFFFFE0` dans `l0_000_fpp__full.app` ; bras FPP à
  matériaux locaux (le droit : `01_ca_pale_body`).
- 23 h 15-23 h 30 : `core.py` (`FPP_TARGETS`, `fpp_torso_mask`, suiveur par slot, groupe `FPP_Body`
  séparé), case « First person » (`gui.py`, `config.py`), `--no-fpp` (CLI). Build CLI sur `exe\home` :
  150,3 Mo, 157 fichiers, 129 s ; dépaqueté et contrôlé (`gen\verify\fpp1`). README, `NEXUS.md`
  (résumé 247 caractères), ETUDE § 16.
- 23 h 35 : exe 1.0.0 rebâti (SHA-256 `b1fd72db…68075` ; autotest de l'exe figé sur `exe\home` : 157
  fichiers, 150 347 776 o, 124 s, « first person on »), zip `InkFlowBuilder-1.0.0.zip` refait (SHA-256
  `c0b18ba7…4b027`) et **recopié sur sa copie dans le dossier du projet** (l'ancienne, 21 h 19, était
  sans FPP). Jeu non touché : la QA FPP est à lui (Build + Install dans l'exe, sauvegarde avec miroir).

## 2026-11-02 (0 h → 0 h 15) — QA FPP validée, interface verrouillée pendant le build

- Vers 0 h : **QA FPP de Hell_Kaiser validée** (9 slots, son pack V's Body entier : créateur, miroir,
  première personne tête baissée, mode photo ; pas de bras plus clair). Sa demande dans le même message :
  verrouiller l'interface pendant le build, avec un seul bouton Annuler.
- 0 h-0 h 09 : `core.Cancelled`, `Cli.run` par `Popen` (WolvenKit tué sur Cancel ou Ctrl+C),
  `run_build(..., cancel)`, archive partielle retirée ; `gui.py` : `_lock`, Build → Cancel,
  fermeture = annuler puis quitter. GUI pilotée : Cancel au `deserialize` propre (13 s, aucun
  WolvenKit restant, sortie vide) ; build complet identique (157 fichiers, 150 347 776 o).
- 0 h 09-0 h 12 : exe rebâti (`7df14236…`), autotest figé identique (145 s) ; zip `c1e354ae…`
  recopié sur ses deux copies.

## 2026-11-02 (13 h → 14 h 30) — Retours Nexus : corps vanilla et EBBRB mesurés

- Page Nexus en ligne (upload par lui dans la nuit) ; 15 messages le matin : trois EBBRB « slots
  visibles, rien sur le corps », un .NET, un 2.3x, deux V masculin, une idée « dynamique ». Il a purgé
  son jeu : Angel + têtes VTK + Ink Flow (9 archives), l'Ink Flow bâti la veille marche toujours.
- Mesuré (ETUDE § 17) : corps vanilla pur = **bras refusés** par `shell()` (matériaux preload), corps
  et tête OK ; EBBRB 5.0.0 téléchargé (Nexus 4654) : **tout passe** dans le moteur. Hypothèse pour les
  trois EBBRB : le builder n'a pas vu le corps (REDmod, MO2, `modlist.txt`), coque vanilla sous un
  corps à 91 k sommets. Correctifs (a)-(f) proposés, en attente de son go ; réponses Nexus rédigées.
- Perf (sa mesure, setup minimal Angel + Ink Flow, appartement H10) : ≈ 100 fps en auto léger / moyen,
  80-90 en high / ultra ; setup complet 50-60 avec micro-saccades. Mesures par piles à venir.

## 2026-11-02 (14 h → 15 h) — 1.0.1 : ordre de chargement, bras vanilla, Scan, build.log

- Go de Hell_Kaiser sur les six points et sur « commit docs + tag v1.0.0 » : docs commitées (`217ada3`),
  tag `v1.0.0` posé sur `dcf165a` et poussé.
- Code (ETUDE § 17, « Livré ») : `game_archives` (modlist.txt, REDmod, ordre MO2), `shell()` à trois magasins,
  ligne Body mesh, Scan game folder, `build.log`, `--from-game`. Preuves : tests d'ordre A → H, build CLI
  complet sur corps vanilla (157 fichiers, 71,1 Mo), exe figé identique à la 1.0.0 sur Angel (157 fichiers,
  150 347 776 o), capture de la fenêtre. Exe `fc33b615…`, zip `8b38f547…` dans `releases\`.
- README (Body mesh, Scan, MO2, Troubleshooting), `NEXUS.md` (étapes, « Slots visible but nothing on V ? »,
  changelog 1.0.1), `NEXUS_POSTS.md` (réponses à poster). Jetables : `dl\4654\ebbrb\` gardé comme fixture
  (zip supprimé), `gen\t101\` gardé (arbre factice vanilla + build de 71 Mo), `fakegameB` supprimé.
- 14 h 28-14 h 37 : sa demande « enlève Angel et bâtis un Ink Flow vanilla » ; `WRITE_UNLOCK.txt` posé par
  lui sur le dossier du jeu. Angel + refits parqués dans `C:\__DEV\cyberpunk\ink_flow\parked\…`, têtes VTK
  gardées ; premier essai à vide (sa config pointait sur des archives déplacées dans `3_Bodies\__InkFlow\`),
  second avec ce dossier : 21 archives, 9 slots, **530 fichiers, 82,6 Mo**, installé, ancien build en backup.
  Code 1.0.1 commité et poussé (`4f6d9d9`). Il demande de relire sa description Nexus publiée (altérée par
  lui) avant de retoucher `NEXUS.md` : URL de la page à obtenir.
- 14 h 40-15 h : **QA du build vanilla (corps vanilla + têtes VTK) par Hell_Kaiser : ÉCHEC**, et c'est la
  panne des utilisateurs EBBRB reproduite : au chargement de sa sauvegarde (faite sur Angel) les deux
  bras Bedellia s'affichent, propres au miroir, en mode photo et dans le créateur ; en FPP directe la
  coque de bras est « pleine de vides » (parties sous la peau) ; au miroir, un 3e slot n'affiche rien,
  les bras décochés disparaissent et ne reviennent pas ; **Confirm du créateur mort, même tous slots Off**
  (= cybercock2067). Mesuré pendant ce temps : aller-retour WolvenKit des maillages ET morphtargets
  vanilla identique à l'octet ; app des bras FPP vanilla = `fpp__full_l/r` pour V féminine (HQ pour V
  masculin) ; torse FPP vanilla = même géométrie que le corps (8 chunks, 4 641 sommets), autre table de
  matériaux ; Angel et EBBRB ne livrent pas `arms\a0_000_fpp__full.app`. Journaux RED4ext / ArchiveXL /
  Codeware : rien.
- 15 h-15 h 10 : isolement (sa demande « vanilla pur », déverrouillage prolongé) : têtes VTK parquées avec
  Angel, Ink Flow retiré, `archive\pc\mod` vide → yeux vides (option d'yeux venue des têtes VTK) mais
  **Confirm passe**. Build vanilla pur (corps, bras, tête du jeu de base, 21 archives, 9 slots : 530
  fichiers, 73,2 Mo, 92 s) posé à 15 h 10 ; QA en cours. Variante `--no-fpp` bâtie en réserve (`outD_nofpp`).
- 15 h 10-16 h 45 : sept poses (tableau ETUDE § 17) : Confirm passe sur vanilla pur **sans** Ink Flow ;
  build Angel sur corps vanilla : miroir OK ; vanilla FPP on : KO ; matériaux embarqués : KO ; **sans FPP :
  OK** (bras décalés en FPP) ; FPP bras seuls : KO. Mesures : aller-retour WolvenKit à l'octet, os identiques,
  blob v20 sur les bras FPP vanilla, paramètres d'attache des bras FPP vanilla lus. Cause non trouvée.
- 16 h 50 : décisions de Hell_Kaiser : **sonde / logger complet en jeu, dans une nouvelle session** ; jeu
  remis dans l'état d'hier soir (Angel, têtes, build Angel). 1.0.1 **non publiable** en l'état (passation).

## 2026-11-02 (17 h → 18 h 15) — Sonde en jeu : la FPP n'était jamais appliquée, `linkController` ; .NET installable

- 17 h : reprise (Fable). Redscript absent de son jeu (binaires macOS posés par WolvenKit, confirmé par lui :
  déjà vu sur Redscript et TweakXL) ; posé depuis le zip 0.5.32 avec la sonde `InkFlow_Probe` (Codeware :
  ressources, cycle de vie des pantins, composants de maillage, F9 = marqueur), compilée hors jeu d'abord
  (ETUDE § 18). `ModLog` finit dans `cyber_engine_tweaks\gamelog.log`.
- 17 h 12-17 h 17 : passage 1 sur Angel par lui (le premier F9 a fait un quickload : raccourci retiré). En FPP,
  « tatouage sous la peau par endroits, démarcation qui bouge » ; journal : coques TPP attachées au pantin FPP,
  aucune coque FPP jamais demandée. Cause lue dans le vanilla : `linkController = 1` sur le maître, 0 chez nous.
- 17 h 25-17 h 45 : correctif `core.py` sur son go, build sur Angel (`tools\probe\angel_build.py`), installé,
  sonde v2 (dump du `.inkcharcustomization`) ; passage 2 par lui : **bras corrects en FPP, mode photo bon** ;
  journal : trois coques FPP attachées et chargées, `linkController=true` vu par le jeu.
- 17 h 50-18 h 10 : sa demande « éviter les soucis de runtime » : bouton **Install .NET Runtime 10** (installeur
  Microsoft x64 épinglé, silencieux ; redistribution permise mais inutile), capture `.10 Runtime.png` abandonnée
  (elle surlignait le binaire Linux). Exe 1.0.1 rebâti `f32d59bc…`, autotest 157 fichiers, zip `42fa8310…`
  dans `releases\`. README, NEXUS.md à jour. Sa question : Redscript chez Angel = scripts d'ArchiveXL, pas requis
  par Ink Flow (ArchiveXL + RED4ext seuls) ; bras cybernétique jamais testé (passation).

## 2026-11-02 (17 h 50 → 18 h 30) — QA corps vanilla avec le correctif : validée ; sonde retirée ; page Nexus récrite

- 17 h 50 : reprise (Opus puis Fable) sur « test avec vanilla maintenant qu'Angel est revalidé ». Build vanilla pur avec
  le correctif (`tools\qa_2026-11-02\build_pure_link.py`, 530 fichiers, 73,2 Mo, SHA `c0c4bbb4…`, 62 s) ; sur son
  déverrouillage : Angel, refits, 4 têtes parqués, Ink Flow seul dans `archive\pc\mod` (17 h 56), ancien build dans
  `backup\2026-11-02_175618`.
- 17 h 57-18 h 10 : **QA de Hell_Kaiser validée** : sauvegarde Angel avec tatouages → repris et affichés sur le vanilla
  au chargement, changement au miroir sans défaut, Samurai suit la peau partout (modificateur, reflet, FPP, photo) ;
  sauvegarde sans slot : idem ; créateur de nouvelle partie OK. Sonde : 6 927 lignes, 0 échec, 3 coques FPP attachées
  (ETUDE § 18, passage 3). Le Confirm mort du § 17 était le même défaut (`linkController = 0`).
- 18 h 15 : jeu remis (Angel, têtes, build `a6fd24c8…` de 17 h 28, 9 archives) ; **sonde retirée** sur sa décision
  (source gardée dans `tools\probe\`), journaux copiés dans `tools\probe\logs\2026-11-02_181554`.
- 18 h 20 : page Nexus publiée (36814) lue par l'API (`gen\nexus_36814_desc.bbcode`) : sa version garde un bandeau
  « UPDATE IN PROGRESS », des crédits, l'AppData, les captures. `NEXUS.md` récrit dessus : résumé avec FPP et 1 à 9,
  prérequis (.NET installé par le builder), section **What works with what** (Angel et vanilla vus en jeu, EBBRB accepté
  par le builder non vu, cyberarms non testés, corps à jour pour 2.5 requis), dépannage « Slots visible but nothing on
  V? », changelog 1.0.1 avec la ligne vanilla. Ses questions : EBBRB = théorie seulement ; famille VTK = critère
  technique du builder (matériaux locaux, apparence de peau standard), pas une liste ; un corps cassé sur 2.5 reste cassé.

## 2026-11-03 (17 h 30 → 18 h 45) — V masculin : mesures, moteur, builds hors jeu, pose vanilla pour QA

- Reprise (Opus) sur « miroir pour V masc vanilla puis Gymfiend ». Téléchargés par lui dans `3_Bodies\__RAM` :
  Gymfiend VTK 1.4.3 + MV Head VTK + options (6423), Hyst EBB 5.0, VTK Vanilla HD 7054, Kala Japanese Faded MV
  (7414) ; décompressés dans `C:\__DEV\cyberpunk\ink_flow\dl\{6423_*,4654_ebb,7054_vtkhd,7414_kala_mv}`.
- Mesuré (jeu de base, lecture seule) : V masculin = chemins `player_man_average` / `masculine` / `pma`, corps SANS
  morphtarget (composant garment), FPP = maillages TPP (corps sans masque, bras HQ), `male_cco` liste `body_tattoo`
  dans FPP_Body + TPP_Body + character_creation (pas de suiveur), index 1041-1049 libres. `shell()` accepte vanilla
  masculin, Gymfiend (corps 6 357 sommets) et MV Head (100 morphs). VTK Vanilla HD : accepté en entier (91 362).
- Moteur (son go) : table masculine (`m_body`, `m_arm_l/r`, `m_head`), `inkflow_pma.inkcharcustomization` sous
  `male:`, `gender_customization()`, préfixe de noms étendu aux formes MV, ligne Body mesh par genre. Non-régression :
  20 tatouages féminins, HEAD contre nouveau moteur = 500/500 fichiers identiques, `.xl` identique
  (`tools\qa_2026-11-03\regress_female.py`). Builds : vanilla masculin 14 tatouages 51,1 Mo ; Gymfiend 42,9 Mo ;
  mixte 34 tatouages 119,7 Mo (`male_build.py`, `check_mixed.py`).
- 18 h 33 : plantage à la sortie de son jeu (DEP après le déchargement de RED4ext, 1 sortie sur 5) : module non
  identifiable dans le dump ; candidat non prouvé audioware 1.10.1-rc.0.
- 18 h 45 : instance remise par lui aux piles 1-2 ; sur son go, build masculin vanilla posé
  (`tools\qa_2026-11-03\game_pose.py vanilla`, SHA `05dd72c8…`). QA attendue : nouvelle partie, V masculin, créateur.
- 19 h-19 h 40 : QA 1 de lui (V masc vanilla) : bandes trouées ou rien sur 9 tatouages, propres sur 5 ; règle sans
  exception sur 14 : texture à 1 mip ou chaîne complète = propre, chaîne tronquée (11 mips sur 4096) = cassée, même
  coque. Texture décodée saine. Canari (Kala V2 masc ré-encodé par WolvenKit export → import, 13 mips) : **propre en
  jeu**, l'original troué. Côté V féminine (même build) : tout bon sauf têtes Kala et Finn sur tête vanilla (défaut
  connu § 17, chantier à part sur sa décision). Sur sa consigne, jeu de test = ses 3 `002_Tattoos_Masc_V_` (seul le
  VTK est pris) + VTK féminins, plus de Kala Faded ni de vanilla Gymfiend.
- 19 h 40 : sur son go, `reencode_truncated()` dans `extract_textures` (export du dossier, mips lus dans l'en-tête
  DDS, import des seules chaînes tronquées) ; non-régression féminine 500/500 rejouée ; build vanilla posé
  (81,4 Mo, SHA `4d878353…`). QA attendue : Kala Japanese V2 masculin propre.
- 20 h-20 h 30 : sur son go « tout, 1.1.0 » : README, NEXUS.md (1.1.0 : V masculin, What works with what, VTK
  Vanilla HD reported working, tête vanilla en limite, changelog), version 1.1.0, exe `24434274…` (autotest figé
  `exe\home` + Kala V2 masc : 19 tatouages, 162 fichiers, 75,6 Mo, ré-encodage au journal), zip `43f0f655…` dans
  `releases\`, ETUDE § 19, passation. Jeu nettoyé sur sa demande (`game_pose.py remove`).

## 2026-11-03 (soir) → 04 — 1.2.0 : tableau des corps détectés, opacité par tatouage

- Sa demande : récapitulatif des corps lisible (féminin / masculin, éléments de corps, tableau) ; opacité par
  tatouage demandée par un utilisateur. Livré dans `gui.py` (cadre « Body meshes in use », colonne Opacity, bouton
  Opacity…, « Default opacity ») et `core.py` (`Catalogue.alpha`, `Item.alpha`) ; README à jour (ETUDE § 20).
- Preuves : coques re-sérialisées (0,6 / 0,85 / 1,0 selon le catalogue) ; exe figé autotesté (157 fichiers,
  Samurai à 0,6) ; non-régression 488/488 et `.xl` identiques contre la 1.1.0 ; captures de la fenêtre.
- Sa réponse : 1.1.0 déjà uploadée ⇒ **1.2.0** : version, exe `4e3f15d1…`, zip `3e1f13f9…` dans `releases\`,
  `NEXUS.md` (étapes 1 et 3, dépannage, changelog 1.2.0, fichier à envoyer, capture de la fenêtre à refaire).
- 04/11 : retour du demandeur : colonne Opacity refuse 1,5 alors que l'opacité générale à 1,5 marche en jeu.
  Bornes 0,1-2,0 partout (`gui.ALPHA_MIN` / `ALPHA_MAX`), parseur testé ; code seul, exe non rebâti (sa décision).

## 2026-11-04 (12 h → 13 h) — Support UV : mesure des mises à plat, architecture, devis (Fable, lecture seule)

- Reprise sur « Reprends » : premier geste de la passation. Framework UV 3.2.1, Solo 2.0, bras UV
  (Solo, Songbird), Songbird Body UV et 5 tatouages UV dépaquetés depuis `V's Body.zip` dans
  `C:\__DEV\cyberpunk\ink_flow\dl\uv\`, sérialisés, matériaux et UV lus (ETUDE § 21 ; scripts
  `tools\qa_2026-11-04\`). Rien posé dans le jeu ; son déverrouillage du dossier du jeu (12 h 14)
  n'a pas servi.
- Trouvé : le framework livre les maillages vanilla et branche le calque par sa chaîne de `.mi` ;
  corps vanilla = framework = Solo = Songbird = corps masculins (même mise à plat) ; Angel range ses
  pieds dans la bande u < 0,22 que le framework réserve aux bras UV ; bras VTK = mise à plat vanilla
  (texture à part), bras UV = bande du corps.
- Export PNG : le CLI refuse « -o » depuis Git Bash (« Please fill in an output path »), passe en
  PowerShell. Ré-encodage BC7 chronométré : 166 s pour un 8K, 25 s pour un 4K. Deux pièges hors UV :
  coque sur Songbird (chunks cyber à masquer), `.app` de Solo non sérialisables par le CLI 9.1.0
  (build sur Solo à vérifier).
- Architecture écrite (ETUDE § 21, cinq points) ; devis présenté, go attendu avant la première ligne
  de code.

## 2026-11-04 (13 h 30 → 15 h) — Support UV codé : moteur 1.3.0, preuves hors jeu (Fable, go « maintenant »)

- `core.py` : `TEX_TARGETS` (une texture, plusieurs cibles), `Entry.tex` / `family`, `Item.targets`
  propre, `mesh_layout()` (mise à plat des bras, masques peau et bande), `shell_mask()`, saut des
  bras de l'autre famille et de leur compagnon FPP, texture UV copiée une fois, morphtarget lu à
  part ; `gui.py` : libellé « (UV) » ; version 1.3.0 ; README et `NEXUS.md` (changelog 1.3.0, « Arms
  and families »).
- Trouvé en bâtissant : le framework UV livre la tête vanilla sans son morphtarget → la 1.2.0
  refusait tout build à cible tête sur un jeu avec le framework ; `extract_mesh` lit désormais le
  morphtarget chez son archive gagnante (jeu de base ici).
- Preuves : arbres factices `gen\uv104\` Solo (194 s, 116 fichiers) et Angel (70), contrôlés par
  `uv_check.py` ; non-régression 380/488 identiques, 108 `.app` de bras gauche = masque du port de
  lien seul, `.xl` identique. Exe non rebâti ; banc en jeu à lui (passation). Commits poussés.

## 2026-11-04 (13 h 50 → 14 h 30) — Banc sur SON Angel : validé ; chevilles par bande effacée ; rousseur à 2,0

- Sa consigne : tester d'abord sur Angel. `game_build.py` : sa config + les 16 UV du zip, build sur
  son jeu en lecture, installé jeu fermé. Premier build : tête masculine Leon Face
  (`01_ca_pale_d01`) non reconnue comme peau → coque vide ; règle en préfixe + garde-fou, rebâti,
  installé (331 Mo, `dfe0d567…`).
- Son QA : tout à l'attendu (VTK comme avant, UV = corps propre, bras et pieds nus, masculin bon).
  Deux points : arrêt du tatouage un peu haut sur la cheville (chunk 6 masqué) ; FrecklesV invisible
  (texture pâle, mesurée). Ses go : bande effacée dans une copie de la texture (`blank_uv_strip`,
  `--keep` garde le BC7, 8K ≈ 55 s) ; opacité 2,0 pour FrecklesV. Rebâti (716 s, 314 Mo,
  `cec96ac7…`), installé 14 h 23. QA attendue.
- Sa question « couche métallique » (retour Nexus sur un retexture David) : le décal vanilla n'a que
  la diffuse ; piste = le décal à `RoughnessTexture` / `MetalnessTexture` vu dans le corps Songbird
  (ETUDE § 21), chantier à part.
- Steam 14 h 05 : 63 Ko téléchargés, manifest verrouillé intact, aucun fichier du jeu modifié
  (vérifié).
- 14 h 35 : son QA : chevilles validées (= Samurai VTK) ; FrecklesV toujours invisible → version VTK
  mesurée aussi pâle : limite des coques gravée (README, NEXUS, ETUDE). 14 h 50, sur son go : exe
  1.3.0 `1b9c6a6b…` (autotest figé 157 fichiers, 150 347 776 o, 321 s), zip `8ac7a3e6…` dans
  `releases\` ; `NEXUS.md` « Files to upload ».

## 2026-11-04 (15 h → 16 h 25) — Conversion des bras UV ↔ vanilla : mesure, 1.4.0, pose (Opus, « Reprends »)

- Chantier choisi par lui (§ 21 point 4). Mesure hors jeu : bras vanilla et bras du framework
  appariés à 99,99 % (14-50 µm) ; Bedellia converti lisible ; bras d'Angel à 0,7 texel du vanilla ;
  encodage `--keep` 4K sur gabarit 8K = BC7, 13 s. Paires UV / VTK des auteurs repeintes : sans
  valeur de preuve. ETUDE § 22.
- Son go « dans les deux sens » : `armconv.py` (numpy seul), `core.py` (références, cache, bras sans
  encre retirés, compagnons FPP). Sa question : les bras Solo ne sont pas écartés du build, seulement
  de la table (autre géométrie) ; la coque reste une copie des bras Solo.
- Bancs factices Solo, Angel, Angel + framework ; non-régression 947 / 947 ; build sur son jeu réel
  1 115 s ; posé 16 h 17 (son déverrouillage, jeu fermé). Commit `5799364`. QA en jeu attendue.

## 2026-11-04 (17 h → 18 h) — QA 1.4.0 : Samurai UV contre VTK, l'épaule nue est la peinture (Fable, « Reprends »)

- Son retour (captures) : Samurai UV sur Angel = deltoïde gauche nu, le VTK y a un gros amas. Sa
  question : bonne approche ? convertir les UV en VTK plutôt ? Confusion annoncée.
- Hors jeu, rien posé : couture corps / bras d'Angel = vanilla (`seam.py`) ; haut du bras (z > 1,42)
  vide dans les 5 textures UV ET dans la texture de bras VTK (`seam2.py`) ; mise à plat du corps
  d'Angel à l'épaule = vanilla à 1-2 texels (`seam4.py`) ; rendu logiciel A / B / C (`seam5.py`) :
  UV sur Angel = UV sur framework. Verdict : deux peintures, rien à coder. ETUDE § 23, images dans
  `canari\seam_2026-11-04\`. Un script d'essai (recouvrement, trop lent) supprimé dans la séance.
- Réponse sur l'approche gravée (§ 23) : la chaîne est déjà la conversion vers le corps actif.
- 18 h 15 : il me reprend deux fois : même auteur, même tatouage (pas « deux compositions ») ; le
  défaut touche tous les UV, donc la chaîne, pas un peintre. Différence pixel à pixel (`seam7.py`) :
  corps identiques à 98,5 %, bras divergents (bande z 1,36-1,46 encrée en VTK, vide en UV). Ma
  conclusion « rien à coder » barrée (§ 23, correction). Kala V2 sans bras : pas une paire utile.
- 18 h 35 : **sa décision** : banc Solo 2.0 (UV sur corps natif) AVANT les UV sur VTK. Il ferme.
  Ligne « Same name, two paintings » retirée de `NEXUS.md` (jamais publiée).

## 2026-11-04 (17 h 35 → 18 h, horloge du poste) — Banc Solo 2.0 posé dans son jeu (Fable, « Reprends », « unlock »)

- Son déverrouillage (`WRITE_UNLOCK.txt` sur le dossier du jeu, 17 h 33) et jeu fermé : Angel +
  `.xl` + refits vanilla parqués (`parked\2026-11-04_angel\`), Solo OG 2.0 + `.xl` + bras Solo UV
  posés depuis `dl\uv\`. Script `tools\qa_2026-11-04\solo_bench.py` (park / build / install /
  restore / status), refuse d'écrire si le jeu tourne.
- Build 1.4.0 sur son jeu tel quel (sa config + 16 UV, 35 tatouages, 9 slots) : 1 339 s, 346,8 Mo,
  1 415 fichiers ; corps Solo détecté en mise à plat vanilla, bras Solo UV en bande ; bras VTK
  convertis vers la bande (8K, 34-39 s chacun ; Kala Arm en 4K) ; `.app` de Solo illisible → masque
  FPP vanilla (connu, § 21). Installé 17 h 59 (`1e97af4f…`), l'Angel dans `backup\2026-11-04_175841`.
- À lui : l'épaule du Samurai UV au créateur (§ 23). Passation réécrite, renvoi `cp:HANDOVER.md`.

## 2026-11-04 (18 h → 19 h 15) — Bras convertis retournés verticalement : trouvé par 3 canaris, corrigé (Fable)

- Son QA Solo : Unknown Samurai UV = corps + bras, épaule pleine ; Samurai VTK = corps OK, **aucune manche**.
  Hors jeu, rien ne distingue bras converti et bras UV (en-têtes, coques, créateur, archive, Oodle du jeu,
  mips, BC7 décodé indépendamment) : seule reste l'orientation de l'image, invisible sur une texture UV
  (bras droit = miroir vertical du gauche).
- Canari 1 (textures échangées) : la texture convertie est en cause. Canari 2 (moitié haute seule sur
  les deux bras) : manche à droite → le jeu lit v = 1 − y/h. Correctif `armconv` (v inversé, cache
  `v2`), canari 3 validé par lui : deux bras complets, même dessin que l'UV. ETUDE § 24 ; § 23 barré
  (bande « vide », remplissage depuis le corps : artefacts de la lecture miroir).
- Sa consigne : builds de test = seulement les tatouages testés (mémoire). Trois plantages, tous jeu
  en arrière-plan, non attribués. Jeu laissé avec Solo + build de 2 tatouages ; builds complets périmés.

## 2026-11-04 (19 h 20 → 19 h 45) — Build Solo complet avec la conversion corrigée, non-régression 947/947, page 1.4.0 préparée (Fable, « Reprends »)

- Reprise sur la passation : jeu fermé, Solo posé, canari de 2 tatouages encore installé. `solo_bench.py build`
  relancé (sa config + 16 UV, 35 tatouages) : 14 min (les 15 conversions refaites, clé de cache `v2` ; le reste
  en cache), 348,1 Mo, SHA `6bf974d1…`, aucune archive en conflit. Rien écrit dans le jeu : l'installation
  attend sa formule sur le dossier du jeu.
- Lu au journal : corps Solo en mise à plat vanilla, bras G / D Solo UV (bande, 100 %), 13 bras VTK convertis
  vers la bande (Samurai 68 % du bras encré contre 56 % avant le correctif, Kala Arm 56 / 51 %, Bedellia 33 / 35 %,
  Vale 36 %, Cover Me In Gold 1 %, Promiscuity 3 / 4 %), Pirate Vince (M) vers vanilla ; `.app` de Solo
  illisible (masque FPP du torse = vanilla, connu).
- Non-régression 1.3.0 (`31bc458`) → arbre courant sur le faux arbre vanilla : 947 / 947 fichiers identiques,
  `.xl` identique. `regress_female.py` prend maintenant la référence git en argument (HEAD par défaut).
- `NEXUS.md` : blocs 1.4.0 (page, « Arms and families », limites, « How it works », changelog, fichiers à
  poser) avec les statuts non vus entre crochets ; lien du framework = Nexus 3783 (-KS- UV Texture Framework,
  vérifié par l'API ; son 3.2.1 vient de son zip, même mod supposé, à confirmer par lui). README : Solo vu
  au créateur (corps + deux bras, VTK convertis compris).
- 19 h 44 : sa formule reçue, jeu fermé : `solo_bench.py install`, build Solo complet (348,1 Mo) dans son jeu, canari 2
  dans `backup\2026-11-04_194421`. À lui : QA Solo au créateur puis FPP, miroir, photo, TPP.

## 2026-11-04 (19 h 45 → 20 h 15) — QA Solo : Samurai VTK validé, plantage au miroir ; rapports lus, télémétrie posée (Fable)

- Son QA : Samurai VTK propre partout (créateur, miroir, FPP au miroir) ; FPP hors miroir = ventre nu (masque FPP
  vanilla, § 21, à corriger) ; plantage en défilant au miroir avant les UV. Sa position : « ça vient de nous ».
- Rapports : 4 plantages 18 h 13-19 h 50 (gel 120 s ; 2 × `memcpy` de texture `exe+0x196A3CC` source perdue ;
  `D3D12Core` lit `0x98`). Carrés de 1 980 / 2 204 unités de 16 o dans la pile : aucune texture du build ni de
  Solo / framework (70 en-têtes exportés, toutes puissances de deux). 24 rapports depuis le 28/10, 20 avant Ink Flow.
- Poste au repos : VRAM 3,0 / 8 Go, RAM 19,9 / 32 Go. Télémétrie `vram_log.py` posée (1 s) ; test à jouer : même
  défilé au miroir, puis le même sans `Ink_Flow.archive`. Remèdes mémoire listés, rien codé avant la mesure.

## 2026-11-04 (20 h 15 → 21 h 55) — Plantages : en-têtes de texture faux chez Kala, correctif, canari 3 (Fable)

- Télémétrie : VRAM 7,35 / 8 Go et RAM 29 / 32 Go au plantage de 20 h 14 (défilé au miroir, +1 Go en 75 s) ; VM et
  Opera coupés + 420 archives parquées (`minimal_bench.py`) : défilé OK, mais chargement de sauvegarde planté à
  5,5 Go VRAM avec la même signature `memcpy`. Sa position : « ça vient de nos dernières modifs ».
- 70 en-têtes de textures exportés (build + Solo + framework) : trois textures de Kala (V2 VTK, V2 UV, V2 With Sleeves)
  déclarent 1 mip / 1 398 128 o sur un tampon de 22 369 648 o = le dépassement de 1,44 Mo des rapports. Angel réparait
  par accident (bande effacée = réimport). Le pack masculin Kala V2 (§ 19) a le même en-tête. ETUDE § 25.
- Correctif `core.normalize_textures` (sérialisation + reconstruction `--keep`, BC7 conservé), validé hors jeu sur
  4 archives, non-régression 944 / 947 (les 3 Kala), commit `3ff9324`. GUI : hauteur des lignes à la police (post Nexus).
- Canari 3 (Kala V2 UV + Samurai VTK, jeu minimal) : passe 1 non corrigée → gel watchdog au 3e chargement (pas la
  signature `memcpy`) ; les 3 gels du jour ont le même fil principal (crochet Present, DLL anonymisée). Passe 2
  corrigée installée 21 h 50, verdict attendu. Post Nexus Solo : instable au chargement (hypothèse concurrente).
- 21 h 57 : **passe 2 (moteur corrigé) plantée au chargement, même signature `memcpy`** : le défaut d'en-tête n'est
  pas la cause. Prochain canari : mêmes 2 tatouages sur Angel, jeu minimal (passation). Lancement lent du jeu minimal
  noté (2 min avant le chargement). Session close à 22 h 05, jeu laissé minimal, formules de retour dans la passation.

## 2026-11-04 (22 h 05 →) — Reprise : lancement lent tranché, canari Angel à poser (Fable)

- Jeu trouvé tel que laissé : fermé, minimal (Solo + 6 entrées, 420 parquées), aucun rapport après 21 h 57.
- Lancement lent = constant, pas le parc : 66 s jusqu'au menu pour le jeu complet (20 h 11, 191 `.xl`) comme pour le
  minimal (21 h 55, 3 `.xl`) ; audioware 18 s à chaque lancement ; sauvegarde ≈ 40 s. Rien à déplacer.
- Déverrouillage du jeu expiré (`WRITE_UNLOCK.txt` de 20 h 55) ; re-enregistré par lui à 22 h 09.
- 22 h 09-22 h 12 : `solo_bench.py restore` (Angel revenu, Solo parti), `canari3.py build` sur Angel (132 s, 33,1 Mo,
  Kala sans encre aux bras donc aucune conversion, Samurai VTK tel quel), `install` ; jeu minimal gardé. Verdict à lui :
  plante ⇒ nous hors conversion ; tient ⇒ Solo ou les bras convertis 8K (à départager ensuite).
- 22 h 30 : passation réécrite sur sa remarque (« log d'état ») : 22 blocs État barrés retirés, 796 → 111 lignes ;
  `cp:HANDOVER.md` § 1 réduit au renvoi. Mémoire : 3e rappel sur le barré dans la passation.
- 22 h 20-22 h 32, sa QA du canari Angel : 3 chargements + longues bascules de slots, **aucun plantage `memcpy`** ;
  **sa décision : Solo parqué, priorité aux corps VTK**. 22 h 32 : gel watchdog, jeu en arrière-plan pendant qu'il
  écrivait, mémoire plate.
- Dumps des 4 gels relus (`dump_frame.py`, scratchpad) : même fil principal bloqué dans le greffon NVIDIA Reflex
  (`sl.reflex.dll`, chargé sous `170_E658703.dll`, `+0x3C43D`), Reflex Disabled dans ses réglages ; ReShade, overlay
  NVIDIA, GPU Tweak (allumé, aucune DLL dans le jeu) hors pile. Première lecture fautive corrigée dans le tour (module 170
  `nvrtum64.dll` : le « 170_ » est le nom du fichier NGX, pas l'index). ETUDE § 25, fin. Test à lui : GPU Tweak fermé.
- 30 rapports depuis le 28/10 relus : trame Reflex dans aucun gel d'avant le 04/11, 7 « GPU crash » le 28/10 avant
  Ink Flow ; ReShade chargé dès le 03/11 ; GPU Tweak absent du dépôt (sa question) ; deux GPU Tweak installés (appli +
  compagnon mobile), désinstallables sans overclock. Décision à lui.
- 23 h 02 : GPU Tweak désinstallé par lui, redémarrage, créateur + Alt-Tab : gel, même pile Reflex (5/5). GPU Tweak
  éliminé. Prochain : compteur FPS NVIDIA coupé, puis `sl.reflex.dll` renommé.
- 23 h 08-23 h 24 : overlay NVIDIA coupé (réglage, pas le raccourci), jeu relancé, créateur + Alt-Tab : 16 min sans
  gel, aucun rapport. Direction : overlay NVIDIA. Sa décision : on avance (retour au jeu normal, rebuild corrigé).

## 2026-11-05 (0 h → 0 h 40) — Instance régénérée par lui, build complet 1.4.0 sur son pack à jour, installé (Fable)

- Il a vidé l'instance et l'a régénérée depuis son backup « Virgin » (plugins WolvenKit réinstallés sauf deux posés à la
  main), piles 1 à 3 posées (Angel sans bras, refits, tête VTK HD, framework UV 3.2.1 ; Gymfiend oublié : V masculin
  vanilla). Le parc de 420 archives n'existe plus : `unpark_all` sans objet.
- Premier build lancé sur sa config du 04/11 (21 + 16 UV de `dl\uv`) : arrêté sur sa remarque, 7 archives de son dossier
  manquaient (Masc UV/VTK ONI V, Masc UV Kala V2 ± Sleeves, VTK ONI V, VTK FrecklesV, VTK Finn Head). Nouveau script
  `tools\qa_2026-11-05\pack_build.py` : tout `3_Bodies\__Tattoos` (44 archives), même cache `work_game`.
- Build : 1 007 s, 42 tatouages (Tortured Skin UV ×2 refusés : 3 fichiers inconnus chacun), 19 bras convertis, 2 UV sans
  encre aux bras (Kala V2, Anal Slut), en-têtes Kala reconstruits, aucun conflit ; 465,8 Mo, 1 632 fichiers, SHA
  `da5757d2…`. Installé à 0 h 36 sur son déverrouillage de 23 h 45 (aucune sauvegarde : instance neuve).
- Ses questions : cache de l'exe ≠ cache des bancs (`%LOCALAPPDATA%\InkFlow\work` contre `gen\uv104\work_game`) ;
  FrecklesV UV = rien d'exclu (corps, 2 bras, tête) ; Cover Me In Gold = rugosités ignorées (décal diffuse seule).
  Son test à faire : FrecklesV en classique sans Ink Flow (taches invisibles en jeu, les deux versions sont pâles).

## 2026-11-05 (0 h 40 → 2 h) — Sa QA : créateur bon, mais trous à l'inventaire / photo et rien sur le corps en FPP (Fable)

- Sa QA 1.4.0 : créateur fem et masc V tout bon (sauf Skeleton Face sur tête masc vanilla : tête vanilla, connu) ;
  Samurai coupé net à la cheville sur Angel (pieds dans la bande, § 21) ; puis mode photo troué en bas des tibias,
  inventaire troué ailleurs, FPP tête baissée = manches sans corps. Page Nexus / README / sticky 1.4.0 écrits puis
  **repris : mentions « vu en FPP et mode photo » retirées, upload gelé**. Exe 1.4.0 bâti (SHA `a1bf1701…`), zip non fait.
- Éliminations : overlay / archives (config minimale `minimal_angel.py`, identique) ; build (octets identiques au
  16 h 17, chaîne de non-régression) ; LOD (un seul niveau) ; textures High (pareil). Lui : instance re-régénérée depuis
  Virgin, Samurai seul rebâti avec les exe 1.3 / 1.2 / 1.1, puis 1.1 sur corps vanilla : **identique partout** → pas
  une régression. Deux retours Nexus sur la FPP relus par lui, réponse éditée (confirmé).
- Mesuré : masque du torse FPP d'Angel = chunks 5-7 = mollets et pieds (hauteurs lues), le torse vient de `Body:ANGEL` ;
  notre coque FPP copie le maillage complet avec ce masque. Correctif défini (ETUDE § 26). Trous à distance : ouvert,
  deux mesures listées. Session close à 2 h ; son jeu : instance Virgin + Load Begone + build 1.1 Samurai sur vanilla.

## 2026-11-05 (14 h → 14 h 50) — Correctif FPP : le corps est dessiné par deux apps, coque de torse ajoutée, canari bâti (Fable)

- « Reprends » : Cyberpunk choisi in-prompt (passation la plus récente). Mesures hors jeu avant de coder (ETUDE § 27) :
  torse FPP vanilla extrait = même découpe que le corps complet (8 chunks, mêmes hauteurs) ; `l0_000_fpp__full.app` est
  l'app des **jambes** (masque `…E0` = mollets et pieds, vanilla compris) ; l'app du **torse** est `t0_000_fpp__full.app`
  (masque `…FF1F` = chunks 0-4) ; `Body:ANGEL` = étiquette sans maillage, le § 26 se trompait sur ce point.
- Sonde du 02/11 relue : le pantin FPP porte le torse FPP garment à `…391` et le corps morph à `…584` ; notre coque à
  `…584` = les mollets qu'il a vus. 130 archives indexées : Angel, Solo, Songbird livrent jambes + torse FPP, jamais
  l'app du torse (prise au jeu de base).
- Codé dans `core.py` : compagnon `fpp_torso` (copie du torse FPP actif, masque de l'app torse), `fpp_body` devient
  « FPP legs », `fpp_app_mask` lit les deux apps avec repli, `FPP_BY_PARENT` en listes, 4 uiSlots par suiveur.
  Canari `tools\qa_2026-11-05\canari_fpp.py` (Samurai VTK seul, corps vanilla) : build 96 s, `check` = coque de torse
  4 641 sommets / 24 décals / masque `…391`, jambes `…584`. **Rien posé dans le jeu** : pose et QA à lui (sa formule).

## 2026-11-05 (15 h → 15 h 45) — Sa QA : torse FPP bon ; trous sous les genoux = maillage « pieds à plat », coque v2 posée (Fable)

- Canari FPP posé à 15 h 09 sur son déverrouillage. Sa QA : torse et cuisses encrés en FPP (Samurai vide sur la poitrine
  = sa texture ; Bedellia / Promiscuity / Vale couvrent le torse) ; tibias troués assis en FPP et en mode photo, trous qui
  **bougent avec la caméra**. Plus aucun gel en 2 h de jeu, overlay NVIDIA coupé.
- Mips du Samurai mesurés sains (14 niveaux, alpha = filtre boîte) : texture éliminée. Sonde du 02/11 relue : sur tous les
  pantins le corps est masqué à 0-4 et les mollets / pieds sont le garment `l0_000_pwa_base__cs_flat` ; ce maillage a les
  sommets et UV des chunks 5-7 du corps, chunk 5 coïncident (0,02 mm), chunks 6-7 à 17-60 mm (pieds à plat). Masquage par
  nom de composant (`partsOverrides`) : notre coque n'est jamais masquée. ETUDE § 27 bis.
- Codé : `low_mask` (chunks sous 0,30 m) sur les coques de corps féminines et FPP jambes ; compagnon TPP `legs_flat`
  (copie de `cs_flat`, nommé comme le composant du jeu). Canari v2 (Samurai + Bedellia) bâti 40 s, 22 Mo, vérifié, posé à
  15 h 44 sur son go in-prompt. Red Hot Tools 1.3.0 BETA13 (2.5) posé par lui via WolvenKit pendant ce temps.
- Sa parenthèse : fichiers `.xl` de suppression de nœuds (mods de lieux, son V's North Oak Villa) cassés par les mises à
  jour ; conversion vers 2.5 à étudier en séance dédiée (ArchiveXL `nodeDeletions`, Red Hot Tools 2.5 à tester par lui).

## 2026-11-05 (15 h 50 → 16 h 40) — QA v2 / v3 : photo, inventaire, FPP propres ; reste le créateur ; Red Hot Tools périmé (Fable)

- Jeu mort au chargement de `RedHotTools.dll` (0xc0000005, journal RED4ext coupé net) : WolvenKit avait posé la RC3 du
  20/10 et un module CET de juillet, et sa « désinstallation » n'a rien retiré. BETA13 (2.5) téléchargée et vérifiée (SHA
  `782635a6…`), posée par lui à la main, zip rangé dans `1_Core` avec la mention WOLVENKIT INIT BROKEN.
- QA v2 : photo et inventaire propres, manche jusqu'à la cheville ; FPP assise encore trouée (coque à plat absente en
  FPP) ; créateur / modificateur troués en bas de face (sonde : là, jambes = second exemplaire du corps, pied levé, pas
  de `cs_flat`). v3 : compagnon `fpp_legs` ; canari posé à 16 h 20 ; **sa QA : FPP assise propre, Bedellia FPP propre,
  photo / inventaire inchangés**. ETUDE § 27 ter. Reste : créateur (état des pieds, apparences dynamiques à mesurer).

## 2026-11-05 (16 h 45 → 17 h 30) — États des pieds : deux options cachées du jeu ; canari v4 bâti (Fable puis Opus)

- « Reprends » : source ArchiveXL lue (`&feet=` dépend de la chaussure, pieds nus = `flat` partout : ne distingue pas le
  créateur du jeu). `female_cco_ep1` extrait : options cachées `lifted_feet` (corps chunks 5-7) et `flat_feet`
  (`cs_flat`), dans leurs groupes, absentes de `TPP_Body`. ETUDE § 28.
- Codé dans `core.py` : coque de corps au masque de l'app du corps (chunks 0-4), compagnon `legs_lifted` (corps par
  l'app des jambes, nom du corps du jeu) dans `character_creation` + `lifted_feet`, `legs_flat` dans `flat_feet` seul.
  Canari v4 `canari_feet.py` : 31 s, 22,2 Mo, vérifié dépaqueté ; bâti seul sur son choix in-prompt, puis **posé à 17 h 29** sur son « vas y pose » (SHA identiques).
- Ses questions : Togglable Feet (corps vanilla seul, trois états de pieds par étiquette de chaussure, § 28) ; lecture des
  pages sans capture (le texte de Nexus ne sort pas par l'extraction de texte, il sort par une lecture du DOM).
- Fable coupé en cours de séance (quota), reprise par Opus sur sa commande.

## 2026-11-05 (17 h 30 → 18 h) — Sa QA du canari v4 : corps vanilla propre partout ; deux constats neufs (Opus)

- Canari v4 posé à 17 h 29 sur son « vas y pose » (SHA identiques, v3 sauvegardé). Sa QA : modificateur, créateur de
  nouvelle partie, mode photo, FPP assise : propres, aucun trou. Le risque annoncé (coque à plat dans `flat_feet` seul)
  ne s'est pas produit en photo.
- Constats neufs, non mesurés : hexagone de Samurai coupé net sur le dessus de la main, partout ; encre de cheville plus
  longue dans le créateur seul (marches noires, « V » rouge). Hypothèses et mesures dans la passation.
- Mesuré pour sa question VTK : Angel, Solo, Songbird livrent apps de jambes et `cs_flat`, aucun l'app du corps ; Angel
  seul livre le pied talon de Togglable Feet. ETUDE § 27 ter corrigé (il disait l'inverse pour `cs_flat`).
- Passation : la ligne de sauvegarde écrite à 17 h 29 portait des octets de contrôle (`\b`, `\2` d'un remplacement
  Python) ; réécrite.
