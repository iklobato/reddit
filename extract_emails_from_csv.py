#!/usr/bin/env python3
"""Extract all unique emails from CSV files into a txt file (one per line)."""

import csv
import re
from pathlib import Path

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def find_email_column(fieldnames: list[str]) -> str | None:
    for f in fieldnames or []:
        if f and f.strip().lower() in ("email", "e-mail", "email_address"):
            return f
    return None


def main() -> int:
    csv_files = sorted(Path(".").rglob("*.csv"))
    seen: set[str] = set()
    emails: list[str] = []

    for p in csv_files:
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                col = find_email_column(reader.fieldnames or [])
                if not col:
                    continue
                for row in reader:
                    val = (row.get(col) or "").strip()
                    if val and EMAIL_RE.match(val) and val.lower() not in seen:
                        seen.add(val.lower())
                        emails.append(val)
        except Exception as e:
            print(f"Skip {p}: {e}")

    out = Path("emails.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(emails))
        if emails:
            f.write("\n")
    print(f"Extracted {len(emails)} unique emails to {out}")
    return 0


if __name__ == "__main__":
    exit(main())
