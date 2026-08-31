from __future__ import annotations

import unittest

from helix_shorts.heuristic import propose_windows
from helix_shorts.srt import parse_srt


DENSE = """1
00:00:00,000 --> 00:00:01,000
hi

2
00:00:08,000 --> 00:00:09,500
this is a much denser stretch of spoken words packed together

3
00:00:09,600 --> 00:00:11,000
continuing the same beat with even more caption text here

4
00:00:11,100 --> 00:00:13,000
still talking so the heuristic should prefer this window
"""


class HeuristicTests(unittest.TestCase):
    def test_picks_dense_middle(self) -> None:
        cues = parse_srt(DENSE)
        windows = propose_windows(cues, video_duration=20.0, max_clips=2)
        self.assertGreaterEqual(len(windows), 1)
        best = max(windows, key=lambda window: window.score)
        self.assertEqual(best.source, "srt-density")
        # Dense cues are 8s–13s; MIN_CLIP_SECONDS expands the window around them.
        self.assertLessEqual(best.start, 8.0)
        self.assertGreaterEqual(best.end, 13.0)
        self.assertGreater(best.score, 0)

    def test_duration_split_without_cues(self) -> None:
        windows = propose_windows([], video_duration=90.0, max_clips=3)
        self.assertGreaterEqual(len(windows), 2)
        self.assertTrue(all(window.source == "duration-split" for window in windows))

    def test_rejects_non_positive_duration(self) -> None:
        with self.assertRaises(ValueError):
            propose_windows([], video_duration=0)


if __name__ == "__main__":
    unittest.main()
