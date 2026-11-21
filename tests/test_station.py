import unittest

from audio_station.alarms.alarm import Alarm
from audio_station.audio.playback import MemoryPlayback
from audio_station.core.station import Command, Station


class StationTests(unittest.TestCase):
    def setUp(self):
        self.alarm = Alarm()
        self.station = Station(MemoryPlayback(("Une", "Deux"), 35), self.alarm)

    def test_transport_wraps_and_pause_keeps_the_selected_track(self):
        before = self.station.snapshot()
        self.station.handle(Command.PREVIOUS)
        self.assertEqual(self.station.snapshot().playback.title, "Deux")

        self.station.handle(Command.PLAY_PAUSE)
        self.station.handle(Command.NEXT)
        self.assertTrue(self.station.snapshot().playback.playing)
        self.station.handle(Command.PLAY_PAUSE)

        after = self.station.snapshot()
        self.assertEqual(after.playback.title, "Une")
        self.assertFalse(after.playback.playing)
        self.assertEqual(before.playback.title, "Une")

    def test_volume_is_bounded(self):
        for _ in range(21):
            self.station.handle(Command.VOLUME_UP)
        self.assertEqual(self.station.snapshot().playback.volume, 100)
        for _ in range(21):
            self.station.handle(Command.VOLUME_DOWN)
        self.assertEqual(self.station.snapshot().playback.volume, 0)

    def test_alarm_can_be_stopped_in_standby_without_resuming_playback(self):
        self.station.handle(Command.PLAY_PAUSE)
        self.station.handle(Command.STANDBY)
        self.station.handle(Command.PLAY_PAUSE)
        self.station.handle(Command.NEXT)
        self.alarm.trigger()
        ringing = self.station.snapshot()
        self.assertTrue(ringing.standby)
        self.assertFalse(ringing.playback.playing)
        self.assertEqual(ringing.playback.title, "Une")
        self.assertTrue(ringing.alarm_ringing)

        self.station.handle(Command.STOP_ALARM)
        self.station.handle(Command.STOP_ALARM)
        dismissed = self.station.snapshot()
        self.assertFalse(dismissed.alarm_ringing)
        self.assertTrue(dismissed.standby)

        self.station.handle(Command.STANDBY)
        awake = self.station.snapshot()
        self.assertFalse(awake.standby)
        self.assertFalse(awake.playback.playing)
