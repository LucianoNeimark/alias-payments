"""Human approval records; creation is handled from payment_request_service."""

from supabase import Client

from app.repositories import approval_repository
from app.schemas.approvals import ApprovalResponse


def list_approvals_for_payment_request(
    client: Client, payment_request_id: str
) -> list[ApprovalResponse]:
    rows = approval_repository.get_approvals_for_payment_request(
        client, payment_request_id
    )
    return [ApprovalResponse.model_validate(r) for r in rows]
