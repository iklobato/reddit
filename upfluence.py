#!/usr/bin/env python3
"""
Unified Upfluence Scraper Tool
==============================

A comprehensive tool for extracting influencer data from Upfluence/Wednesday platform.
Reads filtering rules from filters.json and supports multiple operations through a unified CLI.

Features:
- Search for influencers with customizable filters
- Export full influencer contact details
- Manage community lists (add/remove influencers)
- Clean up list entries
- Parallel processing for efficient data extraction
- Configurable filtering via JSON files

Setup:
1. Set your Upfluence bearer token:
   export UPFLUENCE_BEARER_TOKEN="your_token_here"

2. Configure filters in filters.json (created automatically with defaults)

Usage Examples:
---------------

1. BASIC SEARCH (most common use case):
   Search for influencers matching filters and save to CSV:
   python upfluence.py search --output influencers.csv --limit 100

   With custom keywords:
   python upfluence.py search --keywords "Fintech,Trading,APIs" --limit 50

   Append to existing file:
   python upfluence.py search --output existing.csv --limit 200

2. FULL EXPORT:
   Export complete influencer details (all fields):
   python upfluence.py export --output contacts.csv --workers 32

   Limited export for testing:
   python upfluence.py export --limit 10 --output test.csv

3. LIST MANAGEMENT:
   Remove influencers from community list (dry run first):
   python upfluence.py remove --dry-run
   python upfluence.py remove

   Remove from specific CSV file:
   python upfluence.py remove --from-file entries.csv

4. CLEANUP:
   Delete list entries permanently:
   python upfluence.py cleanup --status selected,rejected

   Dry run to see what would be deleted:
   python upfluence.py cleanup --dry-run

5. CUSTOM FILTERS:
   Use different filter configuration:
   python upfluence.py search --filters custom_filters.json

   Override list ID:
   python upfluence.py search --list-id "123456"

Advanced Usage:
---------------

Combine operations for a complete workflow:
1. Clear existing list: python upfluence.py cleanup
2. Search new influencers: python upfluence.py search --limit 500
3. Export full details: python upfluence.py export --workers 64
4. Remove processed influencers: python upfluence.py remove

Filter Configuration (filters.json):
------------------------------------
- "criterias": Search keywords and fields
- "filters": Platform-specific filters (followers, engagement, etc.)
- "list_id": Target Upfluence list ID
- Override any parameter via command line

Environment Variables:
----------------------
- UPFLUENCE_BEARER_TOKEN: Required authentication token
- Can also use .env file with dotenv support

Output Formats:
---------------
- CSV files with all influencer fields
- Complex fields (lists, dicts) stored as JSON strings
- Automatic header management for appending to existing files
- Timestamp-based default filenames

Notes:
------
- API rate limits: Use --workers 1 if hitting limits
- Pagination: Handles offsets up to 1000 automatically
- Error handling: Logs failed requests, continues processing
- Dry runs: Available for destructive operations
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://facade.upfluence.co/api/v1"
DEFAULT_FILTERS_FILE = "filters.json"
DEFAULT_LIST_ID = "374837"
PER_PAGE = 100


class UpfluenceClient:
    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()

        # Configure retry strategy with exponential backoff
        retry_strategy = Retry(
            total=5,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
            raise_on_status=False,
            respect_retry_after_header=True,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.default_timeout = (30, 60)
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": "https://hq.wednesday.app",
            "Referer": "https://hq.wednesday.app/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Authorization": f"Bearer {token}",
        }

    def _log_response(self, resp: requests.Response, context: str = "") -> None:
        if resp.status_code < 400:
            return
        try:
            body = resp.text
            if len(body) > 2000:
                body = body[:2000] + f"... [truncated, total {len(resp.text)} chars]"
            print(f"[WARN] Response error {context} - status={resp.status_code}")
            print(f"  {body}")
        except Exception:
            pass

    def get_list_entries(
        self,
        list_id: str,
        status: str = "selected",
        page: int = 1,
        per_page: int = PER_PAGE,
    ) -> Tuple[List[Dict], int, int]:
        url = f"{BASE_URL}/list_entries"
        params = {
            "list_id": list_id,
            "page": page,
            "per_page": per_page,
            "status": status,
        }
        resp = self.session.get(
            url, params=params, headers=self.headers, timeout=self.default_timeout
        )
        if not resp.ok:
            self._log_response(resp, "list_entries")
            resp.raise_for_status()
        data = resp.json()
        entries = data.get("list_entries") or []
        meta = data.get("meta") or {}
        total = int(meta.get("total", 0))
        total_pages = int(meta.get("total_pages", 0)) or max(
            1, (total + per_page - 1) // per_page
        )
        return entries, total, total_pages

    def reject_entry(self, list_id: str, entry_id: int, influencer_id: int) -> bool:
        # Since list_entries API doesn't work, just blacklist the influencer
        # The entry_id parameter is kept for compatibility but not used
        return self._blacklist_influencer(influencer_id)

    def _blacklist_influencer(self, influencer_id: int) -> bool:
        """Export influencer to blacklist using export API"""
        url = "https://export.upfluence.co/api/v1/export"
        body = {
            "source": {"influencer_ids": [influencer_id], "max_size": 1000},
            "destination": {"to": "crm:blacklist"},
        }
        try:
            resp = self.session.post(
                url, json=body, headers=self.headers, timeout=self.default_timeout
            )
            success = resp.status_code == 200
            if success:
                print(f"[DEBUG] Successfully blacklisted influencer {influencer_id}")
            else:
                print(
                    f"[DEBUG] Failed to blacklist influencer {influencer_id}: {resp.status_code}"
                )
            return success
        except Exception as e:
            print(f"[DEBUG] Error blacklisting influencer {influencer_id}: {e}")
            return False

    def delete_entry(self, entry_id: int) -> bool:
        url = f"{BASE_URL}/list_entries/{entry_id}"
        resp = self.session.delete(
            url, headers=self.headers, timeout=self.default_timeout
        )
        return resp.status_code in (200, 204)

    def search_matches(
        self, search_body: Dict, page: int = 1, per_page: int = PER_PAGE
    ) -> Tuple[List[Dict], int, int]:
        url = f"{BASE_URL}/matches"
        params = {"page": page, "per_page": per_page}
        offset = (page - 1) * per_page
        if offset <= 1000:
            params["offset"] = offset
        resp = self.session.post(
            url,
            params=params,
            json=search_body,
            headers=self.headers,
            timeout=self.default_timeout,
        )
        if not resp.ok:
            self._log_response(resp, f"matches page={page}")
            if resp.status_code == 400:
                print("[WARN] 400 Bad Request - invalid filter parameters")
                return [], 0, page - 1
            if resp.status_code == 402:
                print("[ERROR] 402 Payment Required - check Upfluence subscription")
                return [], 0, page - 1
            if resp.status_code == 500:
                print(
                    "[ERROR] 500 Internal Server Error - API issue, try simpler filters"
                )
                return [], 0, page - 1
            resp.raise_for_status()
        data = resp.json()
        matches = data.get("matches") or data.get("data") or data.get("hits") or []
        meta = data.get("meta") or {}
        total = (
            int(meta.get("total", 0))
            or data.get("total")
            or data.get("total_count")
            or len(matches)
        )
        total_pages = int(meta.get("totalPages", 0)) or max(
            1, (total + per_page - 1) // per_page
        )
        return matches, total, total_pages

    def unlock_influencer(self, influencer_id: int) -> Optional[Dict]:
        url = f"{BASE_URL}/influencers/{influencer_id}/unlock"
        resp = self.session.put(url, headers=self.headers, timeout=self.default_timeout)
        if resp.status_code != 200:
            self._log_response(resp, f"unlock influencer_id={influencer_id}")
            return None
        data = resp.json()
        return data.get("influencer") or data


def load_filters(filters_file: str = DEFAULT_FILTERS_FILE) -> Dict:
    try:
        with open(filters_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARN] Filters file {filters_file} not found, using defaults")
        return {
            "list_id": DEFAULT_LIST_ID,
            "criterias": [],
            "filters": [],
            "audience_filters": [],
            "social_media_matching_operator": "or",
            "should_save": True,
            "track_hits_results": 10000,
            "score_model": "default",
            "premade_search": None,
        }


def build_search_body(
    filters: Dict, list_id: Optional[str] = None, keywords: Optional[List[str]] = None
) -> Dict:
    search_body = filters.copy()
    if list_id:
        search_body["current_list"] = list_id
    if keywords:
        search_body["criterias"] = [
            {"value": v, "weight": 1, "field": "all", "type": "should"}
            for v in keywords
        ]
    return search_body


def serialize_value(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, (list, dict)):
        return json.dumps(val)
    return str(val).replace("\n", " ").replace("\r", "")


def extract_row(influencer: Dict) -> Dict[str, str]:
    return {key: serialize_value(val) for key, val in influencer.items()}


def log_section(title: str) -> None:
    print(f"\n{'─' * 60}\n  {title}\n{'─' * 60}", flush=True)


def command_search(args) -> int:
    filters = load_filters(args.filters)
    list_id = args.list_id or filters.get("list_id", DEFAULT_LIST_ID)

    token = os.environ.get("UPFLUENCE_BEARER_TOKEN")
    if not token:
        print("[ERROR] UPFLUENCE_BEARER_TOKEN not set")
        return 1

    client = UpfluenceClient(token)

    keywords = args.keywords.split(",") if args.keywords else None
    search_body = build_search_body(filters, list_id, keywords)

    print(f"[INFO] Starting search with list_id={list_id}")
    if keywords:
        print(
            f"[INFO] Keywords: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}"
        )

    output_path = Path(args.output)

    # Determine file mode and whether to write header
    seen_ids = set()

    if args.append and output_path.exists() and output_path.stat().st_size > 0:
        file_mode = "a"
        have_header = True
        print(f"[INFO] Appending to existing file: {output_path}")

        # Read existing IDs from the file to avoid duplicates
        try:
            with open(output_path, "r", encoding="utf-8") as existing_file:
                reader = csv.DictReader(existing_file)
                if reader.fieldnames and "id" in reader.fieldnames:
                    for row in reader:
                        if "id" in row and row["id"]:
                            seen_ids.add(row["id"])
            print(
                f"[INFO] Loaded {len(seen_ids)} existing IDs from file to avoid duplicates"
            )
        except Exception as e:
            print(f"[WARN] Could not read existing file for deduplication: {e}")
    else:
        file_mode = "w"
        have_header = False
        if args.append:
            print(
                f"[INFO] Creating new file (or overwriting empty file): {output_path}"
            )
        else:
            print(f"[INFO] Writing to file: {output_path}")

    page, total_pages = 1, 1
    processed = 0

    with open(output_path, file_mode, newline="", encoding="utf-8") as f:
        writer = None
        fieldnames = []

        while page <= total_pages and (not args.limit or processed < args.limit):
            matches, total, total_pages = client.search_matches(
                search_body, page, args.per_page
            )
            print(
                f"[INFO] Page {page}/{total_pages}: {len(matches)} matches (total: {total})"
            )

            for match in matches:
                influencer_id = (
                    match.get("id")
                    or match.get("influencer_id")
                    or (match.get("influencer") or {}).get("id")
                )
                if not influencer_id or influencer_id in seen_ids:
                    continue

                if args.limit and processed >= args.limit:
                    break

                seen_ids.add(influencer_id)
                influencer = client.unlock_influencer(int(influencer_id))

                if influencer:
                    row = extract_row(influencer)
                    if writer is None:
                        fieldnames = sorted(row.keys())
                        if "id" in fieldnames:
                            fieldnames = ["id"] + [f for f in fieldnames if f != "id"]
                        writer = csv.DictWriter(
                            f, fieldnames=fieldnames, extrasaction="ignore"
                        )
                        if not have_header:
                            writer.writeheader()
                            have_header = True

                    for field in fieldnames:
                        row.setdefault(field, "")
                    writer.writerow(row)
                    f.flush()
                    processed += 1

                    if processed % 10 == 0:
                        print(f"[INFO] Processed {processed} influencers")

                time.sleep(0.1)

            page += 1
            time.sleep(0.2)

    print(f"[INFO] Search complete: {processed} influencers saved to {output_path}")
    return 0


def command_export(args) -> int:
    filters = load_filters(args.filters)
    list_id = args.list_id or filters.get("list_id", DEFAULT_LIST_ID)

    token = os.environ.get("UPFLUENCE_BEARER_TOKEN")
    if not token:
        print("[ERROR] UPFLUENCE_BEARER_TOKEN not set")
        return 1

    client = UpfluenceClient(token)

    search_body = build_search_body(filters, list_id)

    print("[INFO] Fetching matches...")
    all_ids = set()
    page, total_pages = 1, 1

    while page <= total_pages:
        matches, total, total_pages = client.search_matches(
            search_body, page, args.per_page
        )
        for match in matches:
            influencer_id = (
                match.get("id")
                or match.get("influencer_id")
                or (match.get("influencer") or {}).get("id")
            )
            if influencer_id:
                all_ids.add(int(influencer_id))

        print(
            f"[INFO] Page {page}/{total_pages}: {len(matches)} matches (collected: {len(all_ids)})"
        )
        page += 1
        time.sleep(0.2)

    ids_list = sorted(all_ids)
    if args.limit:
        ids_list = ids_list[: args.limit]

    print(
        f"[INFO] Unlocking {len(ids_list)} influencers with {args.workers} workers..."
    )

    results = {}
    lock = threading.Lock()

    def unlock_task(influencer_id: int) -> Tuple[int, Optional[Dict]]:
        task_client = UpfluenceClient(token)
        try:
            influencer = task_client.unlock_influencer(influencer_id)
            return influencer_id, influencer
        finally:
            task_client.session.close()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(unlock_task, iid): iid for iid in ids_list}
        for i, future in enumerate(as_completed(futures), 1):
            influencer_id, influencer = future.result()
            if influencer:
                results[influencer_id] = extract_row(influencer)
            else:
                results[influencer_id] = {"id": str(influencer_id)}

            if i % 50 == 0 or i == len(ids_list):
                print(f"[INFO] Unlocked {i}/{len(ids_list)}")

    rows = [results[iid] for iid in ids_list]
    all_keys = sorted(set().union(*(r.keys() for r in rows)))
    if "id" in all_keys:
        all_keys = ["id"] + [k for k in all_keys if k != "id"]

    for row in rows:
        for k in all_keys:
            row.setdefault(k, "")

    output_path = Path(args.output)

    # Determine file mode and whether to write header
    if args.append and output_path.exists() and output_path.stat().st_size > 0:
        file_mode = "a"
        write_header = False
        print(f"[INFO] Appending to existing file: {output_path}")
    else:
        file_mode = "w"
        write_header = True
        if args.append:
            print(
                f"[INFO] Creating new file (or overwriting empty file): {output_path}"
            )
        else:
            print(f"[INFO] Writing to file: {output_path}")

    with open(output_path, file_mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerows(rows)

    print(f"[INFO] Exported {len(rows)} contacts to {output_path}")
    return 0


def command_remove(args) -> int:
    filters = load_filters(args.filters)
    list_id = args.list_id or filters.get("list_id", DEFAULT_LIST_ID)

    token = os.environ.get("UPFLUENCE_BEARER_TOKEN")
    if not token:
        print("[ERROR] UPFLUENCE_BEARER_TOKEN not set")
        return 1

    client = UpfluenceClient(token)

    if args.from_file:
        print(f"[INFO] Reading entries from {args.from_file}...")
        entries = []
        with open(args.from_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry_id = row.get("list_entry_id") or row.get("id")
                influencer_id = row.get("influencer_id")
                if entry_id and influencer_id:
                    entries.append(
                        {"id": int(entry_id), "influencer_id": int(influencer_id)}
                    )
        print(f"[INFO] Loaded {len(entries)} entries")
    else:
        print("[INFO] Fetching list entries...")
        entries = []
        page, total_pages = 1, 1

        try:
            while page <= total_pages:
                page_entries, total, total_pages = client.get_list_entries(
                    list_id, "selected", page
                )
                entries.extend(page_entries)
                print(
                    f"[INFO] Page {page}/{total_pages}: {len(page_entries)} entries (total: {len(entries)})"
                )
                page += 1
                time.sleep(0.2)
        except requests.HTTPError as e:
            if e.response and e.response.status_code == 404:
                print(
                    "[ERROR] list_entries API endpoint not found (404).\n"
                    "This API endpoint may have changed or the list ID may be incorrect.\n"
                    "Try using --from-file with a CSV file containing influencer IDs.\n"
                    "Example CSV format should have columns: list_entry_id,influencer_id\n"
                    "Or generate a CSV using: python upfluence.py export --output influencers.csv"
                )
                return 1
            raise

    if not entries:
        print("[INFO] No entries to remove.")
        return 0

    if args.dry_run:
        print(f"[INFO] Dry run: would remove {len(entries)} entries.")
        return 0

    print(f"[INFO] Removing {len(entries)} entries...")
    success, failed = 0, 0

    for i, entry in enumerate(entries, 1):
        entry_id = entry.get("id")
        influencer_id = entry.get("influencer_id")

        if entry_id is None or influencer_id is None:
            failed += 1
            continue

        if client.reject_entry(list_id, entry_id, influencer_id):
            success += 1
        else:
            failed += 1

        if i % 20 == 0 or i == len(entries):
            print(
                f"[INFO] Processed {i}/{len(entries)} (success: {success}, failed: {failed})"
            )
        time.sleep(0.1)

    print(f"[INFO] Done. Removed: {success}, Failed: {failed}")
    return 0 if failed == 0 else 1


def command_cleanup(args) -> int:
    filters = load_filters(args.filters)
    list_id = args.list_id or filters.get("list_id", DEFAULT_LIST_ID)

    token = os.environ.get("UPFLUENCE_BEARER_TOKEN")
    if not token:
        print("[ERROR] UPFLUENCE_BEARER_TOKEN not set")
        return 1

    client = UpfluenceClient(token)

    statuses = [s.strip() for s in args.status.split(",")]
    all_entries = []

    for status in statuses:
        print(f"[INFO] Fetching {status} entries...")
        page, total_pages = 1, 1

        try:
            while page <= total_pages:
                page_entries, total, total_pages = client.get_list_entries(
                    list_id, status, page
                )
                all_entries.extend(page_entries)
                print(
                    f"[INFO] Page {page}/{total_pages}: {len(page_entries)} entries (total: {len(all_entries)})"
                )
                page += 1
                time.sleep(0.2)
        except requests.HTTPError as e:
            if e.response and e.response.status_code == 404:
                print(f"[WARN] No {status} entries or API error.")
                continue
            raise

    if not all_entries:
        print("[INFO] No entries to delete.")
        return 0

    if args.dry_run:
        print(f"[INFO] Dry run: would delete {len(all_entries)} entries.")
        return 0

    print(f"[INFO] Deleting {len(all_entries)} entries...")
    success, failed = 0, 0

    for i, entry in enumerate(all_entries, 1):
        entry_id = entry.get("id")
        if entry_id is None:
            failed += 1
            continue

        if client.delete_entry(entry_id):
            success += 1
        else:
            failed += 1

        if i % 20 == 0 or i == len(all_entries):
            print(
                f"[INFO] Processed {i}/{len(all_entries)} (success: {success}, failed: {failed})"
            )
        time.sleep(0.1)

    print(f"[INFO] Done. Deleted: {success}, Failed: {failed}")
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified Upfluence scraper tool")
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Command to execute"
    )

    # Common arguments
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--filters",
        type=str,
        default=DEFAULT_FILTERS_FILE,
        help=f"Filters JSON file (default: {DEFAULT_FILTERS_FILE})",
    )
    common_parser.add_argument(
        "--list-id", type=str, help="Override list ID from filters"
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search", parents=[common_parser], help="Search for influencers and save to CSV"
    )
    search_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_upfluence_influencers.csv",
        help="Output CSV file path",
    )
    search_parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing output file instead of overwriting",
    )
    search_parser.add_argument(
        "-l", "--limit", type=int, help="Max number of influencers to process"
    )
    search_parser.add_argument(
        "--per-page", type=int, default=PER_PAGE, help="Matches per page"
    )
    search_parser.add_argument(
        "--keywords", type=str, help="Comma-separated keywords to search for"
    )
    search_parser.set_defaults(func=command_search)

    # Export command
    export_parser = subparsers.add_parser(
        "export", parents=[common_parser], help="Export all influencer contacts to CSV"
    )
    export_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="upfluence_contacts.csv",
        help="Output CSV file path",
    )
    export_parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing output file instead of overwriting",
    )
    export_parser.add_argument(
        "-w", "--workers", type=int, default=64, help="Concurrent workers for unlock"
    )
    export_parser.add_argument(
        "-l", "--limit", type=int, help="Limit to first N influencers"
    )
    export_parser.add_argument(
        "--per-page", type=int, default=PER_PAGE, help="Matches per page"
    )
    export_parser.set_defaults(func=command_export)

    # Remove command
    remove_parser = subparsers.add_parser(
        "remove", parents=[common_parser], help="Remove influencers from community list"
    )
    remove_parser.add_argument(
        "--from-file",
        type=str,
        help="CSV file with list_entry_id,influencer_id columns",
    )
    remove_parser.add_argument(
        "--dry-run", action="store_true", help="Only list, do not remove"
    )
    remove_parser.set_defaults(func=command_remove)

    # Cleanup command
    cleanup_parser = subparsers.add_parser(
        "cleanup", parents=[common_parser], help="Delete list entries permanently"
    )
    cleanup_parser.add_argument(
        "--status",
        type=str,
        default="selected,rejected",
        help="Comma-separated statuses to delete",
    )
    cleanup_parser.add_argument(
        "--dry-run", action="store_true", help="Only list, do not delete"
    )
    cleanup_parser.set_defaults(func=command_cleanup)

    args = parser.parse_args()

    if not os.environ.get("UPFLUENCE_BEARER_TOKEN"):
        print("[ERROR] UPFLUENCE_BEARER_TOKEN environment variable not set")
        print('  export UPFLUENCE_BEARER_TOKEN="your_token"')
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
