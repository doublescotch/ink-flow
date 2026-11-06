# Nexus posts — drafts (English, Hell_Kaiser posts them)

One block per post; paste as is or trim. The individual replies of 2026-11-02 (EBBRB ×3, 0xVyper,
vanilla body) were removed on 2026-11-04 at Hell_Kaiser's request: posted, and superseded by the
stickies (they stay in git history, commit `546200f` and before).

## Sticky 1.4.0 (replaces the 1.2.0 one below, to post with the 1.4.0 upload ; rewritten 2026-11-06 after his QA of
## the rebuilt pack : the hold of 2026-11-05, 2 h, is lifted, first person and photo mode are now seen)

```
1.4.0 IS OUT: first person and shins fixed, UV Framework tattoos, arm conversion between the two families, per-tattoo opacity. Update, Build again, Install.

What's new (full list in the Changelogs tab; 1.2.0 and 1.3.0 were never uploaded, 1.4.0 carries them):
- First person fixed: the body tattoo now shows when you look down or sit (thanks to those who reported it).
- Shins fixed in photo mode, the inventory and first person: no more holes moving with the camera.
- UV Framework tattoos (the one-file body + arms packs made for -KS- UV Texture Framework) are supported: drop them in the list like VTK ones, each gets its own Ink slot.
- Arms of either family on arms of either family: a UV tattoo on vanilla / Angel arms, a VTK tattoo on Solo's UV arms, gets its arm part converted to your arms' layout (same arm, two unwrappings). This needs -KS- UV Texture Framework in your game; without it the arms of the other family are skipped and build.log says why.
- Per-tattoo opacity column (0.1 to 2.0) and a "Body meshes in use" table at the top of the window (Female V / Male V, Body / Arms / Head).
- Textures with a wrong header (some Kala Japanese V2 files) are rebuilt automatically.

Tested in game (2.5, fresh install): female V on Angel (+ Vanilla Refits, VTK Vanilla HD Head, UV Framework 3.2.1) and on the vanilla body, 42 tattoos VTK and UV: body and arms clean in the creator, at the mirror, in photo mode, in the inventory and in first person. Male V on the vanilla body: creator. Solo 2.0: creator and mirror before the first-person fix, not since (it crashed at save load on our bench, Solo's page reports the same).

Known: on Angel every tattoo stops at the ankles (Angel's feet live in the part of the texture that tattoos do not paint; resampling them is next); in the creator the shin ink ends a little lower than elsewhere; a tattoo past the wrist can stop straight on the back of the hand; heels / shoes feet states and cyberarms not tested; head tattoos on a vanilla head (female or male) do not show; very faint overlays (freckles) do not show through the decal.

Ink Flow only needs ArchiveXL (and the RED4ext it runs on), plus the UV Framework if you want arm conversion.

Still nothing on V? Post your build.log here (button "Open data folder"), with your body mod and your mod manager.
```

## ~~Sticky 1.2.0~~ replaced by the 1.4.0 one above (never posted: 1.2.0 was never uploaded, 2026-11-04)

```
1.2.0 IS OUT: per-tattoo opacity, and a clearer view of the bodies the builder found. Update, Build again, Install.

What's new (full list in the Changelogs tab):
- Per-tattoo opacity (thanks for the request!): the tattoo list has a new Opacity column. Double-click a cell and set 0.1 to 1.0, or select several rows and press "Opacity…". Leave it empty to use the Default opacity of the options (shown in brackets). It applies to all of that tattoo's parts: body, arms, head, first person. Rebuild to apply.
- The detected bodies are now a table at the top of the window: Female V and Male V side by side, one row each for Body, Arms and Head. Green = the body mod archive the shells will be copied from, grey "base game" = vanilla. A red line under the table means the builder sees no body mod at all.
- Nothing else changes: if you set no per-tattoo opacity, your build is the same as with 1.1.0, file for file.

Check the table before you build: if you play with a body mod (Angel, Gymfiend...) and its column says "base game", the builder does not see it and the tattoos will show nothing on V. MO2 users: start InkFlowBuilder.exe THROUGH MO2 (add it as an executable).

Tested in game (2.5): female V on Angel (+ VTK Vanilla HD Head) and on the vanilla body; male V on the vanilla body and on Gymfiend VTK 1.4.3 + MV Head VTK (character creator so far: mirror, first person and photo mode on male V not checked yet). VTK Vanilla HD body: reported working by a user.

Known issue: head tattoos on a VANILLA head (no VTK head mod) do not show yet. With a VTK HD head they work. That is what I am working on next.

Ink Flow only needs ArchiveXL (and the RED4ext it runs on). Codeware, TweakXL, CET: not needed by Ink Flow.

Still nothing on V? Post your build.log here (button "Open data folder"), with your body mod and your mod manager.

Still planned: vanilla head, male head tattoos, cyberarms (not tested yet), UV tattoos. A video of the full process is coming.
```

## ~~Sticky 1.1.0~~ replaced by the 1.2.0 one above (posted with the 1.1.0 upload, 2026-11-03)

```
1.1.0 IS OUT: MALE V is supported. Update, Build again, Install.

What's new (full list in the Changelogs tab):
- Male V: male VTK tattoo packs (the ones that replace v_masc_overlay / masculine arms / male head) now get their own Ink slots in male V's character creator. Same window, same build: load female and male tattoos together, each one goes to the right V. No selector needed, the builder reads which body each tattoo file is made for.
- Each V gets shells copied from HER / HIS own active body: Angel for female V and vanilla for male V (or the other way round, or Gymfiend + vanilla...) all work in one build.
- Tattoos showing as rows of dashes, or not at all: their texture had a truncated mip chain (several male packs). The builder now re-encodes those textures automatically; every other texture is still copied byte for byte. If you saw that, rebuild.
- Female V users: nothing changes for you (same files, byte for byte, as 1.0.1). Update anyway, no need to rebuild unless a tattoo showed as dashes.

Tested in game (2.5): female V on Angel (+ VTK Vanilla HD Head) and on the vanilla body; male V on the vanilla body and on Gymfiend VTK 1.4.3 + MV Head VTK (character creator so far: mirror, first person and photo mode on male V not checked yet). VTK Vanilla HD body: reported working by a user, thanks!

Known issue: head tattoos on a VANILLA head (no VTK head mod) do not show yet. With a VTK HD head they work. Looking into it next.

Male V with a body mod: check the "Body mesh" lines at the top of the window. When the builder sees your male body mod, a "Male V body mesh" line names it. No such line while you use Gymfiend (or another male body)? The builder does not see it (MO2: start InkFlowBuilder.exe THROUGH MO2) and the male tattoos would show nothing on V.

Ink Flow only needs ArchiveXL (and the RED4ext it runs on). Codeware, TweakXL, CET: not needed by Ink Flow.

Still nothing on V? Post your build.log here (button "Open data folder"), with your body mod and your mod manager.

Still planned: male head tattoos (testing next), vanilla head, cyberarms (not tested yet), UV tattoos. A video of the full process is coming.
```

## ~~Sticky 1.0.1~~ replaced by the 1.1.0 one (replaced the one of 2026-11-02 7:55 AM)

```
1.0.1 IS OUT: update, Build again, Install. Your old 1.0.0 build has a first-person bug, rebuilding fixes it.

What 1.0.1 fixes (full list in the Changelogs tab):
- First person: arm tattoos had holes and slid under the skin. Fixed.
- Vanilla body (no body mod at all): now works, tested in game (creator, mirror, first person, photo mode).
- REDmod and MO2: the builder now finds a body installed as REDmod. MO2 users: start InkFlowBuilder.exe THROUGH MO2 (add it as an executable), otherwise it cannot see your mods.
- The window now shows which body the builder found ("Body mesh" line). Red = base game. If you play with a body mod and that line is red, the build will show nothing on V: fix that first.
- .NET 10 Runtime: one button installs the right one. No more guessing on Microsoft's page.
- build.log written at every build, in the data folder (button "Open data folder").

Tested in game: Angel body (+ VTK Vanilla HD Head) and vanilla body, on 2.5. Other VTK bodies (EBBRB...) pass the builder's checks but I have not seen them in game yet. The tattoo shells are copies of YOUR body's meshes, so the body mod itself must work on 2.5. Not on 2.31.

Ink Flow only needs ArchiveXL (and the RED4ext it runs on). Codeware, TweakXL, CET: not needed by Ink Flow.

Still nothing on V? Post your build.log here (paste it or attach it), with your body mod and your mod manager. That file tells me which archive each mesh came from.

Not in 1.0.1, still planned: cyberarms (not tested yet), male V (vanilla, then Gymfiend), UV tattoos. A video of the full process is coming.
```
