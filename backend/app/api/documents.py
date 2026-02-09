"""Documents API routes."""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
import os
import hashlib

from ..dependencies import DB, CurrentUser, ManagerUser
from ..models.document import Document
from ..models.application import Application
from ..models.enums import DocumentType, Role
from ..schemas.common import DocumentResponse, DocumentUpload
from ..services.audit import log_action
from ..config import settings

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    app_id: UUID,
    type: DocumentType,
    current_user: ManagerUser,
    db: DB,
    file: UploadFile = File(...)
):
    """
    Upload a document (contract, video, etc).
    Manager only.
    """
    # Check application
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    # Create directory if not exists
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(app_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{type.value}_{file.filename}")
    
    # Save file and calculate hash
    sha256_hash = hashlib.sha256()
    
    # In a real async app, use aiofiles
    import aiofiles
    async with aiofiles.open(file_path, 'wb') as out_file:
        while content := await file.read(1024):
            await out_file.write(content)
            sha256_hash.update(content)
            
    file_hash = sha256_hash.hexdigest()
    
    # Create DB record
    doc = Document(
        application_id=app.id,
        type=type,
        file_path=file_path,
        original_filename=file.filename,
        mime_type=file.content_type,
        file_hash=file_hash,
        uploaded_by=current_user.id
    )
    db.add(doc)
    await db.flush()
    
    await log_action(
        db=db,
        action="document_uploaded",
        entity_type="document",
        entity_id=doc.id,
        user_id=current_user.id,
        details={"type": type.value, "filename": file.filename}
    )
    
    await db.commit()
    await db.refresh(doc)
    return doc


@router.get("/{doc_id}/download")
async def download_document(
    doc_id: UUID,
    current_user: CurrentUser,
    db: DB
):
    """Download document (secure access)."""
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
    # Check access
    if current_user.role == Role.CLIENT:
        # Check if app belongs to client
        app_res = await db.execute(select(Application).where(Application.id == doc.application_id))
        app = app_res.scalar_one_or_none()
        if not app or app.client_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on server")
        
    return FileResponse(
        path=doc.file_path, 
        filename=doc.original_filename,
        media_type=doc.mime_type
    )


@router.get("/applications/{app_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    app_id: UUID,
    current_user: CurrentUser,
    db: DB
):
    """List documents for application."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    # Access check
    if current_user.role == Role.CLIENT and app.client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    query = select(Document).where(
        (Document.application_id == app.id) &
        (Document.type != DocumentType.VIDEO_SIGNATURE)
    ).order_by(desc(Document.created_at))
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/applications/{app_id}/videos", response_model=DocumentResponse)
async def upload_video(
    app_id: UUID,
    current_user: ManagerUser,
    db: DB,
    file: UploadFile = File(...)
):
    """Upload signature video (Manager only)."""
    # Reuse upload logic but force type
    return await upload_document(
        app_id=app_id,
        type=DocumentType.VIDEO_SIGNATURE,
        current_user=current_user,
        db=db,
        file=file
    )


@router.get("/applications/{app_id}/videos", response_model=List[DocumentResponse])
async def list_videos(
    app_id: UUID,
    current_user: CurrentUser,
    db: DB
):
    """List signature videos for application."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    # Access check
    if current_user.role == Role.CLIENT and app.client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    query = select(Document).where(
        (Document.application_id == app.id) &
        (Document.type == DocumentType.VIDEO_SIGNATURE)
    ).order_by(desc(Document.created_at))
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/videos/{video_id}/download")
async def download_video(
    video_id: UUID,
    current_user: CurrentUser,
    db: DB
):
    """Download video (alias for download document)."""
    return await download_document(doc_id=video_id, current_user=current_user, db=db)
