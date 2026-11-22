from __future__ import annotations

import struct
import subprocess
import sys
import unittest
import wave
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "audio_hat_pcm.py"
SAMPLE_RATE = 48_000
FRAME_COUNT = SAMPLE_RATE * 2
PCM_BYTES = FRAME_COUNT * 4


def run_hat(*arguments: str) -> bytes:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


class AudioHatPcmTests(unittest.TestCase):
    def test_raw_has_expected_duration_and_stereo_frame_order(self) -> None:
        data = run_hat("stereo", "--level-dbfs", "-42", "--format", "raw")
        self.assertEqual(PCM_BYTES, len(data))
        self.assertEqual((0, 0), struct.unpack_from("<hh", data))
        left, right = struct.unpack_from("<hh", data, 500 * 4)
        self.assertNotEqual(0, left)
        self.assertNotEqual(0, right)

    def test_channels_are_isolated_and_silence_is_exact(self) -> None:
        left_data = run_hat("left", "--format", "raw")
        right_data = run_hat("right", "--format", "raw")
        silence = run_hat("silence", "--format", "raw")
        left_frames = struct.iter_unpack("<hh", left_data)
        right_frames = struct.iter_unpack("<hh", right_data)
        self.assertTrue(any(left and not right for left, right in left_frames))
        self.assertTrue(any(right and not left for left, right in right_frames))
        self.assertEqual(b"\0" * PCM_BYTES, silence)

    def test_level_controls_amplitude_and_edges_are_ramped(self) -> None:
        quiet = run_hat("left", "--level-dbfs", "-42", "--format", "raw")
        louder = run_hat("left", "--level-dbfs", "-18", "--format", "raw")
        quiet_peak = max(abs(value) for frame in struct.iter_unpack("<hh", quiet) for value in frame)
        loud_peak = max(abs(value) for frame in struct.iter_unpack("<hh", louder) for value in frame)
        self.assertGreater(loud_peak, quiet_peak * 10)
        self.assertEqual((0, 0), struct.unpack_from("<hh", quiet, 0))
        self.assertEqual((0, 0), struct.unpack_from("<hh", quiet, -4))

    def test_wav_header_is_complete_and_matches_raw_pcm(self) -> None:
        raw = run_hat("stereo", "--format", "raw")
        wav_data = run_hat("stereo", "--format", "wav")
        self.assertEqual(44 + len(raw), len(wav_data))
        with _BytesWave(wav_data) as reader:
            self.assertEqual(2, reader.getnchannels())
            self.assertEqual(2, reader.getsampwidth())
            self.assertEqual(SAMPLE_RATE, reader.getframerate())
            self.assertEqual(FRAME_COUNT, reader.getnframes())
            self.assertEqual(raw, reader.readframes(FRAME_COUNT))

    def test_invalid_modes_levels_and_formats_are_rejected(self) -> None:
        for arguments in (
            ("bad",),
            ("left", "--format", "mp3"),
            ("left", "--level-dbfs", "nan"),
            ("left", "--level-dbfs", "inf"),
            ("left", "--level-dbfs", "-17.99"),
            ("left", "--level-dbfs", "-121"),
        ):
            result = subprocess.run(
                [sys.executable, str(SCRIPT), *arguments],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(0, result.returncode, arguments)


class _BytesWave:
    """Small wave.open-compatible adapter for a non-seekable-output test."""

    def __init__(self, data: bytes) -> None:
        import io

        self._stream = io.BytesIO(data)
        self._reader = wave.open(self._stream, "rb")

    def __enter__(self):
        return self._reader

    def __exit__(self, *exc_info):
        self._reader.close()


if __name__ == "__main__":
    unittest.main()
