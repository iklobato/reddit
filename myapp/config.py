"""Application configuration — database URL from environment."""

import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)
