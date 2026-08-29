"""Agent CRUD endpoints, org-scoped."""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentPrincipal, get_current_principal
from app.core.db import get_db
from app.schemas.agent import AgentCreate, AgentOut, AgentUpdate
from app.services import agent as agent_service

router = APIRouter()


@router.post("", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
async def create_agent(
    body: AgentCreate,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> AgentOut:
    agent = await agent_service.create_agent(db, principal.organization, body)
    return AgentOut.model_validate(agent)


@router.get("", response_model=list[AgentOut])
async def list_agents(
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> list[AgentOut]:
    agents = await agent_service.list_agents(db, principal.organization)
    return [AgentOut.model_validate(agent) for agent in agents]


@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(
    agent_id: uuid.UUID,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> AgentOut:
    agent = await agent_service.get_agent(db, principal.organization, agent_id)
    return AgentOut.model_validate(agent)


@router.patch("/{agent_id}", response_model=AgentOut)
async def update_agent(
    agent_id: uuid.UUID,
    body: AgentUpdate,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> AgentOut:
    agent = await agent_service.update_agent(db, principal.organization, agent_id, body)
    return AgentOut.model_validate(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: uuid.UUID,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> None:
    await agent_service.delete_agent(db, principal.organization, agent_id)
