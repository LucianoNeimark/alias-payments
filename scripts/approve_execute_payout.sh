#!/usr/bin/env bash
# After MCP tool `request_payment` creates a payment request:
#   1. Approve it (reserves funds, enqueues payout).
#   2. Resolve the queued payout id.
#   3. Execute payout (calls MP transfer service when PAYMENTS_* is set on the API).
#
# Uses the same env as the MCP client: AGENTPAY_API_URL, AGENTPAY_API_KEY.
#
# Local: Alias Payments API (e.g. uvicorn on :8003). MP transfer service uses PAYMENTS_SERVICE_* in .env (e.g. :8002).
#   set -a && source .env && set +a
#   export AGENTPAY_API_URL=http://127.0.0.1:8003
#   ./scripts/approve_execute_payout.sh <user_uuid> <payment_request_uuid>

set -euo pipefail

BASE="${AGENTPAY_API_URL:-http://127.0.0.1:8003}"
KEY="${AGENTPAY_API_KEY:-}"
USER_ID="${1:?usage: $0 <user_id> <payment_request_id>}"
PR_ID="${2:?usage: $0 <user_id> <payment_request_id>}"

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

echo "Approving payment request $PR_ID (POST $BASE) ..."
_code=$(curl -sS -o /tmp/appr_body -w "%{http_code}" "${HDR[@]}" -X POST \
  "$BASE/payment-requests/$PR_ID/approve" -d "{\"user_id\": \"$USER_ID\"}")
_json_body "$(cat /tmp/appr_body)"
[[ "$_code" =~ ^2 ]] || {
  echo "approve failed HTTP $_code" >&2
  exit 1
}

echo
echo "Resolving queued payout ..."
PAYOUT_ID="$(
  _code=$(curl -sS -o /tmp/po_list -w "%{http_code}" "${HDR[@]}" \
    "$BASE/payouts/?payment_request_id=$PR_ID")
  [[ "$_code" =~ ^2 ]] || {
    echo "list payouts failed HTTP $_code" >&2
    cat /tmp/po_list >&2
    exit 1
  }
  python3 -c "
import json, sys
rows = json.load(open('/tmp/po_list'))
queued = [r for r in rows if r.get('status') == 'queued']
pick = queued[0] if queued else (rows[0] if rows else None)
if not pick:
    sys.exit('no payout for this payment_request_id')
print(pick['id'])
"
)"

echo "Executing payout $PAYOUT_ID (may take 10–60s) ..."
_code=$(curl -sS -o /tmp/ex_body -w "%{http_code}" "${HDR[@]}" -X POST \
  "$BASE/payouts/$PAYOUT_ID/execute")
_json_body "$(cat /tmp/ex_body)"
[[ "$_code" =~ ^2 ]] || {
  echo "execute failed HTTP $_code" >&2
  exit 1
}
