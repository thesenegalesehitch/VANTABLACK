#!/usr/bin/env bash
set -e
echo "[v5] Creating virtual environment (.venv)"
python3 -m venv .venv
source .venv/bin/activate
echo "[v5] Upgrading pip"
python -m pip install -U pip
echo "[v5] Installing requirements"
python -m pip install -r requirements-v5.txt
echo "[v5] Running doctor"
python -m core.cli.main doctor || true
echo "[v5] Launching demo server"
python -m core.cli.main demo
