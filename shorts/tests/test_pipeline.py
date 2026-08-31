from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from helix_shorts.cli import _make_test_video, _write_sample_srt
from helix_shorts.pipeline import run_shorts
from helix_shorts.publish_gate import assert_held_for_human


class PipelineTests(unittest.TestCase):
    def test_cut_silent_video_holds_publish_gate(self) -> None:
        work = Path(tempfile.mkdtemp(prefix="helix-shorts-test-"))
        self.addCleanup(lambda: shutil.rmtree(work, ignore_errors=True))
        video = work / "long.mp4"
        srt = work / "long.srt"
        out = work / "out"
        _make_test_video(video, seconds=20)
        _write_sample_srt(srt)
        manifest = run_shorts(video=video, out_dir=out, srt=srt, max_clips=3)
        assert_held_for_human(manifest)
        self.assertFalse(manifest["llm"]["used"])
        self.assertFalse(manifest["llm"]["dashscope"])
        self.assertGreaterEqual(manifest["clip_count"], 1)
        self.assertTrue(Path(manifest["clips"][0]["file"]).is_file())
        self.assertTrue(Path(manifest["manifest_path"]).is_file())
        self.assertEqual(manifest["publish"]["auto_post"], False)
        self.assertEqual(manifest["opencut"]["kind"], "helixbuilds-opencut-shorts-import")


if __name__ == "__main__":
    unittest.main()
