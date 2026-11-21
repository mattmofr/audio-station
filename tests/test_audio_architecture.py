"""Static guard for the S0 audio-output boundary.

The Python providers may produce PCM or keep playback state in memory.  They
must not open the sound device themselves: the external snapclient owns that
boundary.  This is intentionally a small AST guard, not a Python sandbox or a
complete data-flow analyser.
"""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src" / "audio_station"

_DIRECT_OUTPUT_MODULES = {
    "alsaaudio",
    "pyaudio",
    "pyalsa",
    "sounddevice",
    "soundcard",
}
_PLAYER_COMMANDS = {
    "aplay",
    "alsaplayer",
    "speaker-test",
}
_PROCESS_CALLS = {
    "call",
    "check_call",
    "check_output",
    "Popen",
    "run",
    "system",
}
_DEVICE_LITERAL = re.compile(r"(?:^|[\s=/'\"])(?:hw|plughw):")


class _AlsaOutputVisitor(ast.NodeVisitor):
    """Find explicit Python-to-ALSA/device output attempts.

    The visitor deliberately reports only syntactic evidence.  It does not
    reject ``subprocess`` or ``os`` in general, since supervising snapclient
    and feeding a PCM pipe are part of the permitted architecture.
    """

    def __init__(self) -> None:
        self.violations: list[tuple[int, str]] = []
        self._direct_modules: set[str] = set()
        self._direct_symbols: set[str] = set()
        self._process_aliases: dict[str, str] = {}

    def _report(self, node: ast.AST, message: str) -> None:
        self.violations.append((getattr(node, "lineno", 0), message))

    @staticmethod
    def _module_name(node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parent = _AlsaOutputVisitor._module_name(node.value)
            return f"{parent}.{node.attr}" if parent else node.attr
        return None

    @staticmethod
    def _strings(node: ast.AST) -> list[str]:
        """Collect literals in this call's containers, not nested calls."""
        values: list[str] = []

        def collect(current: ast.AST) -> None:
            if isinstance(current, ast.Call) and current is not node:
                return
            if isinstance(current, ast.Constant) and isinstance(current.value, str):
                values.append(current.value)
            for child in ast.iter_child_nodes(current):
                collect(child)

        collect(node)
        return values

    @staticmethod
    def _first_command(node: ast.AST) -> str | None:
        """Return the executable represented by a literal process argument."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            command = node.value.strip().split(None, 1)[0] if node.value.strip() else None
            return command.rsplit("/", 1)[-1] if command else None
        if isinstance(node, (ast.List, ast.Tuple)) and node.elts:
            first = node.elts[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                return first.value.rsplit("/", 1)[-1]
        return None

    @staticmethod
    def _process_argument(node: ast.Call) -> ast.AST | None:
        if node.args:
            return node.args[0]
        for keyword in node.keywords:
            if keyword.arg == "args":
                return keyword.value
        return None

    @staticmethod
    def _snapclient_device_indexes(arguments: list[str]) -> set[int]:
        allowed: set[int] = set()
        for index, argument in enumerate(arguments[:-1]):
            if argument == "--soundcard":
                allowed.add(index + 1)
        return allowed

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".", 1)[0]
            if root in _DIRECT_OUTPUT_MODULES:
                self._direct_modules.add(alias.asname or root)
                self._report(node, f"import direct-output binding: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        root = (node.module or "").split(".", 1)[0]
        if root in _DIRECT_OUTPUT_MODULES:
            for alias in node.names:
                name = alias.asname or alias.name
                self._direct_symbols.add(name)
            self._report(node, f"from-import direct-output binding: {node.module}")
        if root in {"os", "subprocess"}:
            self._process_aliases.update(
                (alias.asname, alias.name) for alias in node.names if alias.asname
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        callee = self._module_name(node.func)
        if callee:
            root = callee.split(".", 1)[0]
            member = self._process_aliases.get(callee, callee.rsplit(".", 1)[-1])
            if root in self._direct_modules or callee in self._direct_symbols or member in self._direct_symbols:
                self._report(node, f"direct-output binding executed: {callee}")

            if member in {"CDLL", "LoadLibrary", "dlopen"}:
                if any("libasound" in text.lower() for text in self._strings(node)):
                    self._report(node, "libasound loaded through ctypes/dlopen")

            if member in _PROCESS_CALLS or member.startswith("exec") or member.startswith("spawn"):
                process_argument = self._process_argument(node)
                command = self._first_command(process_argument) if process_argument else None
                process_strings = self._strings(process_argument) if process_argument else []
                if isinstance(process_argument, ast.Constant) and process_strings:
                    process_strings = process_strings[0].split()
                is_ffmpeg_alsa = (
                    command == "ffmpeg"
                    and "-f" in process_strings
                    and any(value == "alsa" for value in process_strings)
                )
                if command in _PLAYER_COMMANDS or is_ffmpeg_alsa:
                    self._report(node, f"direct ALSA player launched: {command}")

        literals = self._strings(node)
        if callee and self._process_aliases.get(callee, callee.rsplit(".", 1)[-1]) in _PROCESS_CALLS:
            process_argument = self._process_argument(node)
            command = self._first_command(process_argument) if process_argument else None
            if command == "snapclient":
                process_literals = self._strings(process_argument) if process_argument else []
                allowed = self._snapclient_device_indexes(process_literals)
                literals = [
                    text for index, text in enumerate(process_literals) if index not in allowed
                ]
        for text in literals:
            if "/dev/snd" in text or _DEVICE_LITERAL.search(text):
                self._report(node, "explicit ALSA device path/target")
        self.generic_visit(node)


def _find_violations(source: str, filename: str = "<snippet>") -> list[str]:
    visitor = _AlsaOutputVisitor()
    visitor.visit(ast.parse(source, filename=filename))
    return [f"{filename}:{line}: {message}" for line, message in visitor.violations]


class AudioArchitectureTests(unittest.TestCase):
    def test_python_audio_station_has_no_direct_alsa_output(self) -> None:
        paths = sorted(SOURCE_ROOT.rglob("*.py"))
        self.assertTrue(paths, f"No Python sources under {SOURCE_ROOT}")
        violations: list[str] = []
        for path in paths:
            violations.extend(_find_violations(path.read_text(encoding="utf-8"), str(path)))
        self.assertEqual([], violations, "\n".join(violations))

    def test_rejects_qualified_alsa_binding_execution(self) -> None:
        source = "import alsaaudio as alsa\nalsa.PCM(type=alsa.PCM_PLAYBACK)\n"
        violations = _find_violations(source)
        self.assertTrue(any("binding executed" in item for item in violations), violations)

    def test_rejects_from_import_alsa_binding(self) -> None:
        violations = _find_violations("from sounddevice import OutputStream\nOutputStream()\n")
        self.assertTrue(violations, "a qualified/direct-output binding must be rejected")

    def test_rejects_aplay_and_explicit_device_target(self) -> None:
        source = "import subprocess\nsubprocess.run(['aplay', '-D', 'hw:0,0', 'tone.wav'])\n"
        violations = _find_violations(source)
        self.assertTrue(any("aplay" in item for item in violations), violations)
        self.assertTrue(any("device" in item for item in violations), violations)

    def test_rejects_explicit_alsa_ffmpeg_launcher(self) -> None:
        cases = (
            "import subprocess\nsubprocess.run(['ffmpeg', '-f', 'alsa', 'default'])",
            "from subprocess import run as launch\nlaunch(['ffmpeg', '-f', 'alsa', 'default'])",
            "import os\nos.system('ffmpeg -f alsa default')",
        )
        for source in cases:
            with self.subTest(source=source):
                violations = _find_violations(source)
                self.assertTrue(any("ffmpeg" in item for item in violations), violations)

    def test_rejects_aplay_system_launcher_and_keyword_popen(self) -> None:
        source = """
import os
import subprocess as sp
os.system('/usr/bin/aplay tone.wav')
sp.Popen(args=['aplay', 'tone.wav'])
"""
        violations = _find_violations(source)
        self.assertGreaterEqual(len([item for item in violations if "player" in item]), 2, violations)

    def test_rejects_ctypes_libasound(self) -> None:
        source = "import ctypes\nctypes.CDLL('libasound.so.2')\n"
        violations = _find_violations(source)
        self.assertTrue(any("libasound" in item for item in violations), violations)

    def test_rejects_opening_sound_device(self) -> None:
        violations = _find_violations("open('/dev/snd/pcmC0D0p', 'wb')\n")
        self.assertTrue(violations, "opening /dev/snd must be rejected")

    def test_ignores_comments(self) -> None:
        source = "# aplay hw:0,0 /dev/snd/libasound.so\nvalue = 'ordinary PCM'\n"
        self.assertEqual([], _find_violations(source))

    def test_allows_pcm_pipe_and_external_snapclient(self) -> None:
        source = """
import io
import subprocess

pcm = io.BytesIO()
client = subprocess.Popen(
    ['snapclient', '--host', '127.0.0.1'], stdin=subprocess.PIPE
)
"""
        self.assertEqual([], _find_violations(source))

    def test_allows_snapclient_soundcard_target_only(self) -> None:
        source = """
import subprocess
subprocess.Popen([
    'snapclient', '--player', 'alsa',
    '--soundcard', 'hw:CARD=MiniAmp,DEV=0',
], stdin=subprocess.PIPE)
"""
        self.assertEqual([], _find_violations(source))

    def test_does_not_allow_alsa_target_in_unrelated_snapclient_argument(self) -> None:
        source = "subprocess.Popen(['snapclient', '--name', 'hw:CARD=MiniAmp'])\n"
        violations = _find_violations(source)
        self.assertTrue(any("device" in item for item in violations), violations)


if __name__ == "__main__":
    unittest.main()
