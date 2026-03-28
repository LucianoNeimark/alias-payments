"""Agent HTTP routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from supabase import Client

from app.database import get_supabase_client
from app.schemas.agents import AgentCreate, AgentResponse, AgentUpdate
from app.services import agent_service

router = APIRouter()

SupabaseDep = Annotated[Client, Depends(get_supabase_client)]


@router.post(
    "/",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_agent(payload: AgentCreate, client: SupabaseDep) -> AgentResponse:
    return agent_service.create_agent(client, payload)


@router.get("/", response_model=list[AgentResponse])
def list_agents(
    client: SupabaseDep,
    user_id: Annotated[UUID, Query(description="Filter agents by owner user")],
) -> list[AgentResponse]:
    return agent_service.list_agents_for_user(client, str(user_id))


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, client: SupabaseDep) -> AgentResponse:
    return agent_service.get_agent(client, agent_id)


@router.patch("/{agent_id}", response_model=AgentResponse)
def patch_agent(
    agent_id: str,
    body: AgentUpdate,
    client: SupabaseDep,
) -> AgentResponse:
    return agent_service.update_agent(client, agent_id, body)
