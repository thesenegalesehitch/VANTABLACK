#!/bin/bash
# Vantablack CLI Launcher
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "$DIR/venv/bin/activate"
export PYTHONPATH="$DIR:$PYTHONPATH"
python3 -m core.cli.main "$@"
