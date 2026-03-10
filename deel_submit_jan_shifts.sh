#!/usr/bin/env bash
# Submit 8h shifts for all business days in January 2026 for both Deel contracts.
# Requires a config file with cookies and auth token per contract (see deel_jan_shifts.conf.example).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/deel_jan_shifts.conf"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Missing config: ${CONFIG_FILE}" >&2
  echo "Copy deel_jan_shifts.conf.example to deel_jan_shifts.conf and fill in cookies and x-auth-token for each contract." >&2
  exit 1
fi

source "$CONFIG_FILE"

for var in CONTRACT_1_ID CONTRACT_1_COOKIES CONTRACT_1_AUTH CONTRACT_2_ID CONTRACT_2_COOKIES CONTRACT_2_AUTH; do
  if [[ -z "${!var:-}" ]]; then
    echo "Missing ${var} in ${CONFIG_FILE}" >&2
    exit 1
  fi
done

BUSINESS_DAYS=(01 02 05 06 07 08 09 12 13 14 15 16 19 20 21 22 23 26 27 28 29 30)

submit_shift() {
  local contract_id=$1
  local cookies=$2
  local auth=$3
  local day=$4
  echo "=== 2026-01-${day} contract ${contract_id} ==="
  curl -s -w "\nHTTP %{http_code}\n" 'https://app.deel.com/deelapi/time_tracking/time_sheets/shifts' \
    -H 'accept: application/json, text/plain, */*' \
    -H 'accept-language: en;q=0.6' \
    -H 'content-type: application/json' \
    -b "$cookies" \
    -H "x-auth-token: $auth" \
    -H 'origin: https://app.deel.com' \
    -H 'referer: https://app.deel.com/time-attendance/'"${contract_id}"'?contractId='"${contract_id}" \
    -H 'sec-ch-ua: "Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "macOS"' \
    -H 'sec-fetch-dest: empty' \
    -H 'sec-fetch-mode: cors' \
    -H 'sec-fetch-site: same-origin' \
    -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36' \
    -H 'x-api-version: 2' \
    -H 'x-app-host: app.deel.com' \
    -H 'x-owner: time-tracking' \
    -H 'x-platform: web' \
    -H "x-react-pathname: /time-attendance/${contract_id}" \
    --data-raw '{"contractOid":"'"${contract_id}"'","start":"2026-01-'"${day}"'T00:00:00.000Z","totalWorkedHours":8,"description":"","type":"BULK","submitType":"BULK","hourlyReportPresetId":"default","isAutoApproved":false,"origin":"PLATFORM","workLocation":null,"workLocationEntityAddressId":null,"shiftType":"UNSPECIFIED","isForecastEdit":false}'
}

for day in "${BUSINESS_DAYS[@]}"; do
  submit_shift "$CONTRACT_1_ID" "$CONTRACT_1_COOKIES" "$CONTRACT_1_AUTH" "$day"
  submit_shift "$CONTRACT_2_ID" "$CONTRACT_2_COOKIES" "$CONTRACT_2_AUTH" "$day"
done

echo "Done. 22 days × 2 contracts = 44 shifts submitted."
