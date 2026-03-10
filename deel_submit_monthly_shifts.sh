#!/usr/bin/env bash
# Submit 8h shifts for all business days of the CURRENT month.
# Run: ./deel_submit_monthly_shifts.sh
#
# Requires deel_shifts.conf with COOKIES and X_AUTH_TOKEN (see deel_shifts.conf.example).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/deel_shifts.conf"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Missing config: ${CONFIG_FILE}" >&2
  echo "Copy deel_shifts.conf.example to deel_shifts.conf and fill in cookies and x-auth-token." >&2
  exit 1
fi

source "$CONFIG_FILE"

for var in CONTRACT_ID COOKIES X_AUTH_TOKEN; do
  if [[ -z "${!var:-}" ]]; then
    echo "Missing ${var} in ${CONFIG_FILE}" >&2
    exit 1
  fi
done

YEAR=$(date +%Y)
MONTH=$(date +%m)

# Last day of current month (macOS: -v+1m -v-1d; Linux: -d "last day")
LAST_DAY=$(date -j -v+1m -v-1d -f "%Y-%m-%d" "${YEAR}-${MONTH}-01" +%d 2>/dev/null) \
  || LAST_DAY=$(date -d "${YEAR}-${MONTH}-01 +1 month -1 day" +%d 2>/dev/null) \
  || LAST_DAY=31

# Compute business days (Mon–Fri) for current month
BUSINESS_DAYS=()
for d in $(seq -w 1 "$LAST_DAY"); do
  dow=$(date -j -f "%Y-%m-%d" "${YEAR}-${MONTH}-${d}" +%u 2>/dev/null) \
    || dow=$(date -d "${YEAR}-${MONTH}-${d}" +%u 2>/dev/null)
  [[ -n "$dow" && "$dow" -le 5 ]] && BUSINESS_DAYS+=("$d")
done

submit_shift() {
  local day=$1
  echo "Submitting ${YEAR}-${MONTH}-${day} (8h)..."
  curl -s -w "\nHTTP %{http_code}\n" 'https://app.deel.com/deelapi/time_tracking/time_sheets/shifts' \
    -H 'accept: application/json, text/plain, */*' \
    -H 'accept-language: en;q=0.6' \
    -H 'content-type: application/json' \
    -b "$COOKIES" \
    -H "x-auth-token: $X_AUTH_TOKEN" \
    -H 'origin: https://app.deel.com' \
    -H "referer: https://app.deel.com/time-attendance/${CONTRACT_ID}?contractId=${CONTRACT_ID}" \
    -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36' \
    -H 'x-api-version: 2' \
    -H 'x-app-host: app.deel.com' \
    -H 'x-owner: time-tracking' \
    -H 'x-platform: web' \
    --data-raw '{"contractOid":"'"${CONTRACT_ID}"'","start":"'"${YEAR}-${MONTH}-${day}"'T00:00:00.000Z","totalWorkedHours":8,"description":"","type":"BULK","submitType":"BULK","hourlyReportPresetId":"default","isAutoApproved":false,"origin":"PLATFORM","workLocation":null,"workLocationEntityAddressId":null,"shiftType":"UNSPECIFIED","isForecastEdit":false}'
  sleep 0.5
}

for day in "${BUSINESS_DAYS[@]}"; do
  submit_shift "$day"
done

echo ""
echo "Done. ${#BUSINESS_DAYS[@]} business days × 8h = $((${#BUSINESS_DAYS[@]} * 8)) hours for ${YEAR}-${MONTH}."
