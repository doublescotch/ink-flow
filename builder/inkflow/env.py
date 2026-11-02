"""The player's machine : game folder, ArchiveXL, .NET runtime, WolvenKit Console (downloaded from GitHub, never
redistributed). Everything the builder stores lives in %LOCALAPPDATA%\\InkFlow."""
import ctypes
import glob
import os
import re
import subprocess
import tempfile
import urllib.request
import zipfile

# Everything the builder stores. `INKFLOW_HOME` overrides it (tests, portable use).
APPDATA = os.environ.get("INKFLOW_HOME") or os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "InkFlow")
CONFIG_FILE = os.path.join(APPDATA, "config.json")
CATALOGUE_FILE = os.path.join(APPDATA, "catalogue.json")
WORK_DIR = os.path.join(APPDATA, "work")
OUT_DIR = os.path.join(APPDATA, "out")
BACKUP_DIR = os.path.join(APPDATA, "backup")
WOLVENKIT_DIR = os.path.join(APPDATA, "wolvenkit")
TATTOO_DIR = os.path.join(APPDATA, "tattoos")      # copies made by "Scan game folder" (the originals may be moved away)
LOG_FILE = os.path.join(APPDATA, "build.log")      # the last build, for support

# WolvenKit Console : version pinned, size pinned (GitHub release asset, read 2026-11-01). SHA-256 pinned after the
# first verified download (see `WOLVENKIT_SHA256`) : a different file is refused.
WOLVENKIT_VERSION = "9.1.0"
WOLVENKIT_URL = f"https://github.com/WolvenKit/WolvenKit/releases/download/{WOLVENKIT_VERSION}/WolvenKit.Console-{WOLVENKIT_VERSION}.zip"
WOLVENKIT_SIZE = 45266516
WOLVENKIT_SHA256 = "7caf49cdf0f478b484b1a5a27e5aef261b879fabea7e72e33ca60eff3b834f4f"   # measured 2026-11-01, two downloads
WOLVENKIT_PAGE = "https://github.com/WolvenKit/WolvenKit/releases"
# WolvenKit Console 9.1.0 is framework-dependent : `WolvenKit.CLI.runtimeconfig.json` asks for Microsoft.NETCore.App 10.0.
DOTNET_MAJOR = 10
DOTNET_URL = "https://dotnet.microsoft.com/download/dotnet/10.0"
# .NET Runtime installer (x64, Windows), version and SHA-256 pinned (downloaded and Authenticode-checked on 2026-11-02,
# signer "CN=.NET, O=Microsoft Corporation"). The builder downloads it and runs it silently : the user never has to pick
# the right file among the SDK / ASP.NET / Desktop / Runtime columns of the Microsoft page.
DOTNET_VERSION = "10.0.14"
DOTNET_INSTALLER_URL = f"https://builds.dotnet.microsoft.com/dotnet/Runtime/{DOTNET_VERSION}/dotnet-runtime-{DOTNET_VERSION}-win-x64.exe"
DOTNET_INSTALLER_SIZE = 30653360
DOTNET_INSTALLER_SHA256 = "53a67d2d68a74a892010191d70080a5b359f41ed7d0bb2f92f120c9f0e4e199d"
DOTNET_DIR = os.path.join(APPDATA, "dotnet")
ARCHIVEXL_URL = "https://www.nexusmods.com/cyberpunk2077/mods/4198"

NO_WINDOW = 0x08000000 if os.name == "nt" else 0
GAME_EXE = r"bin\x64\Cyberpunk2077.exe"
GAME_BASE = r"archive\pc\content\basegame_4_appearance.archive"
STEAM_APP = "1091500"


# ----------------------------------------------------------------------------- game
def valid_game(folder):
    return bool(folder) and os.path.isfile(os.path.join(folder, GAME_EXE)) and os.path.isfile(os.path.join(folder, GAME_BASE))


def _reg(root, key, value):
    if os.name != "nt":
        return None
    import winreg
    for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
        try:
            with winreg.OpenKey(root, key, 0, winreg.KEY_READ | view) as k:
                return winreg.QueryValueEx(k, value)[0]
        except OSError:
            continue
    return None


def steam_libraries():
    libs = []
    if os.name != "nt":
        return libs
    import winreg
    steam = _reg(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath") or \
        _reg(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath")
    if not steam:
        return libs
    steam = os.path.normpath(steam)
    libs.append(steam)
    vdf = os.path.join(steam, "steamapps", "libraryfolders.vdf")
    if os.path.isfile(vdf):
        try:
            with open(vdf, encoding="utf-8", errors="replace") as f:
                for m in re.finditer(r'"path"\s+"([^"]+)"', f.read()):
                    libs.append(os.path.normpath(m.group(1).replace("\\\\", "\\")))
        except OSError:
            pass
    return libs


def find_game_candidates():
    """Folders that look like a Cyberpunk 2077 install : Steam libraries, GOG registry, Epic default, common drives."""
    cands = []
    for lib in steam_libraries():
        cands.append(os.path.join(lib, "steamapps", "common", "Cyberpunk 2077"))
    if os.name == "nt":
        import winreg
        gog = _reg(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\GOG.com\Games\1423049311", "path")
        if gog:
            cands.append(gog)
        for root in (os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")):
            cands.append(os.path.join(root, "Epic Games", "Cyberpunk 2077"))
            cands.append(os.path.join(root, "GOG Galaxy", "Games", "Cyberpunk 2077"))
    seen, out = set(), []
    for c in cands:
        n = os.path.normcase(os.path.normpath(c))
        if n not in seen and valid_game(c):
            seen.add(n)
            out.append(os.path.normpath(c))
    return out


def file_version(path):
    """Version string of a Windows binary (ctypes on version.dll ; no C#)."""
    if os.name != "nt" or not os.path.isfile(path):
        return None
    try:
        ver = ctypes.windll.version
        size = ver.GetFileVersionInfoSizeW(path, None)
        if not size:
            return None
        buf = ctypes.create_string_buffer(size)
        if not ver.GetFileVersionInfoW(path, 0, size, buf):
            return None
        ptr = ctypes.c_void_p()
        length = ctypes.c_uint()
        if not ver.VerQueryValueW(buf, "\\", ctypes.byref(ptr), ctypes.byref(length)):
            return None
        # VS_FIXEDFILEINFO : dwFileVersionMS at offset 8, dwFileVersionLS at 12
        raw = ctypes.string_at(ptr.value, length.value)
        ms = int.from_bytes(raw[8:12], "little")
        ls = int.from_bytes(raw[12:16], "little")
        return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
    except (OSError, AttributeError, ValueError):
        return None


def archivexl(game):
    """-> version string, "present" (no version readable) or None."""
    dll = os.path.join(game, r"red4ext\plugins\ArchiveXL\ArchiveXL.dll")
    if not os.path.isfile(dll):
        return None
    return file_version(dll) or "present"


# ----------------------------------------------------------------------------- .NET
def dotnet_runtimes():
    try:
        r = subprocess.run(["dotnet", "--list-runtimes"], capture_output=True, text=True, timeout=20, creationflags=NO_WINDOW)
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


def has_dotnet(major=DOTNET_MAJOR):
    rx = re.compile(rf"^Microsoft\.NETCore\.App {major}\.")
    return any(rx.match(l) for l in dotnet_runtimes())


# ----------------------------------------------------------------------------- WolvenKit Console
def find_wolvenkit(extra=None):
    """WolvenKit.CLI.exe : the configured path if valid, else what the builder downloaded."""
    if extra and os.path.isfile(extra):
        return extra
    hits = glob.glob(os.path.join(WOLVENKIT_DIR, "**", "WolvenKit.CLI.exe"), recursive=True)
    return sorted(hits)[0] if hits else None


def _safe_extract(zf, dest):
    dest_abs = os.path.abspath(dest)
    for info in zf.infolist():
        target = os.path.abspath(os.path.join(dest, info.filename))
        if os.path.commonpath([dest_abs, target]) != dest_abs:
            raise ValueError("unsafe path in zip: " + info.filename)
    zf.extractall(dest)


def _download_pinned(url, size, sha256, tmp, what, page, progress=None, cancel=None):
    """Stream `url` into the open file `tmp`, checking the pinned size and SHA-256. `progress(done, total)`,
    `cancel()` -> True to abort. Raises RuntimeError with a message meant for the user."""
    import hashlib
    req = urllib.request.Request(url, headers={"User-Agent": "InkFlowBuilder"})
    with urllib.request.urlopen(req, timeout=60) as r:
        total = int(r.headers.get("Content-Length") or size)
        done = 0
        h = hashlib.sha256()
        while True:
            if cancel and cancel():
                raise RuntimeError("download cancelled")
            chunk = r.read(1 << 18)
            if not chunk:
                break
            tmp.write(chunk)
            h.update(chunk)
            done += len(chunk)
            if progress:
                progress(done, total)
    tmp.close()
    if done != size:
        raise RuntimeError(f"unexpected size: {done} bytes (expected {size}); the release may have changed, see {page}")
    if sha256 and h.hexdigest() != sha256:
        raise RuntimeError(f"SHA-256 mismatch: the downloaded file is not the pinned {what}")


def download_dotnet(progress=None, cancel=None):
    """Download the pinned .NET Runtime installer into %LOCALAPPDATA%\\InkFlow\\dotnet\\. Returns its path (kept : a second
    attempt skips the download when the file already matches)."""
    import hashlib
    os.makedirs(DOTNET_DIR, exist_ok=True)
    dest = os.path.join(DOTNET_DIR, os.path.basename(DOTNET_INSTALLER_URL))
    if os.path.isfile(dest) and os.path.getsize(dest) == DOTNET_INSTALLER_SIZE:
        with open(dest, "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() == DOTNET_INSTALLER_SHA256:
                if progress:
                    progress(DOTNET_INSTALLER_SIZE, DOTNET_INSTALLER_SIZE)
                return dest
    tmp = tempfile.NamedTemporaryFile(prefix="dotnet_", suffix=".exe", dir=DOTNET_DIR, delete=False)
    tmp_path = tmp.name
    try:
        _download_pinned(DOTNET_INSTALLER_URL, DOTNET_INSTALLER_SIZE, DOTNET_INSTALLER_SHA256, tmp,
                         f".NET Runtime {DOTNET_VERSION} installer", DOTNET_URL, progress, cancel)
        os.replace(tmp_path, dest)
    finally:
        try:
            tmp.close()
        except OSError:
            pass
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)
    return dest


def install_dotnet(installer):
    """Run the Microsoft installer silently (it asks for elevation itself). Returns its exit code : 0 = installed,
    3010 = installed, reboot pending, 1602 = cancelled by the user at the elevation prompt."""
    p = subprocess.run([installer, "/install", "/quiet", "/norestart"], timeout=1800)
    return p.returncode


def download_wolvenkit(progress=None, cancel=None):
    """Download the pinned WolvenKit Console zip into %LOCALAPPDATA%\\InkFlow\\wolvenkit\\<version>. `progress(done, total)`,
    `cancel()` -> True to abort. Returns the CLI path. Size (and SHA-256 when pinned) are verified before unzipping."""
    os.makedirs(WOLVENKIT_DIR, exist_ok=True)
    dest = os.path.join(WOLVENKIT_DIR, WOLVENKIT_VERSION)
    tmp = tempfile.NamedTemporaryFile(prefix="wkit_", suffix=".zip", dir=WOLVENKIT_DIR, delete=False)
    tmp_path = tmp.name
    try:
        _download_pinned(WOLVENKIT_URL, WOLVENKIT_SIZE, WOLVENKIT_SHA256, tmp, "WolvenKit Console release",
                         WOLVENKIT_PAGE, progress, cancel)
        if os.path.isdir(dest):
            import shutil
            shutil.rmtree(dest, ignore_errors=True)
        os.makedirs(dest, exist_ok=True)
        with zipfile.ZipFile(tmp_path) as zf:
            _safe_extract(zf, dest)
    finally:
        try:
            tmp.close()
        except OSError:
            pass
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)
    exe = find_wolvenkit()
    if not exe:
        raise RuntimeError("WolvenKit.CLI.exe not found after extraction")
    return exe
