#!/usr/bin/env python3
"""
Remove all influencers from Upfluence/Wednesday community (list 374837).

Fetches all list entries with status=selected, then PUTs each with status=rejected.
Or reads from a CSV file with list_entry_id,influencer_id columns.

Usage:
    UPFLUENCE_BEARER_TOKEN="your_token" uv run python upfluence_remove_community.py
    UPFLUENCE_BEARER_TOKEN="your_token" uv run python upfluence_remove_community.py --from-file entries.csv
"""

from __future__ import annotations

import argparse
import csv
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
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "https://hq.wednesday.app",
        "Referer": "https://hq.wednesday.app/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Authorization": f"Bearer {token}",
    }


def fetch_list_entries(
    session: requests.Session,
    token: str,
    page: int = 1,
    per_page: int = PER_PAGE,
) -> tuple[list[dict], int, int]:
    """Fetch one page of list entries. Returns (entries, total, total_pages)."""
    url = f"{BASE_URL}/list_entries"
    params = {"list_id": LIST_ID, "page": page, "per_page": per_page, "status": "selected"}
    resp = session.get(url, params=params, headers=get_headers(token), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    entries = data.get("list_entries") or []
    meta = data.get("meta") or {}
    total = int(meta.get("total", 0))
    total_pages = int(meta.get("total_pages", 0)) or max(1, (total + per_page - 1) // per_page)
    return entries, total, total_pages


def remove_entry(
    session: requests.Session,
    token: str,
    entry_id: int,
    influencer_id: int,
) -> bool:
    """Remove (reject) a list entry. Returns True if successful."""
    url = f"{BASE_URL}/list_entries/{entry_id}"
    body = {
        "list_entry": {
            "name": None,
            "email": None,
            "status": "rejected",
            "score_model": None,
            "list_id": LIST_ID,
            "influencer_id": str(influencer_id),
        }
    }
    resp = session.put(url, json=body, headers=get_headers(token), timeout=30)
    return resp.status_code == 200


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove influencers from Upfluence community")
    parser.add_argument(
        "--from-file",
        "-f",
        type=str,
        default=None,
        help="CSV file with list_entry_id,influencer_id columns (skip API fetch)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Only fetch/list, do not remove")
    args = parser.parse_args()

    token = os.environ.get("UPFLUENCE_BEARER_TOKEN")
    if not token:
        print("Error: Set UPFLUENCE_BEARER_TOKEN environment variable.", file=sys.stderr)
        return 1

    session = requests.Session()
    all_entries: list[dict] = []

    if args.from_file:
        print(f"Reading entries from {args.from_file}...")
        with open(args.from_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                eid = row.get("list_entry_id") or row.get("id")
                inf_id = row.get("influencer_id")
                if eid and inf_id:
                    all_entries.append({"id": int(eid), "influencer_id": int(inf_id)})
        print(f"  Loaded {len(all_entries)} entries")
    else:
        print("Fetching list entries...")
        page = 1
        total_pages = 1
        try:
            while page <= total_pages:
                entries, total, total_pages = fetch_list_entries(session, token, page=page)
                all_entries.extend(entries)
                print(f"  Page {page}/{total_pages}: {len(entries)} entries (collected: {len(all_entries)} / total: {total})")
                if page >= total_pages:
                    break
                page += 1
                time.sleep(0.2)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                print("Error: list_entries API returned 404. Try --from-file with exported data.", file=sys.stderr)
            else:
                raise
            return 1

    if not all_entries:
        print("\nNo entries to remove.")
        return 0

    if args.dry_run:
        print(f"\nDry run: would remove {len(all_entries)} entries.")
        return 0

    print(f"\nRemoving {len(all_entries)} entries...")
    ok = 0
    fail = 0
    for i, entry in enumerate(all_entries, 1):
        eid = entry.get("id")
        inf_id = entry.get("influencer_id")
        if eid is None or inf_id is None:
            fail += 1
            continue
        if remove_entry(session, token, eid, inf_id):
            ok += 1
        else:
            fail += 1
        if i % 20 == 0 or i == len(all_entries):
            print(f"  Removed {i}/{len(all_entries)} (ok: {ok}, fail: {fail})")
        time.sleep(0.1)

    print(f"\nDone. Removed: {ok}, Failed: {fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
