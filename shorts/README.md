# HelixBuilds shorts — no-key runtime on the OpenCut host

This is **not** a new product, repo, or venture. `helixmaximusai/OpenCut` is
the HelixBuilds editing code host. AutoClip is vendored at
[`helixbuilds/autoclip/`](../helixbuilds/autoclip/) (not under `classic/`).
This directory is the **running** long-video-to-shorts path.

Sibling branch: `helix/autoclip-shorts` (does not change HOLD PR #1 on
`helix/working-and-tested`).

## Hard constraints honored

- No DashScope / Qwen / paid LLM. AutoClip's original steps 1–5 need those keys;
  they sit in `helixbuilds/autoclip/` and are **not executed**.
- No auto-post. No Instagram / YouTube / Bilibili accounts.
- Human publish gate on every manifest (`publish.status = held_for_human`).
- $0. Local ffmpeg + stdlib Python only.

## Verified command (exit 0)

From this directory, with `ffmpeg` on PATH:

```sh
cd shorts
PYTHONPATH=. python3 -m helix_shorts test
PYTHONPATH=. python3 -m helix_shorts selftest
PYTHONPATH=. python3 -m helix_shorts conform-selftest
```

`selftest` generates a silent 9:16 color clip, writes a synthetic SRT, cuts
shorts, asserts the publish gate, and runs the waveform-conform fixtures.
`conform-selftest` is the dedicated offset-recovery check (silent mp4 + VO,
plus an xcorr tone pair). Synthetic lavfi fixtures only — never Nick's real
Video #1 / `DRAFT-VIDEO-01-*.mp4`. No API keys.

## Waveform conform (offline, no remux)

Picture-accept helper: given a **silent mp4** and a **VO** (`mp3`/`wav`),
write a JSON offset map + a human report. Optional ffmpeg filtergraph is a
**suggestion** for remux *after* a human accepts picture. This CLI does not
remux production files.

```sh
cd shorts
PYTHONPATH=. python3 -m helix_shorts conform --video /path/to/silent.mp4 --audio /path/to/vo.wav --out ./out
```

Outputs:

- `out/helix-conform.json` — `global_offset_seconds` (VO delay vs picture;
  negative = VO leads), optional per-window suggestions, `filtergraph_suggestion`
- `out/helix-conform.txt` — the same map in prose, plus an example remux
  command that is **not** executed

`global_offset_seconds` is how long to delay the VO so it lines up with
picture. On a silent picture the tool uses VO-onset (trim leading silence).
If the mp4 happens to carry a reference tone, it falls back to waveform
cross-correlation. `$0`. No Higgs / Eleven / DashScope / YouTube.

Cut a real local file (still does not post):

```sh
PYTHONPATH=. python3 -m helix_shorts cut --video /path/to/long.mp4 --srt /path/to/captions.srt --out ./out
```

Outputs:

- `out/clips/*.mp4` — candidate shorts
- `out/helix-shorts.json` — manifest (gate + llm.used=false)
- `out/opencut-import.json` — file list for classic OpenCut media import

## What still needs a key or a human

| Need | Required to run this path? |
| --- | --- |
| DashScope / Qwen / OpenAI / Gemini | **No.** Do not buy. Original AutoClip scoring/titles stay dark. |
| Instagram / YouTube / Bilibili account | **No.** Uploads are not wired. |
| Human publish | **Yes**, if anything ever goes public. Review in OpenCut, then a human posts. |
| Captions | Optional. Without `--srt`, the pipeline duration-splits (labeled `duration-split`, not AI). Local faster-whisper can make an SRT later; not installed here. |
| Redis / Celery / AutoClip frontend / Tauri | Not used. |

## Vendor pin

[`helixbuilds/autoclip/.helix-autoclip-sha`](../helixbuilds/autoclip/.helix-autoclip-sha) → [zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip) `17100c0`.
See [`helixbuilds/autoclip/NOTICE.md`](../helixbuilds/autoclip/NOTICE.md).
