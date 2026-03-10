"""LightAPI application setup — engine, register, run."""

from sqlalchemy import create_engine

from lightapi import LightApi

from myapp.config import DATABASE_URL
from myapp.endpoints import (
    ProductEndpoint,
    ArticleEndpoint,
    NoteEndpoint,
    PublicEndpoint,
    ReadOnlyEndpoint,
)


def create_app():
    """Create and configure the LightApi application."""
    engine = create_engine(DATABASE_URL)
    app = LightApi(engine=engine)
    app.register(
        {
            "/products": ProductEndpoint,
            "/articles": ArticleEndpoint,
            "/notes": NoteEndpoint,
            "/public": PublicEndpoint,
            "/tags": ReadOnlyEndpoint,
        }
    )
    return app


app = create_app()
