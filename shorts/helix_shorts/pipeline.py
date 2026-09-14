"""Long-video-to-shorts pipeline (no LLM key, no auto-post)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from helix_shorts import HOST_REPO, PRODUCT_NAME
from helix_shorts.cut import cut_windows, probe_duration
from helix_shorts.heuristic import ClipWindow, propose_windows
from helix_shorts.opencut_export import opencut_import_manifest
from helix_shorts.publish_gate import (
    assert_held_for_human,
    llm_block,
    publish_block,
)
from helix_shorts.srt import load_srt


def run_shorts(
    video: Path,
    out_dir: Path,
    srt: Optional[Path] = None,
    max_clips: int = 5,
) -> dict[str, Any]:
    video = video.resolve()
    out_dir = out_dir.resolve()
    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    duration = probe_duration(video)
    cues = load_srt(srt) if srt else []
    windows = propose_windows(cues, duration, max_clips=max_clips)
    if not windows:
        raise RuntimeError("no clip windows proposed")

    paths = cut_windows(video, clips_dir, windows)
    pairs: list[tuple[ClipWindow, Path]] = list(zip(windows, paths))

    manifest: dict[str, Any] = {
        "product": PRODUCT_NAME,
        "host": HOST_REPO,
        "source_video": str(video),
        "source_srt": str(srt) if srt else None,
        "video_duration_seconds": round(duration, 3),
        "clip_count": len(pairs),
        "clips": [
            {
                "file": str(path),
                "title": window.title,
                "start": window.start,
                "end": window.end,
                "duration": round(window.duration, 3),
                "score": round(window.score, 4),
                "reason": window.reason,
                "source": window.source,
            }
            for window, path in pairs
        ],
        "opencut": opencut_import_manifest(clips=pairs),
        "publish": publish_block(),
        "llm": llm_block(),
        "still_needs": {
            "paid_qwen_dashscope": (
                "Optional only. AutoClip's original outline/score/title steps need a "
                "DashScope/Qwen (or other paid LLM) key. HelixBuilds shorts does not "
                "call them. Do not buy a key for this path."
            ),
            "human_publish": (
                "A human must review and, if they choose, publish from OpenCut. "
                "No IG/YT/Bilibili accounts are used here."
            ),
            "local_whisper": (
                "If the source has no SRT, generate one locally (faster-whisper) "
                "or pass --srt. Duration-split is the no-caption fallback."
            ),
        },
    }
    assert_held_for_human(manifest)

    manifest_path = out_dir / "helix-shorts.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    opencut_path = out_dir / "opencut-import.json"
    opencut_path.write_text(
        json.dumps(manifest["opencut"], indent=2) + "\n", encoding="utf-8"
    )
    manifest["manifest_path"] = str(manifest_path)
    manifest["opencut_import_path"] = str(opencut_path)
    return manifest
