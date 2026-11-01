"""Ink Flow Builder, command line (same engine as the GUI ; replaces tools/inkflow_build.py v0.3).

  python -I inkflow_cli.py --in <folder> [--game <Cyberpunk 2077>] [--cli <WolvenKit.CLI.exe>] [--slots 2]
         [--slot-index 1041] [--slot-title "Ink {n}"] [--max-name 20] [--alpha 1.0] [--no-mirror] [--route1]
         [--out <dir>] [--work <dir>] [--catalogue <json>] [--name Ink_Flow] [--list] [--install]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkflow import core, env  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True, help="folder of the tattoo .archive files")
    ap.add_argument("--game", default=None, help="game folder (default: detected)")
    ap.add_argument("--cli", default=None, help="WolvenKit.CLI.exe (default: the one the builder downloaded)")
    ap.add_argument("--work", default=env.WORK_DIR)
    ap.add_argument("--out", default=env.OUT_DIR)
    ap.add_argument("--catalogue", default=env.CATALOGUE_FILE, help="slug catalogue (content id -> slug, name)")
    ap.add_argument("--name", default="Ink_Flow")
    ap.add_argument("--slots", type=int, default=2)
    ap.add_argument("--slot-index", type=int, default=1041)
    ap.add_argument("--slot-title", default="Ink {n}")
    ap.add_argument("--max-name", type=int, default=20)
    ap.add_argument("--alpha", type=float, default=1.0)
    ap.add_argument("--no-mirror", action="store_true", help="creator + ripperdoc only (default: mirror too)")
    ap.add_argument("--route1", action="store_true")
    ap.add_argument("--list", action="store_true", help="analyse only, nothing written")
    ap.add_argument("--install", action="store_true", help="copy the result into archive\\pc\\mod (game closed)")
    a = ap.parse_args()

    game = a.game or (env.find_game_candidates() or [None])[0]
    if not game or not env.valid_game(game):
        sys.exit("game folder not found or invalid; pass --game")
    cli = env.find_wolvenkit(a.cli)
    if not a.list and not cli:
        sys.exit("WolvenKit CLI not found; pass --cli or run the GUI once to download it")
    if not os.path.isdir(a.inp):
        sys.exit("input folder not found: " + a.inp)

    log = lambda *x: print(*x, flush=True)  # noqa: E731
    entries = core.scan_folder(a.inp)
    cat = core.Catalogue(a.catalogue)
    cat.import_legacy(a.inp, entries, log)
    cat.ensure(entries)
    if a.list:
        for e in entries:
            if e.supported:
                print(f"  + {e.file} -> {cat.slug(e)} \"{cat.name(e)}\": {', '.join(e.target_codes)}")
            else:
                print(f"  - {e.file} ignored: {e.ignored_reason}")
        codes = sorted({c for e in entries for c in e.target_codes})
        for c, (who, _) in core.active_owners(game, codes).items():
            print(f"  active {c}: {who}")
        conf = core.conflicting_archives(game, [e for e in entries if e.supported], exclude_names=(a.name + ".archive",))
        if conf:
            print("  VTK tattoo archives still in the game (permanent overlay):", ", ".join(conf))
        return

    s = core.Settings(game=game, cli=cli, work=a.work, out=a.out, name=a.name, slots=a.slots, slot_index=a.slot_index,
                      slot_title=a.slot_title, max_name=a.max_name, alpha=a.alpha, mirror=not a.no_mirror, route1=a.route1)
    try:
        res = core.run_build(s, [e for e in entries if e.supported], cat, log)
        if a.install:
            conf = core.conflicting_archives(game, res.items and [it.entry for it in res.items], exclude_names=(a.name + ".archive",))
            if conf:
                print("  NOT moved (decide yourself), archives that paint a permanent overlay:", ", ".join(conf))
            core.install(res, game, env.BACKUP_DIR, log)
    except core.BuildError as e:
        sys.exit("ERROR: " + str(e))


if __name__ == "__main__":
    main()
