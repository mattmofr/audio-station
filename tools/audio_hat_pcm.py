#!/usr/bin/env python3
"""Write a deterministic two-second stereo PCM test signal to stdout."""

from __future__ import annotations

import argparse
import math
import struct
import sys


SAMPLE_RATE = 48_000
CHANNELS = 2
SAMPLE_WIDTH = 2
DURATION_SECONDS = 2
FRAME_COUNT = SAMPLE_RATE * DURATION_SECONDS
LEFT_FREQUENCY = 440.0
RIGHT_FREQUENCY = 660.0
DEFAULT_LEVEL_DBFS = -42.0
MIN_LEVEL_DBFS = -120.0
MAX_LEVEL_DBFS = -18.0
RAMP_SAMPLES = 128


def _level(value: str) -> float:
    try:
        level = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("level must be a finite dBFS number") from error
    if not math.isfinite(level) or not MIN_LEVEL_DBFS <= level <= MAX_LEVEL_DBFS:
        raise argparse.ArgumentTypeError(
            f"level must be between {MIN_LEVEL_DBFS:g} and {MAX_LEVEL_DBFS:g} dBFS"
        )
    return level


def _envelope(index: int) -> float:
    if index < RAMP_SAMPLES:
        return index / RAMP_SAMPLES
    remaining = FRAME_COUNT - 1 - index
    if remaining < RAMP_SAMPLES:
        return remaining / RAMP_SAMPLES
    return 1.0


def pcm_bytes(mode: str, level_dbfs: float) -> bytes:
    """Return interleaved S16LE frames for *mode*, without opening a device."""
    peak = 32767.0 * (10.0 ** (level_dbfs / 20.0))
    output = bytearray(FRAME_COUNT * CHANNELS * SAMPLE_WIDTH)
    for index in range(FRAME_COUNT):
        envelope = _envelope(index)
        left = 0
        right = 0
        if mode in {"left", "stereo"}:
            left = round(peak * envelope * math.sin(2.0 * math.pi * LEFT_FREQUENCY * index / SAMPLE_RATE))
        if mode in {"right", "stereo"}:
            right = round(peak * envelope * math.sin(2.0 * math.pi * RIGHT_FREQUENCY * index / SAMPLE_RATE))
        struct.pack_into("<hh", output, index * 4, left, right)
    return bytes(output)


def wav_bytes(pcm: bytes) -> bytes:
    """Prefix PCM with a RIFF/WAVE header that needs no seeking."""
    byte_rate = SAMPLE_RATE * CHANNELS * SAMPLE_WIDTH
    block_align = CHANNELS * SAMPLE_WIDTH
    fmt = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + len(pcm),
        b"WAVE",
        b"fmt ",
        16,
        1,
        CHANNELS,
        SAMPLE_RATE,
        byte_rate,
        block_align,
        SAMPLE_WIDTH * 8,
        b"data",
        len(pcm),
    )
    return fmt + pcm


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("left", "right", "stereo", "silence"))
    parser.add_argument("--level-dbfs", type=_level, default=DEFAULT_LEVEL_DBFS)
    parser.add_argument("--format", choices=("wav", "raw"), default="raw")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    arguments = parse_args(argv)
    pcm = pcm_bytes(arguments.mode, arguments.level_dbfs)
    output = wav_bytes(pcm) if arguments.format == "wav" else pcm
    sys.stdout.buffer.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
