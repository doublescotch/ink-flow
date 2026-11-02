"""GUI smoke test 1.0.1 : own home, real game, open the window, wait for the Body mesh line, capture, report."""
import ctypes, json, os, struct, sys, zlib
from ctypes import wintypes

HOME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guihome")
os.environ["INKFLOW_HOME"] = HOME
os.makedirs(HOME, exist_ok=True)
IN = r"C:\__DEV\cyberpunk\ink_flow\in"
cfg = {"game": r"E:\Jeux\SteamLibrary\steamapps\common\Cyberpunk 2077",
       "cli": os.path.join(os.environ["LOCALAPPDATA"], r"InkFlow\wolvenkit\9.1.0\WolvenKit.CLI.exe"),
       "out": os.path.join(HOME, "out"), "slots": 2, "mirror": True, "fpp": True, "alpha": 1.0,
       "files": [os.path.join(IN, f) for f in sorted(os.listdir(IN)) if f.lower().endswith(".archive")], "unchecked": []}
with open(os.path.join(HOME, "config.json"), "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2)
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import gui  # noqa: E402

user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
OUT = sys.argv[1]


def capture(hwnd, path):
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w, h = rect.right - rect.left, rect.bottom - rect.top
    hdc = user32.GetWindowDC(hwnd)
    mem = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(mem, bmp)
    user32.PrintWindow(hwnd, mem, 2)

    class BIH(ctypes.Structure):
        _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG), ("biPlanes", wintypes.WORD),
                    ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD), ("biSizeImage", wintypes.DWORD),
                    ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG), ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD)]
    bih = BIH(ctypes.sizeof(BIH), w, -h, 1, 32, 0, 0, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(mem, bmp, 0, h, buf, ctypes.byref(bih), 0)
    raw = buf.raw
    rows = []
    for y in range(h):
        line = raw[y * w * 4:(y + 1) * w * 4]
        rows.append(b"\x00" + bytes(b for i in range(0, len(line), 4) for b in (line[i + 2], line[i + 1], line[i])))

    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(b"".join(rows), 6)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mem)
    user32.ReleaseDC(hwnd, hdc)
    return w, h


gui._dpi_aware()
app = gui.App()
report = {}


def snap():
    app.update_idletasks()
    hwnd = user32.GetParent(app.winfo_id()) or app.winfo_id()
    report["size"] = capture(hwnd, OUT)
    report["rows"] = len(app.tree.get_children())
    report["checked"] = sum(1 for e in app.entries if e.supported and e.id not in app.unchecked)
    report["env_ok"] = app.ok_env
    report["labels"] = [app.lbl_game["text"], app.lbl_axl["text"], app.lbl_dotnet["text"], app.lbl_wk["text"]]
    report["body_line"] = app.lbl_body["text"]
    report["body_color"] = str(app.lbl_body["foreground"])
    report["bodies"] = getattr(app, "bodies", None)
    report["buttons"] = [w["text"] for w in app.winfo_children()[1].winfo_children()[2].winfo_children()] if False else None
    app.on_close()


app.after(6000, snap)
app.mainloop()
print(json.dumps(report, indent=1, ensure_ascii=False))
