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
