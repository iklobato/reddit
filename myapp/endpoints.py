"""REST endpoints with Meta configuration — like a real project."""

from lightapi import (
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


class ProductEndpoint(RestEndpoint):
    """Reflected table — Meta.reflect, Meta.table."""

    class Meta:
        reflect = True
        table = "products"


class ArticleEndpoint(RestEndpoint):
    """Filtering + Pagination — Meta.filtering, Meta.pagination."""

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


class NoteEndpoint(RestEndpoint):
    """Serializer — Meta.serializer restricts response fields."""

    title: str = Field(min_length=1)
    body: str | None = None

    class Meta:
        serializer = Serializer(fields=["id", "title", "created_at", "version"])


class PublicEndpoint(RestEndpoint):
    """Authentication — Meta.authentication with AllowAny."""

    message: str = Field(min_length=1)

    class Meta:
        authentication = Authentication(permission=AllowAny)


class ReadOnlyEndpoint(RestEndpoint, HttpMethod.GET):
    """HttpMethod — only GET allowed."""

    tag: str = Field(min_length=1)

    class Meta:
        table = "tags"
