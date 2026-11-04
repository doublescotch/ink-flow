# Passation — Ink Flow (VTK/UV CCXL Tattoo Loader)

Créée le 2026-11-01 à 2 h 45 (compartimentage demandé par Hell_Kaiser : chaque projet de création porte sa passation et son journal dans son dossier ; `cp:HANDOVER.md` ne garde qu'un renvoi). Ce fichier ne porte que **l'état vivant** : ce qui est posé, ce qui attend, ce qui n'est pas tranché. Les mesures, décisions et acquis vivent dans `ETUDE.md` ; la chronologie dans `LOG.md`.

~~**Pas de git tant que le proto ne tient pas**~~ Dépôt ouvert depuis le 01/11 (21 h 25) :
`https://github.com/doublescotch/ink-flow`, branche `master` ; `canari\` exclu.

## État (2026-11-04, 22 h 15) : canari Angel (mêmes 2 tatouages, jeu minimal) POSÉ dans son jeu, verdict attendu

- **Posé à 22 h 12** (son déverrouillage de 22 h 09, `WRITE_UNLOCK.txt` re-enregistré) : `solo_bench.py restore`
  (Solo + bras UV retirés, Angel + `.xl` + refits revenus du parc), `canari3.py build` sur Angel (132 s, 33,1 Mo,
  SHA `14f05dc1…`, `gen\uv104\out_canari3`), `canari3.py install` ; canari Solo passe 2 dans `backup\2026-11-04_221234`.
  Jeu toujours **minimal** : Angel (3 fichiers) + framework 3.2.1 + Ink Flow, 420 archives parquées.
- **Contenu du canari Angel** : Kala V2 UV = corps seul, bande des bras effacée (réimport, en-tête réécrit) ; Kala n'a
  **pas d'encre sur les bras** (sautés) ; Samurai VTK = corps 8K + bras VTK tels quels. **Aucun bras converti 8K** dans ce
  build, contrairement au canari Solo (deux bras convertis 8K importés par WolvenKit).
- **Lecture du verdict** (3 chargements de sauvegarde + défilé au miroir, par lui) : plante avec la signature `memcpy`
  ⇒ nous, hors conversion (corps Samurai 8K ou Kala UV reconstruite : canari Samurai seul, puis Kala seule). Ne plante
  pas ⇒ **Solo ou les bras convertis 8K**, pas départageables ici : canari suivant = Solo remis avec Samurai seul,
  bras convertis en 4K au lieu de 8K (remède mémoire déjà listé), ou Solo sans aucun tatouage.
- Retour à son jeu normal, sur sa formule (jeu fermé) : `minimal_bench.py unpark_all` puis rebuild complet moteur
  corrigé (≈ 20 min) + `install`, ou remise à la main du build Angel de `backup\2026-11-04_175841`.

## ~~État (2026-11-04, 22 h 05) : le correctif d'en-tête est juste mais N'EST PAS la cause des plantages ; canari suivant = mêmes 2 tatouages sur Angel~~ dépassé (22 h 15 : canari Angel posé)

- **Canari 3, passe 2 (moteur corrigé, Kala V2 UV + Samurai VTK, jeu minimal, VM et Opera coupés) : plantage au
  chargement de la sauvegarde à 21 h 57, signature `memcpy` identique** (`exe+0x196A3CC` ← `+0x343451`, source
  illisible dès le premier octet, `D3D12Core` dans la pile, r8 = 3 072 o). Passe 1 (non corrigé) : gel watchdog au 3e
  chargement. Donc : l'en-tête faux de Kala est réel et corrigé (commit `3ff9324`, à garder), mais ces plantages ont
  une autre cause. Prémisse « Angel ne plantait pas grâce au réimport » : affaiblie, pas prouvée.
- **Ce qui reste dans le jeu minimal au moment du plantage** : Solo OG 2.0 + bras Solo UV + framework 3.2.1 + Ink Flow
  2 tatouages (Kala V2 UV 4K reconstruite ; Samurai VTK = corps 8K + deux bras convertis 8K importés par WolvenKit).
  Suspects : **Solo** (page Nexus : plantages au chargement 2/3 du temps, même installation propre ; `.app` mal formé),
  le framework, nos textures 8K importées (bras convertis), le corps Samurai 8K (jamais suspect sur Angel).
- **Canari suivant, le seul qui tranche** (prochaine session, jeu fermé, sa formule) : `solo_bench.py restore` (Angel
  revient, Solo part) en gardant le jeu minimal, `canari3.py build` + `install` (mêmes 2 tatouages ; sur Angel les bras
  du Samurai restent VTK, ceux de Kala UV sont convertis en 2K/4K vers vanilla), 3 chargements + miroir. Plante avec la
  même signature ⇒ nous (bras convertis ou corps 8K : canari Samurai seul, puis Kala seule). Ne plante pas ⇒ Solo.
- ~~**Lancement lent du jeu minimal** (sa remarque) : près de 2 min avant le chargement ; non expliqué (parc de 420
  archives lu ?)~~ **sans objet (22 h 10, journaux lus)** : jeu complet de 20 h 11 (191 `.xl`) et jeu minimal de
  21 h 55 (3 `.xl`) mettent tous deux **66 s jusqu'au menu**, puis ≈ 40 s pour la sauvegarde ; audioware seul prend
  18 s à chaque lancement. Le dossier parqué n'apparaît dans aucun journal : rien à déplacer.
- Gels watchdog (18 h 13, 20 h 40, 21 h 47) : même fil principal bloqué dans la présentation d'image, DLL anonymisée
  dans la pile (`170_E658703.dll`, 5 modules), ReShade / overlay candidats ; second phénomène, non traité.
- **Son jeu ce soir** : minimal (Solo) + canari 3 passe 2. Retour à son jeu normal sur sa formule (`archive\pc`, jeu
  fermé) : `minimal_bench.py unpark_all`, `solo_bench.py restore`, puis rebuild complet moteur corrigé (≈ 20 min) ou
  remise à la main du build Angel de `backup\2026-11-04_175841` (conversions retournées, mais jamais planté).
- Sauvegardes du jour : `_205556` = Solo complet 19 h 44, `_215048` = passe 1, dernière = passe 2 écrasée par rien.
  Jetables : `gen\uv104\work_canari3`, `out_canari3*`, `scratchpad\tex_*`, `reimport_probe`, `test_normalize_work`.

## ~~État (2026-11-04, 21 h 55) : cause des plantages trouvée (en-têtes de texture faux chez Kala), correctif commité ; canari 3 passe 2 dans son jeu minimal, verdict attendu~~ dépassé (22 h 05 : passe 2 plantée, même signature)

- **Cause mesurée** (ETUDE § 25) : trois textures de Kala (`Kala Japanese V2` VTK, UV, With Sleeves) déclarent
  « 1 mip, 1 398 128 o » sur un tampon de 13 mips (22 369 648 o) ; le moteur copie le mip 4096 hors d'un tampon de
  1,4 Mo = les trois rapports `memcpy` (18 h 34, 20 h 14, 20 h 30, dépassement de 1,44 Mo). Angel ne plantait pas :
  sa copie « bande effacée » réécrivait l'en-tête. Le pack masculin Kala V2 (§ 19) a le même en-tête faux.
- **Correctif commité** (`3ff9324`) : `core.texture_headers` + `core.normalize_textures` (sérialisation, en-tête contre
  tampon, chaîne tronquée ⇒ export + chaîne complète + import `--keep` = BC7 conservé, 22 Mo VRAM au lieu de 85).
  Preuve hors jeu : 4 archives (`test_normalize.py`), non-régression 944 / 947 = les 3 textures de Kala, `.xl` idem.
  Au passage : lignes du tableau Tk à hauteur de police (post Nexus, écran à 150 %).
- **Son jeu maintenant** : jeu MINIMAL (`minimal_bench.py park_all` : 420 archives dans `archive\pc\mod__parked_2026-11-04`,
  gardés Solo + bras UV + framework + Ink Flow) + **canari 3 passe 2** (`canari3.py`, Kala V2 UV + Samurai VTK, moteur
  corrigé, 31,9 Mo, installé 21 h 50). VM et Opera coupés par lui. Sauvegardes : `backup\2026-11-04_205556` = build Solo
  complet de 19 h 44 (non corrigé), `_215048` = passe 1.
- **Passe 1 (non corrigé) jouée par lui** : 3 chargements, dizaines de bascules au miroir ; gel au 3e chargement après un
  clic de plus, **watchdog 120 s**, pas la signature `memcpy`. Les 3 gels du 04/11 (18 h 13, 20 h 40, 21 h 47) ont le
  même fil principal bloqué (`exe+0x26DD2B` → DLL anonymisée `170_E658703.dll` → `exe+0x26DE10`, pile avec `dxgi.dll` à
  20 h 40 : un crochet sur Present, gel côté GPU / présentation) ; le gel du 03/11 22 h 25 est ailleurs. Non attribué :
  ReShade (`d3d12on7`, `ReShade.ini`), overlays, pilote ; un mauvais envoi de texture au GPU reste possible.
- **Verdict attendu de la passe 2** (mêmes gestes, plus longtemps) : tient ⇒ en-tête ; gèle ⇒ Solo ou le crochet
  Present, canari suivant = même jeu minimal sans ReShade / overlay, puis sans Solo (Angel). Sa remarque : les corps
  purement UV ne sont plus d'actualité (Solo, Songbird) ; la priorité = UV sur VTK (Angel, EBB, vanilla), déjà vu bon.
- Solo signalé instable au chargement sur sa page Nexus (post du 28/08/2026) : hypothèse concurrente, ETUDE § 25.
- **Retour à son jeu normal** (sa formule sur `archive\pc`, jeu fermé) : `minimal_bench.py unpark_all`, puis
  `solo_bench.py restore` (Angel), puis rebuild complet avec le moteur corrigé (toutes les textures re-extraites une
  fois, clé `mips2`, ≈ 20 min) et `install`. Ensuite QA Angel, statuts de `NEXUS.md` / README, exe + zip, upload, tags.
- Télémétrie : `scratchpad\vram_log.py` → `vram_2026-11-04.csv`, `_b.csv`. Jetables : `gen\uv104\work_canari3`,
  `out_canari3*`, `scratchpad\tex_*`, `reimport_probe`, `test_normalize_work`.

## ~~État (2026-11-04, 20 h 15) : build Solo installé, Samurai VTK validé ; PLANTAGES = le chantier, télémétrie posée, test à jouer~~ dépassé (21 h 55 : cause trouvée, correctif commité, canari 3 en cours)

- **Son QA Solo (19 h 45-19 h 50)** : Samurai VTK = corps + deux manches partout (créateur, miroir, FPP au miroir) ;
  les VTK défilés au miroir tous bons. **Pas vu** : les UV (plantage avant d'y arriver), FPP ventre, photo, TPP.
  **FPP hors miroir : ventre sans tatouage** sur Solo : le masque FPP du torse est le masque vanilla (`.app` de Solo
  illisible au CLI, § 21) ; à corriger (lire les masques de chunks de Solo autrement), après les plantages.
- **Plantage 19 h 50 en jeu actif**, au miroir en défilant les tatouages : l'hypothèse « jeu en arrière-plan » est
  morte. Sa position : « ça doit venir de nous, le créateur ne coupait pas comme ça avant ». Quatre plantages de
  18 h 13 à 19 h 50, tous avec le banc Solo + un build 1.4.0 (le canari de 2 tatouages compris).
- **Lu dans les rapports** (`%LOCALAPPDATA%\REDEngine\ReportQueue\`, sondes ARP `red4ext\plugins\AppearanceRuntime
  Plugin\Logs\crash-*.txt`) : 18 h 13 = gel 120 s ; 18 h 34 et 19 h 50 = **même signature**, `memcpy` dans
  `Cyberpunk2077.exe+0x196A3CC` appelé de `+0x343451`, copie d'une texture dont la source est partie (19 h 50 : dès le
  premier octet ; 18 h 34 : au-delà d'un tampon de 1,4 Mo) ; 19 h 13 = `D3D12Core.dll+0x52044` lit `0x98` (pointeur
  nul, déjà vu le 29/10). Dimensions dans la pile : carrés de 1 980 et 2 204 unités de 16 o (62,7 et 77,7 Mo) avec
  chaîne de mips : **aucune texture du build ni de Solo / framework n'a ces tailles** (46 + 24 en-têtes exportés,
  toutes en puissances de deux, 8K BC7 pour les bras convertis). Texture non identifiée, dump sans symboles.
- **Historique** : 24 rapports depuis le 28/10, 20 avant tout Ink Flow (7 « GPU crash » le 28/10, gels, IRF le
  01/11, Red Profiler à la sortie). Son jeu plante déjà ; ce qui est nouveau = plante en minutes au miroir.
- **Poste au repos, jeu fermé** (nvidia-smi, 20 h 09) : **VRAM 3,0 Go / 8 pris** (Opera, Claude, VS Code, Edge,
  Outlook…), **RAM 19,9 Go / 32 pris**, commit 33 Go. Le jeu à 3840 × 1600 a 5 Go de VRAM et 12 Go de RAM.
  Hypothèse de travail : pression mémoire (VRAM ou RAM) et textures 8K par tatouage porté (corps 8K + deux bras 8K
  convertis = 3 × 64 Mo BC7 + mips par VTK), le défilé au miroir en charge des dizaines en secondes.
- **Télémétrie posée** : `scratchpad\vram_log.py` → `vram_2026-11-04.csv` (VRAM, GPU %, jeu, RAM, commit, 1 s,
  90 min ou fichier `.stop`). **Test à jouer par lui** : même geste (miroir, défilé des tatouages jusqu'aux UV) ;
  je lis la courbe au plantage. Puis canari discriminant : même geste **sans** `Ink_Flow.archive` (+ `.xl`) dans
  `archive\pc\mod` (lui, ou formule) : plante → le banc Solo / le jeu ; ne plante pas → nous.
- **Remèdes mémoire prêts à coder si la courbe le dit** : une seule texture pour les deux bras convertis (moitié
  basse = G, moitié haute = D, comme les peintres UV : −64 Mo par VTK porté) ; conversion en 4K au lieu de 8K
  (la bande = 22 % de la largeur) ; textures FPP partagées (déjà). Rien codé avant la mesure.
- Reste inchangé : Angel après ce banc (`solo_bench.py restore`, formule), QA Angel, statuts entre crochets de
  `NEXUS.md` / README, exe + zip, upload, tags sur go. Jetables : `scratchpad\tex_pack`, `tex_bodies` (exports DDS).

## ~~État (2026-11-04, 19 h 45) : build Solo complet refait avec le correctif, non-régression 947/947 ; installation et QA Solo à faire, puis Angel~~ dépassé (20 h 15 : installé, Samurai VTK validé, plantages = le chantier)

- **Prêt, pas installé** : `gen\uv104\out_solo_game\Ink_Flow.archive` (348,1 Mo, SHA `6bf974d1…`, `.xl` 194 o), sa
  config + 16 UV, 35 tatouages, 13 bras VTK convertis vers la bande avec le `v` corrigé (Samurai 68 % du bras
  encré), Pirate Vince vers vanilla, aucune archive en conflit. Journal `gen\uv104\log_solo_game.txt`. **Installé dans son jeu à 19 h 44**
  sur sa formule (canari 2 dans `backup\2026-11-04_194421`).
- **Prochain geste** : ~~(1) `solo_bench.py install`~~ fait 19 h 44 ; (2) **sa QA Solo** : créateur (Samurai VTK = deux manches,
  Kala Arm, Bedellia, Vale), puis FPP, miroir, photo, TPP (jamais faits, plantages) ; (3) `solo_bench.py restore`
  (formule), rebâtir sur Angel, **revoir le Samurai UV sur Angel : deltoïde plein** ; Kala Sleeve 1, Bedellia, V
  masculin ; (4) écrire les statuts entre crochets de `NEXUS.md` et du README, exe + zip, upload, tags sur go.
- **Non-régression rejouée** : 1.3.0 (`31bc458`) → arbre courant, 947 / 947 identiques, `.xl` identique
  (`regress_female.py <ref>`). Le correctif ne touche que les conversions.
- **Page 1.4.0 préparée** dans `NEXUS.md` (statuts non vus entre crochets, lien framework = Nexus 3783 à confirmer
  par lui : son 3.2.1 vient de son zip) ; README « Known limits » : Solo vu au créateur. Version : 1.4.0.
- Sauvegardes du jour dans `backup\` : `_175841` = Angel 1.4.0 (conversions retournées), `_182737` = Solo complet
  (idem), `_185219` et `_190814` = canaris. Jetable : `gen\uv104\work_*`, `out_canari*`, `out_solo_game` après
  installation. Trois plantages de la séance précédente (jeu en arrière-plan) : non attribués, à surveiller.
- Ses mots de la veille « là j'avais aucune différence pour moi » : toujours à préciser par lui, rien supposé.

## ~~État (2026-11-04, 19 h 15) : conversion des bras corrigée (retournement vertical), validée sur Solo avec 2 tatouages ; build complet et QA Angel à refaire~~ dépassé (19 h 45 : build complet refait, non-régression rejouée)

- **Trouvé et livré** (ETUDE § 24, commit de cette séance) : `armconv` lisait et écrivait les textures avec v = y/h,
  le jeu lit **v = 1 − y/h** dans l'image que WolvenKit exporte / importe ; chaque bras converti était retourné
  verticalement (contenu miroir, posé sur la moitié que l'autre bras lit). Correctif = `v ← 1 − v` sur les deux jeux
  d'UV après appariement ; clé de cache `v2`. Preuves : 3 canaris en jeu validés par lui, Jaccard 82 % hors jeu.
- **Dans son jeu maintenant** : Solo OG 2.0 + bras Solo UV + framework (Angel parqué dans
  `C:\__DEV\cyberpunk\ink_flow\parked\2026-11-04_angel\`), **build de 2 tatouages** (Samurai VTK + Unknown Samurai UV,
  41 Mo, `595cba24…`, `gen\uv104\out_canari2`). Sauvegardes dans `%LOCALAPPDATA%\InkFlow\backup\` : `2026-11-04_175841`
  = Angel 1.4.0 de 16 h 17 (`6d7043aa…`, conversions retournées), `_182737` = Solo complet (35 tatouages, idem),
  `_185219` = canari 1, `_190814` = canari 2. Les deux builds complets sont **périmés** (conversions fausses).
- **Prochain geste** : (1) rebâtir sur Solo avec sa liste réelle (`solo_bench.py build` puis `install`, ≈ 22 min ; ou
  lui au builder : ses 21 archives + les 16 UV de `dl\uv\tattoos\`) ; QA Solo : FPP, miroir, photo, TPP (jamais faits,
  plantages) ; (2) **Angel remis** (`solo_bench.py restore`, jeu fermé, formule), rebâtir, **revoir le Samurai UV sur
  Angel : le deltoïde doit être plein** ; puis Kala Sleeve 1, Bedellia, V masculin ; (3) non-régression 1.3.0 → 1.4.0 à
  rejouer (`regress`, attendu 947/947 : aucune conversion sur l'arbre vanilla) ; (4) README, `NEXUS.md` changelog 1.4.0,
  exe + zip, upload, tags sur go. Version : rester en 1.4.0 (jamais publiée), le correctif est dedans.
- **Trois plantages du jeu dans la séance, tous jeu en arrière-plan** (Alt-Tab pour écrire sa QA ; une fois avec une
  VM Odoo 15 qui échouait à démarrer au même moment). Non attribué ; hypothèse VRAM 8 Go + textures 8K, non mesurée.
  Rien vu en jeu actif.
- **Sa consigne gravée** (mémoire `feedback-builds-de-test-cibles`) : un banc ou canari = seulement les tatouages de
  la question, jamais sa liste entière.
- Ce qui ne tient plus (barré dans ETUDE § 23) : « bande z 1,36-1,46 vide chez les peintres UV », « remplir la bande
  depuis le corps » ; les `seam*.py` lisent au point miroir. La divergence VTK / UV du Samurai existe (deux exports de
  l'artiste : encre plus noire, patch ventral, motifs décalés d'1 cm) : réglage d'opacité par tatouage, rien à coder.
- Ses mots de la veille « là j'avais aucune différence pour moi » : toujours à préciser par lui, rien supposé.
- Jetable : `gen\uv104\work_solo_game`, `out_solo_game`, `work_canari_swap`, `out_canari_swap`, `work_canari2`,
  `out_canari2` ; scratchpad `diag\` (≈ 1,5 Go d'exports) et `pylib\` (texture2ddecoder) de la séance.

## ~~État (2026-11-04, 18 h) : banc Solo 2.0 posé dans son jeu, l'épaule du Samurai UV à regarder par lui~~ dépassé (19 h 15 : cause trouvée, correctif livré)

- **Dans son jeu depuis 17 h 59** (horloge du poste, qui marque une heure de moins que les blocs
  précédents ; son déverrouillage `WRITE_UNLOCK.txt` de 17 h 33, jeu fermé) : Angel, son `.xl` et
  ses refits vanilla **parqués** dans `C:\__DEV\cyberpunk\ink_flow\parked\2026-11-04_angel\` ;
  **Solo OG 2.0 + `.xl` + Solo OG 2.0 Arms UV posés** (framework 3.2.1 déjà à lui).
- **Ink Flow 1.4.0 rebâti sur ce jeu** (sa config + 16 UV, 35 tatouages, 9 slots, miroir, FPP) :
  346,8 Mo, 1 415 fichiers, 1 339 s, SHA `1e97af4f…8e95` ; l'Angel de 16 h 17 (`6d7043aa…`) dans
  `%LOCALAPPDATA%\InkFlow\backup\2026-11-04_175841`. Aucune archive en conflit.
- **Détection lue dans le journal** (`gen\uv104\run_solo_game.txt`) : corps = Solo (mise à plat
  vanilla, 3 % dans la bande), bras G / D = Solo Arms UV (bande, 100 %), tête = VTK HD Head. Bras
  des UV **directs** ; bras des VTK **convertis vers la bande** (Samurai 56 %, Kala Arm 46 / 38 %
  en 4K, Bedellia 33 / 31 %, Vale 31 %, Promiscuity 2 %, Cover Me In Gold 1 %) ; Pirate Vince (M)
  vers vanilla. `.app` de Solo illisible (`castShadows`, § 21) → masque FPP du torse = vanilla.
- **À lui au créateur, nouvelle partie** : **l'épaule du Samurai UV : pleine ou nue ?** C'est ce
  qui tranche (§ 23, correction). Puis Samurai VTK converti sur les mêmes bras ; Kala Sleeve 1 =
  manches seules ; Bedellia = raccord d'épaule ; torse et bras en FPP (masque vanilla) ; port de
  lien du bras gauche sans encre.
- **Lecture** : épaule **pleine** sur Solo → la bande z 1,36-1,46 est cachée par le corps framework
  et le remède pour Angel = remplir cette bande du bras converti depuis la texture du corps
  (`armconv.py`, source corps vanilla). Épaule **nue** aussi → lecture fausse, lire les `.app` du
  framework (masques de chunks, ordre des surfaces).
- **Retour à Angel** : `tools\qa_2026-11-04\solo_bench.py restore` (jeu fermé, formule), puis le
  build de `backup\2026-11-04_175841` remis à la main ou rebâti. Modes du script : `park | build |
  install | restore | status`. Jetable : `gen\uv104\work_solo_game`, `out_solo_game`.
- Ses mots de la veille « là j'avais aucune différence pour moi » : toujours **à préciser par lui**,
  rien supposé. Reste : QA Angel (Kala Sleeve 1, Bedellia, FPP, V masculin) après ce banc ; README,
  `NEXUS.md` 1.4.0, exe + zip, upload, tags sur go ; 1.3.0 jamais uploadée.

## ~~État (2026-11-04, 18 h 40) : QA 1.4.0 suspendue ; SA DÉCISION = banc Solo 2.0 d'abord (UV sur corps natif), puis UV sur VTK~~ fait (banc posé, bloc du dessus)

- **Premier geste de la reprise** : poser dans son jeu **Solo 2.0 + framework 3.2.1 + bras Solo UV**
  (archives dans `C:\__DEV\cyberpunk\ink_flow\dl\uv\`, Angel et refits parqués), bâtir avec les UV
  (Samurai UV en tête) et regarder **l'épaule** du Samurai UV au créateur : pleine ou nue ? Banc
  jamais fait (Solo + bras UV prouvés hors jeu seulement). Jeu fermé, formule sur le dossier du jeu
  si je pose.
- **Pourquoi** (ETUDE § 23 + correction) : son retour « deltoïde gauche nu sur Samurai UV, plein sur
  Samurai VTK, Angel » n'est **pas** une différence de peinture (j'avais conclu ça trop vite, il m'a
  repris : même auteur). Preuve : partie corps UV = corps VTK à 98,5 % (même mise à plat) ; le bras
  diverge : **bande z 1,36-1,46 du bras encrée en VTK, vide en UV** (chez les 5 peintres UV), poignet
  encré en UV seulement. Lecture : cette bande est cachée sous l'épaule du corps framework, visible
  sur Angel. Le banc Solo tranche.
- **Si l'épaule est pleine sur Solo** : remède côté chaîne pour les bras VTK = remplir la bande
  1,36-1,46 du bras converti depuis la texture du corps (transfert 3D corps → bras, outillage
  `armconv.py`, source corps vanilla). **Si nue aussi** : lecture fausse, regarder les `.app` du
  framework (masques de chunks) et l'ordre réel des surfaces.
- Mesures faites, hors jeu, rien posé : couture corps / bras d'Angel = vanilla ; mise à plat du corps
  d'Angel à l'épaule = vanilla à 1-2 texels ; hexagones gris en haut de la texture = hanches ; haut
  du bras (z > 1,42) vide dans toutes les textures de bras lues. Scripts `tools\qa_2026-11-04\seam*.py`
  (`seam5.py` rendu A/B/C : ne modélise pas ce que le jeu cache, pas une preuve pour la bande ;
  `seam7.py` = différence pixel à pixel, l'outil qui vaut). Images `canari\seam_2026-11-04\`.
- **1.4.0 inchangée dans son jeu** (`6d7043aa…`). Ligne « Same name, two paintings » retirée de
  `NEXUS.md` (jamais publiée, fausse). QA Angel restante (Kala Sleeve 1, Bedellia, FPP, V masculin)
  **après** le banc Solo. Puis README, `NEXUS.md` changelog 1.4.0, exe + zip, upload, tags sur go.
- Ses mots : « là j'avais aucune différence pour moi » (fin de séance, non détaillé : à lui préciser
  à la reprise, sans supposer).

## ~~État (2026-11-04, 16 h 25) : 1.4.0 = conversion des bras UV ↔ vanilla, posée dans son jeu, QA à lui~~ complété (18 h : premier retour de QA tranché, bloc du dessus)

- **Mesuré puis codé sur son go « dans les deux sens »** (ETUDE § 22) : un bras d'une famille sur des
  bras de l'autre est **converti** (texture rééchantillonnée vers la mise à plat active) au lieu
  d'être sauté. Vers vanilla : 2K / 4K, 13-35 s par bras ; vers la bande : 8K, ≈ 40 s. Exige le
  framework UV dans le jeu (ses bras = la carte) ; sinon repli 1.3.0, raison au journal.
- **Preuves hors jeu** : bancs factices Solo / Angel / Angel + framework ; non-régression 947 / 947
  identiques à la 1.3.0 ; texture relue dans l'archive. Commit `5799364`, poussé.
- **Dans son jeu depuis 16 h 17** : build de sa config + 16 UV (391 Mo, 1 358 fichiers, SHA
  `6d7043aa…`), ancien dans `backup\2026-11-04_161654`. 14 UV à bras convertis (Pirate Vince en V
  masculin compris), Kala V2 et Anal Slut sans encre dans la bande (corps seul).
- **QA à lui** : Kala Sleeve 1 (manches), Bedellia (raccord à l'épaule, texte lisible), Samurai UV
  contre Samurai VTK, FPP tête baissée, V masculin. Effets annoncés : trait possible sur une couture
  du dépliage, bras un peu plus doux que l'original.
- **Après la QA** : README (ligne « [IN-GAME STATUS] » des limites), `NEXUS.md` (changelog 1.4.0,
  « Arms and families »), exe + zip 1.4.0 (`build_exe.ps1` installe numpy 2.4.6 : exe ≈ +15 Mo),
  upload (1.3.0 jamais uploadée : la 1.4.0 la remplace), tags sur go.
- Jetable : `C:\__DEV\cyberpunk\ink_flow\dl\uv\conv\` (paires, bancs, ≈ 1 Go), `gen\uv104\*_angelfw`.

## ~~État (2026-11-04, 14 h 55) : UV 1.3.0 validé sur son Angel (chevilles comprises), exe + zip bâtis, upload à lui~~ dépassé (16 h 25 : 1.4.0)

- **Banc fait sur SON Angel** (sa consigne : Angel d'abord) : `game_build.py` (sa config + 16 UV du
  zip) installé 14 h 23 (314 Mo, `cec96ac7…`, ancien dans `backup\2026-11-04_142352`). Son QA du
  premier build : **tout à l'attendu** (VTK inchangés, UV = corps seul, bras et pieds nus, V
  masculin bon). Deux retours traités sur ses go : chevilles (chunk 6 masqué coupait l'anneau) →
  **bande u < 0,22 effacée dans une copie de la texture** pour la coque de corps, plus de masque
  (ETUDE § 21, fin : `--keep` garde le BC7, 8K ≈ 55 s, cache) ; FrecklesV invisible (texture pâle) →
  opacité 2,0 dans le catalogue de test. **QA 14 h 35 : chevilles validées** (= Samurai VTK) ;
  **FrecklesV invisible même à 2,0, et sa version VTK est aussi pâle** : limite des coques (calques
  très pâles), gravée dans README, `NEXUS.md` (Known limits) et ETUDE § 21.
- Correctif au passage : la tête masculine Leon Face nomme sa peau `01_ca_pale_d01` → règle « peau »
  en préfixe, garde-fou « jamais de coque vide ». Commité (`a4e2cae`) ; la bande effacée reste **à
  commiter** avec ce bloc.
- Sa question (retour Nexus « partie métallique absente ») : le décal vanilla ne porte que la
  diffuse ; piste = le décal à rugosité / métal / normale du corps Songbird, chantier à part à
  mesurer.
- Catalogue de test = copie (`gen\uv104\catalogue_game_copy.json`) : son catalogue réel n'a pas les
  16 UV ni le 2,0.
- **Exe et zip 1.3.0 bâtis (14 h 50, sur son go)** : exe `1b9c6a6b…ca92` (11,97 Mo), autotest figé
  sur `exe\home` (18 VTK, jeu réel) : 157 fichiers, 150 347 776 o (= 1.2.0 au bit près côté taille),
  321 s ; zip `releases\Ink_Flow_Builder-1.3.0.zip` `8ac7a3e6…c91ca`. **À lui** : upload (1.1.0 en
  ancienne version, 1.2.0 jamais uploadée), coller `NEXUS.md` (résumé, What works with what avec la
  ligne UV « seen in game » à écrire sur son QA Angel : corps UV, pieds nus, bras sautés ; Solo non
  vu), changelogs 1.2.0 + 1.3.0, capture de la fenêtre (colonne cibles « (UV) »), sticky, tag
  `v1.3.0` sur go.
- Régression après la bande effacée : non rejouée (sans objet sur l'arbre vanilla : aucun chunk dans
  la bande).
- Solo + framework + bras UV **jamais vus en jeu** (prouvé hors jeu seulement) ; la page doit le
  dire tel quel.

## ~~État (2026-11-04, 15 h) : support UV codé et prouvé hors jeu (1.3.0), banc en jeu à lui ; exe non rebâti~~ dépassé (14 h 30 : banc fait)

- **Moteur 1.3.0 livré et commité** (ETUDE § 21, « Livré ») : une texture UV → corps + bras G + bras
  D (+ FPP), tête UV = tête ; mise à plat des bras lue dans le JSON du maillage actif, cibles bras
  sautées quand la famille ne correspond pas (journal « skipped ») ; chunks non-peau cachés dans
  toute coque (port de lien, plaques Songbird) ; pieds et chevilles d'Angel cachés sous une texture
  UV ; morphtarget de tête lu à part quand le framework UV ne le livre pas (la 1.2.0 refusait le
  build sur un jeu avec le framework : corrigé).
- **Preuves** : builds CLI sur arbres factices Solo (116 fichiers, 83 Mo) et Angel (70 fichiers),
  contrôlés (`uv_check.py` : masques, textures copiées une fois, options du créateur) ;
  non-régression 1.2.0 → 1.3.0 : 380/488 identiques, 108 `.app` de bras gauche ne diffèrent que par
  le masque du port de lien, `.xl` identique.
- **Effet visible annoncé** : plus d'encre sur le port de lien personnel de l'avant-bras gauche
  (toutes versions de coque, VTK compris). **Exe et zip 1.3.0 non rebâtis** (`build_exe.ps1`) : sur
  son go, après ou avant le banc.
- **Banc en jeu, à lui (jeu fermé, formule sur le dossier du jeu si je pose)** : (1) Angel + refits
  + têtes parqués ; poser `011_UV_Framework_Texture_3.2.1`, `006_Solo_OG_2.0` + `.xl`,
  `005_Solo_OG_2.0_Arms_UV` (dans `C:\__DEV\cyberpunk\ink_flow\dl\uv\`) ; builder (ou `uv_build.py`
  repointé sur son jeu) avec les 5 UV + Samurai ; Install. (2) Créateur, nouvelle partie : Kala
  Sleeve 1 = manches sur les deux bras, rien sur le corps ; Bedellia = corps + bras ; Garden Bloom =
  corps + tête ; Samurai = corps seul ; FPP (bras), miroir ; **masque FPP du torse Solo** = valeur
  vanilla faute de `.app` lisible : regarder le torse en FPP. (3) Angel remis + les 5 UV : torse
  seul, **pieds nus**, bras nus ; Samurai entier. (4) Le port de lien du bras gauche sans encre
  (effet annoncé).
- **Après son QA** : `NEXUS.md` (« seen in game » à écrire dans « What works with what »), capture
  de la fenêtre (colonne cibles « (UV) »), exe + zip 1.3.0, upload (1.2.0 jamais uploadée : la 1.3.0
  la remplace), tag.
- Chantiers UV restants, non tranchés : conversion des bras (mise à plat vanilla ↔ bande, ETUDE § 21
  point 4) ; tête masculine UV jamais mesurée (`ma_head_overlay_d01`, aucun pack sous la main) ;
  Songbird body non vu.
- Jetable sur le poste : `C:\__DEV\cyberpunk\ink_flow\dl\uv\` (≈ 1 Go) et `gen\uv104\` (arbres
  factices, builds).

## ~~État (2026-11-04, 13 h) : support UV mesuré et architecturé, code sur go ; 1.2.0 toujours à uploader~~ dépassé (15 h : codé)

- **Mesure UV faite (ETUDE § 21, Fable, lecture seule, rien posé)** : corps vanilla = framework UV
  3.2.1 = Solo = Songbird = corps masculins (même mise à plat, peau en u > 0,22) ; **bras UV = bande
  u < 0,22 de la texture du corps** (G en haut, D en bas), **bras VTK = mise à plat vanilla dans
  leur propre texture** ; Angel met ses pieds et chevilles dans la bande (chunks 6-7, 24 % de sa
  peau), jamais peints par les textures VTK.
- **Architecture retenue (ETUDE § 21, fin)** : une texture UV → coques corps + bras G + bras D (+
  FPP) ; bras acceptés seulement si la mise à plat du bras actif est celle de la famille (u max ≤
  0,22 = bras UV) ; corps Angel sous texture UV = chunks 6-7 masqués ; aucune conversion ni
  ré-encodage dans la première version (BC7 = 166 s par 8K, mesuré). Conversion des bras = chantier
  optionnel plus tard.
- **Devis à son go** : une séance de code (`core.py` : `TARGET_BY_TEX` → liste, détection de la mise
  à plat des bras depuis le JSON déjà sérialisé, masque des chunks de bande et des chunks non-peau,
  journal) + non-régression 488/488 + builds CLI sur deux arbres factices (Solo + framework + bras
  UV ; Angel) avec les 5 tatouages UV de `dl\uv\`. Puis **banc en jeu à lui** : Solo 2.0 + framework
  3.2.1 + Solo Arms UV posés (Angel parqué), créateur : Kala Sleeve 1 (manches seules), Bedellia
  (corps + bras), FPP, miroir ; puis Angel + Bedellia (torse seul, pieds nus).
- **Deux pièges trouvés, hors UV, à coder dans le même lot** : (1) `shell()` convertit tous les
  matériaux : sur Songbird Body le tatouage couvrirait les plaques cyber (masquer les chunks
  non-peau de l'apparence) ; (2) les `.app` de Solo 2.0 ne se sérialisent pas avec le CLI 9.1.0
  (`castShadows` Bool) : `fpp_torso_mask()` retombe sur le masque vanilla (`except` lu), le build
  passe ; le vrai masque FPP de Solo = point de QA au banc.
- Jetable sur le poste : `C:\__DEV\cyberpunk\ink_flow\dl\uv\` (archives, `x\` sérialisé, `png\`,
  `reenc\` ≈ 1 Go).
- Reste inchangé : 1.2.0 à uploader (bloc suivant), opacité > 1,0 corrigée non rebâtie, QA opacité
  annoncée.

## ~~État (2026-11-04) : 1.2.0 = tableau des corps détectés + opacité par tatouage, prête~~ dépassé (04/11, 13 h : mesure UV)

- **1.2.0 bâtie et commitée** (ETUDE § 20) : cadre « Body meshes in use » (Female V / Male V × Body
  / Arms / Head), colonne **Opacity** par tatouage (catalogue ; vide = **Default opacity**). Exe
  `4e3f15d1…9bb6`, zip `releases\Ink_Flow_Builder-1.2.0.zip` `3e1f13f9…6a46`. Non-régression 488/488
  contre la 1.1.0. **À lui** : upload Nexus (1.1.0 en ancienne version, champ version 1.2.0), coller
  de `NEXUS.md` les étapes 1 et 3, le dépannage et le changelog 1.2.0, refaire la capture de la
  fenêtre, poster le **sticky 1.2.0** de `NEXUS_POSTS.md` (il remercie le demandeur de l'opacité).
  1.1.0 uploadée par lui (sa réponse du 04/11). ~~Tags : seul `v1.0.0` existe~~ posés et poussés sur
  son go (04/11) : `v1.0.1` = `d86e5ab`, `v1.1.0` = `546200f`, `v1.2.0` = commit du sticky 1.2.0
  (dernier commit de chaque version, comme `v1.0.0` = `dcf165a`). Réponses individuelles du 02/11
  retirées de `NEXUS_POSTS.md` à sa demande (postées, historique git).
- **Opacité > 1,0 par tatouage (04/11, retour du demandeur)** : colonne bornée à 1,0, réglage
  général non ; corrigé dans le code (0,1-2,0 partout, ETUDE § 20, fin), **non rebâti** (sa décision
  : part avec la prochaine version). Réponse au demandeur : en attendant, l'opacité générale à 1,5
  marche, la par-tatouage viendra.
- **Point de QA annoncé** : une coque à opacité propre rend comme le réglage général à la même
  valeur (même champ `DiffuseAlpha`), jamais vu en jeu ; à regarder au créateur avec deux tatouages
  à 0,5 et 1,0.
- **Prochaine séance = support UV** (sa décision du 04/11 ; Fable, mesure et architecture). Cadrage
  relu, rien mesuré : (a) **moteur** : `fullbody_overlay_d01.xbm` (`KNOWN_OTHER`, « not supported
  yet ») est UNE texture pour corps + bras, alors que `TARGET_BY_TEX` mappe une texture vers une
  seule cible : passer à « une texture, plusieurs coques » ; masculin `ma_fullbody_overlay_d01`,
  tête `wa_head_overlay_d01` (Garden Bloom) ; (b) **coque** : la piste A règle la mise à plat UV par
  construction (copie du corps UV actif, ETUDE § 8), MAIS le framework UV 3.2.1 branche le calque
  par une chaîne de `.mi` (§ 2) : si le maillage UV a des matériaux externes, `shell()` le refuse
  aujourd'hui (« external materials ») ; (c) **mélange** : tatouage UV sur corps VTK (Angel) = mises
  à plat différentes, à refuser proprement ou à convertir (§ 11, question « conversion UV ↔ VTK ») ;
  (d) **banc** : il faut un corps UV en jeu (Solo 2.0, UV 3.2.1, bras Songbird UV sont dans
  `3_Bodies\V's Body.zip`). **Premier geste** : dépaqueter UV 3.2.1 + Solo, lire leurs matériaux
  (locaux / externes) et comparer les UV des corps vanilla / Solo / Angel, avant une ligne de code.
- Ensuite : tête vanilla, tête du V masculin, miroir / FPP / photo du V masculin (bloc du 03/11
  ci-dessous, (1)-(3)).

## ~~État (2026-11-03, 20 h 30) : 1.1.0 = V masculin (vanilla + Gymfiend) + ré-encodage des mips tronqués, prête~~ dépassé (04/11, 1.2.0)

- **1.1.0 bâtie et commitée** (ETUDE § 19) : V masculin (table `m_*`, `inkflow_pma` sous `male:`,
  pas de suiveur FPP), ré-encodage WolvenKit des seules textures à chaîne de mips tronquée. Exe
  `24434274…5c05`, zip `releases\Ink_Flow_Builder-1.1.0.zip` `43f0f655…6427`. Non-régression
  féminine 500/500. **À lui** : upload Nexus (1.0.1 en ancienne version), coller `NEXUS.md` (résumé,
  What works with what 1.1.0, changelog), tag `v1.1.0` sur go.
- **QA validée par lui au créateur** (nouvelle partie) : V masculin corps vanilla puis Gymfiend VTK
  1.4.3 + MV Head (Kala Japanese V2 masculin propre après ré-encodage) ; V féminine inchangée (tout
  bon sauf têtes sur tête vanilla).
- **Jeu** : remis par lui aux piles 1-2 ; tout ce que j'avais posé retiré
  (`tools\qa_2026-11-03\game_pose.py remove`, 20 h 15). Gymfiend et MV Head dépaquetés dans
  `C:\__DEV\cyberpunk\ink_flow\dl\6423_*`.
- **Prochaine séance (sa demande)** : (1) **tête vanilla** : la coque de tête ne s'affiche pas sur
  tête vanilla (Kala head, Finn, V féminine, créateur ; déjà vu § 17) ; vérifier d'abord qu'elle est
  toujours présente sur Angel + tête VTK HD ; (2) **tête du V masculin** : pack visage `FACE
  TATTOOS-7414-V2-KALA-MALEV-VTK` + Kala Faded Face dans `3_Bodies\__RAM`, sur Gymfiend + MV Head ;
  (3) miroir / FPP / photo du V masculin quand il aura une sauvegarde.
- Idées notées, non tranchées : option de test « forcer un tatouage sur l'autre genre » (patrons UV
  femme / homme non comparés) ; garder le BC7 après ré-encodage (encodeur à trouver) ; Hyst EBB
  (4654) à passer au moteur.
- Plantage à la sortie du 03/11 18 h 33 (DEP après déchargement de RED4ext, 1 sortie sur 5) : hors
  Ink Flow ; candidat non prouvé audioware 1.10.1-rc.0.

## ~~État (2026-11-02, 18 h 30) : QA vanilla validée, 1.0.1 publiable, page Nexus récrite dans `NEXUS.md`~~ dépassé (03/11, 1.1.0)

- **Dans le jeu** : Angel + refits + 4 têtes VTK + build Ink Flow corrigé de 17 h 28 (`a6fd24c8…`, 9
  archives), remis à 18 h 15 après la QA vanilla. **Sonde retirée** (sa décision), source dans
  `tools\probe\` pour les prochains corps ; Redscript 0.5.32 laissé en place (prérequis d'ArchiveXL,
  il ne l'avait pas). Fichiers macOS `engine\tools\scc`, `libscc_lib.dylib` : à lui de les
  supprimer.
- **Prouvé (ETUDE § 18, passage 3)** : corps vanilla pur + correctif `linkController` : **QA validée
  par lui sur deux sauvegardes et en nouvelle partie** (reprise des tatouages posés sur Angel,
  miroir, FPP, photo) ; sonde : 0 échec, 3 coques FPP attachées. Le Confirm mort du § 17 était ce
  défaut. Build gardé `C:\__DEV\cyberpunk\ink_flow\builds\vanilla_link_qa\`.
- **Exe 1.0.1 inchangé** (`f32d59bc…7109`, zip `42fa8310…4ed2` dans `releases\`) : rien à rebâtir,
  le code n'a pas bougé depuis 18 h 10. **À lui : upload Nexus** (zip, SHA-256 dans la description
  du fichier, 1.0.0 en ancienne version, champ version 1.0.1), **coller `NEXUS.md`** (résumé,
  description, changelog : récrits sur SA page publiée, lue par l'API ; détail des changements en
  tête du fichier), captures listées en fin de `NEXUS.md`, réponses de `NEXUS_POSTS.md` (EBBRB ×3 :
  relire la réponse, elle doit maintenant pointer la ligne Body mesh et le dépannage de la page),
  puis **tag `v1.0.1`** sur un go.
- **Ce qui reste théorique, dit tel quel sur la page** : EBBRB (accepté par le builder, § 17, jamais
  vu rendu) ; autres corps VTK = critère du builder (`shell()` : matériaux locaux, apparence de peau
  standard), pas une liste testée ; un corps non mis à jour pour 2.5 reste cassé sous Ink Flow
  (coques = copies de ses maillages) ; bras cybernétique jamais testé ; hypothèse REDmod / MO2 des
  trois EBBRB attend un `build.log`.
- Scripts : `tools\qa_2026-11-02\build_pure_link.py` (build du passage 3),
  `tools\probe\logs\2026-11-02_181554` (journaux, hors git). `gen\nexus_36814_desc.bbcode` = sa page
  telle que publiée (poste).
- **Son plan avant l'upload (18 h 35)** : test « premier utilisateur » : désinstaller le runtime
  .NET 10 et `%LOCALAPPDATA%\InkFlow`, exe 1.0.1 vierge, **corps vanilla** (Angel + têtes à parquer
  : moi, sur son go, jeu fermé), 2-3 tatouages, Build, Install, captures du processus et du résultat
  en jeu ; puis la même chose sur **Angel**. C'est la première exécution réelle du bouton Install
  .NET Runtime 10 (jamais joué sur ce poste : ETUDE § 18). Effets à savoir :
  `%LOCALAPPDATA%\InkFlow` emporte le catalogue (noms édités), la config (liste des archives,
  slots), le cache (build suivant ≈ 2 min au lieu de 20 s), WolvenKit (retéléchargé, 45 Mo) et
  `backup\` (anciens Ink_Flow ; le build de 17 h 28 reste dans `C:\__DEV\cyberpunk\ink_flow\…\out`
  et dans le jeu).

## ~~État (2026-11-02, 18 h 15) : FPP corrigée et prouvée sur Angel, .NET installable depuis le builder, 1.0.1 prête sauf QA vanilla~~ dépassé (18 h 30)

- **Dans le jeu** : Angel + refits + 4 têtes VTK, **build Ink Flow corrigé** (`linkController`, 170
  Mo, 530 fichiers, bâti à 17 h 28 par `tools\probe\angel_build.py` sur sa config, 9 slots) ;
  l'ancien dans `%LOCALAPPDATA%\InkFlow\backup\2026-11-02_172832`. **Redscript 0.5.32 posé** (4
  fichiers, depuis le zip de `1_Core\__WOLVENKIT`) et **sonde `r6\scripts\InkFlow_Probe\`** encore
  posée : `pose_probe.py remove` sur son go (elle écrit ≈ 4 000 lignes par session dans
  `cyber_engine_tweaks\gamelog.log`). Fichiers macOS `engine\tools\scc`, `libscc_lib.dylib` :
  inoffensifs, à lui de les supprimer.
- **Prouvé (ETUDE § 18)** : la première personne de la 1.0.0 n'a jamais appliqué ses coques FPP
  (`linkController` à 0 sur le maître, gabarit du toolkit) : trous et démarcation mobile sur les
  bras en FPP, vus par lui à 17 h 15. Avec `linkController = 1` : coques FPP attachées et chargées
  (journal), **QA validée par lui (17 h 45) : bras corrects en FPP depuis le miroir, mode photo
  bon**.
- **Exe 1.0.1** `C:\__DEV\cyberpunk\ink_flow\exe\dist\InkFlowBuilder.exe` SHA-256 `f32d59bc…7109`,
  zip `InkFlowBuilder-1.0.1.zip` SHA-256 `42fa8310…4ed2` (copie `releases\`) : correctif FPP +
  bouton **Install .NET Runtime 10** (installeur Microsoft épinglé, silencieux ; l'installation
  elle-même non jouée sur ce poste) + ordre de chargement / bras vanilla / Body mesh / Scan /
  build.log du matin. README et `NEXUS.md` à jour (changelog).
- **Avant l'upload, à trancher par lui** : (a) rejouer le **corps vanilla** (Angel et têtes parqués,
  build vanilla, miroir, Confirm, FPP) avec le correctif et la sonde : le Confirm mort du § 17 a été
  mesuré avec `linkController = 0`, il peut avoir disparu ou non ; sans ça, « or the vanilla body »
  reste une promesse non prouvée ; ou (b) publier 1.0.1 en l'état (Angel / EBBRB prouvés par la
  mesure, FPP réparée) et traiter le vanilla ensuite.
- **Reste non prouvé** : hypothèse REDmod / MO2 des trois EBBRB (attend un `build.log`) ; bras
  cybernétique (lames Mantis) sur nos coques à masque plein (sa question, jamais testé) ; le dump de
  la sonde le dirait.
- **Prérequis Nexus (sa question de 18 h)** : Ink Flow n'exige que **ArchiveXL** (+ RED4ext) ;
  Redscript recommandé (scripts d'ArchiveXL), Codeware et TweakXL inutiles ; Angel = « développé
  avec », pas requis. Page Nexus à sa main.
- Sonde et scripts de la séance versionnés dans **`tools\probe\`**
  (`InkFlow_Probe\InkFlow_Probe.reds`, `pose_probe.py`, `angel_build.py`) ;
  `tools\probe\logs\<date>\` = journaux des deux passages (2 × 1,2 Mo), gardés sur le poste,
  **exclus du dépôt** avec `releases\` et les zips (`.gitignore`, 18 h 20).

## ~~État (2026-11-02, 17 h) : 1.0.1 NON publiable telle quelle, corps vanilla cassé au miroir, sonde à écrire~~ dépassé (18 h 15)

- **Jeu remis dans l'état d'hier soir** (sa décision, 16 h 50) : Angel + refits + 4 têtes VTK remis
  depuis le parc, **build bâti sur Angel reposé** (159 Mo, celui de la QA validée). Variantes du
  jour dans `%LOCALAPPDATA%\InkFlow\backup\2026-11-02_*` et
  `C:\__DEV\cyberpunk\ink_flow\gen\t101\out*`. Sa config du builder pointe sur `3_Bodies\__InkFlow`
  (21 archives).
- **Ce que la QA du jour a prouvé (ETUDE § 17, tableau)** : la recette fonctionne sur le corps
  vanilla **sans première personne** (créateur, miroir, Confirm, photo) ; **les coques FPP de bras
  bâties sur le vanilla cassent l'attache à chaud au miroir** et laissent le créateur sans Confirm ;
  sans FPP, les coques TPP de bras sont rendues en FPP et décalées sur les bras FPP vanilla ; la
  coque de tête vanilla ne s'affiche pas en nouvelle partie. Matériaux preload : hors de cause.
  Cause exacte : **non trouvée**.
- **Conséquence pour 1.0.1** : l'exe `fc33b615…` bâti à 14 h ne contient pas le changement «
  matériaux embarqués » de 16 h (neutre) et, surtout, un joueur **sans mod de corps** aurait un
  miroir cassé au lieu d'une erreur au build : **ne pas uploader** avant d'avoir, au choix de
  Hell_Kaiser : (a) la vraie cause (sonde), ou (b) le garde-fou « corps = jeu de base ⇒ pas de
  coques FPP + avertissement » (5 lignes dans `run_build`, README). Les correctifs REDmod / MO2 /
  Body mesh / Scan / build.log restent bons.
- ~~**Prochaine session = la sonde**~~ faite le 02/11 à 17 h-18 h (ETUDE § 18, `tools\probe\`) (sa
  décision : « une sonde, un logger complet, nouvelle session ») : Redscript + Codeware dans
  `r6\scripts\InkFlow_Probe\`, journal des `Resource/Load|Ready|Failed` sur `inkflow\…`, des
  événements du créateur et des composants attachés au joueur ; plan détaillé ETUDE § 17, dernier
  paragraphe. Codeware 1.21.2 est dans son jeu ; Redscript : vérifier `red4ext\plugins`
  (`r6\scripts` n'existe pas encore). Le script de Hyst
  (`dl\4654\ebbrb\r6\scripts\VTK_Hyst_CC_Edit`) est un bon modèle d'accroche `Resource/Load`.
- Scripts de la séance, versionnés dans **`tools\qa_2026-11-02\`** (chemins en dur du poste) :
  `game_step.py` (isolate / install / angelbuild / embed / nofpp / fpparms / fppbody / restore),
  `build_pure*.py`, `build_fpp_bisect.py`, `vanilla_in_game.py`, `order_test.py`, `vanilla_test.py`,
  `ebbrb_test.py`, `gui_capture_101.py`.
- **Durée du déverrouillage** : `UNLOCK_TTL_SECONDS` dans les deux hooks installés (lignes 67 et 85)
  et dans `pipeline\hooks\` ; à lui (fichiers de règles).

## ~~État (2026-11-02, 15 h) : 1.0.1 bâtie et prouvée hors jeu, upload et QA vanilla à lui~~ dépassé (17 h)

- **1.0.1 livrée sur son go** (ETUDE § 17, « Livré ») : ordre de chargement réel (`modlist.txt`,
  REDmod, ordre MO2), bras vanilla, ligne **Body mesh** dans la fenêtre, bouton **Scan game
  folder…**, `build.log`, conflits sur REDmod aussi, CLI `--from-game`. Exe
  `C:\__DEV\cyberpunk\ink_flow\exe\dist\InkFlowBuilder.exe` SHA-256 `fc33b615…9805` ; zip
  `InkFlowBuilder-1.0.1.zip` SHA-256 `8b38f547…`, copie dans `releases\`.
- **Prouvé** : tests d'ordre A → H ; build CLI complet sur corps vanilla (157 fichiers, 71,1 Mo,
  coque de bras vérifiée) ; exe figé sur Angel = 1.0.0 au bit près hors index (157 fichiers, 150 347
  776 o) ; capture `builder\tests\gui_main_2026-11-02.png`. **Jeu non touché** (son Ink Flow de la
  veille reste posé).
- **Dans le jeu depuis 14 h 37 (sa demande, déverrouillage `WRITE_UNLOCK.txt` sur le dossier du jeu)
  : build 1.0.1 sur le CORPS VANILLA** : Angel parqué (`006_Angel_Body.archive`, `.xl`, refits →
  `C:\__DEV\cyberpunk\ink_flow\parked\2026-11-02_angel\`), têtes VTK HD laissées (son choix après
  coup : « ça permet de tester le corps vanilla avec la seule tête VTK ») ; 21 archives de
  `3_Bodies\__InkFlow\` (sa config `files` repointée dessus, les anciens chemins étaient morts), 9
  slots, miroir, FPP ; corps, bras, bras FPP = jeu de base, tête =
  `006_VTK_Vanilla_HD_Head_xBaebsae` ; **530 fichiers, 82,6 Mo, 139 s, SHA-256 `b7330a9b…`** ;
  l'ancien Ink Flow (Angel) dans `%LOCALAPPDATA%\InkFlow\backup\2026-11-02_143536`. Script :
  scratchpad `vanilla_in_game.py`. **Retour à Angel** = remettre les 3 fichiers parqués, Build,
  Install (formule ou `WRITE_UNLOCK.txt`).
- **À lui** : (1) QA **corps vanilla en jeu** : miroir, bras nus : tatouage de bras visible et collé
  à la peau (Kala Japanese Arm L/R, Samurai) ; corps aussi ; FPP tête baissée ; le personnage garde
  ses slots. (2) Upload Nexus 1.0.1 (zip + SHA-256, changelog dans `NEXUS.md`) **après** relecture
  de `NEXUS.md` contre SA description publiée (il l'a altérée : à relire par moi, il doit me donner
  l'URL de la page). (3) Poster les réponses de `NEXUS_POSTS.md` (EBBRB ×3, 0xVyper). (4) Tag
  `v1.0.1` après l'upload, sur un go.
- **Reste non prouvé** : l'hypothèse REDmod / MO2 pour les trois EBBRB (attend un `build.log`) ; le
  rendu d'une coque vanilla en jeu. Si un `build.log` EBBRB dit `Body : 05_Hyst_Refit…` et que rien
  ne s'affiche quand même, l'hypothèse tombe : chercher alors côté redscript Hyst
  (`VTK_Hyst_CC_Edit`) ou `.app` EBBRB.
- Jetables sur le poste : `dl\4654\ebbrb\` (fixture EBBRB, 178 Mo), `gen\t101\` (arbre factice
  vanilla, cache, build de 71 Mo : 292 Mo), `gen\vanilla_test\`, `gen\ebbrb_test\`. Scripts de test
  dans le scratchpad de la session (`vanilla_test.py`, `ebbrb_test.py`, `order_test.py`,
  `gui_capture_101.py`) : non versionnés.

## ~~État (2026-11-02, 14 h 30) : 1.0.0 publiée sur Nexus, premiers retours, correctifs 1.0.1 proposés~~ remplacé (15 h)

- **Publiée** par lui dans la nuit du 01 au 02/11 (page Nexus en ligne, 15 messages le matin). Son
  jeu purgé le 02/11 : 9 archives (Angel, refits vanilla, têtes VTK HD, Ink Flow de la veille),
  marche.
- **Retours** : trois utilisateurs **EBBRB** (Lorasyl, Bransburk, cybercock2067) : build et install
  sans erreur, slots visibles, **rien sur le corps** ; TheQueenEmzz : .NET 10 non détecté (il a
  répondu : runtime x64, capture ajoutée) ; Brandy1123 : 2.3x non fonctionnel (attendu) ; deux
  demandes de V masculin ; 0xVyper : tout dynamique sans rebuild.
- **Mesuré (ETUDE § 17)** : corps **vanilla pur** : corps et tête passent, **les bras sont refusés**
  par `shell()` (matériaux en `preloadLocalMaterialInstances`) : le README et la page Nexus mentent
  sur « or the vanilla body ». **EBBRB 5.0.0** (Nexus 4654, téléchargé, `dl\4654\ebbrb\`) : le
  moteur accepte tout (corps 91 371 sommets, 12 matériaux, même boîte qu'Angel) : rien à corriger
  côté recette.
- **Hypothèse pour les trois EBBRB (non prouvée)** : le builder n'a pas vu le corps (REDmod `mods\`,
  MO2 hors VFS, ou `modlist.txt`) et a bâti une coque **vanilla** (4 641 sommets) sous un corps à 91
  k sommets : invisible. Le journal de build dit `Body : base game` ; aucun fichier journal n'est
  écrit. **À demander aux trois** : la ligne « 2. active meshes », le gestionnaire de mods (réponses
  rédigées).
- **Correctifs 1.0.1 proposés (sur son go)** : (a) `shell()` accepte les matériaux preload ; (b)
  `find_owner` : `modlist.txt`, `archive\pc\mod`, REDmod, jeu de base ; (c) corps résolu affiché
  dans la fenêtre, rouge si « base game » ; (d) `build.log` dans `%LOCALAPPDATA%\InkFlow` ; (e)
  README et page Nexus (MO2, REDmod, bras vanilla, build.log). (f) bouton Scan game folder : lot à
  part.
- QA à prévoir après (a) : **corps vanilla** (retirer Angel et les têtes de son jeu, bâtir, bras
  tatoués visibles), puis remettre Angel et rebâtir.
- Non versionnés dans le projet : `InkFlowBuilder-1.0.0.zip`, `releases\` (captures 1, 2, 4 de 0 h
  51, Nexus de 9 h). **Tag `v1.0.0` absent** (local et GitHub, mesuré à 14 h 30) : à poser sur
  `dcf165a` avec le commit des docs, sur son go.

## ~~État (2026-11-02, 0 h 15) : QA FPP validée, interface verrouillée pendant le build, upload à lui~~ remplacé (14 h 30)

- **QA FPP de Hell_Kaiser (02/11, vers 0 h) : validée.** 9 slots, tous ses tatouages chargés depuis
  son pack V's Body : (a) créateur, les 9 slots superposables apparaissent bien ; (b) tatouages des
  bras vus au miroir puis en première personne (tête baissée) ; (d) posés au miroir, suivis en FPP ;
  (e) mode photo OK ; **pas de bras plus clair**. (c) rien qui flotte : non signalé.
- **Sa demande d'interface (même message)** : les boutons restaient cliquables pendant le build.
  Livré : fenêtre en lecture seule pendant le build (tous les contrôles ttk grisés, la liste ignore
  clics et touches), le bouton Build devient **Cancel** ; fermer la fenêtre = « annuler et quitter ?
  ». Moteur : `core.Cancelled` (distincte de `BuildError`, que `fpp_torso_mask` avale), `Cli.run`
  tue WolvenKit.
- **Preuves (GUI pilotée, maison `exe\home`)** : Cancel pendant le `deserialize` :
  `WolvenKit.CLI.exe` vivant à l'appui, absent 1 s après, sortie vide (archive partielle retirée),
  bouton « Cancelling… » grisé, 13 s ; 24 contrôles grisés, seul Cancel actif ; build complet
  ensuite : 157 fichiers, 150 347 776 o, identique. Exe figé rebâti à 0 h 09 (SHA-256
  `7df14236…3cb7775`), autotest : 157 fichiers, 150 347 776 o, 145 s. Zip `c1e354ae…5aa02a` recopié
  sur ses deux copies (racine du projet et `releases\`).
- ~~**Attend lui** : boîte Permissions de 20279, relecture de `NEXUS.md`, captures (sa capture
  `releases\Ink Flow Interface.png` de 0 h 05 montre la fenêtre au repos : le verrou n'y change
  rien), upload Nexus (zip + SHA-256 de l'exe), puis tag `v1.0.0`.~~ Publié dans la nuit (état du
  02/11, 14 h 30).

## ~~État (2026-11-01, 23 h 45) : 1.0.0 + première personne bâtie, QA FPP attendue avant l'upload~~ remplacé (0 h 15)

- **Première personne (décision de Hell_Kaiser, 23 h : « ajouter la FPP avant l'upload »)** : livrée
  dans le builder (ETUDE § 16 : suiveur caché par slot lié au sélecteur, coque du corps masquée
  comme le torse FPP actif, copies des bras FPP, groupe `FPP_Body` seul ; case « First person »
  cochée par défaut, `--no-fpp` en CLI). Build CLI : 150,3 Mo, 157 fichiers (+ 10,7 Mo), structure
  contrôlée dépaquetée. **Jamais vue en jeu** : la pose et la QA sont à lui.
- **QA FPP (à lui, sauvegarde avec miroir, bras nus)** : exe 1.0.0 rebâti → Build → Install (jeu
  fermé), puis (a) créateur inchangé (ni double décal ni scintillement des bras) ; (b) en jeu, bras
  et corps vus de V tatoués comme au miroir ; (c) rien qui flotte près de la caméra ; (d) changer le
  slot au miroir ou au charcudoc : la FPP suit ; (e) mode photo inchangé. Replis si (a) ou (b) rate
  : ETUDE § 16, fin.
- **Exe 1.0.0 rebâti à 23 h 35** : `exe\dist\InkFlowBuilder.exe` 11,4 Mo, SHA-256 `b1fd72db…68075`
  (autotest figé : 157 fichiers, 150 347 776 o, 124 s, même résultat que le CLI) ; zip
  `exe\dist\InkFlowBuilder-1.0.0.zip` 11,7 Mo, SHA-256 `c0b18ba7…4b027`, **recopié sur sa copie dans
  le dossier du projet** (celle de 21 h 19 n'avait pas la FPP). README, `NEXUS.md` (limite FPP
  retirée, résumé 247 caractères, étape 4) et ETUDE § 16 à jour ; le tout commité.
- **`publish\` renommé `releases\` par lui (23 h 26, hors git)** : `Ink_Flow_Builder-1.0.0.zip` (sa
  copie de 21 h 19, **remplacée par le zip avec FPP** à 23 h 45), `main.png`, `Ink Flow
  Interface.png` (22 h 54 : fenêtre du builder **sans** la case « First person », capture 1 à
  refaire).

- **Test de l'exe vierge par Hell_Kaiser (22 h)** : `%LOCALAPPDATA%\InkFlow` supprimé, relance : le
  jeu est retrouvé seul (registre Steam + `libraryfolders.vdf`, `env.find_game_candidates`, aucune
  mémoire) ; **bouton Download OK** (WolvenKit dans `InkFlow\wolvenkit`, lié) ; build à faire par
  lui.
- **Slots, tranché par lui (22 h)** : réglage du **builder** (case Slots, 1 à 9, défaut 2), rien
  dans Mod Settings (ArchiveXL fusionne les options du créateur au chargement). Plafond 9 = index
  1041 à 1049 libres sous `body_tattoo` (1040), `fpp_body_tattoo` à 1050. Résumé Nexus, étape 4 de
  la page et README reformulés (« Ink 1 to Ink 9, you choose how many ») : **non commités**.
- Déposés par lui dans le dossier du projet : `InkFlowBuilder-1.0.0.zip` (copie de l'upload, 11,7
  Mo, non versionné, à ajouter au `.gitignore` ou à laisser hors git) et `publish\main.jpg` (22 h
  35, 626 Ko : capture pour la page Nexus ?). À trancher par lui : versionner `publish\` ou non.
- ~~**Exe 1.0.0 : `C:\__DEV\cyberpunk\ink_flow\exe\dist\InkFlowBuilder.exe`** (11,4 Mo, SHA-256
  `13c14eaa…bbc9b9`) ; **zip d'upload `exe\dist\InkFlowBuilder-1.0.0.zip`** (11,7 Mo, exe + README +
  LICENSE, SHA-256 `35b5bf52…40daf6`)~~ remplacés à 23 h 35 par la 1.0.0 avec FPP (SHA-256
  ci-dessus). Preuve : exe figé en mode `INKFLOW_AUTOTEST` (maison `exe\home`, cache chaud) : 18
  tatouages, 106 fichiers, 139 599 872 o en 120 s, **0 octet différent hors index** contre la v0.3b
  posée dans le jeu (536 dans l'index = horodatages), `.xl` identique.
- **Gabarits (décision de Hell_Kaiser, 21 h 15 : garder + créditer)** : le toolkit 20279 se présente
  comme « a template resource … template source files for your WolvenKit project » (description
  Nexus, lue par l'API ; la boîte Permissions n'est pas lisible par l'API : **à lire par lui sur la
  page**) ; en-têtes WolvenKit nettoyés (plus de chemin `C:\__DEV`), localisation = squelette neutre
  (`placeholder`, plus rien de Kylin). Crédit thrasherpass dans le README et la page Nexus.
- README : rebâtir après un changement de corps, slot conservé, comment le corps est choisi, limites
  (UV, FPP, morph au charcudoc non coché), crédits. **Dans le jeu : build 0.4.0 de 20 h 03
  inchangé** (même contenu que la 1.0.0 au bit près hors index : rien à reposer).
- Brouillon de la page Nexus : **`NEXUS.md`** (racine du projet, anglais : nom, résumé, description
  BBCode, permissions, crédits, fichier à envoyer, captures à prendre).

## Où sont les choses

- Projet (OneDrive, dépôt git) : `cp:__DEV\Projects\Ink Flow\` : `ETUDE.md` (§ 1-15), `NEXUS.md`
  (page Nexus), `builder\` (exe : `inkflow\`, `README.md`, `LICENSE`, `build_exe.ps1`),
  `tools\inkflow_build.py` (générateur **v0.3**, figé), `tools\rdar.py`, `tools\build_canari.py`
  (figé), `tools\nexus_dl.py`, `templates\` (gabarits JSON neutralisés), `canari\` (v1-v5, hors
  git).
- Jetable (poste) : `C:\__DEV\cyberpunk\ink_flow\` : `in\` (17 archives VTK de test tirées de
  `3_Bodies\V's Body.zip` + catalogue `inkflow_slugs.json`), `gen\` (`mesh`, `tex`, `pack`, `out`,
  `verify`, `head_src` = tête HD extraite), `src\` (copies d'archives du jeu, dont les trois
  `*_HD_Head*`), `builds\v0\`, `v0.1\`, **`v0.2b\`** (archives posées précédemment),
  `canari_retire\`.
- Jeu : `archive\pc\mod\Ink_Flow.archive` + `.xl` (écriture = `WRITE_UNLOCK.txt` sur
  `archive\pc\mod`, 60 min, ou la formule ; jeu fermé).

## État (2026-11-01, 13 h 15)

- ~~Dans le jeu : v0.2b~~ (posée à 2 h 47, SHA-256 `52833f2e…e3bc3f`, QA validée à 2 h 50) →
  remplacée ; copie dans `builds\v0.2b\`.
- **Dans le jeu : v0.3, posée à 13 h 11** (formule de Hell_Kaiser, jeu fermé, SHA-256 identiques
  `108c324e…` / `.xl f361f55b…`) = v0.2b + **cible tête** (**127,8 Mo, 101 fichiers**, 17 tatouages
  dont Kala Japanese Head = tête seule et Garden Bloom = corps + tête ; `.xl` inchangé). Vérifié
  dépaqueté avant la pose : 22 textures identiques aux sources, coques de tête = copie du maillage
  HD (1 chunk, 27 591 sommets, 62 matériaux → décal), morphtargets de tête (105 cibles) repointés,
  `.app` conformes, switchers à 4 uiSlots (ETUDE § 12). **QA partielle par Hell_Kaiser (14 h) : Kala
  Japanese Head s'affiche bien** (la coque de tête rend, la section corps des infos tête suffit pour
  l'affichage) ; non rapportés : morphs du visage (preset, nez, mâchoire), animation faciale, cumul,
  mode photo.

**QA 2 par Hell_Kaiser (01/11, 16 h-17 h, sauvegarde avancée jusqu'à l'appartement H10 : miroir et
mode photo disponibles)** : Kala Japanese Head **propre** ; c'est un motif de cou, le seul tatouage
de tête VTK de son montage, donc **aucune confirmation visuelle possible des morphs du visage**
(preset, nez, mâchoire : il les a changés, rien à voir sur le cou) ; son avis : la recette est
bonne. **Les slots Ink Flow n'apparaissent pas dans le modificateur du miroir, seulement dans le
créateur de personnage** : c'est voulu par le générateur, qui copie les étiquettes `editTags =
[NewGame, Ripperdoc]` du gabarit vanilla des tatouages (`tools/inkflow_build.py`, `tags`) : comme
les tatouages vanilla, créateur et charcudoc seulement. Pour les montrer au miroir : lire
l'étiquette que porte une option visible au miroir dans un `.inkcharcustomization` vanilla
(maquillage, coiffure) et l'ajouter aux nôtres (option du générateur, `--mirror`, une ligne). Mode
photo : à regarder (tatouage de tête et de corps présents sur V, de face et en gros plan).

## État (2026-11-01, 17 h 15)

- ~~Dans le jeu : v0.3~~ (13 h 11, SHA-256 `108c324e…`, copie `builds\v0.3\`) → remplacée.
- **Dans le jeu : v0.3b, posée à 17 h 11** (son déverrouillage, jeu fermé, SHA-256
  `a30204f80eb93d57…` / `.xl f361f55b…` inchangé ; copie `builds\v0.3b\`) = v0.3 + **`--mirror`**
  (étiquettes `NewGame`, `HairDresser`, `Ripperdoc` sur les 2 sélecteurs et les 54 options, mesuré
  dans `gen\verify\v03b`) + **18e tatouage de test : « Finn Face »**
  (`00_VTK_arcane_finn_tattoo_fem_standalone_head.archive`, Nexus 18402, extrait de `3_Bodies\…zip`
  dans `in\` **sans entrer dans V's Body** : c'est un vrai tatouage de visage, pour juger les morphs
  ; slug `arcane_finn_head`). **139,6 Mo, 106 fichiers**, build 123 s ; vérifié dépaqueté : 106/106,
  texture Finn identique à la source (SHA-256), entrées `inkflow_slot{1,2}_arcane_finn_head_head`.

## État (2026-11-01, 20 h) : builder v0.4, exe bâti et testé

- **Dans le jeu : v0.3b inchangée** (17 h 11, SHA-256 `a30204f8…`), QA 1-3 validées (affichage,
  miroir, mode photo, cumul tête + visage) ; recette VTK corps / bras / tête **validée par
  Hell_Kaiser**.
- **Builder v0.4** dans `builder\` (ETUDE § 14) : moteur `inkflow/core.py` (refonte de
  `tools/inkflow_build.py` v0.3, figé), `env.py`, `gui.py` (Tk), `inkflow_cli.py`, `build_exe.ps1`,
  `README.md`, `LICENSE` (MIT, **titulaire « Hell_Kaiser » à confirmer**), `tests/gui_capture.py` +
  capture. Décisions de Hell_Kaiser (19 h) : **interface Tk native**, **pas de git encore**.
- **`InkFlowBuilder.exe` 0.4.0 : `C:\__DEV\cyberpunk\ink_flow\exe\dist\InkFlowBuilder.exe`** (11,4
  Mo, PyInstaller un fichier, SHA-256 dans la sortie de `build_exe.ps1`) ; venv dans `exe\venv`,
  maison de test `exe\home` (`INKFLOW_HOME`, config + catalogue + WolvenKit téléchargé + cache 516
  Mo). **Preuves** : moteur CLI = 106/106 entrées identiques à la v0.3b, même taille ; **exe figé,
  cache vide, mode `INKFLOW_AUTOTEST` : 18 tatouages, 139,6 Mo, 106 fichiers identiques, 201 s**
  avec le WolvenKit qu'il a téléchargé lui-même (45 Mo, SHA-256 épinglée, vérifiée sur deux
  téléchargements) ; fenêtre capturée (`builder\tests\gui_main_2026-11-01.png`). Non testé sans clic
  : bouton Install (déplacement des archives VTK en conflit, sauvegarde), dialogue des doublons de
  noms, édition des noms (logique simple, à prendre en main par lui).
- L'exe n'est **pas** copié dans OneDrive (binaire de 11 Mo, se rebâtit en 20 s) ; à sa demande
  seulement.

## État (2026-11-01, 21 h) : exe pris en main, 1.0 décidée, dépôt git ouvert

- **QA 4 de l'exe par Hell_Kaiser (20 h-20 h 30) : validée.** Game folder détecté seul ; Browse vers
  un autre dossier → « CLI WolvenKit non détecté », mappé à la main (le bouton Download n'a pas été
  essayé) ; `in\` ajouté (catalogue : 20 entrées importées de `inkflow_slugs.json`) ; un nom édité à
  la main ; Build ; Install → popup de succès (`Ink_Flow.archive` + `.xl` dans `archive\pc\mod`,
  anciens dans `%LOCALAPPDATA%\InkFlow\backup\2026-11-01_200343`). En jeu : miroir OK, le nom édité
  s'affiche, **le slot actif du personnage a gardé son tatouage** après le build frais (slug stable
  par empreinte de contenu : un joueur qui ajoute des tatouages ne perd pas ses réglages). Un seul
  écart vu : rien.
- **Dans le jeu : build de l'exe 0.4.0** (20 h 03), contenu = v0.3b (18 tatouages, 2 slots, miroir,
  opacité 1,0).
- **Décisions de Hell_Kaiser (21 h)** : **livrer une 1.0 à ce stade** ; **dépôt git `ink-flow`,
  ouvert** (« tout cœur ouvert, les gens doivent pouvoir contrôler ce qu'on a fait ») : initialisé
  **en local** à 21 h 05 à la racine du projet (branche `main`, committer Hell_Kaiser, auteur Claude
  Fable 5.1), contenu = builder + tools + templates + ETUDE, LOG, HANDOVER ; `canari\` exclu
  (textures tierces). ~~Aucun dépôt GitHub créé~~ **En ligne à 21 h 25 sur son go :
  `https://github.com/doublescotch/ink-flow`, public, branche `master`** (règle : tous ses dépôts).
- **Comment l'exe choisit le corps** (question de Hell_Kaiser, réponse lue dans `core.py`,
  `find_owner`) : pour chaque cible (corps, bras G/D, tête), il cherche dans `archive\pc\mod` la
  **première archive dans l'ordre de chargement du jeu** (alphabétique, insensible à la casse) qui
  livre le maillage vanilla (`t0_000_pwa_base__full.mesh`…), sinon le jeu de base ; la coque est une
  copie de CE maillage. Donc même choix que le jeu si plusieurs corps sont chargés ; le journal de
  build l'écrit (`Body : 006_Angel_Body.archive (over …)`). Pas « Angel » en dur : tout corps dont
  le maillage a des matériaux locaux et l'apparence de peau standard passe, sinon erreur «
  unsupported body mod ». Ce qui n'est **pas** supporté : la **famille UV** (texture
  `fullbody_overlay_d01.xbm`, corps Solo), V masculin ~~, FPP~~ (FPP livrée le 01/11 à 23 h 30, §
  16). **Conséquence à écrire dans le README** : changer de corps après un build = rebâtir (la coque
  est une copie de l'ancien corps).

## Prochain geste (1.0)

1. **Avant publication** : ~~(a) `env.py` : test du bouton Download par lui (renommer ou vider
`exe\home\wolvenkit\` ou `%LOCALAPPDATA%\InkFlow\wolvenkit\`, relancer l'exe, cliquer Download : 45
Mo, SHA-256 vérifiée par l'outil)~~ **fait à 22 h, OK** ; ~~(b) README~~ fait (21 h 30) ; ~~(c)
permissions~~ tranché « garder + créditer » (21 h 15), **lui : lire la boîte Permissions de 20279
sur le site** ; ~~(d) version 1.0.0, exe rebâti, SHA-256 notée~~ fait (21 h 18, `13c14eaa…`) ; ~~(e)
dépôt GitHub~~ fait (21 h 25) ; ~~(f) page Nexus~~ brouillon `NEXUS.md` (21 h 25), **à relire par
lui** ; (g) **ses captures** (4 listées dans `NEXUS.md`, second écran) ; (h) **upload Nexus par
lui** (zip + SHA-256 dans la description du fichier), puis tag `v1.0.0` sur le dépôt. **Avant (g) et
(h) : (0) la QA FPP** (bloc « État » ci-dessus) ; l'upload attend son verdict. 2. **Après la 1.0** :
famille UV (corps Solo), icônes dans le créateur, ~~FPP~~ (livrée), V masculin, poids (morphtarget
partagé), morph changé au charcudoc (QA non cochée). 3. ~~Prise en main de l'exe par Hell_Kaiser~~
**faite (QA 4)**. 2. ~~Poser la v0.3~~ **posée à 13 h 11**. 2. **QA v0.3 à lui** (liste complète
ETUDE § 12) ; les points qui tranchent : (b) la coque de tête **suit les morphs** du visage (preset,
nez, mâchoire…) et (a) s'affiche tout court : c'est le seul point non lu de la recette (nos infos
tête sont dans la section **corps** du créateur, le vanilla met les siennes dans la section tête).
Si (a) ou (b) rate : variante = infos tête dans `headCustomizationOptions` (groupes `TPP`,
`character_customization`, `TPP_photomode`) référencées depuis nos switchers du corps ; ≈ 30 lignes.
3. ~~**Décision de Hell_Kaiser (01/11, 16 h) : « on finit Ink Flow après, nouvelle session »** : QA
complète de la tête~~ faite (QA 3) ; ~~**exe + interface**~~ livré (v0.4, 20 h). Reste, à son choix
: **git** (il a dit « pas encore » ; à ouvrir avant toute publication), **icônes** dans le créateur,
**famille UV**, **FPP**, **V masculin**, **poids** (16,4 Mo de morphtarget par tête : morphtarget
partagé par dynamic materials), **morph changé au charcudoc** (point de QA non coché, non bloquant),
**signature de code / faux positifs antivirus** avant Nexus.

## Décisions du 2026-11-01 (gravées ETUDE § 11-12)

- **Nombre de slots = réglage du mod**, défaut 2 (`--slots`) ; champ `group` du catalogue abandonné.
- **Rien dans le sélecteur vanilla** (`--route1` disponible, non par défaut).
- Noms ≤ 20 caractères, sans auteur, dans le catalogue `in\inkflow_slugs.json` (modifiables par lui,
  puis rebâtir) ; limite à remesurer avec 24-26 caractères avant de la monter.
- **Tête = même recette que le corps** (copie du maillage actif en décal + copie de son
  morphtarget), aucun masque de chunk : le maillage HD de tête est tout en peau (mesuré § 12).

## Ouvert (non tranché, non mesuré)

- **Section des infos tête** : corps (choisi, non lu) contre tête (vanilla) ; tranché par la QA
  (a)/(b).
- ~~**FPP** : aucune coque FPP ; non testable sur sa sauvegarde (créateur seul).~~ Livrée le 01/11 à
  23 h 30 (ETUDE § 16) ; **QA en jeu attendue**, points (a)-(e) du bloc « État ».
- **Mode photo / miroir** : groupe `TPP_photomode` de la tête non renseigné par nos groupes.
- **Vêtements** : masques de chunks par nom de composant, jamais testé habillé.
- **Corps UV** : coque à la mise à plat UV, dérivable du corps UV (ETUDE § 5.1) ; aucune surface UV
  sur son montage (§ 10).
- **Couture au cou** : `femv_vtk_headpatch` (xBaebsae) et seamfix d'Angel se dessinent peut-être
  par-dessus la coque de tête ; à voir en QA (f).
- **Bras gauche plus clair** : vu une fois (v0), jamais revu ; non bloquant.
- **Archives d'origine encore dans le jeu** : détectées par nom de fichier seulement (empreintes
  d'index possibles en 0,4 s, non fait). Aucune dans le jeu à 13 h.
- **Hook** : cas 204 (listing WolvenKit d'une archive du jeu pris pour une écriture) consigné, à
  qualifier avec 203 en séance pipeline ; les `.app` vanilla des tatouages faciaux restent non lus.

## Attend Hell_Kaiser

- ~~**Sa QA de la v0.3 en jeu** (liste ETUDE § 12 ; points qui tranchent : la coque de tête
  s'affiche et suit les morphs du visage).~~ Faite le 01/11 à 16 h-17 h (QA 2 ci-dessus) : affichage
  OK, morphs non vérifiables sur son montage, miroir sans nos slots (voulu, à ouvrir sur décision),
  mode photo à regarder.
- ~~**Décision de Hell_Kaiser (01/11, 17 h) : ouvrir le sélecteur au miroir**~~ **fait (v0.3b, 17 h
  11)** : étiquette mesurée sur `female_cco` vanilla
  (`x\van\…\female_cco.inkcharcustomization.json`) : miroir = `HairDresser` (maquillage, cicatrices,
  ongles, Heterochromia : `NewGame` + `HairDresser` + `Ripperdoc`) ; tatouages vanilla = `NewGame` +
  `Ripperdoc` seulement.
- ~~**QA v0.3b attendue**~~ **QA v0.3b (Hell_Kaiser, 01/11, 18 h) : « le Finn tattoo apparaît bien,
  correctement sur le visage, dans le modificateur du miroir, dans l'écran d'inventaire, en mode
  photo et avec le mod de troisième personne »** → (a) sélecteurs au miroir : OK ; (b) tatouage de
  visage affiché : OK, **suivi d'un morph changé au miroir : non rapporté, à confirmer** ; (c) mode
  photo : OK (le groupe `TPP_photomode` non renseigné ne manque donc pas) ; (d) cumul Finn + Kala :
  non rapporté. Le plantage juste après le mode photo (18 h 03) est celui d'Infinite Randomizer
  Framework (3e du jour, retiré ensuite), pas Ink Flow.
- ~~**Pour la prochaine séance Ink Flow** : un tatouage de VISAGE VTK (pas de cou) dans `in\` pour
  juger les morphs : à prendre dans ses archives ou sur Nexus.~~ Fait (Finn Face, v0.3b).
- **QA 3 (Hell_Kaiser, 01/11, 18 h 45) : (d) cumul Kala Japanese Head + Finn Face sur deux slots :
  les deux ensemble, bien collés à la peau : OK.** (b) suivi d'un morph CHANGÉ : non testable, le
  miroir n'a pas la sculpture avancée du visage (nez, mâchoire…), il faut le charcudoc, et sa
  sauvegarde est au début de l'intro. Son argument, que je retiens : son visage n'est pas aux
  options par défaut, et l'encre de Finn suit les traits autour de l'œil sur ce visage-là ; si la
  coque de tête ne suivait pas les morphs, on verrait déjà l'écart sur son visage actuel. Donc la
  copie repointée du morphtarget fonctionne au moins en statique ; le changement au charcudoc reste
  un point de QA à cocher plus tard, non bloquant. **Verdict de Hell_Kaiser : la recette VTK (corps,
  bras, tête) est validée ; prochain chantier = premier jet du builder .exe pour les utilisateurs.**
