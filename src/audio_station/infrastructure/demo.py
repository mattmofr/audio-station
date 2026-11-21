from collections.abc import Iterator

from audio_station.alarms.alarm import Alarm
from audio_station.audio.playback import MemoryPlayback
from audio_station.core.station import Command, Station, StationState
from audio_station.infrastructure.config import Config

DEMO_TITLES = ("Piste 01", "Piste 02", "Piste 03")


def run_demo(config: Config) -> Iterator[tuple[str, StationState]]:
    alarm = Alarm()
    station = Station(MemoryPlayback(DEMO_TITLES, config.volume), alarm)
    yield "démarrage", station.snapshot()

    for command in (Command.PLAY_PAUSE, Command.NEXT, Command.VOLUME_UP, Command.STANDBY):
        station.handle(command)
        yield command.value, station.snapshot()

    alarm.trigger()
    yield "réveil", station.snapshot()

    for command in (Command.STOP_ALARM, Command.STANDBY, Command.PLAY_PAUSE):
        station.handle(command)
        yield command.value, station.snapshot()
