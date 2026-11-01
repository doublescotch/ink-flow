"""Builder settings, one JSON file in %LOCALAPPDATA%\\InkFlow."""
import json
import os

from . import env

DEFAULTS = {
    "game": "",
    "cli": "",
    "out": env.OUT_DIR,
    "slots": 2,
    "mirror": True,
    "alpha": 1.0,
    "slot_title": "Ink {n}",
    "max_name": 20,
    "files": [],          # archive paths added by the player
    "unchecked": [],      # content ids the player unchecked
    "last_dir": "",
}


class Config:
    def __init__(self, path=env.CONFIG_FILE):
        self.path = path
        self.d = dict(DEFAULTS)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    self.d.update({k: v for k, v in json.load(f).items() if k in DEFAULTS})
            except (OSError, ValueError):
                pass

    def __getitem__(self, k):
        return self.d[k]

    def __setitem__(self, k, v):
        self.d[k] = v

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.d, f, indent=2, ensure_ascii=False)
        os.replace(tmp, self.path)
