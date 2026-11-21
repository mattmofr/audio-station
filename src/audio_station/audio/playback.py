from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PlaybackState:
    title: str
    playing: bool
    volume: int


class Playback(Protocol):
    def snapshot(self) -> PlaybackState: ...

    def set_playing(self, playing: bool) -> None: ...

    def skip(self, offset: int) -> None: ...

    def adjust_volume(self, delta: int) -> None: ...


class MemoryPlayback:
    """Simule la lecture et le volume sans périphérique audio."""

    def __init__(self, titles: Sequence[str], volume: int) -> None:
        self._titles = tuple(titles)
        if not self._titles:
            raise ValueError("La liste de pistes simulées est vide.")
        if not 0 <= volume <= 100:
            raise ValueError("Le volume doit être compris entre 0 et 100.")
        self._index = 0
        self._playing = False
        self._volume = volume

    def snapshot(self) -> PlaybackState:
        return PlaybackState(self._titles[self._index], self._playing, self._volume)

    def set_playing(self, playing: bool) -> None:
        self._playing = playing

    def skip(self, offset: int) -> None:
        self._index = (self._index + offset) % len(self._titles)

    def adjust_volume(self, delta: int) -> None:
        self._volume = max(0, min(100, self._volume + delta))
