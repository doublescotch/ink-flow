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

## État (2026-11-04, 22 h 45) : canari Angel tenu, Solo parqué sur sa décision ; gels = greffon NVIDIA Reflex ; jeu encore minimal

- **Plantages `memcpy` (ETUDE § 25)** : 5 sur 5 avec Solo dans le jeu ; le canari Angel (mêmes 2
  tatouages, aucun bras converti, jeu minimal) a tenu 3 chargements et de longues bascules de slots
  (sa QA, 22 h 20-22 h 32). Reste indistinct : Solo ou les bras convertis 8K (Solo seulement).
  **Sa décision (22 h 35) : Solo parqué, on n'y revient pas pour l'instant** ; priorité = corps VTK
  (Hyst, Angel, Eve, EBB, EBBRB) et tatouages UV sur VTK, déjà vus bons. En-tête Kala : corrigé.
- **Gels watchdog 120 s (4 sur 4, dumps lus)** : fil principal bloqué dans le greffon **NVIDIA
  Reflex** (`sl.reflex.dll`, chargé sous `170_E658703.dll`, `+0x3C43D`, chemin de présentation),
  Reflex pourtant Disabled dans ses réglages ; mémoire plate ; pas Ink Flow (le canari de 33 Mo gèle
  comme le jeu complet). ReShade, overlay NVIDIA, GPU Tweak III hors pile (GPU Tweak = aucune DLL
  dans le jeu, effet par le pilote possible, non prouvable). **Test à lui** : GPU Tweak fermé, Alt-Tab
  3 min ; puis overlay NVIDIA coupé ; puis `sl.reflex.dll` renommé (à sa main). ETUDE § 25, fin.
- **Son jeu maintenant : minimal** (Angel + refits + framework 3.2.1 + canari Angel 33,1 Mo, SHA
  `14f05dc1…`, 420 archives parquées). Sauvegardes `backup\` : `_175841` Angel 1.4.0 (conversions
  retournées, jamais planté), `_205556` Solo complet, `_215048` passe 1, `_221234` passe 2 Solo.
- **Retour à son jeu normal** (sa formule, jeu fermé) : `minimal_bench.py unpark_all`, puis rebuild
  complet moteur corrigé sur Angel (≈ 20 min, textures re-extraites, clé `mips2`) + `install`. Puis
  QA Angel (section Ouvert) et publication 1.4.0 (section Attend).
- **Réponse à sa question UV (22 h 40)** : un tatouage UV sur corps VTK = le corps marche sans le
  framework (même mise à plat que vanilla) ; ses bras sont **convertis au build** vers la mise à plat
  des bras VTK, et cette conversion lit le maillage de bras du framework **présent dans le jeu au
  moment du build** (`arm_refs`) ; sans lui, bras sautés, raison au journal. L'archive produite est
  autonome : rien ne pointe vers le framework en jeu.
- Télémétrie `vram_2026-11-04_c.csv` (scratchpad de la session) tourne jusqu'à 23 h 44.
- Lancement lent : sans objet (66 s jusqu'au menu, jeu complet comme minimal ; audioware 18 s).

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
- Bras convertis **dans les deux sens** (UV ↔ vanilla), framework UV requis sinon repli 1.3.0 (§ 22) ;
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
