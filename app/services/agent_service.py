"""Agent domain service."""

from fastapi import HTTPException, status
from supabase import Client

from app.repositories import agent_repository, user_repository
from app.schemas.agents import AgentCreate, AgentResponse, AgentUpdate


def _to_agent_row_create(payload: AgentCreate) -> dict:
    row: dict = {
        "user_id": str(payload.user_id),
        "name": payload.name,
        "is_active": True,
    }
    if payload.description is not None:
        row["description"] = payload.description
    if payload.default_spending_limit is not None:
        row["default_spending_limit"] = float(payload.default_spending_limit)
    return row


def _agent_response(row: dict) -> AgentResponse:
    return AgentResponse.model_validate(row)


def create_agent(client: Client, payload: AgentCreate) -> AgentResponse:
    if not user_repository.get_user_by_id(client, str(payload.user_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    row = agent_repository.create_agent(client, _to_agent_row_create(payload))
    return _agent_response(row)


def get_agent(client: Client, agent_id: str) -> AgentResponse:
    row = agent_repository.get_agent_by_id(client, agent_id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    return _agent_response(row)


def list_agents_for_user(client: Client, user_id: str) -> list[AgentResponse]:
    if not user_repository.get_user_by_id(client, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    rows = agent_repository.list_agents_by_user_id(client, user_id)
    return [_agent_response(r) for r in rows]


def update_agent(client: Client, agent_id: str, payload: AgentUpdate) -> AgentResponse:
    if not agent_repository.get_agent_by_id(client, agent_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    patch: dict = {}
    if payload.name is not None:
        patch["name"] = payload.name
    if payload.description is not None:
        patch["description"] = payload.description
    if payload.default_spending_limit is not None:
        patch["default_spending_limit"] = float(payload.default_spending_limit)
    if payload.is_active is not None:
        patch["is_active"] = payload.is_active

    if not patch:
        row = agent_repository.get_agent_by_id(client, agent_id)
        assert row is not None
        return _agent_response(row)

    updated = agent_repository.update_agent(client, agent_id, patch)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or could not be updated",
        )
    return _agent_response(updated)
