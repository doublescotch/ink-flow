# Passation — Ink Flow (VTK/UV CCXL Tattoo Loader)

Créée le 2026-11-01 à 2 h 45 (compartimentage demandé par Hell_Kaiser : chaque projet de création
porte sa passation et son journal dans son dossier ; `cp:HANDOVER.md` ne garde qu'un renvoi).
**Réécrite le 2026-11-04 à 22 h 30 sur sa remarque** (« pourquoi le handover s'est transformé en
log d'état ») : vingt-deux blocs « État » barrés, empilés heure par heure, sont partis ; la
chronologie est dans `LOG.md` (une entrée par séance, mêmes heures), les mesures, décisions et
acquis dans `ETUDE.md` (§ 1-28). Ce fichier ne porte que **l'état vivant** : un seul bloc d'état,
réécrit à chaque séance, puis ce qui est ouvert et ce qui attend Hell_Kaiser. Une entrée livrée ou
tranchée se barre avec ce qui l'a fermée ; un bloc d'état remplacé se réécrit, il ne s'empile pas.

Dépôt `https://github.com/doublescotch/ink-flow`, branche `master`, `canari\` exclu. Tags posés :
`v1.0.0`, `v1.0.1`, `v1.1.0`, `v1.2.0` ; 1.3.0 et 1.4.0 sans tag (jamais publiées).

## État (2026-11-05, 19 h 45) : canari v4 validé vanilla ET Angel ; pack 1.4.0 + exe REBÂTIS, non posés

- **Sa QA du canari Angel (19 h)** : propre partout, identique au vanilla ; cheville plus longue au créateur seul.
  **Mesure (ETUDE § 29)** : le Samurai n'a aucune encre sur le pied, bord net ; même ensemble d'UV dans les deux
  coques ; au créateur l'encre finit même plus haut. Cause = autre chose (second calque ?), non bloquant.
- **Rebâtis avec le moteur actuel (son choix 19 h « mesure puis build »)** : exe `exe\dist\InkFlowBuilder.exe`
  22,7 Mo, SHA `8802c4d1…` ; pack complet `gen\uv104\out_pack` 1 577 s, 42 tatouages, **633,6 Mo / 2 646 fichiers**
  (avant correctif : 465,8 Mo / 1 632, gardé dans `out_pack_pre_fix_2026-11-05_0036`), SHA `36e00ca4…`, aucun
  conflit. Journal : `gen\uv104\pack_build_2026-11-05_1920.log`. **Pose sur son déverrouillage, puis sa passe courte.**
- **Validé par sa QA (18 h, canari v4 posé à 17 h 29, corps vanilla, Samurai + Bedellia)** : modificateur
  de l'appartement, créateur de nouvelle partie, mode photo, FPP assise jambe croisée : propres, aucun
  trou. Avec le v3 (16 h 35) : FPP tête baissée et inventaire propres. Torse plein à confirmer avec
  Promiscuity ou Vale (Samurai et Bedellia ont le ventre vide : leurs textures).
- **Mécanique (ETUDE § 28)** : le bas des jambes = deux options **cachées** du jeu, `lifted_feet` (corps
  chunks 5-7, pied levé) et `flat_feet` (`cs_flat`), chacune dans son groupe. Coques v4 : corps chunks
  0-4, `legs_lifted` dans `character_creation` + `lifted_feet`, `legs_flat` dans `flat_feet` seul.
- **Constat 1 de sa QA, non mesuré** : dessus de la main, le dernier hexagone de Samurai est coupé net,
  partout (créateur, photo). Hypothèse à trancher : l'encre de la texture continue sur la main, mais la
  main est dessinée par un autre maillage ou chunk que nos coques de bras. Mesure : quel composant
  dessine la main (sonde du 02/11, maillages `arms_hq`), puis l'encre de la texture à cet endroit.
- **Constat 2, mesuré (§ 29)** : au **créateur seul**, encre de cheville plus longue en escalier (vanilla et
  Angel, forme un peu différente). Ni texture, ni UV, ni étirement : hypothèse = second calque au créateur
  (coque à plat flottante ?). Mesure qui tranche : canari coloré (une teinte par coque) ou sonde (Redscript,
  Codeware, CET à poser). 1.4.1.
- **Canari v4 Angel** posé à 18 h 31 (7 archives de sa config minimale Angel copiées de l'arbre `3_Bodies`,
  `CANARI_BODY=angel`, SHA `1d2b193e…`, v4 vanilla dans `backup\2026-11-05_183135`) ; validé par lui à 19 h.
- **Prochain geste** : poser le pack rebâti (`pack_build.py install`, son déverrouillage) ; sa passe courte
  sur Angel (Samurai UV bras convertis, V masculin, bascules de slots longues, VRAM : le pack a grossi de
  36 %) ; zip ; crochets de `NEXUS.md` / README / sticky réécrits **après** cette passe ; upload. 1.4.1 :
  main, cheville du créateur, talons (Angel livre `l0_000_pwa_base__cs_heel.mesh`, chemin de Togglable
  Feet ; maillage vanilla toujours en hash `15467513564352523783`).
- **Canari v4** : `tools\qa_2026-11-05\canari_feet.py`, sortie `gen\uv104\out_canari_feet` (vanilla,
  SHA `bed06d81…`, 22,2 Mo) et `out_canari_feet_angel` (`CANARI_BODY=angel`, travail à part) ; v3
  sauvegardé dans `%LOCALAPPDATA%\InkFlow\backup\2026-11-05_172940`.
- **Son jeu** : instance Virgin + Load Begone + config minimale Angel (corps, Refits, tête VTK HD ×3,
  UV Framework 3.2.1) + canari v4 Angel ; Red Hot Tools BETA13 posé par lui ; ses piles 1-3 à reposer ;
  overlay NVIDIA coupé ; aucun plantage ni gel de la journée.
- **Ouvert, même mécanique** : « V habillée » (les habits masquent le corps par nom) ; V masculin :
  jambes jamais mesurées.
- **1.4.0 : tout est bâti, rien n'est publiable** : pack complet 465,8 Mo (`gen\uv104\out_pack`, SHA
  `da5757d2…`) et exe `exe\dist\InkFlowBuilder.exe` (SHA `a1bf1701…`) **d'avant le correctif**, à
  rebâtir ; zip non fait. `NEXUS.md`, README, sticky de `NEXUS_POSTS.md` : crochets « TO REWRITE
  AFTER THE FIX », **upload gelé** jusqu'à sa QA FPP et les trous ; les crochets se réécrivent après
  sa QA, jamais avant (faute du 05/11 à 2 h).
- **Reste ouvert de sa QA** : Skeleton Face sur tête masculine vanilla (tête vanilla, limite connue)
  ; Samurai coupé net à la cheville sur Angel (pieds dans la bande, § 21, remède = rééchantillonner
  les pieds comme les bras) ; Tortured Skin UV ×2 refusés (3 fichiers inconnus) ; FrecklesV à tester
  en classique.
- **Plantages `memcpy`** : 5 sur 5 avec Solo, Solo parqué sur sa décision (04/11). **Gels watchdog**
  : greffon Reflex dans la pile, overlay NVIDIA coupé = 16 min sans gel, suspect n° 1 (ETUDE § 25).
- **Caches** : exe = `%LOCALAPPDATA%\InkFlow\work`, bancs = `gen\uv104\work_game` ; copie vers le
  sien sur son go. Son catalogue réel n'a pas les noms des UV.
- **UV sur corps VTK** : le corps marche sans le framework ; les bras sont convertis au build et la
  conversion lit le maillage de bras du framework présent dans le jeu au moment du build
  (`arm_refs`).

## Ouvert (non tranché, non mesuré)

- **Gels watchdog** (18 h 13, 20 h 40, 21 h 47) : fil principal bloqué dans la présentation d'image,
  DLL anonymisée `170_E658703.dll` dans la pile, `dxgi.dll` une fois : crochet sur Present (ReShade
  `d3d12on7`, overlay, pilote). Second phénomène, non attribué, non traité.
- **Remèdes mémoire prêts à coder si la mesure le dit** : une texture pour les deux bras convertis
  (moitié G / moitié D, −64 Mo par VTK porté) ; conversion en 4K au lieu de 8K (la bande = 22 % de
  la largeur). Poste au repos : VRAM 3,0 / 8 Go, RAM 19,9 / 32 Go ; au plantage de 20 h 14 : 7,35 Go
  et 29 Go. Rien codé avant la mesure.
- **FPP hors miroir sur Solo : ventre sans tatouage** : masque FPP du torse = vanilla, l'`.app` de
  Solo ne se sérialise pas au CLI 9.1.0 (`castShadows`, § 21). Lire les masques autrement ; après.
- Dimensions vues dans les piles (carrés de 1 980 et 2 204 unités de 16 o) : aucune texture du
  build ni de Solo / framework (70 en-têtes exportés, toutes en puissances de deux). Non identifiée.
- **QA Angel avec le moteur corrigé, jamais faite** : Samurai UV (le deltoïde nu était la conversion
  retournée, § 24), Kala Sleeve 1 (manches), Bedellia (raccord d'épaule), FPP, V masculin, opacité
  par tatouage (jamais vue en jeu : deux tatouages à 0,5 et 1,0 au créateur).
- **Têtes** : la coque de tête ne s'affiche pas sur tête vanilla (§ 17 ; vérifier d'abord Angel +
  tête VTK HD) ; tête du V masculin (`FACE TATTOOS-7414-V2-KALA-MALEV-VTK`, Kala Faded Face dans
  `3_Bodies\__RAM`, sur Gymfiend + MV Head) ; miroir / FPP / photo du V masculin ; tête masculine UV
  jamais mesurée (`ma_head_overlay_d01`, aucun pack).
- **Jamais vus en jeu** : Songbird body (plaques cyber masquées par le code), EBBRB (accepté par le
  builder), bras cybernétique, V habillée (masques par nom de composant), couture au cou
  (`femv_vtk_headpatch`, seamfix d'Angel), groupe `TPP_photomode` de la tête.
- Décal vanilla = diffuse seule (retour Nexus « partie métallique absente ») : piste = décal
  rugosité / métal / normale du corps Songbird, chantier à part.
- Pack masculin Kala V2 : même en-tête faux (§ 19, § 25), couvert par `normalize_textures`.
- Ses mots du 03/11 « là j'avais aucune différence pour moi » : à préciser par lui, rien supposé.
- Sa remarque du 04/11 : les corps purement UV (Solo, Songbird) ne sont plus d'actualité ; la
  priorité = UV sur VTK (Angel, EBB, vanilla), déjà vu bon. Solo : page Nexus signale des plantages
  au chargement 2 fois sur 3 (post du 28/08/2026), hypothèse concurrente.
- Hook : cas 204 (listing WolvenKit pris pour une écriture) à qualifier avec 203, séance pipeline.

## Attend Hell_Kaiser

- **Publication 1.4.0** (après la QA Angel ; 1.2.0 et 1.3.0 jamais uploadées, la 1.4.0 les
  remplace) : statuts entre crochets de `NEXUS.md` et du README (« [IN-GAME STATUS] », Solo vu au
  créateur seulement, lien framework = Nexus 3783 à confirmer : son 3.2.1 vient de son zip) ; exe +
  zip (`build_exe.ps1`, numpy ≈ +15 Mo) ; upload avec SHA-256 dans la description ; capture de la
  fenêtre (colonne cibles « (UV) ») ; sticky de `NEXUS_POSTS.md` ; tags `v1.3.0` et `v1.4.0` sur go.
- Fichiers macOS laissés par l'installateur WolvenKit : `engine\tools\scc`, `libscc_lib.dylib`,
  inoffensifs, à supprimer par lui.
- Effets visibles annoncés et jamais regardés : plus d'encre sur le port de lien du bras gauche ;
  trait possible sur une couture du dépliage des bras convertis, bras un peu plus doux.

## Décisions gravées (détail dans ETUDE)

- Slots = réglage du **builder**, 1 à 9, défaut 2, index 1041-1049 ; rien dans Mod Settings (§ 11).
- Rien dans le sélecteur vanilla ; miroir ouvert (`HairDresser`, v0.3b) ; noms ≤ 20 caractères.
- Tête = même recette que le corps (copie du maillage actif + morphtarget), aucun masque (§ 12).
- Bras convertis **dans les deux sens** (UV ↔ vanilla), framework requis sinon repli 1.3.0 (§ 22) ;
  image WolvenKit lue avec **v = 1 − y/h** (§ 24) ; en-têtes contrôlés et textures reconstruites en
  BC7 `--keep` (§ 25).
- Un banc ou un canari = seulement les tatouages de la question, jamais sa liste entière (04/11).
- Limites gravées (README, `NEXUS.md`) : calques très pâles invisibles (FrecklesV) ; un corps non
  mis à jour pour 2.5 reste cassé sous Ink Flow ; corps VTK = critère du builder, pas une liste.

## Où sont les choses

- Projet (OneDrive, dépôt git) : `ETUDE.md`, `LOG.md`, `NEXUS.md`, `NEXUS_POSTS.md`, `builder\`
  (`inkflow\`, `InkFlowBuilder.py`, `inkflow_cli.py`, `tests\`, `build_exe.ps1`), `releases\`
  (zips 1.0.0 → 1.3.0, captures), `tools\` (`qa_2026-11-02..04\`, `probe\` = sonde Redscript,
  `inkflow_build.py` v0.3 figé, `rdar.py`, `nexus_dl.py`), `templates\`, `canari\` (hors git).
- Outils du jour, `tools\qa_2026-11-04\` : `solo_bench.py` (`park | build | install | restore |
  status`), `minimal_bench.py` (`park_all | unpark_all | status`), `canari3.py` (`build | install`),
  `regress_female.py <ref>`, `test_normalize.py`, `seam*.py` (`seam7.py` = l'outil qui vaut).
- Jetable (poste) : `C:\__DEV\cyberpunk\ink_flow\` : `gen\uv104\` (`catalogue_game_copy.json`,
  `work_*`, `out_*`, journaux), `dl\uv\` (Solo, framework, 16 UV, `conv\` ≈ 1 Go), `dl\6423_*`,
  `parked\2026-11-04_angel\` (vide depuis 22 h 09), `exe\dist\`, `builds\`, `in\`, `src\`.
- `%LOCALAPPDATA%\InkFlow\` : config, catalogue, cache, WolvenKit, `backup\<stamp>\` (anciens
  `Ink_Flow` : `_175841` Angel 1.4.0, `_205556` Solo complet, `_215048` passe 1, `_221234` passe 2).
- Jeu : `archive\pc\mod\Ink_Flow.archive` + `.xl` ; écriture = `WRITE_UNLOCK.txt` sur le dossier du
  jeu (60 min) ou la formule ; jeu fermé. Rapports : `%LOCALAPPDATA%\REDEngine\ReportQueue\`.
