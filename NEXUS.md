# Nexus page — Ink Flow (page 36814, 1.3.0 UV of 2026-11-04 ; 1.2.0 opacity, 1.1.0 male V, 1.0.1 rewrite below)

Fields to paste on https://www.nexusmods.com/cyberpunk2077/mods/36814. Written for the Nexus
page (English). Rewritten from the **published** text (read through the API on 2026-11-02 at
18 h 20, copy in `C:\__DEV\cyberpunk\ink_flow\gen\nexus_36814_desc.bbcode`): Hell_Kaiser's
additions (credits, AppData, screenshots, "in addition to vanilla ones") are kept, the "UPDATE IN
PROGRESS" banner goes, and every claim below is one we measured or he saw in game.

## What changes on the page for 1.3.0 (2026-11-04, UV Framework tattoos ; **upload after Hell_Kaiser's QA in game**)

- Summary: "VTK tattoo archives" → "VTK and UV Framework tattoo archives". Requirements, last bullet: UV bodies.
- What works with what: a UV line (Solo 2.0 + UV Framework 3.2.1 + UV arms) : **write "seen in game" only after his
  QA** ; the "Not tested" line loses "UV Framework tattoos" and gains "Songbird 2.0 body (built, not seen)".
- How to use, step 2: "VTK and UV tattoo archives". How it works: the UV paragraph. Known limits: UV line replaced.
- Changelog 1.3.0.

## What changes on the page for 1.2.0 (2026-11-04)

- How to use, step 1: the Body mesh line becomes the "Body meshes in use" table (female V / male V).
- How to use, step 3: the per-tattoo Opacity column (a user's request).
- "Slots visible but nothing on V?": "Body mesh line" → "Body meshes in use table". Changelog 1.2.0.

## What changes on the page for 1.1.0 (2026-11-03)

- Summary and "What it does": male V.
- Requirements: female or male V, with the bodies seen in game.
- "What works with what (1.1.0)": male vanilla body and Gymfiend VTK 1.4.3 + MV Head VTK seen in the
  creator; VTK Vanilla HD reported working by a user (and passes the builder's checks); head tattoos
  on a vanilla head not shown (known, next).
- How it works: re-encoded textures. Known limits: "Female V only" goes, male V scope and vanilla
  head added. Changelog 1.1.0.

## What changed on the page for 1.0.1 (2026-11-02)

- Summary: first person and "1 to 9" added (was "Body, arms and head").
- Requirements: the builder now installs .NET 10 itself (the "bottom left corner" screenshot
  becomes a fallback); Redscript listed as what ArchiveXL's page asks, not as an Ink Flow need.
- "What works with what": new section, honest matrix (Angel and vanilla body seen in game;
  EBBRB accepted by the builder, never seen in game; cyberarms untested; body mod must itself
  work on your game version).
- How to use: step 1 gets the Body mesh line, step 2 gets Scan game folder, MO2 note.
- "Slots visible but nothing on V?": new troubleshooting section (the three EBBRB reports).
- Changelog 1.0.1 for the Changelogs tab.

## Name

Ink Flow - VTK CCXL Tattoo Loader

## Summary (250 characters max; this one is 241)

Turn every VTK tattoo archive you own into stackable slots ("Ink 1" to "Ink 9") in the character creator, ripperdoc and mirror. Female and male V; body, arms, head, first person. Built on your PC; nothing from other authors is redistributed.

## Description

Paste as is: one line per paragraph or per `[*]`, never wrapped (Nexus keeps the line breaks).

```bbcode
[size=5][b]What it does[/b][/size]

VTK tattoos normally replace the vanilla body tattoo texture: one tattoo file, one look, and two tattoo mods fight for the same slot. Ink Flow adds its own slots to the character creator ("Ink 1", "Ink 2", … up to 9), and each slot lists [b]every[/b] VTK tattoo archive you include in the build. Pick one per slot, stack them, change them at the ripperdoc or at the apartment mirror. Body, left arm, right arm and head tattoos are all handled, and a tattoo that only covers the head or one arm stays on that part. The tattoos follow V in first person (arms, and the body when you look down). Female and male V (since 1.1.0): a male tattoo pack goes to male V's slots, a female one to female V's, from the same build.

Ink Flow ships [b]no tattoo[/b]. It ships a small Windows builder: you drop your tattoo archives in, give each one the name you want to read in the creator, click Build, click Install. The result is one [b]Ink_Flow.archive[/b] + [b].xl[/b] in your game, built on your machine from your files.

[size=5][b]Requirements[/b][/size]

[list]
[*]Cyberpunk 2077 2.x (PC). Built and tested on 2.5.
[*][url=https://www.nexusmods.com/cyberpunk2077/mods/4198]ArchiveXL[/url] and what its page asks for (RED4ext; Redscript for ArchiveXL's script features). Ink Flow itself needs nothing else: no Codeware, no TweakXL, no CET.
[*]The [url=https://dotnet.microsoft.com/download/dotnet/10.0]Microsoft .NET 10 runtime[/url] (x64), needed by WolvenKit Console. Since 1.0.1 the builder installs it for you: one button, Microsoft's own installer (30 MB, version and SHA-256 checked, silent install, the usual Windows elevation prompt). If you prefer the manual way: on Microsoft's page take the bottom-left box ".NET Runtime", Windows, x64 Installer, not the SDK or the Desktop runtime (see screenshot). WolvenKit Console is downloaded from GitHub on first run (45 MB, version pinned and checked).
[*]Female V with the vanilla body or a body mod of the VTK family (Angel, EBBRB…), or male V with the vanilla body or Gymfiend VTK: see "What works with what" below. The screenshot shows the archives of an Angel setup.
[/list]

[size=5][b]What works with what (1.1.0)[/b][/size]

[list]
[*][b]Angel body[/b] (+ Vanilla Refits, VTK Vanilla HD Head): seen in game, every feature: creator, ripperdoc, mirror, first person, photo mode, body / arms / head tattoos, stacking. This is the setup Ink Flow was developed on.
[*][b]Vanilla body[/b] (no body mod at all): seen in game, same features for body and arms. Head tattoos on the vanilla head (no VTK head mod) do not show: known, being looked at; with a VTK HD head they work.
[*][b]VTK Vanilla HD body[/b]: reported working by a user, and passes the builder's checks entirely (body, arms, first-person arms).
[*][b]Male V, vanilla body[/b] and [b]Gymfiend VTK 1.4.3 + MV Head VTK[/b]: seen in the character creator (body tattoos, stacking). Mirror, first person and photo mode not seen in game yet; male head tattoos not tested yet.
[*][b]Other VTK bodies[/b]: the builder reads the body, arm and head meshes your game actually loads and copies them. EBBRB 5.0 passes the builder's checks (measured on its archive, not seen in game yet). Any body mod whose meshes keep local materials and the standard skin appearance passes; a body mod that does not pass stops the build with "unsupported body mod" rather than producing a broken result. The body mod must itself work on your game version: the tattoo shells are copies of its meshes, so a body not updated for 2.5 will not get better under Ink Flow.
[*][b]UV Framework bodies[/b] (1.3.0): Solo 2.0 + UV Framework Texture 3.2.1 + Solo arms UV: [SEEN IN GAME: to confirm after QA, else "built and checked, not seen in game yet"]. A UV tattoo is one texture for body + both arms; on UV arms the builder draws all three, on vanilla / VTK arms (Angel…) it draws the body part only and says so in build.log (the arm layouts differ, see "Arms and families" below). Songbird 2.0 body: builds (its cyber plates are left out of the shell), not seen in game.
[*][b]Not tested[/b]: cyberarms (Mantis Blades, Gorilla Arms… the tattoo shells cover the arms fully; what happens on a cyberarm has not been looked at).
[/list]

[size=5][b]Arms and families (1.3.0)[/b][/size]

VTK and UV tattoos share one body layout: the body part of a tattoo of either family fits every body, vanilla, VTK or UV, and the builder always builds it. The arms differ: UV Framework arms are unwrapped into the left strip of the body texture (a UV tattoo is one file for body + arms), vanilla and VTK arms into textures of their own (a VTK tattoo ships separate arm files). A texture of one family on arms of the other would be garbage, so the builder reads the layout of the arm meshes your game loads and builds the arm shells only for tattoos of the same family; the others get the body part and a "skipped" line in build.log. An arms-only UV tattoo (a sleeve) on VTK arms therefore builds nothing. Angel unwraps its feet into that strip: under a UV tattoo the feet are hidden in the shell rather than painted with arm ink (VTK textures never paint there).

[size=5][b]How to use[/b][/size]

[list=1]
[*]Unzip, run [b]InkFlowBuilder.exe[/b]. The Setup box shows: game folder, ArchiveXL, .NET 10, WolvenKit Console. Fix what is red (the buttons do it: Install .NET Runtime 10, Download WolvenKit Console). Under it, the [b]Body meshes in use[/b] table names, for female V and male V, the archive your game loads for the body, the arms and the head (the shells are copied from these): green = a mod archive, grey "base game" = the vanilla mesh. A red line under the table means no body mod was seen at all: right only if you really play on the vanilla body; if you use a body mod, see "Slots visible but nothing on V?" below before building.
[*][b]Scan game folder…[/b] finds the VTK and UV tattoo archives your game already loads (archive\pc\mod and REDmod folders) and adds them. Or [b]Add files…[/b] / [b]Add folder…[/b] with .archive files from anywhere. The list shows what each file covers: Body, Arm L, Arm R, Head. Files Ink Flow cannot use are greyed out with the reason.
[*]Double-click a name to rename it (20 characters max, that is what you read in the creator). Uncheck what you do not want. The [b]Opacity[/b] column sets one tattoo's opacity (double-click, 0.1 to 1.0, or select several rows and press Opacity…); empty = the Default opacity of the options, shown in brackets.
[*]Choose the number of slots (1 to 9: how many tattoos V wears at once, in addition to the vanilla ones), whether the slots also appear at the apartment mirror, and whether to build the first-person shells (on by default).
[*][b]Build[/b] (about two minutes for 18 tattoos the first time, less afterwards), then [b]Install into game[/b] with the game closed. If the original tattoo archives are still in archive\pc\mod the builder tells you and can move them to a backup folder (left in place, they paint a permanent tattoo under the slots).
[*]In game: character creator, ripperdoc, mirror → "Ink 1", "Ink 2" under Body Tattoos.
[/list]

Add tattoos later? Add the files, Build, Install. Your character keeps the tattoos already chosen in each slot (a tattoo keeps its internal id across rebuilds, even if you rename the file). Ink Flow keeps its data in C:\Users\<you>\AppData\Local\InkFlow (the "Open data folder" button): your list, the WolvenKit download, a cache that makes the next build fast, your previous Ink_Flow.archive files as backups, and build.log.

[b]Changed your body mod?[/b] Build again. The shells that carry the tattoos are copies of the body and head meshes that were active when you built.

[size=5][b]Slots visible but nothing on V?[/b][/size]

The shells are copies of the body mesh the builder saw when you built. If the Body meshes in use table said "base game" while you play with a body mod, the shells are vanilla-shaped and hide under the skin of your body: the slots are there, nothing is drawn. Make the table show your body mod, then Build and Install:
[list]
[*]Mod Organizer 2: start the builder through MO2 (add it as an executable), otherwise it does not see MO2's virtual folder.
[*]REDmod (mods\<name>\archives): read since 1.0.1, in the game's order (mods.json / REDmod load order).
[*]Vortex or manual install: the body archive must be in archive\pc\mod; 1.0.1 honours modlist.txt.
[/list]
Still wrong? Open the data folder and post [b]build.log[/b] from a fresh build: its second block names the archive each mesh was copied from.

[size=5][b]How it works[/b][/size]

For each tattoo file the builder extracts the texture(s), copies your active body / arm / head meshes with their skin materials replaced by the vanilla tattoo decal material, points the decal at the tattoo texture, and writes one appearance per tattoo and per slot plus the character-creator entries (CCXL). Since 1.3.0 a UV Framework texture is pointed at by the body and both arm shells at once (one copy of the texture), and only the skin chunks of a mesh are shown in a shell. The head shell carries a copy of the face morph target, so it follows face sculpting. First person works like the vanilla tattoos: a hidden companion of each slot drives first-person shells (the body shell through the first-person chunk mask, copies of your first-person arm meshes). Male V needs no companion: the game shows his third-person body and arms in first person, so his shells are listed for both views, as the vanilla male tattoos are. The textures are copied byte for byte (what you see is the author's tattoo, unchanged), except those whose mip chain stops early (several male packs): they render as broken stripes through the decal, so the builder re-encodes them with WolvenKit (same image, full mip chain, uncompressed: about 4 MB in the archive, about 85 MB of video memory while a 4096 tattoo is worn). The build log lists them. Everything is generated by WolvenKit Console from JSON; the source of the builder is public.

[size=5][b]Known limits (1.1.0)[/b][/size]

[list]
[*]Head tattoos on a vanilla head (no VTK head mod) do not show yet.
[*]Male V: seen in the character creator only so far (vanilla body, Gymfiend VTK).
[*]UV Framework tattoos (1.3.0): arms only when your arm meshes are UV arms (see "Arms and families"); no conversion between the two arm layouts yet.
[*]Cyberarms not tested (see above).
[*]Text options in the creator, no icons yet.
[*]Face sculpting changed at the ripperdoc after a build has not been QA'd (the head shell follows the morphs of an already sculpted face, so it should be fine).
[/list]

[size=5][b]Antivirus[/b][/size]

The builder is a single-file PyInstaller executable (Python + tkinter). Some antivirus heuristics flag such files. The SHA-256 of the exe is in the file description; the source is on GitHub and you can run it with Python instead ([i]python InkFlowBuilder.py[/i]).

[size=5][b]Source[/b][/size]

MIT. [url=https://github.com/doublescotch/ink-flow]github.com/doublescotch/ink-flow[/url] (builder, engine, study notes). Issues and ideas welcome there or in the posts tab.

[size=5][b]Credits[/b][/size]

[url=https://www.patreon.com/kalahira]Kala[/url], [url=https://www.nexusmods.com/profile/bedellia?gameId=3333]Bedellia[/url] and [url=https://www.nexusmods.com/profile/shivakoko]Shivakoko[/url] for the tattoos in the screenshots. Please help me find the authors of the Samurai and Garden Bloom tattoos, they are listed as "Unknown" in the names. Amazing works; this project would not exist without their art to give it a point.
thrasherpass for the [url=https://www.nexusmods.com/cyberpunk2077/mods/20279]CCXL Tattoo Toolkit[/url], the template resource whose switcher layout Ink Flow follows. psiberx for ArchiveXL and RED4ext. The WolvenKit team for WolvenKit Console (downloaded by the builder, not shipped).
```

## Changelog 1.3.0 (Nexus "Changelogs" tab, 2026-11-04)

```
1.3.0
- UV Framework tattoos (Solo-type bodies) are built, no longer "ignored": a UV tattoo is one texture for body + both arms (plus a head file for some), and it becomes body + arm L + arm R shells. The arm shells are built only when the arm meshes your game loads are UV Framework arms; on vanilla / VTK arms (Angel…) the body part is built and build.log says the arms were skipped (the two arm layouts differ; a conversion may come later). The head overlay of a UV pack is built like a VTK head tattoo.
- Angel + UV tattoo: the feet are hidden in that shell (Angel unwraps them into the part of the texture a UV tattoo uses for the arms).
- Tattoo shells no longer cover non-skin chunks of your meshes (the personal link port on the left forearm, Songbird's cyber plates): a tattoo is skin only. Rebuild and install.
- Per-tattoo opacity accepts 0.1 to 2.0 like the Default opacity (1.2.0 refused above 1.0 in the column).
- The texture cache is rebuilt once (new file list).
```

## Changelog 1.2.0 (Nexus "Changelogs" tab, 2026-11-04)

```
1.2.0
- Per-tattoo opacity (requested in the posts): a new Opacity column in the tattoo list. Double-click a cell (0.1 to 1.0), or select several rows and press Opacity…. Empty = the Default opacity of the options (the old Opacity setting), shown in brackets. The value applies to all of that tattoo's shells (body, arms, head, first person). Rebuild and install.
- The detected body meshes are now a table: female V and male V side by side, one row each for body, arms and head, the archives they win over in small grey type underneath. Same detection as before, easier to read.
- Nothing else changes: with no per-tattoo opacity set, a build is the same as with 1.1.0.
```

## Changelog 1.1.0 (Nexus "Changelogs" tab, 2026-11-03)

```
1.1.0
- Male V: male VTK tattoo packs (v_masc_overlay, masculine arms, male head) get their own Ink slots in male V's character creator, built from the same window, alongside the female ones. Seen in game on the vanilla male body and on Gymfiend VTK 1.4.3 + MV Head VTK (character creator).
- Tattoos showing as rows of dashes or not at all: their texture had a truncated mip chain (several male packs). The builder now re-encodes such textures with WolvenKit (full mip chain); every other texture is still copied byte for byte. Rebuild and install.
- The Body mesh line shows the male body mod too when one is found.
- Female builds are unchanged (same files, byte for byte, as 1.0.1 for the same tattoos).
```

## Changelog 1.0.1 (Nexus "Changelogs" tab, 2026-11-02)

```
1.0.1
- First person fixed: the arm tattoos showed holes and slid under the skin when the arms moved, because the first-person shells were never applied (the slot's switcher did not drive its hidden first-person companion, as the game's own body_tattoo drives fpp_body_tattoo) and the third-person arm shells were drawn over the first-person arms. Rebuild and install.
- Vanilla body (no body mod) now works in game: 1.0.0 stopped with "unsupported body mod" on the vanilla arm meshes, and the first-person shells broke the mirror (same cause as above). Seen in game: creator, mirror, first person, photo mode.
- .NET 10 runtime missing? One button installs it (Microsoft's x64 Runtime installer, 30 MB, version and SHA-256 checked, silent install with the usual Windows elevation prompt). No more hunting the right link among the SDK / ASP.NET / Desktop boxes.
- Body detection follows the game's real load order: archive\pc\mod (modlist.txt honoured), then REDmod folders (mods\*\archives, load order honoured), then the base game. 1.0.0 only read archive\pc\mod alphabetically, so a body deployed as REDmod or seen through MO2's virtual folder was missed and the shells were built on the vanilla body (slots visible, nothing drawn).
- The window shows which body / arms / head archives the shells will be copied from (red when it is the base game).
- New "Scan game folder…" button: finds the VTK tattoo archives your game already loads, copies them to the builder's folder and adds them.
- build.log written in the data folder at each build (send it when something does not show).
- The conflict check at install also looks at REDmod folders.
```

## Permissions (Nexus boxes)

- Upload to other sites: no (link here).
- Modification: yes, with credit, under the MIT licence.
- Conversion to other games: not applicable.
- Asset use: the tool contains no third-party asset. The CCXL templates come from the CCXL Tattoo
  Toolkit (see credits).

## Files to upload

- 1.2.0 (2026-11-04) : `Ink_Flow_Builder-1.2.0.zip` (`releases\`, SHA-256 `3e1f13f9…6a46`):
  `InkFlowBuilder.exe` (SHA-256 `4e3f15d1…9bb6`) + `README.md` + `LICENSE`. Same file description as
  below. Mark 1.1.0 as old version. Mod version field: 1.2.0.
- 1.1.0 (2026-11-03, uploaded) : `Ink_Flow_Builder-1.1.0.zip` (`releases\`, SHA-256 `43f0f655…6427`):
  `InkFlowBuilder.exe` (SHA-256 `24434274…5c05`) + `README.md` + `LICENSE`. Same file description as
  below. Mark 1.0.1 as old version. Mod version field: 1.1.0.
- 1.0.1 (2026-11-02, uploaded) : `InkFlowBuilder-1.0.1.zip` (`releases\`, SHA-256 `42fa8310…4ed2`): `InkFlowBuilder.exe` (SHA-256
  `f32d59bc…7109`) + `README.md` + `LICENSE`. File description: version, SHA-256 of the exe,
  "downloads WolvenKit Console 9.1.0 from GitHub on first run, installs .NET 10 Runtime on request".
  Mark 1.0.0 as old version (the published MAIN is 172045; 172010 is already archived).
- Mod version field: 1.0.1.

## Screenshots (Hell_Kaiser, second screen, see FEEDBACK captures)

1.2.0: the builder window is new (Body meshes in use table, Opacity column): its screenshot is to
redo. Already on the page: builder window, .NET page with the runtime box, Angel setup archives. To
redo or add for 1.0.1: (1) the builder window with the **Body mesh** line green (Angel) and the
**Install .NET Runtime 10** button visible, (2) a first-person shot with arm tattoos, (3) the
vanilla body with Samurai at the mirror.
