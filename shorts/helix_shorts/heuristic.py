"""No-key highlight windows from captions (or even duration splits).

AutoClip's step1–5 call DashScope/Qwen. HelixBuilds shorts does not.
Speech-dense SRT clusters become 9:16 candidate shorts.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from helix_shorts.srt import Cue


MIN_CLIP_SECONDS = 12.0
MAX_CLIP_SECONDS = 60.0
TARGET_CLIP_SECONDS = 30.0
MERGE_GAP_SECONDS = 1.5
DEFAULT_MAX_CLIPS = 5


@dataclass(frozen=True)
class ClipWindow:
    start: float
    end: float
    score: float
    title: str
    reason: str
    source: str  # "srt-density" | "duration-split"

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


def _merge_cues(cues: list[Cue], gap: float) -> list[list[Cue]]:
    if not cues:
        return []
    ordered = sorted(cues, key=lambda cue: cue.start)
    clusters: list[list[Cue]] = [[ordered[0]]]
    for cue in ordered[1:]:
        last = clusters[-1][-1]
        if cue.start - last.end <= gap:
            clusters[-1].append(cue)
        else:
            clusters.append([cue])
    return clusters


def _score_cluster(cluster: list[Cue]) -> float:
    duration = max(cluster[-1].end - cluster[0].start, 0.001)
    chars = sum(cue.char_count for cue in cluster)
    density = chars / duration
    return density * (1.0 + math.log1p(len(cluster)))


def _fit_duration(start: float, end: float, video_duration: float) -> tuple[float, float]:
    start = max(0.0, start)
    end = min(video_duration, end)
    length = end - start
    if length < MIN_CLIP_SECONDS:
        extra = MIN_CLIP_SECONDS - length
        start = max(0.0, start - extra / 2)
        end = min(video_duration, start + MIN_CLIP_SECONDS)
    if end - start > MAX_CLIP_SECONDS:
        mid = (start + end) / 2
        start = max(0.0, mid - TARGET_CLIP_SECONDS / 2)
        end = min(video_duration, start + TARGET_CLIP_SECONDS)
    return round(start, 3), round(end, 3)


def windows_from_cues(
    cues: list[Cue],
    video_duration: float,
    max_clips: int = DEFAULT_MAX_CLIPS,
) -> list[ClipWindow]:
    if video_duration <= 0:
        raise ValueError("video_duration must be > 0")
    clusters = _merge_cues(cues, MERGE_GAP_SECONDS)
    candidates: list[ClipWindow] = []
    for index, cluster in enumerate(clusters, start=1):
        raw_start, raw_end = cluster[0].start, cluster[-1].end
        start, end = _fit_duration(raw_start, raw_end, video_duration)
        if end - start < 1.0:
            continue
        snippet = cluster[0].text.strip()[:48] or f"clip-{index:02d}"
        candidates.append(
            ClipWindow(
                start=start,
                end=end,
                score=_score_cluster(cluster),
                title=snippet,
                reason="caption-density cluster (no LLM)",
                source="srt-density",
            )
        )
    candidates.sort(key=lambda window: window.score, reverse=True)
    picked: list[ClipWindow] = []
    for candidate in candidates:
        if len(picked) >= max_clips:
            break
        overlaps = any(
            not (candidate.end <= existing.start or candidate.start >= existing.end)
            for existing in picked
        )
        if overlaps:
            continue
        picked.append(candidate)
    picked.sort(key=lambda window: window.start)
    return picked


def windows_from_duration(
    video_duration: float,
    max_clips: int = DEFAULT_MAX_CLIPS,
) -> list[ClipWindow]:
    """Fallback when there is no SRT: even splits. Not AI. Labeled as such."""
    if video_duration <= 0:
        raise ValueError("video_duration must be > 0")
    clip_len = min(TARGET_CLIP_SECONDS, max(MIN_CLIP_SECONDS, video_duration))
    if video_duration <= clip_len + 1:
        return [
            ClipWindow(
                start=0.0,
                end=round(video_duration, 3),
                score=0.0,
                title="full-window",
                reason="no captions; duration split (not AI)",
                source="duration-split",
            )
        ]
    n = min(max_clips, max(1, int(video_duration // clip_len)))
    windows: list[ClipWindow] = []
    for i in range(n):
        start = i * clip_len
        end = min(video_duration, start + clip_len)
        if end - start < MIN_CLIP_SECONDS and i > 0:
            break
        windows.append(
            ClipWindow(
                start=round(start, 3),
                end=round(end, 3),
                score=0.0,
                title=f"window-{i + 1:02d}",
                reason="no captions; duration split (not AI)",
                source="duration-split",
            )
        )
    return windows


def propose_windows(
    cues: Optional[list[Cue]],
    video_duration: float,
    max_clips: int = DEFAULT_MAX_CLIPS,
) -> list[ClipWindow]:
    if cues:
        windows = windows_from_cues(cues, video_duration, max_clips=max_clips)
        if windows:
            return windows
    return windows_from_duration(video_duration, max_clips=max_clips)
