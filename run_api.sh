#!/data/data/com.termux/files/usr/bin/bash
cd ~/veritas_cordovaos || exit 1
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
