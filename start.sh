#!/usr/bin/env bash
set -euo pipefail

echo "=================================="
echo " Starting InfiniteTalk & Wan2GP   "
echo "=================================="

# Check if port 8000 is open
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "[Error] Port 8000 is already in use. Please free the port and try again."
    exit 1
fi

if [ ! -d .venv ]; then
  echo "=> Creating Python virtual environment..."
  python3 -m venv .venv
fi

echo "=> Activating environment and installing dependencies..."
source .venv/bin/activate
pip install -q -r requirements.txt

echo "=> Creating required directories..."
mkdir -p data/uploads data/cache data/outputs logs

echo "=> Starting backend server..."
exec uvicorn backend.main:app --host 127.0.0.1 --port 8000
