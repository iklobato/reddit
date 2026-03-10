#!/usr/bin/env python3
"""Submit billable hours to Deel. All config from .env (see .env.example)."""

import os
import sys
from datetime import date

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ.get("DEEL_API_BASE_URL", "https://api.letsdeel.com/rest/v2").rstrip("/")


def main() -> None:
    token = os.environ.get("DEEL_API_TOKEN")
    if not token:
        print("Error: DEEL_API_TOKEN is required in .env", file=sys.stderr)
        sys.exit(1)

    contract_id = os.environ.get("DEEL_CONTRACT_ID")
    date_submitted = os.environ.get("DEEL_DATE") or date.today().isoformat()
    hours = float(os.environ.get("DEEL_HOURS", "8"))
    description = os.environ.get("DEEL_DESCRIPTION", "Work as per contract")
    auto_approve = os.environ.get("DEEL_AUTO_APPROVE", "").lower() in ("1", "true", "yes")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    if not contract_id:
        r = requests.get(
            f"{BASE_URL}/contracts",
            headers=headers,
            params={"statuses": "active", "limit": 50},
            timeout=30,
        )
        r.raise_for_status()
        contracts = r.json().get("data") or []
        if not contracts:
            print("Error: No active contracts and DEEL_CONTRACT_ID not set.", file=sys.stderr)
            sys.exit(1)
        contract_id = contracts[0]["id"]

    r = requests.post(
        f"{BASE_URL}/timesheets",
        headers=headers,
        json={
            "data": {
                "contract_id": contract_id,
                "date_submitted": date_submitted,
                "quantity": hours,
                "description": description,
                "is_auto_approved": auto_approve,
            }
        },
        timeout=30,
    )
    r.raise_for_status()

    data = r.json().get("data", {})
    print(f"Created: {data.get('id')} — {date_submitted} ({hours}h) {data.get('status', '')}")


if __name__ == "__main__":
    main()
