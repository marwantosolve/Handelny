"""Orchestrates a single chat turn: persistence, retrieval, and LLM streaming.

This is Mode 1 only (strict KB-grounding): if the agent has no knowledge
base attached, or retrieval finds nothing above the relevance floor, we
short-circuit to the agent's configured fallback message instead of ever
calling the LLM.
"""
import uuid
from collections.abc import AsyncIterator

from sqlalchemy import select

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.core.exceptions import NotFoundError
from app.models.agent import Agent
from app.models.conversation import Conversation
from app.models.message import ROLE_ASSISTANT, ROLE_USER, Message
from app.services import llm as llm_module
from app.services.retrieval import retrieve_context

HISTORY_LIMIT = 6


async def _get_or_create_conversation(
    db, agent_id: uuid.UUID, org_id: uuid.UUID, session_id: str
) -> Conversation:
    result = await db.execute(
        select(Conversation).where(
            Conversation.agent_id == agent_id, Conversation.session_id == session_id
        )
    )
    conversation = result.scalar_one_or_none()
    if conversation:
        return conversation

    conversation = Conversation(agent_id=agent_id, org_id=org_id, session_id=session_id)
    db.add(conversation)
    await db.flush()
    return conversation


async def _load_recent_history(db, conversation_id: uuid.UUID) -> list[dict]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(HISTORY_LIMIT)
    )
    messages = list(result.scalars().all())
    messages.reverse()
    return [{"role": message.role, "content": message.content} for message in messages]


def _dedupe_citations(context_items: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    citations: list[dict] = []
    for item in context_items:
        key = (item["filename"], item["page_number"], item["chunk_id"])
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            {
                "filename": item["filename"],
                "page_number": item["page_number"],
                "chunk_id": item["chunk_id"],
            }
        )
    return citations


async def _fallback_turn(db, conversation: Conversation, agent: Agent) -> AsyncIterator[dict]:
    fallback_text = agent.fallback_message

    yield {"event": "token", "data": {"text": fallback_text}}
    yield {"event": "citations", "data": {"sources": []}}

    assistant_message = Message(
        conversation_id=conversation.id,
        org_id=agent.org_id,
        role=ROLE_ASSISTANT,
        content=fallback_text,
        sources=[],
    )
    db.add(assistant_message)
    await db.commit()

    yield {"event": "done", "data": {"message_id": str(assistant_message.id)}}


async def stream_chat_response(
    agent_id: uuid.UUID, session_id: str, user_message: str
) -> AsyncIterator[dict]:
    """Runs one chat turn end-to-end, yielding SSE-ready event dicts.

    Events: {"event": "token" | "citations" | "done" | "error", "data": {...}}
    """
    async with AsyncSessionLocal() as db:
        agent = await db.get(Agent, agent_id)
        if not agent:
            raise NotFoundError("Agent not found")

        conversation = await _get_or_create_conversation(
            db, agent_id=agent_id, org_id=agent.org_id, session_id=session_id
        )

        user_msg = Message(
            conversation_id=conversation.id,
            org_id=agent.org_id,
            role=ROLE_USER,
            content=user_message,
        )
        db.add(user_msg)
        await db.commit()

        if agent.kb_id is None:
            async for event in _fallback_turn(db, conversation, agent):
                yield event
            return

        context_items = await retrieve_context(
            org_id=agent.org_id,
            kb_id=agent.kb_id,
            query=user_message,
            top_k=settings.retrieval_top_k,
        )

        if not context_items:
            async for event in _fallback_turn(db, conversation, agent):
                yield event
            return

        context_block = "\n\n".join(
            f"[Source: {item['filename']}, Page {item['page_number']}]\n{item['content']}"
            for item in context_items
        )
        history = await _load_recent_history(db, conversation.id)

        llm_client = llm_module.get_llm_client()
        full_text = ""
        try:
            delta_stream = await llm_client.stream_generate(
                system_prompt=agent.system_prompt,
                context_block=context_block,
                history=history,
                user_message=user_message,
            )
            async for delta in delta_stream:
                full_text += delta
                yield {"event": "token", "data": {"text": delta}}
        except Exception as exc:  # noqa: BLE001
            yield {"event": "error", "data": {"message": str(exc)}}
            return

        citations = _dedupe_citations(context_items)
        yield {"event": "citations", "data": {"sources": citations}}

        assistant_message = Message(
            conversation_id=conversation.id,
            org_id=agent.org_id,
            role=ROLE_ASSISTANT,
            content=full_text,
            sources=citations,
        )
        db.add(assistant_message)
        await db.commit()

        yield {"event": "done", "data": {"message_id": str(assistant_message.id)}}
