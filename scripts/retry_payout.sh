#!/usr/bin/env bash
# Retry a payout that is in needs_manual_review or failed status.
#
# Usage:
#   ./scripts/retry_payout.sh <payout_id>
#
# Optionally set AGENTPAY_API_URL (default http://127.0.0.1:8003).

set -euo pipefail

BASE="${AGENTPAY_API_URL:-http://127.0.0.1:8003}"
KEY="${AGENTPAY_API_KEY:-}"
PAYOUT_ID="${1:?usage: $0 <payout_id>}"

HDR=(-H "Content-Type: application/json")
if [[ -n "$KEY" ]]; then
  HDR+=(-H "X-API-Key: $KEY")
fi

_json_body() {
  local body="$1"
  if echo "$body" | python3 -m json.tool >/dev/null 2>&1; then
    echo "$body" | python3 -m json.tool
  else
    printf '%s\n' "$body"
  fi
}

echo "Retrying payout $PAYOUT_ID (POST $BASE/payouts/$PAYOUT_ID/retry) ..."
_code=$(curl -sS -o /tmp/retry_body -w "%{http_code}" "${HDR[@]}" -X POST \
  "$BASE/payouts/$PAYOUT_ID/retry")
_json_body "$(cat /tmp/retry_body)"
if [[ ! "$_code" =~ ^2 ]]; then
  echo "retry failed HTTP $_code" >&2
  exit 1
fi
echo
echo "Done."
