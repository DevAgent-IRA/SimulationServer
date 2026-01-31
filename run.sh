#!/bin/bash
cd "$(dirname "$0")"
source backend/venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
