# Passation — Ink Flow (VTK/UV CCXL Tattoo Loader)

Créée le 2026-11-01 à 2 h 45 (compartimentage demandé par Hell_Kaiser : chaque projet de création
porte sa passation et son journal dans son dossier ; `cp:HANDOVER.md` ne garde qu'un renvoi).
**Réécrite le 2026-11-04 à 22 h 30 sur sa remarque** (« pourquoi le handover s'est transformé en
log d'état ») : vingt-deux blocs « État » barrés, empilés heure par heure, sont partis ; la
chronologie est dans `LOG.md` (une entrée par séance, mêmes heures), les mesures, décisions et
acquis dans `ETUDE.md` (§ 1-25). Ce fichier ne porte que **l'état vivant** : un seul bloc d'état,
réécrit à chaque séance, puis ce qui est ouvert et ce qui attend Hell_Kaiser. Une entrée livrée ou
tranchée se barre avec ce qui l'a fermée ; un bloc d'état remplacé se réécrit, il ne s'empile pas.

Dépôt `https://github.com/doublescotch/ink-flow`, branche `master`, `canari\` exclu. Tags posés :
`v1.0.0`, `v1.0.1`, `v1.1.0`, `v1.2.0` ; 1.3.0 et 1.4.0 sans tag (jamais publiées).

## État (2026-11-05, 15 h 45) : FPP torse validé par lui ; trous sous les genoux expliqués, coque « jambes à plat » posée (canari v2), sa QA en cours

- **FPP torse : vu bon par lui (15 h 30)** sur le canari FPP (ETUDE § 27 : le corps en FPP = deux
  apps, torse 0-4 + jambes 5-7 ; compagnon `fpp_torso` codé). Samurai n'a pas d'encre sur la
  poitrine (sa texture) : Bedellia au slot 2 du canari v2 pour voir le torse plein.
- **Trous sous les genoux (photo, inventaire, FPP assis), cause mesurée (ETUDE § 27 bis)** : le jeu
  dessine mollets et pieds avec `l0_000_pwa_base__cs_flat` (pieds à plat ; chunk 5 coïncident, 6-7
  à 17-60 mm) et masque les chunks 5-7 du corps **par nom de composant** ; notre coque, nommée
  autrement, gardait 6-7. Texture éliminée (mips du Samurai sains). Pas une question de vue.
- **Correctif v2 codé** : `low_mask` (chunks sous 0,30 m) sur coque de corps féminine et FPP jambes ;
  compagnon TPP `legs_flat` = copie de `cs_flat`, texture du corps, **nommé `l0_000_pwa_base__cs_flat`**
  pour suivre les masquages des chaussures (hypothèse, à trancher par sa QA talons). Canari v2
  (Samurai + Bedellia, corps vanilla, 22 Mo) vérifié et **posé à 15 h 44** (sauvegarde `backup\2026-11-05_154440`).
- **Sa QA en cours** : tibias sans trous, cheville / pied encrés ; torse Bedellia en FPP ; talons =
  coque cachée sans trous (sinon repli : coque des talons, maillage `high_heels` = hash non résolu) ;
  jonction genou ; créateur / miroir inchangés. Ensuite Angel (même canari) puis le pack complet.
- **Ouvert, même mécanique** : « V habillée » (les habits masquent le corps par nom, pas nos coques :
  piste = nommer chaque coque comme le composant du jeu qu'elle copie, à mesurer après sa QA talons) ;
  V masculin : jambes jamais mesurées, `low_mask` non appliqué.
- **Son jeu** : instance re-régénérée depuis « Virgin » à 2 h, `archive\pc\mod` = Load Begone + Ink
  Flow 1.1 Samurai seul sur corps vanilla (15,5 Mo, SHA `08d84f60…`). Ses piles 1-3 à reposer par
  lui. Overlay NVIDIA coupé (gels, § 25). `minimal_angel.py` reste utilisable. Rien écrit par moi.
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
