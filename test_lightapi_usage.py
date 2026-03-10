#!/usr/bin/env python3
"""
Usage test for LightAPI features — verifies all features work when used in an app.

Run: uv run python test_lightapi_usage.py

Requires: PostgreSQL with products table (run sql/seed_products.sql first)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent
_SQL_SEED = _PROJECT_ROOT / "sql" / "seed_products.sql"


def _ensure_products_table() -> None:
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
        pass


_ensure_products_table()

from starlette.testclient import TestClient  # noqa: E402

from lightapi_test_app import create_app  # noqa: E402


def ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def fail(msg: str, detail: str = "") -> None:
    print(f"  ✗ {msg}")
    if detail:
        print(f"    {detail}")


def run_checks() -> bool:
    """Run all usage checks. Returns True if all pass."""
    app = create_app()
    client = TestClient(app.build_app())
    all_ok = True

    # ─── CRUD (base) ─────────────────────────────────────────────────────────
    print("\n--- CRUD ---")
    r = client.get("/products")
    if r.status_code != 200 or "results" not in r.json():
        fail("GET /products list", f"status={r.status_code}")
        all_ok = False
    else:
        ok("GET /products list")

    r = client.post("/products", json={"sku": "U-001", "name": "Usage Test", "price": 9.99})
    if r.status_code != 201:
        fail("POST /products create", f"status={r.status_code} body={r.text[:200]}")
        all_ok = False
    else:
        data = r.json()
        if data.get("name") != "Usage Test" or "version" not in data:
            fail("POST /products response shape")
            all_ok = False
        else:
            ok("POST /products create")

    r = client.get("/products/1")
    if r.status_code != 200 or "sku" not in r.json():
        fail("GET /products/1 retrieve")
        all_ok = False
    else:
        ok("GET /products/1 retrieve")

    r = client.get("/products/1")
    version = r.json().get("version", 1)
    r = client.patch("/products/1", json={"name": "Patched", "version": version})
    if r.status_code != 200 or r.json().get("name") != "Patched":
        fail("PATCH /products/1")
        all_ok = False
    else:
        ok("PATCH /products/1")

    r = client.get("/products/1")
    version = r.json().get("version")
    data = r.json()
    r = client.put("/products/1", json={"sku": data["sku"], "name": "Put", "price": "1.11", "version": version})
    if r.status_code != 200 or r.json().get("name") != "Put":
        fail("PUT /products/1")
        all_ok = False
    else:
        ok("PUT /products/1")

    r = client.post("/products", json={"sku": "DEL-X", "name": "Del", "price": 0})
    pid = r.json()["id"]
    r = client.delete(f"/products/{pid}")
    if r.status_code != 204:
        fail("DELETE /products")
        all_ok = False
    else:
        ok("DELETE /products")

    # ─── Meta: Filtering ──────────────────────────────────────────────────────
    print("\n--- Meta: Filtering ---")
    for title, cat, author in [("Python News", "news", "Alice"), ("Django Tutorial", "tutorial", "Bob")]:
        client.post("/articles", json={"title": title, "category": cat, "author": author, "published": True})

    r = client.get("/articles?category=news")
    if r.status_code != 200:
        fail("Filter ?category=news", f"status={r.status_code}")
        all_ok = False
    else:
        results = r.json().get("results", [])
        if results and any(i.get("category") != "news" for i in results):
            fail("Filter ?category=news (wrong results)")
            all_ok = False
        else:
            ok("Filter ?category=news")

    r = client.get("/articles?search=python")
    if r.status_code != 200:
        fail("Search ?search=python")
        all_ok = False
    else:
        ok("Search ?search=python")

    r = client.get("/articles?ordering=-title")
    if r.status_code != 200:
        fail("Ordering ?ordering=-title")
        all_ok = False
    else:
        titles = [i["title"] for i in r.json().get("results", [])]
        if titles != sorted(titles, reverse=True):
            fail("Ordering ?ordering=-title (wrong order)")
            all_ok = False
        else:
            ok("Ordering ?ordering=-title")

    # ─── Meta: Pagination ────────────────────────────────────────────────────
    print("\n--- Meta: Pagination ---")
    r = client.get("/articles?page=1")
    if r.status_code != 200:
        fail("Pagination ?page=1")
        all_ok = False
    else:
        data = r.json()
        if "results" not in data or ("count" not in data and "pages" not in data and "next" not in data):
            fail("Pagination response shape")
            all_ok = False
        elif len(data["results"]) > 2:
            fail("Pagination page_size=2 not respected")
            all_ok = False
        else:
            ok("Pagination ?page=1 (page_size=2)")

    # ─── Meta: Serializer ────────────────────────────────────────────────────
    print("\n--- Meta: Serializer ---")
    r = client.post("/items", json={"name": "Item1", "description": None, "secret_code": "abc"})
    if r.status_code != 201:
        fail("POST /items", f"status={r.status_code}")
        all_ok = False
    else:
        data = r.json()
        if "secret_code" in data or "description" in data:
            fail("Serializer excludes secret_code/description from read")
            all_ok = False
        elif "id" not in data or "name" not in data:
            fail("Serializer includes id, name")
            all_ok = False
        else:
            ok("Serializer restricts response fields")

    # ─── Meta: Authentication ─────────────────────────────────────────────────
    print("\n--- Meta: Authentication ---")
    r = client.get("/protected")
    if r.status_code != 200:
        fail("GET /protected with AllowAny", f"status={r.status_code}")
        all_ok = False
    else:
        ok("GET /protected (AllowAny)")

    r = client.post("/protected", json={"data": "test"})
    if r.status_code != 201:
        fail("POST /protected with AllowAny", f"status={r.status_code}")
        all_ok = False
    else:
        ok("POST /protected (AllowAny)")

    # ─── Meta: HttpMethod ─────────────────────────────────────────────────────
    print("\n--- Meta: HttpMethod ---")
    r = client.get("/readonly")
    if r.status_code != 200:
        fail("GET /readonly (HttpMethod.GET)")
        all_ok = False
    else:
        ok("GET /readonly")

    r = client.post("/readonly", json={"label": "x"})
    if r.status_code != 405:
        fail("POST /readonly should be 405", f"status={r.status_code}")
        all_ok = False
    else:
        ok("POST /readonly returns 405")

    return all_ok


if __name__ == "__main__":
    print("LightAPI usage test — verifying features work at runtime")
    success = run_checks()
    print()
    sys.exit(0 if success else 1)
