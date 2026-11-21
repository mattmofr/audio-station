import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from audio_station.infra.config import Config, ConfigError, load_config


class ConfigTests(unittest.TestCase):
    def test_original_config_import_remains_compatible(self):
        from audio_station.infrastructure import config

        self.assertIs(config.Config, Config)
        self.assertIs(config.ConfigError, ConfigError)
        self.assertIs(config.load_config, load_config)

    def load_text(self, content: str) -> Config:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "test.toml"
            path.write_text(content, encoding="utf-8")
            return load_config(path)

    def test_empty_configuration_uses_demo_defaults(self):
        self.assertEqual(self.load_text(""), Config())

    def test_valid_pins_and_volume_are_retained_and_pins_are_immutable(self):
        config = self.load_text("[playback]\nvolume = 42\n[hardware.control_pins]\nprevious = 5")
        self.assertEqual(config.volume, 42)
        self.assertEqual(config.control_pins, {"previous": 5})
        with self.assertRaises(TypeError):
            config.control_pins["previous"] = 18

    def test_miniamp_pins_are_reserved(self):
        for pin in (16, 18, 19, 20, 21, 26):
            with self.subTest(pin=pin):
                with self.assertRaisesRegex(ConfigError, rf"GPIO{pin}.*MiniAmp"):
                    self.load_text(f"[hardware.control_pins]\nnext = {pin}")

    def test_spi0_pins_are_reserved(self):
        for pin in (7, 8, 9, 10, 11):
            with self.subTest(pin=pin):
                with self.assertRaisesRegex(ConfigError, rf"GPIO{pin}.*SPI0"):
                    self.load_text(f"[hardware.control_pins]\nnext = {pin}")

    def test_duplicate_pins_are_rejected(self):
        with self.assertRaisesRegex(ConfigError, "partagent GPIO5"):
            self.load_text("[hardware.control_pins]\nprevious = 5\nnext = 5")

    def test_invalid_values_and_unknown_options_are_rejected(self):
        samples = (
            "[playback]\nvolume = true",
            "[playback]\nvolume = 101",
            "[playback]\nvolum = 42",
            "[hardware]\nenabled = true",
            "[hardware.control_pins]\nnext = true",
            "[hardware.control_pins]\nnext = 28",
            "[hardware.control_pins]\nnext = 1",
            "[hardware]\ncontrol_pins = 5",
            "[hardware",
        )
        for sample in samples:
            with self.subTest(sample=sample):
                with self.assertRaises(ConfigError):
                    self.load_text(sample)
