#!/bin/bash
# Simple launcher - runs the app directly via Python (for development)
cd "$(dirname "$0")"
source venv/bin/activate
PYTHONPATH=src python3 src/main.py
