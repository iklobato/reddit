"""
Simple LightAPI app for a dockerized local PostgreSQL.

Default Docker PostgreSQL credentials: postgres/postgres@localhost:5432/postgres
Override via DATABASE_URL env var.
"""

import os
from sqlalchemy import create_engine
from lightapi import LightApi, RestEndpoint, Field

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)


class ItemEndpoint(RestEndpoint):
    """Simple CRUD endpoint for items."""

    name: str = Field(min_length=1)
    description: str | None = None


if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    app = LightApi(engine=engine)
    app.register({"/items": ItemEndpoint})
    app.run(host="0.0.0.0", port=8000)
