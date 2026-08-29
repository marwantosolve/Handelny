"""LLM abstraction so the underlying provider (currently Gemini via Google AI
Studio) can be swapped out later without touching the chat orchestrator.
"""
from collections.abc import AsyncIterator
from typing import Protocol

from app.core.config import settings


class LLMClient(Protocol):
    async def stream_generate(
        self,
        system_prompt: str,
        context_block: str,
        history: list[dict],
        user_message: str,
    ) -> AsyncIterator[str]:
        """Returns (via await) an async iterator of text deltas.

        Note the calling convention: `stream_generate(...)` is itself a
        coroutine, so callers must `await` it once to get the async
        iterator, then `async for` over that:

            stream = await client.stream_generate(...)
            async for delta in stream:
                ...
        """
        ...


def _format_history(history: list[dict]) -> str:
    if not history:
        return "(no previous messages)"

    lines = []
    for message in history:
        speaker = "User" if message.get("role") == "user" else "Assistant"
        lines.append(f"{speaker}: {message.get('content', '')}")
    return "\n".join(lines)


def _build_prompt(
    system_prompt: str, context_block: str, history: list[dict], user_message: str
) -> str:
    formatted_history = _format_history(history)
    return (
        f"{system_prompt}\n\n"
        f"Context:\n{context_block}\n\n"
        f"Conversation so far:\n{formatted_history}\n\n"
        f"User: {user_message}\n"
        f"Assistant:"
    )


class GeminiLLMClient:
    """LLMClient implementation backed by the Google AI Studio Gemini API.

    NOTE: the `google-genai` SDK's streaming surface has shifted across
    releases. As of the version this was written against, the async
    streaming call is:

        response = await client.aio.models.generate_content_stream(
            model=..., contents=...
        )
        async for chunk in response:
            ...chunk.text...

    i.e. a single `await` yields an async iterator of response chunks. If a
    future SDK version changes this shape, only this method needs updating —
    everything else in the app talks to `LLMClient`, not to `google.genai`
    directly.
    """

    def __init__(self) -> None:
        from google import genai

        self._client = genai.Client(api_key=settings.google_ai_studio_api_key)
        self._model = settings.google_ai_model

    async def stream_generate(
        self,
        system_prompt: str,
        context_block: str,
        history: list[dict],
        user_message: str,
    ) -> AsyncIterator[str]:
        prompt = _build_prompt(system_prompt, context_block, history, user_message)

        stream = await self._client.aio.models.generate_content_stream(
            model=self._model,
            contents=prompt,
        )

        async def _iterate_deltas() -> AsyncIterator[str]:
            async for chunk in stream:
                if chunk.text:
                    yield chunk.text

        return _iterate_deltas()


_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = GeminiLLMClient()
    return _llm_client
