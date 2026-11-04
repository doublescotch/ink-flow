import json, sys, os
B = "base/characters/common/player_base_bodies/player_female_average"
FILES = [
 ("vanilla body", "C:/__DEV/cyberpunk/ink_flow/x/van2/"+B+"/t0_000_pwa_base__full.mesh.json"),
 ("Angel body", "C:/__DEV/cyberpunk/ink_flow/x/angel/"+B+"/t0_000_pwa_base__full.mesh.json"),
 ("FW body", "011_UV_Framework_Texture_3.2.1/"+B+"/t0_000_pwa_base__full.mesh.json"),
 ("FW arm L", "011_UV_Framework_Texture_3.2.1/"+B+"/arms_hq/a0_000_pwa_base_hq__l.mesh.json"),
 ("FW arm R", "011_UV_Framework_Texture_3.2.1/"+B+"/arms_hq/a0_000_pwa_base_hq__r.mesh.json"),
 ("FW fpp torso", "011_UV_Framework_Texture_3.2.1/"+B+"/fpp/t0_000_pwa_fpp__torso.mesh.json"),
 ("FW fpp arm L", "011_UV_Framework_Texture_3.2.1/"+B+"/fpp/a0_000_pwa_fpp__full_l.mesh.json"),
 ("FW male body", "011_UV_Framework_Texture_3.2.1/base/characters/common/player_base_bodies/player_man_average/t0_000_pma_base__full.mesh.json"),
 ("FW head F", "011_UV_Framework_Texture_3.2.1/base/characters/head/player_base_heads/player_female_average/h0_000_pwa_c__basehead/h0_000_pwa_c__basehead.mesh.json"),
 ("Solo body", "006_Solo_OG_2.0/"+B+"/t0_000_pwa_base__full.mesh.json"),
 ("Solo fpp torso", "006_Solo_OG_2.0/"+B+"/fpp/t0_000_pwa_fpp__torso.mesh.json"),
 ("Solo tattoo_01 shell", "006_Solo_OG_2.0/"+B+"/tattoos/tx_000_pwa_base__full_tattoo_01.mesh.json"),
 ("Solo arm L UV", "005_Solo_OG_2.0_Arms_UV/"+B+"/arms_hq/a0_000_pwa_base_hq__l.mesh.json"),
 ("Solo fpp arm L UV", "005_Solo_OG_2.0_Arms_UV/"+B+"/fpp/a0_000_pwa_fpp__full_l.mesh.json"),
 ("Songbird arm L UV", "005_Songbird_Arms_UV/"+B+"/arms_hq/a0_000_pwa_base_hq__l.mesh.json"),
 ("Songbird seamfix", "005_Songbird_Arms_UV/"+B+"/t0_000_pwa_base__full_seamfix.mesh.json"),
 ("Songbird body UV", "009_Songbird_Body_2.0_UV/"+B+"/t0_000_pwa_base__full.mesh.json"),
 ("Songbird body arm L", "009_Songbird_Body_2.0_UV/"+B+"/arms_hq/a0_000_pwa_base_hq__l.mesh.json"),
]
def dp(v):
    if isinstance(v, dict) and "DepotPath" in v: return v["DepotPath"]["$value"]
    return v
for label, p in FILES:
    if not os.path.isfile(p): print(f"## {label}: ABSENT {p}"); continue
    r = json.load(open(p, encoding="utf-8"))["Data"]["RootChunk"]
    ent = r["materialEntries"]
    stores = {k: len(v) for k, v in (("buffer", (r.get("localMaterialBuffer") or {}).get("materials") or []),
              ("preload", r.get("preloadLocalMaterialInstances") or []), ("local", r.get("localMaterialInstances") or [])) if v}
    ext = len(r.get("externalMaterials") or []), len(r.get("preloadExternalMaterials") or [])
    chunks = r["renderResourceBlob"]["Data"]["header"]["renderChunkInfos"]
    apps = [a["Data"]["name"]["$value"] for a in r["appearances"]]
    print(f"## {label}: {len(ent)} entries, local={sum(e['isLocalInstance'] for e in ent)}, stores={stores}, external={ext}, "
          f"chunks={len(chunks)} verts={sum(c['numVertices'] for c in chunks)}, apps={len(apps)} ({apps[0] if apps else '-'}…)")
    mats = (r.get("localMaterialBuffer") or {}).get("materials") or [x["Data"] for x in (r.get("preloadLocalMaterialInstances") or [])] or [x["Data"] for x in (r.get("localMaterialInstances") or [])]
    seen = set()
    for e in ent:
        nm = e["name"]["$value"]
        if e["isLocalInstance"]:
            m = mats[e["index"]]
            base = dp(m.get("baseMaterial"))
            vals = {}
            for v in m.get("values") or []:
                for k, val in v.items():
                    if k != "$type": vals[k] = dp(val)
            key = (base, tuple(sorted(vals)))
            sec = vals.get("SecondaryAlbedo")
            if key in seen and sec is None: continue
            seen.add(key)
            print(f"   {nm:28s} base={base}  SecondaryAlbedo={sec}  params={sorted(vals)}")
        else:
            print(f"   {nm:28s} EXTERNAL -> {dp((r.get('externalMaterials') or r.get('preloadExternalMaterials'))[e['index']])}")
    for nm in ("ext",):
        pass
