"""CLI: python3 -m helix_shorts cut|conform|selftest|conform-selftest|test"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helix_shorts.conform import (
    ConformError,
    conform_waveforms,
    write_conform_outputs,
    write_picture_with_tone,
    write_tone_wav,
)
from helix_shorts.cut import probe_duration
from helix_shorts.ffmpeg import get_ffmpeg_path
from helix_shorts.pipeline import run_shorts
from helix_shorts.publish_gate import PublishGateError, assert_held_for_human


def _cmd_cut(args: argparse.Namespace) -> int:
    srt = Path(args.srt) if args.srt else None
    manifest = run_shorts(
        video=Path(args.video),
        out_dir=Path(args.out),
        srt=srt,
        max_clips=args.max_clips,
    )
    print(json.dumps({"ok": True, "manifest": manifest["manifest_path"]}, indent=2))
    return 0


def _cmd_conform(args: argparse.Namespace) -> int:
    payload = conform_waveforms(
        Path(args.video),
        Path(args.audio),
        max_windows=args.max_windows,
    )
    written = write_conform_outputs(payload, Path(args.out))
    print(
        json.dumps(
            {
                "ok": True,
                "json": written["json_path"],
                "report": written["report_path"],
                "global_offset_seconds": written["global_offset_seconds"],
                "method": written["method"],
                "filtergraph_suggestion": written["filtergraph_suggestion"],
                "remux_auto": written["remux"]["auto"],
            },
            indent=2,
        )
    )
    return 0


def _run_conform_selftest(work: Path) -> dict[str, object]:
    """Synthetic fixtures only. Never touches production DRAFT-VIDEO media."""
    work.mkdir(parents=True, exist_ok=True)
    silent = work / "silent.mp4"
    vo = work / "vo.wav"
    pictured = work / "pictured-tone.mp4"
    vo_early = work / "vo-early.wav"
    out_silent = work / "conform-silent"
    out_xcorr = work / "conform-xcorr"

    _make_test_video(silent, seconds=6)
    write_tone_wav(vo, tone_start=0.5, tone_duration=2.0, total_duration=4.0)
    silent_map = write_conform_outputs(conform_waveforms(silent, vo), out_silent)
    if not silent_map["video_silent"]:
        raise RuntimeError("silent fixture was not detected as silent")
    if silent_map["remux"]["auto"] is not False or silent_map["remux"]["applied"] is not False:
        raise RuntimeError("conform selftest must not remux")
    if silent_map["llm"]["used"]:
        raise RuntimeError("conform selftest used an LLM; that is not allowed")
    onset = silent_map["vo_onset_seconds"]
    if onset is None or abs(float(onset) - 0.5) > 0.08:
        raise RuntimeError(f"expected VO onset ~0.5s, got {onset}")
    if abs(float(silent_map["global_offset_seconds"]) + 0.5) > 0.08:
        raise RuntimeError(
            f"expected silent-picture offset ~-0.5s, got {silent_map['global_offset_seconds']}"
        )
    if "atrim" not in str(silent_map["filtergraph_suggestion"]):
        raise RuntimeError("expected atrim filtergraph suggestion for leading VO silence")
    if not Path(silent_map["json_path"]).is_file() or not Path(silent_map["report_path"]).is_file():
        raise RuntimeError("conform outputs missing")

    write_picture_with_tone(pictured, seconds=6.0, tone_start=1.0, tone_duration=2.0)
    write_tone_wav(vo_early, tone_start=0.5, tone_duration=2.0, total_duration=6.0)
    xcorr_map = write_conform_outputs(conform_waveforms(pictured, vo_early), out_xcorr)
    if xcorr_map["method"] != "waveform-xcorr":
        raise RuntimeError(f"expected waveform-xcorr, got {xcorr_map['method']}")
    recovered = float(xcorr_map["global_offset_seconds"])
    if abs(recovered - 0.5) > 0.08:
        raise RuntimeError(f"expected xcorr offset ~+0.5s, got {recovered}")
    if xcorr_map["remux"]["applied"] is not False:
        raise RuntimeError("xcorr path remuxed; that is not allowed")

    return {
        "silent_offset": silent_map["global_offset_seconds"],
        "silent_method": silent_map["method"],
        "xcorr_offset": xcorr_map["global_offset_seconds"],
        "xcorr_method": xcorr_map["method"],
        "remux_auto": False,
    }


def _write_sample_srt(path: Path) -> None:
    # Sparse start, dense middle (the highlight), sparse end.
    path.write_text(
        "\n".join(
            [
                "1",
                "00:00:00,000 --> 00:00:01,500",
                "Intro padding.",
                "",
                "2",
                "00:00:06,000 --> 00:00:08,000",
                "Pay attention now this is the actual point of the video",
                "",
                "3",
                "00:00:08,200 --> 00:00:10,000",
                "because the middle is packed with caption density.",
                "",
                "4",
                "00:00:10,100 --> 00:00:12,000",
                "Keep talking through the highlight window.",
                "",
                "5",
                "00:00:12,100 --> 00:00:14,000",
                "Still dense speech so the heuristic should pick this.",
                "",
                "6",
                "00:00:18,000 --> 00:00:19,000",
                "Bye.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _make_test_video(path: Path, seconds: int = 20) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        get_ffmpeg_path(),
        "-f",
        "lavfi",
        "-i",
        f"color=c=blue:s=320x568:d={seconds}:r=10",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-pix_fmt",
        "yuv420p",
        "-y",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not path.is_file():
        raise RuntimeError(f"failed to create test video: {result.stderr}")


def _cmd_selftest(_args: argparse.Namespace) -> int:
    work = Path(tempfile.mkdtemp(prefix="helix-shorts-"))
    try:
        video = work / "long.mp4"
        srt = work / "long.srt"
        out = work / "out"
        _make_test_video(video)
        _write_sample_srt(srt)
        duration = probe_duration(video)
        if duration < 15:
            raise RuntimeError(f"test video too short: {duration}")
        manifest = run_shorts(video=video, out_dir=out, srt=srt, max_clips=3)
        assert_held_for_human(manifest)
        if manifest["llm"]["used"] or manifest["llm"]["dashscope"]:
            raise RuntimeError("selftest used an LLM; that is not allowed")
        if manifest["clip_count"] < 1:
            raise RuntimeError("selftest produced zero clips")
        for clip in manifest["clips"]:
            if not Path(clip["file"]).is_file():
                raise RuntimeError(f"missing clip file: {clip['file']}")
        conform = _run_conform_selftest(work / "conform")
        print(
            json.dumps(
                {
                    "ok": True,
                    "clips": manifest["clip_count"],
                    "publish": manifest["publish"]["status"],
                    "llm": manifest["llm"]["path"],
                    "out": str(out),
                    "conform": conform,
                },
                indent=2,
            )
        )
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _cmd_conform_selftest(_args: argparse.Namespace) -> int:
    work = Path(tempfile.mkdtemp(prefix="helix-conform-"))
    try:
        result = _run_conform_selftest(work)
        print(json.dumps({"ok": True, "conform": result}, indent=2))
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _cmd_test(_args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(root / "tests"),
        pattern="test_*.py",
        top_level_dir=str(root),
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="helix_shorts",
        description=(
            "HelixBuilds shorts on OpenCut. Local ffmpeg + SRT heuristics. "
            "No DashScope/Qwen. No auto-post."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    cut = sub.add_parser("cut", help="cut shorts from a local video")
    cut.add_argument("--video", required=True, help="path to a local video file")
    cut.add_argument("--srt", default=None, help="optional SRT captions")
    cut.add_argument("--out", required=True, help="output directory")
    cut.add_argument("--max-clips", type=int, default=5)
    cut.set_defaults(func=_cmd_cut)

    conform = sub.add_parser(
        "conform",
        help="offline waveform offset map for silent picture + VO (no remux)",
    )
    conform.add_argument("--video", required=True, help="path to a local silent (or pictured) mp4")
    conform.add_argument("--audio", required=True, help="path to VO audio (mp3/wav)")
    conform.add_argument("--out", required=True, help="output directory for JSON + report")
    conform.add_argument("--max-windows", type=int, default=8)
    conform.set_defaults(func=_cmd_conform)

    selftest = sub.add_parser(
        "selftest",
        help="generate a silent test video, cut shorts, assert publish gate (exit 0)",
    )
    selftest.set_defaults(func=_cmd_selftest)

    conform_selftest = sub.add_parser(
        "conform-selftest",
        help="synthetic silent-mp4 + VO fixtures; recover known offsets (exit 0)",
    )
    conform_selftest.set_defaults(func=_cmd_conform_selftest)

    test = sub.add_parser("test", help="run unit tests")
    test.set_defaults(func=_cmd_test)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except PublishGateError as exc:
        print(f"publish gate blocked: {exc}", file=sys.stderr)
        return 2
    except ConformError as exc:
        print(f"helix_shorts conform failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — CLI boundary
        print(f"helix_shorts failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
