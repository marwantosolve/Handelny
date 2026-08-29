"""Knowledge base CRUD endpoints, org-scoped."""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentPrincipal, get_current_principal
from app.core.db import get_db
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseOut
from app.services import knowledge_base as kb_service

router = APIRouter()


@router.post("", response_model=KnowledgeBaseOut, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    body: KnowledgeBaseCreate,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseOut:
    kb = await kb_service.create_knowledge_base(db, principal.organization, body.name)
    return KnowledgeBaseOut.model_validate(kb)


@router.get("", response_model=list[KnowledgeBaseOut])
async def list_knowledge_bases(
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> list[KnowledgeBaseOut]:
    kbs = await kb_service.list_knowledge_bases(db, principal.organization)
    return [KnowledgeBaseOut.model_validate(kb) for kb in kbs]


@router.get("/{kb_id}", response_model=KnowledgeBaseOut)
async def get_knowledge_base(
    kb_id: uuid.UUID,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseOut:
    kb = await kb_service.get_knowledge_base(db, principal.organization, kb_id)
    return KnowledgeBaseOut.model_validate(kb)


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: uuid.UUID,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> None:
    await kb_service.delete_knowledge_base(db, principal.organization, kb_id)
