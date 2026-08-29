"""End-to-end document ingestion, run via FastAPI `BackgroundTasks` (v1 has
no Celery/Redis workers). Opens its own DB session since background tasks
have no request-scoped session available.
"""
import logging
import uuid

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models.chunk import Chunk
from app.models.document import STATUS_ERROR, STATUS_PROCESSING, STATUS_READY, Document
from app.models.knowledge_base import KnowledgeBase
from app.services import vector_store
from app.services.embedding import embed_texts
from app.services.ingestion.chunker import chunk_text
from app.services.ingestion.cleaner import clean_text
from app.services.ingestion.language import detect_language
from app.services.ingestion.parser import parse_document

logger = logging.getLogger("handelny.ingestion")

EMBEDDING_BATCH_SIZE = 32


async def ingest_document(document_id: uuid.UUID) -> None:
    """Parses, chunks, embeds, and indexes a single document.

    On failure, persists `Document.status = error` with the error message
    and re-raises so the failure isn't silently swallowed.
    """
    async with AsyncSessionLocal() as db:
        document = await db.get(Document, document_id)
        if not document:
            logger.error("ingest_document: document %s not found", document_id)
            return

        document.status = STATUS_PROCESSING
        await db.commit()

        try:
            # Lazy import: owned by another concurrently-developed module.
            from app.services.file_storage import download_file

            file_bytes = await download_file(document.storage_path)

            pages = await parse_document(file_bytes, document.file_type)
            cleaned_pages = [
                {"content": clean_text(page["content"]), "page_number": page["page_number"]}
                for page in pages
            ]

            full_text = "\n\n".join(page["content"] for page in cleaned_pages)
            document.language = detect_language(full_text)

            chunks = chunk_text(
                cleaned_pages,
                chunk_size_tokens=settings.chunk_size_tokens,
                overlap_tokens=settings.chunk_overlap_tokens,
            )

            if chunks:
                embeddings: list[list[float]] = []
                for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
                    batch = chunks[start : start + EMBEDDING_BATCH_SIZE]
                    batch_embeddings = await embed_texts(
                        [chunk["content"] for chunk in batch], is_query=False
                    )
                    embeddings.extend(batch_embeddings)

                points = []
                chunk_rows = []
                for chunk, embedding in zip(chunks, embeddings):
                    point_id = str(uuid.uuid4())
                    points.append(
                        {
                            "id": point_id,
                            "vector": embedding,
                            "payload": {
                                "kb_id": str(document.kb_id),
                                "document_id": str(document.id),
                                "chunk_index": chunk["chunk_index"],
                                "content": chunk["content"],
                                "page_number": chunk["page_number"],
                                "filename": document.filename,
                            },
                        }
                    )
                    chunk_rows.append(
                        Chunk(
                            document_id=document.id,
                            kb_id=document.kb_id,
                            org_id=document.org_id,
                            content=chunk["content"],
                            token_count=chunk["token_count"],
                            chunk_index=chunk["chunk_index"],
                            page_number=chunk["page_number"],
                            qdrant_point_id=point_id,
                        )
                    )

                await vector_store.ensure_collection(document.org_id)
                await vector_store.upsert_chunks(document.org_id, points)

                db.add_all(chunk_rows)

            document.status = STATUS_READY
            document.chunk_count = len(chunks)
            document.page_count = len(pages)
            document.error_message = None

            knowledge_base = await db.get(KnowledgeBase, document.kb_id)
            if knowledge_base is not None:
                knowledge_base.chunk_count = (knowledge_base.chunk_count or 0) + len(chunks)

            await db.commit()

        except Exception as exc:  # noqa: BLE001
            # Deliberately NOT re-raised: this runs as a FastAPI BackgroundTask,
            # after the HTTP response has already been sent. Letting the
            # exception propagate would bubble up through the ASGI stack with
            # nowhere useful to go (and can even surface as a broken response
            # in ASGI test transports). The failure is already fully captured
            # on the Document row for the frontend to poll and display.
            logger.exception("ingest_document failed for document %s", document_id)
            await db.rollback()
            document = await db.get(Document, document_id)
            if document is not None:
                document.status = STATUS_ERROR
                document.error_message = str(exc)
                await db.commit()
