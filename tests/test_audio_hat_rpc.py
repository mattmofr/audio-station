import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

from tools.audio_hat_rpc import BenchError, bench_status, main, request


class RecordingConnection:
    def sendall(self, data):
        self.sent = data


def status_fixture(ip="127.0.0.1", stream="Music"):
    return {
        "server": {
            "groups": [{
                "stream_id": stream,
                "muted": False,
                "clients": [{
                    "id": "audio-station-s1",
                    "connected": True,
                    "host": {"ip": ip},
                    "config": {"volume": {"percent": 5, "muted": True}},
                }],
            }],
        },
    }


class AudioHatRpcTests(unittest.TestCase):
    def test_volume_cli_preserves_percent_and_confirms_mute_change(self):
        before = status_fixture()
        after = status_fixture()
        after["server"]["groups"][0]["clients"][0]["config"]["volume"]["muted"] = False
        messages = (
            {"jsonrpc": "2.0", "id": 1, "result": before},
            {"jsonrpc": "2.0", "id": 2, "result": {"volume": {"percent": 5, "muted": False}}},
            {"jsonrpc": "2.0", "id": 3, "result": after},
        )
        replies = io.BytesIO(("\n".join(json.dumps(message) for message in messages) + "\n").encode())
        connection = MagicMock()
        connection.__enter__.return_value = connection
        connection.makefile.return_value = replies
        argv = ["audio_hat_rpc.py", "volume", "--client-id", "audio-station-s1", "--mute", "off"]
        output = io.StringIO()
        with (
            patch("tools.audio_hat_rpc.socket.create_connection", return_value=connection) as connect,
            patch("sys.argv", argv),
            redirect_stdout(output),
        ):
            main()
        connect.assert_called_once_with(("127.0.0.1", 17105), timeout=2)
        sent = [json.loads(call.args[0]) for call in connection.sendall.call_args_list]
        self.assertEqual([message["method"] for message in sent], [
            "Server.GetStatus", "Client.SetVolume", "Server.GetStatus",
        ])
        self.assertEqual(sent[1]["params"], {
            "id": "audio-station-s1", "volume": {"percent": 5, "muted": False},
        })
        self.assertEqual(json.loads(output.getvalue())["volume"], {"percent": 5, "muted": False})

    def test_reads_the_matching_response_after_a_notification(self):
        connection = RecordingConnection()
        replies = io.BytesIO(
            b'{"jsonrpc":"2.0","method":"Client.OnConnect"}\n'
            b'{"jsonrpc":"2.0","id":3,"result":{"volume":{"percent":5,"muted":false}}}\n'
        )
        result, _ = request(connection, replies, 3, "Client.SetVolume", {
            "id": "audio-station-s1", "volume": {"percent": 5, "muted": False},
        })
        self.assertEqual(result["volume"], {"percent": 5, "muted": False})
        self.assertTrue(connection.sent.endswith(b"\n"))
        self.assertEqual(json.loads(connection.sent)["id"], 3)

    def test_rejects_incomplete_response(self):
        with self.assertRaises(BenchError):
            request(RecordingConnection(), io.BytesIO(b'{"id":3}'), 3, "Server.GetStatus")

    def test_only_the_named_local_client_on_music_is_accepted(self):
        fixture = status_fixture()
        self.assertEqual(bench_status(fixture, "audio-station-s1")["volume"]["percent"], 5)
        for other, client_id in (
            (status_fixture("::1"), "audio-station-s1"),
            (status_fixture(stream="Alarm"), "audio-station-s1"),
            (fixture, "other-client"),
        ):
            with self.subTest(client_id=client_id, stream=other["server"]["groups"][0]["stream_id"]):
                with self.assertRaises(BenchError):
                    bench_status(other, client_id)

    def test_refuses_when_a_second_connected_client_is_present(self):
        fixture = status_fixture()
        clients = fixture["server"]["groups"][0]["clients"]
        clients.append({**clients[0], "id": "other-client"})
        with self.assertRaises(BenchError):
            bench_status(fixture)
