"""Stories Admin API routes."""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile

from ..dependencies import DB, AdminUser
from ..models.story import Story, Slide
from ..schemas.story import (
    StoryCreate, StoryUpdate, StoryResponse,
    SlideCreate, SlideUpdate, SlideResponse
)
from ..services.audit import log_action

router = APIRouter(prefix="/admin/stories", tags=["Admin Stories"])


@router.post("", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def create_story(
    request: StoryCreate,
    current_user: AdminUser,
    db: DB
):
    """Create a new story group (Admin only)."""
    story = Story(
        title=request.title.model_dump(),
        preview_image=request.preview_image,
        order=request.order,
        is_active=request.is_active
    )
    db.add(story)
    await db.flush()
    
    await log_action(
        db=db,
        action="story_created",
        entity_type="story",
        entity_id=story.id,
        user_id=current_user.id,
        new_value=request.model_dump()
    )
    
    await db.commit()
    
    # Reload with slides to avoid lazy load issues
    result = await db.execute(
        select(Story).where(Story.id == story.id).options(selectinload(Story.slides))
    )
    return result.scalar_one()


@router.patch("/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: UUID,
    request: StoryUpdate,
    current_user: AdminUser,
    db: DB
):
    """Update a story group (Admin only)."""
    result = await db.execute(select(Story).where(Story.id == story_id))
    story = result.scalar_one_or_none()
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    old_value = {
        "title": story.title,
        "preview_image": story.preview_image,
        "order": story.order,
        "is_active": story.is_active
    }
    
    if request.title is not None:
        story.title = request.title.model_dump()
    if request.preview_image is not None:
        story.preview_image = request.preview_image
    if request.order is not None:
        story.order = request.order
    if request.is_active is not None:
        story.is_active = request.is_active
    
    await log_action(
        db=db,
        action="story_updated",
        entity_type="story",
        entity_id=story.id,
        user_id=current_user.id,
        old_value=old_value,
        new_value=request.model_dump(exclude_unset=True)
    )
    
    await db.commit()
    
    # Reload with slides to avoid lazy load issues
    result = await db.execute(
        select(Story).where(Story.id == story_id).options(selectinload(Story.slides))
    )
    return result.scalar_one()


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
    story_id: UUID,
    current_user: AdminUser,
    db: DB
):
    """Delete a story group and all its slides (Admin only)."""
    result = await db.execute(select(Story).where(Story.id == story_id))
    story = result.scalar_one_or_none()
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    await db.delete(story)
    
    await log_action(
        db=db,
        action="story_deleted",
        entity_type="story",
        entity_id=story_id,
        user_id=current_user.id,
        old_value={"title": story.title}
    )
    
    await db.commit()
    return None


# --- Slide Management ---

@router.post("/{story_id}/slides", response_model=SlideResponse, status_code=status.HTTP_201_CREATED)
async def create_slide(
    story_id: UUID,
    request: SlideCreate,
    current_user: AdminUser,
    db: DB
):
    """Add a slide to a story group (Admin only)."""
    # Verify story exists
    result = await db.execute(select(Story).where(Story.id == story_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Story not found")
    
    slide = Slide(
        story_id=story_id,
        title=request.title.model_dump(),
        content=request.content.model_dump(),
        image_url=request.image_url,
        button_text=request.button_text.model_dump() if request.button_text else None,
        button_link=request.button_link,
        order=request.order
    )
    db.add(slide)
    await db.flush()
    
    await log_action(
        db=db,
        action="slide_created",
        entity_type="slide",
        entity_id=slide.id,
        user_id=current_user.id,
        new_value=request.model_dump()
    )
    
    await db.commit()
    await db.refresh(slide)
    return slide


@router.delete("/slides/{slide_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slide(
    slide_id: UUID,
    current_user: AdminUser,
    db: DB
):
    """Delete a specific slide (Admin only)."""
    result = await db.execute(select(Slide).where(Slide.id == slide_id))
    slide = result.scalar_one_or_none()
    
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    await db.delete(slide)
    
    await log_action(
        db=db,
        action="slide_deleted",
        entity_type="slide",
        entity_id=slide_id,
        user_id=current_user.id
    )
    
    await db.commit()
    return None


@router.post("/upload", response_model=dict)
async def upload_story_image(
    current_user: AdminUser,
    file: UploadFile = File(...)
):
    """Upload an image for a story or slide (Admin only)."""
    import shutil
    import os
    from datetime import datetime
    from ..config import settings
    
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    ext = file.filename.split('.')[-1].lower() if file.filename else "jpg"
    
    from uuid import uuid4
    filename = f"story_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:8]}.{ext}"
    
    upload_path = os.path.join(settings.UPLOAD_DIR, "stories")
    os.makedirs(upload_path, exist_ok=True)
    
    file_path = os.path.join(upload_path, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": f"http://localhost:8000/uploads/stories/{filename}"}
