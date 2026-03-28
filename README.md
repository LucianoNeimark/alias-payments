# Alias Payments

FastAPI skeleton for payments-related APIs.

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

## Layout

- `app/main.py` — FastAPI app and router registration
- `app/config.py` / `app/database.py` — settings and Supabase client
- `app/schemas/` — Pydantic request/response models
- `app/repositories/` — Supabase table access
- `app/api/routers/` — HTTP routes
- `app/services/` — domain services
