#!/usr/bin/env python3
"""Find and remove duplicate and overlapping Clockify time entries for January 2026."""

import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

WORKSPACE_ID = "62028d70696722459416193d"
USER_ID = "6936e11513651e5c016306e6"
JAN_START = "2026-01-01T00:00:00Z"
JAN_END = "2026-02-01T00:00:00Z"
BASE = "https://api.clockify.me/api/v1"


def main() -> None:
    api_key = os.environ.get("CLOCKIFY_API_KEY")
    if not api_key:
        raise SystemExit("CLOCKIFY_API_KEY not set in .env")

    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

    # Fetch all time entries for January 2026
    url = f"{BASE}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries"
    r = requests.get(
        url,
        headers=headers,
        params={"start": JAN_START, "end": JAN_END},
        timeout=30,
    )
    r.raise_for_status()
    entries = r.json()

    if not entries:
        print("No time entries in January 2026.")
        return

    def key(e: dict) -> tuple:
        ti = e.get("timeInterval") or {}
        return (
            ti.get("start"),
            ti.get("end"),
            e.get("projectId"),
            e.get("userId"),
        )

    def overlaps(a: dict, b: dict) -> bool:
        ti_a = a.get("timeInterval") or {}
        ti_b = b.get("timeInterval") or {}
        start_a, end_a = ti_a.get("start"), ti_a.get("end")
        start_b, end_b = ti_b.get("start"), ti_b.get("end")
        if not all([start_a, end_a, start_b, end_b]):
            return False
        return start_a < end_b and end_a > start_b

    # 1) Duplicates: same (start, end, projectId, userId) -> keep first, delete rest
    by_key: dict[tuple, list[dict]] = {}
    for e in entries:
        k = key(e)
        by_key.setdefault(k, []).append(e)

    to_delete_ids: set[str] = set()
    for k, group in by_key.items():
        if len(group) > 1:
            # Keep first (by id order), delete the rest
            group.sort(key=lambda x: x.get("id", ""))
            for dup in group[1:]:
                to_delete_ids.add(dup["id"])

    # 2) Overlaps: different keys but time ranges overlap (same user)
    # Sort by start, then for each pair check overlap; delete the second of overlapping pair
    remaining = [e for e in entries if e["id"] not in to_delete_ids]
    remaining.sort(key=lambda e: (e.get("timeInterval") or {}).get("start") or "")

    i = 0
    while i < len(remaining):
        a = remaining[i]
        j = i + 1
        while j < len(remaining):
            b = remaining[j]
            if overlaps(a, b):
                to_delete_ids.add(b["id"])
                remaining.pop(j)
                continue
            j += 1
        i += 1

    if not to_delete_ids:
        print("No duplicates or overlaps found.")
        return

    print(f"Deleting {len(to_delete_ids)} duplicate/overlapping time entry(ies):")
    for eid in sorted(to_delete_ids):
        del_url = f"{BASE}/workspaces/{WORKSPACE_ID}/time-entries/{eid}"
        resp = requests.delete(del_url, headers=headers, timeout=30)
        if resp.status_code in (200, 204):
            print(f"  Deleted {eid}")
        else:
            print(f"  Failed to delete {eid}: {resp.status_code} {resp.text[:200]}")


if __name__ == "__main__":
    main()
