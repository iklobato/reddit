#!/usr/bin/env python3
"""
Delete all list entries (selected/community and rejected) from Upfluence list.

Uses DELETE /list_entries/{id} to permanently remove each entry.

Usage:
    UPFLUENCE_BEARER_TOKEN="your_token" uv run python upfluence_delete_list_entries.py
"""

from __future__ import annotations

import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://facade.upfluence.co/api/v1"
LIST_ID = "374837"
PER_PAGE = 100


def get_headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "https://hq.wednesday.app",
        "Referer": "https://hq.wednesday.app/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Authorization": f"Bearer {token}",
    }


def fetch_list_entries(
    session: requests.Session,
    token: str,
    status: str,
    page: int = 1,
    per_page: int = PER_PAGE,
) -> tuple[list[dict], int, int]:
    """Fetch one page of list entries. Returns (entries, total, total_pages)."""
    url = f"{BASE_URL}/list_entries"
    params = {"list_id": LIST_ID, "page": page, "per_page": per_page, "status": status}
    resp = session.get(url, params=params, headers=get_headers(token), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    entries = data.get("list_entries") or []
    meta = data.get("meta") or {}
    total = int(meta.get("total", 0))
    total_pages = int(meta.get("total_pages", 0)) or max(1, (total + per_page - 1) // per_page)
    return entries, total, total_pages


def delete_entry(session: requests.Session, token: str, entry_id: int) -> bool:
    """DELETE a list entry. Returns True if successful."""
    url = f"{BASE_URL}/list_entries/{entry_id}"
    resp = session.delete(url, headers=get_headers(token), timeout=30)
    return resp.status_code in (200, 204)


def main() -> int:
    token = os.environ.get("UPFLUENCE_BEARER_TOKEN")
    if not token:
        print("Error: Set UPFLUENCE_BEARER_TOKEN environment variable.", file=sys.stderr)
        return 1

    session = requests.Session()
    all_entries: list[dict] = []

    for status in ("selected", "rejected"):
        print(f"Fetching {status} entries...")
        page = 1
        total_pages = 1
        try:
            while page <= total_pages:
                entries, total, total_pages = fetch_list_entries(
                    session, token, status=status, page=page
                )
                all_entries.extend(entries)
                print(f"  Page {page}/{total_pages}: {len(entries)} entries (total: {total})")
                if page >= total_pages:
                    break
                page += 1
                time.sleep(0.2)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                print(f"  No {status} entries or API error.")
            else:
                raise

    if not all_entries:
        print("\nNo entries to delete.")
        return 0

    print(f"\nDeleting {len(all_entries)} entries...")
    ok = 0
    fail = 0
    for i, entry in enumerate(all_entries, 1):
        eid = entry.get("id")
        if eid is None:
            fail += 1
            continue
        if delete_entry(session, token, eid):
            ok += 1
        else:
            fail += 1
        if i % 20 == 0 or i == len(all_entries):
            print(f"  Deleted {i}/{len(all_entries)} (ok: {ok}, fail: {fail})")
        time.sleep(0.1)

    print(f"\nDone. Deleted: {ok}, Failed: {fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
