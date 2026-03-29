# Alias Payments

FastAPI skeleton for payment-related APIs.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file (or export variables) with your Supabase project credentials:

- `SUPABASE_URL` — project URL
- `SUPABASE_KEY` — service role or anon key (use the key that matches your RLS policies)

## Run

```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API docs.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/register` | Register user (creates wallet automatically) |
| GET | `/users/` | List users |
| GET | `/users/{user_id}` | Get user by id |
| GET | `/users/by-auth/{auth_provider_user_id}` | Get user by auth provider id |
| PATCH | `/users/{user_id}/status` | Update user status |
| POST | `/agents/` | Create agent (linked to a user) |
| GET | `/agents/?user_id=` | List agents for a user |
| GET | `/agents/{agent_id}` | Get agent |
| PATCH | `/agents/{agent_id}` | Update agent |
| GET | `/wallets/{user_id}` | Get wallet (available + reserved balance) |
| POST | `/funding-orders/` | Create funding order (provisions CVU via Talo) |
| GET | `/funding-orders/?user_id=` | List funding orders |
| GET | `/funding-orders/{order_id}` | Get funding order |
| POST | `/webhooks/talo` | Receive Talo webhook (idempotent) |
| POST | `/payment-requests/` | Create payment request (idempotent via `idempotency_key`) |
| GET | `/payment-requests/?user_id=` | List payment requests for a user |
| GET | `/payment-requests/{id}` | Get payment request |
| POST | `/payment-requests/{id}/approve` | Approve, reserve funds, enqueue payout |
| POST | `/payment-requests/{id}/reject` | Reject payment request |
| GET | `/payment-requests/{id}/approvals` | List approval decisions |
| GET | `/payouts/` | List payouts (optional `payment_request_id` filter) |
| GET | `/payouts/{id}` | Get payout |
| POST | `/payouts/{id}/execute` | Run bank executor (mock); headers `X-Mock-Failure`, `X-Mock-Manual-Review` |
| GET | `/ledger/{wallet_id}` | Ledger history for a wallet |

### Dashboard auth (Supabase JWT)

When `AGENTPAY_API_KEY` is set, requests must send **`X-API-Key`** (MCP/agents) **or** a valid
**`Authorization: Bearer <access_token>`** from Supabase Auth (dashboard).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/me` | Current user, wallet, agents, recent activity |
| GET | `/me/stats` | Aggregated counts for widgets |
| GET | `/me/activity` | Recent payment requests + payouts |
| GET | `/me/payment-requests` | List (optional `status` query) |
| GET | `/me/payment-requests/{id}` | Get one (owner only) |
| GET | `/me/payment-requests/{id}/approvals` | Approval history |
| POST | `/me/payment-requests/{id}/approve` | Approve (body optional `approved_amount`, `decision_reason`) |
| POST | `/me/payment-requests/{id}/reject` | Reject |
| GET | `/me/agents` | List agents |
| PATCH | `/me/agents/{id}` | Update agent (owner only) |
| GET | `/me/payouts` | List payouts for your requests |
| POST | `/me/payouts/{id}/retry` | Retry payout (owner only) |
| GET | `/me/funding-orders` | List funding orders |
| GET | `/me/ledger` | Ledger for your wallet |

Set **`SUPABASE_JWT_SECRET`** (Supabase → Settings → API → JWT) so the API can verify user tokens.
Set **`DASHBOARD_CORS_ORIGINS`** (comma-separated) for the Next.js app origin(s).

## User dashboard (Next.js)

The `dashboard/` app is a separate Next.js 14 UI:

```bash
cd dashboard
cp .env.local.example .env.local
# set NEXT_PUBLIC_SUPABASE_* and NEXT_PUBLIC_API_URL
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Sign in with Supabase Auth; the app user must exist
(`POST /users/register` with `auth_provider_user_id` = Supabase user id).

## Layout

- `app/main.py` — FastAPI app and router registration
- `app/config.py` / `app/database.py` — settings and Supabase client
- `app/schemas/` — Pydantic request/response models
- `app/repositories/` — Supabase table access
- `app/api/routers/` — HTTP routes  
- `dashboard/` — Next.js operator dashboard (Supabase Auth + `/me` API)
- `app/services/` — domain services
- `mcp/` — MCP server (see below)

---

## MCP Server

A hosted MCP server that exposes AgentPay tools to AI agents over HTTP using the [Streamable HTTP transport](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http).

### Tools

| Tool | Description |
|------|-------------|
| `get_balance` | Query available and reserved balance for a user's wallet |
| `request_payment` | Create a payment request to a destination CVU |
| `get_payment_request` | Check the current status of a payment request |
| `list_payment_requests` | List payment requests for a user |
| `get_agent_config` | Get agent configuration (limits, active status) |

### Run locally

```bash
cd mcp
pip install -r requirements.txt
python server.py
```

The server starts on `http://0.0.0.0:8001/mcp` by default. Make sure the FastAPI backend is running on port 8000 (or set `AGENTPAY_API_URL`).

### Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_HOST` | MCP server bind host | `0.0.0.0` |
| `MCP_PORT` | MCP server bind port | `8001` |
| `AGENTPAY_API_URL` | FastAPI backend URL | `http://localhost:8000` |
| `AGENTPAY_API_KEY` | API key for backend authentication | (none) |

### Connect from Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "agentpay": {
      "url": "https://<mcp-service>.railway.app/mcp"
    }
  }
}
```

### Connect from any MCP HTTP-compatible agent

Any agent that supports MCP Streamable HTTP transport can connect using:

```
URL:  https://<mcp-service>.railway.app/mcp
```

### Deploy on Railway

The project is designed for two Railway services from the same repo:

1. **Backend (FastAPI)** — uses the root `Dockerfile` and `railway.toml`.
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **MCP Server** — create a second service in Railway pointing to the same repo:
   - Root directory: `/mcp`
   - Dockerfile path: `mcp/Dockerfile`
   - Set env var `AGENTPAY_API_URL` to the backend's internal URL (Railway private networking):
     `http://<backend-service>.railway.internal:<PORT>`
   - Set env var `AGENTPAY_API_KEY` matching the backend's `AGENTPAY_API_KEY`

The MCP server will be publicly accessible at `https://<mcp-service>.railway.app/mcp`.
