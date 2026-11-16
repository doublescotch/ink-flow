# Changelog

Same text as the "Changelogs" tab of the [Nexus page](https://www.nexusmods.com/cyberpunk2077/mods/36814).

## 1.4.0 (2026-11-04)

- Arms of either family on arms of either family: a UV Framework tattoo on vanilla / VTK arms (Angel…), a VTK tattoo on UV Framework arms (Solo…), now gets its arm part converted to your arms' layout instead of skipped (same arm, two unwrappings: each texel moves to the same spot of the arm). Once per tattoo, cached. Needs UV Framework Texture in the game (its arm meshes are the map); without it the arms are skipped as in 1.3.0 and build.log says why. The converted arm is a resampling: a little softer, and a hairline may show on a seam.
- Texture header check: textures whose header declares a single mip over a buffer that holds the full chain (Kala Japanese V2 VTK / UV / With Sleeves, female and male packs) are rebuilt by WolvenKit so the header matches the data (BC7 kept). build.log lists them.
- First person fixed: the body tattoo now shows when V looks down or sits (two users reported it). The game draws V's first-person body with two meshes, the torso and the legs, each with its own mask; Ink Flow now copies both instead of one mesh with the wrong mask (on Angel that mask was the lower legs).
- Shins fixed in photo mode, the inventory and first person (holes that moved with the camera): the game draws the lower legs with a separate "flat feet" mesh there, and with a raised-feet copy of the body in the creator. Each tattoo now has a shell for both, in the game's own feet groups.
- The built archive is bigger (about a third more for the same tattoos: the new leg and torso shells).
- Carries 1.2.0 (per-tattoo opacity, Body meshes in use table) and 1.3.0 (UV Framework tattoos, skin-only shells, Angel feet), never uploaded.
- The conversion cache is rebuilt once. Rebuild and install.

## 1.3.0 (2026-11-04)

- UV Framework tattoos (Solo-type bodies) are built, no longer "ignored": a UV tattoo is one texture for body + both arms (plus a head file for some), and it becomes body + arm L + arm R shells. The arm shells are built only when the arm meshes your game loads are UV Framework arms; on vanilla / VTK arms (Angel…) the body part is built and build.log says the arms were skipped (the two arm layouts differ; a conversion may come later). The head overlay of a UV pack is built like a VTK head tattoo.
- Angel + UV tattoo: the body shell reads a copy of the texture with the arm part cleared, so the feet stay bare (Angel unwraps them into the part of the texture a UV tattoo uses for the arms). One WolvenKit pass per texture the first time (10 to 60 s), cached afterwards.
- Tattoo shells no longer cover non-skin chunks of your meshes (the personal link port on the left forearm, Songbird's cyber plates): a tattoo is skin only. Rebuild and install.
- Per-tattoo opacity accepts 0.1 to 2.0 like the Default opacity (1.2.0 refused above 1.0 in the column).
- The texture cache is rebuilt once (new file list).

## 1.2.0 (2026-11-04)

- Per-tattoo opacity (requested in the posts): a new Opacity column in the tattoo list. Double-click a cell (0.1 to 1.0), or select several rows and press Opacity…. Empty = the Default opacity of the options (the old Opacity setting), shown in brackets. The value applies to all of that tattoo's shells (body, arms, head, first person). Rebuild and install.
- The detected body meshes are now a table: female V and male V side by side, one row each for body, arms and head, the archives they win over in small grey type underneath. Same detection as before, easier to read.
- Nothing else changes: with no per-tattoo opacity set, a build is the same as with 1.1.0.

## 1.1.0 (2026-11-03)

- Male V: male VTK tattoo packs (v_masc_overlay, masculine arms, male head) get their own Ink slots in male V's character creator, built from the same window, alongside the female ones. Seen in game on the vanilla male body and on Gymfiend VTK 1.4.3 + MV Head VTK (character creator).
- Tattoos showing as rows of dashes or not at all: their texture had a truncated mip chain (several male packs). The builder now re-encodes such textures with WolvenKit (full mip chain); every other texture is still copied byte for byte. Rebuild and install.
- The Body mesh line shows the male body mod too when one is found.
- Female builds are unchanged (same files, byte for byte, as 1.0.1 for the same tattoos).

## 1.0.1 (2026-11-02)

- First person fixed: the arm tattoos showed holes and slid under the skin when the arms moved, because the first-person shells were never applied (the slot's switcher did not drive its hidden first-person companion, as the game's own body_tattoo drives fpp_body_tattoo) and the third-person arm shells were drawn over the first-person arms. Rebuild and install.
- Vanilla body (no body mod) now works in game: 1.0.0 stopped with "unsupported body mod" on the vanilla arm meshes, and the first-person shells broke the mirror (same cause as above). Seen in game: creator, mirror, first person, photo mode.
- .NET 10 runtime missing? One button installs it (Microsoft's x64 Runtime installer, 30 MB, version and SHA-256 checked, silent install with the usual Windows elevation prompt). No more hunting the right link among the SDK / ASP.NET / Desktop boxes.
- Body detection follows the game's real load order: archive\\pc\\mod (modlist.txt honoured), then REDmod folders (mods\\*\\archives, load order honoured), then the base game. 1.0.0 only read archive\\pc\\mod alphabetically, so a body deployed as REDmod or seen through MO2's virtual folder was missed and the shells were built on the vanilla body (slots visible, nothing drawn).
- The window shows which body / arms / head archives the shells will be copied from (red when it is the base game).
- New "Scan game folder…" button: finds the VTK tattoo archives your game already loads, copies them to the builder's folder and adds them.
- build.log written in the data folder at each build (send it when something does not show).
- The conflict check at install also looks at REDmod folders.

## 1.0.0 (2026-11-02)

- First release.
