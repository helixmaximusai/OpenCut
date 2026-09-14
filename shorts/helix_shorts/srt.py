"""Stdlib SRT parser. No pysrt (AutoClip's subtitle_processor depends on it)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


_TIME = re.compile(
    r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})"
    r"\s*-->\s*"
    r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})"
)


@dataclass(frozen=True)
class Cue:
    index: int
    start: float
    end: float
    text: str

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)

    @property
    def char_count(self) -> int:
        return len(re.sub(r"\s+", "", self.text))


def _hms_to_seconds(h: str, m: str, s: str, ms: str) -> float:
    millis = int(ms.ljust(3, "0")[:3])
    return int(h) * 3600 + int(m) * 60 + int(s) + millis / 1000.0


def parse_srt(text: str) -> list[Cue]:
    """Parse SRT (or a close dialect) into timed cues."""
    if not text.strip():
        return []

    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip())
    cues: list[Cue] = []
    for block in blocks:
        lines = [line.strip("\ufeff") for line in block.split("\n") if line.strip()]
        if not lines:
            continue
        time_line_idx = 0
        index = len(cues) + 1
        if lines[0].isdigit() and len(lines) > 1:
            index = int(lines[0])
            time_line_idx = 1
        if time_line_idx >= len(lines):
            continue
        match = _TIME.search(lines[time_line_idx])
        if not match:
            continue
        start = _hms_to_seconds(*match.group(1, 2, 3, 4))
        end = _hms_to_seconds(*match.group(5, 6, 7, 8))
        body = " ".join(lines[time_line_idx + 1 :]).strip()
        cues.append(Cue(index=index, start=start, end=end, text=body))
    return cues


def load_srt(path: Path) -> list[Cue]:
    return parse_srt(path.read_text(encoding="utf-8"))


def seconds_to_ffmpeg(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds % 1) * 1000))
    if millis == 1000:
        secs += 1
        millis = 0
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
