"""Telecharge les fichiers MAIN d'un mod Nexus (API v1) dans dl\<modId>\ ; cle lue dans nexus.env, jamais affichee."""
import os
_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # Ink Flow project root
_DEPOT = os.environ.get("INKFLOW_DEPOT") or os.path.abspath(os.path.join(_ROOT, "..", "..", ".."))   # mods folder: three levels above the project, or INKFLOW_DEPOT
import json, os, subprocess, sys, urllib.parse
def key():
    for line in open((os.environ.get("NEXUS_ENV") or os.path.join(_DEPOT, "..", "..", "Nexus", "__DEV", "nexus.env")), encoding="utf-8-sig"):
        if line.strip().startswith("NEXUS_API_KEY="): return line.split("=",1)[1].strip()
    sys.exit("cle absente")
def curl(args):
    p=subprocess.run(["curl","-sS","--fail","-L","-A","hk-cp-tattoo/1"]+args,capture_output=True); 
    if p.returncode: sys.exit(p.stderr.decode(errors="replace"))
    return p.stdout
k=key(); mod=sys.argv[1]; cat=sys.argv[2] if len(sys.argv)>2 else "MAIN"
out=os.path.join(r"C:\__DEV\cyberpunk\ink_flow\dl",mod); os.makedirs(out,exist_ok=True)
info=json.loads(curl(["-H",f"apikey: {k}",f"https://api.nexusmods.com/v1/games/cyberpunk2077/mods/{mod}.json"]))
print("mod:",info["name"],"| version",info["version"],"| auteur",info["author"],"| maj",info.get("updated_time"))
files=json.loads(curl(["-H",f"apikey: {k}",f"https://api.nexusmods.com/v1/games/cyberpunk2077/mods/{mod}/files.json"]))["files"]
for f in files: print("  ",f["file_id"],f["category_name"],"|",f["file_name"],"|",f["version"],"|",f["size_kb"],"ko")
for f in files:
    if f["category_name"]!=cat: continue
    links=json.loads(curl(["-H",f"apikey: {k}",f"https://api.nexusmods.com/v1/games/cyberpunk2077/mods/{mod}/files/{f['file_id']}/download_link.json"]))
    url=links[0]["URI"].replace(" ","%20"); dest=os.path.join(out,f["file_name"])
    subprocess.run(["curl","-sS","--fail","-L","-A","hk-cp-tattoo/1","-o",dest,url],check=True)
    print("telecharge:",dest,os.path.getsize(dest))
