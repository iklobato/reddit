"""
LightAPI test application showcasing Meta features.

Endpoints:
- /products: reflected table (reflect, table)
- /articles: filtering, pagination
- /items: serializer
- /protected: authentication (AllowAny for testing)
"""

import os
from sqlalchemy import create_engine
from lightapi import (
    LightApi,
    RestEndpoint,
    Field,
    Filtering,
    Pagination,
    Serializer,
    Authentication,
    AllowAny,
)
from lightapi.filters import FieldFilter, SearchFilter, OrderingFilter
from lightapi.methods import HttpMethod

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)


class ProductEndpoint(RestEndpoint):
    """Reflected endpoint - Meta.reflect, Meta.table."""

    class Meta:
        reflect = True
        table = "products"


class ArticleEndpoint(RestEndpoint):
    """Filtering + Pagination - Meta.filtering, Meta.pagination."""

    title: str = Field(min_length=1)
    category: str = Field(min_length=1)
    author: str = Field(min_length=1)
    published: bool = Field(default=True)

    class Meta:
        filtering = Filtering(
            backends=[FieldFilter, SearchFilter, OrderingFilter],
            fields=["category", "published"],
            search=["title", "author"],
            ordering=["title", "author", "created_at"],
        )
        pagination = Pagination(style="page_number", page_size=2)


class ItemEndpoint(RestEndpoint):
    """Serializer - Meta.serializer restricts response fields."""

    name: str = Field(min_length=1)
    description: str | None = None
    secret_code: str = Field(min_length=1)

    class Meta:
        serializer = Serializer(
            read=["id", "name", "created_at", "version"],
            write=["id", "name"],
        )


class ProtectedEndpoint(RestEndpoint):
    """Authentication - Meta.authentication with AllowAny for open access."""

    data: str = Field(min_length=1)

    class Meta:
        authentication = Authentication(permission=AllowAny)


class ReadOnlyEndpoint(RestEndpoint, HttpMethod.GET):
    """HttpMethod.GET: only GET allowed, no POST/PUT/PATCH/DELETE."""

    label: str = Field(min_length=1)


def create_app():
    """Create and configure the LightApi application."""
    engine = create_engine(DATABASE_URL)
    api = LightApi(engine=engine)
    api.register(
        {
            "/products": ProductEndpoint,
            "/articles": ArticleEndpoint,
            "/items": ItemEndpoint,
            "/protected": ProtectedEndpoint,
            "/readonly": ReadOnlyEndpoint,
        }
    )
    return api


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
