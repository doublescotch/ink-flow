"""Ink Flow Builder : Tk interface (first cut, v0.4). One window : setup line, tattoo list, options, log.
All strings live in `T` (English ; a second language = a second table)."""
import ctypes
import os
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, simpledialog, ttk
from tkinter.scrolledtext import ScrolledText

from . import APP_NAME, MOD_NAME, VERSION, core, env
from .config import Config

T = {
    "title": f"{APP_NAME} {VERSION}",
    "setup": "Setup",
    "game": "Game folder",
    "browse": "Browse…",
    "detect": "Detect",
    "game_ok": "Game: OK",
    "game_bad": "Game: not found — pick the Cyberpunk 2077 folder",
    "axl_ok": "ArchiveXL: {v}",
    "axl_bad": "ArchiveXL: MISSING (required)",
    "dotnet_ok": ".NET {m} runtime: OK",
    "dotnet_bad": ".NET {m} runtime: MISSING",
    "wk_ok": "WolvenKit Console: OK",
    "wk_bad": "WolvenKit Console: not installed",
    "wk_download": "Download WolvenKit Console ({mb} MB)",
    "wk_locate": "Locate…",
    "get_dotnet": "Get .NET {m}…",
    "get_axl": "Get ArchiveXL…",
    "body_wait": "Body mesh: looking in the game folder…",
    "body_line": "Body mesh: {b}   |   arms: {a}   |   head: {h}",
    "body_vanilla": ("Body mesh: BASE GAME (vanilla). No body mod seen in archive\\pc\\mod or mods\\. Fine if you use none; "
                     "if you DO use one, the builder cannot see it (Mod Organizer 2: run the builder through MO2) — see README."),
    "tattoos": "Tattoos (.archive files of VTK tattoos you own)",
    "add_files": "Add files…",
    "add_folder": "Add folder…",
    "scan_game": "Scan game folder…",
    "scan_result": ("{n} VTK tattoo archive(s) found in your game, copied to the builder's tattoo folder and added to the list:\n\n{l}\n\n"
                    "At install time the builder will offer to move the originals to the backup folder "
                    "(left in place they paint a permanent tattoo under the slots)."),
    "scan_none": "No VTK tattoo archive found in archive\\pc\\mod or mods\\ (REDmod).",
    "log_note": "\n\nThe full log is in build.log in the data folder (button \"Open data folder\").",
    "remove": "Remove",
    "rename": "Rename…",
    "check_all": "Check all",
    "uncheck_all": "Uncheck all",
    "col_on": "✓",
    "col_file": "File",
    "col_targets": "Targets",
    "col_name": "Name in game",
    "col_note": "Note",
    "hint_names": "Double-click a name to edit it (max {n} characters, shown in the character creator). Click ✓ to include or exclude.",
    "options": "Options",
    "slots": "Slots",
    "mirror": "Also available at the apartment mirror",
    "fpp": "First person (arms and body seen by V)",
    "alpha": "Opacity",
    "out": "Output folder",
    "open": "Open",
    "build": "Build",
    "install": "Install into game",
    "clear_cache": "Clear cache",
    "about": "About",
    "ready": "Ready.",
    "building": "Building…",
    "cancel": "Cancel",
    "cancelling": "Cancelling…",
    "cancelled": "Build cancelled. Nothing was installed.",
    "quit_busy": "A build is running. Cancel it and quit?",
    "quit_download": "WolvenKit Console is still downloading. Quit anyway?",
    "built": "Built {name}.archive ({mb} MB, {n} files) in {s} s.",
    "installed": "Installed into archive\\pc\\mod.",
    "err": "Error",
    "err_build": "The build failed:\n\n{e}",
    "err_install": "The install failed:\n\n{e}",
    "no_selection": "No tattoo is checked.",
    "need_setup": "Setup is incomplete: the game folder, ArchiveXL, the .NET runtime and WolvenKit Console are all required.",
    "dup_names": "Several tattoos share the same name in game:\n\n{d}\n\nThe game cannot tell them apart. Build anyway?",
    "game_running": "Cyberpunk 2077 is running. Close the game, then install.",
    "conflicts": ("These archives in archive\\pc\\mod are VTK tattoo archives. They paint a permanent tattoo in the skin, "
                  "under Ink Flow's layers, so you would see two tattoos at once:\n\n{l}\n\n"
                  "Move them to the backup folder? (Yes = move, No = keep them, Cancel = do not install)"),
    "install_done": "{name}.archive and its .xl are in archive\\pc\\mod.\n\n{b}Start the game: the Ink slots are in the character creator, at the ripperdoc{m}.",
    "backup_note": "Replaced files were moved to:\n{d}\n\n",
    "mirror_note": " and at the apartment mirror",
    "cache_q": "Delete the extraction cache ({mb} MB)? The next build will extract everything again.",
    "scan_fail": "Could not read:\n{f}",
    "dl_progress": "Downloading WolvenKit Console… {d}/{t} MB",
    "dl_fail": "The download failed:\n\n{e}\n\nYou can download WolvenKit Console {v} yourself from GitHub and use Locate….",
    "dl_dotnet": ("WolvenKit Console is installed but cannot start: it needs the .NET {m} runtime.\n\n"
                  "Install \".NET Runtime {m}\" (x64) from the Microsoft page that will open, then press Detect."),
    "about_text": (f"{APP_NAME} {VERSION}\nInk Flow — VTK/UV CCXL Tattoo Loader\n\n"
                   "Builds ONE archive that adds your own VTK tattoo archives as slots of the character creator, "
                   "from the files you already own. Nothing from other authors is redistributed.\n\n"
                   "Requires ArchiveXL in the game and WolvenKit Console (downloaded from GitHub, MIT/GPL by its authors).\n"
                   "This tool: MIT licence. No telemetry. Data folder:\n{d}"),
    "open_data": "Open data folder",
    "version_check": "Checking WolvenKit Console…",
}


def _dpi_aware():
    if os.name == "nt":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (OSError, AttributeError):
            pass


def _open_folder(path):
    os.makedirs(path, exist_ok=True)
    if os.name == "nt":
        os.startfile(path)  # noqa: S606
    else:
        subprocess.Popen(["xdg-open", path])


def _dir_size(path):
    total = 0
    for d, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(d, f))
            except OSError:
                pass
    return total


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(T["title"])
        self.minsize(900, 640)
        self.geometry("1040x760")
        self.cfg = Config()
        self.cat = core.Catalogue(env.CATALOGUE_FILE)
        self.entries = []            # core.Entry, display order
        self.unchecked = set(self.cfg["unchecked"])
        self.q = queue.Queue()
        self.busy = False
        self.building = False        # busy with a build (Cancel offered) rather than a download
        self.cancel = threading.Event()
        self.quit_after_cancel = False
        self.result = None
        self.cli = None
        self.ok_env = False
        self.autotest = None
        self._editor = None
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(100, self._poll)
        self.after(50, self._startup)

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        pad = {"padx": 6, "pady": 3}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(3, weight=2)

        # --- setup
        f = ttk.LabelFrame(self, text=T["setup"])
        f.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        f.columnconfigure(1, weight=1)
        ttk.Label(f, text=T["game"]).grid(row=0, column=0, sticky="w", **pad)
        self.game_var = tk.StringVar(value=self.cfg["game"])
        e = ttk.Entry(f, textvariable=self.game_var)
        e.grid(row=0, column=1, sticky="ew", **pad)
        e.bind("<FocusOut>", lambda _e: self.refresh_env())
        e.bind("<Return>", lambda _e: self.refresh_env())
        ttk.Button(f, text=T["browse"], command=self.pick_game).grid(row=0, column=2, **pad)
        ttk.Button(f, text=T["detect"], command=self.detect_game).grid(row=0, column=3, **pad)
        st = ttk.Frame(f)
        st.grid(row=1, column=0, columnspan=4, sticky="ew", padx=6, pady=(0, 4))
        self.lbl_game = ttk.Label(st, text="")
        self.lbl_axl = ttk.Label(st, text="")
        self.lbl_dotnet = ttk.Label(st, text="")
        self.lbl_wk = ttk.Label(st, text="")
        for i, w in enumerate((self.lbl_game, self.lbl_axl, self.lbl_dotnet, self.lbl_wk)):
            w.grid(row=0, column=i, sticky="w", padx=(0, 18))
        act = ttk.Frame(f)
        act.grid(row=2, column=0, columnspan=4, sticky="ew", padx=6, pady=(0, 6))
        self.btn_axl = ttk.Button(act, text=T["get_axl"], command=lambda: webbrowser.open(env.ARCHIVEXL_URL))
        self.btn_dotnet = ttk.Button(act, text=T["get_dotnet"].format(m=env.DOTNET_MAJOR), command=lambda: webbrowser.open(env.DOTNET_URL))
        self.btn_wk = ttk.Button(act, text=T["wk_download"].format(mb=env.WOLVENKIT_SIZE // 1_000_000), command=self.download_wolvenkit)
        self.btn_wk_locate = ttk.Button(act, text=T["wk_locate"], command=self.locate_wolvenkit)
        self.btn_axl.grid(row=0, column=0, padx=(0, 6))
        self.btn_dotnet.grid(row=0, column=1, padx=(0, 6))
        self.btn_wk.grid(row=0, column=2, padx=(0, 6))
        self.btn_wk_locate.grid(row=0, column=3, padx=(0, 6))
        # The body the shells will be copied from (1.0.1) : what the game loads for the body mesh, resolved in a thread.
        self.lbl_body = ttk.Label(f, text="", wraplength=980, justify="left")
        self.lbl_body.grid(row=3, column=0, columnspan=4, sticky="w", padx=6, pady=(0, 6))
        self._bodies_game = None

        # --- tattoos
        f = ttk.LabelFrame(self, text=T["tattoos"])
        f.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        f.columnconfigure(0, weight=1)
        f.rowconfigure(0, weight=1)
        cols = ("on", "file", "targets", "name", "note")
        self.tree = ttk.Treeview(f, columns=cols, show="headings", selectmode="extended")
        heads = {"on": T["col_on"], "file": T["col_file"], "targets": T["col_targets"], "name": T["col_name"], "note": T["col_note"]}
        widths = {"on": 32, "file": 360, "targets": 150, "name": 200, "note": 220}
        for c in cols:
            self.tree.heading(c, text=heads[c])
            self.tree.column(c, width=widths[c], anchor="center" if c == "on" else "w", stretch=(c in ("file", "note")))
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        sb = ttk.Scrollbar(f, orient="vertical", command=self.tree.yview)
        sb.grid(row=0, column=1, sticky="ns", pady=6)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.tag_configure("ignored", foreground="#888888")
        self.tree.bind("<Button-1>", self._tree_click)
        self.tree.bind("<Double-1>", self._tree_double)
        self.tree.bind("<space>", lambda _e: self._toggle_selected())
        self.tree.bind("<F2>", lambda _e: self.rename_selected())
        self.tree.bind("<Delete>", lambda _e: self.remove_selected())
        bb = ttk.Frame(f)
        bb.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6))
        for i, (txt, cmd) in enumerate((
                (T["add_files"], self.add_files), (T["add_folder"], self.add_folder), (T["scan_game"], self.scan_game),
                (T["remove"], self.remove_selected),
                (T["rename"], self.rename_selected), (T["check_all"], lambda: self._check_all(True)),
                (T["uncheck_all"], lambda: self._check_all(False)))):
            ttk.Button(bb, text=txt, command=cmd).grid(row=0, column=i, padx=(0, 6))
        ttk.Label(f, text=T["hint_names"].format(n=self.cfg["max_name"]), foreground="#555555").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=6, pady=(0, 6))

        # --- options
        f = ttk.LabelFrame(self, text=T["options"])
        f.grid(row=2, column=0, sticky="ew", padx=8, pady=4)
        f.columnconfigure(5, weight=1)
        ttk.Label(f, text=T["slots"]).grid(row=0, column=0, sticky="w", **pad)
        self.slots_var = tk.IntVar(value=int(self.cfg["slots"]))
        ttk.Spinbox(f, from_=1, to=9, width=4, textvariable=self.slots_var).grid(row=0, column=1, sticky="w", **pad)
        self.mirror_var = tk.BooleanVar(value=bool(self.cfg["mirror"]))
        ttk.Checkbutton(f, text=T["mirror"], variable=self.mirror_var).grid(row=0, column=2, sticky="w", padx=(18, 6))
        self.fpp_var = tk.BooleanVar(value=bool(self.cfg["fpp"]))
        ttk.Checkbutton(f, text=T["fpp"], variable=self.fpp_var).grid(row=0, column=3, sticky="w", padx=(18, 6))
        ttk.Label(f, text=T["alpha"]).grid(row=0, column=4, sticky="w", padx=(18, 6))
        self.alpha_var = tk.DoubleVar(value=float(self.cfg["alpha"]))
        ttk.Spinbox(f, from_=0.1, to=1.0, increment=0.1, width=5, textvariable=self.alpha_var, format="%.1f").grid(row=0, column=5, sticky="w", **pad)
        ttk.Label(f, text=T["out"]).grid(row=1, column=0, sticky="w", **pad)
        self.out_var = tk.StringVar(value=self.cfg["out"])
        ttk.Entry(f, textvariable=self.out_var).grid(row=1, column=1, columnspan=5, sticky="ew", **pad)
        ttk.Button(f, text=T["browse"], command=self.pick_out).grid(row=1, column=6, **pad)
        ttk.Button(f, text=T["open"], command=lambda: _open_folder(self.out_var.get())).grid(row=1, column=7, **pad)

        # --- actions + log
        f = ttk.Frame(self)
        f.grid(row=3, column=0, sticky="nsew", padx=8, pady=(4, 8))
        f.columnconfigure(0, weight=1)
        f.rowconfigure(2, weight=1)
        row = ttk.Frame(f)
        row.grid(row=0, column=0, sticky="ew")
        self.btn_build = ttk.Button(row, text=T["build"], command=self.build)
        self.btn_install = ttk.Button(row, text=T["install"], command=self.install, state="disabled")
        self.btn_build.grid(row=0, column=0, padx=(0, 6))
        self.btn_install.grid(row=0, column=1, padx=(0, 18))
        ttk.Button(row, text=T["clear_cache"], command=self.clear_cache).grid(row=0, column=2, padx=(0, 6))
        ttk.Button(row, text=T["open_data"], command=lambda: _open_folder(env.APPDATA)).grid(row=0, column=3, padx=(0, 6))
        ttk.Button(row, text=T["about"], command=self.about).grid(row=0, column=4, padx=(0, 6))
        self.progress = ttk.Progressbar(f, mode="determinate", maximum=100)
        self.progress.grid(row=1, column=0, sticky="ew", pady=4)
        self.log = ScrolledText(f, height=10, wrap="word", state="disabled", font=("Consolas", 9))
        self.log.grid(row=2, column=0, sticky="nsew")
        self.status = ttk.Label(self, text=T["ready"], anchor="w", relief="sunken")
        self.status.grid(row=4, column=0, sticky="ew")

    # ------------------------------------------------------------------ startup / environment
    def _startup(self):
        if not self.game_var.get() or not env.valid_game(self.game_var.get()):
            c = env.find_game_candidates()
            if c:
                self.game_var.set(c[0])
        self.refresh_env()
        files = [p for p in self.cfg["files"] if os.path.isfile(p)]
        if files:
            self._add_paths(files, quiet=True)
        # Unattended test of a built exe : INKFLOW_AUTOTEST=<report.json> builds at once and exits, writing a report.
        self.autotest = os.environ.get("INKFLOW_AUTOTEST")
        if self.autotest:
            self.after(500, self.build)

    def _autotest_done(self, ok, text):
        import json
        rep = {"ok": ok, "text": text, "env_ok": self.ok_env, "rows": len(self.entries),
               "checked": len(self._selected_entries()), "labels": [self.lbl_game["text"], self.lbl_axl["text"], self.lbl_dotnet["text"], self.lbl_wk["text"]],
               "frozen": bool(getattr(sys, "frozen", False)), "templates": core.templates_dir(),
               "log": self.log.get("1.0", "end")[-4000:]}
        if ok and self.result:
            rep.update({"archive": self.result.archive, "size": self.result.size, "files": len(self.result.listing), "seconds": round(self.result.seconds)})
        with open(self.autotest, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=1, ensure_ascii=False)
        self.on_close()

    def refresh_env(self):
        game = self.game_var.get().strip()
        ok_game = env.valid_game(game)
        self.lbl_game.config(text=T["game_ok"] if ok_game else T["game_bad"], foreground="#1a7f37" if ok_game else "#c0392b")
        axl = env.archivexl(game) if ok_game else None
        self.lbl_axl.config(text=T["axl_ok"].format(v=axl) if axl else T["axl_bad"], foreground="#1a7f37" if axl else "#c0392b")
        self.btn_axl.grid() if not axl else self.btn_axl.grid_remove()
        dn = env.has_dotnet()
        self.lbl_dotnet.config(text=(T["dotnet_ok"] if dn else T["dotnet_bad"]).format(m=env.DOTNET_MAJOR), foreground="#1a7f37" if dn else "#c0392b")
        self.btn_dotnet.grid() if not dn else self.btn_dotnet.grid_remove()
        self.cli = env.find_wolvenkit(self.cfg["cli"])
        self.lbl_wk.config(text=T["wk_ok"] if self.cli else T["wk_bad"], foreground="#1a7f37" if self.cli else "#c0392b")
        self.btn_wk.grid() if not self.cli else self.btn_wk.grid_remove()
        self.cfg["game"] = game
        self.cfg["cli"] = self.cli or ""
        self.ok_env = ok_game and bool(axl) and dn and bool(self.cli)
        self._update_buttons()
        self.refresh_bodies(game if ok_game else None)

    def refresh_bodies(self, game, force=False):
        """Resolve, in a thread, which archive the game loads for the body, arms and head meshes (what the shells
        will be copied from). Shown under the setup lines ; red when it is the base game."""
        if game == self._bodies_game and not force:
            return
        self._bodies_game = game
        if not game:
            self.lbl_body.config(text="")
            return
        self.lbl_body.config(text=T["body_wait"], foreground="#555555")

        def work():
            try:
                who = {c: w for c, (w, _) in core.active_owners(game, [t["code"] for t in core.TARGETS]).items()}
            except Exception as e:  # noqa: BLE001
                who = {"error": str(e)}
            self.q.put(("bodies", game, who))

        threading.Thread(target=work, daemon=True).start()

    def _show_bodies(self, game, who):
        if game != self._bodies_game:
            return
        if "error" in who:
            self.lbl_body.config(text=f"Body mesh: could not read the game archives ({who['error']})", foreground="#c0392b")
            return
        arms = who["arm_l"] if who["arm_l"] == who["arm_r"] else f"{who['arm_l']} / {who['arm_r']}"
        if who["body"] == core.BASE_GAME:
            self.lbl_body.config(text=T["body_vanilla"], foreground="#c0392b")
        else:
            self.lbl_body.config(text=T["body_line"].format(b=who["body"], a=arms, h=who["head"]), foreground="#1a7f37")
        self.bodies = who

    def _update_buttons(self):
        if self.building:            # the build button is the Cancel button while a build runs
            self.btn_build.config(text=T["cancelling"] if self.cancel.is_set() else T["cancel"],
                                  state="disabled" if self.cancel.is_set() else "normal")
            self.btn_install.config(state="disabled")
            return
        can = self.ok_env and not self.busy and any(e.supported and e.id not in self.unchecked for e in self.entries)
        self.btn_build.config(text=T["build"], state="normal" if can else "disabled")
        self.btn_install.config(state="normal" if (self.result and not self.busy and env.valid_game(self.game_var.get())) else "disabled")

    def pick_game(self):
        d = filedialog.askdirectory(title=T["game"], initialdir=self.game_var.get() or None)
        if d:
            self.game_var.set(os.path.normpath(d))
            self.refresh_env()

    def detect_game(self):
        c = env.find_game_candidates()
        if c:
            self.game_var.set(c[0])
        self.refresh_env()

    def pick_out(self):
        d = filedialog.askdirectory(title=T["out"], initialdir=self.out_var.get() or None)
        if d:
            self.out_var.set(os.path.normpath(d))

    def locate_wolvenkit(self):
        p = filedialog.askopenfilename(title="WolvenKit.CLI.exe", filetypes=[("WolvenKit.CLI.exe", "WolvenKit.CLI.exe"), ("exe", "*.exe")])
        if p:
            self.cfg["cli"] = p
            self.refresh_env()
            self._self_test_cli()

    def download_wolvenkit(self):
        if self.busy:
            return
        self._set_busy(True, T["dl_progress"].format(d=0, t=env.WOLVENKIT_SIZE // 1_000_000))

        def prog(d, t):
            self.q.put(("progress", 100.0 * d / max(t, 1), T["dl_progress"].format(d=d // 1_000_000, t=t // 1_000_000)))

        def work():
            try:
                exe = env.download_wolvenkit(prog)
                self.q.put(("downloaded", exe))
            except Exception as e:  # noqa: BLE001
                self.q.put(("dl_error", str(e)))

        threading.Thread(target=work, daemon=True).start()

    def _self_test_cli(self):
        if not self.cli:
            return
        self.status.config(text=T["version_check"])
        ok, out = core.Cli(self.cli, self._log).version()
        self._log(f"WolvenKit CLI {'OK' if ok else 'FAILED'}: {out.splitlines()[-1] if out else ''}")
        if not ok and not env.has_dotnet():
            messagebox.showwarning(APP_NAME, T["dl_dotnet"].format(m=env.DOTNET_MAJOR))
            webbrowser.open(env.DOTNET_URL)
        self.status.config(text=T["ready"])

    # ------------------------------------------------------------------ tattoo list
    def add_files(self):
        ps = filedialog.askopenfilenames(title=T["add_files"], initialdir=self.cfg["last_dir"] or None,
                                         filetypes=[("Cyberpunk archive", "*.archive")])
        if ps:
            self.cfg["last_dir"] = os.path.dirname(ps[0])
            self._add_paths(list(ps))

    def add_folder(self):
        d = filedialog.askdirectory(title=T["add_folder"], initialdir=self.cfg["last_dir"] or None)
        if d:
            self.cfg["last_dir"] = d
            self._add_paths([os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(".archive")], legacy_dir=d)

    def scan_game(self):
        """Find the VTK tattoo archives the game currently loads (archive\\pc\\mod and REDmod), copy them into the
        builder's tattoo folder (the originals will be offered for backup at install) and add the copies."""
        if self.busy:
            return
        game = self.game_var.get().strip()
        if not env.valid_game(game):
            messagebox.showwarning(APP_NAME, T["game_bad"])
            return
        self.config(cursor="watch")
        self.update_idletasks()
        try:
            found = core.find_tattoo_archives(game)
            copied, lines = [], []
            if found:
                os.makedirs(env.TATTOO_DIR, exist_ok=True)
            for label, full in found:
                cid = core.rdar.content_id(full)
                dst = os.path.join(env.TATTOO_DIR, os.path.basename(full))
                if os.path.isfile(dst) and core.rdar.content_id(dst) != cid:
                    stem, ext = os.path.splitext(os.path.basename(full))
                    dst = os.path.join(env.TATTOO_DIR, f"{stem}__{cid[:8]}{ext}")
                if not os.path.isfile(dst):
                    shutil.copy2(full, dst)
                copied.append(dst)
                lines.append(label)
        finally:
            self.config(cursor="")
        if not copied:
            messagebox.showinfo(APP_NAME, T["scan_none"])
            return
        self._log(f"scan game folder: {len(copied)} VTK tattoo archive(s) copied to {env.TATTOO_DIR}")
        for l in lines:
            self._log("  " + l)
        self._add_paths(copied)
        messagebox.showinfo(APP_NAME, T["scan_result"].format(n=len(copied), l="\n".join(lines)))

    def _add_paths(self, paths, quiet=False, legacy_dir=None):
        self.config(cursor="watch")
        self.update_idletasks()
        try:
            new = core.scan_files(paths)
            folders = {os.path.dirname(e.path) for e in new}
            for d in ([legacy_dir] if legacy_dir else []) + sorted(folders):
                self.cat.import_legacy(d, new, self._log)
            self.cat.ensure(new)
            known = {e.id for e in self.entries if e.id}
            bad = []
            for e in new:
                if not e.id:
                    bad.append(e.file)
                    continue
                if e.id in known:
                    continue
                known.add(e.id)
                self.entries.append(e)
            self.entries.sort(key=lambda e: e.file.lower())
            self.cat.save()
            if bad and not quiet:
                messagebox.showwarning(APP_NAME, T["scan_fail"].format(f="\n".join(bad)))
        finally:
            self.config(cursor="")
        self._refresh_tree()

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for e in self.entries:
            if e.supported:
                on = "" if e.id in self.unchecked else "✔"
                label, cut = core.option_label(self.cat.name(e), self.cfg["max_name"])
                note = (f"ignored: {e.ignored_reason}" if (e.other or e.unknown) else "") + ("  [name cut]" if cut else "")
                self.tree.insert("", "end", iid=e.id, values=(on, e.file, " + ".join(t["label"] for t in e.targets), label, note))
            else:
                self.tree.insert("", "end", iid=e.id or e.file, values=("", e.file, "—", "", f"ignored: {e.ignored_reason}"), tags=("ignored",))
        self.cfg["files"] = [e.path for e in self.entries]
        self.cfg["unchecked"] = sorted(self.unchecked)
        self._update_buttons()

    def _entry(self, iid):
        return next((e for e in self.entries if (e.id or e.file) == iid), None)

    def _tree_click(self, ev):
        if self.busy:
            return "break"
        if self.tree.identify_region(ev.x, ev.y) != "cell":
            return
        if self.tree.identify_column(ev.x) == "#1":
            self._toggle(self.tree.identify_row(ev.y))
            return "break"

    def _tree_double(self, ev):
        if self.busy:
            return "break"
        if self.tree.identify_region(ev.x, ev.y) != "cell":
            return
        iid = self.tree.identify_row(ev.y)
        if self.tree.identify_column(ev.x) == "#4":
            self._edit_name(iid)
        elif self.tree.identify_column(ev.x) != "#1":
            self._toggle(iid)

    def _toggle(self, iid):
        e = self._entry(iid)
        if self.busy or not e or not e.supported:
            return
        if e.id in self.unchecked:
            self.unchecked.discard(e.id)
        else:
            self.unchecked.add(e.id)
        self._refresh_tree()

    def _toggle_selected(self):
        for iid in self.tree.selection():
            self._toggle(iid)

    def _check_all(self, on):
        if self.busy:
            return
        for e in self.entries:
            if e.supported:
                (self.unchecked.discard if on else self.unchecked.add)(e.id)
        self._refresh_tree()

    def remove_selected(self):
        sel = set(self.tree.selection())
        if self.busy or not sel:
            return
        self.entries = [e for e in self.entries if (e.id or e.file) not in sel]
        self._refresh_tree()

    def rename_selected(self):
        sel = self.tree.selection()
        if not self.busy and len(sel) == 1:
            e = self._entry(sel[0])
            if e and e.supported:
                new = simpledialog.askstring(T["rename"], T["col_name"], initialvalue=self.cat.name(e), parent=self)
                if new is not None and new.strip():
                    self.cat.set_name(e, new)
                    self.cat.save()
                    self._refresh_tree()

    def _edit_name(self, iid):
        e = self._entry(iid)
        if self.busy or not e or not e.supported:
            return
        self._close_editor()
        x, y, w, h = self.tree.bbox(iid, "#4")
        var = tk.StringVar(value=self.cat.name(e))
        ed = ttk.Entry(self.tree, textvariable=var)
        ed.place(x=x, y=y, width=w, height=h)
        ed.focus_set()
        ed.select_range(0, "end")

        def commit(_ev=None):
            if var.get().strip():
                self.cat.set_name(e, var.get())
                self.cat.save()
            self._close_editor()
            self._refresh_tree()

        ed.bind("<Return>", commit)
        ed.bind("<FocusOut>", commit)
        ed.bind("<Escape>", lambda _ev: self._close_editor())
        self._editor = ed

    def _close_editor(self):
        if self._editor is not None:
            self._editor.destroy()
            self._editor = None

    # ------------------------------------------------------------------ build / install
    def _settings(self):
        return core.Settings(game=self.game_var.get().strip(), cli=self.cli, work=env.WORK_DIR, out=self.out_var.get().strip() or env.OUT_DIR,
                             name=MOD_NAME, slots=max(1, int(self.slots_var.get())), slot_title="Ink {n}", max_name=int(self.cfg["max_name"]),
                             alpha=round(float(self.alpha_var.get()), 2), mirror=bool(self.mirror_var.get()),
                             fpp=bool(self.fpp_var.get()), route1=False)

    def _selected_entries(self):
        return [e for e in self.entries if e.supported and e.id not in self.unchecked]

    def build(self):
        if self.building:
            self.cancel_build()
            return
        if self.busy:
            return
        if not self.ok_env:
            messagebox.showwarning(APP_NAME, T["need_setup"])
            return
        sel = self._selected_entries()
        if not sel:
            messagebox.showinfo(APP_NAME, T["no_selection"])
            return
        names = {}
        for e in sel:
            names.setdefault(core.option_label(self.cat.name(e), self.cfg["max_name"])[0], []).append(e.file)
        dup = {n: f for n, f in names.items() if len(f) > 1}
        if dup and not messagebox.askyesno(APP_NAME, T["dup_names"].format(d="\n".join(f"\"{n}\": {', '.join(f)}" for n, f in dup.items()))):
            return
        try:
            s = self._settings()
        except (tk.TclError, ValueError) as e:
            messagebox.showerror(T["err"], str(e))
            return
        self.cfg["slots"], self.cfg["mirror"], self.cfg["fpp"], self.cfg["alpha"], self.cfg["out"] = s.slots, s.mirror, s.fpp, s.alpha, s.out
        self.cfg.save()
        self.result = None
        self._clear_log()
        self._start_logfile(s, sel)
        self.cancel.clear()
        self.building = True
        self._set_busy(True, T["building"])

        def prog(i, n, text):
            self.q.put(("progress", 100.0 * i / max(n, 1), text))

        def work():
            try:
                res = core.run_build(s, sel, self.cat, lambda *a: self.q.put(("log", " ".join(str(x) for x in a))), prog, self.cancel)
                self.q.put(("built", res))
            except core.Cancelled:
                self.q.put(("cancelled",))
            except core.BuildError as e:
                self.q.put(("build_error", str(e)))
            except Exception as e:  # noqa: BLE001
                import traceback
                self.q.put(("build_error", f"{e}\n\n{traceback.format_exc()[-1500:]}"))

        threading.Thread(target=work, daemon=True).start()

    def cancel_build(self):
        if self.building and not self.cancel.is_set():
            self.cancel.set()
            self.status.config(text=T["cancelling"])
            self._update_buttons()

    def install(self):
        if self.busy or not self.result:
            return
        game = self.game_var.get().strip()
        if core.game_running():
            messagebox.showwarning(APP_NAME, T["game_running"])
            return
        self.config(cursor="watch")
        self.update_idletasks()
        try:
            conf = core.conflicting_archives(game, [it.entry for it in self.result.items], exclude_names=(MOD_NAME + ".archive",))
        finally:
            self.config(cursor="")
        move = []
        if conf:
            ans = messagebox.askyesnocancel(APP_NAME, T["conflicts"].format(l="\n".join(conf)))
            if ans is None:
                return
            if ans:
                move = conf
        try:
            backup = core.install(self.result, game, env.BACKUP_DIR, self._log, move_conflicts=move)
        except core.BuildError as e:
            messagebox.showerror(T["err"], T["err_install"].format(e=e))
            return
        self.status.config(text=T["installed"])
        messagebox.showinfo(APP_NAME, T["install_done"].format(
            name=MOD_NAME, b=T["backup_note"].format(d=backup) if backup else "", m=T["mirror_note"] if self.mirror_var.get() else ""))

    def clear_cache(self):
        if self.busy:
            return
        mb = _dir_size(env.WORK_DIR) // 1_000_000 if os.path.isdir(env.WORK_DIR) else 0
        if messagebox.askyesno(APP_NAME, T["cache_q"].format(mb=mb)):
            shutil.rmtree(env.WORK_DIR, ignore_errors=True)
            self._log("cache cleared")

    def about(self):
        messagebox.showinfo(T["about"], T["about_text"].format(d=env.APPDATA))

    # ------------------------------------------------------------------ plumbing
    def _set_busy(self, busy, text=None):
        self.busy = busy
        if not busy:
            self.building = False
        if text:
            self.status.config(text=text)
        if not busy:
            self.progress["value"] = 0
        self._lock(busy)
        self._update_buttons()

    def _lock(self, on):
        """Whole window read-only while busy : every ttk control but the build/Cancel button. The tattoo list ignores
        clicks and keys through `self.busy` (a disabled Treeview still takes them)."""
        self._close_editor()
        todo = list(self.winfo_children())
        while todo:
            w = todo.pop()
            todo.extend(w.winfo_children())
            if w is not self.btn_build and isinstance(w, (ttk.Button, ttk.Entry, ttk.Spinbox, ttk.Checkbutton, ttk.Treeview)):
                w.state(["disabled"] if on else ["!disabled"])

    def _clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def _log(self, *a):
        line = " ".join(str(x) for x in a)
        self.log.config(state="normal")
        self.log.insert("end", line + "\n")
        self.log.see("end")
        self.log.config(state="disabled")
        try:
            with open(env.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            pass

    def _start_logfile(self, s, sel):
        """`build.log` (data folder) starts over at each build : version, date, environment, settings, the body the
        shells come from, then every log line. What a player sends when the tattoos do not show."""
        import time
        try:
            os.makedirs(env.APPDATA, exist_ok=True)
            with open(env.LOG_FILE, "w", encoding="utf-8") as f:
                f.write(f"{APP_NAME} {VERSION}  {time.strftime('%Y-%m-%d %H:%M:%S')}  frozen={bool(getattr(sys, 'frozen', False))}\n")
                f.write(f"game: {s.game}\ncli: {s.cli}\nout: {s.out}\n")
                f.write(f"setup: {self.lbl_game['text']} | {self.lbl_axl['text']} | {self.lbl_dotnet['text']} | {self.lbl_wk['text']}\n")
                f.write(f"{self.lbl_body['text']}\n")
                f.write(f"settings: slots={s.slots} mirror={s.mirror} fpp={s.fpp} alpha={s.alpha} max_name={s.max_name}\n")
                f.write(f"tattoos: {len(sel)} checked of {len(self.entries)}\n\n")
        except OSError:
            pass

    def _poll(self):
        try:
            while True:
                kind, *args = self.q.get_nowait()
                if kind == "log":
                    self._log(args[0])
                elif kind == "bodies":
                    self._show_bodies(args[0], args[1])
                elif kind == "progress":
                    self.progress["value"] = args[0]
                    self.status.config(text=args[1])
                elif kind == "built":
                    self.result = args[0]
                    self._set_busy(False, T["built"].format(name=MOD_NAME, mb=f"{self.result.size / 1e6:.1f}", n=len(self.result.listing), s=f"{self.result.seconds:.0f}"))
                    self.refresh_bodies(self._bodies_game, force=True)     # a mesh may have been extracted from a new archive
                    if self.autotest:
                        self._autotest_done(True, self.status["text"])
                elif kind == "build_error":
                    self._log("ERROR: " + args[0])
                    self._set_busy(False, T["ready"])
                    if self.autotest:
                        self._autotest_done(False, args[0])
                    else:
                        messagebox.showerror(T["err"], T["err_build"].format(e=args[0][:1500]) + T["log_note"])
                elif kind == "cancelled":
                    self._log(T["cancelled"])
                    self._set_busy(False, T["cancelled"])
                    if self.autotest:
                        self._autotest_done(False, T["cancelled"])
                    elif self.quit_after_cancel:
                        self.on_close()
                        return
                elif kind == "downloaded":
                    self.cfg["cli"] = args[0]
                    self._set_busy(False, T["ready"])
                    self.refresh_env()
                    self._self_test_cli()
                elif kind == "dl_error":
                    self._set_busy(False, T["ready"])
                    messagebox.showerror(T["err"], T["dl_fail"].format(e=args[0], v=env.WOLVENKIT_VERSION))
                    webbrowser.open(env.WOLVENKIT_PAGE)
        except queue.Empty:
            pass
        self.after(100, self._poll)

    def on_close(self):
        if self.building and not self.autotest:
            # Quit = cancel first : the WolvenKit process is killed and the half-written archive removed, then close.
            if self.quit_after_cancel or messagebox.askyesno(APP_NAME, T["quit_busy"]):
                self.quit_after_cancel = True
                self.cancel_build()
            return
        if self.busy and not self.autotest and not messagebox.askyesno(APP_NAME, T["quit_download"]):
            return
        try:
            self.cfg["game"] = self.game_var.get().strip()
            self.cfg["out"] = self.out_var.get().strip()
            self.cfg["slots"] = int(self.slots_var.get())
            self.cfg["mirror"] = bool(self.mirror_var.get())
            self.cfg["fpp"] = bool(self.fpp_var.get())
            self.cfg["alpha"] = round(float(self.alpha_var.get()), 2)
            self.cfg["unchecked"] = sorted(self.unchecked)
            self.cfg.save()
            self.cat.save()
        except (OSError, ValueError, tk.TclError):
            pass
        self.destroy()


def main():
    _dpi_aware()
    try:
        app = App()
    except Exception as e:  # noqa: BLE001
        if os.name == "nt":
            ctypes.windll.user32.MessageBoxW(0, f"{APP_NAME} could not start:\n\n{e}", APP_NAME, 0x10)
        raise
    app.mainloop()


if __name__ == "__main__":
    sys.exit(main())
