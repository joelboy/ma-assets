#!/usr/bin/env python3
"""Build web-optimised MĀ asset library from originals on Joel's Mac.
Resumable: skips outputs that already exist. Writes manifest to _build/manifest.jsonl.
"""
import os, sys, json, hashlib, re, time
from pathlib import Path
from PIL import Image, ImageOps
Image.MAX_IMAGE_PIXELS = None

HOME = Path(os.environ["HOME"])
PICS = HOME / "mnt/Pictures"
PROJ = HOME / "mnt/MĀ Yoga AMAI"
OUT  = PROJ / "ma-assets"
FULL_MAX, FULL_Q = 1600, 82
THUMB_MAX, THUMB_Q = 400, 72
EXTS = {".jpg", ".jpeg", ".png"}

MP = PICS / "MĀ Photos"
KJ = MP / "Kim Jay Photos Complete"
SP = PICS / "Style Package"
# (repo set path, source dir, recursive, description)
SETS = [
  ("photos/ethos-2025/web/studio-details",  MP/"WEB-photos/1 - Studio Details", False, "Ethos Imagery Oct 2025 Herald St studio shoot – space, props, details"),
  ("photos/ethos-2025/web/instructors",     MP/"WEB-photos/2 - Instructors", False, "Ethos Imagery 2025 – instructors teaching, poses"),
  ("photos/ethos-2025/web/clinic",          MP/"WEB-photos/3 - Clinic Offerings", False, "Ethos Imagery 2025 – clinic / wellness offerings"),
  ("photos/ethos-2025/web/teacher-training",MP/"WEB-photos/4 - Teacher Training", False, "Ethos Imagery 2025 – YTT / teacher training"),
  ("photos/ethos-2025/web/headshots",       MP/"WEB-photos/5 - Headshots", False, "Ethos Imagery 2025 – teacher headshots"),
  ("photos/ethos-2025/web/web-ready",     MP/"WEB-photos/web-ready", False, "Ethos Imagery Oct 2025 – web-ready selects"),
  ("photos/ethos-2025/web/new-web-ready", MP/"WEB-photos/new-web-ready", False, "Ethos Imagery Oct 2025 – newer web-ready selects"),
  ("photos/ethos-2025/web/initial-selections", MP/"WEB-photos/Initial Selections", False, "Ethos Imagery Oct 2025 – initial selections"),
  ("photos/kimjay-2020/fall-studio",     KJ/"Ma yoga fall 2020", False, "Kim Jay 2020 – fall studio session"),
  ("photos/ethos-2025/full-shoot",         KJ/"Shoot 3 - Studio Images", True, "Ethos Imagery Oct 2025 – full shoot by category (large set)"),
  ("photos/kimjay-2020/studio-finals",          KJ/"STUDIO FINALS", False, "Kim Jay 2020 – studio finals (curated)"),
  ("photos/kimjay-2020/avatar-grove",   KJ/"AVATAR GROVE FINALS", False, "Kim Jay 2020 – Avatar Grove forest yoga"),
  ("photos/kimjay-2020/island-view-beach", KJ/"Island View Beach-web", False, "Kim Jay 2020 – Island View Beach yoga"),
  ("photos/poster-picks",                KJ/"MA Posters Oct 9 batch", False, "Curated photo picks used for posters (Oct 9 batch)"),
  ("photos/seaside-2026/resolve-stills", MP/"SeasideYoga", False, "MĀ Seaside (Cadboro Bay) Oct 2026 – Resolve stills (PNG)"),
  ("photos/seaside-2026/a003-graded",    PROJ/"_resolve/stills_graded", False, "MĀ Seaside Oct 2026 – A003 graded clip stills"),
  ("photos/india-retreat",               MP/"India Photos", False, "India retreat photos"),
  ("photos/teachers",                    MP/"Staff Photos", False, "Teacher / staff portraits"),
  ("photos/teachers",                    SP/"Common Teachers", False, "Teacher / staff portraits"),
  ("photos/teachers",                    SP/"YTT Pictures", False, "Teacher / staff portraits"),
  ("photos/teachers",                    SP, False, "Teacher / staff portraits"),  # Carley, Katyanna jpgs (non-recursive; logos filtered below)
  ("photos/events/diwali",               PICS/"Diwali", False, "Diwali – paintings (public domain) + generated art"),
  ("photos/events/diwali",               MP/"_web_diwali_retreat", False, "Sri Diwali retreat web photos"),
  ("ads/sound-healing/warm-carousel",    PICS/"Sound Healing Ads v6/Warm Carousel", False, "Sound Healing ad carousel v6 – warm"),
  ("ads/sound-healing/cold-carousel",    PICS/"Sound Healing Ads v6/Cold Carousel", False, "Sound Healing ad carousel v6 – cold"),
  ("ads/sound-healing/picks",            MP/"Sound Healing Ad 02", False, "Photo picks for Sound Healing ads"),
  ("ads/sound-healing/picks",            MP/"Sound-Healing-Ad-Creatives", False, "Sound Healing ad creatives"),
  ("ads/sound-healing/picks",            SP/"Images Sound Healing", False, "Sound Healing style-package images"),
  ("ads/seaside-2026-10",                PROJ/"ad-creative-2026-10-19", False, "MĀ Seaside launch ad creative 2026-10-19"),
  ("posters/2026-09",                    PROJ/"posters", False, "Poster exports Sept 2026 (App/Instagram/Print/Stories variants)"),
]
# single extra files
EXTRA = [("photos/ethos-2025/web/studio-details", MP/"282-DL-Ethos-100625-MA Yoga-1778.jpg")]
# brand: copied verbatim (no resize)
BRAND = [
  (SP/"_logo_extract", ["0_MĀ_Logo.png","1_MĀ_Logo_Gold.png","2_MĀ_Logo_White.png","3_MĀ_Logo_Dark.png","4_MĀ.png","logo-mark-cmyk-copy.pdf"]),
  (SP, ["ma-logo.png","mā-yoga-logo-mark-full-colour-cmyk.pdf","style-guide.html"]),
  (PROJ/"poster-assets", ["MA-LOGO.png","ma-yoga-logo-full-colour.png","ma-yoga-logo.svg"]),
]
SKIP_NAME = re.compile(r"(review_|contact_sheet|\.drx$|copy\.jpg$)", re.I)
TEACHER_ROOT_ALLOW = {"Carley DeGoede 02.jpg", "Katyanna Ryan.jpg"}

def slug(s):
    s = s.replace("MĀ","MA").replace("mā","ma").replace("Ā","A").replace("ā","a")
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip("-").lower()
    s = re.sub(r"-{2,}", "-", s)
    return s

def quick_hash(p: Path):
    h = hashlib.md5(); st = p.stat(); h.update(str(st.st_size).encode())
    with open(p,"rb") as f: h.update(f.read(1<<20))
    return h.hexdigest()[:16]

def process(src: Path, set_path: str, desc: str, seen, mf, counters):
    if SKIP_NAME.search(src.name) and "YTT Pictures" not in str(src): return
    if src.suffix.lower() not in EXTS: return
    qh = quick_hash(src)
    stem = slug(src.stem); 
    if stem.endswith("-copy"): stem = stem[:-5]
    rel_full = f"{set_path}/{stem}.jpg"
    if qh in seen:
        mf.write(json.dumps({"dup_of": seen[qh], "orig": str(src), "set": set_path})+"\n"); counters["dup"]+=1; return
    seen[qh] = rel_full
    full = OUT/rel_full; thumb = OUT/"thumbs"/rel_full
    if full.exists() and thumb.exists():
        counters["skip"]+=1
        with Image.open(full) as im: w,h = im.size
        mf.write(json.dumps({"path": rel_full, "thumb": f"thumbs/{rel_full}", "set": set_path, "set_desc": desc, "w": w, "h": h, "bytes": full.stat().st_size, "orig": str(src), "hash": qh})+"\n"); return
    try:
        with Image.open(src) as im:
            ow, oh = im.size
            im.draft("RGB", (FULL_MAX*2, FULL_MAX*2))
            im = ImageOps.exif_transpose(im)
            if im.mode in ("RGBA","LA","P"):
                bg = Image.new("RGB", im.size, (255,255,255)); 
                im = im.convert("RGBA"); bg.paste(im, mask=im.split()[-1]); im = bg
            elif im.mode != "RGB": im = im.convert("RGB")
            full.parent.mkdir(parents=True, exist_ok=True); thumb.parent.mkdir(parents=True, exist_ok=True)
            f = im.copy(); f.thumbnail((FULL_MAX, FULL_MAX), Image.LANCZOS)
            f.save(full, "JPEG", quality=FULL_Q, optimize=True, progressive=True)
            t = im.copy(); t.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
            t.save(thumb, "JPEG", quality=THUMB_Q, optimize=True)
            mf.write(json.dumps({"path": rel_full, "thumb": f"thumbs/{rel_full}", "set": set_path, "set_desc": desc, "w": f.size[0], "h": f.size[1], "bytes": full.stat().st_size, "orig": str(src), "orig_w": ow, "orig_h": oh, "hash": qh})+"\n")
            counters["done"]+=1
    except Exception as e:
        mf.write(json.dumps({"error": str(e), "orig": str(src)})+"\n"); counters["err"]+=1

BUDGET = float(sys.argv[1]) if len(sys.argv)>1 else 1e9
def main():
    (OUT/"_build").mkdir(parents=True, exist_ok=True)
    seen = {}; counters = {"done":0,"skip":0,"dup":0,"err":0}; t0=time.time()
    with open(OUT/"_build/manifest.jsonl","w") as mf:
        for set_path, d, rec, desc in SETS:
            if not d.exists(): mf.write(json.dumps({"error":"missing dir","orig":str(d)})+"\n"); continue
            files = sorted(p for p in (d.rglob("*") if rec else d.iterdir()) if p.is_file())
            if d == SP: files = [p for p in files if p.name in TEACHER_ROOT_ALLOW]
            for p in files:
                sp = set_path if not rec else f"{set_path}/{slug(p.parent.name)}" if p.parent != d else set_path
                process(p, sp, desc, seen, mf, counters)
                if time.time()-t0 > BUDGET: print("BUDGET HIT", counters, flush=True); return
            print(f"{set_path}: {counters} {time.time()-t0:.0f}s", flush=True)
        for set_path, p in EXTRA: process(p, set_path, "Ethos Imagery 2025", seen, mf, counters)
        for d, names in BRAND:
            for n in names:
                src = d/n
                if not src.exists(): continue
                dst = OUT/"brand"/slug(src.stem)+src.suffix.lower() if False else OUT/"brand"/(slug(src.stem)+src.suffix.lower())
                dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists(): dst.write_bytes(src.read_bytes())
                mf.write(json.dumps({"path": f"brand/{dst.name}", "set":"brand", "set_desc":"Logos, brand marks, style guide", "bytes": dst.stat().st_size, "orig": str(src)})+"\n")
    print("DONE", counters, f"{time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__": main()
