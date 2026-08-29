"""Business logic for agent CRUD, scoped to the caller's organization."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.agent import Agent
from app.models.knowledge_base import KnowledgeBase
from app.models.organization import Organization
from app.schemas.agent import AgentCreate, AgentUpdate


async def _validate_kb(db: AsyncSession, org_id: uuid.UUID, kb_id: uuid.UUID) -> None:
    kb = (
        await db.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.id == kb_id, KnowledgeBase.org_id == org_id
            )
        )
    ).scalar_one_or_none()
    if not kb:
        raise NotFoundError("Knowledge base not found")


async def create_agent(db: AsyncSession, organization: Organization, data: AgentCreate) -> Agent:
    if data.kb_id is not None:
        await _validate_kb(db, organization.id, data.kb_id)

    kwargs = data.model_dump(exclude_unset=True, exclude_none=True)
    agent = Agent(org_id=organization.id, **kwargs)
    db.add(agent)
    await db.commit()
    return agent


async def list_agents(db: AsyncSession, organization: Organization) -> list[Agent]:
    result = await db.execute(
        select(Agent).where(Agent.org_id == organization.id).order_by(Agent.created_at)
    )
    return list(result.scalars().all())


async def get_agent(db: AsyncSession, organization: Organization, agent_id: uuid.UUID) -> Agent:
    agent = (
        await db.execute(
            select(Agent).where(Agent.id == agent_id, Agent.org_id == organization.id)
        )
    ).scalar_one_or_none()
    if not agent:
        raise NotFoundError("Agent not found")
    return agent


async def update_agent(
    db: AsyncSession, organization: Organization, agent_id: uuid.UUID, data: AgentUpdate
) -> Agent:
    agent = await get_agent(db, organization, agent_id)

    updates = data.model_dump(exclude_unset=True)
    if "kb_id" in updates and updates["kb_id"] is not None:
        await _validate_kb(db, organization.id, updates["kb_id"])

    for field, value in updates.items():
        setattr(agent, field, value)

    await db.commit()
    return agent


async def delete_agent(db: AsyncSession, organization: Organization, agent_id: uuid.UUID) -> None:
    agent = await get_agent(db, organization, agent_id)
    await db.delete(agent)
    await db.commit()
