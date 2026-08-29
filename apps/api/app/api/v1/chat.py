"""Public chat endpoint (no auth) — the embeddable-widget-style API for v1."""
import json
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatMessageRequest
from app.services.chat import stream_chat_response

router = APIRouter()


def _format_event(event: dict) -> str:
    return f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"


@router.post("/{agent_id}/message")
async def send_message(agent_id: uuid.UUID, body: ChatMessageRequest) -> StreamingResponse:
    event_generator = stream_chat_response(
        agent_id=agent_id, session_id=body.session_id, user_message=body.message
    )

    # Pull the first event before returning the StreamingResponse. This way,
    # errors raised early in the orchestrator (e.g. NotFoundError for an
    # unknown agent) propagate through FastAPI's normal AppError handling
    # instead of being swallowed after SSE response headers are already on
    # the wire.
    try:
        first_event = await event_generator.__anext__()
    except StopAsyncIteration:
        first_event = None

    async def event_stream():
        if first_event is not None:
            yield _format_event(first_event)
        async for event in event_generator:
            yield _format_event(event)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
