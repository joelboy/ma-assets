#!/usr/bin/env python3
"""Build assets.json + index.html (gallery) from _build/manifest.jsonl and the files on disk.
Run from the repo root:  python3 tools/build_index.py
"""
import json, os, re, subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://joelboy.github.io/ma-assets/"
SET_LABELS = {
    "photos/ethos-2025/web": "Ethos 2025 · web selects",
    "photos/ethos-2025/full-shoot": "Ethos 2025 · full shoot",
    "photos/kimjay-2020": "Kim Jay 2020",
    "photos/seaside-2026": "MĀ Seaside 2026",
    "photos/india-retreat": "India retreat",
    "photos/teachers": "Teachers",
    "photos/events": "Events",
    "ads": "Ad creative",
    "posters": "Posters",
    "brand": "Brand / logos",
    "video": "Video",
}

def clean_orig(p):
    p = p.replace("\\", "/")
    for marker in ("/mnt/Pictures/", "/mnt/MĀ Yoga AMAI/"):
        if marker in p:
            return ("Pictures/" if marker.endswith("Pictures/") else "MĀ Yoga AMAI/") + p.split(marker, 1)[1]
    return p

def main():
    items, dups = {}, []
    mf = ROOT / "_build/manifest.jsonl"
    if mf.exists():
        for line in mf.read_text().splitlines():
            d = json.loads(line)
            if "dup_of" in d:
                dups.append({"of": d["dup_of"], "orig": clean_orig(d["orig"]), "set": d["set"]}); continue
            if "path" not in d: continue
            d["orig"] = clean_orig(d["orig"])
            items[d["path"]] = d
    # anything on disk not in manifest (e.g. video, brand added later)
    for sub in ("photos", "ads", "posters", "brand", "video"):
        for p in sorted((ROOT / sub).rglob("*")):
            if not p.is_file() or p.name.startswith("."): continue
            rel = p.relative_to(ROOT).as_posix()
            if rel in items: continue
            d = {"path": rel, "set": "/".join(rel.split("/")[:-1]), "bytes": p.stat().st_size}
            if p.suffix.lower() in (".jpg", ".jpeg", ".png"):
                try:
                    with Image.open(p) as im: d["w"], d["h"] = im.size
                except Exception: pass
                t = ROOT / "thumbs" / rel
                if t.exists(): d["thumb"] = f"thumbs/{rel}"
            elif p.suffix.lower() == ".mp4":
                try:
                    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                          "stream=width,height,duration", "-of", "csv=p=0", str(p)],
                                         capture_output=True, text=True).stdout.strip().split(",")
                    d["w"], d["h"], d["duration"] = int(out[0]), int(out[1]), round(float(out[2]), 1)
                except Exception: pass
            items[rel] = d
    # drop manifest entries whose file disappeared
    items = {k: v for k, v in items.items() if (ROOT / k).exists()}
    for d in items.values():
        d["url"] = BASE + d["path"]
        if d.get("thumb"): d["thumb_url"] = BASE + d["thumb"]
        d["orientation"] = ("portrait" if d.get("h", 0) > d.get("w", 0) else "landscape" if d.get("w") else None)
        d["group"] = next((v for k, v in SET_LABELS.items() if d["set"].startswith(k)), d["set"].split("/")[0])
    assets = sorted(items.values(), key=lambda d: d["path"])
    # "picks" collections: sets that turned out to be duplicates of canonical files
    collections = {}
    for dd in dups:
        if dd["set"].endswith("/picks") or "poster" in dd["set"] or dd["set"] == "photos/teachers":
            collections.setdefault(dd["set"], []).append(dd["of"])
    out = {"base_url": BASE, "generated_from": "tools/build_index.py", "count": len(assets),
           "sets": sorted({d["set"] for d in assets}), "assets": assets, "collections": collections}
    (ROOT / "assets.json").write_text(json.dumps(out, ensure_ascii=False, indent=0))
    # compact machine listing for quick grep
    (ROOT / "assets.txt").write_text("\n".join(f'{d["path"]}\t{d.get("w","")}x{d.get("h","")}\t{d.get("orig","")}' for d in assets) + "\n")
    # gallery
    html = (ROOT / "tools/gallery_template.html").read_text()
    (ROOT / "index.html").write_text(html.replace("__COUNT__", str(len(assets))))
    print(f"{len(assets)} assets, {len(dups)} dup refs, {len(collections)} collections")

if __name__ == "__main__":
    main()
