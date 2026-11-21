import argparse
from pathlib import Path
from typing import Sequence

from audio_station.infra.config import Config, ConfigError, load_config
from audio_station.infra.demo import run_demo
from audio_station.ui.display import render_demo, status_text


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audio Station")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="jouer le scénario simulé hors ligne")
    demo.add_argument("--config", type=Path, help="charger une configuration TOML DEMO")
    demo.add_argument("--output", type=Path, help="enregistrer la dernière image au format PNG")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config) if args.config is not None else Config()
    except ConfigError as error:
        demo.error(str(error))

    print("DEMO — Audio Station")
    for event, state in run_demo(config):
        print(f"{event:<12} | {status_text(state):<15} | {state.playback.title} | {state.playback.volume} %")
    if args.output is not None:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            render_demo(state).save(args.output, format="PNG")
        except OSError as error:
            demo.error(f"Impossible d’écrire {args.output} — {error}")
        print(f"Image PNG enregistrée dans {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
