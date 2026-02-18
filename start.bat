@echo off
setlocal enabledelayedexpansion

if not exist .venv (
  py -m venv .venv
)

call .venv\Scripts\activate
pip install -q -r requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000
