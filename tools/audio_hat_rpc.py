#!/usr/bin/env python3
"""Contrôle JSON-RPC du seul client local du banc Audio Station S1."""

import argparse
import json
import socket
import time

LOOPBACK = "127.0.0.1"
CONTROL_PORT = 17105
MAX_LINE = 1024 * 1024


class BenchError(RuntimeError):
    """Le profil dédié ou le résultat de la commande est incertain."""


def request(connection, replies, request_id, method, params=None):
    payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        payload["params"] = params
    started = time.monotonic()
    connection.sendall((json.dumps(payload) + "\n").encode("utf-8"))
    for _ in range(16):
        line = replies.readline(MAX_LINE + 1)
        if not line.endswith(b"\n") or len(line) > MAX_LINE:
            raise BenchError("Réponse Snapcast absente ou trop longue.")
        reply = json.loads(line)
        if isinstance(reply, dict) and reply.get("id") == request_id:
            result = reply.get("result")
            if reply.get("jsonrpc") != "2.0" or "error" in reply or not isinstance(result, dict):
                raise BenchError(f"{method} a échoué.")
            return result, round((time.monotonic() - started) * 1000, 2)
    raise BenchError("Aucune réponse corrélée à la commande.")


def bench_status(result, client_id=None):
    server = result["server"]
    connected = [
        (group, client)
        for group in server["groups"]
        for client in group["clients"]
        if client["connected"]
    ]
    if len(connected) != 1:
        raise BenchError("Le banc doit avoir exactement un client connecté.")
    group, client = connected[0]
    if group["stream_id"] != "Music" or client["host"]["ip"] != LOOPBACK:
        raise BenchError("Le seul client doit recevoir Music sur la boucle locale.")
    if client_id is not None and client["id"] != client_id:
        raise BenchError("L’identifiant lu diffère du client S1 indiqué.")
    volume = client["config"]["volume"]
    if type(volume["percent"]) is not int or not 0 <= volume["percent"] <= 100 or type(volume["muted"]) is not bool:
        raise BenchError("Le volume du client renvoyé par Snapcast est invalide.")
    return {
        "client_id": client["id"],
        "stream": group["stream_id"],
        "group_muted": group["muted"],
        "volume": {"percent": volume["percent"], "muted": volume["muted"]},
        "snapserver": server.get("server", {}).get("snapserver", {}).get("version"),
        "snapclient": client.get("snapclient", {}).get("version"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "volume"))
    parser.add_argument("--client-id", help="identifiant exact relevé avec status")
    parser.add_argument("--percent", type=int)
    parser.add_argument("--mute", choices=("on", "off"))
    args = parser.parse_args()

    if args.action == "status" and (args.percent is not None or args.mute is not None):
        parser.error("status est une lecture seule.")
    if args.action == "volume":
        if not args.client_id or (args.percent is None and args.mute is None):
            parser.error("volume exige --client-id et au moins --percent ou --mute.")
        if args.percent is not None and not 0 <= args.percent <= 100:
            parser.error("--percent doit être compris entre 0 et 100.")

    try:
        with socket.create_connection((LOOPBACK, CONTROL_PORT), timeout=2) as connection:
            with connection.makefile("rb") as replies:
                result, rtt = request(connection, replies, 1, "Server.GetStatus")
                status = bench_status(result, args.client_id)
                if args.action == "volume":
                    volume = dict(status["volume"])
                    if args.percent is not None:
                        volume["percent"] = args.percent
                    if args.mute is not None:
                        volume["muted"] = args.mute == "on"
                    request(connection, replies, 2, "Client.SetVolume", {
                        "id": status["client_id"], "volume": volume,
                    })
                    result, rtt = request(connection, replies, 3, "Server.GetStatus")
                    status = bench_status(result, args.client_id)
                    if status["volume"] != volume:
                        raise BenchError("Le volume demandé n’est pas confirmé par le serveur.")
    except (BenchError, OSError) as error:
        parser.exit(1, f"Banc S1 — {error}\n")
    except (ValueError, KeyError, TypeError, AttributeError):
        parser.exit(1, "Banc S1 — état JSON-RPC inattendu. Vérifier la version Snapcast.\n")

    print(json.dumps({**status, "status_rpc_rtt_ms": rtt}, ensure_ascii=False))


if __name__ == "__main__":
    main()
