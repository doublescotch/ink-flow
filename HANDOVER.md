# Passation — Ink Flow (VTK/UV CCXL Tattoo Loader)

Créée le 2026-11-01 à 2 h 45 (compartimentage demandé par Hell_Kaiser : chaque projet de création porte sa passation et son journal dans son dossier ; `cp:HANDOVER.md` ne garde qu'un renvoi). Ce fichier ne porte que **l'état vivant** : ce qui est posé, ce qui attend, ce qui n'est pas tranché. Les mesures, décisions et acquis vivent dans `ETUDE.md` ; la chronologie dans `LOG.md`.

~~**Pas de git tant que le proto ne tient pas**~~ Dépôt ouvert depuis le 01/11 (21 h 25) :
`https://github.com/doublescotch/ink-flow`, branche `master` ; `canari\` exclu.

## État (2026-11-04, 13 h) : support UV mesuré et architecturé, code sur go ; 1.2.0 toujours à uploader

- **Mesure UV faite (ETUDE § 21, Fable, lecture seule, rien posé)** : corps vanilla = framework UV 3.2.1 = Solo =
  Songbird = corps masculins (même mise à plat, peau en u > 0,22) ; **bras UV = bande u < 0,22 de la texture du
  corps** (G en haut, D en bas), **bras VTK = mise à plat vanilla dans leur propre texture** ; Angel met ses pieds
  et chevilles dans la bande (chunks 6-7, 24 % de sa peau), jamais peints par les textures VTK.
- **Architecture retenue (ETUDE § 21, fin)** : une texture UV → coques corps + bras G + bras D (+ FPP) ; bras
  acceptés seulement si la mise à plat du bras actif est celle de la famille (u max ≤ 0,22 = bras UV) ; corps Angel
  sous texture UV = chunks 6-7 masqués ; aucune conversion ni ré-encodage dans la première version (BC7 = 166 s
  par 8K, mesuré). Conversion des bras = chantier optionnel plus tard.
- **Devis à son go** : une séance de code (`core.py` : `TARGET_BY_TEX` → liste, détection de la mise à plat des
  bras depuis le JSON déjà sérialisé, masque des chunks de bande et des chunks non-peau, journal) + non-régression
  488/488 + builds CLI sur deux arbres factices (Solo + framework + bras UV ; Angel) avec les 5 tatouages UV de
  `dl\uv\`. Puis **banc en jeu à lui** : Solo 2.0 + framework 3.2.1 + Solo Arms UV posés (Angel parqué), créateur :
  Kala Sleeve 1 (manches seules), Bedellia (corps + bras), FPP, miroir ; puis Angel + Bedellia (torse seul, pieds nus).
- **Deux pièges trouvés, hors UV, à coder dans le même lot** : (1) `shell()` convertit tous les matériaux : sur
  Songbird Body le tatouage couvrirait les plaques cyber (masquer les chunks non-peau de l'apparence) ; (2) les
  `.app` de Solo 2.0 ne se sérialisent pas avec le CLI 9.1.0 (`castShadows` Bool) : `fpp_torso_mask()` retombe
  sur le masque vanilla (`except` lu), le build passe ; le vrai masque FPP de Solo = point de QA au banc.
- Jetable sur le poste : `C:\__DEV\cyberpunk\ink_flow\dl\uv\` (archives, `x\` sérialisé, `png\`, `reenc\` ≈ 1 Go).
- Reste inchangé : 1.2.0 à uploader (bloc suivant), opacité > 1,0 corrigée non rebâtie, QA opacité annoncée.

## ~~État (2026-11-04) : 1.2.0 = tableau des corps détectés + opacité par tatouage, prête~~ dépassé (04/11, 13 h : mesure UV)

- **1.2.0 bâtie et commitée** (ETUDE § 20) : cadre « Body meshes in use » (Female V / Male V × Body / Arms / Head),
  colonne **Opacity** par tatouage (catalogue ; vide = **Default opacity**). Exe `4e3f15d1…9bb6`, zip
  `releases\Ink_Flow_Builder-1.2.0.zip` `3e1f13f9…6a46`. Non-régression 488/488 contre la 1.1.0. **À lui** :
  upload Nexus (1.1.0 en ancienne version, champ version 1.2.0), coller de `NEXUS.md` les étapes 1 et 3, le
  dépannage et le changelog 1.2.0, refaire la capture de la fenêtre, poster le **sticky 1.2.0** de
  `NEXUS_POSTS.md` (il remercie le demandeur de l'opacité). 1.1.0 uploadée par lui (sa réponse du 04/11).
  ~~Tags : seul `v1.0.0` existe~~ posés et poussés sur son go (04/11) : `v1.0.1` = `d86e5ab`, `v1.1.0` = `546200f`,
  `v1.2.0` = commit du sticky 1.2.0 (dernier commit de chaque version, comme `v1.0.0` = `dcf165a`).
  Réponses individuelles du 02/11 retirées de `NEXUS_POSTS.md` à sa demande (postées, historique git).
- **Opacité > 1,0 par tatouage (04/11, retour du demandeur)** : colonne bornée à 1,0, réglage général non ;
  corrigé dans le code (0,1-2,0 partout, ETUDE § 20, fin), **non rebâti** (sa décision : part avec la prochaine
  version). Réponse au demandeur : en attendant, l'opacité générale à 1,5 marche, la par-tatouage viendra.
- **Point de QA annoncé** : une coque à opacité propre rend comme le réglage général à la même valeur (même champ
  `DiffuseAlpha`), jamais vu en jeu ; à regarder au créateur avec deux tatouages à 0,5 et 1,0.
- **Prochaine séance = support UV** (sa décision du 04/11 ; Fable, mesure et architecture). Cadrage relu, rien
  mesuré : (a) **moteur** : `fullbody_overlay_d01.xbm` (`KNOWN_OTHER`, « not supported yet ») est UNE texture pour
  corps + bras, alors que `TARGET_BY_TEX` mappe une texture vers une seule cible : passer à « une texture, plusieurs
  coques » ; masculin `ma_fullbody_overlay_d01`, tête `wa_head_overlay_d01` (Garden Bloom) ; (b) **coque** : la
  piste A règle la mise à plat UV par construction (copie du corps UV actif, ETUDE § 8), MAIS le framework UV 3.2.1
  branche le calque par une chaîne de `.mi` (§ 2) : si le maillage UV a des matériaux externes, `shell()` le refuse
  aujourd'hui (« external materials ») ; (c) **mélange** : tatouage UV sur corps VTK (Angel) = mises à plat
  différentes, à refuser proprement ou à convertir (§ 11, question « conversion UV ↔ VTK ») ; (d) **banc** : il faut
  un corps UV en jeu (Solo 2.0, UV 3.2.1, bras Songbird UV sont dans `3_Bodies\V's Body.zip`). **Premier geste** :
  dépaqueter UV 3.2.1 + Solo, lire leurs matériaux (locaux / externes) et comparer les UV des corps vanilla / Solo /
  Angel, avant une ligne de code.
- Ensuite : tête vanilla, tête du V masculin, miroir / FPP / photo du V masculin (bloc du 03/11 ci-dessous, (1)-(3)).

## ~~État (2026-11-03, 20 h 30) : 1.1.0 = V masculin (vanilla + Gymfiend) + ré-encodage des mips tronqués, prête~~ dépassé (04/11, 1.2.0)

- **1.1.0 bâtie et commitée** (ETUDE § 19) : V masculin (table `m_*`, `inkflow_pma` sous `male:`, pas de suiveur
  FPP), ré-encodage WolvenKit des seules textures à chaîne de mips tronquée. Exe `24434274…5c05`, zip
  `releases\Ink_Flow_Builder-1.1.0.zip` `43f0f655…6427`. Non-régression féminine 500/500. **À lui** : upload Nexus
  (1.0.1 en ancienne version), coller `NEXUS.md` (résumé, What works with what 1.1.0, changelog), tag `v1.1.0` sur go.
- **QA validée par lui au créateur** (nouvelle partie) : V masculin corps vanilla puis Gymfiend VTK 1.4.3 + MV Head
  (Kala Japanese V2 masculin propre après ré-encodage) ; V féminine inchangée (tout bon sauf têtes sur tête vanilla).
- **Jeu** : remis par lui aux piles 1-2 ; tout ce que j'avais posé retiré (`tools\qa_2026-11-03\game_pose.py remove`,
  20 h 15). Gymfiend et MV Head dépaquetés dans `C:\__DEV\cyberpunk\ink_flow\dl\6423_*`.
- **Prochaine séance (sa demande)** : (1) **tête vanilla** : la coque de tête ne s'affiche pas sur tête vanilla
  (Kala head, Finn, V féminine, créateur ; déjà vu § 17) ; vérifier d'abord qu'elle est toujours présente sur Angel +
  tête VTK HD ; (2) **tête du V masculin** : pack visage `FACE TATTOOS-7414-V2-KALA-MALEV-VTK` + Kala Faded Face dans
  `3_Bodies\__RAM`, sur Gymfiend + MV Head ; (3) miroir / FPP / photo du V masculin quand il aura une sauvegarde.
- Idées notées, non tranchées : option de test « forcer un tatouage sur l'autre genre » (patrons UV femme / homme
  non comparés) ; garder le BC7 après ré-encodage (encodeur à trouver) ; Hyst EBB (4654) à passer au moteur.
- Plantage à la sortie du 03/11 18 h 33 (DEP après déchargement de RED4ext, 1 sortie sur 5) : hors Ink Flow ;
  candidat non prouvé audioware 1.10.1-rc.0.

## ~~État (2026-11-02, 18 h 30) : QA vanilla validée, 1.0.1 publiable, page Nexus récrite dans `NEXUS.md`~~ dépassé (03/11, 1.1.0)

- **Dans le jeu** : Angel + refits + 4 têtes VTK + build Ink Flow corrigé de 17 h 28 (`a6fd24c8…`, 9 archives),
  remis à 18 h 15 après la QA vanilla. **Sonde retirée** (sa décision), source dans `tools\probe\` pour les prochains
  corps ; Redscript 0.5.32 laissé en place (prérequis d'ArchiveXL, il ne l'avait pas). Fichiers macOS `engine\tools\scc`,
  `libscc_lib.dylib` : à lui de les supprimer.
- **Prouvé (ETUDE § 18, passage 3)** : corps vanilla pur + correctif `linkController` : **QA validée par lui sur deux
  sauvegardes et en nouvelle partie** (reprise des tatouages posés sur Angel, miroir, FPP, photo) ; sonde : 0 échec, 3
  coques FPP attachées. Le Confirm mort du § 17 était ce défaut. Build gardé `C:\__DEV\cyberpunk\ink_flow\builds\vanilla_link_qa\`.
- **Exe 1.0.1 inchangé** (`f32d59bc…7109`, zip `42fa8310…4ed2` dans `releases\`) : rien à rebâtir, le code n'a pas
  bougé depuis 18 h 10. **À lui : upload Nexus** (zip, SHA-256 dans la description du fichier, 1.0.0 en ancienne
  version, champ version 1.0.1), **coller `NEXUS.md`** (résumé, description, changelog : récrits sur SA page publiée, lue
  par l'API ; détail des changements en tête du fichier), captures listées en fin de `NEXUS.md`, réponses de
  `NEXUS_POSTS.md` (EBBRB ×3 : relire la réponse, elle doit maintenant pointer la ligne Body mesh et le dépannage de la
  page), puis **tag `v1.0.1`** sur un go.
- **Ce qui reste théorique, dit tel quel sur la page** : EBBRB (accepté par le builder, § 17, jamais vu rendu) ; autres
  corps VTK = critère du builder (`shell()` : matériaux locaux, apparence de peau standard), pas une liste testée ; un
  corps non mis à jour pour 2.5 reste cassé sous Ink Flow (coques = copies de ses maillages) ; bras cybernétique jamais
  testé ; hypothèse REDmod / MO2 des trois EBBRB attend un `build.log`.
- Scripts : `tools\qa_2026-11-02\build_pure_link.py` (build du passage 3), `tools\probe\logs\2026-11-02_181554`
  (journaux, hors git). `gen\nexus_36814_desc.bbcode` = sa page telle que publiée (poste).
- **Son plan avant l'upload (18 h 35)** : test « premier utilisateur » : désinstaller le runtime .NET 10 et
  `%LOCALAPPDATA%\InkFlow`, exe 1.0.1 vierge, **corps vanilla** (Angel + têtes à parquer : moi, sur son go, jeu fermé),
  2-3 tatouages, Build, Install, captures du processus et du résultat en jeu ; puis la même chose sur **Angel**. C'est
  la première exécution réelle du bouton Install .NET Runtime 10 (jamais joué sur ce poste : ETUDE § 18). Effets à
  savoir : `%LOCALAPPDATA%\InkFlow` emporte le catalogue (noms édités), la config (liste des archives, slots), le cache
  (build suivant ≈ 2 min au lieu de 20 s), WolvenKit (retéléchargé, 45 Mo) et `backup\` (anciens Ink_Flow ; le
  build de 17 h 28 reste dans `C:\__DEV\cyberpunk\ink_flow\…\out` et dans le jeu).

## ~~État (2026-11-02, 18 h 15) : FPP corrigée et prouvée sur Angel, .NET installable depuis le builder, 1.0.1 prête sauf QA vanilla~~ dépassé (18 h 30)

- **Dans le jeu** : Angel + refits + 4 têtes VTK, **build Ink Flow corrigé** (`linkController`, 170 Mo, 530 fichiers,
  bâti à 17 h 28 par `tools\probe\angel_build.py` sur sa config, 9 slots) ; l'ancien dans
  `%LOCALAPPDATA%\InkFlow\backup\2026-11-02_172832`. **Redscript 0.5.32 posé** (4 fichiers, depuis le zip de
  `1_Core\__WOLVENKIT`) et **sonde `r6\scripts\InkFlow_Probe\`** encore posée : `pose_probe.py remove` sur son go
  (elle écrit ≈ 4 000 lignes par session dans `cyber_engine_tweaks\gamelog.log`). Fichiers macOS `engine\tools\scc`,
  `libscc_lib.dylib` : inoffensifs, à lui de les supprimer.
- **Prouvé (ETUDE § 18)** : la première personne de la 1.0.0 n'a jamais appliqué ses coques FPP (`linkController` à 0
  sur le maître, gabarit du toolkit) : trous et démarcation mobile sur les bras en FPP, vus par lui à 17 h 15. Avec
  `linkController = 1` : coques FPP attachées et chargées (journal), **QA validée par lui (17 h 45) : bras corrects
  en FPP depuis le miroir, mode photo bon**.
- **Exe 1.0.1** `C:\__DEV\cyberpunk\ink_flow\exe\dist\InkFlowBuilder.exe` SHA-256 `f32d59bc…7109`, zip
  `InkFlowBuilder-1.0.1.zip` SHA-256 `42fa8310…4ed2` (copie `releases\`) : correctif FPP + bouton **Install .NET
  Runtime 10** (installeur Microsoft épinglé, silencieux ; l'installation elle-même non jouée sur ce poste) + ordre de
  chargement / bras vanilla / Body mesh / Scan / build.log du matin. README et `NEXUS.md` à jour (changelog).
- **Avant l'upload, à trancher par lui** : (a) rejouer le **corps vanilla** (Angel et têtes parqués, build vanilla,
  miroir, Confirm, FPP) avec le correctif et la sonde : le Confirm mort du § 17 a été mesuré avec `linkController = 0`,
  il peut avoir disparu ou non ; sans ça, « or the vanilla body » reste une promesse non prouvée ; ou (b) publier
  1.0.1 en l'état (Angel / EBBRB prouvés par la mesure, FPP réparée) et traiter le vanilla ensuite.
- **Reste non prouvé** : hypothèse REDmod / MO2 des trois EBBRB (attend un `build.log`) ; bras cybernétique (lames
  Mantis) sur nos coques à masque plein (sa question, jamais testé) ; le dump de la sonde le dirait.
- **Prérequis Nexus (sa question de 18 h)** : Ink Flow n'exige que **ArchiveXL** (+ RED4ext) ; Redscript recommandé
  (scripts d'ArchiveXL), Codeware et TweakXL inutiles ; Angel = « développé avec », pas requis. Page Nexus à sa main.
- Sonde et scripts de la séance versionnés dans **`tools\probe\`** (`InkFlow_Probe\InkFlow_Probe.reds`,
  `pose_probe.py`, `angel_build.py`) ; `tools\probe\logs\<date>\` = journaux des deux passages (2 × 1,2 Mo),
  gardés sur le poste, **exclus du dépôt** avec `releases\` et les zips (`.gitignore`, 18 h 20).

## ~~État (2026-11-02, 17 h) : 1.0.1 NON publiable telle quelle, corps vanilla cassé au miroir, sonde à écrire~~ dépassé (18 h 15)

- **Jeu remis dans l'état d'hier soir** (sa décision, 16 h 50) : Angel + refits + 4 têtes VTK remis depuis le
  parc, **build bâti sur Angel reposé** (159 Mo, celui de la QA validée). Variantes du jour dans
  `%LOCALAPPDATA%\InkFlow\backup\2026-11-02_*` et `C:\__DEV\cyberpunk\ink_flow\gen\t101\out*`. Sa config
  du builder pointe sur `3_Bodies\__InkFlow` (21 archives).
- **Ce que la QA du jour a prouvé (ETUDE § 17, tableau)** : la recette fonctionne sur le corps vanilla
  **sans première personne** (créateur, miroir, Confirm, photo) ; **les coques FPP de bras bâties sur le
  vanilla cassent l'attache à chaud au miroir** et laissent le créateur sans Confirm ; sans FPP, les coques
  TPP de bras sont rendues en FPP et décalées sur les bras FPP vanilla ; la coque de tête vanilla ne
  s'affiche pas en nouvelle partie. Matériaux preload : hors de cause. Cause exacte : **non trouvée**.
- **Conséquence pour 1.0.1** : l'exe `fc33b615…` bâti à 14 h ne contient pas le changement « matériaux
  embarqués » de 16 h (neutre) et, surtout, un joueur **sans mod de corps** aurait un miroir cassé au lieu
  d'une erreur au build : **ne pas uploader** avant d'avoir, au choix de Hell_Kaiser : (a) la vraie cause
  (sonde), ou (b) le garde-fou « corps = jeu de base ⇒ pas de coques FPP + avertissement » (5 lignes dans
  `run_build`, README). Les correctifs REDmod / MO2 / Body mesh / Scan / build.log restent bons.
- ~~**Prochaine session = la sonde**~~ faite le 02/11 à 17 h-18 h (ETUDE § 18, `tools\probe\`) (sa décision : « une sonde, un logger complet, nouvelle session ») :
  Redscript + Codeware dans `r6\scripts\InkFlow_Probe\`, journal des `Resource/Load|Ready|Failed` sur
  `inkflow\…`, des événements du créateur et des composants attachés au joueur ; plan détaillé ETUDE § 17,
  dernier paragraphe. Codeware 1.21.2 est dans son jeu ; Redscript : vérifier `red4ext\plugins`
  (`r6\scripts` n'existe pas encore). Le script de Hyst (`dl\4654\ebbrb\r6\scripts\VTK_Hyst_CC_Edit`) est
  un bon modèle d'accroche `Resource/Load`.
- Scripts de la séance, versionnés dans **`tools\qa_2026-11-02\`** (chemins en dur du poste) : `game_step.py`
  (isolate / install / angelbuild / embed / nofpp / fpparms / fppbody / restore), `build_pure*.py`,
  `build_fpp_bisect.py`, `vanilla_in_game.py`, `order_test.py`, `vanilla_test.py`, `ebbrb_test.py`,
  `gui_capture_101.py`.
- **Durée du déverrouillage** : `UNLOCK_TTL_SECONDS` dans les deux hooks installés (lignes 67 et 85) et
  dans `pipeline\hooks\` ; à lui (fichiers de règles).

## ~~État (2026-11-02, 15 h) : 1.0.1 bâtie et prouvée hors jeu, upload et QA vanilla à lui~~ dépassé (17 h)

- **1.0.1 livrée sur son go** (ETUDE § 17, « Livré ») : ordre de chargement réel (`modlist.txt`, REDmod, ordre
  MO2), bras vanilla, ligne **Body mesh** dans la fenêtre, bouton **Scan game folder…**, `build.log`,
  conflits sur REDmod aussi, CLI `--from-game`. Exe `C:\__DEV\cyberpunk\ink_flow\exe\dist\InkFlowBuilder.exe`
  SHA-256 `fc33b615…9805` ; zip `InkFlowBuilder-1.0.1.zip` SHA-256 `8b38f547…`, copie dans `releases\`.
- **Prouvé** : tests d'ordre A → H ; build CLI complet sur corps vanilla (157 fichiers, 71,1 Mo, coque de
  bras vérifiée) ; exe figé sur Angel = 1.0.0 au bit près hors index (157 fichiers, 150 347 776 o) ; capture
  `builder\tests\gui_main_2026-11-02.png`. **Jeu non touché** (son Ink Flow de la veille reste posé).
- **Dans le jeu depuis 14 h 37 (sa demande, déverrouillage `WRITE_UNLOCK.txt` sur le dossier du jeu) :
  build 1.0.1 sur le CORPS VANILLA** : Angel parqué (`006_Angel_Body.archive`, `.xl`, refits →
  `C:\__DEV\cyberpunk\ink_flow\parked\2026-11-02_angel\`), têtes VTK HD laissées (son choix après coup :
  « ça permet de tester le corps vanilla avec la seule tête VTK ») ; 21 archives de `3_Bodies\__InkFlow\`
  (sa config `files` repointée dessus, les anciens chemins étaient morts), 9 slots, miroir, FPP ; corps,
  bras, bras FPP = jeu de base, tête = `006_VTK_Vanilla_HD_Head_xBaebsae` ; **530 fichiers, 82,6 Mo, 139 s,
  SHA-256 `b7330a9b…`** ; l'ancien Ink Flow (Angel) dans `%LOCALAPPDATA%\InkFlow\backup\2026-11-02_143536`.
  Script : scratchpad `vanilla_in_game.py`. **Retour à Angel** = remettre les 3 fichiers parqués, Build,
  Install (formule ou `WRITE_UNLOCK.txt`).
- **À lui** : (1) QA **corps vanilla en jeu** : miroir, bras nus : tatouage de bras visible et collé à la
  peau (Kala Japanese Arm L/R, Samurai) ; corps aussi ; FPP tête baissée ; le personnage garde ses slots.
  (2) Upload Nexus 1.0.1 (zip + SHA-256, changelog dans `NEXUS.md`) **après** relecture de `NEXUS.md`
  contre SA description publiée (il l'a altérée : à relire par moi, il doit me donner l'URL de la page).
  (3) Poster les réponses de `NEXUS_POSTS.md` (EBBRB ×3, 0xVyper). (4) Tag `v1.0.1` après l'upload, sur un go.
- **Reste non prouvé** : l'hypothèse REDmod / MO2 pour les trois EBBRB (attend un `build.log`) ; le rendu
  d'une coque vanilla en jeu. Si un `build.log` EBBRB dit `Body : 05_Hyst_Refit…` et que rien ne s'affiche
  quand même, l'hypothèse tombe : chercher alors côté redscript Hyst (`VTK_Hyst_CC_Edit`) ou `.app` EBBRB.
- Jetables sur le poste : `dl\4654\ebbrb\` (fixture EBBRB, 178 Mo), `gen\t101\` (arbre factice vanilla,
  cache, build de 71 Mo : 292 Mo), `gen\vanilla_test\`, `gen\ebbrb_test\`. Scripts de test dans le scratchpad
  de la session (`vanilla_test.py`, `ebbrb_test.py`, `order_test.py`, `gui_capture_101.py`) : non versionnés.

## ~~État (2026-11-02, 14 h 30) : 1.0.0 publiée sur Nexus, premiers retours, correctifs 1.0.1 proposés~~ remplacé (15 h)

- **Publiée** par lui dans la nuit du 01 au 02/11 (page Nexus en ligne, 15 messages le matin). Son jeu
  purgé le 02/11 : 9 archives (Angel, refits vanilla, têtes VTK HD, Ink Flow de la veille), marche.
- **Retours** : trois utilisateurs **EBBRB** (Lorasyl, Bransburk, cybercock2067) : build et install sans
  erreur, slots visibles, **rien sur le corps** ; TheQueenEmzz : .NET 10 non détecté (il a répondu :
  runtime x64, capture ajoutée) ; Brandy1123 : 2.3x non fonctionnel (attendu) ; deux demandes de V
  masculin ; 0xVyper : tout dynamique sans rebuild.
- **Mesuré (ETUDE § 17)** : corps **vanilla pur** : corps et tête passent, **les bras sont refusés** par
  `shell()` (matériaux en `preloadLocalMaterialInstances`) : le README et la page Nexus mentent sur
  « or the vanilla body ». **EBBRB 5.0.0** (Nexus 4654, téléchargé, `dl\4654\ebbrb\`) : le moteur
  accepte tout (corps 91 371 sommets, 12 matériaux, même boîte qu'Angel) : rien à corriger côté recette.
- **Hypothèse pour les trois EBBRB (non prouvée)** : le builder n'a pas vu le corps (REDmod `mods\`, MO2
  hors VFS, ou `modlist.txt`) et a bâti une coque **vanilla** (4 641 sommets) sous un corps à 91 k
  sommets : invisible. Le journal de build dit `Body : base game` ; aucun fichier journal n'est écrit.
  **À demander aux trois** : la ligne « 2. active meshes », le gestionnaire de mods (réponses rédigées).
- **Correctifs 1.0.1 proposés (sur son go)** : (a) `shell()` accepte les matériaux preload ; (b)
  `find_owner` : `modlist.txt`, `archive\pc\mod`, REDmod, jeu de base ; (c) corps résolu affiché dans la
  fenêtre, rouge si « base game » ; (d) `build.log` dans `%LOCALAPPDATA%\InkFlow` ; (e) README et page
  Nexus (MO2, REDmod, bras vanilla, build.log). (f) bouton Scan game folder : lot à part.
- QA à prévoir après (a) : **corps vanilla** (retirer Angel et les têtes de son jeu, bâtir, bras tatoués
  visibles), puis remettre Angel et rebâtir.
- Non versionnés dans le projet : `InkFlowBuilder-1.0.0.zip`, `releases\` (captures 1, 2, 4 de 0 h 51,
  Nexus de 9 h). **Tag `v1.0.0` absent** (local et GitHub, mesuré à 14 h 30) : à poser sur `dcf165a`
  avec le commit des docs, sur son go.

## ~~État (2026-11-02, 0 h 15) : QA FPP validée, interface verrouillée pendant le build, upload à lui~~ remplacé (14 h 30)

- **QA FPP de Hell_Kaiser (02/11, vers 0 h) : validée.** 9 slots, tous ses tatouages chargés depuis son
  pack V's Body : (a) créateur, les 9 slots superposables apparaissent bien ; (b) tatouages des bras vus
  au miroir puis en première personne (tête baissée) ; (d) posés au miroir, suivis en FPP ; (e) mode
  photo OK ; **pas de bras plus clair**. (c) rien qui flotte : non signalé.
- **Sa demande d'interface (même message)** : les boutons restaient cliquables pendant le build. Livré :
  fenêtre en lecture seule pendant le build (tous les contrôles ttk grisés, la liste ignore clics et
  touches), le bouton Build devient **Cancel** ; fermer la fenêtre = « annuler et quitter ? ». Moteur :
  `core.Cancelled` (distincte de `BuildError`, que `fpp_torso_mask` avale), `Cli.run` tue WolvenKit.
- **Preuves (GUI pilotée, maison `exe\home`)** : Cancel pendant le `deserialize` : `WolvenKit.CLI.exe`
  vivant à l'appui, absent 1 s après, sortie vide (archive partielle retirée), bouton « Cancelling… »
  grisé, 13 s ; 24 contrôles grisés, seul Cancel actif ; build complet ensuite : 157 fichiers,
  150 347 776 o, identique. Exe figé rebâti à 0 h 09 (SHA-256 `7df14236…3cb7775`), autotest : 157 fichiers,
  150 347 776 o, 145 s. Zip `c1e354ae…5aa02a` recopié sur ses deux copies (racine du projet et `releases\`).
- ~~**Attend lui** : boîte Permissions de 20279, relecture de `NEXUS.md`, captures (sa capture
  `releases\Ink Flow Interface.png` de 0 h 05 montre la fenêtre au repos : le verrou n'y change rien),
  upload Nexus (zip + SHA-256 de l'exe), puis tag `v1.0.0`.~~ Publié dans la nuit (état du 02/11, 14 h 30).

## ~~État (2026-11-01, 23 h 45) : 1.0.0 + première personne bâtie, QA FPP attendue avant l'upload~~ remplacé (0 h 15)

- **Première personne (décision de Hell_Kaiser, 23 h : « ajouter la FPP avant l'upload »)** : livrée
  dans le builder (ETUDE § 16 : suiveur caché par slot lié au sélecteur, coque du corps masquée comme le
  torse FPP actif, copies des bras FPP, groupe `FPP_Body` seul ; case « First person » cochée par défaut,
  `--no-fpp` en CLI). Build CLI : 150,3 Mo, 157 fichiers (+ 10,7 Mo), structure contrôlée dépaquetée.
  **Jamais vue en jeu** : la pose et la QA sont à lui.
- **QA FPP (à lui, sauvegarde avec miroir, bras nus)** : exe 1.0.0 rebâti → Build → Install (jeu fermé),
  puis (a) créateur inchangé (ni double décal ni scintillement des bras) ; (b) en jeu, bras et corps vus
  de V tatoués comme au miroir ; (c) rien qui flotte près de la caméra ; (d) changer le slot au miroir ou
  au charcudoc : la FPP suit ; (e) mode photo inchangé. Replis si (a) ou (b) rate : ETUDE § 16, fin.
- **Exe 1.0.0 rebâti à 23 h 35** : `exe\dist\InkFlowBuilder.exe` 11,4 Mo, SHA-256 `b1fd72db…68075`
  (autotest figé : 157 fichiers, 150 347 776 o, 124 s, même résultat que le CLI) ;
  zip `exe\dist\InkFlowBuilder-1.0.0.zip` 11,7 Mo, SHA-256 `c0b18ba7…4b027`, **recopié sur sa copie
  dans le dossier du projet** (celle de 21 h 19 n'avait pas la FPP). README, `NEXUS.md` (limite FPP
  retirée, résumé 247 caractères, étape 4) et ETUDE § 16 à jour ; le tout commité.
- **`publish\` renommé `releases\` par lui (23 h 26, hors git)** : `Ink_Flow_Builder-1.0.0.zip` (sa copie
  de 21 h 19, **remplacée par le zip avec FPP** à 23 h 45), `main.png`, `Ink Flow Interface.png` (22 h 54 :
  fenêtre du builder **sans** la case « First person », capture 1 à refaire).

- **Test de l'exe vierge par Hell_Kaiser (22 h)** : `%LOCALAPPDATA%\InkFlow` supprimé, relance : le jeu
  est retrouvé seul (registre Steam + `libraryfolders.vdf`, `env.find_game_candidates`, aucune
  mémoire) ; **bouton Download OK** (WolvenKit dans `InkFlow\wolvenkit`, lié) ; build à faire par lui.
- **Slots, tranché par lui (22 h)** : réglage du **builder** (case Slots, 1 à 9, défaut 2), rien dans
  Mod Settings (ArchiveXL fusionne les options du créateur au chargement). Plafond 9 = index 1041 à
  1049 libres sous `body_tattoo` (1040), `fpp_body_tattoo` à 1050. Résumé Nexus, étape 4 de la page
  et README reformulés (« Ink 1 to Ink 9, you choose how many ») : **non commités**.
- Déposés par lui dans le dossier du projet : `InkFlowBuilder-1.0.0.zip` (copie de l'upload, 11,7 Mo,
  non versionné, à ajouter au `.gitignore` ou à laisser hors git) et `publish\main.jpg` (22 h 35,
  626 Ko : capture pour la page Nexus ?). À trancher par lui : versionner `publish\` ou non.
- ~~**Exe 1.0.0 : `C:\__DEV\cyberpunk\ink_flow\exe\dist\InkFlowBuilder.exe`** (11,4 Mo, SHA-256
  `13c14eaa…bbc9b9`) ; **zip d'upload `exe\dist\InkFlowBuilder-1.0.0.zip`** (11,7 Mo, exe + README +
  LICENSE, SHA-256 `35b5bf52…40daf6`)~~ remplacés à 23 h 35 par la 1.0.0 avec FPP (SHA-256 ci-dessus). Preuve : exe figé en mode `INKFLOW_AUTOTEST` (maison `exe\home`,
  cache chaud) : 18 tatouages, 106 fichiers, 139 599 872 o en 120 s, **0 octet différent hors index**
  contre la v0.3b posée dans le jeu (536 dans l'index = horodatages), `.xl` identique.
- **Gabarits (décision de Hell_Kaiser, 21 h 15 : garder + créditer)** : le toolkit 20279 se présente
  comme « a template resource … template source files for your WolvenKit project » (description Nexus,
  lue par l'API ; la boîte Permissions n'est pas lisible par l'API : **à lire par lui sur la page**) ;
  en-têtes WolvenKit nettoyés (plus de chemin `C:\__DEV`), localisation = squelette neutre
  (`placeholder`, plus rien de Kylin). Crédit thrasherpass dans le README et la page Nexus.
- README : rebâtir après un changement de corps, slot conservé, comment le corps est choisi, limites
  (UV, FPP, morph au charcudoc non coché), crédits. **Dans le jeu : build 0.4.0 de 20 h 03 inchangé**
  (même contenu que la 1.0.0 au bit près hors index : rien à reposer).
- Brouillon de la page Nexus : **`NEXUS.md`** (racine du projet, anglais : nom, résumé, description
  BBCode, permissions, crédits, fichier à envoyer, captures à prendre).

## Où sont les choses

- Projet (OneDrive, dépôt git) : `cp:__DEV\Projects\Ink Flow\` : `ETUDE.md` (§ 1-15), `NEXUS.md` (page
  Nexus), `builder\` (exe : `inkflow\`, `README.md`, `LICENSE`, `build_exe.ps1`), `tools\inkflow_build.py`
  (générateur **v0.3**, figé), `tools\rdar.py`, `tools\build_canari.py` (figé), `tools\nexus_dl.py`,
  `templates\` (gabarits JSON neutralisés), `canari\` (v1-v5, hors git).
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
  `fullbody_overlay_d01.xbm`, corps Solo), V masculin ~~, FPP~~ (FPP livrée le 01/11 à 23 h 30, § 16). **Conséquence à écrire dans le README** :
  changer de corps après un build = rebâtir (la coque est une copie de l'ancien corps).

## Prochain geste (1.0)

1. **Avant publication** : ~~(a) `env.py` : test du bouton Download par lui (renommer ou vider
   `exe\home\wolvenkit\` ou `%LOCALAPPDATA%\InkFlow\wolvenkit\`, relancer l'exe, cliquer Download :
   45 Mo, SHA-256 vérifiée par l'outil)~~ **fait à 22 h, OK** ; ~~(b) README~~ fait (21 h 30) ; ~~(c) permissions~~ tranché
   « garder + créditer » (21 h 15), **lui : lire la boîte Permissions de 20279 sur le site** ;
   ~~(d) version 1.0.0, exe rebâti, SHA-256 notée~~ fait (21 h 18, `13c14eaa…`) ; ~~(e) dépôt GitHub~~
   fait (21 h 25) ; ~~(f) page Nexus~~ brouillon `NEXUS.md` (21 h 25), **à relire par lui** ; (g) **ses
   captures** (4 listées dans `NEXUS.md`, second écran) ; (h) **upload Nexus par lui** (zip + SHA-256
   dans la description du fichier), puis tag `v1.0.0` sur le dépôt. **Avant (g) et (h) : (0) la QA FPP**
   (bloc « État » ci-dessus) ; l'upload attend son verdict.
2. **Après la 1.0** : famille UV (corps Solo), icônes dans le créateur, ~~FPP~~ (livrée), V masculin, poids
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
- ~~**FPP** : aucune coque FPP ; non testable sur sa sauvegarde (créateur seul).~~ Livrée le 01/11 à
  23 h 30 (ETUDE § 16) ; **QA en jeu attendue**, points (a)-(e) du bloc « État ».
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
