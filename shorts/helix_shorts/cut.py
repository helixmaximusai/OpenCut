"""Cut clip files with ffmpeg. Stream-copy path from AutoClip VideoProcessor."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from helix_shorts.ffmpeg import get_ffmpeg_path, get_ffprobe_path
from helix_shorts.heuristic import ClipWindow
from helix_shorts.srt import seconds_to_ffmpeg


class CutError(RuntimeError):
    """ffmpeg/ffprobe failed."""


def probe_duration(video: Path) -> float:
    if not video.is_file():
        raise CutError(f"video not found: {video}")
    cmd = [
        get_ffprobe_path(),
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        str(video),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise CutError(f"ffprobe failed: {result.stderr.strip() or result.stdout}")
    payload = json.loads(result.stdout)
    duration = payload.get("format", {}).get("duration")
    if duration is None:
        raise CutError("ffprobe did not return format.duration")
    return float(duration)


def extract_clip(input_video: Path, output_path: Path, start: float, end: float) -> None:
    """Extract [start, end) seconds. Re-encodes so lavfi test clips and copy-unfriendly sources work."""
    if end <= start:
        raise CutError(f"invalid clip range {start} -> {end}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    duration = end - start
    cmd = [
        get_ffmpeg_path(),
        "-ss",
        seconds_to_ffmpeg(start),
        "-i",
        str(input_video),
        "-t",
        f"{duration:.3f}",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-crf",
        "28",
        "-an",
        "-movflags",
        "+faststart",
        "-y",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not output_path.is_file():
        raise CutError(f"ffmpeg extract failed: {result.stderr.strip() or result.stdout}")


def cut_windows(input_video: Path, clips_dir: Path, windows: list[ClipWindow]) -> list[Path]:
    paths: list[Path] = []
    for index, window in enumerate(windows, start=1):
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in window.title)[:40]
        if not safe:
            safe = f"clip-{index:02d}"
        out = clips_dir / f"{index:02d}_{safe}.mp4"
        extract_clip(input_video, out, window.start, window.end)
        paths.append(out)
    return paths
