"""Smoke test of the Setup box when the .NET runtime is missing : `env.has_dotnet` forced to False, window captured to
PNG (same GDI capture as gui_capture.py), the .NET button's text and visibility reported. No download, no install."""
import ctypes
import json
import os
import struct
import sys
import zlib
from ctypes import wintypes

HOME = r"C:\__DEV\cyberpunk\ink_flow\exe\home"
os.environ["INKFLOW_HOME"] = HOME
sys.path.insert(0, r"D:\OneDrive - NS2I\Perso\Jeux\Mods\Cyberpunk 2.5\__DEV\__DEV\Projects\Ink Flow\builder")
from inkflow import env  # noqa: E402

env.has_dotnet = lambda major=env.DOTNET_MAJOR: False      # the player without the runtime
from inkflow import gui  # noqa: E402

user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32


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
    report["size"] = capture(hwnd, r"C:\__DEV\cyberpunk\ink_flow\exe\gui_dotnet_missing.png")
    report["dotnet_label"] = app.lbl_dotnet["text"]
    report["dotnet_button"] = app.btn_dotnet["text"]
    report["dotnet_button_visible"] = bool(app.btn_dotnet.winfo_ismapped())
    report["env_ok"] = app.ok_env
    report["build_state"] = str(app.btn_build["state"])
    app.destroy()


app.after(2000, snap)
app.mainloop()
print(json.dumps(report, indent=1, ensure_ascii=False))
