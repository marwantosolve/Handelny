"""Document upload/list/get/delete endpoints, org-scoped.

This router is mounted with no prefix (see `app.api.v1.router`), so each route
below spells out its full path under both `/knowledge-bases/{kb_id}/documents`
and `/documents/{document_id}`.
"""
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentPrincipal, get_current_principal
from app.core.db import get_db
from app.schemas.document import DocumentDetail, DocumentOut, DocumentUploadResponse
from app.services import document as document_service
from app.services import knowledge_base as kb_service

router = APIRouter()


@router.post(
    "/knowledge-bases/{kb_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    kb_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    kb = await kb_service.get_knowledge_base(db, principal.organization, kb_id)
    content = await file.read()

    document = await document_service.upload_document(
        db, principal.organization, kb, filename=file.filename or "upload", content=content
    )

    background_tasks.add_task(document_service.trigger_ingestion, document.id)

    return DocumentUploadResponse.model_validate(document)


@router.get("/knowledge-bases/{kb_id}/documents", response_model=list[DocumentOut])
async def list_documents(
    kb_id: uuid.UUID,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentOut]:
    kb = await kb_service.get_knowledge_base(db, principal.organization, kb_id)
    documents = await document_service.list_documents(db, principal.organization, kb)
    return [DocumentOut.model_validate(document) for document in documents]


@router.get("/documents/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: uuid.UUID,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> DocumentDetail:
    document = await document_service.get_document(db, principal.organization, document_id)
    return DocumentDetail.model_validate(document)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
) -> None:
    await document_service.delete_document(db, principal.organization, document_id)
