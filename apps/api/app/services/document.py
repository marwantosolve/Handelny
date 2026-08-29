"""Business logic for document upload/list/get/delete, scoped to the caller's org."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppError, NotFoundError
from app.models.document import STATUS_PENDING, Document
from app.models.knowledge_base import KnowledgeBase
from app.models.organization import Organization
from app.services import file_storage


def _validate_upload(filename: str, size: int) -> str:
    if "." not in filename:
        raise AppError("File must have an extension")

    extension = filename.rsplit(".", 1)[-1].lower()
    if extension not in settings.allowed_file_types:
        allowed = ", ".join(settings.allowed_file_types)
        raise AppError(f"Unsupported file type '.{extension}'. Allowed types: {allowed}")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    if size > max_bytes:
        raise AppError(f"File exceeds the maximum upload size of {settings.max_upload_mb}MB")

    return extension


async def upload_document(
    db: AsyncSession,
    organization: Organization,
    kb: KnowledgeBase,
    filename: str,
    content: bytes,
) -> Document:
    extension = _validate_upload(filename, len(content))

    document = Document(
        kb_id=kb.id,
        org_id=organization.id,
        filename=filename,
        file_type=extension,
        file_size=len(content),
        storage_path="",
        status=STATUS_PENDING,
    )
    db.add(document)
    await db.flush()

    storage_path = await file_storage.upload_file(
        org_id=organization.id,
        kb_id=kb.id,
        document_id=document.id,
        filename=filename,
        content=content,
    )
    document.storage_path = storage_path
    kb.doc_count += 1

    await db.commit()
    return document


async def list_documents(
    db: AsyncSession, organization: Organization, kb: KnowledgeBase
) -> list[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.kb_id == kb.id, Document.org_id == organization.id)
        .order_by(Document.created_at)
    )
    return list(result.scalars().all())


async def get_document(
    db: AsyncSession, organization: Organization, document_id: uuid.UUID
) -> Document:
    document = (
        await db.execute(
            select(Document).where(
                Document.id == document_id, Document.org_id == organization.id
            )
        )
    ).scalar_one_or_none()
    if not document:
        raise NotFoundError("Document not found")
    return document


async def delete_document(
    db: AsyncSession, organization: Organization, document_id: uuid.UUID
) -> None:
    document = await get_document(db, organization, document_id)

    kb = await db.get(KnowledgeBase, document.kb_id)

    await file_storage.delete_file(document.storage_path)
    await db.delete(document)

    if kb:
        kb.doc_count = max(0, kb.doc_count - 1)
        kb.chunk_count = max(0, kb.chunk_count - document.chunk_count)

    await db.commit()


async def trigger_ingestion(document_id: uuid.UUID) -> None:
    """Background-task entrypoint that kicks off ingestion for a newly uploaded document.

    Uses a lazy import so this module (and the API) keeps working even if the
    RAG ingestion pipeline module isn't present yet during parallel development.
    """
    from app.services.ingestion_pipeline import ingest_document

    await ingest_document(document_id)
