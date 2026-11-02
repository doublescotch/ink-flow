# Nexus posts — drafts (English, Hell_Kaiser posts them)

Written 2026-11-02 after the first 15 comments (ETUDE § 17). One block per reply ; paste as is or trim.

## To the three EBBRB reports (Lorasyl, Bransburk, cybercock2067) — one reply each, or one sticky

Thanks for the report. I downloaded Hyst's EBBRB 5.0.0 and ran it through the builder's engine: it is
accepted exactly like Angel (same mesh layout, same materials), so the recipe itself is not the problem.

What I suspect instead: the builder did not SEE your body mod when it built, and fell back to the
vanilla body. The tattoo shells are copies of the body mesh that was active at build time; a vanilla
shell sits under the skin of a bigger body, so the slots show up but nothing is drawn. This happens
when the body is not in archive\pc\mod as a real file at build time:
- Vortex with "REDmod deployment" (the body lives in <game>\mods\...): not read by 1.0.0.
- Mod Organizer 2: the game folder is virtual; run InkFlowBuilder.exe THROUGH MO2 (add it as an
  executable) so it sees your mods.
- A modlist.txt in archive\pc\mod: 1.0.0 ignores it.

~~Could you paste the "2. active meshes" lines of the builder log (the text box under the list,
right after Build)? They look like "Body : 006_Angel_Body.archive". If yours says "Body : base game",
that is it. Also tell me which mod manager you use. 1.0.1 will read REDmod folders and modlist.txt,
show the detected body in the window (red when it is the vanilla one), and write a build.log you can
send.~~ (wording for 1.0.0 ; replaced below once 1.0.1 is uploaded, 2026-11-02 18 h 30)

Please update to 1.0.1: it reads REDmod folders and modlist.txt, and the window now has a "Body mesh"
line that names the body archive the shells will be copied from. If that line is red ("base game")
while you play with EBBRB, the builder does not see your body: MO2 users, start the builder through
MO2; otherwise tell me where your EBBRB archive lives. If the line is green with your EBBRB archive,
Build, Install, and if nothing shows still, post the build.log from the data folder (button "Open data
folder"): its second block says which archive each mesh came from. I have not seen EBBRB in game
myself, only checked that its meshes pass the builder, so your log is what will settle it.

## To 0xVyper (dynamic / no rebuild)

Thanks, I looked into it before building this. The blocker is on the engine side: a resource is
addressed by the hash of its path, and every VTK tattoo ships the same path (v_overlay.xbm). Nothing at
runtime, ArchiveXL included, can say "this archive goes in slot 2": each tattoo needs its own path, and
the shells need a copy of your actual body mesh, which only WolvenKit can write. So some packing step
stays. What I can do in that direction: a "Scan game folder" button that finds the VTK tattoo archives
you already have (archive\pc\mod and REDmod), lists them, and moves them aside at install, so there is
nothing to collect by hand. Rebuild stays a one-click step when you add a tattoo.

## Vanilla body (to add to the sticky / description once 1.0.1 is out)

Known issue in 1.0.0: with NO body mod at all (pure vanilla body), arm tattoos stop the build with
"unsupported body mod" (the vanilla arm meshes store their materials differently), and the first-person
shells break the mirror. Fixed in 1.0.1: the vanilla body was played in game (creator, mirror, first
person, photo mode, 2026-11-02). Update, Build, Install.
