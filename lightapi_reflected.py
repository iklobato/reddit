"""
LightAPI app using database reflection for the products table.

Requires products table to exist (run sql/seed_products.sql first).
"""

import os
from sqlalchemy import create_engine
from lightapi import LightApi, RestEndpoint

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)


class ProductEndpoint(RestEndpoint):
    """Reflected endpoint - columns come from the products table."""

    class Meta:
        reflect = True
        table = "products"


if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    app = LightApi(engine=engine)
    app.register({"/products": ProductEndpoint})
    app.run(host="0.0.0.0", port=8001)
