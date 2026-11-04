"""PNG -> DDS RGBA8 (DX10 header, DXGI 28) with a full box-filtered mip chain, alpha-weighted so empty texels do not
darken the ink (2026-11-04, Opus, measurement of the arm conversion).

  python ddswrite.py <in.png> <out.dds>
"""
import struct, sys
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def mips(img):
    """Square power-of-two texture : 2 x 2 box filter, colour weighted by alpha."""
    out = [img]
    a = img.astype(np.float64)
    while a.shape[0] > 1:
        n = a.shape[0] // 2
        q = a.reshape(n, 2, n, 2, 4)
        al = q[..., 3:4].sum(axis=(1, 3))
        rgb = (q[..., :3] * q[..., 3:4]).sum(axis=(1, 3))
        b = q.mean(axis=(1, 3))
        b[..., :3] = np.where(al > 0, rgb / np.maximum(al, 1e-9), b[..., :3])
        a = b
        out.append(np.clip(np.rint(a), 0, 255).astype(np.uint8))
    return out


def write(path, img):
    levels = mips(img)
    h, w = img.shape[:2]
    DDSD = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000 | 0x20000
    head = struct.pack("<4sII II II I 44x", b"DDS ", 124, DDSD, h, w, w * 4, 0, len(levels))
    pf = struct.pack("<II4sIIIII", 32, 0x4, b"DX10", 0, 0, 0, 0, 0)
    caps = struct.pack("<IIIII", 0x1000 | 0x8 | 0x400000, 0, 0, 0, 0)
    dx10 = struct.pack("<IIIII", 28, 3, 0, 1, 0)
    with open(path, "wb") as f:
        f.write(head + pf + caps + dx10)
        for lv in levels:
            f.write(np.ascontiguousarray(lv).tobytes())


if __name__ == "__main__":
    write(sys.argv[2], np.asarray(Image.open(sys.argv[1]).convert("RGBA")))
