import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

DEMO_WITH_IO_GUARD = """
import os
import runpy
import sys


def forbid_io(event, args):
    if event.startswith("socket.") or event in {
        "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.fork",
    }:
        raise AssertionError(f"Unexpected external I/O: {event}")
    if event == "open" and isinstance(args[0], (str, bytes)):
        path = os.path.realpath(os.fsdecode(args[0]))
        if path.startswith(("/dev/", "/sys/class/gpio/", "/sys/devices/platform/")):
            raise AssertionError(f"Unexpected device I/O: {path}")


sys.addaudithook(forbid_io)
runpy.run_module("audio_station", run_name="__main__", alter_sys=True)
"""


class DemoTests(unittest.TestCase):
    def test_headless_demo_under_io_guard_writes_an_rgb_png(self):
        with TemporaryDirectory() as directory:
            destination = Path(directory) / "preview" / "frame.png"
            config = Path(directory) / "demo.toml"
            config.write_text("[playback]\nvolume = 60\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable, "-c", DEMO_WITH_IO_GUARD, "demo",
                    "--config", str(config), "--output", str(destination),
                ],
                cwd=directory,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Réveil en cours", result.stdout)
            self.assertRegex(result.stdout, r"stop_alarm\s+\| Veille")
            self.assertRegex(result.stdout, r"play_pause\s+\| Lecture\s+\| Piste 02 \| 65 %")
            with Image.open(destination) as frame:
                self.assertEqual(frame.format, "PNG")
                self.assertEqual(frame.mode, "RGB")
                self.assertEqual(frame.size, (320, 240))
                frame.load()

    def test_invalid_config_does_not_write_output(self):
        with TemporaryDirectory() as directory:
            destination = Path(directory) / "unexpected.png"
            result = subprocess.run(
                [
                    sys.executable, "-m", "audio_station", "demo",
                    "--config", str(Path(directory) / "missing.toml"),
                    "--output", str(destination),
                ],
                cwd=directory,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("missing.toml", result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertFalse(destination.exists())
