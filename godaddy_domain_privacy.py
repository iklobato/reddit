#!/usr/bin/env python3
"""
GoDaddy domain privacy: show and enforce WHOIS privacy for a domain.

Uses .env: GODADDY_API_KEY, GODADDY_API_SECRET.
Usage:
  python godaddy_domain_privacy.py onetrust.global
  python godaddy_domain_privacy.py onetrust.global --ensure
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

BASE = "https://api.godaddy.com"


def load_env() -> None:
    env_file = Path(__file__).resolve().parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def get_auth() -> tuple[str, str]:
    load_env()
    key = os.environ.get("GODADDY_API_KEY")
    secret = os.environ.get("GODADDY_API_SECRET")
    if not key or not secret:
        print("Error: set GODADDY_API_KEY and GODADDY_API_SECRET in .env", file=sys.stderr)
        sys.exit(1)
    return key, secret


def get_domain(session: requests.Session, domain: str) -> dict | None:
    key, secret = get_auth()
    r = session.get(
        f"{BASE}/v1/domains/{domain}",
        headers={"Authorization": f"sso-key {key}:{secret}"},
        timeout=30,
    )
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def patch_domain(session: requests.Session, domain: str, payload: dict) -> bool:
    key, secret = get_auth()
    r = session.patch(
        f"{BASE}/v1/domains/{domain}",
        headers={
            "Authorization": f"sso-key {key}:{secret}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 204):
        return True
    if r.status_code == 400:
        try:
            err = r.json()
            print("API response:", err, file=sys.stderr)
        except Exception:
            print("Response:", r.text[:500], file=sys.stderr)
    return False


def main() -> int:
    if not requests:
        print("Install requests: uv pip install requests", file=sys.stderr)
        return 1
    parser = argparse.ArgumentParser(description="GoDaddy domain WHOIS privacy")
    parser.add_argument("domain", help="Domain name (e.g. onetrust.global)")
    parser.add_argument("--ensure", action="store_true", help="PATCH domain to ensure privacy ON, exposeWhois OFF")
    args = parser.parse_args()
    domain = args.domain.strip().lower()

    session = requests.Session()
    data = get_domain(session, domain)
    if not data:
        print(f"Domain not found or no access: {domain}")
        return 1

    privacy = data.get("privacy", False)
    expose_whois = data.get("exposeWhois", True)

    print(f"Domain: {domain}")
    print(f"  privacy (WHOIS privacy):  {privacy}")
    print(f"  exposeWhois:              {expose_whois}")
    print()

    if args.ensure:
        if privacy and not expose_whois:
            print("Privacy already correctly set. No change needed.")
            return 0
        payload = {"privacy": True, "exposeWhois": False}
        if patch_domain(session, domain, payload):
            print("Updated: privacy=true, exposeWhois=false")
        else:
            print("PATCH failed. You may need to set these in GoDaddy dashboard (see below).")
            return 1
    else:
        if not privacy or expose_whois:
            print("To enforce privacy, run: python godaddy_domain_privacy.py", domain, "--ensure")
            print("Or in GoDaddy: My Products → Domain → Manage → Privacy → enable and disable 'Expose WHOIS'.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
