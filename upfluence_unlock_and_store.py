#!/usr/bin/env python3
"""
Upfluence: clear list, fetch matches, unlock each influencer, write to CSV, remove from list.

Usage:
    UPFLUENCE_BEARER_TOKEN=token uv run python upfluence_unlock_and_store.py
    uv run python upfluence_unlock_and_store.py -l 5 --dry-run
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

import requests
from dotenv import load_dotenv

load_dotenv()

BASE = "https://facade.upfluence.co/api/v1"
DEFAULT_LIST_ID = "374837"
# Target: influencers who promote financial/trading tools, APIs, market data
DEFAULT_KEYWORDS = (
    "Fintech", "Trading", "Market data", "Stocks", "APIs", "Developers",
    "Algorithmic trading", "Quantitative finance", "Python", "Backtesting",
    "Technical analysis", "Stock market", "Day trading", "Trading education",
    "API integration", "Real-time data", "Financial API", "Trading API",
)
# Keywords with specific field (hashtags = active content creators)
DEFAULT_CRITERIAS = [
    *[{"value": v, "weight": 1, "field": "all", "type": "should"} for v in DEFAULT_KEYWORDS],
    {"value": "trading", "weight": 1, "field": "influencer.hashtags", "type": "should"},
    {"value": "stocks", "weight": 1, "field": "influencer.hashtags", "type": "should"},
]
# Multi-platform filters (OR: match any). Engagement filters prioritize active, growing audiences.
DEFAULT_FILTERS = [
    # Follower ranges
    {"value": {"from": 10000, "to": 500000}, "type": "range-int", "slug": "youtubeFollowers", "name": "youtube.followers"},
    {"value": {"from": 5000, "to": 200000}, "type": "range-int", "slug": "twitterFollowers", "name": "twitter.followers"},
    {"value": {"from": 3000, "to": 150000}, "type": "range-int", "slug": "instagramFollowers", "name": "instagram.followers"},
    {"value": {"from": 10000, "to": 300000}, "type": "range-int", "slug": "tiktokFollowers", "name": "tiktok.followers"},
    # Language
    {"value": ["en"], "type": "multi-string", "slug": "lg", "name": "influencer.lang"},
    # Engagement growth (growing reach = relevant audience)
    {"value": "3", "type": "float", "slug": "youtubeEngagementRateGrowth", "name": "youtube.engagement_growth_rate", "order": ">", "isPercent": True},
    {"value": "3", "type": "float", "slug": "youtubeCommunityRateGrowth", "name": "youtube.community_growth_rate", "order": ">", "isPercent": True},
    {"value": "3", "type": "float", "slug": "twitterCommunityRateGrowth", "name": "twitter.community_growth_rate", "order": ">", "isPercent": True},
    {"value": "2", "type": "float", "slug": "instagramEngagementRateGrowth", "name": "instagram.engagement_growth_rate", "order": ">", "isPercent": True},
    {"value": "2", "type": "float", "slug": "instagramCommunityRateGrowth", "name": "instagram.community_growth_rate", "order": ">", "isPercent": True},
    # Average engagement (min 3% = active audience, not bots)
    {"value": 3, "type": "average-engagement", "slug": "instagramAverageEngagements", "name": "instagram", "isPercent": True, "order": ">"},
    {"value": "3", "type": "average-engagement", "slug": "tiktokAverageEngagements", "name": "tiktok", "isPercent": True, "order": ">"},
]


def build_search(list_id: str, keywords: tuple[str, ...] | None = None) -> dict:
    if keywords:
        criterias = [{"value": v, "weight": 1, "field": "all", "type": "should"} for v in keywords]
    else:
        criterias = DEFAULT_CRITERIAS
    return {
        "current_list": list_id,
        "criterias": criterias,
        "filters": DEFAULT_FILTERS,
        "audience_filters": [],
        "social_media_matching_operator": "or",
        "should_save": True,
        "track_hits_results": 10000,
        "score_model": "default",
        "premade_search": None,
    }

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://hq.wednesday.app",
    "Referer": "https://hq.wednesday.app/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}


def log(level: str, msg: str, **kw) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    extra = " | ".join(f"{k}={v}" for k, v in kw.items()) if kw else ""
    print(f"[{ts}] [{level:5}] {msg}" + (f" | {extra}" if extra else ""), flush=True)


def log_section(title: str) -> None:
    print(f"\n{'─' * 60}\n  {title}\n{'─' * 60}", flush=True)


def log_response(resp: requests.Response | None, context: str = "") -> None:
    """Log response body on failure. Truncate if too long."""
    if resp is None:
        return
    try:
        body = resp.text
        try:
            parsed = json.loads(resp.text)
            body = json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            pass
        if len(body) > 2000:
            body = body[:2000] + f"... [truncated, total {len(resp.text)} chars]"
        log("WARN", f"Response body {context}", status=resp.status_code)
        print(f"  {body}", flush=True)
    except Exception as e:
        log("WARN", f"Could not log response: {e}")


def h(token: str) -> dict:
    return {**HEADERS, "Authorization": f"Bearer {token}"}


def list_entries(session: requests.Session, token: str, list_id: str, per_page: int,
                 status: str = "selected", page: int = 1) -> tuple[list[dict], int, int]:
    r = session.get(f"{BASE}/list_entries", params={"list_id": list_id, "page": page, "per_page": per_page, "status": status},
                    headers=h(token), timeout=60)
    if not r.ok:
        log_response(r, "list_entries")
        r.raise_for_status()
    d = r.json()
    entries = d.get("list_entries") or []
    m = d.get("meta") or {}
    total = int(m.get("total", 0))
    tp = int(m.get("total_pages", 0)) or max(1, (total + per_page - 1) // per_page)
    return entries, total, tp


def reject(session: requests.Session, token: str, list_id: str, entry_id: int, inf_id: int) -> bool:
    r = session.put(f"{BASE}/list_entries/{entry_id}", json={
        "list_entry": {"status": "rejected", "list_id": list_id, "influencer_id": str(inf_id)}
    }, headers=h(token), timeout=30)
    if not r.ok:
        log_response(r, f"reject entry_id={entry_id} inf_id={inf_id}")
    return r.status_code == 200


def matches(session: requests.Session, token: str, page: int, search: dict, per_page: int) -> tuple[list[dict], int, int]:
    params = {"page": page, "per_page": per_page}
    if (page - 1) * per_page <= 1000:
        params["offset"] = (page - 1) * per_page
    try:
        r = session.post(f"{BASE}/matches", params=params, json=search, headers=h(token), timeout=60)
        r.raise_for_status()
        d = r.json()
        items = d.get("matches") or d.get("data") or d.get("hits") or []
        m = d.get("meta") or {}
        total = int(m.get("total", 0)) or d.get("total") or d.get("total_count") or len(items)
        tp = int(m.get("totalPages", 0)) or max(1, (total + per_page - 1) // per_page)
        return items, total, tp
    except requests.HTTPError as e:
        if e.response:
            log_response(e.response, f"matches page={page}")
            if e.response.status_code == 400:
                log("WARN", "Matches API 400 (pagination limit?), stopping", page=page)
                return [], 0, page - 1
            if e.response.status_code == 402:
                log("ERROR", "402 Payment Required - check Upfluence subscription/billing/plan limits")
                return [], 0, page - 1
        raise
    except Exception as ex:
        log("WARN", "Matches API error", page=page, error=str(ex)[:100])
        return [], 0, page - 1


def unlock(session: requests.Session, token: str, inf_id: int) -> dict | None:
    r = session.put(f"{BASE}/influencers/{inf_id}/unlock", headers=h(token), timeout=30)
    if r.status_code != 200:
        log_response(r, f"unlock inf_id={inf_id}")
        return None
    return r.json().get("influencer") or r.json()


def entry_id(inf: dict, session: requests.Session, token: str, list_id: str, inf_id: int) -> int | None:
    raw = inf.get("list_entry_ids")
    if raw is not None:
        if isinstance(raw, list) and raw:
            x = raw[0]
            return x.get("id") if isinstance(x, dict) else int(x)
        try:
            return int(raw)
        except (ValueError, TypeError):
            pass
        if isinstance(raw, str):
            try:
                p = json.loads(raw)
                return int(p[0]) if isinstance(p, list) and p else int(p)
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
    for e in list_entries(session, token, list_id, 100, "selected", 1)[0]:
        if e.get("influencer_id") == inf_id:
            return e.get("id")
    return None


def to_row(d: dict) -> dict[str, str]:
    def cell(v):
        if v is None: return ""
        if isinstance(v, bool): return "true" if v else "false"
        if isinstance(v, (int, float)): return str(v)
        if isinstance(v, (list, dict)): return json.dumps(v)
        return str(v).replace("\n", " ").replace("\r", "")
    return {k: cell(v) for k, v in d.items()}


def main() -> int:
    p = argparse.ArgumentParser(
        description="Upfluence: clear list, fetch matches, unlock influencers, write CSV, remove from list.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("-o", "--output", type=Path,
                   default=Path(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_upfluence_influencers.csv"),
                   help="Output CSV file path (default: timestamp_upfluence_influencers.csv)")
    p.add_argument("-l", "--limit", type=int, default=None,
                   help="Max number of influencers to process (default: unlimited)")
    p.add_argument("-w", "--workers", type=int, default=1,
                   help="Parallel workers (use 1 if you hit community_limit/402 - list has size cap)")
    p.add_argument("--list-id", type=str, default=DEFAULT_LIST_ID,
                   help="Upfluence list ID to use")
    p.add_argument("-k", "--keywords", type=str, nargs="*", default=None,
                   help="Search keywords (default: fintech, APIs, trading, etc.)")
    p.add_argument("--per-page", type=int, default=100,
                   help="Matches per page")
    p.add_argument("--dry-run", action="store_true",
                   help="Only clear list, do not fetch or process matches")
    p.add_argument("--skip-clear", action="store_true",
                   help="Skip Phase 1 (clearing list)")
    a = p.parse_args()

    list_id = a.list_id
    keywords = tuple(a.keywords) if a.keywords else None  # None = use DEFAULT_CRITERIAS
    search = build_search(list_id, keywords)
    per_page = a.per_page

    token = os.environ.get("UPFLUENCE_BEARER_TOKEN")
    if not token:
        log("ERROR", "UPFLUENCE_BEARER_TOKEN not set")
        return 1

    s = requests.Session()
    t0 = time.time()

    log_section("Upfluence Unlock & Store")
    kw_preview = "default (trading, APIs, market data, ...)" if not keywords else ", ".join(keywords[:5]) + ("..." if len(keywords) > 5 else "")
    log("INFO", "Config", output=str(a.output), workers=a.workers, limit=a.limit or "unlimited", keywords=kw_preview)
    log("INFO", "List", list_id=list_id)

    # Phase 1: Clear list
    if not a.skip_clear:
        log_section("Phase 1: Clear list")
        page, tp, n = 1, 1, 0
        try:
            while page <= tp:
                entries, total, tp = list_entries(s, token, list_id, per_page, "selected", page)
                log("INFO", "Fetched list entries", page=f"{page}/{tp}", entries=len(entries), total=total)
                for i, e in enumerate(entries):
                    if e.get("id") and e.get("influencer_id") and not a.dry_run:
                        reject(s, token, list_id, e["id"], e["influencer_id"])
                        n += 1
                    if (i + 1) % 20 == 0 and entries:
                        log("INFO", "Rejecting...", done=n)
                    time.sleep(0.1)
                page += 1
                time.sleep(0.2)
        except requests.HTTPError as e:
            if e.response:
                log_response(e.response, "list_entries")
                if e.response.status_code == 404:
                    log("ERROR", "list_entries API 404")
                    return 1
            raise
        log("INFO", "Phase 1 complete", removed=n, elapsed=f"{time.time()-t0:.1f}s")
    else:
        log("INFO", "Phase 1: Skipped (--skip-clear)")

    if a.dry_run:
        log("INFO", "Dry run finished")
        return 0

    # Phase 2+3: Stream matches -> unlock -> write CSV -> reject
    log_section("Phase 2+3: Fetch, unlock, store, remove")
    log("INFO", "Starting", workers=a.workers, output=str(a.output))
    out = a.output
    have_header = out.exists() and out.stat().st_size
    keys: list[str] = []
    if have_header:
        with open(out, encoding="utf-8") as rf:
            keys = list(csv.DictReader(rf).fieldnames or [])
    lock = threading.Lock()
    state = {"writer": None, "keys": keys, "done": 0}

    def process(inf_id: int) -> int:
        sess = requests.Session()
        try:
            inf = unlock(sess, token, inf_id)
            if not inf:
                log("WARN", "Unlock failed", influencer_id=inf_id)
                return 0
            row = to_row(inf)
            with lock:
                w = state["writer"]
                k = state["keys"]
                if w is None:
                    k = k or sorted(row.keys())
                    if "id" in row and "id" not in k:
                        k = ["id"] + [x for x in k if x != "id"]
                    state["keys"] = k
                    state["writer"] = csv.DictWriter(f, fieldnames=k, extrasaction="ignore")
                    if not have_header:
                        state["writer"].writeheader()
                for col in state["keys"]:
                    row.setdefault(col, "")
                state["writer"].writerow(row)
                f.flush()
                state["done"] += 1
            eid = entry_id(inf, sess, token, list_id, inf_id)
            if eid:
                reject(sess, token, list_id, eid, inf_id)
            return 1
        except requests.HTTPError as ex:
            if ex.response:
                log_response(ex.response, f"process inf_id={inf_id}")
            log("WARN", "HTTP error, skipping", influencer_id=inf_id)
            return 0
        except Exception as ex:
            if hasattr(ex, "response") and getattr(ex, "response", None):
                log_response(ex.response, f"process inf_id={inf_id}")
            log("WARN", "Error, skipping", influencer_id=inf_id, error=str(ex)[:80])
            return 0

    seen: set[int] = set()
    page, tp = 1, 1

    phase_start = time.time()
    last_log_done = 0

    with open(out, "a", newline="", encoding="utf-8") as f:
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            futures = {}
            while page <= tp:
                items, total, tp = matches(s, token, page, search, per_page)
                if items:
                    log("INFO", "Matches", page=f"{page}/{tp}", items=len(items), total=total)
                for m in items:
                    iid = m.get("id") or m.get("influencer_id") or (m.get("influencer") or {}).get("id")
                    if not iid or iid in seen:
                        continue
                    if a.limit and len(seen) >= a.limit:
                        break
                    seen.add(iid)
                    futures[ex.submit(process, int(iid))] = iid
                page += 1
                time.sleep(0.2)
                if a.limit and len(seen) >= a.limit:
                    break

            total_tasks = len(futures)
            for future in as_completed(futures):
                done = state["done"]
                if done > 0 and done >= last_log_done + 5:
                    last_log_done = done
                    el = time.time() - phase_start
                    rate = done / el if el > 0 else 0
                    eta = (total_tasks - done) / rate if rate > 0 else 0
                    log("INFO", "Progress", done=f"{done}/{total_tasks}", rate=f"{rate:.1f}/s",
                        elapsed=f"{el:.0f}s", eta=f"{eta:.0f}s")

    elapsed = time.time() - t0
    log_section("Complete")
    log("INFO", "Finished", stored=state["done"], output=str(out), elapsed=f"{elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
