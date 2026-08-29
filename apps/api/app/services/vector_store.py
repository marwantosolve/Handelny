"""Per-organization dense vector storage and retrieval backed by Qdrant.

Each organization gets its own collection (`org_{org_id}`) so that tenants
are physically isolated at the vector-store level. Knowledge-base scoping
within an org is enforced via a payload filter on `kb_id`.
"""
import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings
from app.services.embedding import EMBEDDING_DIM

_client: AsyncQdrantClient | None = None


def _get_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(url=settings.qdrant_url)
    return _client


def _collection_name(org_id: uuid.UUID) -> str:
    return f"org_{org_id}"


async def ensure_collection(org_id: uuid.UUID) -> None:
    """Creates the org's collection if it doesn't already exist."""
    client = _get_client()
    collection_name = _collection_name(org_id)

    if await client.collection_exists(collection_name):
        return

    await client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
    )


async def upsert_chunks(org_id: uuid.UUID, points: list[dict]) -> None:
    """Upserts chunk vectors.

    Each point: {"id": str (uuid), "vector": list[float], "payload": {...}}
    """
    if not points:
        return

    client = _get_client()
    collection_name = _collection_name(org_id)

    qdrant_points = [
        PointStruct(id=point["id"], vector=point["vector"], payload=point["payload"])
        for point in points
    ]
    await client.upsert(collection_name=collection_name, points=qdrant_points)


async def search(
    org_id: uuid.UUID, kb_id: uuid.UUID, query_vector: list[float], top_k: int
) -> list[dict]:
    """Dense vector search scoped to a single knowledge base within an org."""
    client = _get_client()
    collection_name = _collection_name(org_id)

    if not await client.collection_exists(collection_name):
        return []

    query_filter = Filter(
        must=[FieldCondition(key="kb_id", match=MatchValue(value=str(kb_id)))]
    )

    results = await client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
    )

    return [
        {"id": str(point.id), "score": point.score, "payload": point.payload or {}}
        for point in results
    ]


async def delete_document_points(org_id: uuid.UUID, document_id: uuid.UUID) -> None:
    """Removes all vector points belonging to a document (e.g. on re-ingest/delete)."""
    client = _get_client()
    collection_name = _collection_name(org_id)

    if not await client.collection_exists(collection_name):
        return

    delete_filter = Filter(
        must=[FieldCondition(key="document_id", match=MatchValue(value=str(document_id)))]
    )
    await client.delete(collection_name=collection_name, points_selector=delete_filter)
