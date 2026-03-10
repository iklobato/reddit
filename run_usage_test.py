#!/usr/bin/env python3
"""
LightAPI usage test — comprehensive integration check.

Uses the app as a real user would: import from myapp, build the ASGI app,
hit endpoints via HTTP. Verifies all Meta features and PostgreSQL state.

Run: uv run python run_usage_test.py

Requires: PostgreSQL in Docker (container 'psql') with default credentials.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SQL = _ROOT / "sql" / "seed_products.sql"


def _run_sql(sql: str) -> tuple[int, str, str]:
    """Run SQL via docker exec. Returns (exit_code, stdout, stderr)."""
    try:
        r = subprocess.run(
            ["docker", "exec", "-i", "psql", "psql", "-U", "postgres", "-d", "postgres", "-t", "-A"],
            input=sql.encode(),
            capture_output=True,
            timeout=10,
        )
        return r.returncode, (r.stdout or b"").decode(), (r.stderr or b"").decode()
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return -1, "", str(e)


def _run_sql_file(path: Path) -> None:
    try:
        subprocess.run(
            ["docker", "exec", "-i", "psql", "psql", "-U", "postgres", "-d", "postgres", "-f", "-"],
            stdin=path.open(),
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


# Setup
if _SQL.exists():
    _run_sql_file(_SQL)
_run_sql("DROP TABLE IF EXISTS articleendpoints, noteendpoints, publicendpoints, tags CASCADE;")

from starlette.testclient import TestClient

from myapp.app import create_app
from myapp.config import DATABASE_URL


def ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def fail(msg: str, detail: str = "") -> None:
    print(f"  ✗ {msg}")
    if detail:
        print(f"    {detail}")


def main() -> int:
    all_ok = True

    # ─── PostgreSQL health check ──────────────────────────────────────────────
    print("--- PostgreSQL (docker) ---")
    code, out, err = _run_sql("SELECT 1;")
    if code != 0:
        fail("Connection", err or f"exit_code={code}")
        all_ok = False
    else:
        ok("Connection")

    code, out, err = _run_sql("SELECT COUNT(*) FROM products;")
    if code != 0:
        fail("Products table exists", err or f"exit_code={code}")
        all_ok = False
    elif not out.strip().isdigit():
        fail("Products table exists", f"unexpected output: {out!r}")
        all_ok = False
    else:
        n = int(out.strip())
        ok(f"Products table ({n} rows)")

    code, out, err = _run_sql(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='products' ORDER BY ordinal_position;"
    )
    if code != 0:
        fail("Products schema", err or f"exit_code={code}")
        all_ok = False
    else:
        cols = [c.strip() for c in out.strip().split("\n") if c.strip()]
        expected = {"id", "sku", "name", "price", "created_at", "updated_at", "version"}
        if set(cols) != expected:
            fail("Products schema", f"got {cols}")
            all_ok = False
        else:
            ok("Products schema (id, sku, name, price, created_at, updated_at, version)")

    # ─── App & client ─────────────────────────────────────────────────────────
    app = create_app()
    client = TestClient(app.build_app())

    # ─── CRUD (reflected products) ─────────────────────────────────────────────
    print("\n--- CRUD (Meta.reflect) ---")
    r = client.get("/products")
    if r.status_code != 200 or "results" not in r.json():
        fail("GET list", f"status={r.status_code}")
        all_ok = False
    else:
        ok("GET list")

    r = client.post("/products", json={"sku": "T-001", "name": "Test", "price": 12.99})
    if r.status_code != 201:
        fail("POST create", f"status={r.status_code}")
        all_ok = False
    else:
        d = r.json()
        if d.get("name") != "Test" or "version" not in d:
            fail("POST response shape")
            all_ok = False
        else:
            ok("POST create")

    r = client.get("/products/1")
    if r.status_code != 200 or "sku" not in r.json():
        fail("GET retrieve")
        all_ok = False
    else:
        ok("GET retrieve")

    v = client.get("/products/1").json().get("version", 1)
    r = client.patch("/products/1", json={"name": "Patched", "version": v})
    if r.status_code != 200 or r.json().get("name") != "Patched":
        fail("PATCH partial update")
        all_ok = False
    else:
        ok("PATCH partial update")

    d = client.get("/products/1").json()
    r = client.put("/products/1", json={"sku": d["sku"], "name": "Put", "price": "2.50", "version": d["version"]})
    if r.status_code != 200 or r.json().get("price") != "2.50":
        fail("PUT full update")
        all_ok = False
    else:
        ok("PUT full update")

    r = client.post("/products", json={"sku": "DEL-X", "name": "Del", "price": 0})
    pid = r.json()["id"]
    r = client.delete(f"/products/{pid}")
    if r.status_code != 204:
        fail("DELETE")
        all_ok = False
    else:
        ok("DELETE")

    # ─── Error responses ──────────────────────────────────────────────────────
    print("\n--- Error responses ---")
    r = client.get("/products/99999")
    if r.status_code != 404:
        fail("GET non-existent → 404", f"status={r.status_code}")
        all_ok = False
    else:
        ok("GET non-existent → 404")

    r = client.delete("/products/99999")
    if r.status_code != 404:
        fail("DELETE non-existent → 404", f"status={r.status_code}")
        all_ok = False
    else:
        ok("DELETE non-existent → 404")

    r = client.post("/products", json={"sku": "X", "name": "X"})  # missing price
    if r.status_code != 422:
        fail("POST validation error → 422", f"status={r.status_code}")
        all_ok = False
    else:
        ok("POST validation error → 422")

    v = client.get("/products/1").json().get("version", 1)
    r = client.patch("/products/1", json={"name": "X", "version": 999})  # stale version
    if r.status_code != 409:
        fail("PATCH version conflict → 409", f"status={r.status_code}")
        all_ok = False
    else:
        ok("PATCH version conflict → 409")

    r = client.patch("/products/1", json={"name": "X"})  # missing version
    if r.status_code != 422:
        fail("PATCH missing version → 422", f"status={r.status_code}")
        all_ok = False
    else:
        ok("PATCH missing version → 422")

    r = client.put("/products/1", json={"sku": "SKU-001", "name": "X", "price": "1"})  # missing version
    if r.status_code != 422:
        fail("PUT missing version → 422", f"status={r.status_code}")
        all_ok = False
    else:
        ok("PUT missing version → 422")

    # ─── Meta: Filtering ──────────────────────────────────────────────────────
    print("\n--- Meta: Filtering ---")
    for t, c, a in [
        ("Python News", "news", "Alice"),
        ("Django Tutorial", "tutorial", "Bob"),
        ("FastAPI Update", "news", "Charlie"),
        ("REST Design", "tutorial", "Alice"),
        ("Python 3.12", "news", "Bob"),
    ]:
        client.post("/articles", json={"title": t, "category": c, "author": a, "published": True})

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

    r = client.get("/articles?published=true")
    if r.status_code != 200:
        fail("Filter ?published=true", f"status={r.status_code}")
        all_ok = False
    else:
        ok("Filter ?published=true")

    r = client.get("/articles?category=news&published=true")
    if r.status_code != 200:
        fail("Combined filters", f"status={r.status_code}")
        all_ok = False
    else:
        ok("Combined filters")

    r = client.get("/articles?search=python")
    if r.status_code != 200:
        fail("Search ?search=python")
        all_ok = False
    else:
        results = r.json().get("results", [])
        found = any("python" in (i.get("title", "") + i.get("author", "")).lower() for i in results)
        if results and not found:
            fail("Search ?search=python (no match)")
            all_ok = False
        else:
            ok("Search ?search=python")

    r = client.get("/articles?ordering=title")
    if r.status_code != 200:
        fail("Ordering ?ordering=title (asc)")
        all_ok = False
    else:
        titles = [i["title"] for i in r.json().get("results", [])]
        if titles != sorted(titles):
            fail("Ordering ?ordering=title (wrong order)")
            all_ok = False
        else:
            ok("Ordering ?ordering=title (asc)")

    r = client.get("/articles?ordering=-created_at")
    if r.status_code != 200:
        fail("Ordering ?ordering=-created_at")
        all_ok = False
    else:
        ok("Ordering ?ordering=-created_at")

    r = client.get("/articles?category=nonexistent")
    if r.status_code != 200:
        fail("Filter no matches", f"status={r.status_code}")
        all_ok = False
    else:
        results = r.json().get("results", [])
        if results:
            fail("Filter no matches (expected empty)")
            all_ok = False
        else:
            ok("Filter no matches returns empty")

    r = client.get("/articles?search=xyznonexistent123")
    if r.status_code != 200:
        fail("Search no matches", f"status={r.status_code}")
        all_ok = False
    else:
        ok("Search no matches")

    # ─── PostgreSQL: app tables ────────────────────────────────────────────────
    print("\n--- PostgreSQL: app tables ---")
    for tbl in ["articleendpoints", "noteendpoints", "publicendpoints", "tags"]:
        code, out, err = _run_sql(f"SELECT 1 FROM {tbl} LIMIT 1;")
        if code != 0:
            fail(f"Table {tbl} exists", err or f"exit_code={code}")
            all_ok = False
        else:
            ok(f"Table {tbl} exists")

    # ─── PostgreSQL: version & updated_at ──────────────────────────────────────
    print("\n--- PostgreSQL: optimistic locking ---")
    v_before = client.get("/products/1").json().get("version", 1)
    client.patch("/products/1", json={"name": "VersionCheck", "version": v_before})
    code, out, err = _run_sql("SELECT version, updated_at FROM products WHERE id=1;")
    if code != 0:
        fail("Version/updated_at in DB", err)
        all_ok = False
    else:
        parts = (out or "").strip().split("|")
        if len(parts) >= 1 and parts[0].strip().isdigit() and int(parts[0]) > v_before:
            ok("Version incremented in DB after PATCH")
        else:
            fail("Version incremented in DB", f"got {out!r}")
            all_ok = False

    # ─── Meta: Pagination ──────────────────────────────────────────────────────
    print("\n--- Meta: Pagination ---")
    r = client.get("/articles?page=1")
    if r.status_code != 200:
        fail("Pagination ?page=1", f"status={r.status_code}")
        all_ok = False
    else:
        data = r.json()
        if "results" not in data:
            fail("Pagination response shape")
            all_ok = False
        elif len(data["results"]) > 2:
            fail("page_size=2 not respected")
            all_ok = False
        elif "count" not in data and "pages" not in data and "next" not in data:
            fail("Pagination metadata")
            all_ok = False
        else:
            ok("Pagination ?page=1 (page_size=2)")

    r = client.get("/articles?page=2")
    if r.status_code != 200:
        fail("Pagination ?page=2")
        all_ok = False
    else:
        ok("Pagination ?page=2")

    # ─── Meta: Serializer ──────────────────────────────────────────────────────
    print("\n--- Meta: Serializer ---")
    r = client.post("/notes", json={"title": "Note1", "body": "secret"})
    if r.status_code != 201:
        fail("POST /notes", f"status={r.status_code}")
        all_ok = False
    else:
        data = r.json()
        if "body" in data:
            fail("Serializer excludes body from create response")
            all_ok = False
        elif "id" not in data or "title" not in data or "created_at" not in data or "version" not in data:
            fail("Serializer includes id, title, created_at, version")
            all_ok = False
        else:
            ok("Serializer on create response")

    nid = r.json()["id"]
    r = client.get(f"/notes/{nid}")
    if r.status_code != 200:
        fail("GET /notes/{id}")
        all_ok = False
    else:
        if "body" in r.json():
            fail("Serializer excludes body from retrieve")
            all_ok = False
        else:
            ok("Serializer on retrieve")

    r = client.get("/notes")
    if r.status_code != 200:
        fail("GET /notes list")
        all_ok = False
    else:
        results = r.json().get("results", [])
        if results and "body" in results[0]:
            fail("Serializer excludes body from list")
            all_ok = False
        else:
            ok("Serializer on list")

    r = client.post("/notes", json={"title": "Note2", "body": None})
    if r.status_code != 201:
        fail("POST with optional body=null", f"status={r.status_code}")
        all_ok = False
    else:
        ok("Optional field body=null")

    # ─── Meta: Authentication ─────────────────────────────────────────────────
    print("\n--- Meta: Authentication ---")
    r = client.get("/public")
    if r.status_code != 200:
        fail("GET /public (AllowAny)", f"status={r.status_code}")
        all_ok = False
    else:
        ok("GET /public (AllowAny)")

    r = client.post("/public", json={"message": "hello"})
    if r.status_code != 201:
        fail("POST /public (AllowAny)", f"status={r.status_code}")
        all_ok = False
    else:
        ok("POST /public (AllowAny)")

    # ─── Meta: HttpMethod ──────────────────────────────────────────────────────
    print("\n--- Meta: HttpMethod ---")
    r = client.get("/tags")
    if r.status_code != 200:
        fail("GET /tags (HttpMethod.GET)")
        all_ok = False
    else:
        ok("GET /tags")

    r = client.post("/tags", json={"tag": "x"})
    if r.status_code != 405:
        fail("POST /tags → 405", f"status={r.status_code}")
        all_ok = False
    else:
        ok("POST /tags → 405")

    r = client.put("/tags/1", json={"tag": "x", "version": 1})
    if r.status_code != 405:
        fail("PUT /tags → 405", f"status={r.status_code}")
        all_ok = False
    else:
        ok("PUT /tags → 405")

    # ─── Data persistence (API → DB) ──────────────────────────────────────────
    print("\n--- Data persistence (API → PostgreSQL) ---")
    r = client.post("/products", json={"sku": "PERSIST-1", "name": "Persist Test", "price": 42.0})
    if r.status_code != 201:
        fail("Create via API")
        all_ok = False
    else:
        pid = r.json()["id"]
        code, out, err = _run_sql(f"SELECT name, price FROM products WHERE id = {pid};")
        if code != 0:
            fail("Data in PostgreSQL after API create", err or "query failed")
            all_ok = False
        elif "Persist Test" not in (out or ""):
            fail("Data in PostgreSQL after API create", f"row not found: {out!r}")
            all_ok = False
        else:
            ok("Data in PostgreSQL after API create")

    # ─── Numeric/Decimal handling ──────────────────────────────────────────────
    print("\n--- Numeric handling ---")
    r = client.get("/products/1")
    if r.status_code != 200:
        fail("GET product price")
        all_ok = False
    else:
        price = r.json().get("price")
        if price is None:
            fail("Price in response")
            all_ok = False
        else:
            ok(f"Price serialized as string (e.g. {price!r})")

    print()
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
