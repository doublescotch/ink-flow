"""Lecture de l'index d'une .archive REDengine 4 (RDAR), sans WolvenKit : liste des empreintes FNV-1a 64 des chemins.
Sert au generateur Ink Flow pour reconnaitre la famille d'une archive de tatouage et trouver, parmi les archives
du joueur, celle qui livre le corps actif (premiere dans l'ordre alphabetique = premiere chargee).
Format (WolvenKit Archive.cs) : en-tete 40 o (RDAR, version, indexPosition u64, indexSize, debugPosition u64,
debugSize, filesize u64) ; index : fileTableOffset, fileTableSize, crc u64, fileEntryCount, fileSegmentCount,
resourceDependencyCount, puis fileEntryCount entrees de 56 o (nameHash u64, timestamp, ...).
Lecture seule, quelques Ko par archive."""
import os
import struct

FNV_OFFSET = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3
MASK = (1 << 64) - 1


def fnv1a64(path):
    """Empreinte d'un chemin de ressource (tel quel : le jeu stocke ses chemins en minuscules avec des `\\`)."""
    h = FNV_OFFSET
    for b in path.encode("utf-8"):
        h = ((h ^ b) * FNV_PRIME) & MASK
    return h


def hashes(archive):
    """Ensemble des empreintes des fichiers contenus dans `archive`."""
    with open(archive, "rb") as f:
        head = f.read(40)
        if len(head) < 40 or head[:4] != b"RDAR":
            raise ValueError("pas une archive RDAR : " + archive)
        _, _, index_pos, index_size, _, _, _ = struct.unpack("<4sIQIQIQ", head)
        f.seek(index_pos)
        idx = f.read(index_size)
    _, _, _, n_files, _, _ = struct.unpack_from("<IIQIII", idx, 0)
    out = set()
    off = 28
    for _ in range(n_files):
        (h,) = struct.unpack_from("<Q", idx, off)
        out.add(h)
        off += 56
    return out


def content_id(archive):
    """Identite du CONTENU d'une archive : SHA-256 du fichier entier, 16 caracteres hexadecimaux. Survit a un
    renommage, change des qu'un octet change. (Le champ SHA-1 par entree de l'index est vide dans les archives
    produites par WolvenKit : `da39a3ee…`, SHA-1 de la chaine vide, mesure le 2026-11-01.)"""
    import hashlib
    h = hashlib.sha256()
    with open(archive, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()[:16]


def archives_in(folder):
    """Les .archive d'un dossier dans l'ordre de chargement du jeu (alphabetique, sans tenir compte de la casse)."""
    return sorted((f for f in os.listdir(folder) if f.lower().endswith(".archive")), key=str.lower)


def owners(folder, path):
    """Archives du dossier qui livrent `path`, dans l'ordre de chargement (la premiere gagne)."""
    h = fnv1a64(path)
    return [a for a in archives_in(folder) if h in hashes(os.path.join(folder, a))]


if __name__ == "__main__":
    import sys
    folder = sys.argv[1]
    for p in sys.argv[2:]:
        print(p, "->", owners(folder, p))
