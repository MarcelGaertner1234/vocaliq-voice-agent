from typing import Any, Dict, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.core.database import get_session
from api.services.knowledge_service import KnowledgeService
from api.models.company import Company, KnowledgeBase, Document

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


async def _get_or_create_default_company(session: AsyncSession) -> Company:
    result = await session.execute(select(Company).order_by(Company.created_at.asc()))
    company = result.scalar_one_or_none()
    if company:
        return company
    # Create a default company
    company = Company(name="Default Company", slug="default", voice_language="de-DE")
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


async def _get_or_create_kb(session: AsyncSession, company: Company) -> KnowledgeBase:
    result = await session.execute(select(KnowledgeBase).where(KnowledgeBase.company_id == company.id))
    kb = result.scalar_one_or_none()
    if kb:
        return kb
    service = KnowledgeService()
    kb = await service.create_knowledge_base(company)
    return kb


@router.get("/documents")
async def list_documents(session: AsyncSession = Depends(get_session)):
    try:
        company = await _get_or_create_default_company(session)
        result = await session.execute(select(Document).join(KnowledgeBase).where(KnowledgeBase.company_id == company.id))
        docs = result.scalars().all()
        return [
            {
                "id": d.id,
                "filename": d.filename,
                "file_type": d.file_type,
                "file_size": d.file_size,
                "chunk_count": d.chunk_count,
                "uploaded_at": d.uploaded_at,
                "processing_status": d.processing_status,
            } for d in docs
        ]
    except Exception as e:
        raise HTTPException(500, f"Failed to list documents: {e}")


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    try:
        company = await _get_or_create_default_company(session)
        kb = await _get_or_create_kb(session, company)
        service = KnowledgeService()
        doc = await service.upload_document(kb, file)
        return {
            "id": doc.id,
            "filename": doc.filename,
            "status": doc.processing_status,
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to upload document: {e}")


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, session: AsyncSession = Depends(get_session)):
    try:
        # Fetch document and KB
        result = await session.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(404, "Document not found")
        service = KnowledgeService()
        await service.delete_document(doc)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to delete document: {e}")


@router.get("/search")
async def search(query: str, limit: int = 5, session: AsyncSession = Depends(get_session)):
    try:
        company = await _get_or_create_default_company(session)
        kb = await _get_or_create_kb(session, company)
        service = KnowledgeService()
        results = await service.search_knowledge(kb, query=query, limit=limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(500, f"Failed to search knowledge: {e}") 