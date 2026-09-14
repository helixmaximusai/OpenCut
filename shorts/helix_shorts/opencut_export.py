"""OpenCut (HelixBuilds editing) import manifest. Files only — no upload."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from helix_shorts.heuristic import ClipWindow


def opencut_import_manifest(
    *,
    clips: list[tuple[ClipWindow, Path]],
    aspect: str = "9:16",
) -> dict[str, Any]:
    return {
        "kind": "helixbuilds-opencut-shorts-import",
        "editor": "classic OpenCut on helixmaximusai/OpenCut (HelixBuilds editing)",
        "aspect": aspect,
        "auto_open": False,
        "clips": [
            {
                "file": str(path.name),
                "name": window.title,
                "start_seconds": window.start,
                "end_seconds": window.end,
                "duration_seconds": round(window.duration, 3),
                "media_type": "video",
                "reason": window.reason,
                "source": window.source,
            }
            for window, path in clips
        ],
        "instructions": (
            "Import each clip as media in classic OpenCut (`classic/apps/web`). "
            "This pipeline does not create an OpenCut project file and does not publish."
        ),
    }
