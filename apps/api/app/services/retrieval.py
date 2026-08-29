"""Dense-vector-only retrieval for the Mode 1 (strict KB-grounding) agent flow."""
import uuid

from app.services import vector_store
from app.services.embedding import embed_texts

# Minimum cosine similarity for a chunk to be considered relevant. Anything
# below this is treated as "no relevant context found" so the caller can
# fall back to the agent's fallback_message instead of hallucinating.
MIN_RELEVANCE_SCORE = 0.55


async def retrieve_context(
    org_id: uuid.UUID, kb_id: uuid.UUID, query: str, top_k: int
) -> list[dict]:
    """Embeds the query and returns relevant chunks, sorted by score desc.

    Returns [] if nothing meets the minimum relevance floor.
    """
    [query_vector] = await embed_texts([query], is_query=True)

    results = await vector_store.search(
        org_id=org_id, kb_id=kb_id, query_vector=query_vector, top_k=top_k
    )

    context_items = [
        {
            "content": result["payload"].get("content", ""),
            "filename": result["payload"].get("filename"),
            "page_number": result["payload"].get("page_number"),
            "score": result["score"],
            "chunk_id": result["id"],
        }
        for result in results
        if result["score"] >= MIN_RELEVANCE_SCORE
    ]

    context_items.sort(key=lambda item: item["score"], reverse=True)
    return context_items
