#!/usr/bin/env bash
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
VENV_DIR="$REPO_DIR/.venv"
PYTHON="$VENV_DIR/bin/python"

if [ ! -x "$PYTHON" ]; then
    printf '%s\n' "Environnement .venv absent ou inutilisable dans $REPO_DIR." >&2
    printf '%s\n' "Créez-le et installez le projet manuellement avant de relancer la CI locale." >&2
    exit 1
fi

cd "$REPO_DIR"
"$PYTHON" -m pip check
"$PYTHON" -m unittest discover -s tests -v
