#!/usr/bin/env python3
"""
Export Upfluence/Wednesday influencer contacts to CSV.

Lists all matches from the facade API, unlocks each influencer for full details,
and exports all influencer fields to CSV (id, name, email, categories, etc.).
Complex fields (location, categories, processed_features) are stored as JSON.

Usage:
    export UPFLUENCE_BEARER_TOKEN="your_token"
    uv run python upfluence_export_contacts.py [--output contacts.csv] [--workers 64] [--limit N]
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://facade.upfluence.co/api/v1"
DEFAULT_OUTPUT = "upfluence_contacts.csv"
DEFAULT_LOG_FILE = "upfluence_export.log"
PER_PAGE = 100
POOL_SIZE = 64

# Exact filtering from Upfluence/Wednesday matches API
DEFAULT_SEARCH_BODY = {
    "current_list": "374837",
    "criterias": [
        {"value": "Fintech", "weight": 1, "field": "all", "type": "should"},
        {"value": "APIs", "weight": 1, "field": "all", "type": "should"},
        {"value": "Trading", "weight": 1, "field": "all", "type": "should"},
        {"value": "Developers", "weight": 1, "field": "all", "type": "should"},
        {"value": "Markets", "weight": 1, "field": "all", "type": "should"},
        {"value": "entrepreneur", "weight": 1, "field": "all", "type": "should"},
        {"value": "stock", "weight": 1, "field": "influencer.hashtags", "type": "should"},
        {"value": "software", "weight": 1, "field": "all", "type": "should"},
        {"value": "polygon", "weight": 1, "field": "all", "type": "must_not"},
    ],
    "filters": [
        {"value": "5", "type": "float", "slug": "youtubeEngagementRateGrowth", "name": "youtube.engagement_growth_rate", "order": ">", "isPercent": True},
        {"value": "5", "type": "float", "slug": "youtubeCommunityRateGrowth", "name": "youtube.community_growth_rate", "order": ">", "isPercent": True},
        {"value": "5", "type": "float", "slug": "twitterCommunityRateGrowth", "name": "twitter.community_growth_rate", "order": ">", "isPercent": True},
        {"value": {"from": 5000, "to": ""}, "type": "range-int", "slug": "twitterFollowers", "name": "twitter.followers"},
        {"value": {"from": 25000, "to": ""}, "type": "range-int", "slug": "youtubeFollowers", "name": "youtube.followers"},
        {"value": ["en"], "type": "multi-string", "slug": "lg", "name": "influencer.lang"},
        {"value": {"from": "50000", "to": None}, "type": "range-int", "slug": "tiktokFollowers", "name": "tiktok.followers"},
        {"value": "5", "type": "average-engagement", "slug": "tiktokAverageEngagements", "name": "tiktok", "isPercent": True, "order": ">"},
        {"value": "5", "type": "float", "slug": "tiktokEngagementRateGrowth", "name": "tiktok.engagement_growth_rate", "order": ">", "isPercent": True},
        {"value": "5", "type": "float", "slug": "tiktokCommunityRateGrowth", "name": "tiktok.community_growth_rate", "order": ">", "isPercent": True},
        {"value": {"from": "50000", "to": None}, "type": "range-int", "slug": "instagramFollowers", "name": "instagram.followers"},
        {"value": 5, "type": "average-engagement", "slug": "instagramAverageEngagements", "name": "instagram", "isPercent": True, "order": ">"},
        {"value": "2", "type": "float", "slug": "instagramEngagementRateGrowth", "name": "instagram.engagement_growth_rate", "order": ">", "isPercent": True},
        {"value": "2", "type": "float", "slug": "instagramCommunityRateGrowth", "name": "instagram.community_growth_rate", "order": ">", "isPercent": True},
    ],
    "audience_filters": [],
    "social_media_matching_operator": "or",
    "should_save": True,
    "track_hits_results": 10000,
    "score_model": "default",
    "premade_search": None,
}

logger = logging.getLogger("upfluence_export")


def get_headers(token: str) -> dict[str, str]:
    return {
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://hq.wednesday.app",
        "Referer": "https://hq.wednesday.app/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "authorization": f"Bearer {token}",
    }


def _log_response(resp: requests.Response, context: str) -> None:
    """Log full request/response for debugging."""
    try:
        body = resp.text
        if len(body) > 50000:
            body = body[:50000] + f"\n... [truncated, total {len(resp.text)} chars]"
    except Exception:
        body = "[unable to read body]"
    # Redact auth header
    req_headers = dict(resp.request.headers)
    if "Authorization" in req_headers:
        req_headers["Authorization"] = "Bearer ***"
    if "authorization" in req_headers:
        req_headers["authorization"] = "Bearer ***"
    logger.info(
        "--- %s ---\nREQUEST: %s %s\nRequest headers: %s\nRequest body: %s\nRESPONSE: status=%s\nResponse headers: %s\nResponse body: %s",
        context,
        resp.request.method,
        resp.url,
        req_headers,
        (resp.request.body or b"").decode("utf-8", errors="replace")[:2000],
        resp.status_code,
        dict(resp.headers),
        body,
    )


def fetch_matches(
    session: requests.Session,
    token: str,
    page: int = 1,
    per_page: int = PER_PAGE,
    search_body: dict | None = None,
) -> tuple[list[dict], int, int]:
    """Fetch one page of matches. Returns (matches, total_count, total_pages)."""
    url = f"{BASE_URL}/matches"
    # API may reject offset > 1000; omit offset for high pages
    offset = (page - 1) * per_page
    params: dict[str, int] = {"page": page, "per_page": per_page}
    if offset <= 1000:
        params["offset"] = offset
    body = search_body or DEFAULT_SEARCH_BODY
    try:
        resp = session.post(
            url,
            params=params,
            json=body,
            headers=get_headers(token),
            timeout=60,
        )
        _log_response(resp, f"matches page={page}")
        resp.raise_for_status()
        data = resp.json()

        matches = data.get("matches") or data.get("data") or data.get("hits") or []
        meta = data.get("meta") or {}
        total = int(meta.get("total", 0)) or data.get("total") or data.get("total_count") or len(matches)
        total_pages = int(meta.get("totalPages", 0)) or max(1, (total + per_page - 1) // per_page)
        return matches, total, total_pages
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 400:
            logger.warning("matches API 400 at page %s (offset limit?), stopping pagination", page)
            return [], 0, page - 1
        raise
    except Exception:
        return [], 0, page - 1


def get_influencer_ids(matches: list[dict]) -> list[int]:
    """Extract influencer IDs from match objects."""
    ids = []
    for m in matches:
        iid = m.get("id") or m.get("influencer_id") or m.get("influencer", {}).get("id")
        if iid is not None:
            ids.append(int(iid))
    return ids


def unlock_influencer(
    session: requests.Session,
    token: str,
    influencer_id: int,
) -> dict | None:
    """Unlock an influencer and return the full influencer object."""
    url = f"{BASE_URL}/influencers/{influencer_id}/unlock"
    resp = session.put(url, headers=get_headers(token), timeout=30)
    _log_response(resp, f"unlock influencer_id={influencer_id}")
    if resp.status_code != 200:
        return None
    data = resp.json()
    return data.get("influencer") or data


def _unlock_task(influencer_id: int, token: str) -> tuple[int, dict | None]:
    """Thread-safe unlock task; uses its own session per worker."""
    session = requests.Session()
    try:
        inf = unlock_influencer(session, token, influencer_id)
        return (influencer_id, inf)
    finally:
        session.close()


def _serialize_value(val: object) -> str:
    """Convert any value to CSV-safe string. Complex types stored as JSON."""
    if val is None:
        return ""
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, list):
        return json.dumps(val)
    if isinstance(val, dict):
        return json.dumps(val)
    return str(val).replace("\n", " ").replace("\r", "")


def extract_row(influencer: dict) -> dict[str, str]:
    """Extract all fields from influencer, safe for CSV."""
    return {key: _serialize_value(val) for key, val in influencer.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Upfluence contacts to CSV")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path(DEFAULT_OUTPUT),
        help=f"Output CSV path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=POOL_SIZE,
        help=f"Concurrent workers for unlock (default: {POOL_SIZE})",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=None,
        help="Limit to first N influencers (for testing)",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path(DEFAULT_LOG_FILE),
        help=f"Log file for API requests/responses (default: {DEFAULT_LOG_FILE})",
    )
    args = parser.parse_args()
    output_path = args.output

    # Configure logging to file
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    fh = logging.FileHandler(args.log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(fh)
    logger.info("=== Upfluence export started ===")

    token = os.environ.get("UPFLUENCE_BEARER_TOKEN")
    if not token:
        print("Error: Set UPFLUENCE_BEARER_TOKEN environment variable.", file=sys.stderr)
        return 1

    session = requests.Session()
    all_ids: set[int] = set()
    page = 1

    print("Fetching matches...")
    total_matched = 0
    total_pages = 1
    while page <= total_pages:
        matches, total_matched, total_pages = fetch_matches(session, token, page=page)
        ids = get_influencer_ids(matches)
        if not ids:
            break
        all_ids.update(ids)
        print(f"  Page {page}/{total_pages}: {len(ids)} matches (collected: {len(all_ids)} / total: {total_matched})")
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.2)

    print(f"\n  Total matched in search: {total_matched}")
    ids_list = sorted(all_ids)
    if args.limit is not None:
        ids_list = ids_list[: args.limit]
        print(f"  Limited to first {len(ids_list)} influencers")
    workers = args.workers
    print(f"\nUnlocking {len(ids_list)} influencers with {workers} workers...")

    results: dict[int, dict[str, str]] = {}
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_unlock_task, iid, token): iid for iid in ids_list}
        for future in as_completed(futures):
            iid, inf = future.result()
            if inf:
                results[iid] = extract_row(inf)
            else:
                results[iid] = {"id": str(iid)}
            done += 1
            if done % 50 == 0 or done == len(ids_list):
                print(f"  Unlocked {done}/{len(ids_list)}")

    rows = [results[iid] for iid in ids_list]
    all_keys = sorted(set().union(*(r.keys() for r in rows)))
    if "id" in all_keys:
        all_keys = ["id"] + [k for k in all_keys if k != "id"]
    for row in rows:
        for k in all_keys:
            row.setdefault(k, "")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nExported {len(rows)} contacts to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
