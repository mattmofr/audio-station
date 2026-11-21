import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

from audio_station.hardware.pins import validate_control_pins


class ConfigError(ValueError):
    """Configuration TOML absente, illisible ou invalide."""


@dataclass(frozen=True)
class Config:
    volume: int = 35
    control_pins: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if type(self.volume) is not int or not 0 <= self.volume <= 100:
            raise ValueError("playback.volume doit être un entier de 0 à 100.")
        pins = validate_control_pins(self.control_pins)
        object.__setattr__(self, "control_pins", MappingProxyType(pins))


def load_config(path: Path) -> Config:
    try:
        with path.open("rb") as stream:
            data = tomllib.load(stream)
        _check_keys(data, {"playback", "hardware"}, "configuration")
        playback = _table(data, "playback")
        hardware = _table(data, "hardware")
        _check_keys(playback, {"volume"}, "playback")
        _check_keys(hardware, {"control_pins"}, "hardware")

        return Config(playback.get("volume", Config.volume), _table(hardware, "control_pins"))
    except (OSError, ValueError) as error:
        raise ConfigError(f"{path} — {error}") from error


def _table(data: dict, key: str) -> dict:
    table = data.get(key, {})
    if not isinstance(table, dict):
        raise ValueError(f"{key} doit être une table TOML.")
    return table


def _check_keys(data: dict, allowed: set[str], table: str) -> None:
    unknown = sorted(data.keys() - allowed)
    if unknown:
        raise ValueError(f"Clés inconnues dans {table} ({', '.join(unknown)}).")
