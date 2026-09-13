"""Offline waveform conform: silent picture + VO → offset map.

Local ffmpeg + stdlib only. Never remuxes production files. Never calls
DashScope / Eleven / Higgs / YouTube. Suggestion strings only.
"""

from __future__ import annotations

import json
import math
import struct
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from helix_shorts import HOST_REPO, PRODUCT_NAME, PUBLISH_HELD
from helix_shorts.cut import probe_duration
from helix_shorts.ffmpeg import get_ffmpeg_path, get_ffprobe_path
from helix_shorts.publish_gate import publish_block

PCM_RATE = 8000
HOP_SAMPLES = 160  # 20 ms
HOP_SECONDS = HOP_SAMPLES / PCM_RATE
SILENCE_PEAK = 180.0  # s16 peak; digital silence sits far below this
ONSET_RATIO = 0.12
MIN_ISLAND_SECONDS = 0.25
DEFAULT_MAX_SEARCH_SECONDS = 10.0
DEFAULT_MAX_WINDOWS = 8
CONFORM_KIND = "helixbuilds-waveform-conform"


class ConformError(RuntimeError):
    """ffmpeg/ffprobe or conform input failed."""


@dataclass(frozen=True)
class Envelope:
    values: tuple[float, ...]
    hop_seconds: float
    sample_rate: int
    peak: float

    @property
    def duration(self) -> float:
        return len(self.values) * self.hop_seconds

    @property
    def silent(self) -> bool:
        return self.peak < SILENCE_PEAK


@dataclass(frozen=True)
class WindowSuggestion:
    index: int
    picture_start: float
    picture_end: float
    audio_start: float
    audio_end: float
    offset_seconds: float
    confidence: float
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "picture_start": round(self.picture_start, 3),
            "picture_end": round(self.picture_end, 3),
            "audio_start": round(self.audio_start, 3),
            "audio_end": round(self.audio_end, 3),
            "offset_seconds": round(self.offset_seconds, 3),
            "confidence": round(self.confidence, 4),
            "reason": self.reason,
        }


def has_audio_stream(path: Path) -> bool:
    if not path.is_file():
        raise ConformError(f"media not found: {path}")
    cmd = [
        get_ffprobe_path(),
        "-v",
        "error",
        "-select_streams",
        "a",
        "-show_entries",
        "stream=index,codec_type",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise ConformError(f"ffprobe audio probe failed: {result.stderr.strip() or result.stdout}")
    payload = json.loads(result.stdout or "{}")
    streams = payload.get("streams") or []
    return any(stream.get("codec_type") == "audio" for stream in streams)


def extract_pcm_s16le(path: Path) -> bytes:
    """Decode any ffmpeg-readable media to mono s16le @ PCM_RATE. Empty if no audio."""
    if not path.is_file():
        raise ConformError(f"media not found: {path}")
    if not has_audio_stream(path):
        return b""
    cmd = [
        get_ffmpeg_path(),
        "-nostdin",
        "-v",
        "error",
        "-i",
        str(path),
        "-ac",
        "1",
        "-ar",
        str(PCM_RATE),
        "-f",
        "s16le",
        "-acodec",
        "pcm_s16le",
        "pipe:1",
    ]
    result = subprocess.run(cmd, capture_output=True, check=False)
    if result.returncode != 0:
        err = (result.stderr or b"").decode("utf-8", errors="replace").strip()
        raise ConformError(f"ffmpeg pcm extract failed: {err}")
    return result.stdout or b""


def pcm_to_envelope(pcm: bytes, hop_samples: int = HOP_SAMPLES) -> Envelope:
    if hop_samples <= 0:
        raise ValueError("hop_samples must be > 0")
    if len(pcm) < 2:
        return Envelope(values=(), hop_seconds=hop_samples / PCM_RATE, sample_rate=PCM_RATE, peak=0.0)
    count = len(pcm) // 2
    samples = struct.unpack("<" + "h" * count, pcm[: count * 2])
    values: list[float] = []
    peak = 0.0
    for start in range(0, count, hop_samples):
        chunk = samples[start : start + hop_samples]
        if not chunk:
            break
        acc = 0.0
        local_peak = 0.0
        for sample in chunk:
            mag = abs(sample)
            acc += mag * mag
            if mag > local_peak:
                local_peak = mag
        rms = math.sqrt(acc / len(chunk))
        values.append(rms)
        if local_peak > peak:
            peak = local_peak
    return Envelope(
        values=tuple(values),
        hop_seconds=hop_samples / PCM_RATE,
        sample_rate=PCM_RATE,
        peak=peak,
    )


def energy_islands(
    envelope: Envelope,
    *,
    min_seconds: float = MIN_ISLAND_SECONDS,
    ratio: float = ONSET_RATIO,
) -> list[tuple[float, float]]:
    if not envelope.values or envelope.silent:
        return []
    thresh = max(max(envelope.values) * ratio, 1.0)
    islands: list[tuple[float, float]] = []
    index = 0
    n = len(envelope.values)
    hop = envelope.hop_seconds
    while index < n:
        if envelope.values[index] < thresh:
            index += 1
            continue
        end = index + 1
        while end < n and envelope.values[end] >= thresh:
            end += 1
        start_s = index * hop
        end_s = end * hop
        if end_s - start_s >= min_seconds:
            islands.append((round(start_s, 3), round(end_s, 3)))
        index = end
    return islands


def first_onset_seconds(envelope: Envelope) -> Optional[float]:
    islands = energy_islands(envelope)
    if not islands:
        return None
    return islands[0][0]


def delay_vo_to_match_picture(
    picture: Envelope,
    vo: Envelope,
    *,
    max_abs_seconds: float = DEFAULT_MAX_SEARCH_SECONDS,
) -> tuple[float, float]:
    """Return (offset_seconds, confidence).

    offset_seconds is how long to delay the VO so it lines up with picture.
    Positive: picture leads (adelay the VO). Negative: VO leads (trim VO).
    """
    if not picture.values or not vo.values or picture.silent or vo.silent:
        return 0.0, 0.0
    hop = picture.hop_seconds
    max_lag = max(1, int(max_abs_seconds / hop))
    # Raw RMS (not mean-centered): silence*silence stays ~0 so a wrap-around
    # of the quiet floor cannot beat an actual tone alignment.
    pic = picture.values
    voice = vo.values
    best_lag = 0
    best = -2.0
    for lag in range(-max_lag, max_lag + 1):
        score = _ncc_at_lag(pic, voice, lag)
        if score > best:
            best = score
            best_lag = lag
    onset_pic = first_onset_seconds(picture)
    onset_vo = first_onset_seconds(vo)
    if onset_pic is not None and onset_vo is not None:
        prior_lag = int(round((onset_pic - onset_vo) / hop))
        if abs(prior_lag) <= max_lag:
            prior_score = _ncc_at_lag(pic, voice, prior_lag)
            # Prefer the onset prior when it is nearly as good (avoids aliases).
            if prior_score >= best - 0.05:
                best_lag = prior_lag
                best = max(best, prior_score)
    confidence = max(0.0, min(1.0, best))
    return best_lag * hop, confidence


def _ncc_at_lag(picture: tuple[float, ...], vo: tuple[float, ...], lag: int) -> float:
    # picture[i] vs vo[i - lag]. lag>0 means VO event is earlier (delay VO).
    acc = 0.0
    norm_p = 0.0
    norm_v = 0.0
    p_len = len(picture)
    v_len = len(vo)
    start = max(0, lag)
    end = min(p_len, v_len + lag)
    if end <= start:
        return -1.0
    for index in range(start, end):
        vo_index = index - lag
        p_val = picture[index]
        v_val = vo[vo_index]
        acc += p_val * v_val
        norm_p += p_val * p_val
        norm_v += v_val * v_val
    denom = math.sqrt(norm_p * norm_v)
    if denom <= 1e-12:
        return -1.0
    return acc / denom


def suggest_filtergraph(offset_seconds: float) -> str:
    """ffmpeg filtergraph *suggestion* only. Never executed by this module."""
    if abs(offset_seconds) < 0.001:
        return "[1:a]anull[a]"
    if offset_seconds > 0:
        millis = int(round(offset_seconds * 1000.0))
        return f"[1:a]adelay={millis}:all=1[a]"
    return f"[1:a]atrim=start={abs(offset_seconds):.3f},asetpts=PTS-STARTPTS[a]"


def _onset_confidence(envelope: Envelope, onset: Optional[float]) -> float:
    if onset is None or envelope.silent or not envelope.values:
        return 0.0
    peak = max(envelope.values)
    mean = sum(envelope.values) / len(envelope.values)
    if peak <= 0:
        return 0.0
    return max(0.0, min(1.0, (peak - mean) / peak))


def _windows_from_islands(
    islands: list[tuple[float, float]],
    *,
    offset: float,
    confidence: float,
    picture_duration: float,
    reason: str,
    max_windows: int,
) -> list[WindowSuggestion]:
    suggestions: list[WindowSuggestion] = []
    for index, (audio_start, audio_end) in enumerate(islands[:max_windows], start=1):
        picture_start = max(0.0, audio_start + offset)
        picture_end = max(picture_start, min(picture_duration, audio_end + offset))
        suggestions.append(
            WindowSuggestion(
                index=index,
                picture_start=picture_start,
                picture_end=picture_end,
                audio_start=audio_start,
                audio_end=audio_end,
                offset_seconds=offset,
                confidence=confidence,
                reason=reason,
            )
        )
    return suggestions


def _local_window_offsets(
    picture: Envelope,
    vo: Envelope,
    *,
    global_offset: float,
    max_windows: int,
) -> list[WindowSuggestion]:
    if picture.silent or vo.silent or not picture.values:
        return []
    hop = picture.hop_seconds
    total = max(picture.duration, vo.duration, hop)
    count = min(max_windows, max(1, int(total / 2.0)))
    span = total / count
    search = min(2.0, DEFAULT_MAX_SEARCH_SECONDS)
    suggestions: list[WindowSuggestion] = []
    for index in range(count):
        start = index * span
        end = start + span
        pic_slice = _slice_envelope(picture, start, end)
        vo_start = start - global_offset
        vo_slice = _slice_envelope(vo, vo_start - search, vo_start + span + search)
        if pic_slice.silent or vo_slice.silent:
            continue
        local, confidence = delay_vo_to_match_picture(pic_slice, vo_slice, max_abs_seconds=search)
        # vo_slice starts at vo_start-search, so convert back to a global VO delay.
        offset = global_offset + local
        suggestions.append(
            WindowSuggestion(
                index=index + 1,
                picture_start=round(start, 3),
                picture_end=round(end, 3),
                audio_start=round(start - offset, 3),
                audio_end=round(end - offset, 3),
                offset_seconds=offset,
                confidence=confidence,
                reason="windowed waveform xcorr",
            )
        )
    return suggestions


def _slice_envelope(envelope: Envelope, start: float, end: float) -> Envelope:
    hop = envelope.hop_seconds
    i0 = max(0, int(start / hop))
    i1 = min(len(envelope.values), max(i0 + 1, int(math.ceil(end / hop))))
    values = envelope.values[i0:i1]
    peak = max(values) if values else 0.0
    return Envelope(values=values, hop_seconds=hop, sample_rate=envelope.sample_rate, peak=peak)


def build_report(payload: dict[str, Any]) -> str:
    windows = payload.get("windows") or []
    lines = [
        "HelixBuilds waveform conform",
        "============================",
        f"kind: {payload.get('kind')}",
        f"video: {payload.get('video')}",
        f"audio: {payload.get('audio')}",
        f"video_duration_seconds: {payload.get('video_duration_seconds')}",
        f"audio_duration_seconds: {payload.get('audio_duration_seconds')}",
        f"video_has_audio: {payload.get('video_has_audio')}",
        f"video_silent: {payload.get('video_silent')}",
        f"audio_silent: {payload.get('audio_silent')}",
        f"method: {payload.get('method')}",
        f"global_offset_seconds: {payload.get('global_offset_seconds')}",
        f"offset_meaning: {payload.get('offset_meaning')}",
        f"vo_onset_seconds: {payload.get('vo_onset_seconds')}",
        f"confidence: {payload.get('confidence')}",
        "",
        "windows:",
    ]
    if not windows:
        lines.append("  (none)")
    for window in windows:
        lines.append(
            "  {index}: picture {picture_start:.3f}-{picture_end:.3f}  "
            "audio {audio_start:.3f}-{audio_end:.3f}  "
            "offset {offset_seconds:+.3f}s  conf {confidence:.3f}  {reason}".format(**window)
        )
    remux = payload.get("remux") or {}
    lines.extend(
        [
            "",
            "filtergraph_suggestion (not executed):",
            f"  {payload.get('filtergraph_suggestion')}",
            "",
            "example remux AFTER picture accept (do not auto-run on production files):",
            "  ffmpeg -i PICTURE.mp4 -i VO.wav -filter_complex "
            f"'{payload.get('filtergraph_suggestion')}' "
            "-map 0:v -map '[a]' -c:v copy -c:a aac -shortest OUT.mp4",
            "",
            f"remux.auto: {remux.get('auto')}",
            f"remux.applied: {remux.get('applied')}",
            f"remux.note: {remux.get('note')}",
            f"publish.status: {(payload.get('publish') or {}).get('status')}",
            f"llm.used: {(payload.get('llm') or {}).get('used')}",
        ]
    )
    return "\n".join(lines) + "\n"


def _llm_block() -> dict[str, Any]:
    return {
        "used": False,
        "dashscope": False,
        "qwen": False,
        "openai": False,
        "gemini": False,
        "higgs": False,
        "eleven": False,
        "path": "waveform-envelope-offline",
    }


def conform_waveforms(
    video: Path,
    audio: Path,
    *,
    max_windows: int = DEFAULT_MAX_WINDOWS,
    max_search_seconds: float = DEFAULT_MAX_SEARCH_SECONDS,
) -> dict[str, Any]:
    if max_windows < 1:
        raise ValueError("max_windows must be >= 1")
    if max_search_seconds <= 0:
        raise ValueError("max_search_seconds must be > 0")
    video = video.resolve()
    audio = audio.resolve()
    if not video.is_file():
        raise ConformError(f"video not found: {video}")
    if not audio.is_file():
        raise ConformError(f"audio not found: {audio}")

    video_duration = probe_duration(video)
    audio_duration = probe_duration(audio)
    video_has_audio = has_audio_stream(video)
    picture_env = pcm_to_envelope(extract_pcm_s16le(video) if video_has_audio else b"")
    vo_env = pcm_to_envelope(extract_pcm_s16le(audio))
    vo_onset = first_onset_seconds(vo_env)
    islands = energy_islands(vo_env)

    if picture_env.silent or not video_has_audio:
        method = "silent-picture-vo-onset"
        offset = 0.0 if vo_onset is None else -float(vo_onset)
        confidence = _onset_confidence(vo_env, vo_onset)
        windows = _windows_from_islands(
            islands,
            offset=offset,
            confidence=confidence,
            picture_duration=video_duration,
            reason="vo energy island on silent picture",
            max_windows=max_windows,
        )
    else:
        method = "waveform-xcorr"
        offset, confidence = delay_vo_to_match_picture(
            picture_env, vo_env, max_abs_seconds=max_search_seconds
        )
        windows = _local_window_offsets(
            picture_env, vo_env, global_offset=offset, max_windows=max_windows
        )
        if not windows:
            windows = _windows_from_islands(
                islands,
                offset=offset,
                confidence=confidence,
                picture_duration=video_duration,
                reason="vo energy island (xcorr fallback)",
                max_windows=max_windows,
            )

    payload: dict[str, Any] = {
        "product": PRODUCT_NAME,
        "host": HOST_REPO,
        "kind": CONFORM_KIND,
        "video": str(video),
        "audio": str(audio),
        "video_duration_seconds": round(video_duration, 3),
        "audio_duration_seconds": round(audio_duration, 3),
        "duration_delta_seconds": round(video_duration - audio_duration, 3),
        "video_has_audio": video_has_audio,
        "video_silent": bool(picture_env.silent or not video_has_audio),
        "audio_silent": bool(vo_env.silent),
        "vo_onset_seconds": None if vo_onset is None else round(vo_onset, 3),
        "global_offset_seconds": round(offset, 3),
        "offset_meaning": (
            "seconds to delay the VO relative to picture start "
            "(negative = VO leads; trim or advance VO)"
        ),
        "confidence": round(confidence, 4),
        "method": method,
        "windows": [window.as_dict() for window in windows],
        "filtergraph_suggestion": suggest_filtergraph(offset),
        "remux": {
            "auto": False,
            "after_picture_accept": True,
            "applied": False,
            "note": (
                "Suggestion only. Do not auto-remux production files. "
                "Apply only after a human accepts picture."
            ),
        },
        "publish": publish_block(),
        "llm": _llm_block(),
        "still_needs": {
            "human_picture_accept": (
                "A human accepts picture, then may apply the filtergraph "
                "suggestion. This CLI does not remux."
            ),
            "paid_apis": (
                "Do not buy keys. Waveform conform is offline ffmpeg + stdlib."
            ),
        },
    }
    if payload["publish"]["status"] != PUBLISH_HELD or payload["remux"]["auto"] is not False:
        raise ConformError("conform payload violated hold/no-remux constraints")
    return payload


def write_conform_outputs(payload: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "helix-conform.json"
    report_path = out_dir / "helix-conform.txt"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(build_report(payload), encoding="utf-8")
    payload = dict(payload)
    payload["json_path"] = str(json_path)
    payload["report_path"] = str(report_path)
    return payload


def write_tone_wav(
    path: Path,
    *,
    tone_start: float,
    tone_duration: float,
    total_duration: float,
    frequency: int = 1000,
) -> None:
    """Synthetic VO/reference tone. Leading silence + sine + pad. No network."""
    if tone_start < 0 or tone_duration <= 0 or total_duration <= 0:
        raise ValueError("tone timings must be positive")
    if tone_start + tone_duration > total_duration + 1e-6:
        raise ValueError("tone must fit inside total_duration")
    path.parent.mkdir(parents=True, exist_ok=True)
    delay_ms = int(round(tone_start * 1000.0))
    cmd = [
        get_ffmpeg_path(),
        "-nostdin",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency={frequency}:sample_rate={PCM_RATE}:duration={tone_duration}",
        "-af",
        f"adelay={delay_ms}:all=1,apad=whole_dur={total_duration}",
        "-t",
        f"{total_duration:.3f}",
        "-ac",
        "1",
        "-ar",
        str(PCM_RATE),
        "-y",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not path.is_file():
        raise ConformError(f"failed to create tone wav: {result.stderr}")


def write_picture_with_tone(
    path: Path,
    *,
    seconds: float,
    tone_start: float,
    tone_duration: float,
    frequency: int = 1000,
) -> None:
    """Synthetic picture that *does* carry a reference tone (for xcorr tests)."""
    if seconds <= 0:
        raise ValueError("seconds must be > 0")
    path.parent.mkdir(parents=True, exist_ok=True)
    delay_ms = int(round(tone_start * 1000.0))
    cmd = [
        get_ffmpeg_path(),
        "-nostdin",
        "-f",
        "lavfi",
        "-i",
        f"color=c=red:s=320x568:d={seconds}:r=10",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency={frequency}:sample_rate={PCM_RATE}:duration={tone_duration}",
        "-filter_complex",
        f"[1:a]adelay={delay_ms}:all=1,apad=whole_dur={seconds}[a]",
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-shortest",
        "-y",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not path.is_file():
        raise ConformError(f"failed to create pictured tone video: {result.stderr}")
