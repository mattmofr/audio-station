from dataclasses import dataclass
from enum import StrEnum

from audio_station.alarms.alarm import Alarm
from audio_station.audio.playback import Playback, PlaybackState


class Command(StrEnum):
    PREVIOUS = "previous"
    PLAY_PAUSE = "play_pause"
    NEXT = "next"
    STANDBY = "standby"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    STOP_ALARM = "stop_alarm"


@dataclass(frozen=True)
class StationState:
    playback: PlaybackState
    standby: bool
    alarm_ringing: bool


class Station:
    def __init__(self, playback: Playback, alarm: Alarm) -> None:
        self._playback = playback
        self._alarm = alarm
        self._standby = False

    def snapshot(self) -> StationState:
        return StationState(self._playback.snapshot(), self._standby, self._alarm.ringing)

    def handle(self, command: Command) -> None:
        if command == Command.STOP_ALARM:
            self._alarm.stop()
            return

        if command == Command.STANDBY:
            if not self._standby:
                self._playback.set_playing(False)
            self._standby = not self._standby
            return

        if self._standby:
            return

        match command:
            case Command.PREVIOUS:
                self._playback.skip(-1)
            case Command.PLAY_PAUSE:
                self._playback.set_playing(not self._playback.snapshot().playing)
            case Command.NEXT:
                self._playback.skip(1)
            case Command.VOLUME_UP:
                self._playback.adjust_volume(5)
            case Command.VOLUME_DOWN:
                self._playback.adjust_volume(-5)
