from __future__ import annotations

import unittest

from helix_shorts.srt import parse_srt, seconds_to_ffmpeg


SAMPLE = """1
00:00:01,000 --> 00:00:02,500
Hello world

2
00:00:03,000 --> 00:00:04,000
Second cue
"""


class SrtTests(unittest.TestCase):
    def test_parse_two_cues(self) -> None:
        cues = parse_srt(SAMPLE)
        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0].start, 1.0)
        self.assertEqual(cues[0].end, 2.5)
        self.assertIn("Hello", cues[0].text)

    def test_empty(self) -> None:
        self.assertEqual(parse_srt(""), [])

    def test_ffmpeg_time(self) -> None:
        self.assertEqual(seconds_to_ffmpeg(6.14), "00:00:06.140")
        self.assertEqual(seconds_to_ffmpeg(0), "00:00:00.000")


if __name__ == "__main__":
    unittest.main()
