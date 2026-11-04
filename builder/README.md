# Ink Flow Builder

**Ink Flow — VTK/UV CCXL Tattoo Loader** adds *your own* VTK tattoo archives to the Cyberpunk 2077 character creator
as extra tattoo slots ("Ink 1", "Ink 2", …), each with every tattoo you own, stackable, for body, arms and head,
in third person and in first person.
The builder turns the `.archive` files you already downloaded into **one** `Ink_Flow.archive` + `.xl` on your machine.
Nothing made by other authors is redistributed.

## Requirements

- Cyberpunk 2077 2.x on PC, with **ArchiveXL** (and RED4ext, which it runs on). Redscript, Codeware and TweakXL are
  not needed by Ink Flow.
- **WolvenKit Console** 9.1.0: the builder downloads it from GitHub on first run (45 MB) into `%LOCALAPPDATA%\InkFlow`.
- The **.NET 10 runtime** (x64), required by WolvenKit Console. The builder tells you if it is missing and installs it
  for you (one button: Microsoft's installer is downloaded, version and SHA-256 checked, then run silently).
- Female or male V (since 1.1.0), VTK or UV Framework tattoos (UV since 1.3.0). A tattoo archive is female or male
  by the files it replaces (`v_overlay` / `femme_arm_*` / `pwa` head, or `v_masc_overlay` / `masculine_arm_*` /
  `pma` head; UV: `fullbody_overlay_d01` / `wa_head_overlay_d01`, or the `ma_` forms); one build carries both.
- **Arms of either family on arms of either family (1.4.0).** A UV tattoo is one texture for body + both arms,
  drawn for UV Framework arms (Solo, Songbird…); a VTK tattoo keeps the arms in textures of their own, drawn for
  vanilla / VTK arms (Angel, vanilla…). The body part of either family fits every body (same layout). When the arm
  part was drawn for the other family than your arms, the builder **converts** it to your arms' layout (same arm,
  two unwrappings: each texel is moved to the same spot of the arm), once per tattoo and cached: about 20 s per arm
  for a UV tattoo, up to a minute for a VTK arm going onto UV arms (an 8K texture: the UV arm area is small). This
  needs **UV Framework Texture** in your game (its arm meshes are the map between the two layouts, even when your
  body mod overrides them); without it the arms are skipped as in 1.3.0, and `build.log` says why.

## How to use

1. Start `InkFlowBuilder.exe`. Check the four green lines of **Setup** (game folder, ArchiveXL, .NET, WolvenKit). The
   red ones have a button: Install .NET Runtime 10, Download WolvenKit Console.
   Under them, the **Body meshes in use** table names, for female V and male V, the archive the game loads for the body,
   the arms and the head (the shells are copied from these), with the archives it wins over in small grey type. Green =
   a mod archive; grey "base game" = the vanilla mesh. A red line under the table means no body mod was seen at all,
   which is right only if you use none (see Troubleshooting).
2. **Scan game folder…** finds the VTK and UV tattoo archives your game already loads (`archive\pc\mod` and REDmod), copies
   them into the builder's tattoo folder and adds them. Or **Add files…** / **Add folder…** with `.archive` files from
   anywhere. The builder reads each file and shows what it covers: Body, Arm L, Arm R, Head. Unsupported files are
   greyed out with the reason.
3. Give each tattoo the **name** you want to read in the creator (double-click, 20 characters max). Uncheck the ones you do not want.
   The **Opacity** column sets one tattoo's opacity (double-click, 0.1 to 2.0: above 1.0 brightens a faded texture; or select several rows and press
   **Opacity…**). Empty = the **Default opacity** of the options, shown in brackets. Rebuild to apply.
4. Choose the number of **slots** (1 to 9: how many tattoos V can wear at once), whether the slots also show at the **apartment mirror**,
   and whether to build the **first person** shells (on by default: the body and arms V sees of herself; about 1 MB more per arm tattoo).
5. **Build** (about 2 minutes for 18 tattoos the first time, faster afterwards: the extractions are cached), then **Install into game** with the game closed.
   The builder warns about VTK tattoo archives still loaded by the game (`archive\pc\mod` or REDmod: they would paint a permanent tattoo under the slots) and can move them to a backup folder.
   If a mod manager deployed them, disable them in the manager instead, otherwise it will put them back.
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
uses: for each part (body, left arm, right arm, head) the builder walks the game's load order and takes the first
archive that delivers the vanilla mesh: `archive\pc\mod` (in the order of `modlist.txt` if that file exists, else
alphabetical, case-insensitive), then the REDmod folders `mods\<name>\archives` (in the order of
`r6\cache\modded\MO_REDmod_load_order.txt` if present, else alphabetical by folder; legacy archives load before
REDmods), and falls back to the base game. The window shows it (**Body meshes in use** table) and the build log names it
(`Body : 006_Angel_Body.archive (over …)`). Any body mod whose mesh keeps local materials and the standard skin
appearance works, and so does the vanilla body; otherwise the builder stops with "unsupported body mod". The head
shell carries a copy of the face morph target so it follows face sculpting.

Textures are copied byte for byte, with one exception: a texture whose mip chain stops before 1x1 (11 levels on a
4096, as in several male packs) renders as broken stripes through the decal material, so the builder re-encodes it
with WolvenKit (export, then import: full mip chain). The re-encoded texture is uncompressed: about 4 MB in the
archive, about 85 MB of video memory while a 4096 tattoo is worn. The build log names every re-encoded file.

**Male V** (1.1.0): the game builds him differently. His body is a plain mesh (no morph target), and in first person
the game shows his third-person body and arms, so the male shells need no first-person companion: they are listed in
the `FPP_Body`, `TPP_Body` and `character_creation` groups, as the vanilla male tattoos are. His slots live in their
own `inkflow_pma.inkcharcustomization` (ArchiveXL `male:` key), same indexes (1041-1049, free for both).

**Mod Organizer 2**: MO2 shows the game a virtual folder; a program started outside MO2 sees an empty or partial
`archive\pc\mod`. Add `InkFlowBuilder.exe` as an executable in MO2 and start it from there, so the Body meshes in
use table shows your body mod. With Vortex (hardlink deployment, or REDmod deployment) nothing special is needed.

First person follows the vanilla pattern: each slot gets a hidden companion switcher linked to it (the way the game's
own `fpp_body_tattoo` follows `body_tattoo`), listed in the `FPP_Body` group only, that drives the first-person shells:
the body shell again, shown through the chunk mask the active first-person torso uses (read from the active
`l0_000_fpp__full.app`; the torso mesh is a byte-identical copy of the body mesh), and copies of the active first-person
arm meshes. The head is never seen in first person, so it has no first-person shell.

## Files

- `InkFlowBuilder.py`, `inkflow/gui.py`: the window (tkinter).
- `inkflow/core.py`: the engine (also used by `inkflow_cli.py`, a command line with the same options plus `--from-game`).
- `inkflow/rdar.py`: reads the index of an `.archive` (the hashes of the paths it ships) without WolvenKit.
- `inkflow/env.py`: game detection, ArchiveXL, .NET, WolvenKit download (pinned version, size and SHA-256 checked).
- `templates/` (one folder up): JSON templates in WolvenKit format: the `.app` and `.inkcharcustomization` skeletons
  come from the **CCXL Tattoo Toolkit** by thrasherpass (Nexus 20279), a template resource made for this; the
  localization skeleton is a neutral placeholder. Every path, name and entry is rewritten at build time.
- `build_exe.ps1`: builds the single-file exe with PyInstaller.

Data folder: `%LOCALAPPDATA%\InkFlow` (`config.json`, `catalogue.json`, `work\` cache, `out\`, `backup\`, `wolvenkit\`,
`tattoos\` copies made by Scan game folder, `build.log` of the last build). Set `INKFLOW_HOME` to use another folder.

## Troubleshooting

- **The Ink slots show in the creator but nothing appears on V.** The shells were copied from a body that is not the
  one you play with (the Body meshes in use table said "base game" while you use a body mod, or you changed body
  since). Make the table show your body mod (MO2: start the builder through MO2), Build, Install. Still wrong? Open
  the data folder and send `build.log` (posts tab or GitHub issue): its second block says which archive each mesh
  came from.
- **"unsupported body mod" at build time.** The active body or arm mesh stores its materials in a way the builder
  does not handle. Send `build.log` with the name of the body mod. (1.0.0 refused the vanilla arms for this reason;
  fixed in 1.0.1.)
- **".NET 10 runtime: MISSING" although you installed it.** WolvenKit Console needs the **.NET Runtime 10 x64**, not
  the SDK, not the Desktop runtime alone, not x86. Press **Install .NET Runtime 10** in the Setup box: the builder
  fetches the right installer itself (Windows asks for elevation once). If that fails, on the Microsoft page take the
  ".NET Runtime" box → Windows → Installers → x64.
- **First person: the arm tattoo shows holes or slides under the skin when the arms move** (1.0.0). The first-person
  shells were never applied (the slot's switcher did not drive its hidden first-person companion), so the third-person
  arm shells were drawn over the first-person arms. Fixed in 1.0.1: rebuild and install.
- **A tattoo shows as rows of dashes, or not at all** (1.0.x, mostly male packs): its texture had a truncated mip
  chain. Fixed in 1.1.0: the builder re-encodes such textures. Rebuild and install.
- **Head tattoo not visible on a vanilla head** (no VTK head mod): known, under investigation. Head tattoos are drawn
  for VTK HD heads and work with one (seen with VTK Vanilla HD Head).
- **A UV tattoo shows on the body but not on the arms** (or a VTK arm tattoo is missing on a UV body). Your arm
  meshes are of the other family and the builder could not convert the texture: `build.log`, block 2, says "no arm
  conversion possible" with the reason, usually that UV Framework Texture is not in the game (its arm meshes are
  needed for the conversion). Install it (it changes nothing on a VTK body: the body mod still wins the meshes) and
  rebuild. A UV tattoo with no ink in the arm part (body-only packs such as Kala Japanese V2) has no arm shells
  either: "no ink on this arm" in the log.
- **A UV tattoo on Angel: the feet stay bare.** Angel unwraps its feet into the part of the texture a UV tattoo uses
  for the arms, so the body shell reads a copy of the texture with that part cleared (made once per texture with
  WolvenKit, 10 to 60 s, cached; the texture format is kept) rather than paint arm ink on the feet. VTK textures
  never paint there either.
- **Game 2.3x.** Not supported: the 2.5 bodies are different. Someone may fork the generator for 2.31 (MIT).

## Known limits of this first cut

- UV Framework tattoos (1.3.0): seen in game on Angel (body, feet and ankles bare). On Solo 2.0 + UV Framework 3.2.1 +
  Solo arms UV: seen in the character creator (body and both arms); mirror, first person and photo mode not seen, the
  Solo bench crashed at save load (Solo's own page reports the same), Solo parked for now; in first person on Solo the
  belly uses the vanilla torso mask (Solo's `.app` cannot be read by WolvenKit Console). Songbird 2.0 body: the shell
  hides its cyber chunks, not seen in game. No icons in the creator (text options).
- First person [TO REWRITE AFTER THE FIX]: the body tattoo does not show when looking down (arms do), on every body
  (vanilla, Angel). The first-person body shell is a copy of the full body mesh wearing the chunk mask of the
  first-person torso mesh, whose chunks are numbered differently (on Angel that mask is the lower legs; her torso is
  another component). Present since 1.0.1, measured 2026-11-05. Fix: one first-person shell per body component of
  the first-person appearance, copy of that component's mesh with its own mask.
- Inventory and photo mode [UNDER INVESTIGATION]: holes on the shins with the 8K Samurai, none in the creator; same
  shell in every view, so the camera distance (mip levels of that texture) is the lead, not the shells.
- Arm conversion (1.4.0): UV arms onto Angel's arms: seen in the creator and at the mirror for every UV tattoo of the
  test pack, on a game rebuilt from scratch; VTK arms onto UV arms (Solo): seen in the character creator. The converted texture is a resampling: a little softer than the original, and a seam of the unwrapping may
  show a hairline where the two layouts cut the arm differently.
- Feet and ankles on Angel: Angel unwraps them into the arm strip of the body texture, which VTK textures do not paint
  and which the builder clears for UV textures: on Angel every tattoo stops in a straight line at the ankle, even one
  painted further down by its author (Samurai). Angel-specific; being looked at (resampling the feet like the arms).
- Very faint overlays (freckles, beauty marks: GetTenSO FrecklesV, VTK or UV) do not show through the tattoo decal,
  even at opacity 2.0: they are painted to melt into the skin's own overlay layer. Keep those as overlay archives.
- Male V (vanilla body, Gymfiend VTK 1.4.3 + MV Head VTK) seen in the character creator only so far; mirror, first
  person and photo mode not seen in game yet. Head tattoos on a vanilla head (female or male): see Troubleshooting.
- Face sculpting changed at the ripperdoc after a build has not been QA'd yet (the head shell follows the face morphs
  on an already sculpted face).
- Single-file PyInstaller executables are sometimes flagged by antivirus heuristics. The source is here; you can run `python InkFlowBuilder.py` instead.

## Credits and licence

- **thrasherpass**: CCXL Tattoo Toolkit (Nexus 20279), whose templates define the switcher layout.
- **psiberx**: ArchiveXL, and **WolvenKit** team: WolvenKit Console, downloaded at first run, not shipped.
- The tattoo authors whose archives you build with. This tool redistributes nothing of theirs. A built
  `Ink_Flow.archive` contains their textures: it is for your own game, do not share it without their permission.

MIT (this tool). Source: https://github.com/doublescotch/ink-flow
