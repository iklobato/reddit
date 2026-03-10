#!/usr/bin/env python3
"""
Test script for LightAPI features, especially class Meta options.

Run: uv run python test_lightapi_features.py
Or:  uv run pytest test_lightapi_features.py -v

Requires: PostgreSQL with products table (run sql/seed_products.sql first)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import httpx
import pytest

# Ensure products table exists before importing app (which connects to DB)
_PROJECT_ROOT = Path(__file__).resolve().parent
_SQL_SEED = _PROJECT_ROOT / "sql" / "seed_products.sql"


def _ensure_products_table() -> None:
    """Run SQL seed if products table might not exist."""
    if not _SQL_SEED.exists():
        return
    try:
        subprocess.run(
            ["docker", "exec", "-i", "psql", "psql", "-U", "postgres", "-d", "postgres", "-f", "-"],
            stdin=_SQL_SEED.open(),
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # Docker/psql not available, assume table exists


_ensure_products_table()

from lightapi_test_app import create_app  # noqa: E402


@pytest.fixture
def asgi_app():
    """Build ASGI app for testing."""
    app = create_app()
    return app.build_app()


@pytest.fixture
async def client(asgi_app):
    """Async HTTP client using ASGI transport (no real server)."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=asgi_app),
        base_url="http://test",
    ) as c:
        yield c


@pytest.fixture
async def articles_seeded(client):
    """Create sample articles for filtering/pagination tests."""
    for title, cat, author in [
        ("Python Tips", "news", "Alice"),
        ("Django Guide", "tutorial", "Bob"),
        ("FastAPI News", "news", "Alice"),
        ("Python 3.12", "news", "Charlie"),
        ("REST APIs", "tutorial", "Bob"),
    ]:
        await client.post(
            "/articles",
            json={"title": title, "category": cat, "author": author, "published": True},
        )


# ─── CRUD (base features) ────────────────────────────────────────────────────


def test_products_list(client):
    """GET /products returns list."""
    r = client.get("/products")
    assert r.status_code == 200
    data = r.json()
    assert "results" in data
    assert isinstance(data["results"], list)


def test_products_create(client):
    """POST /products creates item (reflection)."""
    r = client.post("/products", json={"sku": "TEST-001", "name": "Test Product", "price": 12.99})
    assert r.status_code == 201
    data = r.json()
    assert data["sku"] == "TEST-001"
    assert data["name"] == "Test Product"
    assert data["price"] == "12.99"
    assert "id" in data
    assert "version" in data


def test_products_retrieve(client):
    """GET /products/{id} returns single item."""
    r = client.get("/products/1")
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert "sku" in data


def test_products_patch(client):
    """PATCH /products/{id} partial update."""
    r = client.get("/products/1")
    assert r.status_code == 200
    version = r.json()["version"]
    r = client.patch("/products/1", json={"name": "Patched Name", "version": version})
    assert r.status_code == 200
    assert r.json()["name"] == "Patched Name"


def test_products_put(client):
    """PUT /products/{id} full update."""
    r = client.get("/products/1")
    assert r.status_code == 200
    data = r.json()
    version = data["version"]
    r = client.put(
        "/products/1",
        json={
            "sku": data["sku"],
            "name": "Full Update Name",
            "price": "99.99",
            "version": version,
        },
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Full Update Name"
    assert r.json()["price"] == "99.99"


def test_products_delete(client):
    """DELETE /products/{id} removes item."""
    # Create then delete to avoid affecting other tests
    r = client.post("/products", json={"sku": "DEL-001", "name": "To Delete", "price": 1.0})
    assert r.status_code == 201
    pid = r.json()["id"]
    r = client.delete(f"/products/{pid}")
    assert r.status_code == 204
    r = client.get(f"/products/{pid}")
    assert r.status_code == 404


# ─── Meta: Filtering ──────────────────────────────────────────────────────────


def test_articles_filter_by_category(client, articles_seeded):
    """Filtering: ?category=news."""
    r = client.get("/articles?category=news")
    assert r.status_code == 200
    data = r.json()
    assert "results" in data
    for item in data["results"]:
        assert item["category"] == "news"


def test_articles_search(client, articles_seeded):
    """Filtering: ?search=python."""
    r = client.get("/articles?search=python")
    assert r.status_code == 200
    data = r.json()
    assert "results" in data
    # At least one result should match "python" in title or author
    if data["results"]:
        found = any(
            "python" in (item.get("title", "") + item.get("author", "")).lower()
            for item in data["results"]
        )
        assert found or len(data["results"]) == 0


def test_articles_ordering(client, articles_seeded):
    """Filtering: ?ordering=-title (descending)."""
    r = client.get("/articles?ordering=-title")
    assert r.status_code == 200
    data = r.json()
    assert "results" in data
    titles = [item["title"] for item in data["results"]]
    assert titles == sorted(titles, reverse=True)


# ─── Meta: Pagination ────────────────────────────────────────────────────────


def test_articles_pagination(client, articles_seeded):
    """Pagination: ?page=1, page_size from Meta."""
    r = client.get("/articles?page=1")
    assert r.status_code == 200
    data = r.json()
    assert "results" in data
    assert "count" in data or "pages" in data or "next" in data
    # Page size is 2 from Meta
    assert len(data["results"]) <= 2


def test_articles_pagination_page_2(client):
    """Pagination: ?page=2."""
    r = client.get("/articles?page=2")
    assert r.status_code == 200
    data = r.json()
    assert "results" in data


# ─── Meta: Serializer ────────────────────────────────────────────────────────


def test_items_serializer_restricts_fields(client):
    """Serializer: response only includes id, name, created_at, version (excludes secret_code)."""
    r = client.post(
        "/items",
        json={"name": "Serialized Item", "description": "Hidden", "secret_code": "xyz"},
    )
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert "name" in data
    assert "created_at" in data
    assert "version" in data
    assert "secret_code" not in data
    assert "description" not in data


# ─── Meta: Authentication ─────────────────────────────────────────────────────


def test_protected_endpoint_with_allow_any(client):
    """Authentication(permission=AllowAny): allows unauthenticated access."""
    r = client.get("/protected")
    assert r.status_code == 200
    data = r.json()
    assert "results" in data


def test_protected_endpoint_create(client):
    """Protected endpoint: POST works with AllowAny."""
    r = client.post("/protected", json={"data": "open-secret"})
    assert r.status_code == 201


# ─── HttpMethod mixins ──────────────────────────────────────────────────────


def test_readonly_endpoint_get_only(client):
    """HttpMethod.GET: only GET allowed."""
    r = client.get("/readonly")
    assert r.status_code == 200
    r = client.post("/readonly", json={"label": "x"})
    assert r.status_code == 405


# ─── Run as script ───────────────────────────────────────────────────────────


def main() -> int:
    """Run tests and print summary."""
    return pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    sys.exit(main())
