# Ink Flow Builder

**Ink Flow — VTK/UV CCXL Tattoo Loader** adds *your own* VTK tattoo archives to the Cyberpunk 2077 character creator
as extra tattoo slots ("Ink 1", "Ink 2", …), each with every tattoo you own, stackable, for body, arms and head,
in third person and in first person.
The builder turns the `.archive` files you already downloaded into **one** `Ink_Flow.archive` + `.xl` on your machine.
Nothing made by other authors is redistributed.

## Requirements

- Cyberpunk 2077 2.x on PC, with **ArchiveXL** (and its dependencies RED4ext, Redscript).
- **WolvenKit Console** 9.1.0: the builder downloads it from GitHub on first run (45 MB) into `%LOCALAPPDATA%\InkFlow`.
- The **.NET 10 runtime** (x64), required by WolvenKit Console. The builder tells you if it is missing and opens the Microsoft page.
- Female V. VTK tattoos only in this version (UV Framework tattoos are listed as "ignored").

## How to use

1. Start `InkFlowBuilder.exe`. Check the four green lines of **Setup** (game folder, ArchiveXL, .NET, WolvenKit). Download WolvenKit Console if asked.
2. **Add files…** or **Add folder…**: your VTK tattoo `.archive` files (the ones you would normally drop in `archive\pc\mod`).
   The builder reads each file and shows what it covers: Body, Arm L, Arm R, Head. Unsupported files are greyed out with the reason.
3. Give each tattoo the **name** you want to read in the creator (double-click, 20 characters max). Uncheck the ones you do not want.
4. Choose the number of **slots** (1 to 9: how many tattoos V can wear at once), whether the slots also show at the **apartment mirror**,
   and whether to build the **first person** shells (on by default: the body and arms V sees of herself; about 1 MB more per arm tattoo).
5. **Build** (about 2 minutes for 18 tattoos the first time, faster afterwards: the extractions are cached), then **Install into game** with the game closed.
   The builder warns about VTK tattoo archives still in `archive\pc\mod` (they would paint a permanent tattoo under the slots) and can move them to a backup folder.
6. In game: character creator, ripperdoc (and mirror if enabled) → **Ink 1 / Ink 2 / …** under "Body Tattoos".

Rebuild whenever you add tattoos or rename them. A tattoo keeps its internal id across rebuilds and renames of the file
(the id comes from the file content), so a saved character keeps the tattoos it wears in each slot.

**Rebuild after changing your body mod.** The shells are copies of the body and head meshes that were active when you
built: if you install, remove or reorder a body mod later, build again (and install), otherwise the tattoos keep the
old body's shape.

Only the archives you add are read. The builder never uploads anything, never touches your saves, and never writes
in the game folder before you click **Install into game** (the previous `Ink_Flow` files go to `backup\`).

## How it works

The shell meshes that carry each tattoo are copies of **your active body and head meshes**, with their skin materials
replaced by the vanilla tattoo decal material pointing at the tattoo texture. "Active" means what the game itself
uses: for each part (body, left arm, right arm, head) the builder looks in `archive\pc\mod` for the first archive in
the game's load order (alphabetical, case-insensitive) that delivers the vanilla mesh, and falls back to the base game.
The build log names it (`Body : 006_Angel_Body.archive (over …)`). Any body mod whose mesh keeps local materials and
the standard skin appearance works; otherwise the builder stops with "unsupported body mod". The head shell carries a
copy of the face morph target so it follows face sculpting. Textures are copied byte for byte.

First person follows the vanilla pattern: each slot gets a hidden companion switcher linked to it (the way the game's
own `fpp_body_tattoo` follows `body_tattoo`), listed in the `FPP_Body` group only, that drives the first-person shells:
the body shell again, shown through the chunk mask the active first-person torso uses (read from the active
`l0_000_fpp__full.app`; the torso mesh is a byte-identical copy of the body mesh), and copies of the active first-person
arm meshes. The head is never seen in first person, so it has no first-person shell.

## Files

- `InkFlowBuilder.py`, `inkflow/gui.py`: the window (tkinter).
- `inkflow/core.py`: the engine (also used by `inkflow_cli.py`, a command line with the same options).
- `inkflow/env.py`: game detection, ArchiveXL, .NET, WolvenKit download (pinned version, size and SHA-256 checked).
- `templates/` (one folder up): JSON templates in WolvenKit format: the `.app` and `.inkcharcustomization` skeletons
  come from the **CCXL Tattoo Toolkit** by thrasherpass (Nexus 20279), a template resource made for this; the
  localization skeleton is a neutral placeholder. Every path, name and entry is rewritten at build time.
- `build_exe.ps1`: builds the single-file exe with PyInstaller.

Data folder: `%LOCALAPPDATA%\InkFlow` (`config.json`, `catalogue.json`, `work\` cache, `out\`, `backup\`, `wolvenkit\`). Set `INKFLOW_HOME` to use another folder.

## Known limits of this first cut

- Female V only. UV Framework tattoos (Solo-type bodies) not supported yet. No icons in the creator (text options).
- Face sculpting changed at the ripperdoc after a build has not been QA'd yet (the head shell follows the face morphs
  on an already sculpted face).
- Single-file PyInstaller executables are sometimes flagged by antivirus heuristics. The source is here; you can run `python InkFlowBuilder.py` instead.

## Credits and licence

- **thrasherpass**: CCXL Tattoo Toolkit (Nexus 20279), whose templates define the switcher layout.
- **psiberx**: ArchiveXL, and **WolvenKit** team: WolvenKit Console, downloaded at first run, not shipped.
- The tattoo authors whose archives you build with. This tool redistributes nothing of theirs. A built
  `Ink_Flow.archive` contains their textures: it is for your own game, do not share it without their permission.

MIT (this tool). Source: https://github.com/doublescotch/ink-flow
