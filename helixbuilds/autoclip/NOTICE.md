# AutoClip vendor snapshot (HelixBuilds)

Path: `helixbuilds/autoclip/` on branch `helix/autoclip-shorts`.

This directory is a **read-only provenance snapshot** of selected files from
[zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip) at SHA
`17100c05252b9a947ea1a857f8d0ea4f3af2317b` (MIT). Pin file: `.helix-autoclip-sha`.

HelixBuilds editing lives on `helixmaximusai/OpenCut`. AutoClip is absorbed
here as the **long-video-to-shorts vendor**, not as a second CapCut/OpenCut
product, not as a new GitHub repo, and not as a new venture.

This folder does **not** replace `classic/` (OpenCut classic editor).

## What was copied

- `backend/pipeline/` — original LLM-era steps (outline → timeline → score → title → cluster → cut)
- `backend/utils/ffmpeg_utils.py`
- `backend/utils/video_processor.py`
- `backend/utils/subtitle_processor.py`

## What was deliberately not copied

- Frontend / Tauri desktop (parallel AutoClip product)
- Bilibili / YouTube downloaders and uploaders (no auto-post, no IG/YT accounts)
- DashScope / OpenAI / Gemini / SiliconFlow LLM clients
- Docker / install-LLM scripts

## Runtime

**Do not import this vendor tree.** It still references AutoClip's DashScope
config and will not run here without paid keys. Stop rather than buy a key.

The working HelixBuilds path is `shorts/helix_shorts/` (ffmpeg + SRT
heuristics, no LLM key, human publish gate).
