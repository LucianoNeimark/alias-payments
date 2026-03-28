"""Seed script: inserts a consistent demo dataset via asyncpg.

Usage:
    python -m scripts.seed_demo
"""

import asyncio
import os
import uuid
from datetime import datetime, timezone

import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
RAW_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

USER_ID = uuid.uuid4()
AGENT_ID = uuid.uuid4()
WALLET_ID = uuid.uuid4()
FUNDING_ORDER_ID = uuid.uuid4()
FUNDING_EVENT_ID = uuid.uuid4()
PAYMENT_REQUEST_ID = uuid.uuid4()
APPROVAL_ID = uuid.uuid4()
PAYOUT_ID = uuid.uuid4()
LEDGER_1_ID = uuid.uuid4()
LEDGER_2_ID = uuid.uuid4()
LEDGER_3_ID = uuid.uuid4()

NOW = datetime.now(timezone.utc)


async def seed() -> None:
    conn = await asyncpg.connect(RAW_URL)

    try:
        async with conn.transaction():
            # 1. Demo user
            await conn.execute(
                """
                INSERT INTO users (id, auth_provider_user_id, email, username, status)
                VALUES ($1, $2, $3, $4, 'active')
                """,
                USER_ID,
                "demo-auth-provider-id",
                "demo@aliaspayments.com",
                "demo",
            )

            # 2. Active agent
            await conn.execute(
                """
                INSERT INTO agents (id, user_id, name, description, default_spending_limit, is_active)
                VALUES ($1, $2, $3, $4, $5, true)
                """,
                AGENT_ID,
                USER_ID,
                "research-agent",
                "Agente demo para investigacion y pagos de paywalls",
                5000.00,
            )

            # 3. Wallet (final state: available=8800, reserved=0 after all ledger ops)
            await conn.execute(
                """
                INSERT INTO wallets (id, user_id, currency, available_balance, reserved_balance)
                VALUES ($1, $2, 'ARS', 8800.00, 0.00)
                """,
                WALLET_ID,
                USER_ID,
            )

            # 4. Funded order
            await conn.execute(
                """
                INSERT INTO funding_orders
                    (id, user_id, wallet_id, requested_amount, currency,
                     provider, provider_payment_id, cvu, alias, status)
                VALUES ($1, $2, $3, 10000.00, 'ARS',
                        'talo', 'pay_demo_001', '0000003100000000000001', 'agentpay.demo.fondeo', 'credited')
                """,
                FUNDING_ORDER_ID,
                USER_ID,
                WALLET_ID,
            )

            # 5. Funding event
            await conn.execute(
                """
                INSERT INTO funding_events
                    (id, funding_order_id, provider_event_id, provider_status,
                     received_amount, raw_payload, processed_at)
                VALUES ($1, $2, $3, 'SUCCESS', 10000.00, $4, $5)
                """,
                FUNDING_EVENT_ID,
                FUNDING_ORDER_ID,
                "evt_demo_001",
                '{"source": "seed_demo"}',
                NOW,
            )

            # 6. Completed payment request
            await conn.execute(
                """
                INSERT INTO payment_requests
                    (id, user_id, agent_id, wallet_id, amount, currency,
                     destination_cvu, destination_alias, destination_holder_name,
                     purpose, status, idempotency_key)
                VALUES ($1, $2, $3, $4, 1200.00, 'ARS',
                        '0000003100000000000099', 'proveedor.demo', 'Juan Perez',
                        'Pago de paywall base de datos', 'completed', $5)
                """,
                PAYMENT_REQUEST_ID,
                USER_ID,
                AGENT_ID,
                WALLET_ID,
                f"seed-demo-{PAYMENT_REQUEST_ID}",
            )

            # 7. Approval
            await conn.execute(
                """
                INSERT INTO approvals
                    (id, payment_request_id, user_id, decision, decision_reason, approved_amount)
                VALUES ($1, $2, $3, 'approved', 'Pago legitimo de demo', 1200.00)
                """,
                APPROVAL_ID,
                PAYMENT_REQUEST_ID,
                USER_ID,
            )

            # 8. Completed payout
            await conn.execute(
                """
                INSERT INTO payouts
                    (id, payment_request_id, execution_provider, source_account_label,
                     destination_cvu, destination_alias, amount, currency, status,
                     executor_run_id, provider_receipt_ref)
                VALUES ($1, $2, 'selenium_mercadopago', 'mp_pool_demo',
                        '0000003100000000000099', 'proveedor.demo', 1200.00, 'ARS', 'completed',
                        'run_demo_001', 'op_demo_001')
                """,
                PAYOUT_ID,
                PAYMENT_REQUEST_ID,
            )

            # 9. Ledger entries (chronological order)

            # 9a. funding_credit: +10000 available
            await conn.execute(
                """
                INSERT INTO ledger_entries
                    (id, wallet_id, entry_type, direction, amount, currency,
                     reference_type, reference_id,
                     balance_after_available, balance_after_reserved, description)
                VALUES ($1, $2, 'funding_credit', 'credit', 10000.00, 'ARS',
                        'funding_order', $3,
                        10000.00, 0.00, 'Acreditacion de fondeo Talo')
                """,
                LEDGER_1_ID,
                WALLET_ID,
                str(FUNDING_ORDER_ID),
            )

            # 9b. reserve: -1200 available, +1200 reserved
            await conn.execute(
                """
                INSERT INTO ledger_entries
                    (id, wallet_id, entry_type, direction, amount, currency,
                     reference_type, reference_id,
                     balance_after_available, balance_after_reserved, description)
                VALUES ($1, $2, 'reserve', 'debit', 1200.00, 'ARS',
                        'payment_request', $3,
                        8800.00, 1200.00, 'Reserva para pago aprobado')
                """,
                LEDGER_2_ID,
                WALLET_ID,
                str(PAYMENT_REQUEST_ID),
            )

            # 9c. payout_debit: -1200 reserved
            await conn.execute(
                """
                INSERT INTO ledger_entries
                    (id, wallet_id, entry_type, direction, amount, currency,
                     reference_type, reference_id,
                     balance_after_available, balance_after_reserved, description)
                VALUES ($1, $2, 'payout_debit', 'debit', 1200.00, 'ARS',
                        'payout', $3,
                        8800.00, 0.00, 'Debito por payout completado')
                """,
                LEDGER_3_ID,
                WALLET_ID,
                str(PAYOUT_ID),
            )

        print("Seed completed successfully!")
        print(f"  User ID:            {USER_ID}")
        print(f"  Agent ID:           {AGENT_ID}")
        print(f"  Wallet ID:          {WALLET_ID}")
        print(f"  Funding Order ID:   {FUNDING_ORDER_ID}")
        print(f"  Payment Request ID: {PAYMENT_REQUEST_ID}")
        print(f"  Payout ID:          {PAYOUT_ID}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed())
