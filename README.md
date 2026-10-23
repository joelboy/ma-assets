# MĀ Asset Library

Web-optimised brand assets for **MĀ Wellness & Yoga** (Victoria, BC), served by GitHub Pages so any tool — Claude Design, ad builders, newsletters, the website — can reference a stable URL instead of uploading files.

**Gallery:** https://joelboy.github.io/ma-assets/  ·  **Machine index:** [`assets.json`](assets.json) · [`assets.txt`](assets.txt)

Every file is reachable at `https://joelboy.github.io/ma-assets/<path>`.

## Layout

| Path | What's in it |
|---|---|
| `photos/ethos-2025/web/…` | Ethos Imagery Oct 2025 Herald St shoot — SEO-named web selects, by category (`studio-details`, `instructors`, `clinic`, `teacher-training`, `headshots`, `web-ready`, `new-web-ready`, `initial-selections`) |
| `photos/ethos-2025/full-shoot/…` | Same shoot, the full delivery by category (`clinic-offerings`, `crystal-bowls-singing`, `earth-studio-*`, `silks`, `finals-*`) |
| `photos/kimjay-2020/…` | Kim Jay 2020 — `fall-studio`, `studio-finals`, `avatar-grove`, `island-view-beach` |
| `photos/seaside-2026/…` | MĀ Seaside (Cadboro Bay) Oct 2026 — `a003-graded` clip stills, `resolve-stills` |
| `photos/india-retreat/` | India retreat |
| `photos/events/diwali/` | Diwali / Sri Diwali retreat imagery |
| `photos/teachers/` | Teacher portraits (most live in `ethos-2025` — see `collections` in `assets.json`) |
| `ads/…` | Finished ad creative: `sound-healing/*`, `seaside-2026-10` |
| `posters/2026-09/` | Poster exports (App / Instagram / Print / Stories variants) |
| `brand/` | Logos (PNG/SVG/PDF) and the style guide |
| `video/seaside-2026/{9x16,4x5}/` | Seaside social cuts, 1080p H.264 |
| `thumbs/…` | 400 px thumbnails mirroring `photos/`, `ads/`, `posters/` |

Images are max **1600 px** on the long edge, JPEG q82 — right for web, social, ads and design mockups. For print, use the original: `assets.json` records each file's `orig` path on Joel's Mac (`Pictures/…` or `MĀ Yoga AMAI/…`).

## Updating

Originals never live here. To add or refresh assets:

1. Drop new originals into the right folder on the Mac (`Pictures/MĀ Photos/…`) and, if it's a new set, add a line to `SETS` in `tools/build_assets.py`.
2. `python3 tools/build_assets.py` (resumable — only new files are processed).
3. `python3 tools/build_index.py`
4. Commit and push `main`. Pages redeploys in about a minute.

Or just tell Claude "sync the asset library" — it runs the same steps.

## Limits to keep in mind

GitHub Pages: 1 GB site, 100 GB/month bandwidth, 100 MB per file. Current size is ~0.55 GB. Full-res originals and long video masters stay off this repo.
