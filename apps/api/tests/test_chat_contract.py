"""Contract tests for the public chat endpoint's request/response shape.

Builds a standalone FastAPI app around `app.api.v1.chat.router` so these
tests don't depend on whether `app.api.v1.router` has been wired up yet by
the coordinating agent. The "unknown agent" test needs a live Postgres
connection (via `AsyncSessionLocal`); the others don't touch the DB.
"""
import uuid

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.v1.chat import router as chat_router
from app.core.exceptions import AppError, app_error_handler, unhandled_error_handler


@pytest.fixture
async def chat_client():
    app = FastAPI()
    app.include_router(chat_router, prefix="/chat")
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_chat_message_validates_empty_body(chat_client):
    response = await chat_client.post(
        f"/chat/{uuid.uuid4()}/message",
        json={"session_id": "", "message": ""},
    )
    assert response.status_code == 422


async def test_chat_message_unknown_agent_returns_404(chat_client):
    # No agent with this id exists; requires a reachable Postgres instance.
    response = await chat_client.post(
        f"/chat/{uuid.uuid4()}/message",
        json={"session_id": "sess-1", "message": "Hello"},
    )
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["type"] == "NotFoundError"


async def test_chat_message_streams_sse_events_in_order(chat_client, monkeypatch):
    """When the orchestrator succeeds, each yielded event dict should be
    formatted as an `event: ...\\ndata: ...\\n\\n` SSE frame, in order."""
    import app.api.v1.chat as chat_module

    async def fake_stream_chat_response(agent_id, session_id, user_message):
        yield {"event": "token", "data": {"text": "Hello"}}
        yield {"event": "citations", "data": {"sources": []}}
        yield {"event": "done", "data": {"message_id": "abc-123"}}

    monkeypatch.setattr(chat_module, "stream_chat_response", fake_stream_chat_response)

    response = await chat_client.post(
        f"/chat/{uuid.uuid4()}/message",
        json={"session_id": "sess-1", "message": "Hi"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    body = response.text
    token_pos = body.index("event: token")
    citations_pos = body.index("event: citations")
    done_pos = body.index("event: done")

    assert token_pos < citations_pos < done_pos
    assert '"text": "Hello"' in body
    assert '"message_id": "abc-123"' in body
