"""Pytest configuration for calculator app tests."""

import sys
from pathlib import Path

# Ensure the calculator package (app/calculator) is importable when tests run from repo root.
APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
