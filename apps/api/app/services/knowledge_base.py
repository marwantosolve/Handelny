"""Business logic for knowledge base CRUD, scoped to the caller's organization."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.models.organization import Organization
from app.services import file_storage


async def create_knowledge_base(
    db: AsyncSession, organization: Organization, name: str
) -> KnowledgeBase:
    kb = KnowledgeBase(org_id=organization.id, name=name)
    db.add(kb)
    await db.commit()
    return kb


async def list_knowledge_bases(
    db: AsyncSession, organization: Organization
) -> list[KnowledgeBase]:
    result = await db.execute(
        select(KnowledgeBase)
        .where(KnowledgeBase.org_id == organization.id)
        .order_by(KnowledgeBase.created_at)
    )
    return list(result.scalars().all())


async def get_knowledge_base(
    db: AsyncSession, organization: Organization, kb_id: uuid.UUID
) -> KnowledgeBase:
    kb = (
        await db.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.id == kb_id, KnowledgeBase.org_id == organization.id
            )
        )
    ).scalar_one_or_none()
    if not kb:
        raise NotFoundError("Knowledge base not found")
    return kb


async def delete_knowledge_base(
    db: AsyncSession, organization: Organization, kb_id: uuid.UUID
) -> None:
    kb = await get_knowledge_base(db, organization, kb_id)

    documents = (
        await db.execute(select(Document).where(Document.kb_id == kb.id))
    ).scalars().all()
    for document in documents:
        await file_storage.delete_file(document.storage_path)

    await db.delete(kb)
    await db.commit()
