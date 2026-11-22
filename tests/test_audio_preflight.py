import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "audio_preflight.sh"


class AudioPreflightTests(unittest.TestCase):
    def test_fixture_is_observational_and_redacts_config_and_addresses(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            (fixture / "proc/device-tree").mkdir(parents=True)
            (fixture / "proc/asound").mkdir(parents=True)
            (fixture / "etc").mkdir()
            (fixture / "boot/firmware").mkdir(parents=True)
            (fixture / "dev/snd").mkdir(parents=True)
            (fixture / "proc/device-tree/model").write_bytes(b"Raspberry Pi 3 Model B\0")
            (fixture / "proc/cpuinfo").write_text("Model\t: fallback\n", encoding="utf-8")
            (fixture / "proc/asound/cards").write_text(" 0 [MiniAmp ]: HifiBerry MiniAmp\n", encoding="utf-8")
            (fixture / "etc/os-release").write_text('PRETTY_NAME="Fixture OS"\nID=fixture\n', encoding="utf-8")
            (fixture / "boot/firmware/config.txt").write_text(
                "# dtoverlay=hifiberry-dac\n"
                "dtoverlay=vc4-kms-v3d,argument=fixture-only.invalid # must-not-appear\n"
                "SECRET=must-not-appear\n",
                encoding="utf-8",
            )

            bin_dir = fixture / "bin"
            bin_dir.mkdir()
            commands = {
                "aplay": "#!/bin/sh\nprintf '%s\\n' 'card 0: MiniAmp'\n",
                "fuser": "#!/bin/sh\nprintf '%s\\n' 'fixture fuser output'\n",
                "snapserver": "#!/bin/sh\nprintf '%s\\n' 'Snapserver 0.1 fixture'\n",
                "snapclient": "#!/bin/sh\nprintf '%s\\n' 'Snapclient 0.1 fixture'\n",
                "vcgencmd": "#!/bin/sh\nprintf '%s\\n' 'throttled=0x0'\n",
                "ps": "#!/bin/sh\nprintf '%s\\n' ' 12 snapclient 1.0 2.0 3000'\n",
                "ss": (
                    "#!/bin/sh\nprintf '%s\\n' 'LISTEN 0 5 fixture-only.invalid:17104 *:*' "
                    "'LISTEN 0 5 127.0.0.1:17105 *:*'\n"
                ),
                "uname": "#!/bin/sh\nprintf '%s\\n' 'Linux fixture 6.1 armv7l'\n",
            }
            for name, content in commands.items():
                path = bin_dir / name
                path.write_text(content, encoding="utf-8")
                path.chmod(path.stat().st_mode | stat.S_IXUSR)

            env = dict(
                os.environ,
                AUDIO_PREFLIGHT_ROOT=str(fixture),
                PATH=f"{bin_dir}:/usr/bin:/bin",
            )
            result = subprocess.run(
                [str(SCRIPT)], cwd=ROOT, env=env, text=True,
                capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("qualification=NON_TESTE", result.stdout)
            self.assertIn("model=Raspberry Pi 3 Model B", result.stdout)
            self.assertIn("candidate=# dtoverlay=hifiberry-dac", result.stdout)
            self.assertIn("candidate=dtoverlay=vc4-kms-v3d", result.stdout)
            self.assertIn("Snapserver 0.1 fixture", result.stdout)
            self.assertIn("port=17104 scope=autre", result.stdout)
            self.assertIn("port=17105 scope=boucle-ipv4", result.stdout)
            self.assertNotIn("must-not-appear", result.stdout)
            self.assertNotIn("fixture-only.invalid", result.stdout)

    def test_script_is_executable(self) -> None:
        self.assertTrue(SCRIPT.stat().st_mode & stat.S_IXUSR)
