"""Initial schema: enums, tables, indexes, triggers, RLS.

Revision ID: 0001
Revises:
Create Date: 2026-03-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# ---------------------------------------------------------------------------
# Enum definitions
# ---------------------------------------------------------------------------
ENUMS = [
    ("user_status", ["active", "suspended", "banned"]),
    ("funding_order_status", ["pending", "credited", "underpaid", "overpaid", "expired", "failed"]),
    (
        "payment_request_status",
        [
            "requested", "rejected", "insufficient_funds", "reserved",
            "executing", "completed", "failed", "needs_manual_review",
        ],
    ),
    ("payout_status", ["queued", "executing", "completed", "failed", "needs_manual_review"]),
    ("ledger_entry_type", ["funding_credit", "reserve", "release", "payout_debit", "manual_adjustment"]),
    ("ledger_direction", ["credit", "debit"]),
    ("approval_decision", ["approved", "rejected"]),
]

TABLES_WITH_UPDATED_AT = [
    "users", "agents", "wallets", "funding_orders", "payment_requests", "payouts",
]

RLS_CRUD_TABLES = ["wallets", "payment_requests", "agents", "funding_orders"]


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # 1. Create PostgreSQL enum types
    # -----------------------------------------------------------------------
    for enum_name, values in ENUMS:
        sa.Enum(*values, name=enum_name).create(op.get_bind(), checkfirst=True)

    # -----------------------------------------------------------------------
    # 2. Create tables in FK-dependency order
    # -----------------------------------------------------------------------

    # -- users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("auth_provider_user_id", sa.Text, nullable=False, unique=True),
        sa.Column("email", sa.Text, nullable=False),
        sa.Column("username", sa.Text, nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "suspended", "banned", name="user_status", create_type=False),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # -- agents
    op.create_table(
        "agents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("default_spending_limit", sa.Numeric(12, 2), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # -- wallets
    op.create_table(
        "wallets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("currency", sa.Text, nullable=False, server_default=sa.text("'ARS'")),
        sa.Column("available_balance", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("reserved_balance", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # -- funding_orders
    op.create_table(
        "funding_orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("wallet_id", UUID(as_uuid=True), sa.ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requested_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.Text, nullable=False, server_default=sa.text("'ARS'")),
        sa.Column("provider", sa.Text, nullable=False),
        sa.Column("provider_payment_id", sa.Text, nullable=False),
        sa.Column("cvu", sa.Text, nullable=False),
        sa.Column("alias", sa.Text, nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "credited", "underpaid", "overpaid", "expired", "failed",
                     name="funding_order_status", create_type=False),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # -- funding_events
    op.create_table(
        "funding_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "funding_order_id", UUID(as_uuid=True),
            sa.ForeignKey("funding_orders.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("provider_event_id", sa.Text, nullable=False, unique=True),
        sa.Column("provider_status", sa.Text, nullable=False),
        sa.Column("received_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("raw_payload", JSONB, nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # -- payment_requests
    op.create_table(
        "payment_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("wallet_id", UUID(as_uuid=True), sa.ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.Text, nullable=False, server_default=sa.text("'ARS'")),
        sa.Column("destination_cvu", sa.Text, nullable=False),
        sa.Column("destination_alias", sa.Text, nullable=True),
        sa.Column("destination_holder_name", sa.Text, nullable=True),
        sa.Column("purpose", sa.Text, nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "requested", "rejected", "insufficient_funds", "reserved",
                "executing", "completed", "failed", "needs_manual_review",
                name="payment_request_status", create_type=False,
            ),
            nullable=False,
            server_default=sa.text("'requested'"),
        ),
        sa.Column("idempotency_key", sa.Text, nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # -- approvals
    op.create_table(
        "approvals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "payment_request_id", UUID(as_uuid=True),
            sa.ForeignKey("payment_requests.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "decision",
            sa.Enum("approved", "rejected", name="approval_decision", create_type=False),
            nullable=False,
        ),
        sa.Column("decision_reason", sa.Text, nullable=True),
        sa.Column("approved_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # -- payouts
    op.create_table(
        "payouts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "payment_request_id", UUID(as_uuid=True),
            sa.ForeignKey("payment_requests.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("execution_provider", sa.Text, nullable=False),
        sa.Column("source_account_label", sa.Text, nullable=True),
        sa.Column("destination_cvu", sa.Text, nullable=False),
        sa.Column("destination_alias", sa.Text, nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.Text, nullable=False, server_default=sa.text("'ARS'")),
        sa.Column(
            "status",
            sa.Enum("queued", "executing", "completed", "failed", "needs_manual_review",
                     name="payout_status", create_type=False),
            nullable=False,
            server_default=sa.text("'queued'"),
        ),
        sa.Column("executor_run_id", sa.Text, nullable=True),
        sa.Column("provider_receipt_ref", sa.Text, nullable=True),
        sa.Column("failure_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # -- ledger_entries
    op.create_table(
        "ledger_entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("wallet_id", UUID(as_uuid=True), sa.ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "entry_type",
            sa.Enum("funding_credit", "reserve", "release", "payout_debit", "manual_adjustment",
                     name="ledger_entry_type", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "direction",
            sa.Enum("credit", "debit", name="ledger_direction", create_type=False),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.Text, nullable=False, server_default=sa.text("'ARS'")),
        sa.Column("reference_type", sa.Text, nullable=False),
        sa.Column("reference_id", sa.Text, nullable=False),
        sa.Column("balance_after_available", sa.Numeric(12, 2), nullable=False),
        sa.Column("balance_after_reserved", sa.Numeric(12, 2), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # -----------------------------------------------------------------------
    # 3. Explicit indexes on foreign keys and search columns
    # -----------------------------------------------------------------------
    op.create_index("ix_agents_user_id", "agents", ["user_id"])
    op.create_index("ix_wallets_user_id", "wallets", ["user_id"])
    op.create_index("ix_funding_orders_user_id", "funding_orders", ["user_id"])
    op.create_index("ix_funding_orders_wallet_id", "funding_orders", ["wallet_id"])
    op.create_index("ix_funding_events_funding_order_id", "funding_events", ["funding_order_id"])
    op.create_index("ix_payment_requests_user_id", "payment_requests", ["user_id"])
    op.create_index("ix_payment_requests_agent_id", "payment_requests", ["agent_id"])
    op.create_index("ix_payment_requests_wallet_id", "payment_requests", ["wallet_id"])
    op.create_index("ix_payment_requests_status", "payment_requests", ["status"])
    op.create_index("ix_approvals_payment_request_id", "approvals", ["payment_request_id"])
    op.create_index("ix_approvals_user_id", "approvals", ["user_id"])
    op.create_index("ix_payouts_payment_request_id", "payouts", ["payment_request_id"])
    op.create_index("ix_payouts_status", "payouts", ["status"])
    op.create_index("ix_ledger_entries_wallet_id", "ledger_entries", ["wallet_id"])

    # -----------------------------------------------------------------------
    # 4. Trigger function + per-table triggers for updated_at
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    for table in TABLES_WITH_UPDATED_AT:
        op.execute(f"""
            CREATE TRIGGER trg_{table}_updated_at
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION set_updated_at();
        """)

    # -----------------------------------------------------------------------
    # 5. Row Level Security
    # -----------------------------------------------------------------------

    # Enable RLS on all relevant tables
    for table in [*RLS_CRUD_TABLES, "ledger_entries", "payouts"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")

    # CRUD policies: user can manage their own rows
    for table in RLS_CRUD_TABLES:
        op.execute(f"""
            CREATE POLICY "Users can manage own {table}" ON {table}
                FOR ALL TO authenticated
                USING ((select auth.uid()) = user_id)
                WITH CHECK ((select auth.uid()) = user_id);
        """)

    # Read-only policy for ledger_entries via wallet ownership
    op.execute("""
        CREATE POLICY "Users can read own ledger_entries" ON ledger_entries
            FOR SELECT TO authenticated
            USING (
                wallet_id IN (
                    SELECT id FROM wallets WHERE user_id = (select auth.uid())
                )
            );
    """)

    # Read-only policy for payouts via payment_request ownership
    op.execute("""
        CREATE POLICY "Users can read own payouts" ON payouts
            FOR SELECT TO authenticated
            USING (
                payment_request_id IN (
                    SELECT id FROM payment_requests WHERE user_id = (select auth.uid())
                )
            );
    """)


def downgrade() -> None:
    # -----------------------------------------------------------------------
    # 5. Drop RLS policies
    # -----------------------------------------------------------------------
    op.execute('DROP POLICY IF EXISTS "Users can read own payouts" ON payouts;')
    op.execute('DROP POLICY IF EXISTS "Users can read own ledger_entries" ON ledger_entries;')
    for table in RLS_CRUD_TABLES:
        op.execute(f'DROP POLICY IF EXISTS "Users can manage own {table}" ON {table};')
    for table in [*RLS_CRUD_TABLES, "ledger_entries", "payouts"]:
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")

    # -----------------------------------------------------------------------
    # 4. Drop triggers and function
    # -----------------------------------------------------------------------
    for table in TABLES_WITH_UPDATED_AT:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at();")

    # -----------------------------------------------------------------------
    # 3. Drop indexes
    # -----------------------------------------------------------------------
    op.drop_index("ix_ledger_entries_wallet_id", table_name="ledger_entries")
    op.drop_index("ix_payouts_status", table_name="payouts")
    op.drop_index("ix_payouts_payment_request_id", table_name="payouts")
    op.drop_index("ix_approvals_user_id", table_name="approvals")
    op.drop_index("ix_approvals_payment_request_id", table_name="approvals")
    op.drop_index("ix_payment_requests_status", table_name="payment_requests")
    op.drop_index("ix_payment_requests_wallet_id", table_name="payment_requests")
    op.drop_index("ix_payment_requests_agent_id", table_name="payment_requests")
    op.drop_index("ix_payment_requests_user_id", table_name="payment_requests")
    op.drop_index("ix_funding_events_funding_order_id", table_name="funding_events")
    op.drop_index("ix_funding_orders_wallet_id", table_name="funding_orders")
    op.drop_index("ix_funding_orders_user_id", table_name="funding_orders")
    op.drop_index("ix_wallets_user_id", table_name="wallets")
    op.drop_index("ix_agents_user_id", table_name="agents")

    # -----------------------------------------------------------------------
    # 2. Drop tables (reverse dependency order)
    # -----------------------------------------------------------------------
    op.drop_table("ledger_entries")
    op.drop_table("payouts")
    op.drop_table("approvals")
    op.drop_table("payment_requests")
    op.drop_table("funding_events")
    op.drop_table("funding_orders")
    op.drop_table("wallets")
    op.drop_table("agents")
    op.drop_table("users")

    # -----------------------------------------------------------------------
    # 1. Drop enum types
    # -----------------------------------------------------------------------
    for enum_name, _ in reversed(ENUMS):
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
