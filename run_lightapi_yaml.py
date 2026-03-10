#!/usr/bin/env python3
"""
Run LightAPI from YAML configuration.

Uses the same PostgreSQL database as the rest of the project.
No Python endpoint classes — everything is defined in lightapi.yaml.

Run: uv run python run_lightapi_yaml.py

Requires: PostgreSQL (container 'psql') with default credentials.
Set DATABASE_URL or it defaults to postgresql://postgres:postgres@localhost:5432/postgres
"""

import os
import subprocess
from pathlib import Path

# Default database URL (same as myapp)
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)

from lightapi import LightApi

_CONFIG = Path(__file__).resolve().parent / "lightapi.yaml"

if __name__ == "__main__":
    app = LightApi.from_config(str(_CONFIG))
    app.run(host="0.0.0.0", port=8003)
