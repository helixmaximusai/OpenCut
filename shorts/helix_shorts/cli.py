"""CLI: python3 -m helix_shorts cut|selftest|test"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helix_shorts.cut import probe_duration
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
    from helix_shorts.ffmpeg import get_ffmpeg_path

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
        print(
            json.dumps(
                {
                    "ok": True,
                    "clips": manifest["clip_count"],
                    "publish": manifest["publish"]["status"],
                    "llm": manifest["llm"]["path"],
                    "out": str(out),
                },
                indent=2,
            )
        )
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

    selftest = sub.add_parser(
        "selftest",
        help="generate a silent test video, cut shorts, assert publish gate (exit 0)",
    )
    selftest.set_defaults(func=_cmd_selftest)

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
    except Exception as exc:  # noqa: BLE001 — CLI boundary
        print(f"helix_shorts failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
