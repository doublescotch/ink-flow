# Nexus page — Ink Flow (page 36814, rewrite for 1.0.1, 2026-11-02)

Fields to paste on https://www.nexusmods.com/cyberpunk2077/mods/36814. Written for the Nexus
page (English). Rewritten from the **published** text (read through the API on 2026-11-02 at
18 h 20, copy in `C:\__DEV\cyberpunk\ink_flow\gen\nexus_36814_desc.bbcode`): Hell_Kaiser's
additions (credits, AppData, screenshots, "in addition to vanilla ones") are kept, the "UPDATE IN
PROGRESS" banner goes, and every claim below is one we measured or he saw in game.

## What changes on the page, in short

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

## Summary (250 characters max; this one is 247)

Turn every VTK tattoo archive you own into stackable slots ("Ink 1" to "Ink 9", you choose how many) in the character creator, ripperdoc and mirror. Body, arms, head, first person. Built on your PC; nothing from other authors is redistributed.

## Description

Paste as is: one line per paragraph or per `[*]`, never wrapped (Nexus keeps the line breaks).

```bbcode
[size=5][b]What it does[/b][/size]

VTK tattoos normally replace the vanilla body tattoo texture: one tattoo file, one look, and two tattoo mods fight for the same slot. Ink Flow adds its own slots to the character creator ("Ink 1", "Ink 2", … up to 9), and each slot lists [b]every[/b] VTK tattoo archive you include in the build. Pick one per slot, stack them, change them at the ripperdoc or at the apartment mirror. Body, left arm, right arm and head tattoos are all handled, and a tattoo that only covers the head or one arm stays on that part. The tattoos follow V in first person (arms, and the body when you look down).

Ink Flow ships [b]no tattoo[/b]. It ships a small Windows builder: you drop your tattoo archives in, give each one the name you want to read in the creator, click Build, click Install. The result is one [b]Ink_Flow.archive[/b] + [b].xl[/b] in your game, built on your machine from your files.

[size=5][b]Requirements[/b][/size]

[list]
[*]Cyberpunk 2077 2.x (PC). Built and tested on 2.5.
[*][url=https://www.nexusmods.com/cyberpunk2077/mods/4198]ArchiveXL[/url] and what its page asks for (RED4ext; Redscript for ArchiveXL's script features). Ink Flow itself needs nothing else: no Codeware, no TweakXL, no CET.
[*]The [url=https://dotnet.microsoft.com/download/dotnet/10.0]Microsoft .NET 10 runtime[/url] (x64), needed by WolvenKit Console. Since 1.0.1 the builder installs it for you: one button, Microsoft's own installer (30 MB, version and SHA-256 checked, silent install, the usual Windows elevation prompt). If you prefer the manual way: on Microsoft's page take the bottom-left box ".NET Runtime", Windows, x64 Installer, not the SDK or the Desktop runtime (see screenshot). WolvenKit Console is downloaded from GitHub on first run (45 MB, version pinned and checked).
[*]Female V, with either the vanilla body or a body mod of the VTK family (Angel, EBBRB…, see "What works with what" below). The screenshot shows the archives of an Angel setup.
[/list]

[size=5][b]What works with what (1.0.1)[/b][/size]

[list]
[*][b]Angel body[/b] (+ Vanilla Refits, VTK Vanilla HD Head): seen in game, every feature: creator, ripperdoc, mirror, first person, photo mode, body / arms / head tattoos, stacking. This is the setup Ink Flow was developed on.
[*][b]Vanilla body[/b] (no body mod at all): seen in game, same features. Head tattoos use the vanilla head: a tattoo drawn for a VTK HD head may sit slightly differently.
[*][b]Other VTK bodies[/b]: the builder reads the body, arm and head meshes your game actually loads and copies them. EBBRB 5.0 passes the builder's checks (measured on its archive, not seen in game yet). Any body mod whose meshes keep local materials and the standard skin appearance passes; a body mod that does not pass stops the build with "unsupported body mod" rather than producing a broken result. The body mod must itself work on your game version: the tattoo shells are copies of its meshes, so a body not updated for 2.5 will not get better under Ink Flow.
[*][b]Not tested[/b]: cyberarms (Mantis Blades, Gorilla Arms… the tattoo shells cover the arms fully; what happens on a cyberarm has not been looked at), male V (not supported), UV Framework tattoos (ignored by the builder for now).
[/list]

[size=5][b]How to use[/b][/size]

[list=1]
[*]Unzip, run [b]InkFlowBuilder.exe[/b]. The Setup box shows: game folder, ArchiveXL, .NET 10, WolvenKit Console. Fix what is red (the buttons do it: Install .NET Runtime 10, Download WolvenKit Console). The last line, [b]Body mesh[/b], names the body mod the builder sees: green = a body mod found, red = base game. Red is right only if you really play on the vanilla body; if you use a body mod and the line is red, see "Slots visible but nothing on V?" below before building.
[*][b]Scan game folder…[/b] finds the VTK tattoo archives your game already loads (archive\pc\mod and REDmod folders) and adds them. Or [b]Add files…[/b] / [b]Add folder…[/b] with .archive files from anywhere. The list shows what each file covers: Body, Arm L, Arm R, Head. Files Ink Flow cannot use are greyed out with the reason.
[*]Double-click a name to rename it (20 characters max, that is what you read in the creator). Uncheck what you do not want.
[*]Choose the number of slots (1 to 9: how many tattoos V wears at once, in addition to the vanilla ones), whether the slots also appear at the apartment mirror, and whether to build the first-person shells (on by default).
[*][b]Build[/b] (about two minutes for 18 tattoos the first time, less afterwards), then [b]Install into game[/b] with the game closed. If the original tattoo archives are still in archive\pc\mod the builder tells you and can move them to a backup folder (left in place, they paint a permanent tattoo under the slots).
[*]In game: character creator, ripperdoc, mirror → "Ink 1", "Ink 2" under Body Tattoos.
[/list]

Add tattoos later? Add the files, Build, Install. Your character keeps the tattoos already chosen in each slot (a tattoo keeps its internal id across rebuilds, even if you rename the file). Ink Flow keeps its data in C:\Users\<you>\AppData\Local\InkFlow (the "Open data folder" button): your list, the WolvenKit download, a cache that makes the next build fast, your previous Ink_Flow.archive files as backups, and build.log.

[b]Changed your body mod?[/b] Build again. The shells that carry the tattoos are copies of the body and head meshes that were active when you built.

[size=5][b]Slots visible but nothing on V?[/b][/size]

The shells are copies of the body mesh the builder saw when you built. If the Body mesh line said BASE GAME while you play with a body mod, the shells are vanilla-shaped and hide under the skin of your body: the slots are there, nothing is drawn. Make the line show your body mod, then Build and Install:
[list]
[*]Mod Organizer 2: start the builder through MO2 (add it as an executable), otherwise it does not see MO2's virtual folder.
[*]REDmod (mods\<name>\archives): read since 1.0.1, in the game's order (mods.json / REDmod load order).
[*]Vortex or manual install: the body archive must be in archive\pc\mod; 1.0.1 honours modlist.txt.
[/list]
Still wrong? Open the data folder and post [b]build.log[/b] from a fresh build: its second block names the archive each mesh was copied from.

[size=5][b]How it works[/b][/size]

For each tattoo file the builder extracts the texture(s), copies your active body / arm / head meshes with their skin materials replaced by the vanilla tattoo decal material, points the decal at the tattoo texture, and writes one appearance per tattoo and per slot plus the character-creator entries (CCXL). The head shell carries a copy of the face morph target, so it follows face sculpting. First person works like the vanilla tattoos: a hidden companion of each slot drives first-person shells (the body shell through the first-person chunk mask, copies of your first-person arm meshes). The textures are copied byte for byte: what you see is the author's tattoo, unchanged. Everything is generated by WolvenKit Console from JSON; the source of the builder is public.

[size=5][b]Known limits (1.0.1)[/b][/size]

[list]
[*]Female V only.
[*]VTK family only. UV Framework tattoos (Solo-type bodies) are listed as "ignored" for now, planned.
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

- `InkFlowBuilder-1.0.1.zip` (`releases\`, SHA-256 `42fa8310…4ed2`): `InkFlowBuilder.exe` (SHA-256
  `f32d59bc…7109`) + `README.md` + `LICENSE`. File description: version, SHA-256 of the exe,
  "downloads WolvenKit Console 9.1.0 from GitHub on first run, installs .NET 10 Runtime on request".
  Mark 1.0.0 as old version (the published MAIN is 172045; 172010 is already archived).
- Mod version field: 1.0.1.

## Screenshots (Hell_Kaiser, second screen, see FEEDBACK captures)

Already on the page: builder window, .NET page with the runtime box, Angel setup archives. To
redo or add for 1.0.1: (1) the builder window with the **Body mesh** line green (Angel) and the
**Install .NET Runtime 10** button visible, (2) a first-person shot with arm tattoos, (3) the
vanilla body with Samurai at the mirror.
