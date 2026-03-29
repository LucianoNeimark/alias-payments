/* API response shapes (subset; matches FastAPI / Pydantic). */

export type User = {
  id: string;
  auth_provider_user_id: string;
  email: string;
  username: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export type Wallet = {
  id: string;
  user_id: string;
  currency: string;
  available_balance: string;
  reserved_balance: string;
  created_at: string;
  updated_at: string;
};

export type Agent = {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  default_spending_limit: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type PaymentRequest = {
  id: string;
  user_id: string;
  agent_id: string;
  wallet_id: string;
  amount: string;
  currency: string;
  destination_cvu: string;
  destination_alias: string | null;
  destination_holder_name: string | null;
  purpose: string;
  status: string;
  idempotency_key: string;
  created_at: string;
  updated_at: string;
};

export type Approval = {
  id: string;
  payment_request_id: string;
  user_id: string;
  decision: string;
  decision_reason: string | null;
  approved_amount: number;
  created_at: string;
};

export type Payout = {
  id: string;
  payment_request_id: string;
  execution_provider: string;
  source_account_label: string | null;
  destination_cvu: string;
  destination_alias: string | null;
  amount: string;
  currency: string;
  status: string;
  executor_run_id: string | null;
  provider_receipt_ref: string | null;
  failure_reason: string | null;
  created_at: string;
  updated_at: string;
};

export type FundingOrder = {
  id: string;
  user_id: string;
  wallet_id: string;
  requested_amount: number | string;
  currency: string;
  provider: string;
  provider_payment_id: string | null;
  cvu: string | null;
  alias: string | null;
  status: string;
  expires_at: string | null;
  created_at: string;
  updated_at: string;
};

export type LedgerEntry = {
  id: string;
  wallet_id: string;
  entry_type: string;
  direction: string;
  amount: string;
  currency: string;
  reference_type: string;
  reference_id: string;
  balance_after_available: string;
  balance_after_reserved: string;
  description: string | null;
  created_at: string;
};

export type MeResponse = {
  user: User;
  wallet: Wallet | null;
  agents: Agent[];
  pending_payment_requests_count: number;
  recent_payment_requests: PaymentRequest[];
  recent_payouts: Payout[];
  recent_ledger_entries: LedgerEntry[];
};

export type MeStatsResponse = {
  pending_payment_requests: number;
  active_agents: number;
  total_agents: number;
  wallet_available: string;
  wallet_reserved: string;
  payouts_completed: number;
  payouts_failed: number;
  payouts_needs_manual_review: number;
};
