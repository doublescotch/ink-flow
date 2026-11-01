# Ink Flow Builder

**Ink Flow — VTK/UV CCXL Tattoo Loader** adds *your own* VTK tattoo archives to the Cyberpunk 2077 character creator
as extra tattoo slots ("Ink 1", "Ink 2", …), each with every tattoo you own, stackable, for body, arms and head.
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
4. Choose the number of **slots** (how many tattoos V can wear at once) and whether the slots also show at the **apartment mirror**.
5. **Build** (about 2 minutes for 18 tattoos the first time, faster afterwards: the extractions are cached), then **Install into game** with the game closed.
   The builder warns about VTK tattoo archives still in `archive\pc\mod` (they would paint a permanent tattoo under the slots) and can move them to a backup folder.
6. In game: character creator, ripperdoc (and mirror if enabled) → **Ink 1 / Ink 2 / …** under "Body Tattoos".

Rebuild whenever you add tattoos or rename them. A tattoo keeps its internal id across rebuilds and renames of the file, so a saved character keeps its tattoos.

## How it works

The shell meshes that carry each tattoo are copies of **your active body and head meshes** (whatever body mod is first in your `archive\pc\mod`, or the vanilla game), with their skin materials replaced by the vanilla tattoo decal material pointing at the tattoo texture. The head shell carries a copy of the face morph target so it follows face sculpting. Textures are copied byte for byte.

## Files

- `InkFlowBuilder.py`, `inkflow/gui.py`: the window (tkinter).
- `inkflow/core.py`: the engine (also used by `inkflow_cli.py`, a command line with the same options).
- `inkflow/env.py`: game detection, ArchiveXL, .NET, WolvenKit download (pinned version, size and SHA-256 checked).
- `templates/` (one folder up): the JSON templates of the CCXL Tattoo Toolkit, in WolvenKit format.
- `build_exe.ps1`: builds the single-file exe with PyInstaller.

Data folder: `%LOCALAPPDATA%\InkFlow` (`config.json`, `catalogue.json`, `work\` cache, `out\`, `backup\`, `wolvenkit\`). Set `INKFLOW_HOME` to use another folder.

## Known limits of this first cut

- Female V only. UV Framework tattoos not supported yet. No icons in the creator (text options).
- Single-file PyInstaller executables are sometimes flagged by antivirus heuristics. The source is here; you can run `python InkFlowBuilder.py` instead.

## Licence

MIT (this tool). WolvenKit belongs to its authors and is downloaded, not shipped. Tattoos stay the property of their authors.
