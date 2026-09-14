# AutoClip vendor snapshot (HelixBuilds)

Path: `helixbuilds/autoclip/` on branch `helix/autoclip-shorts`.

This directory is a **read-only provenance pin** of
[zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip) at SHA
`17100c05252b9a947ea1a857f8d0ea4f3af2317b` (MIT). Pin file: `.helix-autoclip-sha`.

HelixBuilds editing lives on `helixmaximusai/OpenCut`. AutoClip is absorbed
here as the **long-video-to-shorts vendor**, not as a second CapCut/OpenCut
product, not as a new GitHub repo, and not as a new venture.

This folder does **not** replace `classic/` (OpenCut classic editor).

## What lives here

- `.helix-autoclip-sha` — exact upstream commit
- `LICENSE` — MIT from AutoClip
- `NOTICE.md` — this file

Upstream source is **not** copied into this tree. Incomplete pipeline files
(missing `llm_client`, DashScope config, `mkdir` on import) fought the host
rule "do not run this / do not buy a key." Read the original at:

https://github.com/zhouxiaoka/autoclip/tree/17100c05252b9a947ea1a857f8d0ea4f3af2317b

## What was deliberately not copied

- Frontend / Tauri desktop (parallel AutoClip product)
- Bilibili / YouTube downloaders and uploaders (no auto-post, no IG/YT accounts)
- DashScope / OpenAI / Gemini / SiliconFlow LLM clients
- Docker / install-LLM scripts
- `backend/` pipeline and utils (see upstream SHA)

## Runtime

**Do not import a vendor tree here.** There isn't one. Stop rather than buy
a key.

The working HelixBuilds path is `shorts/helix_shorts/` (ffmpeg + SRT
heuristics, no LLM key, human publish gate).
