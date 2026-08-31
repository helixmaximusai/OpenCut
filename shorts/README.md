"""HelixBuilds shorts — AutoClip absorbed on the OpenCut host.

This is **not** a new product, repo, or venture. `helixmaximusai/OpenCut` is
the HelixBuilds editing code host. AutoClip is the long-video-to-shorts
pipeline sitting next to classic OpenCut, not a CapCut clone and not a
parallel AutoClip desktop app.

Sibling branch: `helix/autoclip-shorts` (does not change HOLD PR #1 on
`helix/working-and-tested`).

## Hard constraints honored

- No DashScope / Qwen / paid LLM. AutoClip's original steps 1–5 need those keys;
  they are vendored for provenance and **not executed**.
- No auto-post. No Instagram / YouTube / Bilibili accounts.
- Human publish gate on every manifest (`publish.status = held_for_human`).
- $0. Local ffmpeg + stdlib Python only.

## Verified command (exit 0)

From this directory, with `ffmpeg` on PATH:

```sh
cd shorts
PYTHONPATH=. python3 -m helix_shorts test
PYTHONPATH=. python3 -m helix_shorts selftest
```

`selftest` generates a silent 9:16 color clip, writes a synthetic SRT, cuts
shorts, and asserts the publish gate. No API keys.

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

`shorts/.helix-autoclip-sha` → [zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip) `17100c0`.
See `vendor/autoclip/NOTICE.md`. MIT license in `vendor/autoclip/LICENSE`.
