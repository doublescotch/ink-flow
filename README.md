# Ink Flow - VTK CCXL Tattoo Loader

Turn every VTK tattoo archive you own into stackable slots ("Ink 1" to "Ink 9") in the character creator, ripperdoc and mirror. Female and male V; body, arms, head, first person. Built on your PC; nothing from other authors is redistributed.

Nexus page and download: [nexusmods.com/cyberpunk2077/mods/36814](https://www.nexusmods.com/cyberpunk2077/mods/36814).
The text below is the description of that page. The builder's own notes (run from source, build the
exe) are in [`builder/README.md`](builder/README.md); versions: [`CHANGELOG.md`](CHANGELOG.md); licence: MIT
([`builder/LICENSE`](builder/LICENSE)).

## What it does

VTK tattoos normally replace the vanilla body tattoo texture: one tattoo file, one look, and two tattoo mods fight for the same slot. Ink Flow adds its own slots to the character creator ("Ink 1", "Ink 2", … up to 9), and each slot lists **every** VTK tattoo archive you include in the build. Pick one per slot, stack them, change them at the ripperdoc or at the apartment mirror. Body, left arm, right arm and head tattoos are all handled, and a tattoo that only covers the head or one arm stays on that part. The tattoos follow V in first person (arms, and the body when you look down). Female and male V (since 1.1.0): a male tattoo pack goes to male V's slots, a female one to female V's, from the same build.

Ink Flow ships **no tattoo**. It ships a small Windows builder: you drop your tattoo archives in, give each one the name you want to read in the creator, click Build, click Install. The result is one **Ink_Flow.archive** + **.xl** in your game, built on your machine from your files.

## Requirements

- Cyberpunk 2077 2.x (PC). Built and tested on 2.5.
- [ArchiveXL](https://www.nexusmods.com/cyberpunk2077/mods/4198) and what its page asks for (RED4ext; Redscript for ArchiveXL's script features). Ink Flow itself needs nothing else: no Codeware, no TweakXL, no CET.
- The [Microsoft .NET 10 runtime](https://dotnet.microsoft.com/download/dotnet/10.0) (x64), needed by WolvenKit Console. Since 1.0.1 the builder installs it for you: one button, Microsoft's own installer (30 MB, version and SHA-256 checked, silent install, the usual Windows elevation prompt). If you prefer the manual way: on Microsoft's page take the bottom-left box ".NET Runtime", Windows, x64 Installer, not the SDK or the Desktop runtime (see screenshot). WolvenKit Console is downloaded from GitHub on first run (45 MB, version pinned and checked).
- Female V with the vanilla body or a body mod of the VTK family (Angel, EBBRB…), or male V with the vanilla body or Gymfiend VTK: see "What works with what" below. The screenshot shows the archives of an Angel setup.

## What works with what (1.4.0)

- **Angel body** (+ Vanilla Refits, VTK Vanilla HD Head): seen in game, every feature: creator, ripperdoc, mirror, first person, photo mode, body / arms / head tattoos, stacking. This is the setup Ink Flow was developed on. 1.4.0: seen again on a game rebuilt from scratch (Angel + Vanilla Refits + VTK Vanilla HD Head + UV Framework 3.2.1), the whole test pack, 42 tattoos VTK and UV with 19 arm conversions: body and arms clean in the creator, at the mirror, in photo mode, in the inventory and in first person (looking down, sitting), with the VTK and the UV version of the same tattoo.
- **Vanilla body** (no body mod at all): seen in game, same views, body and arms (1.4.0: creator, mirror, photo mode, inventory, first person). Head tattoos on the vanilla head (no VTK head mod) do not show: known, being looked at; with a VTK HD head they work.
- **VTK Vanilla HD body**: reported working by a user, and passes the builder's checks entirely (body, arms, first-person arms).
- **Male V, vanilla body** and **Gymfiend VTK 1.4.3 + MV Head VTK**: 1.4.0 seen in game on a save with male V, the builder run as a user over a whole setup (Angel for female V, Gymfiend for male V): body and arm tattoos at the ripperdoc, in the inventory, in photo mode and in first person, as on female V. On Gymfiend, UV tattoos (arms converted) leave V's right shoulder bare (seen with OneSlowZZ Pirate Vince UV); a VTK tattoo on that shoulder not seen yet. Male face tattoos do not show, on the vanilla male head nor on MV Head VTK (seen with Kala Halloween Skeleton).
- **Other VTK bodies**: the builder reads the body, arm and head meshes your game actually loads and copies them. EBBRB 5.0 passes the builder's checks (measured on its archive, not seen in game yet). Any body mod whose meshes keep local materials and the standard skin appearance passes; a body mod that does not pass stops the build with "unsupported body mod" rather than producing a broken result. The body mod must itself work on your game version: the tattoo shells are copies of its meshes, so a body not updated for 2.5 will not get better under Ink Flow.
- **UV Framework bodies** (1.3.0, arms of both families since 1.4.0): Solo 2.0 + UV Framework Texture 3.2.1 + Solo arms UV: body and both arms seen in the character creator with UV tattoos, and in the creator and at the mirror with a VTK tattoo whose arms are converted (see "Arms and families" below); not seen again since the first-person and legs fix. Photo mode on Solo: not seen, our Solo bench crashed at save load (Solo's own page reports the same on a clean install; the same tattoos on Angel never crashed), so Solo is parked for now; in first person on Solo the belly uses the vanilla torso mask (Solo's .app cannot be read by WolvenKit Console). Songbird 2.0 body: builds (its cyber plates are left out of the shell), not seen in game.
- **Not tested**: cyberarms (Mantis Blades, Gorilla Arms… the tattoo shells cover the arms fully; what happens on a cyberarm has not been looked at).

## Arms and families (1.4.0)

VTK and UV tattoos share one body layout: the body part of a tattoo of either family fits every body, vanilla, VTK or UV, and the builder always builds it. The arms differ: UV Framework arms are unwrapped into the left strip of the body texture (a UV tattoo is one file for body + arms), vanilla and VTK arms into textures of their own (a VTK tattoo ships separate arm files). The builder reads the layout of the arm meshes your game loads. A tattoo of the same family is drawn as is. Since 1.4.0 a tattoo of the other family gets its arm part **converted** to your arms' layout: same arm, two unwrappings, each texel is moved to the same spot of the arm (a UV sleeve onto Angel's or vanilla arms, a VTK sleeve onto Solo's UV arms). Once per tattoo, cached: about 20 s per arm for a UV tattoo, up to a minute for a VTK arm going onto UV arms. This needs [-KS- UV Texture Framework](https://www.nexusmods.com/cyberpunk2077/mods/3783) in your game (developed on its 3.2.1 archive) (its arm meshes are the map between the two layouts, even when your body mod overrides them); without it the arms are skipped as in 1.3.0 and build.log says why. Angel unwraps its feet into that strip: under a UV tattoo the body shell reads a copy of the texture with the strip cleared (made once per texture, cached), so the feet stay bare instead of showing arm ink (VTK textures never paint there).

## How to use

1. Unzip, run **InkFlowBuilder.exe**. The Setup box shows: game folder, ArchiveXL, .NET 10, WolvenKit Console. Fix what is red (the buttons do it: Install .NET Runtime 10, Download WolvenKit Console). Under it, the **Body meshes in use** table names, for female V and male V, the archive your game loads for the body, the arms and the head (the shells are copied from these): green = a mod archive, grey "base game" = the vanilla mesh. A red line under the table means no body mod was seen at all: right only if you really play on the vanilla body; if you use a body mod, see "Slots visible but nothing on V?" below before building.
2. **Scan game folder…** finds the VTK and UV tattoo archives your game already loads (archive\\pc\\mod and REDmod folders) and adds them. Or **Add files…** / **Add folder…** with .archive files from anywhere. The list shows what each file covers: Body, Arm L, Arm R, Head. Files Ink Flow cannot use are greyed out with the reason.
3. Double-click a name to rename it (20 characters max, that is what you read in the creator). Uncheck what you do not want. The **Opacity** column sets one tattoo's opacity (double-click, 0.1 to 2.0, or select several rows and press Opacity…); empty = the Default opacity of the options, shown in brackets.
4. Choose the number of slots (1 to 9: how many tattoos V wears at once, in addition to the vanilla ones), whether the slots also appear at the apartment mirror, and whether to build the first-person shells (on by default).
5. **Build** (about two minutes for 18 tattoos the first time, less afterwards), then **Install into game** with the game closed. If the original tattoo archives are still in archive\\pc\\mod the builder tells you and can move them to a backup folder (left in place, they paint a permanent tattoo under the slots).
6. In game: character creator, ripperdoc, mirror → "Ink 1", "Ink 2" under Body Tattoos.

Add tattoos later? Add the files, Build, Install. Your character keeps the tattoos already chosen in each slot (a tattoo keeps its internal id across rebuilds, even if you rename the file). Ink Flow keeps its data in C:\\Users\\\<you>\\AppData\\Local\\InkFlow (the "Open data folder" button): your list, the WolvenKit download, a cache that makes the next build fast, your previous Ink_Flow.archive files as backups, and build.log.

**Changed your body mod?** Build again. The shells that carry the tattoos are copies of the body and head meshes that were active when you built.

## Slots visible but nothing on V?

The shells are copies of the body mesh the builder saw when you built. If the Body meshes in use table said "base game" while you play with a body mod, the shells are vanilla-shaped and hide under the skin of your body: the slots are there, nothing is drawn. Make the table show your body mod, then Build and Install:
- Mod Organizer 2: start the builder through MO2 (add it as an executable), otherwise it does not see MO2's virtual folder.
- REDmod (mods\\\<name>\\archives): read since 1.0.1, in the game's order (mods.json / REDmod load order).
- Vortex or manual install: the body archive must be in archive\\pc\\mod; 1.0.1 honours modlist.txt.

Still wrong? Open the data folder and post **build.log** from a fresh build: its second block names the archive each mesh was copied from.

## How it works

For each tattoo file the builder extracts the texture(s), copies your active body / arm / head meshes with their skin materials replaced by the vanilla tattoo decal material, points the decal at the tattoo texture, and writes one appearance per tattoo and per slot plus the character-creator entries (CCXL). Since 1.3.0 a UV Framework texture is pointed at by the body and both arm shells at once (one copy of the texture), and only the skin chunks of a mesh are shown in a shell. Since 1.4.0 an arm texture drawn for the other arm layout is resampled through the two arm meshes (the UV Framework arm and your arm share the vertices, each with its own unwrapping) into a texture of your arms' layout, written by WolvenKit with a full mip chain. The head shell carries a copy of the face morph target, so it follows face sculpting. The game draws V's lower legs with other meshes than the body: in the creator a second copy of the body with the feet raised, everywhere else a separate "flat feet" mesh; since 1.4.0 each tattoo gets a shell for both, listed in the game's own (hidden) feet groups, so the shins keep their ink in every view. First person works like the vanilla tattoos: a hidden companion of each slot drives first-person shells (a copy of your first-person torso mesh, the legs, copies of your first-person arm meshes), each through the chunk mask of the game's own first-person appearance. Male V needs no companion: the game shows his third-person body and arms in first person, so his shells are listed for both views, as the vanilla male tattoos are. The textures are copied byte for byte (what you see is the author's tattoo, unchanged), except those whose mip chain stops early (several male packs): they render as broken stripes through the decal, so the builder re-encodes them with WolvenKit (same image, full mip chain, uncompressed: about 4 MB in the archive, about 85 MB of video memory while a 4096 tattoo is worn). The build log lists them. Everything is generated by WolvenKit Console from JSON; the source of the builder is public.

## Known limits (1.4.0)

- Head tattoos on a vanilla head (no VTK head mod, female or male) do not show yet, nor on male V's MV Head VTK.
- Character creator and apartment mirror: the ink of the shins ends a little lower than in photo mode, the inventory or first person, with a stepped edge. Same texture and same unwrapping in both shells (measured), so it is not the author's art; cosmetic, being looked at.
- Feet on Angel: Angel unwraps its feet into the arm strip of the body texture, which VTK textures do not paint and which the builder clears for UV textures. On Angel every tattoo therefore stops in a straight line at the ankle, even one the author painted down to the toes (seen with Arasaka Workshop Vibrant body paints, which cover the feet on the vanilla body). Angel-specific; next (resampling the feet the way the arms are).
- Hands: a tattoo that goes past the wrist can stop in a straight line on the back of the hand (seen with Samurai). Being looked at.
- Feet states with shoes (high heels, flat shoes) not tested: barefoot only so far.
- Male V on Gymfiend VTK: a UV tattoo (arms converted) leaves V's right shoulder bare (seen with OneSlowZZ Pirate Vince UV); a VTK tattoo on that shoulder not seen yet. Being looked at.
- Arm conversion (1.4.0): the converted arm is a resampling of the author's texture: a little softer than the original, and a hairline may show on a seam where the two unwrappings cut the arm differently. VTK arms onto UV arms (Solo): seen in the creator. UV arms onto vanilla / VTK arms (Angel): seen in the creator and at the mirror for every UV tattoo of the test pack. Needs UV Framework Texture in the game, see "Arms and families".
- Very faint overlays (freckles, beauty marks: GetTenSO FrecklesV, VTK or UV) do not show through the tattoo decal, even at opacity 2.0: they are painted to melt into the skin's own overlay layer. Keep those as plain overlay archives.
- Cyberarms not tested (see above).
- Text options in the creator, no icons yet.
- Face sculpting changed at the ripperdoc after a build has not been QA'd (the head shell follows the morphs of an already sculpted face, so it should be fine).

## Antivirus

The builder is a single-file PyInstaller executable (Python + tkinter). Some antivirus heuristics flag such files. The SHA-256 of the exe is in the file description; the source is on GitHub and you can run it with Python instead (*python InkFlowBuilder.py*).

## Source

MIT. [github.com/doublescotch/ink-flow](https://github.com/doublescotch/ink-flow) (builder, engine). Issues and ideas welcome there or in the posts tab.

## Credits

[Kala](https://www.patreon.com/kalahira), [Bedellia](https://www.nexusmods.com/profile/bedellia?gameId=3333) and [Shivakoko](https://www.nexusmods.com/profile/shivakoko) for the tattoos in the screenshots. Please help me find the authors of the Samurai and Garden Bloom tattoos, they are listed as "Unknown" in the names. Amazing works; this project would not exist without their art to give it a point.
thrasherpass for the [CCXL Tattoo Toolkit](https://www.nexusmods.com/cyberpunk2077/mods/20279), the template resource whose switcher layout Ink Flow follows. psiberx for ArchiveXL and RED4ext. The WolvenKit team for WolvenKit Console (downloaded by the builder, not shipped).
