#!/usr/bin/env python3
"""
Check if a domain has email configured and if mail servers are reachable.
Uses: dig (MX, A) and a quick TCP connect to SMTP port (no auth).
Usage: python check_domain_email.py <domain> [optional_email]
Example: python check_domain_email.py iktech.solutions contact@iktech.solutions
"""

import socket
import subprocess
import sys
from typing import Any


def dig(record_type: str, name: str) -> list[str]:
    """Return list of record values (e.g. MX targets or A records)."""
    try:
        out = subprocess.run(
            ["dig", "+short", record_type, name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode != 0:
            return []
        lines = [s.strip() for s in (out.stdout or "").strip().splitlines() if s.strip()]
        return lines
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def get_mx(domain: str) -> list[tuple[int, str]]:
    """Return list of (priority, host) for MX records."""
    lines = dig("MX", domain)
    result: list[tuple[int, str]] = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            try:
                prio = int(parts[0])
                host = parts[1].rstrip(".")
                result.append((prio, host))
            except ValueError:
                continue
    return sorted(result)


def get_a(host: str) -> list[str]:
    """Return list of A record IPs for host."""
    return dig("A", host)


def tcp_reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except (socket.timeout, socket.error, OSError):
        return False


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: check_domain_email.py <domain> [email_address]", file=sys.stderr)
        return 1
    domain = sys.argv[1].strip().lower()
    email = sys.argv[2].strip().lower() if len(sys.argv) > 2 else None

    print(f"Domain: {domain}")
    print()

    mx_list = get_mx(domain)
    if not mx_list:
        print("MX records: NONE — email is not configured for this domain.")
        print("To have working email, add MX records (e.g. GoDaddy Workspace or another provider).")
        return 0

    print("MX records (email configured):")
    for prio, host in mx_list:
        ips = get_a(host)
        ip_str = ", ".join(ips) if ips else "(no A records)"
        print(f"  {prio} {host}  →  {ip_str}")
    print()

    # SMTP reachability (inbound mail)
    primary_mx = mx_list[0][1]
    for port, label in [(25, "SMTP (25)"), (587, "Submission (587)")]:
        ok = tcp_reachable(primary_mx, port)
        status = "reachable" if ok else "not reachable (may be blocked or filtered)"
        print(f"  {primary_mx} port {port} ({label}): {status}")
    print()

    if email:
        local, _, check_domain = email.partition("@")
        if check_domain != domain:
            print(f"Note: {email} is for {check_domain}, not {domain}.")
        else:
            print(f"Address: {email}")
            print("  Mailbox existence cannot be verified without logging in.")
            print("  Use the GoDaddy checklist below to confirm this mailbox works.")
    else:
        print("Optional: pass an email address to get a checklist for that mailbox.")
        print("  Example: python check_domain_email.py iktech.solutions contact@iktech.solutions")

    print()
    print("--- GoDaddy: confirm mailbox is working ---")
    print("1. Go to https://www.godaddy.com → My Products → Domains.")
    print("2. Find the domain → Workspace Email / Email (or Manage).")
    print("3. Ensure the mailbox exists (e.g. contact, info, you@...) and note the password.")
    print("4. Test in webmail: https://webmail.secureserver.net (login with full email + password).")
    print("5. In your mail client use: imap.secureserver.net (993), smtp.secureserver.net (465 or 587).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
