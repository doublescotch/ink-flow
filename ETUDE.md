# Étude — sélecteur de tatouages UV / VTK dans le créateur de personnage (CCXL)

Écrite le 2026-10-31 (Claude Fable 5.1), à la demande de Hell_Kaiser. Lecture seule : rien n'est construit, rien n'est posé dans le jeu. Tout ce qui est affirmé ci-dessous a été **lu dans les fichiers** (`V's Body.zip`, archives du jeu 2.5 sur `E:`, CLI WolvenKit 9.1.0) sauf mention « à mesurer ».

## 1. Demande

Un mod où le joueur **référence ses archives de tatouages** (UV ou VTK) et les retrouve **dans le créateur de personnage vanilla** pour les choisir en jeu (mode RP), avec :
- route 1, classique : les tatouages référencés apparaissent dans le sélecteur de tatouage vanilla (un seul choix) ;
- route 2, avancée : un interrupteur à la Heterochromia qui débloque une série de sélecteurs par partie du corps (tête, torse, dos, bras G/D, jambes G/D), chacun pouvant recevoir n'importe quel fichier ; le mod ne distingue pas les parties, il charge le fichier, la priorité habituelle règle les chevauchements ;
- plus tard, le même principe pour d'autres options du corps (archives de skins).

## 2. Ce que font les archives actuelles (lu)

| Famille | Fichier remplacé par l'archive | Où ce fichier est branché |
|---|---|---|
| UV (X_Common `002_Tattoos_UV_*`) | `base\4k\common\overlays\fullbody_overlay_d01.xbm` (+ `wa_head_overlay_d01.xbm` pour Garden Bloom) | `SecondaryAlbedo` du matériau du **corps** : chaîne `.mi` du framework UV 3.2.1, `default_body_01_ca_pale.mi` (idem `ma_fullbody_overlay_d01` côté masculin) |
| VTK corps (Angel `002_Tattoos_VTK_*`) | `base\v_textures\body\v_overlay.xbm` | `SecondaryAlbedo` des matériaux locaux de `t0_000_pwa_base__full.mesh` du corps Angel |
| VTK bras (Kala) | `base\characters\player\femme\body\arms\textures\femme_arm_left_01_overlay.xbm` (et `right`) | `SecondaryAlbedo` des matériaux des bras `a0_000_pwa_base_hq__l/r.mesh` du corps Angel |
| VTK tête | `h0_001_pwa_c__basehead_overlay.xbm` | matériau de la tête VTK |

**Conséquence 1** : une archive de tatouage UV/VTK n'est **pas** un tatouage au sens du créateur : c'est une couche peinte en permanence sur la peau, hors sélecteur. Deux archives qui visent le même fichier ne se superposent pas : la première chargée gagne (ordre alphabétique des `.archive`).

**Conséquence 2 (question de Hell_Kaiser)** : les tatouages du sélecteur vanilla sont des **maillages-coques** séparés (`tx_000_pwa_base__full_tattoo_01..05.mesh`, option `body_tattoo_0N` → `t0_000_base__tattoo_0N.app`). Les coques livrées par Angel et Solo 2.0 sont des refits de forme, mais leurs matériaux pointent **toujours** sur les textures vanilla (`tattoo_body__customisation_0N_d02.xbm`). Donc : l'overlay UV/VTK et un tatouage vanilla sélectionné **se cumulent** à l'écran, rien ne masque rien ; le joueur n'a pas à remettre le sélecteur à zéro, sauf s'il ne veut pas voir les deux.

## 2 bis. Les « slots » que les frameworks offrent déjà (question du 31/10)

Les frameworks ne connaissent **aucune partie du corps** : ils connaissent des **fichiers**. Un fichier = un slot ; deux archives qui visent le même fichier ne se superposent pas (la première chargée gagne, ordre alphabétique) ; deux archives qui visent deux fichiers différents coexistent sans se gêner. Dans l'arbre extrait de `3_Bodies` (ta sélection assemblée : Angel + `005_Songbird_Arms_UV` + UV 3.2.1 + tête VTK HD), les surfaces et leurs fichiers sont :

| Surface | Maillage actif (arbre) | Fichier d'overlay lié | Qui le remplace aujourd'hui |
|---|---|---|---|
| Torse, dos, jambes | corps Angel `t0_000_pwa_base__full.mesh` (VTK) | `base\v_textures\body\v_overlay.xbm` | `002_Tattoos_VTK_Kala_Japanese_Arm_Body` |
| Tête | tête VTK | `…\h0_001_pwa_c__basehead_overlay.xbm` | `002_Tattoos_VTK_Kala_Japanese_Arm_Head` |
| Bras (TPP et FPP) | bras Songbird UV `a0_000_pwa_base_hq__l/r.mesh`, `fpp\a0_000_pwa_fpp__full_l/r.mesh` (005 charge avant 006 : ils l'emportent sur les bras VTK d'Angel) | `base\4k\common\overlays\fullbody_overlay_d01.xbm` via la chaîne `.mi` UV 3.2.1 (`female_0X.mi` → `default_female_body_0X.mi` → `default_body_0X.mi`) | personne (aucun `002_Tattoos_UV_*` dans l'arbre) |
| Bras VTK | `femme_arm_left/right_01_overlay.xbm` | — | `002_Tattoos_VTK_Kala_Japanese_Arm_Left/Right` : **sans surface** dans ce montage d'après les fichiers, puisque les bras affichés sont les bras UV ; **à vérifier en jeu** (si les manches Kala s'affichent, mon ordre de priorité est faux) |
| Glow (émissif) | mêmes maillages | `v_glow.xbm` (VTK), `glow_overlay_d01.xbm` (UV), `femme_arm_*_glow.xbm` | — |

Donc le pack Kala en 4 parties n'est pas « 4 tatouages superposés » : ce sont 4 fichiers distincts, un par surface, et c'est le framework qui les répartit. Pour un UV « full body » sur ce montage, la texture est un seul fichier corps + bras (mise à plat UV) mais n'a de surface que sur les bras ; le torse reste VTK.

**Pour le mod** : les « parties du corps » de la route 2 ne peuvent pas être calquées sur les slots des frameworks (il n'y en a que 3 par surface : corps, tête, bras). Les slots du mod sont des **couches** indépendantes (coques), et c'est le dessin du fichier qui décide où le tatouage apparaît ; c'est cohérent avec ta consigne « le mod ne fait pas la différence, il charge le fichier ».

## 3. Mécanisme du créateur (lu dans `female_cco.inkcharcustomization`)

- `body_tattoo` = `gameuiSwitcherInfo` (uiSlot `body_tattoo_switcher`, pilote le slot `body_tattoo`), 8 options `body_tattoo_00..07` ; chaque option est un `gameuiAppearanceInfo` sur le slot `body_tattoo`, `link = skin color`, qui pointe un `.app` ; l'`.app` a une appearance par teint (`w__01_ca_pale`…) dont le composant est la coque avec `meshAppearance` = teint.
- Fusion CCXL (wiki, confirmée par le pack Kylin) : une option **sans nom** avec `link = hairstyle` s'ajoute au sélecteur vanilla ; une option de même `name` fusionne ; sinon elle est ajoutée. Le même geste sur `link = body_tattoo` ajoute nos tatouages **au sélecteur vanilla** (route 1).
- Heterochromia (lu) : un `gameuiSwitcherInfo` `heterochromia` à deux options ; « off » active `eyes_color` + `eyes_color_none`, « on » active `eyes_color_left` + `eyes_color_right` (deux `gameuiAppearanceInfo` sur les slots `eyes_color` et `eyes_color_2`, chacun avec son `.app` et un maillage d'yeux coupé en deux). C'est exactement le patron de la route 2 : un interrupteur, N slots, chaque slot = un `gameuiAppearanceInfo` avec la liste complète des tatouages.

## 4. Verdict de faisabilité

**Faisable, mais pas « dynamique » au sens strict.** Le jeu adresse une ressource par le hachage de son chemin ; une archive de tatouage ne contient qu'une texture au chemin `fullbody_overlay_d01` (ou `v_overlay`). Rien, ni ArchiveXL ni un script, ne peut à l'exécution dire « cette archive-ci dans ce slot-là » : il faut que chaque tatouage vive **sous un chemin unique**. Le mod est donc un **générateur** (Python + CLI WolvenKit, comme `build_anoise3.py`) :

1. le joueur dépose ses `.archive` de tatouages dans un dossier du mod (ou les référence dans un fichier) ;
2. le générateur lit chaque archive, reconnaît la famille à la texture qu'elle remplace (table § 2), extrait le `.xbm` et le replace sous `hk\tattoos\<slug>\overlay.xbm` ;
3. il écrit l'`.inkcharcustomization` (pwa/pma), un `.app` par tatouage, la localisation (noms = nom de fichier), les icônes (`OptionsIcons` TweakXL + `.inkatlas`, optionnel au début), le `.xl`, et emballe une seule `.archive` + `.xl` ;
4. relancer le générateur après un ajout ; les choix en jeu sont stockés **par nom d'option** : un slug stable par fichier, sinon le personnage perd son choix.

Le rendu passe par des **coques**, comme les tatouages vanilla et comme CCXL Tattoo Toolkit / Fun Tattoos Overhaul (qui livre « Vanilla VTK, Angel & EBBRB ») : une coque par slot actif, matériau de coque avec `DiffuseTexture` = la texture du joueur.

## 4 bis. Forme de livraison (Hell_Kaiser, 2026-10-31 : « un FOMOD qui compile à partir des archives du joueur, ça me va »)

Un FOMOD ne compile rien : script de choix Vortex/MO2, il copie des fichiers présents dans le paquet. Deux montages :

1. **Paquet pré-converti + FOMOD de choix** : on convertit les packs connus à l'avance. Écarté par défaut : redistribution des textures d'autres auteurs (Fun Tattoos Overhaul l'interdit explicitement ; norme Nexus pour les tatouages).
2. **Builder complet chez le joueur, modèle Lethal Curves** (**retenu**, précisé par Hell_Kaiser le 31/10 : « un outil .exe comme mon pack Lethal Curves, qui construit l'archive de notre mod en y incluant les tatouages convertis que l'utilisateur sélectionne ; je vise large, un outil pour tout le monde »). Lu dans `3_Bodies\__RAM\…Modular Rig Deform Builder-23462-2-1-1.zip` : exe Python (PyInstaller, interface WebView2 + bottle, pythonnet), **gabarits JSON au format WolvenKit** dans `_internal\resources\axl\` (`app.app.json`, `rootentity.ent.json`, `fpp_meshentity.ent.json`, `localization.json.json`, `factory.csv.json`, `icon.inkatlas.json`, `.xl`), et un écran de setup qui fait **télécharger WolvenKit Console au joueur** (`ui\assets\images\setup\wolvenkit-console-download.png`) : le CLI convertit les JSON en fichiers du jeu et emballe l'archive. Rien d'autrui n'est redistribué.

   Transposé aux tatouages : le joueur glisse ses `.archive`, coche ceux qu'il veut, l'outil reconnaît la famille (table § 2), extrait les textures (CLI), les replace sous `hk\tattoos\<slug>\…`, génère depuis les gabarits l'`.inkcharcustomization` pwa/pma, un `.app` par tatouage, la **localisation avec le vrai nom du fichier**, les icônes (miniature réduite de la texture → `.xbm` + atlas, comme Lethal Curves compose ses icônes en PNG), le `.xl`, et sort **une** archive + `.xl` à poser. Nombre de slots libre. Les choix en jeu étant stockés par nom d'option, l'outil garde une table `fichier → slug` pour que la régénération ne fasse pas perdre le personnage.

   Variante allégée gardée en réserve : partie statique pré-construite + simple réécriture de l'empreinte FNV-1a 64 du chemin de la texture (Python pur, sans WolvenKit), au prix de noms génériques ; utile seulement si la dépendance à WolvenKit Console posait problème, ce que Lethal Curves montre acceptée par la communauté.

   ~~Coûts propres au builder : gabarits à maintenir **par corps** (Angel/VTK, Solo/UV, vanilla, masculin), setup WolvenKit Console à la première exécution, taille du paquet (Lethal Curves : 2 Go décompressé, 62 572 fichiers, surtout ses presets).~~ **Corrigé le 2026-10-31 soir après le canari** (question de Hell_Kaiser : « pourquoi lourd ? une archive de tatouage n'est pas spécifique à un corps ») : une archive de tatouage est une **texture seule** dans une mise à plat ; seules **deux familles** de mise à plat existent (VTK = vanilla, qu'Angel reprend ; UV Framework = Solo 2.0, Songbird), la forme du corps ne fait qu'étirer le dessin avec la surface, pas de cuisson par corps. La seule pièce propre à un corps est la **coque**, et les mods de corps la livrent déjà aux chemins vanilla : le builder **lit la coque active chez le joueur** (son `archive\pc\mod`, la première chargée gagne, sinon le jeu de base), lui change sa texture et la sort sous `inkflow\` : c'est ce que `build_canari.py` fait, **aucun gabarit par corps à embarquer**. Reste par famille : la coque livrée par Solo est dessinée dans la mise à plat vanilla (ses matériaux pointent les textures vanilla), donc pour un corps UV il faut une coque à la mise à plat UV, dérivable du corps UV lui-même (mesure § 5.1). Coûts réels : setup WolvenKit Console, et le poids des textures du joueur (Samurai 8K = 8,8 Mo d'archive). Les 2 Go de Lethal Curves étaient ses presets.

## 5. Risques et mesures à faire, dans l'ordre

1. **UV des coques (bloquant pour le corps Solo / UV)** — les coques Angel/Solo sont dessinées pour les textures vanilla ; la texture UV Framework suit la mise à plat du **corps** UV (un seul fichier corps + bras). Une coque pour tatouage UV doit donc être dérivée du **corps Solo** lui-même (copie gonflée, Blender, `Solo 2.0 Refit.blend` existe) ; pour VTK (Angel), la mise à plat corps est celle de vanilla, les coques Angel existantes devraient convenir. **À mesurer** : exporter corps et coque en glb (CLI `export` exige un dépôt déballé dans les réglages WolvenKit, non fait ici) et comparer les UV.
2. **Chevauchement de coques (route 2)** — deux coques pleines l'une sur l'autre peuvent scintiller (z-fighting) là où les deux ont de l'alpha. Vanilla cumule déjà cicatrices + tatouage facial ; **canari** : deux slots, deux fichiers, regarder en jeu avant d'aller plus loin. Si ça scintille : coques à gonflement croissant par slot, ou une coque par **zone** (torse, dos, bras…) découpée par chunk, ce qui redonnerait un sens aux parties du corps.
3. **Teint de peau** — les coques vanilla ont un matériau par teint (`customization_tattoos_<teint>.mi`). Première version : un seul matériau pour tous les teints (c'est déjà ce que fait l'overlay actuel). Ensuite, ArchiveXL dynamic materials (`{material}`, `*` + Soft, ≥ 1.27) pour éviter de dupliquer les maillages.
4. **Bras UV sur Angel** — le setup Angel met des bras UV sur un corps VTK : un tatouage UV n'y touche que les bras. Le générateur doit poser la coque **par cible** (corps VTK, bras UV, tête) selon le fichier remplacé, pas par archive.
5. **Icônes** — 39 icônes par pack dans Beautiful Exotics ; pour nous, une miniature générée depuis la texture (réduction PNG → `.xbm` + atlas) est possible, ou pas d'icône au départ (texte seul). Character Creator UI Improvements (34310, Codeware) offre une grille quand il y a beaucoup d'options.
6. **Ordre d'archives** — nos coques ne remplacent rien ; mais les archives de tatouages d'origine doivent être **retirées** du jeu (sinon l'overlay permanent reste). Le générateur peut le dire explicitement.

## 6. Extension aux skins (idée du 31/10)

Même générateur, autre table : une archive de skin remplace `d02_naked.xbm` / `n02_naked.xbm` / `wa_base_rm02.xbm` (UV) ou `v_body_d/n/rm.xbm` (VTK), parfois 4 à 10 fichiers d'un coup (Arkhe Universal Skin). Dans le créateur, `skin_color` est un `gameuiAppearanceInfo` à 12 définitions (icône + nom d'appearance de la tête) et chaque corps/coque/bras a une appearance **par teint**. Ajouter une option « skin » = ajouter une 13e définition et son appearance dans **tous** les maillages concernés (corps, bras, tête, coques, et les refits de vêtements qui exposent la peau). C'est une tout autre échelle : chaque mod de corps devrait être patché. Plus réaliste : garder les skins en remplacement de fichier (comme aujourd'hui) et ne mettre dans le créateur que ce qui est une **couche** (tatouages, taches de rousseur, maquillage). À trancher plus tard, après la preuve des tatouages.

## 7. ~~Prochain geste proposé (sur go)~~ Canari construit le 2026-10-31 (go de Hell_Kaiser), à poser et juger en jeu

~~Un **canari** avant tout générateur : à la main, dans WolvenKit, un `.xl` + `_pwa.inkcharcustomization` avec **une** option ajoutée au sélecteur `body_tattoo`, un `.app` et une coque Angel existante repointée sur `hk\tattoos\samurai\overlay.xbm` (texture tirée de `002_Tattoos_VTK_Samurai`). Succès = le tatouage apparaît dans le créateur et s'affiche sur Angel. Puis même chose avec deux slots (route 2) pour juger le chevauchement. Seulement ensuite le générateur.~~

**Nom du mod (Hell_Kaiser, 2026-10-31) : Ink Flow — VTK/UV CCXL Tattoo Loader.** Préfixe de chemins `inkflow\`. L'exe du builder demandera un dépôt git ouvert pour la confiance ; **aucun git pour l'instant, le proto d'abord** (Hell_Kaiser).

**Construit** par `tools\build_canari.py` (Python + CLI WolvenKit 9.1.0, sans WolvenKit GUI) : `canari\Ink_Flow_Canari.archive` (8 fichiers, 8,8 Mo) + `.xl`. Travail jetable dans `C:\__DEV\cyberpunk\ink_flow\` (sources extraites `x\`, toolkit 20279 dans `dl\`, `build\`). Contenu :
- `inkflow\tattoos\samurai\samurai.xbm` = `v_overlay.xbm` de `002_Tattoos_VTK_Samurai` copié à l'octet (8192², BC7, mips ; même mise à plat que la texture vanilla `tattoo_body__customisation_01_d02`, vérifié sur les PNG) ;
- `samurai_pwa.mesh` + `samurai_pwa.morphtarget` = la coque Angel `tx_000_pwa_base__full_tattoo_01` (mesh et morphtarget `breast_big`) avec ses 24 instances locales de matériau repointées (`DiffuseTexture` → notre texture ; `baseMaterial` inchangé = `customization_tattoos_<teint>.mi`, c'est-à-dire `mesh_decal.mt` à `DiffuseAlpha` 0,6 : l'opacité vanilla, **à juger**, 1,0 possible) ; `samurai_fpp_pwa.mesh` = idem pour la coque FPP ;
- `samurai.app` (gabarit toolkit `chest_tattoo.app`, `entMorphTargetSkinnedMeshComponent` → notre morphtarget, `meshAppearance` `01_ca_pale`, `components` **et** `compiledData` repointés) et `samurai_fpp.app` (gabarit `arm_tattoo.app`, `entGarmentSkinnedMeshComponent`) ;
- `inkflow_pwa.inkcharcustomization` : **route 1** = switcher sans nom `link=body_tattoo` (patron Kylin) dont l'option « Samurai (Ink Flow) » active `inkflow_samurai` (uiSlot `body_tattoo`) + `inkflow_samurai_fpp` (uiSlot `fpp_body_tattoo`) ; **route 2** = switcher `inkflow_slot1` index **3350** (3300-3309 sont réservés au toolkit), uiSlot `inkflow_slot1_switcher`, options Off / Samurai → même `.app` ; `link=None` partout (un seul matériau pour tous les teints, comme le toolkit) ;
- `localization\inkflow_en-us.json` (JsonResource, 2 clés `UI-Customization-inkflow_*`) ; `.xl` = `customizations.female` + `localization.onscreens.en-us`, sans scope.

Vérifié hors jeu : archive dépaquetée et resérialisée, tous les chemins en clair et cohérents (morphtarget → mesh, .app → morphtarget/mesh, inkcc → .app, loc), texture identique à la source (SHA-256).

**Acquis de lecture (toolkit 20279 + vanilla)** : une coque CCXL = `.mesh` à une entrée de matériau locale (`baseMaterial` = `.mi` sur `mesh_decal.mt`, `DiffuseTexture` = la texture), `.morphtarget` (pwa, cible `breast_big`) ou `.mesh` seul (pma, fpp), `.app` à **une** appearance `w__<nom>` avec `components` en clair (pas de `partsValues`), appearance info `enabled 0 hidden 1`, groupes `FPP_Body`/`TPP_Body`/`character_creation` à renseigner. Le vanilla `body_tattoo` est un switcher `link=body_tattoo`, `linkController 1`, ses infos `body_tattoo_0N` ont `link=skin color` et 12 définitions `w__<teint>` ; `fpp_body_tattoo` suit par `link=body_tattoo`.

**Posé dans le jeu le 2026-10-31 soir** (`archive\pc\mod\Ink_Flow_Canari.archive` + `.xl`, identiques à `canari\` par SHA-256, jeu fermé ; déverrouillage par `WRITE_UNLOCK.txt`, la formule ayant été masquée par un bloc injecté : cas 202 du registre des hooks). Rien à retirer (Kala reste : overlay permanent + coque, c'est un premier test de chevauchement). **QA en jeu** : (1) `red4ext\logs\archive_xl-*.log` sans erreur sur `inkflow` ; (2) créateur / Ripperdoc : « Samurai (Ink Flow) » en fin du sélecteur Tatouage corps ; un sélecteur « Ink Flow - Slot 1 » ; (3) le Samurai s'affiche sur Angel, placé comme l'overlay VTK (si décalé : la coque Angel ne suit pas la mise à plat VTK) ; (4) vue FPP : manches visibles ; (5) opacité 0,6 acceptable ou non ; (6) les deux sélecteurs cochés en même temps = deux coques identiques superposées : scintillement ? (7) retirer l'archive : le personnage sauvegardé avec l'option perd-il proprement le tatouage ?

**QA du 2026-10-31 soir (Hell_Kaiser, captures)** : le jeu démarre ; « Body Tattoos : Samurai (Ink Flow) » dans le sélecteur vanilla ; le Samurai s'affiche sur Angel, **par-dessus** le Kala permanent encore en place (deux couches cumulées, lisibles toutes deux) : points 1 à 3 vus. Kala sera retiré pour la suite des tests. Restent FPP, opacité, les deux sélecteurs cochés ensemble, retrait propre. (Artefacts en vagues sur la peau des captures = ShareX, pas le jeu.)

**Deuxième QA du 31/10 soir (Kala retiré, captures)** : le sélecteur custom marche ; FPP non testable (sauvegarde au tout début, pas de miroir ni de Ripperdoc, seulement le créateur). Trois défauts :
1. **Gris sur le sélecteur custom, noir sur le vanilla, inversion en désactivant le custom.** Cause lue dans ce que j'ai construit : v1 donnait le **même `.app` et le même nom de composant** (`inkflow_samurai`) aux deux sélecteurs ; désactiver le slot custom retirait le composant par son nom, donc aussi celui du vanilla ; restait la coque FPP (`inkflow_samurai_fpp`, que l'option vanilla active aussi dans le créateur) seule à 0,6 = gris. Le « noir » du vanilla = deux coques empilées (TPP + FPP). Donc : opacité d'une coque seule à 0,6 = trop pâle.
2. **Couture du bras** : bras plus clairs que le torse, et tatouage du bras coupé à l'épaule, **même sans tatouage actif**, disparaît si Ink Flow est retiré (captures 1 à 3). Non expliqué. Journal ArchiveXL comparé entre lancement avec (19 h 36) et sans (19 h 47) : **aucune différence** hors la fusion de notre localisation, aucune erreur ; la fusion `customizations` n'est pas journalisée. Angel porte un seamfix VTK (`femv_seamfix.app` patché dans le corps, mesh `t0_000_pwa_base__full_seamfix`, matériaux `neckMAT`/`armsMAT`, zone épaules-cou) : piste = le seamfix ou le teint des bras ne suit plus quand notre `.inkcharcustomization` est fusionné. Le « tatouage coupé » est peut-être le dessin lui-même (la texture Samurai n'a presque rien sur le devant du torse) ; la couture de peau, elle, est réelle.
3. Opacité : voir 1.

**v2 construite** (`tools\build_canari.py`, `--alpha` 1,0 par défaut, `--fpp`, `--no-route1`, `--no-route2`, `--tag`) : un `.app` et un nom de composant **par slot** (`inkflow_samurai`, `inkflow_slot1_samurai`), **opacité 1,0**, **sans coque FPP** dans l'option vanilla (pour vérifier l'empilement). Trois variantes dans `canari\v2\` pour bissecter la couture : **A_complet** (posée dans le jeu le 31/10 soir), **B_slot1_seul** (sans l'option du sélecteur vanilla = sans le switcher `None` lié à `body_tattoo`), **C_vanilla_seul** (sans le sélecteur propre). Même nom de fichier : on remplace les deux fichiers dans `archive\pc\mod`.

~~**QA v2 à faire** : (a) A : les deux sélecteurs rendent-ils le même noir, et chacun se désactive-t-il sans toucher l'autre ? (b) A : la couture du bras est-elle encore là sans tatouage ? si oui, B puis C : laquelle la fait disparaître ? (c) opacité 1,0 : trop dur ou juste ?~~ **QA v2 A validée par Hell_Kaiser le 31/10 soir** : couture du bras **disparue** (« ça affiche bien »), les deux sélecteurs rendent la même teinte correcte, plus d'inversion à la désactivation, les deux cochés = noir à peine plus noir, aucun artefact. B et C sans objet. Cause probable de la couture, **non prouvée** : la coque FPP (`inkflow_samurai_fpp`, Angel `tx_000_pwa_fpp__full_tattoo_01`) que l'option vanilla activait dans le créateur, seul changement structurel entre v1 et v2 hors les `.app` séparés ; à confirmer en la remettant (`--fpp`) quand la vue FPP sera testable (miroir ou Ripperdoc). **Reste ouvert pour la FPP réelle** : en vanilla `fpp_body_tattoo` suit `body_tattoo` par `link` et par **index d'option**, pas par nom ; notre option ajoutée au sélecteur vanilla prend un index hors de la liste FPP ; à mesurer en jeu si le tatouage apparaît en première personne, sinon il faudra un switcher `None` lié à `fpp_body_tattoo` avec le même index.

~~**Prochain geste après la QA** : deux slots avec deux fichiers différents (chevauchement réel), puis le générateur (route 2 avec N slots, un `.app` par fichier, noms réels), puis la mesure UV des coques Solo pour le corps UV.~~

**v3 construite le 2026-10-31 (21 h) : deux fichiers, deux slots** (`canari\v3\`, archive 10,9 Mo, 16 fichiers ; `tools\build_canari.py` généralisé : table `FILES` slug → texture, `--files samurai,kala`, `--slots 2`). Par fichier : texture copiée à l'octet, coque TPP + FPP et morphtarget Angel repointés dessus (la coque porte le renvoi vers la texture) ; par (slot, fichier) : un `.app` et un nom de composant uniques (`inkflow_slot1_samurai`, `inkflow_slot1_kala`, `inkflow_slot2_*`). Sélecteurs `inkflow_slot1` (index 3350) et `inkflow_slot2` (3351), options Off / Samurai / Kala chacun ; route 1 inchangée (Samurai seul dans le sélecteur vanilla, sans coque FPP). Kala = `v_overlay.xbm` de `002_Tattoos_VTK_Kala_Japanese_Arm_Body`, **2048², TrueColor sans mips** (le Samurai est en 8192² BC7 avec mips) : deux formats de texture différents, voulus. Structure vérifiée après dépaquetage (switchers, infos, groupes `TPP_Body`/`FPP_Body`/`character_creation`). Même nom de fichier que la v2 : remplacer les deux fichiers dans `archive\pc\mod`.

**QA v3 à faire en jeu** : (a) les deux sélecteurs « Ink Flow - Slot 1 / 2 » offrent Off / Samurai / Kala ; (b) Slot 1 = Samurai, Slot 2 = Kala : les deux dessins se superposent-ils proprement (scintillement ou non là où ils se recouvrent, Kala passe-t-il par-dessus ou dessous) ; (c) Kala seul : net ou flou de près (2048² sans mips) ; (d) Slot 1 = Kala, Slot 2 = Samurai : l'ordre des slots change-t-il qui est dessus ; (e) désactiver un slot ne touche pas l'autre.

**QA v3 (Hell_Kaiser, 31/10, 21 h 30, captures)** : (a) oui, Slot 1 et Slot 2 offrent Off / Samurai / Kala (Kala n'est pas dans le sélecteur vanilla : voulu, route 1 = premier fichier seul) ; (b) les deux cochés se superposent bien. **Défaut vu, le même qu'au 31/10 midi** : tatouage **coupé en escalier** sur les fesses, manquant aux épaules, et sur la jambe droite une **ligne de coupure identique pour Kala et pour Samurai** (dessin présent derrière, absent devant) : la limite ne suit pas le dessin mais la géométrie. Son hypothèse : la coque passe sous la peau là où le corps est déformé par son preset **Lethal Curves**.

**Mesure (31/10, 21 h 40, lecture seule)** : Lethal Curves (`004_Rig_Lethal_Curves_Angel_TPP_RR_Vanilla_AXL`, 23462) est un **rig de déformation** (remplace `player_woman_base_deformations.rig` et patche `tpp_meshentity.ent` dans `player_wa.ent`) : il met à l'échelle des os, et tout maillage skinné à ces os suit. Or la coque et le corps n'ont pas la même densité : corps Angel `t0_000_pwa_base__full.mesh` = **8 chunks, 91 360 sommets** ; coque Angel `tx_000_pwa_base__full_tattoo_01.mesh` = **1 chunk, 12 589 sommets** (vanilla : 3 296, 83 os) ; mêmes 167 os. Une coque sept fois moins dense ne suit pas une déformation d'os comme le corps dense : le corps ressort à travers elle, et la limite suit ses grands triangles (l'« escalier »). XS Sporty Sexy Map (`001_Skin_…`) ne contient aucun maillage : hors de cause. High Res Tattoos : textures seulement. **Test qui tranche, à lui** : retirer les deux fichiers `004_Rig_Lethal_Curves…` (jeu fermé), même sauvegarde : si l'escalier des fesses disparaît, c'est bien la coque face au rig. Un tatouage **vanilla** du sélecteur vanilla doit montrer la même coupure (même coque Angel).

**~~Hypothèse Lethal Curves~~ TUÉE par Hell_Kaiser le 31/10 (22 h)** : sans le rig, effet identique ; les morceaux de tatouage au bord de la coupure **bougent avec l'animation** (z-fighting : coque et peau se disputent la même profondeur). L'archive d'origine `002_Tattoos_VTK_Samurai` s'affiche, elle, **entière et stable** (dos, fesses, épaules, jambes : captures). **Mesure (22 h)** : le corps Angel `t0_000_pwa_base__full.mesh` cite `base\v_textures\body\v_overlay.xbm` dans ses **24 matériaux** de peau : un tatouage VTK n'est **pas une coque**, c'est un **calque du matériau de la peau du corps lui-même**. Il suit donc le corps au sommet près, par construction. Notre canari affiche la même texture par une **coque décal** séparée (`tx_000_pwa_base__full_tattoo_01`, 12 589 sommets contre 91 360) : partout où sa géométrie ne coïncide pas avec la peau déformée, elle passe dessous. **Acquis corrigé (§ 4 bis)** : « une archive de tatouage est une texture seule » reste vrai, mais VTK l'affiche dans la peau, pas par une coque ; d'où **un seul tatouage VTK à la fois** (un seul `v_overlay.xbm`), ce qu'Ink Flow veut dépasser.

**Piste de correction (à chiffrer, non commencée)** : construire la coque **depuis le corps actif lui-même** (`t0_000_pwa_base__full.mesh` du joueur, 8 chunks, mêmes poids) en remplaçant ses matériaux par le matériau décal des coques ; coque = corps à l'identique, donc aucune déformation ne les sépare. Prix : 91 k sommets rendus par slot actif au lieu de 12,6 k ; à mesurer en jeu (canari v5). Cohérent avec l'acquis § 4 bis : le builder prend ce que le joueur a déjà.

**Demandes de Hell_Kaiser pour le générateur (31/10)** : (1) **nombre de slots custom choisi par le joueur** ; en jeu, un réglage Mod Settings ne peut pas changer les options du créateur (fusionnées par ArchiveXL au chargement) : forme réaliste = réglage du **builder**, qui régénère l'archive avec N slots ; une bascule en jeu demanderait une étude à part (masquer des switchers par script, non exploré). (2) **slots custom juste sous le sélecteur vanilla**, pas en bas : indices vanilla `body_tattoo` = 1040, `fpp_body_tattoo` = 1050, `body_scars` = 1060 ; nos 3350 tombent en bas. **v4 = v3 avec `--slot-index 1041`** (1041-1049 libres) : si les slots remontent sous « Body Tattoos », l'ordre à l'écran suit l'index (et non la position dans la liste fusionnée) ; sinon il faudra une autre voie.

**Après** : le générateur (fichiers réels du joueur, table `fichier → slug` stable, N slots), puis la mesure UV des coques Solo pour le corps UV.

## 8. Devis des deux pistes (2026-11-01, Fable, lecture seule : aucune ligne de code)

**Mesures de la séance** (fichiers extraits dans `C:\__DEV\cyberpunk\ink_flow\x\van2\` depuis `basegame_4_appearance`, et `x\angel\` depuis `006_Angel_Body.archive`) :
- Le matériau de peau du corps (`female_<teint>.mi`, 12 teints, même base pour vanilla et Angel) a **un** paramètre de calque : `SecondaryAlbedo` = `base\v_textures\body\v_overlay.xbm`, `SecondaryAlbedoInfluence` 1. C'est l'emplacement unique que VTK remplace.
- Le corps vanilla est déclaré **exactement comme la coque** : `entMorphTargetSkinnedMeshComponent`, `morphResource` = `t0_000_pwa_base__full.morphtarget` (cibles `breast_small` / `breast_big`), `chunkMask` plein, `castShadows Never` dans `appearances\entity\`. Une coque copiée du corps s'écrit donc avec le gabarit `.app` du canari actuel, seul le chemin change.
- **Angel livre son corps et son morphtarget** sous les chemins vanilla (`006_Angel_Body.archive`, 129 entrées) : le builder trouve tout chez le joueur, rien à redistribuer (acquis § 4 bis confirmé).
- Densités : vanilla corps **4 641** sommets, coque vanilla 3 296 (rapport 0,7) ; Angel corps **91 360**, coque Angel 12 589 (rapport 0,14). La coque d'Angel est un maillage à part, pas une copie du corps : c'est l'écart géométrique qui la fait passer sous la peau, pas la densité seule.
- Décal : `customization_tattoos_<teint>.mi` = `base\materials\mesh_decal.mt` + `DiffuseAlpha` 0,6, rien d'autre (`.mt` absent des listes, non lu).
- Tailles : corps Angel **4,2 Mo** (mesh) + **2,7 Mo** (morphtarget) ; coque Angel 0,75 + 0,45 Mo ; texture Samurai 6,9 Mo, Kala 0,23 Mo ; canari v4 posé 10,9 Mo. Pillow 12.3 et numpy présents dans son Python.

### Piste A — coque copiée du corps actif (canari v5)

**Principe** : par fichier de tatouage, copier le `t0_000_pwa_base__full.mesh` + `.morphtarget` du joueur (Angel ici, vanilla sinon), remplacer ses 12 matériaux de peau par le matériau décal (`baseMaterial` = `customization_tattoos_01_ca_pale.mi`, `DiffuseTexture` = la texture, `DiffuseAlpha` 1,0), garder les 8 chunks et les 12 appearances (toutes vers ce matériau), repointer le `baseMesh` du morphtarget vers la copie. `.app`, `.inkcharcustomization`, localisation et `.xl` de la v4 inchangés. Coque = corps à l'identique (mêmes sommets, poids, cibles `breast`, `garmentSupport`) : aucune déformation ne les sépare, **y compris sous les vêtements** (le `garmentSupport` du corps suit).
**Ce que ça ferme en prime** : le risque § 5.1 (coques à la mise à plat UV) disparaît par construction : la copie d'un corps UV garde les UV du corps UV, celle d'Angel les UV vanilla/VTK ; et § 5.4 (bras UV sur Angel) suit la même recette par cible (copie du maillage des bras).
**Travail** : `build_canari.py` : une fonction `body_shell()` à côté de `retexture_mesh()` (≈ 60 lignes : matériaux remplacés au lieu de retexturés, appearances réécrites), option `--shell body|angel_tattoo`, gabarit morphtarget = celui du corps. **Une séance courte, Opus** (outillage), build, pose par formule, QA à lui.
**Prix** : archive + **6,9 Mo par fichier** de tatouage (mesh + morphtarget, hors texture) tant qu'un mesh porte la texture ; réductible plus tard par ArchiveXL dynamic materials (§ 5.3). Rendu : **91 k sommets par slot actif** au lieu de 12,6 k, soit un second corps Angel par slot ; négligeable face à une scène de Night City, à confirmer à l'œil et au compteur fps.
**Risques** : (1) **z-fighting entre deux surfaces identiques** : c'est le cas que `mesh_decal.mt` est fait pour rendre (biais de profondeur ; les tatouages et cicatrices vanilla sont déjà des décals collés au corps) ; si le canari scintille malgré tout, gonflement de la copie le long des normales (lecture du tampon de sommets quantifié : une séance de plus). (2) **Masques de chunks** : les vêtements cachent des morceaux du corps par étiquettes appliquées au composant **par son nom** (`t0_000_pwa_base__full` dans le `.xl` d'Angel) ; notre composant a un autre nom : un tatouage peut rester visible à travers un haut. Même risque que le canari actuel, jamais testé habillé (le créateur est nu) ; à mesurer au premier miroir ou Ripperdoc ; remède connu si besoin : `overrides.tags` ArchiveXL sur nos noms. (3) `castShadows Never` à garder, sinon double ombre. (4) FPP : autre maillage (`l0_000_fpp__full`), même recette plus tard (`--fpp`), hors v5.

### Piste B — peindre dans la peau, comme VTK (fusion à la construction)

**Principe** : le builder exporte chaque texture choisie en PNG (CLI `export --uext png`), les compose dans l'ordre (alpha « over », mise à l'échelle au plus grand format : Kala 2048² → 8192²), réimporte le résultat à la place de `v_overlay.xbm` (CLI `import --keep` sur une copie de l'original : format BC7 et mips conservés). Ink Flow devient **l'unique archive VTK** du joueur ; rien dans le créateur (ni `.inkcharcustomization`, ni `.app`, ni coque). Famille UV : même geste sur sa texture de calque (table § 2), composée à part.
**Travail** : script `bake_overlay.py` (≈ 120 lignes, Pillow), **une séance courte, Opus**. Rendu = VTK par construction, aucun risque de géométrie.
**Prix** : une texture 8192² BC7 ≈ 7 Mo quel que soit le nombre de tatouages ; composition ≈ 270 Mo de mémoire par calque 8K (secondes) ; **compression BC7 d'un 8K à l'import : minutes possibles**, à chronométrer.
**Limites** : le choix se fait dans le builder, **pas en jeu** (changer = reconstruire + relancer) ; un seul rendu à la fois ; les deux familles ne se mélangent pas sur une même surface ; conflit avec toute autre archive VTK (à retirer, § 5.6 déjà). Perd la raison d'être annoncée du mod : le sélecteur dans le créateur.

### Recommandation

**A d'abord** : seule piste qui garde le créateur, et elle ferme § 5.1 gratuitement. **B en réserve** comme mode « fusion » du builder (qualité VTK sans créateur, ou corps sans coque possible) : peu cher, compatible avec A, à faire après si A tient. **Test gratuit avant tout, dans le créateur avec Angel** : choisir un tatouage **vanilla** (sélecteur « Body Tattoos », options 1 à 5) : s'il montre le même escalier, la coque livrée par Angel est en cause pour tout le monde, et A est la seule issue côté coques.

**Questions de Hell_Kaiser au devis (2026-11-01)** et réponses :
- « VTK sépare nativement les bras du corps, pourquoi pas pareil ? » : VTK ne sépare rien, ce sont deux **maillages** (corps, bras) avec chacun **son** matériau de peau et donc **son** unique `SecondaryAlbedo`. Le nombre d'emplacements natifs = le nombre de maillages de peau, et chacun n'en a qu'un : le shader `skin.mt` fixe ses paramètres, on ne peut pas lui ajouter un « TertiaryAlbedo ». D'où les coques, qui sont la voie du jeu lui-même (tatouages et cicatrices vanilla).
- « Le builder pourrait-il produire plusieurs fusions, chacune une option du créateur ? » : en théorie oui, par une **appearance du corps par combinaison et par teint** (12 × N) et une option du créateur qui change l'appearance du corps ; non exploré, en conflit avec l'option « skin color » qui pilote déjà cette appearance, et toujours **une seule combinaison à la fois** (un sélecteur à N options pré-cuites, pas N slots). A donne de vrais slots.
- **GO de Hell_Kaiser pour A (2026-11-01)** : « vas-y fais A déjà et je vois ce que ça donne ».

### Canari v5 construit (2026-11-01)

`tools\build_canari.py --files samurai,kala --slots 2 --slot-index 1041 --shell body --tag v5` → `canari\v5\` (archive **22,2 Mo**, 16 fichiers, même `.xl`). Par fichier : `<slug>_pwa.mesh` = copie du corps Angel (8 chunks, 91 360 sommets, 167 os, 12 appearances intactes) dont les 12 matériaux sont devenus `customization_tattoos_01_ca_pale.mi` + `DiffuseTexture` = la texture + `DiffuseAlpha` 1,0 ; `<slug>_pwa.morphtarget` = morphtarget du corps Angel (cible `breast_big`, appearance `01_ca_pale`) repointé sur la copie ; composants des `.app` : `castShadows` et `castLocalShadows` = `Never`. **Vérifié après dépaquetage** : `.inkcharcustomization`, localisation, `.xl`, textures et coque FPP identiques à l'octet à la v4 ; texture Samurai = source (SHA-256) ; morphtarget 2 701 532 octets contre 2 701 582 à l'original (le chemin seul change).

~~**QA v5 à faire en jeu**~~ **QA v5 (Hell_Kaiser, 2026-11-01, 0 h 30, capture) : la piste A tient.** Posée dans le jeu à 0 h 20 (formule, SHA-256 identiques). Slot 1 = Samurai : tatouage **entier et collé à la peau** (dos, fesses, jambes, épaules : toutes les zones qui cassaient en v4), **aucun scintillement** vu, les deux sélecteurs marchent et se superposent toujours. Les points (a), (b), (c) sont vus ; (d) poitrine et (e) coût fps non mesurés (sans enjeu à l'œil). **Acquis** : une coque copie du corps actif en matériau décal s'affiche comme un calque VTK ; `mesh_decal.mt` rend bien deux surfaces identiques sans z-fighting. Reste ouvert, inchangé : FPP (miroir / Ripperdoc), vêtements (masques de chunks par nom de composant), corps UV. **Détail d'interface vu sur la capture** : « Ink Flow - Slot 1 » et sa valeur « Samurai (Ink Flow) » se chevauchent : dans les slots propres, le générateur nommera les options par le nom du fichier seul, sans suffixe (le suffixe reste utile dans le sélecteur vanilla).

## 9. Générateur v0 (2026-11-01, Fable, « Go maintenant » de Hell_Kaiser)

`tools\inkflow_build.py` + `tools\rdar.py` + `templates\` (trois gabarits JSON copiés : `chest_tattoo.app.json` et `your_tattoo_pwa.inkcharcustomization.json` du toolkit 20279, `localization.json.json` de Kylin). `build_canari.py` reste figé (canaris v1-v5). Travail dans `C:\__DEV\cyberpunk\ink_flow\gen\` (`body`, `tex`, `pack`, `out`, `verify`), entrée de test `C:\__DEV\cyberpunk\ink_flow\in\` (les 14 archives VTK d'Angel tirées de `3_Bodies\V's Body.zip`).

**Ce qu'il fait** (en-tête du script) : lit l'index de chaque `.archive` du dossier d'entrée sans WolvenKit (`rdar.py` : en-tête RDAR + table des empreintes FNV-1a 64), reconnaît la famille par le fichier remplacé (table `FAMILIES`, § 2 : VTK corps / bras G-D / tête, UV corps, masques de rugosité) ; **v0 = VTK corps seulement**, le reste est listé « ignoré » ; trouve le corps actif (première archive de `archive\pc\mod` dans l'ordre alphabétique qui livre `t0_000_pwa_base__full.mesh`, sinon `basegame_4_appearance`), l'extrait et le sérialise (CLI, en cache sur taille + date) ; extrait `v_overlay.xbm` de chaque archive (CLI, en cache) ; construit par tatouage la coque copie du corps (recette v5, matériau décal en constante), le morphtarget, un `.app` par slot et un pour le sélecteur vanilla ; écrit l'`.inkcharcustomization` (switcher `None` lié à `body_tattoo` à N options + N sélecteurs propres à partir de `--slot-index` 1041), la localisation, le `.xl` ; un seul appel `convert deserialize` sur le dossier, `pack`, liste ; signale les archives d'origine encore dans le jeu (à retirer) et le canari (mêmes noms d'options). Options : `--in --game --slots --slot-index --alpha --out --work --name --no-route1 --list`.

**Mesures** : `rdar.py` validé contre le CLI sur les 14 archives (contenus identiques) ; **0,4 s** pour sonder les **625** archives de `archive\pc\mod` contre 3 à 4 s par appel CLI (démarrage .NET) ; corps actif = `006_Angel_Body.archive`, devant `011_UV_Framework_Texture_3.2.1.archive` qui livre aussi mesh + morphtarget du corps sous les chemins vanilla ; bras `a0_000_pwa_base_hq__l/r.mesh` **absents** de `archive\pc\mod` sous ce chemin (les bras Songbird vivent ailleurs : à mesurer avant la famille bras). Familles trouvées : **8 archives VTK corps** (Bedellia Unrelated, BuryFlowers Promiscuity Body et Body No Juice, Cover Me In Gold, Garden Bloom, Japanese Slut No Cum, Kala Japanese Arm Body, Samurai) et 6 bras/tête seuls (BuryFlowers bras ×2, Kala tête + bras ×2, Thorny Rose = bras droit) ; Cover Me In Gold livre aussi `v_body_rm.xbm` et les masques de rugosité des bras (peau, pas tatouage) ; Garden Bloom et Kala ont une partie tête (`h0_001_pwa_c__basehead_overlay.xbm`), ignorée en v0.

**Build** : **95 s** à froid (2 appels CLI pour le corps, 8 `unbundle`, 1 `deserialize` de 42 JSON en 50 s, `pack`, liste), 60 s en cache ; `out\Ink_Flow.archive` **71,2 Mo, 50 fichiers** (par tatouage : texture + mesh 4,2 Mo + morphtarget 2,7 Mo + 3 `.app` ; + inkcc + localisation) + `Ink_Flow.archive.xl` (même contenu que celui du canari). **Vérifié après dépaquetage** : switchers `None`→`body_tattoo` (8 options, index 0-7), `inkflow_slot1` (1041) et `inkflow_slot2` (1042) à 9 options (Off + 8) ; 26 infos ; groupes `FPP_Body` / `TPP_Body` / `character_creation` à 28 noms ; 18 libellés ; coque = 8 chunks, 91 360 sommets, 12 matériaux → décal (`DiffuseTexture` = la texture du slug, `DiffuseAlpha` 1,0) ; morphtarget `breast_big` → la coque ; `.app` → le morphtarget, ombres `Never` ; **8 textures identiques aux sources (SHA-256)**. Archive : SHA-256 `ede6d2e2…525eb`.

**Choix (à confirmer par lui en jeu)** : nom affiché = nom du fichier sans préfixe `NNN_Tattoos_VTK_` ni extension, `_` → espace (« Samurai », « BuryFlowers Promiscuity Body No Juice ») ; dans les slots propres le nom seul, dans le sélecteur vanilla « Nom (Ink Flow) » ; slug = même radical en minuscules (`samurai`, `garden_bloom`), 40 caractères au plus, table `inkflow_slugs.json` **dans le dossier d'entrée**, écrite une fois et jamais modifiée (le slug du Samurai est celui du canari : le personnage sauvegardé garde son choix) ; route 1 pour **tous** les fichiers ; pas de coque FPP (point ouvert inchangé) ; corps actif = celui du joueur.

**Question de Hell_Kaiser (tatouages du visage)** : la tête est une **surface à part** (maillage de `007_VTK_Vanilla_HD_Head`, calque `h0_001_pwa_c__basehead_overlay.xbm`, § 2 bis) : même recette qu'au corps, **par cible** (copie du maillage de tête actif en décal), non faite en v0 ; une archive « full » comme Garden Bloom ne donne pour l'instant que sa partie corps.

**QA v0 (à lui, après pose à la place du canari)** : (a) « Body Tattoos » : 8 options « … (Ink Flow) » à la suite des vanilla ; (b) « Ink Flow - Slot 1 / 2 » juste sous « Body Tattoos », Off + 8 noms sans suffixe, lisibles (chevauchement disparu ?) ; (c) chaque tatouage entier et collé à la peau, comme le v5 ; (d) deux slots cochés = superposition propre ; (e) noms acceptables ou règle à changer ; (f) fluidité du créateur avec 8 coques disponibles (une active par slot) ; (g) sauvegarde faite sous le v5 : Slot 1 = Samurai retrouvé (même nom d'option).

**QA v0 (Hell_Kaiser, 2026-11-01, 1 h 20, capture) : le proto tient.** Posé à 1 h 14 à la place du canari. Slots 1 et 2 : les 8 tatouages présents, **aucune coupure** ; superposition OK. **Défaut vu une fois** : bras gauche plus clair que le corps avec une couture à l'épaule (même symptôme qu'au canari v1, mais un seul bras, et **sans aucune coque FPP** cette fois) ; retour au menu principal (passage en Borderless) puis rechargement du créateur : **disparu**. Donc intermittent, lié au chargement, pas à une coque FPP : l'hypothèse de la v1 (coque FPP = couture) perd son seul indice ; piste = le seamfix d'Angel (`femv_seamfix.app`, matériaux `armsMAT`/`neckMAT`) ou le teint des bras qui s'applique après nos `.app`. À surveiller à chaque QA ; non bloquant. Points (e) noms, (f) fluidité, (g) sauvegarde v5 : non rapportés. **Demande suivante : les bras.**

**Reste après la QA** : familles bras / tête / UV par cible (mesurer d'abord où vivent les bras Songbird et la tête HD dans `archive\pc\mod`), icônes, exe + interface (modèle Lethal Curves), FPP, vêtements (masques), poids (6,9 Mo par tatouage : dynamic materials § 5.3).

## 10. Mesure des bras et devis (2026-11-01, 1 h 40, Fable, lecture seule)

**Correction de § 2 bis** : dans le jeu tel qu'installé ce soir, **aucune archive Songbird** (`005_Songbird_Arms_UV` absente de `archive\pc\mod`, 625 archives sondées) : les bras actifs sont les **bras VTK d'Angel**. `006_Angel_Body` livre `arms_hq\a0_000_pwa_base_hq__l/r.mesh` (TPP) et `fpp\a0_000_pwa_fpp__full_l/r.mesh` (FPP), devant `011_UV_Framework_Texture_3.2.1` qui livre aussi ces chemins (et le corps, et la tête). Conséquences : les archives VTK de bras du joueur (Samurai bras, Kala bras G/D, BuryFlowers bras G/D, Thorny Rose) **ont une surface** sur ce montage ; la famille UV (`fullbody_overlay_d01.xbm`, livré par 011) n'en a **aucune** (corps et bras VTK) ; la tête = `h0_000_pwa_c__basehead.mesh` de `006_VTK_Vanilla_HD_Head_xBaebsae`, calque `h0_001_pwa_c__basehead_overlay.xbm` de `006_VTK_Vanilla_HD_Head_Textures` (`007_VTK_Vanilla_HD_Head` = textures seules, aucun maillage). Le hook d'écriture a refusé `unbundle` depuis l'archive du jeu (lecture prise pour une écriture : cas 203 du registre) ; mesure faite sur `C:\__DEV\cyberpunk\ink_flow\src\006_Angel_Body.archive`, **index identique** à celui du jeu (186 703 872 o).

**Maillages lus** (`gen\arms\`) :

| Cible | Maillage | Chunks / sommets | Matériaux locaux | Apparences | Peau (`baseMaterial`, `SecondaryAlbedo`) |
|---|---|---|---|---|---|
| bras G TPP | `arms_hq\a0_000_pwa_base_hq__l.mesh` | 4 / 31 950 | 15 | 22 | `female_arm_<teint>.mi`, `femme_arm_left_01_overlay` |
| bras D TPP | `arms_hq\a0_000_pwa_base_hq__r.mesh` | 3 / 30 616 | 15 | 22 | idem, `right` |
| bras G FPP | `fpp\a0_000_pwa_fpp__full_l.mesh` | 4 / 31 952 | 15 | 14 | idem |
| bras D FPP | `fpp\a0_000_pwa_fpp__full_r.mesh` | 3 / 30 616 | 14 | 14 | idem (entrées `<teint>_body`) |
| torse FPP | `fpp\t0_000_pwa_fpp__torso.mesh` | 8 / 91 360 | 12 | 12 | `female_<teint>.mi`, `v_overlay` (= le corps TPP) |
| seamfix | `base\vtk\femv_seamfix.mesh` (+ `_fpp`) | 4 / 5 156 (4 733) | 48 (`armleft_`/`armright_`/… × teints) | 12 | `female_arm_*.mi` |

Tous à matériaux **locaux**, même structure que le corps : la recette v5 (copie + décal) s'applique telle quelle. Les bras n'ont **pas de morphtarget** : composant `entGarmentSkinnedMeshComponent` + `.mesh` (gabarit toolkit `arm_tattoo.app`, apparences `w__arm_tattoo_left` / `w__arm_tattoo_right`, dans `dl\20279`). Le `.app` FPP d'Angel (`l0_000_fpp__full.app`, 12 apparences par teint) déclare le torse FPP en `entGarmentSkinnedMeshComponent` aussi, et un composant vide `Body:ANGEL` (étiquette).

**Devis bras (piste A par cible)** : par fichier de tatouage et par texture de bras trouvée (gauche, droite, ou les deux) : copie du maillage de bras actif TPP en décal (texture du côté, `DiffuseAlpha` 1,0), un `.app` par (slot, fichier, côté), composant `inkflow_slot<n>_<slug>_arm_l/r` ; l'option du slot active **corps + bras G + bras D** du fichier (plusieurs `names` par option, patron vanilla). Prix : + 1,0 à 1,2 Mo par bras et par fichier (Samurai : 3 cibles ≈ 9,2 Mo). Travail : table `FAMILIES` → cible (maillage actif, gabarit, côté), extraction et cache par cible, boucle de construction par cible, options multi-`names` ; ≈ 120 lignes dans `inkflow_build.py`, **une séance courte**, QA à lui. **À mesurer en jeu, pas lisible** : (1) **FPP** : les bras sont ce qu'on voit en première personne ; recette = mêmes copies sur `fpp\a0_000_pwa_fpp__full_l/r` déclarées par le groupe `FPP_Body` (uiSlot `fpp_body_tattoo` ?) ; sans miroir ni Ripperdoc sur sa sauvegarde, il faut une sauvegarde plus avancée ou le mode photo ; (2) **couture** : le seamfix d'Angel (patch de peau épaules-cou) se dessine par-dessus le bras : un tatouage qui traverse l'épaule pourrait avoir un trou de la largeur du patch ; remède connu = copier aussi le seamfix en décal dans la cible bras ; (3) **tête** : même recette, mais le maillage de tête mêle peau et autres matériaux (yeux, bouche, cils…) : masquer les chunks non-peau (`chunkMask`) ; chantier à part, après les bras.

**Noms des options (demande de Hell_Kaiser, 1 h 35)** : le joueur nomme chaque option dans le builder, avec une limite de caractères (mesure : « Ink Flow - Slot 1 » + « Kala Japanese Arm Body », 22 caractères, se chevauchent dans le créateur ; la limite exacte se mesurera avec un titre court). Forme retenue : `inkflow_slugs.json` devient un **catalogue** `{fichier: {slug, name}}` (nom modifiable par le joueur, slug jamais), `--max-name` (défaut 20 : avertit et coupe), `--slot-title` (défaut « Ink {n} »). Implémenté dans le générateur le 01/11 à 1 h 45, **non rebâti ni posé** (le build en jeu reste celui de 1 h 04).

### v0.1 construite, vérifiée et posée (2026-11-01, 1 h 50, GO « Go bras maintenant »)

`inkflow_build.py` réécrit **par cible** (table `TARGETS` : corps, bras gauche, bras droit ; chaque cible = texture remplacée, maillage actif, gabarit `.app`, type de composant, suffixe) : une archive de tatouage donne une option qui active **une info par cible** sur **un uiSlot par cible** (`inkflow_slot<n>`, `_arm_l`, `_arm_r` ; patron Heterochromia) ; une cible absente du tatouage reçoit l'info « off » de ce uiSlot (changer de tatouage ne laisse jamais un bras de l'ancien). Bras : copie de `arms_hq\a0_000_pwa_base_hq__l/r.mesh` d'Angel (15 matériaux → décal), composant `entGarmentSkinnedMeshComponent` (gabarit toolkit `arm_tattoo.app`, copié dans `templates\`). Route 1 (sélecteur vanilla) : corps seulement. Catalogue : `{fichier: {slug, name, id}}`, **`id` = SHA-256 du fichier** (le champ SHA-1 des entrées d'index est vide dans les archives WolvenKit : `da39a3ee…`) : un fichier renommé garde son slug (Hell_Kaiser renomme ses archives avec l'auteur : `002_Tattoos_VTK_Unknown_Samurai`, `…_Shivakoko_Cover_Me_In_Gold`, `…_KamZZLPC_Thorny_Rose`). Cache des textures clé = archive + liste des cibles (le cache v0 ne contenait que `v_overlay`). `--slot-title` « Ink {n} », `--max-name` 20 (coupe + avertissement, doublons signalés : les deux « BuryFlowers Promiscu… » sont à renommer dans le catalogue).

**Build** sur les 14 archives de test : **13 tatouages** (8 corps, dont Samurai et Cover Me In Gold avec leurs deux bras ; 5 bras seuls : BuryFlowers G/D, Kala G/D, Thorny Rose D), 1 ignorée (Kala tête). 94 s à froid (3 maillages, 13 unbundle, 69 JSON désérialisés en 50 s), 56 s en cache. **`Ink_Flow.archive` 89,6 Mo, 86 fichiers** ; SHA-256 `414851a5a9955bdb…`. **Vérifié dépaqueté** : switchers `None`→`body_tattoo` (8 options), `inkflow_slot1/2` (index 1041/1042, 3 uiSlots chacun, Off + 13 options, chaque option = 3 noms info-ou-off) ; 48 infos, 42 `.app` tous présents, 8 morphtargets, aucun renvoi cassé ; groupes à 50 noms ; 28 libellés (« Ink 1 », « Ink 2 ») ; bras Samurai = 31 950 sommets, 15 matériaux décal ; **17 textures identiques aux sources**. **Posée dans le jeu à 1 h 50** (`WRITE_UNLOCK`, jeu fermé, SHA-256 identiques) ; la v0 (71,2 Mo) gardée dans `C:\__DEV\cyberpunk\ink_flow\builds\v0\`.

**QA v0.1 (à lui)** : (a) « Ink 1 / Ink 2 » lisibles, 13 options + Off ; (b) Samurai ou Cover Me In Gold : corps **et** bras tatoués, continuité à l'épaule (couture du seamfix ?) ; (c) un bras seul (Thorny Rose, Kala Left) : rien sur le corps, le bras tatoué du bon côté ; (d) passer de Samurai à Bedellia : les bras s'éteignent ; (e) Slot 1 = Samurai + Slot 2 = Thorny Rose : superposition sur le bras droit ; (f) le bras gauche plus clair revient-il ; (g) FPP dès qu'une sauvegarde le permet.

**QA v0.1 (Hell_Kaiser, 2026-11-01, 2 h 05) : validée.** Les tatouages de bras s'affichent, **mappage correct** ; Samurai affiche **corps et bras ensemble, proprement** (une option = trois infos sur trois uiSlots : la forme tient) ; les deux slots se superposent toujours bien ; **pas de bras plus clair** revu. Point levé : « Unrelated n'affiche que le corps » = l'archive VTK ne porte que le corps (l'auteur livre corps, bras G et bras D en trois fichiers VTK, un pack entier en UV : page Nexus vérifiée par lui) ; il a téléchargé les deux bras (`002_Tattoos_VTK_Bedellia_Unrelated_Arm_Left/Right`) et les a rangés dans `V's Body.zip`. Même chose pour Thorny Rose : son archive = bras droit seul. Titres « Ink 1 / Ink 2 » et limite 20 : pas de retour négatif. Renommages faits par lui dans `V's Body.zip` pendant la séance : VTK et UV préfixés de l'auteur (ou `Unknown_`), **deux archives VTK de plus** dans Angel.

## 11. v0.2 : jeu de test rechargé, noms courts, archives sans table de noms (2026-11-01, 2 h 10 → 2 h 20, Fable, « Reprends »)

**Entrée** : `C:\__DEV\cyberpunk\ink_flow\in\` vidé et rechargé depuis `3_Bodies\V's Body.zip` (dossier `Angel\archive\pc\mod\002_Tattoos_VTK_*.archive`, dates d'origine conservées) : **17 archives**, 16 tatouages construits, 1 ignorée (Kala Japanese tête). Par rapport au jeu de la v0.1 : Thorny Rose et Promiscuity Body No Juice retirées par lui, **+ Unrelated bras G/D, + Kala Vale corps et bras G, + Japanese Slut (ex-`_X`, sans extension avant donc jamais lue)** ; 5 archives renommées avec l'auteur, **toutes retrouvées par SHA-256** (slugs `bedellia_unrelated`, `japanese_slut_no_cum`, `cover_me_in_gold`, `garden_bloom`, `samurai` conservés : les personnages sauvegardés gardent leur choix). Les entrées sans fichier (Thorny Rose, No Juice) restent dans le catalogue, slug réservé. Les UV de `X_Common` ne sont pas prises : aucune surface sur ce montage (§ 10).

**Noms (champ `name` du catalogue, ≤ 20 caractères, sans auteur : l'auteur est dans le nom de fichier, le créateur n'a pas la place)** : Unrelated Body / Arm L / Arm R, Japanese Slut, Japanese Slut Alt (ex-No Cum), Promiscuity Body / Arm L / Arm R, Kala Japanese Body / Arm L / Arm R (/ Head, ignorée), Kala Vale Body / Arm L, Cover Me In Gold, Garden Bloom, Samurai. Choix de Fable, modifiables par lui dans `in\inkflow_slugs.json` (rebâtir ensuite).

**Panne trouvée et corrigée (générateur v0.2)** : sur `Kala_Vale_Arm_Left` et `Kala_Vale_Body` (archives de mars 2023), le CLI WolvenKit extrait l'entrée mais **ne résout pas son chemin** et la nomme `<empreinte>.bin` (`3786553998184708553.bin` = FNV-1a 64 de `femme_arm_left_01_overlay.xbm`, mesuré ; contenu CR2W) ; le filtre `-r` sur le chemin ne retenait donc rien et le build s'arrêtait sur « texture absente ». Les archives Kala Japanese (janvier 2023, même chemin, `debugSize` 0 aussi) sont résolues : la différence tient à l'outil d'empaquetage d'origine, non lue plus loin. Correctif : `TEX_REGEX` accepte `\d+\.bin`, et `extract_textures` remet chaque `.bin` dont l'empreinte est connue (`HASH_PATH`) à son chemin (journal « chemin retabli depuis l'empreinte »). Le cache des textures est invalidé (la clé porte la regex) : toutes les archives réextraites.

**Build** : 113 s (17 unbundle, 80 JSON désérialisés en 61 s, pack 3 s) ; **`Ink_Flow.archive` 105,5 Mo, 100 fichiers** : 1 inkcc, 1 localisation, 49 `.app` (9 route 1 + 2 slots × 20 cibles), 20 maillages, 9 morphtargets, 20 textures. SHA-256 `16cfb6beee7841c0…27ed47c`. **Vérifié dépaqueté** (`gen\verify\v02`) : 100/100 entrées, **20 textures identiques aux sources extraites** (SHA-256), aucune sans source. **Posée dans le jeu à 2 h 20** (`WRITE_UNLOCK` sur `archive\pc\mod`, jeu fermé, empreintes identiques) ; la v0.1 (89,6 Mo) copiée depuis le jeu dans `C:\__DEV\cyberpunk\ink_flow\builds\v0.1\`. Aucune archive de tatouage d'origine dans le jeu à la pose (les deux `BuryFlowers_Japanese_Slut_*` vues à 2 h 09 avaient été retirées par lui).

**Limite vue à la construction, à trancher par lui** : un fichier = une option, et une option occupe un slot. Bedellia Unrelated, BuryFlowers Promiscuity et Kala Japanese livrent **corps, bras G et bras D en trois fichiers** : avec 2 slots on ne porte pas le tatouage complet (corps + un bras au plus). Deux remèdes : `--slots 3` (mécanique, trois sélecteurs) ou un champ `group` dans le catalogue (fichiers d'un même groupe fondus en **une** option à trois cibles, comme Samurai) : ≈ 30 lignes, forme préférable, à son go. Autre trou : les archives d'origine encore dans le jeu sont détectées **par nom de fichier** seulement ; renommées, elles passent (détection par empreintes d'index possible en 0,4 s, non faite).

**QA v0.2 (à lui)** : (a) « Ink 1 / Ink 2 » : Off + 16 options, noms courts lisibles, aucun doublon ; (b) **Kala Vale Body + Kala Vale Arm L** (chemins rétablis depuis l'empreinte) : tatouage entier et au bon endroit ; (c) Japanese Slut (nouvelle) sur le corps ; (d) Unrelated : corps en Ink 1 + Arm L en Ink 2 → le bras droit manque **par construction** (limite ci-dessus) ; (e) Samurai et Cover Me In Gold inchangés (corps + bras) ; (f) sauvegarde faite sous la v0.1 : Samurai retrouvé (slug conservé) ; (g) bras clair intermittent revu ?

**QA v0.2 (Hell_Kaiser, 2026-11-01, 2 h 35, capture) : validée.** Slots 1 et 2 : la logique tient ; noms courts lisibles, **sans chevauchement et avec de la marge** (« INK 1 … PROMISCUITY ARM L » : 17 caractères, place restante visible) ; une série répartie sur les deux slots (Kala Vale corps en Ink 1 + bras en Ink 2) s'affiche bien ; bras gauche clair non revu.

**Décisions de Hell_Kaiser (2 h 40)** :
1. **Nombre de slots = réglage du mod**, défaut 2 (déjà `--slots` ; le champ `group` du catalogue proposé plus haut est **abandonné**) : une série en trois fichiers se porte entière en montant le nombre de slots.
2. **Sélecteur vanilla retiré** : les noms longs y débordent encore, et une archive corps + bras n'y afficherait que le corps alors que le slot propre affiche les deux : confusant. Nos ajouts ne vivent que dans nos slots. Générateur : `--no-route1` devient le défaut, `--route1` remet l'option (code conservé) ; les libellés « … (Ink Flow) » ne sont plus écrits non plus.
3. Limite de 20 caractères : de la marge reste ; à mesurer avec un nom de 24-26 caractères avant de changer le défaut.

**v0.2b bâtie (2 h 40)** : 62 s en cache ; **105,5 Mo, 91 fichiers** (1 inkcc, 1 localisation, 40 `.app` = 2 slots × 20 cibles, 20 maillages, 9 morphtargets, 20 textures) ; SHA-256 `52833f2e3b8447c5…e3bc3f`, `.xl` inchangé. Vérifié dépaqueté : 91/91, 20 textures identiques aux sources, **0 `body_tattoo` dans l'inkcc, 0 « (Ink Flow) » dans la localisation**, 18 libellés (16 noms + 2 titres). ~~**Non posée** : déverrouillage expiré à 2 h 33, jeu fermé par lui à 2 h 36.~~ **Posée à 2 h 47** (déverrouillage re-sauvegardé par lui, jeu fermé, SHA-256 identiques). **QA v0.2b (Hell_Kaiser, 2 h 50) : validée** : plus rien d'Ink Flow dans le sélecteur vanilla, Ink 1 / Ink 2 se comportent normalement.

**Question notée (Hell_Kaiser, 2 h 45, pour plus tard)** : outil communautaire de conversion UV ↔ VTK, ou faisable en CLI ? Non cherché ; la page du wiki « converting between tattoo frameworks » (Sources) décrit une conversion manuelle.

## 12. Tête VTK : mesure, recette, v0.3 (2026-11-01, 12 h 30 → 13 h, Fable, chantier choisi par Hell_Kaiser sur « Reprends »)

**Prémisse tuée** : « maillage de tête mêlant peau et autres matériaux, chunks non-peau à masquer » (§ 10, écrit sans lecture). Mesuré sur le maillage de tête actif `h0_000_pwa_c__basehead.mesh` livré par `006_VTK_Vanilla_HD_Head_xBaebsae` (copié dans `C:\__DEV\cyberpunk\ink_flow\src\`, index identique au jeu ; extrait dans `gen\head_src\`) : **1 chunk, 27 591 sommets, 254 os, 62 matériaux locaux, tous de peau** (`female_head_<teint>.mi`, 6 teints × 5 albédos `d01..d05` + variantes `00_warm_ivory`, `00_beige`, `00_amber`, `01_honey`, `02_band`, `00_umber`, + 2 `npc_*_plastic_doll` sur `multilayered.mt`), 63 apparences à un seul `chunkMaterials`, `meshMeshParamGarmentSupport`. Chaque matériau de peau cite `SecondaryAlbedo = h0_001_pwa_c__basehead_overlay.xbm` : c'est l'emplacement VTK tête (§ 2). Yeux (`he_000_pwa_c__basehead.mesh`, morphtarget `he_000_pwa__morphs`, 21 cibles), dents, cils, bouche sont **d'autres maillages** : aucun masque de chunk à poser, la recette v5 s'applique telle quelle.

**Morphs du visage** : la tête est déformée par `h0_000_pwa__morphs.morphtarget` (**105 cibles** `h011`…`h215`, 1 507 464 diffs, `baseTexture` = normale `h0_001_pwa_c__basehead_n01.xbm` avec diffs de texture ; 16,4 Mo), piloté par les 5 `gameuiMorphInfo` du créateur (eyes 213, nose 246, mouth 247, jaw 248, ear 249) et les presets. Il **ne porte pas le radical du maillage** et vit dans le dossier parent (`player_female_average\`), dans la même archive. Patron suivi pour qu'une coque suive le visage : **Heterochromia** (lu : `heterochromia_pwa__eyes_left.app` = `entMorphTargetSkinnedMeshComponent`, `morphResource` = **sa propre copie** du morphtarget des yeux `heterochromia_pwa_split_eyes.morphtarget`, `chunkMask` 18446744073709551608). Les `.app` vanilla des tatouages faciaux (`tattoos\hx_000__tattoo_01..15.app`, switcher `facial_tattoo` index 270, infos `link = skin color`, 12 définitions `w__<teint>`, groupes de tête `TPP` / `character_customization` / `TPP_photomode`, jamais `FPP`) **n'ont pas été lus** : le hook a refusé le listing de `basegame_4_appearance.archive` (cas 204 du registre, même famille que 203 ; pas de copie possible, plusieurs Go). Le sélecteur vanilla `facial_tattoo` est dans `headCustomizationOptions` ; **nos infos tête sont écrites dans `bodyCustomizationOptions`** avec les groupes `TPP_Body` / `FPP_Body` / `character_creation`, comme les bras (une option = 4 noms sur 4 uiSlots) : **à juger en jeu**, c'est le seul point de la recette qui n'est pas lu ; si la coque de tête ne s'affiche pas ou ne suit pas les morphs, variante à bâtir = infos tête dans la section tête (groupes `TPP`, `character_customization`, `TPP_photomode`) référencées depuis nos switchers du corps.

**Générateur v0.3** (`tools\inkflow_build.py`) : cible `head` dans `TARGETS` (texture `…\h0_000_pwa_c__basehead\textures\h0_001_pwa_c__basehead_overlay.xbm`, maillage `h0_000_pwa_c__basehead.mesh`, morph `h0_000_pwa__morphs.morphtarget`, gabarit `chest_tattoo.app.json`, composant `entMorphTargetSkinnedMeshComponent`, suffixe `_head`) ; `extract_mesh` généralisé (regex à deux radicaux, sérialisation du dossier commun) ; `retarget_morph()` (copie du morphtarget, `baseMesh` seul changé : cibles, `baseTexture` et diffs de normales conservés, même géométrie) ; « VTK tête » retiré des fichiers ignorés. Analyse (`--list`) : 17 tatouages, 0 ignoré ; tête active = `006_VTK_Vanilla_HD_Head_xBaebsae.archive` (devant `011_UV_Framework_Texture_3.2.1`). Entrées à tête dans le jeu de test : **Kala Japanese Head** (tête seule, 150 Ko) et **Garden Bloom** (corps + tête, 45 Ko) ; Cover Me In Gold n'a pas de tête.

**Build** : 160 s à froid (tête : 2 appels CLI ; 17 `unbundle` de textures réextraites, la clé du cache porte la liste des cibles ; 79 JSON désérialisés en 82 s, les deux morphtargets de tête font 58 Mo de JSON chacun) ; **`Ink_Flow.archive` 127,8 Mo, 101 fichiers** (1 inkcc, 1 localisation, 44 `.app` = 2 slots × 22 cibles, 22 maillages, 11 morphtargets, 22 textures) + `.xl` inchangé ; SHA-256 `108c324e0c6df398…6517f4d1`. **Prix d'une tête** : 1,15 Mo (mesh) + **16,4 Mo (morphtarget)** + texture, par tatouage à tête ; l'archive passe de 105,5 à 127,8 Mo pour deux têtes. Réductible plus tard par un morphtarget partagé (dynamic materials § 5.3), non fait.

**Vérifié dépaqueté** (`gen\verify\v03`, script `verify_v03.py` du scratchpad) : 101/101 entrées ; **22 textures identiques aux sources** (SHA-256) ; coques de tête = 1 chunk, 27 591 sommets, 62 matériaux → `customization_tattoos_01_ca_pale.mi` + `DiffuseTexture` = la texture `_head` du slug + `DiffuseAlpha` 1,0, 63 apparences, ombres RT coupées ; morphtargets de tête → la coque, 105 cibles `h011`…`h215`, 1 507 464 diffs ; `.app` → le morphtarget, `meshAppearance 01_ca_pale`, ombres `Never`, `chunkMask` plein ; switchers `inkflow_slot1/2` (1041/1042) à **4 uiSlots** (`…`, `_arm_l`, `_arm_r`, `_head`), 18 options (Off + 17) de 4 noms chacune ; 52 infos ; groupes à 54 noms ; option Kala Japanese Head = `off, off_arm_l, off_arm_r, kala_japanese_arm_head_head` ; option Garden Bloom = `garden_bloom, off_arm_l, off_arm_r, garden_bloom_head` ; aucune ressource manquante ; 19 libellés (17 noms + « Ink 1 », « Ink 2 »), 0 `body_tattoo`, 0 « (Ink Flow) ». **Non posée** : déverrouillage de `archive\pc\mod` expiré (dernier à 2 h 44), jeu fermé ; la v0.2b en jeu (SHA `52833f2e…`) est copiée dans `C:\__DEV\cyberpunk\ink_flow\builds\v0.2b\`.

**QA v0.3 (à lui, après pose)** : (a) Ink 1 = **Kala Japanese Head** : tatouage sur le visage, placé comme l'overlay VTK d'origine (si décalé : la mise à plat de la coque n'est pas celle de la texture, impossible ici puisque c'est le même maillage) ; (b) **morphs** : changer preset de visage, nez, mâchoire, bouche, yeux, oreilles → la coque suit (aucun décollement, aucun trou) ; c'est le point qui tranche la section (corps) choisie pour les infos tête ; (c) **animation faciale** du créateur (clignement, respiration) : la coque suit (même squelette, 254 os) ; (d) yeux, dents, bouche intérieure, cils **intacts** (la coque est la peau seule) ; (e) teint : changer la couleur de peau ne change rien à la coque (un seul décal) ; (f) couture au cou : `femv_vtk_headpatch` d'xBaebsae et le seamfix d'Angel se dessinent-ils par-dessus (trou de la largeur du patch ?) ; (g) **Garden Bloom** = corps + tête ensemble, Off éteint les deux ; (h) cumul avec un tatouage facial vanilla, des cicatrices, du maquillage, un cyberware de visage ; (i) Ink 2 = Kala Japanese Head par-dessus Ink 1 = Garden Bloom : superposition propre ; (j) fluidité du créateur (une coque de 27 k sommets + 105 morphs par slot actif).

**Ouvert après la tête** : section des infos tête (corps aujourd'hui, à juger) ; poids du morphtarget par tête ; mode photo / miroir (groupe `TPP_photomode` de la tête non renseigné par nos groupes du corps : la coque de tête pourrait **manquer en mode photo** si ce groupe est le seul évalué là ; à mesurer dès une sauvegarde le permet).

## Sources

- Wiki modding : [CCXL additions](https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-creators-theory/core-mods-explained/archivexl/archivexl-character-creator-additions), [CCXL body tattoos](https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-creators-theory/core-mods-explained/archivexl/archivexl-character-creator-additions/ccxl-body-tattoos), [options .inkcc](https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-creators-theory/files-and-what-they-do/file-formats/character-creator/.inkcharactercustomization-cc-options), [overlays par framework](https://wiki.redmodding.org/cyberpunk-2077-modding/modding-guides/npcs/custom-tattoos-and-scars/converting-between-tattoo-frameworks/overlay-list), [dynamic materials](https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-creators-theory/core-mods-explained/archivexl/archivexl-dynamic-materials), [scopes](https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-creators-theory/core-mods-explained/archivexl/archivexl-resource-patching/resource-patching-scopes).
- Nexus : [CCXL Tattoo Toolkit 20279](https://www.nexusmods.com/cyberpunk2077/mods/20279), [Fun Tattoos Overhaul VTK UV CCXL 33230](https://www.nexusmods.com/cyberpunk2077/mods/33230), [Partner Name Tattoo CCXL 19574](https://www.nexusmods.com/cyberpunk2077/mods/19574), [Character Creator UI Improvements 34310](https://www.nexusmods.com/cyberpunk2077/mods/34310).
- Fichiers lus : `3_Bodies\V's Body.zip` (Heterochromia, Kylin Ponytail, UV 3.2.1, Angel, Solo 2.0, tatouages), `E:\…\Cyberpunk 2077\archive\pc\content\basegame_{1_engine,4_gamedata,4_appearance}.archive`.

## 13. Étiquettes d'édition : où le sélecteur apparaît (mesuré le 2026-11-01, 17 h)

`editTags` des `gameuiSwitcherInfo` / `gameuiAppearanceInfo`, comptés dans le `female_cco.inkcharcustomization` vanilla (`C:\__DEV\cyberpunk\ink_flow\x\van\…`) : `NewGame` seul = 356 entrées (FPP, couleurs d'ongles TPP/FPP…) ; `NewGame` + `HairDresser` + `Ripperdoc` = 415 (maquillage yeux/lèvres/joues, cicatrices `body_scars`, ongles, cheveux, Heterochromia) ; `NewGame` + `Ripperdoc` = 86 (**`body_tattoo`, `facial_tattoo`**, couleur de peau, poitrine, tétons, boutons) ; 4 implants (`launcher`, `mantis`, `monowire`, `strongarms`) les trois. Le **miroir de l'appartement est `HairDresser`** ; le charcudoc est `Ripperdoc`. Les tatouages vanilla ne sont donc pas modifiables au miroir, et nos entrées (copiées du gabarit du toolkit 20279, `NewGame` + `Ripperdoc`) non plus : constaté par Hell_Kaiser (QA 2). **Décision (Hell_Kaiser, 17 h) : nos sélecteurs portent les trois étiquettes** (`--mirror`, défaut OFF dans l'outil pour rester vanilla, ON dans son build) ; les entrées « off » aussi, sinon un slot vidé au miroir n'aurait pas d'option. Non mesuré : si un sélecteur `HairDresser` sans ses « off » casse le miroir ; si le mode photo (`TPP_photomode`) lit ces étiquettes (il ne modifie rien, il affiche).

## 14. Builder v0.4 : exe pour les utilisateurs (2026-11-01, 19 h, Fable, go de Hell_Kaiser « interface Tk, pas de git »)

**Forme** : dossier `builder\` du projet : paquet `inkflow\` (`core.py` = moteur, `env.py` = poste du joueur, `config.py`, `gui.py` = fenêtre Tk, `rdar.py`), `InkFlowBuilder.py` (entrée), `inkflow_cli.py` (même moteur en ligne de commande), `build_exe.ps1` (PyInstaller, un seul fichier), `README.md` (utilisateur, anglais), `LICENSE` (MIT, titulaire à confirmer par Hell_Kaiser). Les gabarits restent dans `templates\` (embarqués dans l'exe par `--add-data`). `tools\inkflow_build.py` v0.3 est figé, référence du moteur.

**Moteur** : refonte à l'identique de la v0.3 (`BuildError` à la place de `sys.exit`, journal par rappel, `Settings`, `Catalogue` par **empreinte de contenu** SHA-256 : un fichier renommé garde son slug et le personnage sauvé garde ses tatouages ; l'ancien `inkflow_slugs.json` à côté des archives est importé une fois). **Preuve** : les 18 archives de `in\` rebâties par `inkflow_cli.py` avec le cache `gen\` : **106/106 entrées identiques à la v0.3b posée dans le jeu, même taille (139 599 872 o)** ; 538 octets diffèrent, tous dans l'index (horodatages des entrées RDAR), aucun dans les fichiers.

**Poste du joueur (`env.py`)** : jeu trouvé par les bibliothèques Steam (`SteamPath` + `libraryfolders.vdf`), le registre GOG (`1423049311`), les chemins Epic / GOG Galaxy ; validé par `bin\x64\Cyberpunk2077.exe` + `basegame_4_appearance.archive`. ArchiveXL lu avec sa version par `version.dll` (ctypes ; jamais de C# en ligne). **WolvenKit Console 9.1.0 est dépendant du runtime : `WolvenKit.CLI.runtimeconfig.json` exige `Microsoft.NETCore.App 10.0`** ; l'outil vérifie `dotnet --list-runtimes`, ouvre la page Microsoft si absent, et lance `WolvenKit.CLI.exe --version` après le téléchargement. Téléchargement depuis la release GitHub épinglée : `WolvenKit.Console-9.1.0.zip`, **45 266 516 o, SHA-256 `7caf49cd…834f4f`** (mesuré deux fois le 01/11) ; taille et empreinte vérifiées avant dépaquetage, chemins du zip contrôlés (zip-slip) ; 141 s ici. Tout vit dans `%LOCALAPPDATA%\InkFlow\` (`config.json`, `catalogue.json`, `work\` cache, `out\`, `backup\`, `wolvenkit\`), redirigeable par `INKFLOW_HOME` (tests sans toucher au poste : `C:\__DEV\cyberpunk\ink_flow\exe\home\`).

**Piège mesuré : la détection des archives VTK restées dans le jeu.** Par empreinte d'index « livre une texture cible », `006_Angel_Body.archive` et `006_VTK_Vanilla_HD_Head_Textures.archive` sortent aussi : les mods de corps et de tête livrent eux aussi `v_overlay.xbm` / `…basehead_overlay.xbm` (129 entrées pour Angel). Les déplacer casserait le corps. Retenu : une archive est signalée si **toutes** ses entrées sont des textures de calque connues (archive « pure » de tatouage) ou si son contenu est **identique** (taille puis SHA-256) à un tatouage choisi. L'outil propose de les déplacer dans `backup\<horodatage>\` (oui / non / annuler), jamais d'office.

**Interface (Tk, `gui.py`)** : une fenêtre : Setup (dossier du jeu, Parcourir, Détecter ; quatre voyants Game / ArchiveXL / .NET 10 / WolvenKit avec le bouton d'action quand ça manque), liste des tatouages (case, fichier, cibles, nom en jeu éditable par double-clic ou F2, note « ignored : raison »), options (slots 1-9, miroir, opacité, dossier de sortie), Build / Install into game / Clear cache / Open data folder / About, barre de progression, journal. Construction dans un fil, interface vivante. Textes dans la table `T` (anglais ; une seconde langue = une seconde table). DPI aware. Mode `INKFLOW_AUTOTEST=<rapport.json>` : construit au lancement et écrit un rapport (test sans clic d'un exe figé).

**Exe** : PyInstaller 6 dans un venv `C:\__DEV\cyberpunk\ink_flow\exe\venv` (Python 3.11 du Store : fonctionne), `--onefile --windowed`, **11,4 Mo**. Capture de la fenêtre (PrintWindow par ctypes, PNG écrit à la main) : `exe\gui_main.png`, les 18 tatouages listés et cochés, quatre voyants verts, Build actif. **Exe figé testé sans clic** (mode `INKFLOW_AUTOTEST`, maison `exe\home` vide de cache, WolvenKit téléchargé par l'outil lui-même) : **18 tatouages, 139 599 872 o, 106 entrées identiques à la v0.3b, `.xl` identique, 201 s** (contre 123 s avec le cache de `gen\` : les extractions dominent).

**Limites annoncées du premier jet** : V féminine ; VTK seulement (UV listé « ignored ») ; pas d'icônes ; `--route1` absent de l'interface ; faux positifs antivirus possibles (un fichier PyInstaller) ; pas de signature de code.

## 15. Version 1.0.0 : gabarits, preuve, zip (2026-11-01, 21 h 15 → 21 h 45, Fable, go de Hell_Kaiser « tout le lot »)

**Gabarits (décision : garder + créditer).** Les trois gabarits `.app` / `.inkcharcustomization` sont des
exports WolvenKit du CCXL Tattoo Toolkit 20279 (thrasherpass), dont la description Nexus (lue par l'API
v1, `description`) dit : « a template resource for CCXL tattoo additions… template source files for your
WolvenKit project ». Les copier dans un projet est l'usage prévu ; la boîte « Permissions » de la page
n'est pas servie par l'API (et la page refuse les clients hors navigateur) : Hell_Kaiser la lit sur le
site. Le gabarit de localisation (Kylin) ne servait que de squelette (`core.py` vide ses entrées et
écrit les siennes) : remplacé par une entrée neutre `placeholder`. Les en-têtes `ArchiveFileName`
(chemins `C:\__DEV\…`) sont remplacés par le nom du gabarit. Crédit thrasherpass dans README et NEXUS.md.

**Preuve d'identité après nettoyage** : `VERSION = "1.0.0"`, `build_exe.ps1` → exe 11,4 Mo, SHA-256
`13c14eaa…bbc9b9` ; mode `INKFLOW_AUTOTEST` sur `exe\home` (cache chaud) : 18 tatouages, 106 fichiers,
139 599 872 o, 120 s ; comparaison octet à octet avec la v0.3b du jeu (scratchpad `cmp_rdar.py`, index
lu dans l'en-tête RDAR : position 139 583 488, taille 14 684) : **536 octets différents, tous dans
l'index, 0 hors index** ; `.xl` identique. Les en-têtes des JSON n'entrent donc pas dans les fichiers
produits, et le squelette de localisation neutre donne la même localisation.

**Livrable** : `exe\dist\InkFlowBuilder-1.0.0.zip` (exe + README + LICENSE, 11,7 Mo, SHA-256
`35b5bf52…40daf6`), à envoyer sur Nexus par Hell_Kaiser avec la SHA-256 de l'exe dans la description
du fichier. Non fait par moi : upload, captures, test du bouton Download (ses gestes).

## 16. Première personne (2026-11-01, 23 h → 23 h 30, Fable, décision de Hell_Kaiser « ajouter la FPP avant l'upload »)

**Pourquoi elle manquait** : coque FPP d'Angel dans le canari v1 (suspecte, non prouvée, d'une couture
de bras ; retirée en v2, § 7) ; soupçon tombé à la QA v0 (couture revue sans coque FPP, § 9) ; jamais
testable sur sa sauvegarde du début ; passée « après la 1.0 » à chaque passation.

**Mesuré avant de coder** (vanilla `female_cco.inkcharcustomization`, extraction Angel `gen\arms`) :
- Le `link` d'un switcher est une **clé partagée**, pas un nom : `body_tattoo` porte `link=body_tattoo`
  et `fpp_body_tattoo` (index 1050, caché, `uiSlots=[fpp_body_tattoo]`, tags `NewGame`) porte le même ;
  `nipples` et `fpp_nipples` partagent `nipples type` (tags `NewGame, Ripperdoc` tous deux). Les options
  du suiveur ont les mêmes index que celles du maître. 8 switchers vanilla ont `link` = leur nom, 11 rien.
- Groupes : `FPP_Body` ne liste que les entrées `fpp_*` ; `TPP_Body` et `character_creation` que les TPP.
  Le générateur 1.0.0 mettait tous nos noms dans les trois groupes.
- `fpp\t0_000_pwa_fpp__torso.mesh` (Angel) = **octet pour octet** `t0_000_pwa_base__full.mesh` (SHA-256
  `d067067d…`, 4 220 371 o) : la coque FPP du corps est la coque TPP, aucun maillage de plus.
- L'app FPP d'Angel `l0_000_fpp__full.app` affiche ce torse avec `chunkMask` **0xFFFFFFFFFFFFFFE0**
  (chunks 5-7 du corps, 42 091 sommets ; 0-4 cachés). La coque FPP reçoit le même masque, lu dans l'app
  FPP active du joueur (`fpp_torso_mask`, cache, repli sur la valeur mesurée).
- Bras FPP `fpp\a0_000_pwa_fpp__full_l/r.mesh` : 4 / 3 chunks, 31 952 / 30 616 sommets, matériaux locaux,
  apparence `01_ca_pale` ; le droit nomme ses matériaux `01_ca_pale_body` (contrôle de `shell()` élargi
  à un préfixe). Vanilla FPP : `t0_000_fpp__tattoo_01.app` = un seul maillage « full » dédié (12 589
  sommets), `entGarmentSkinnedMeshComponent`, masque plein ; non repris (c'est la piste v4 qui cassait).

**Recette (builder `core.py`, `FPP_TARGETS`, réglage `fpp`, défaut on, case « First person » de la fenêtre,
`--no-fpp` en CLI)** : par slot, un switcher suiveur `inkflow_slot<n>_fpp` (index 1066-1074, libres en
vanilla), `link` = `inkflow_slot<n>` posé aussi sur le maître, `uiSlots` `inkflow_slot<n>_fpp`,
`_fpp_arm_l`, `_fpp_arm_r`, mêmes tags que le maître, options aux mêmes index (Off + un par fichier,
`off_fpp*` quand le fichier n'a pas la cible). Par fichier : `fpp_body` = `.app` garment sur
`<slug>_pwa.mesh` avec le masque ; `fpp_arm_l/r` = copie décal du bras FPP actif (texture du bras TPP,
`<slug>_pwa_fpp_arm_l/r.mesh`). Groupes : `FPP_Body` = noms `_fpp` seuls ; TPP et création = les autres
(sans `fpp`, l'ancien comportement reste). Tête : rien (jamais vue en FPP).

**Build CLI (`exe\home`, cache chaud)** : 18 tatouages, **150,3 Mo, 157 fichiers, 129 s** (1.0.0 : 139,6 Mo,
106) : + 11 maillages de bras FPP (≈ 1 Mo chacun), + 40 `.app`. Dépaqueté (`gen\verify\fpp1`) : 4
switchers (1041, 1042 ; 1066, 1067 liés), 100 infos dont 46 FPP, `FPP_Body` 48 / 0, `TPP_Body` et
`character_creation` 56 / 0 ; `samurai_slot1_fpp.app` → `samurai_pwa.mesh` masque `…E0` ; bras FPP →
texture du bras, `customization_tattoos_01_ca_pale.mi`, alpha 1,0. Exe rebâti (§ 15 pour la méthode).

**QA en jeu (à lui, sauvegarde avec miroir)** : (a) créateur **inchangé** (pas de double décal ni de
scintillement sur les bras : prouve que `FPP_Body` n'est pas dessiné dans le créateur) ; (b) en jeu,
bras nus, regarder ses bras et vers le bas : tatouage présent, aligné avec le TPP (miroir) ; (c) aucun
bout de tatouage flottant près de la caméra (masque) ; (d) changer de slot au miroir ou au charcudoc :
la FPP suit (lien + tags) ; (e) mode photo inchangé. Si (a) rate : le groupe ne filtre pas le dessin, il
faudra un `.app` FPP dédié hors du créateur (étude à part). Si (b) rate sans rien d'autre : `link` non
suivi pour une clé custom → repli = noms FPP dans les options du maître (patron canari v1, § 7).

## 17. Retours Nexus du 02/11 : corps vanilla, EBBRB, ordre de chargement (2026-11-02, 13 h → 14 h 30, Fable, lecture seule)

**Retours lus** (15 messages sur la page Nexus, matin du 02/11) : trois utilisateurs EBBRB (Lorasyl,
Bransburk, cybercock2067) : build et install sans erreur, slots visibles dans le créateur, **rien sur le
corps** ; un .NET 10 non détecté ; un « ne marche pas en 2.3x » (attendu) ; deux demandes de V masculin ;
0xVyper : « tout dynamique, sans rebuild ».

**Mesure 1 : corps vanilla pur (aucun mod de corps).** Même code que le moteur (`find_owner` sans
`archive\pc\mod` → repli `basegame_4_appearance.archive`), script jetable `vanilla_test.py` :

| Cible | Maillage vanilla | Matériaux | `shell()` |
|---|---|---|---|
| corps | 8 chunks, 4 641 sommets | 46, `localMaterialBuffer` | OK, morph 2 cibles |
| bras G / D | 4 / 3 chunks, 5 787 / 4 934 | 23 / 22 en **`preloadLocalMaterialInstances`** | **refusé** : « non-local materials (unsupported body mod) » |
| tête | 1 chunk, 7 186 | 62 locaux | OK, morph 105 cibles |
| bras FPP G / D | 5 529 / 4 934 | 22 / 16 locaux | OK |
| app FPP | masque `…E0` | | OK |

Le README et la page Nexus annoncent « or the vanilla body » : **faux pour les bras**. Un joueur sans mod
de corps a une erreur au build dès qu'un fichier couvre un bras, avec un message qui accuse un body mod.
Les `preloadLocalMaterialInstances` sont des `CMaterialInstance` (`baseMaterial` `female_arm_<teint>.mi`,
`values` vides) rangés en `{HandleId, Data}` : même contenu que `localMaterialBuffer.materials`, autre
rangement. Correctif : `shell()` remplace la liste présente (buffer ou preload), ≈ 10 lignes ; **QA en
jeu sur corps vanilla nécessaire** (jamais vu).

**Mesure 2 : EBBRB 5.0.0** (Hyst, Nexus 4654, fichier 170224 du 28/10, 185 Mo, dépaqueté dans
`C:\__DEV\cyberpunk\ink_flow\dl\4654\ebbrb\`) : une archive `05_Hyst_Refit_ForcedBigBreastsBooty.archive`
+ `EBBRB.xl` (même patron qu'Angel : patch `femv_seamfix`, `hyst_boobs_*`, `player.bodyTypes: [EBBRB]`)
+ `r6\scripts\VTK_Hyst_CC_Edit\VTK_Hyst_CC_Edit.reds`. L'archive **livre** corps, bras HQ, bras FPP, torse
FPP, app FPP, morphtarget du corps, `v_overlay`, `femme_arm_*_overlay`, pas la tête. Moteur sur un
`archive\pc\mod` qui ne contient qu'elle (`ebbrb_test.py`) : **tout passe** (corps 8 chunks, 91 371
sommets, 12 matériaux locaux ; bras 31 950 / 30 616 ; bras FPP 31 952 / 30 616 ; masque `…E0` ; morph 1
cible). Angel (son cache) : 91 360 sommets, 12 matériaux, boîte englobante identique à 1,5 cm près.
**Le moteur n'a aucune raison de rater EBBRB quand il le voit.**

**Hypothèse retenue pour « slots visibles, rien sur le corps » : le builder n'a pas vu le corps.**
`find_owner` ne lit que `archive\pc\mod`, en ordre alphabétique. Trois cas où le corps affiché par le jeu
n'y est pas : (1) **REDmod** (`<jeu>\mods\<nom>\archives\`, déploiement Vortex « REDmod ») : les archives
legacy chargent avant les REDmod, un corps REDmod est donc actif dès qu'aucun corps n'est dans
`archive\pc\mod` ; (2) **MO2** : système de fichiers virtuel, le dossier réel est vide ou partiel quand le
builder tourne hors MO2 ; (3) `archive\pc\mod\modlist.txt` : le jeu suit ce fichier, pas l'alphabet. Dans
les trois cas, repli « base game » : la coque est le corps **vanilla** (4 641 sommets, boîte -0,117 → 1,653
contre 0,007 → 1,531), posée sous la peau d'un corps à 91 k sommets plus volumineux : invisible ou par
plaques. Le journal de build l'écrit (`Body : base game`) mais la fenêtre ne le met pas en évidence et
aucun fichier journal n'est écrit. **Pas prouvé** : il faut la ligne « 2. active meshes » d'un des trois.

Le redscript de Hyst (au chargement de `female_cco`, remplace l'option `breast` [4] et les options
`[0..n)` du groupe `FPP_Body` par un donneur `mods\vtk\hyst_bodies\cc_edit.inkcharcustomization`) n'écrase
que les premières entrées du groupe ; les nôtres sont ajoutées par ArchiveXL. Risque faible, non mesuré.
Angel ne livre pas ce script (aucun `r6\scripts` dans son jeu purgé).

**« Tout dynamique » (0xVyper)** : le § 4 reste vrai : une ressource = un chemin haché, deux archives qui
livrent `v_overlay.xbm` ne sont pas distinguables à l'exécution, et la coque exige la copie du maillage
actif, que seul WolvenKit sait réécrire. Faisable dans cet esprit : un bouton **Scan game folder** qui
trouve seul les archives VTK pures (critère déjà codé dans `conflicting_archives`) dans `archive\pc\mod`
et REDmod, les importe dans la liste et les écarte à l'install. Le rebuild reste, la collecte à la main
disparaît.

**Correctifs proposés (1.0.1, sur son go)** : (a) `shell()` accepte les matériaux preload (bras vanilla) ;
(b) `find_owner` : `modlist.txt` s'il existe, sinon `archive\pc\mod` alphabétique, puis REDmod
`mods\*\archives`, puis jeu de base ; (c) la fenêtre affiche le corps résolu (« Body: 006_Angel_Body.archive »),
en rouge si « base game », avec le conseil MO2 / REDmod ; (d) `build.log` écrit dans
`%LOCALAPPDATA%\InkFlow` à chaque build ; (e) README et page Nexus : MO2 = lancer le builder depuis MO2,
REDmod, bras vanilla, « send your build.log ». (f) Scan game folder : lot séparé.

**Livré (1.0.1, 14 h → 15 h, go de Hell_Kaiser sur les six points, question in-prompt)** :
- `core.py` : `game_archives(game)` = ordre de chargement réel (`archive\pc\mod` selon `modlist.txt` s'il
  existe, sinon alphabétique ; puis `mods\<nom>\archives` selon `r6\cache\modded\MO_REDmod_load_order.txt`
  s'il existe, sinon alphabétique par dossier ; les legacy chargent avant les REDmod) ; `find_owner` le suit,
  repli jeu de base ; libellés `006_Angel_Body.archive` / `mods\x\archives\y.archive (REDmod)` ; clé de cache
  des extractions = chemin complet de l'archive source. `shell()` accepte les trois magasins de matériaux
  (`localMaterialBuffer`, `preloadLocalMaterialInstances`, `localMaterialInstances`), un seul à la fois, et
  remplace le `Data` des handles. `is_pure_tattoo`, `find_tattoo_archives` (Scan), `conflicting_archives`
  sur legacy + REDmod avec des libellés relatifs au jeu, `install` sauvegarde sous le même chemin relatif.
  `rdar.index()` : index des archives en cache (chemin, taille, mtime).
- `gui.py` : ligne **Body mesh** sous les quatre voyants (fil, `active_owners` sur corps / bras / tête ;
  rouge « BASE GAME … MO2 » si le corps est le jeu de base) ; bouton **Scan game folder…** (copie dans
  `%LOCALAPPDATA%\InkFlow\tattoos\`, nom suffixé par l'empreinte si collision) ; `build.log` réécrit à chaque
  build (version, date, jeu, voyants, ligne Body mesh, réglages, puis chaque ligne du journal) ; erreur de
  build renvoie vers `build.log`. CLI : `--from-game`, `--in` facultatif.
- **Preuves** : `order_test.py` (arbre factice) : alphabétique, `modlist.txt`, REDmod, ordre MO2, legacy
  avant REDmod, détection des tatouages purs, libellés de conflits : **A → H conformes**. `vanilla_test.py`
  après correctif : bras G / D **SHELL OK** (23 / 22 matériaux). **Build CLI complet sur le corps vanilla**
  (arbre factice `gen\t101\fakegame`, jonction vers le `content` du jeu, `archive\pc\mod` vide) : 18 tatouages,
  **157 fichiers, 71,1 Mo, 206 s** ; coque de bras dépaquetée et resérialisée : 23 matériaux preload = décal
  `customization_tattoos_01_ca_pale.mi` → `inkflow\tattoos\samurai\samurai_arm_l.xbm`, 5 787 sommets.
  **Exe figé 1.0.1** (autotest `exe\home`, Angel) : **157 fichiers, 150 347 776 o, identiques à la 1.0.0**,
  207 s, `build.log` écrit. Fenêtre capturée (`builder\tests\gui_main_2026-11-02.png`) : ligne verte
  « Body mesh: 006_Angel_Body.archive | arms: … | head: 006_VTK_Vanilla_HD_Head_xBaebsae.archive ».
  Exe final (après un changement de séparateur dans le libellé) : SHA-256 `fc33b615…9805`, autotest
  rejoué : 157 fichiers, 150 347 776 o, 149 s ; zip `InkFlowBuilder-1.0.1.zip` SHA-256 `8b38f547…`, copie
  dans `releases\`. **Build vanilla posé dans SON jeu** (14 h 37, Angel parqué, têtes VTK gardées, 21
  archives, 9 slots) : 530 fichiers, 82,6 Mo, 139 s ; QA en jeu à lui.
- **Non prouvé en jeu** : le rendu d'une coque de bras vanilla (QA à lui : Angel et têtes retirés, build,
  install, bras tatoués au miroir ; puis remettre Angel et rebâtir) ; et l'hypothèse REDmod / MO2 elle-même,
  qui attend le `build.log` d'un des trois utilisateurs EBBRB.

**QA du corps vanilla en jeu (Hell_Kaiser, 14 h 40 → 16 h 45, sept poses successives, `game_step.py`)** :

| Build posé (corps vanilla pur sauf mention) | Créateur nouvelle partie | Miroir sur sa sauvegarde (faite sur Angel) | Confirm |
|---|---|---|---|
| vanilla + têtes VTK, FPP on (14 h 37) | — | coques du chargement visibles, rien à l'activation, disparaissent | **mort** même tout Off |
| rien (Ink Flow retiré, têtes parquées) | — | yeux vides (option d'yeux des têtes VTK) | passe |
| vanilla pur, FPP on | corps et bras OK, **tête non** | rien à l'activation (Samurai = corps + 2 bras) | mort après activation |
| **build d'hier bâti sur Angel**, corps vanilla | — | **Samurai apparaît** (débordant, attendu) | **passe** |
| vanilla pur, FPP on, matériaux de bras embarqués | — | rien | mort |
| vanilla pur, **sans FPP** | OK | **Bedellia bras G puis un corps : apparaissent, Confirm, reflet et mode photo OK** ; en FPP : corps OK, **bras troués / décalés** | **passe** |
| vanilla pur, **FPP bras seuls** (pas de coque FPP corps) | OK | rien à l'activation, coques du chargement disparaissent | mort |

**Conclusions** : (1) le Confirm mort de la première pose venait du mélange têtes VTK + corps vanilla +
Ink Flow, pas du cœur ; (2) **les coques FPP de bras bâties sur `fpp\a0_000_pwa_fpp__full_l/r` vanilla
cassent l'attache à chaud au miroir** (le créateur de nouvelle partie n'attache pas de FPP, il marche) ; la
coque FPP du corps seule n'a pas été testée ; (3) **les matériaux preload ne sont pas la cause** (variante
embarquée : même échec) ; le correctif « tout dans `localMaterialBuffer` » reste dans `shell()`, neutre ;
(4) sans FPP, les coques TPP de bras (copies des bras HQ) sont **rendues en première personne** par-dessus
des bras FPP vanilla d'une autre forme → trous et décalage ; chez Angel les deux maillages ont la même forme,
rien à voir ; (5) la coque de **tête** vanilla ne s'affiche pas en nouvelle partie (non creusé).

**Mesuré sans trouver la cause de (2)** : aller-retour WolvenKit identique à l'octet (maillages et
morphtargets) ; os des bras FPP vanilla = ceux d'Angel (67 à gauche, 171 à droite, même ordre) ; structure
des maillages identique hors densité. **Seules différences restantes** entre coque FPP vanilla et Angel :
`renderResourceBlob.header.version` **20** (vanilla FPP) contre **18** (Angel, bras HQ vanilla, corps) ;
`parameters` `meshMeshParamGarmentSupport` + `garmentMeshParamGarment` présents (absents chez Angel, mais
présents sur le bras HQ vanilla qui marche) ; `renderBuffer.Flags` 7471104 contre 4063232 (idem bras HQ qui
marche). Côté attache, le jeu pose ses bras FPP en **`entSkinnedMeshComponent`** avec
`renderingPlaneAnimationParam` `renderPlaneLeftArm` / `renderPlane` et `visibilityAnimationParam`
`visibilityLeftArm` / `visibilityRightArm` (noms croisés, tel quel dans `arms\a0_000_fpp__full.app`) ; le
tatouage FPP vanilla (`t0_000_fpp__tattoo_01.app`) est un garment sur `renderPlane` **None**, visibilité
None, maillage dédié de 3 296 sommets ; nos gabarits : garment, `renderPlane`, visibilité None. Journaux
RED4ext, ArchiveXL, Codeware : muets.

**Prochain geste (décision de Hell_Kaiser, 16 h 50 : « une sonde, un logger complet, nouvelle session »)** :
un script Redscript + Codeware `InkFlow_Probe` posé dans `r6\scripts\` du jeu (jetable, hors livraison) qui
journalise par `ModLog` : `Resource/Load` et `Resource/Ready|Failed` pour tout chemin `inkflow\…`,
les événements du créateur (`gameuiCharacterCustomizationSystem` : option changée, apply, confirm), et les
composants attachés / détachés sur le joueur (nom, maillage, visible) ; lecture dans
`red4ext\plugins\Codeware\…log` ou `r6\logs\`. Puis rejouer : Angel (témoin), vanilla sans FPP, vanilla FPP
bras seuls. Hypothèses à départager par la sonde : blob v20 refusé à chaud ; garment params ; type de
composant / paramètres d'animation des bras FPP. En parallèle, option de livraison 1.0.1 **sans attendre** :
ne pas bâtir de coques FPP quand le corps est le jeu de base (avertissement dans la fenêtre), et cacher les
coques TPP de bras en FPP si le jeu offre un paramètre pour ça (à lire dans l'app TPP vanilla, non extraite :
`t0_000_base__full.app` n'est pas dans `basegame_4_appearance`, chercher les autres `basegame_*`).

## 18. Sonde Redscript/Codeware : la FPP n'était jamais appliquée, `linkController` (2026-11-02, 17 h → 18 h, Fable, « Reprends »)

**Constat de reprise** : Redscript absent de son jeu (purge du 02/11 ; `engine\tools` ne contenait que `scc` et
`libscc_lib.dylib`, binaires macOS posés par l'installateur WolvenKit qui se trompe de plateforme, déjà vu sur
Redscript et TweakXL). Posé depuis le zip 0.5.32 de `1_Core\__WOLVENKIT` (`scripts.ini`, `scc.exe`, `scc_lib.dll`,
`scc.toml`) ; RED4ext compile `r6\scripts` au lancement (« scc invoked successfully », `r6\cache\final.redscripts.modded`).

**Sonde** `tools\probe\InkFlow_Probe\InkFlow_Probe.reds` (jetable, hors livraison ; `pose_probe.py check|pose|remove|logs`) :
Codeware `Resource/Load` et `Resource/PostLoad` (CMesh, MorphTargetMesh, `.app`, `.ent`, `.inkcharcustomization`, filtrés
sur `inkflow` / bras / corps / tête / FPP / tatouage / chemins non résolus), `Entity/Assemble|Reassemble|Attach|
AfterAttach|Detach` des pantins (classe, gabarit, puis chaque composant de maillage : classe, nom, maillage, apparence,
`chunkMask`, `renderingPlaneAnimationParam`, `visibilityAnimationParam`, activé, état du jeton au dépôt), `Session/*`,
**F9 = marqueur** (`Input/Key`). v2 : dump du `.inkcharcustomization` au PostLoad (switchers avec `link`,
`linkController`, `uiSlots` ; groupes ; `perspectiveInfo`). Compilée hors jeu avant la pose : `scc.exe -compile` sur une
copie de `r6\scripts` + les `.reds` de Codeware + `final.redscripts` (80 s ; une boîte « Compilation error » s'affiche
à l'écran même en ligne de commande). Codeware n'a pas de `Resource/Failed` : l'échec se lit par l'absence de LOAD et par
`token.IsFailed()`. **`ModLog` écrit dans le journal du jeu, repris par CET dans
`bin\x64\plugins\cyber_engine_tweaks\gamelog.log`** (tronqué à chaque lancement) ; rien dans `r6\logs` ni `red4ext\logs`.
Les chemins non vanilla sortent en hash (registre Codeware) : décodés par FNV-1a 64 des chemins du pack (`rdar.fnv1a64`).

**Passage 1 (Angel, build validé de la veille, Samurai sur le slot 1)** : le journal du pantin première personne
(`player_wa_fpp_ep1.ent`, PlayerPuppet) après activation au miroir porte **les coques TPP** `inkflow_slot1_unknown_samurai`
(morphtarget du corps, masque plein), `_arm_l`, `_arm_r` (copies des bras HQ, `renderPlane`) **et aucune coque FPP** ;
aucun `.app` ni maillage `_fpp` n'est jamais demandé (LOAD) ; tout ce qui est attaché est `loaded=true failed=false`.
Vu par lui au même moment : « tatouage sous la peau par endroits, démarcation qui bouge avec les bras » = coque HQ dessinée
par-dessus les bras FPP vanilla, maillages d'une autre forme. **La QA FPP du 02/11 à 0 h n'avait pas vu ce défaut.**
Les pantins miroir / photo sont des `NPCPuppet` (`player_wa_tpp_ep1.ent`, `player_wa_tpp_reflexion.ent`).

**Cause** : dans le vanilla, le maître `body_tattoo` porte `linkController = 1` et le suiveur `fpp_body_tattoo`
`linkController = 0` (même chose `nipples` / `fpp_nipples`) ; le gabarit du toolkit 20279 met 0 partout et le builder
ne touchait pas ce champ : **sans contrôleur, le suiveur reste à Off**. Autres écarts relevés, non retenus : étiquettes
du suiveur (vanilla `NewGame` seul ; les nôtres en ont trois) ; index 1041-1048 occupés en vanilla par les infos
`body_tattoo_00..07` (sans effet mesuré). `perspectiveInfo` vanilla : `FPP_Body` ↔ `TPP_Body` ; notre fichier n'en a pas.

**Correctif** (`core.py`, bloc `if s.fpp`) : `s2["linkController"] = 1` sur le maître, `0` sur le suiveur.
**Passage 2 (même séquence, build rebâti sur Angel par `tools\probe\angel_build.py`, 170 Mo, 530 fichiers, 186 s)** :
le pantin FPP porte `inkflow_slot1_unknown_samurai_fpp` (`unknown_samurai_pwa.mesh`, masque `…E0`),
`_fpp_arm_l`, `_fpp_arm_r` (maillages `_pwa_fpp_arm_l/r.mesh`), tous chargés ; le jeu lit `linkController=true` sur
`inkflow_slot1` et `false` sur `inkflow_slot1_fpp`. **QA de Hell_Kaiser : bras corrects en FPP depuis le miroir, mode
photo bon.** Reste vrai : les coques TPP de bras restent aussi attachées au pantin FPP (comme avant) ; en FPP elles
sont maintenant recouvertes par la coque FPP de même forme, le défaut n'est plus visible. Le dump du `female_cco_ep1`
vanilla au PostLoad ne montre pas nos entrées (`inkflow=0`) : ArchiveXL fusionne après ce point ; notre ressource
est chargée à part (531 options, groupes `FPP_Body` 252 / `TPP_Body` 279 / `character_creation` 279).

~~**Non tranché** : le corps vanilla (QA du § 17) a été testé avec `linkController = 0` aussi ; le Confirm mort au
miroir avec les coques FPP vanilla reste inexpliqué, à rejouer avec le correctif et la sonde.~~ **Tranché le 02/11 à
18 h 10 (passage 3, corps vanilla pur, sa décision « on va faire un test avec vanilla »)** : build vanilla pur avec le
correctif (`tools\qa_2026-11-02\build_pure_link.py`, arbre factice, corps / bras / tête du jeu de base, 21 archives,
9 slots, FPP : **530 fichiers, 73 248 768 o, SHA-256 `c0c4bbb4…`, 62 s**), posé à 17 h 56 (Angel, refits et 4 têtes
parqués, `archive\pc\mod` = Ink Flow seul). **QA de Hell_Kaiser : validée sur les deux sauvegardes** : (1) sauvegarde
faite sur Angel avec des tatouages posés : les tatouages sont **repris et affichés sur le corps vanilla au chargement**,
sans passer par le miroir ; changement au miroir sans défaut ; Samurai (corps + 2 bras) suit la peau partout :
modificateur, reflet, **FPP**, mode photo ; (2) sauvegarde sans slot actif : même résultat ; (3) créateur de nouvelle
partie : affiche bien. Le Confirm n'est pas nommé dans son rapport mais les changements au miroir sont appliqués, ce qui
le suppose. **Journal de la sonde (6 927 lignes, `tools\probe\logs\2026-11-02_181554`) : 0 `Failed`** ; le pantin
`player_wa_fpp_ep1.ent` porte `inkflow_slot1_unknown_samurai_fpp`, `_fpp_arm_l`, `_fpp_arm_r`, `linkController=true`
lu sur les maîtres. **Conclusion** : le miroir cassé et le Confirm mort du § 17 disparaissent avec le seul changement
`linkController = 1` ; le mécanisme par lequel un suiveur non piloté tuait le Confirm sur le vanilla et pas sur Angel
n'a pas été lu (non bloquant : plus reproductible). Le § 17 garde sa valeur de table des symptômes avec `linkController
= 0`. Jeu remis à 18 h 15 (Angel, têtes, build de 17 h 28 `a6fd24c8…`, 9 archives) ; le build vanilla est gardé dans
`C:\__DEV\cyberpunk\ink_flow\builds\vanilla_link_qa\`. **Sonde retirée du jeu à 18 h 15 (sa décision : « retire-la pour
le build publiable, garde-la de côté pour d'autres corps »)**, source dans `tools\probe\`, Redscript 0.5.32 laissé en
place. La sonde journalise seule (`Resource/Load`, `Entity/Reassemble`, `Session/*`) ; F9 n'écrit qu'un séparateur
`MARK n`, inutile quand la question est binaire comme ici.

**Reste non tranché** : bras cybernétique (lames Mantis…) : masque plein sur nos coques, jamais testé (question de
Hell_Kaiser) ; EBBRB en jeu (accepté par le builder, § 17, jamais vu rendu). Vanilla `t0_000_fpp__tattoo_01.app` :
un seul maillage dédié ; nous gardons corps + deux bras.

**Builder, même séance (sa demande : « éviter les soucis de runtime »)** : bouton **Install .NET Runtime 10 (30 MB)** à
la place de « Get .NET 10… » : `env.download_dotnet` (installeur Microsoft x64 10.0.14 épinglé par taille et SHA-256
`53a67d2d…`, signature Authenticode « CN=.NET, O=Microsoft Corporation » vérifiée le 02/11 ; téléchargement commun
`_download_pinned` avec WolvenKit ; gardé dans `%LOCALAPPDATA%\InkFlow\dotnet\`, rappel sans retéléchargement),
`env.install_dotnet` (`/install /quiet /norestart`, codes 0 / 3010 / 1602), fil + file d'attente comme WolvenKit,
redétection, repli = page Microsoft avec la consigne « .NET Runtime → Windows → Installers → x64 ». La capture
`.10 Runtime.png` de `releases\` n'est plus nécessaire (et son surlignage visait le binaire Linux). Redistribuer
l'installeur serait permis (MIT, termes Microsoft) : écarté, le téléchargement épinglé suffit. Testé : téléchargement
3 s, SHA OK, second appel 0 s ; fenêtre avec `.NET` forcé manquant capturée (`tests\gui_capture_dotnet.py`,
`exe\gui_dotnet_missing.png`) : voyant rouge, bouton visible, Build grisé. L'installation elle-même n'a pas été jouée
(runtime déjà présent sur le poste). Garde-fou `_show_bodies` quand la fenêtre est déjà détruite (trace de l'autotest).

**Exe 1.0.1 rebâti** : SHA-256 `f32d59bc…7109` (11 951 071 o), autotest `exe\home` : 157 fichiers, 150 347 776 o,
129 s (même taille que la 1.0.0 : le drapeau ne change pas la longueur du CR2W) ; zip `InkFlowBuilder-1.0.1.zip`
SHA-256 `42fa8310…4ed2` (11 681 627 o), copie dans `releases\`. README, `NEXUS.md` (prérequis, étape 1, changelog) à jour.

## 19. V masculin et textures à chaîne de mips tronquée (2026-11-03, 17 h 30 → 20 h 30, Opus, go de Hell_Kaiser)

**Mesures (jeu de base en lecture, `x\male\`, `tools\qa_2026-11-03\`)** : V masculin = `player_man_average`,
textures `v_masc_overlay`, `masculine_arm_{left,right}_01_overlay`, tête `h0_001_pma_c__basehead_overlay`. Corps
`t0_000_pma_base__full.mesh` **sans morphtarget**, composant `entGarmentSkinnedMeshComponent` (8 chunks, 4 648
sommets, 38 matériaux en `localMaterialBuffer`) ; bras HQ en `preloadLocalMaterialInstances` ; tête 7 190 sommets,
64 matériaux, morphtarget 100 cibles. **Pas de maillage FPP masculin** : `t0_000_fpp__full.app` montre le corps TPP
sans masque, `arms\a0_000_fpp__full.app` les bras HQ. `male_cco` : `body_tattoo` (1040, contrôleur 1) **sans
suiveur**, ses options listées dans FPP_Body, TPP_Body et character_creation ; sélecteurs 1020, 1040, 1060, 1090… :
1041-1049 et 1066-1074 libres. Gymfiend VTK 1.4.3 : corps 6 357 sommets, mêmes stockages ; MV Head VTK livre tête +
morphtarget. VTK Vanilla HD (7054) : `shell()` accepte tout (corps 91 362 sommets, bras, bras FPP, masque `…E0`).

**Moteur 1.1.0** : `TARGETS` porte un genre (`m_body`, `m_arm_l/r`, `m_head`, suffixes `_m*`, fichiers `_pma`) ;
`gender_customization()` écrit un `.inkcharcustomization` par genre présent (`inkflow_pma` sous `male:`), suiveurs
FPP pour la V féminine seulement, coques masculines listées dans les trois groupes ; préfixe de noms étendu aux
formes `002_Tattoos_Masc_V_VTK_` et `00_MV_[VTK]_` (les slugs des noms déjà reconnus ne changent pas) ; ligne Body
mesh par genre. **Non-régression** : 20 tatouages féminins, moteur du dernier commit contre nouveau = 500/500
fichiers identiques au SHA-256, `.xl` identique (`regress_female.py`, rejouée après le ré-encodage).

**QA 1 de Hell_Kaiser (créateur, nouvelle partie, corps vanilla)** : sur 14 tatouages masculins, bandes trouées ou
rien sur 9, propres sur 5, et la règle est sans exception : **texture à 1 mip ou à chaîne complète = propre, chaîne
tronquée (11 mips sur 4096, arrêt à 4×4, `allowTextureDowngrade` 1, `platformMipBiasPC` 1) = cassée**, sur la même
coque. La texture décodée (export DDS) est saine. Canari : la même image réimportée par WolvenKit (13 mips, non
compressée) : **propre en jeu**, l'original troué. Pourquoi ces textures passent dans la peau VTK et cassent dans le
décal : non mesuré.

**Correctif** : `reencode_truncated()` dans `extract_textures` : export du dossier de textures du tatouage
(`-gp` jeu), mips lus dans l'en-tête DDS, import des seules chaînes ni 1 ni complètes (`max(w,h).bit_length()`),
ligne au journal ; clé de cache `|mips1`. Coût : texture non compressée (≈ 4 Mo dans l'archive, ≈ 85 Mo de mémoire
vidéo pour une 4096 portée) ; garder le BC7 demanderait un encodeur que le CLI n'a pas. **QA 2 et 3 validées par lui
au créateur** : Kala Japanese V2 masculin propre sur corps vanilla puis sur Gymfiend + MV Head ; V féminine inchangée.

**Exe 1.1.0** : SHA-256 `24434274…5c05`, autotest figé `exe\home` + Kala V2 masculin : 19 tatouages, 162 fichiers,
75,6 Mo, 406 s, ré-encodage au journal ; zip `43f0f655…6427` (`releases\Ink_Flow_Builder-1.1.0.zip`).

**Reste ouvert** : têtes sur tête vanilla (Kala head, Finn : rien au créateur, déjà vu § 17 ; marche sur tête VTK
HD) ; tête masculine jamais vue (pack visage 7414 dans `3_Bodies\__RAM`) ; miroir, FPP, photo du V masculin
(il n'a pas de sauvegarde masculine) ; tatouage d'un genre forcé sur l'autre (patrons UV non comparés) ; Hyst EBB
décompressé, non passé au moteur.

## 20. Tableau des corps détectés et opacité par tatouage : 1.2.0 (2026-11-03 → 04, Opus, demande de Hell_Kaiser)

**Demande** : (1) le récapitulatif des corps détectés était illisible (deux lignes longues, « over … » mêlé aux
noms) : séparer V féminine / V masculin et les éléments de corps, en tableau ; (2) un utilisateur Nexus demande une
opacité réglable tatouage par tatouage, en plus de l'opacité générale.

**Interface** : cadre « Body meshes in use » dans Setup : colonnes Female V / Male V, lignes Body / Arms / Head ;
cellule = archive gagnante (vert) ou « base game » (gris), archives écrasées en petit gris dessous ; bras G ≠ D =
deux lignes `L:` / `R:`. Ligne rouge sous le tableau seulement si aucun corps moddé n'est vu (ni féminin ni
masculin). `build.log` reçoit la forme texte (`bodies_text`). Colonne **Opacity** dans la liste : valeur propre, ou
celle par défaut entre parenthèses ; double-clic = champ à flèches, bouton **Opacity…** pour une sélection ; vide =
retour au défaut ; « 0,6 » accepté ; bornes 0,1-1,0. Le réglage général devient **Default opacity**.

**Moteur** : `alpha` rangé dans le catalogue par empreinte de contenu (à côté du nom), absent = `Settings.alpha` ;
`Item.alpha`, appliqué à toutes les coques du tatouage (TPP, FPP ; la FPP du corps réutilise la coque du corps).
Le slug ne change pas : un personnage garde ses slots. La CLI en profite par le catalogue.

**Preuves** : build CLI réel (3 tatouages, Angel) re-sérialisé : `DiffuseAlpha` 0,6 sur bras G TPP et FPP, 0,85 sur
le corps, 1,0 sur le bras droit sans valeur propre. Exe figé 1.2.0 (`4e3f15d1…9bb6`), autotest `exe\home` avec
Samurai à 0,6 : 18 tatouages, 157 fichiers, 150 347 776 o, 218 s, Samurai à 0,6 sur ses six coques au journal.
Non-régression (`tools\qa_2026-11-03\regress_female.py`, HEAD 1.1.0 contre arbre de travail, sa config, 9 slots) :
**488/488 fichiers identiques, `.xl` identique**. Captures de la fenêtre (cas réel Angel + Gymfiend, cas fabriqué
sans corps moddé avec bras G/D différents) : lisibles. Zip `3e1f13f9…6a46` (`releases\Ink_Flow_Builder-1.2.0.zip`).
Non vu en jeu : une coque à 0,6 rend comme le réglage général à 0,6 (même champ du même matériau).
