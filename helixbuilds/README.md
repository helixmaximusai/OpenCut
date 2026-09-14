# HelixBuilds overlays (this OpenCut host)

Not a new repo. `helixmaximusai/OpenCut` is the HelixBuilds editing code host.

| Path | What |
| --- | --- |
| [`autoclip/`](autoclip/) | Vendored AutoClip snapshot (provenance). Do **not** run it: upstream steps need DashScope/Qwen. |
| [`../shorts/`](../shorts/) | HelixBuilds shorts runtime: ffmpeg + SRT heuristics, no LLM key, human publish gate. |

Sibling branch `helix/autoclip-shorts`. Do not merge HOLD PR #1. Do not clobber `classic/`.
