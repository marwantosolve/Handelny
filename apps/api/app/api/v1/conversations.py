"""Auth-required endpoints for browsing chat history (conversations & messages)."""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentPrincipal, get_current_principal
from app.core.db import get_db
from app.core.exceptions import NotFoundError
from app.models.agent import Agent
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter()


@router.get("/")
async def list_conversations(
    agent_id: uuid.UUID = Query(...),
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    agent = await db.get(Agent, agent_id)
    if not agent or agent.org_id != principal.organization.id:
        raise NotFoundError("Agent not found")

    message_count_subquery = (
        select(func.count(Message.id))
        .where(Message.conversation_id == Conversation.id)
        .correlate(Conversation)
        .scalar_subquery()
    )

    result = await db.execute(
        select(Conversation, message_count_subquery.label("message_count"))
        .where(
            Conversation.agent_id == agent_id,
            Conversation.org_id == principal.organization.id,
        )
        .order_by(Conversation.created_at.desc())
    )

    return [
        {
            "id": str(conversation.id),
            "session_id": conversation.session_id,
            "created_at": conversation.created_at,
            "message_count": message_count,
        }
        for conversation, message_count in result.all()
    ]


@router.get("/{conversation_id}/messages")
async def list_messages(
    conversation_id: uuid.UUID,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    conversation = await db.get(Conversation, conversation_id)
    if not conversation or conversation.org_id != principal.organization.id:
        raise NotFoundError("Conversation not found")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )

    return [
        {
            "id": str(message.id),
            "role": message.role,
            "content": message.content,
            "sources": message.sources,
            "created_at": message.created_at,
        }
        for message in result.scalars().all()
    ]
