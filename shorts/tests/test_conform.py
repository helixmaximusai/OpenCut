from __future__ import annotations

import math
import shutil
import tempfile
import unittest
from pathlib import Path

from helix_shorts.cli import _make_test_video
from helix_shorts.conform import (
    Envelope,
    conform_waveforms,
    delay_vo_to_match_picture,
    energy_islands,
    first_onset_seconds,
    pcm_to_envelope,
    suggest_filtergraph,
    write_conform_outputs,
    write_picture_with_tone,
    write_tone_wav,
)
from helix_shorts.publish_gate import assert_held_for_human


def _tone_envelope(*, start_bin: int, width: int = 40, total: int = 200) -> Envelope:
    values = [1.0] * total
    for index in range(start_bin, min(total, start_bin + width)):
        values[index] = 400.0
    return Envelope(values=tuple(values), hop_seconds=0.02, sample_rate=8000, peak=400.0)


class EnvelopeMathTests(unittest.TestCase):
    def test_pcm_rms_envelope_length(self) -> None:
        # 8000 samples = 1s @ 8kHz; hop 160 → 50 bins
        pcm = (b"\x00\x00" * 80) + (b"\xff\x7f" * 80) + (b"\x00\x00" * 7840)
        env = pcm_to_envelope(pcm)
        self.assertGreaterEqual(len(env.values), 49)
        self.assertFalse(env.silent)
        self.assertGreater(env.peak, 180)

    def test_empty_pcm_is_silent(self) -> None:
        env = pcm_to_envelope(b"")
        self.assertTrue(env.silent)
        self.assertEqual(env.values, ())

    def test_onset_and_islands(self) -> None:
        env = _tone_envelope(start_bin=25)  # 0.50s
        onset = first_onset_seconds(env)
        self.assertIsNotNone(onset)
        assert onset is not None
        self.assertAlmostEqual(onset, 0.5, delta=0.03)
        islands = energy_islands(env)
        self.assertGreaterEqual(len(islands), 1)
        self.assertAlmostEqual(islands[0][0], 0.5, delta=0.03)

    def test_xcorr_recovers_known_lag(self) -> None:
        picture = _tone_envelope(start_bin=50)  # 1.00s
        vo = _tone_envelope(start_bin=25)  # 0.50s
        offset, confidence = delay_vo_to_match_picture(picture, vo)
        self.assertGreater(confidence, 0.8)
        self.assertAlmostEqual(offset, 0.5, delta=0.03)

    def test_xcorr_zero_when_aligned(self) -> None:
        env = _tone_envelope(start_bin=40)
        offset, confidence = delay_vo_to_match_picture(env, env)
        self.assertGreater(confidence, 0.9)
        self.assertAlmostEqual(offset, 0.0, delta=0.03)

    def test_silent_picture_skips_xcorr(self) -> None:
        silent = Envelope(values=(0.0, 0.0, 0.0), hop_seconds=0.02, sample_rate=8000, peak=0.0)
        vo = _tone_envelope(start_bin=10)
        offset, confidence = delay_vo_to_match_picture(silent, vo)
        self.assertEqual(offset, 0.0)
        self.assertEqual(confidence, 0.0)

    def test_filtergraph_delay_and_trim(self) -> None:
        self.assertEqual(suggest_filtergraph(0.0), "[1:a]anull[a]")
        self.assertEqual(suggest_filtergraph(0.4), "[1:a]adelay=400:all=1[a]")
        self.assertEqual(
            suggest_filtergraph(-0.5),
            "[1:a]atrim=start=0.500,asetpts=PTS-STARTPTS[a]",
        )


class SyntheticFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.work = Path(tempfile.mkdtemp(prefix="helix-conform-test-"))
        self.addCleanup(lambda: shutil.rmtree(self.work, ignore_errors=True))

    def test_silent_mp4_plus_vo_onset(self) -> None:
        video = self.work / "silent.mp4"
        audio = self.work / "vo.wav"
        out = self.work / "out"
        _make_test_video(video, seconds=6)
        write_tone_wav(audio, tone_start=0.5, tone_duration=2.0, total_duration=4.0)
        payload = write_conform_outputs(conform_waveforms(video, audio), out)
        assert_held_for_human(payload)
        self.assertTrue(payload["video_silent"])
        self.assertFalse(payload["video_has_audio"])
        self.assertEqual(payload["method"], "silent-picture-vo-onset")
        self.assertFalse(payload["llm"]["used"])
        self.assertFalse(payload["remux"]["auto"])
        self.assertFalse(payload["remux"]["applied"])
        self.assertIsNotNone(payload["vo_onset_seconds"])
        self.assertTrue(math.isclose(float(payload["vo_onset_seconds"]), 0.5, abs_tol=0.08))
        self.assertTrue(math.isclose(float(payload["global_offset_seconds"]), -0.5, abs_tol=0.08))
        self.assertIn("atrim", payload["filtergraph_suggestion"])
        self.assertGreaterEqual(len(payload["windows"]), 1)
        self.assertTrue(Path(payload["json_path"]).is_file())
        report = Path(payload["report_path"]).read_text(encoding="utf-8")
        self.assertIn("HelixBuilds waveform conform", report)
        self.assertIn("do not auto-run", report)
        self.assertNotIn("DRAFT-VIDEO-01", report)

    def test_xcorr_recovers_half_second_shift(self) -> None:
        video = self.work / "pictured.mp4"
        audio = self.work / "vo.wav"
        write_picture_with_tone(video, seconds=6.0, tone_start=1.0, tone_duration=2.0)
        write_tone_wav(audio, tone_start=0.5, tone_duration=2.0, total_duration=6.0)
        payload = conform_waveforms(video, audio)
        self.assertEqual(payload["method"], "waveform-xcorr")
        self.assertFalse(payload["video_silent"])
        self.assertTrue(math.isclose(float(payload["global_offset_seconds"]), 0.5, abs_tol=0.08))
        self.assertIn("adelay", payload["filtergraph_suggestion"])
        self.assertFalse(payload["remux"]["auto"])

    def test_missing_inputs_raise(self) -> None:
        with self.assertRaises(Exception):
            conform_waveforms(self.work / "nope.mp4", self.work / "nope.wav")


if __name__ == "__main__":
    unittest.main()
