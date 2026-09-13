---
name: helixbuilds-autoclip-shorts
description: Use when working on HelixBuilds shorts (AutoClip absorbed on helixmaximusai/OpenCut). No-key ffmpeg + SRT path only. Covers when-to-use, $0 / no-DashScope constraints, verify commands, and what fails closed without Qwen keys.
---

# HelixBuilds shorts (AutoClip absorb, no-key)

**Candidate only.** Lives in-repo at `skill-candidates/helixbuilds-autoclip-shorts/SKILL.md`. Do not install this into a user skill library. Do not merge. Do not publish. Do not enable Qwen / DashScope. Do not buy a key. **$0**.

Sibling of the editing-host candidate (`skill-candidates/helixbuilds-editing-host/`). This skill is the **long-video-to-shorts** path, not the classic OpenCut editor build.

## When to use

Use this when the task is **HelixBuilds shorts** on the existing OpenCut host (`helixmaximusai/OpenCut`).

- **Absorb, do not fork.** AutoClip is HelixBuilds shorts on this host. Not a new repo, venture, registry row, or CapCut/OpenCut clone.
- **Runtime = `shorts/`.** `python3 -m helix_shorts` (ffmpeg + SRT heuristics, human publish gate). No paid LLM.
- **Vendor = provenance only.** `helixbuilds/autoclip/` is a snapshot of [zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip) pin `17100c0` (`helixbuilds/autoclip/.helix-autoclip-sha`). Do **not** import or run it.
- **Branch = `helix/autoclip-shorts`.** Draft PR #2. Sibling of HOLD PR #1 (`helix/working-and-tested`). Do not merge either. Do not clobber `classic/`.
- **No auto-post.** No Instagram / YouTube / Bilibili accounts. Manifest `publish.status` must stay `held_for_human`.

Do **not** use this skill to stand up AutoClip-the-desktop-app, buy DashScope/Qwen, wire uploads, or treat the vendor tree as the running pipeline.

## Verify (no keys)

`ffmpeg` and `ffprobe` on PATH. Unset paid-LLM vars so the path cannot silently pick up a key:

```sh
unset DASHSCOPE_API_KEY OPENAI_API_KEY QWEN_API_KEY GEMINI_API_KEY SILICONFLOW_API_KEY
cd shorts
PYTHONPATH=. python3 -m helix_shorts test
PYTHONPATH=. python3 -m helix_shorts selftest
```

**Pass:** both commands exit **0**. `selftest` prints `ok: true`, `publish: held_for_human`, `llm: srt-heuristic-or-duration-split`. No DashScope, no Qwen, no network LLM.

Cut a local file (still does not post):

```sh
PYTHONPATH=. python3 -m helix_shorts cut --video /path/to/long.mp4 --srt /path/to/captions.srt --out ./out
```

Outputs: `out/clips/*.mp4`, `out/helix-shorts.json`, `out/opencut-import.json`.

### Re-verified (improve loop #2 — do not merge)

| Ref | Tip SHA | Notes |
|---|---|---|
| PR #2 `helix/autoclip-shorts` | `b1fa9719a5e34f0022ea351bb15a14d9ef4549e7` | Open draft. `test` **0** (12 tests), `selftest` **0**. Keys unset. |
| PR #1 `helix/working-and-tested` | `5d5cbad4334e13b958d226f1cb3d424998d95f3c` | Open draft HOLD. Do not merge. `classic/` not clobbered. |

Env on that re-run: `DASHSCOPE_API_KEY` / `OPENAI_API_KEY` / `QWEN_API_KEY` unset. ffmpeg 6.1.1, Python 3.12.3.

## What fails closed without keys

The no-key path is **green** because it never calls a paid LLM. The original AutoClip steps stay dark. Do not buy a key to “make them green.”

| Surface | Without DashScope / Qwen / OpenAI / Gemini | Why it stays closed |
|---|---|---|
| Vendor steps 1–5 (`helixbuilds/autoclip/backend/pipeline/step{1,2,3,4,5}_*.py`) | **Import fails.** `ModuleNotFoundError: No module named 'backend.utils.llm_client'` | LLM client was deliberately not vendored (`NOTICE.md`). |
| Vendor step 6 (`step6_video.py`) | **Import fails.** `ModuleNotFoundError: No module named 'backend.core'` | `backend/core/shared_config.py` not copied. |
| `backend.utils.llm_client` / `backend.core.shared_config` / `backend.utils.text_processor` | **Absent.** Files are not in the tree. | Fail closed at import, not at a live API call. |
| Vendor prompts (`helixbuilds/autoclip/prompt/*.txt`) | **Absent.** | Steps 1–5 cannot load outline/timeline/score/title/cluster prompts. |
| Vendor `pipeline/config.py` `DEFAULT_API_KEY` | **`None`** when those env vars are unset. | `DASHSCOPE_API_KEY or OPENAI_API_KEY`. Empty string if the var is exported blank — still no usable key. Do not set one. |
| HelixBuilds shorts LLM block | `used/dashscope/qwen/openai/gemini` all **false**; `path` = `srt-heuristic-or-duration-split` | `shorts/helix_shorts/publish_gate.py` `llm_block()`. |
| Human publish gate | `auto_post=true` (or YT/IG/Bilibili flags) raises `PublishGateError` | CLI exits **2**. No accounts wired. |
| AutoClip frontend / Tauri / Docker / downloaders / uploaders | **Not copied.** | Not a parallel AutoClip product. |
| Captions without `--srt` | Duration-split fallback, labeled `duration-split` (not AI). | Optional local faster-whisper later; not installed; do not buy a cloud ASR key. |
| Classic OpenCut live import | Manifest is written; dragging files into the editor UI is **not** part of this headless verify. | Use the editing-host skill for `classic/` `bun run build`. |

Probed on `b1fa9719` with keys unset: vendor step imports failed as in the table; `helix_shorts` still cut a silent 9:16 clip and held publish.

## Still not a product launch

- Do not merge PR #2 or this candidate.
- Do not enable Qwen / DashScope / OpenAI / Gemini.
- Do not publish or deploy.
- $0.
