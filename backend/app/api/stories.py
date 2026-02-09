"""Stories API routes (Public)."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from typing import List

from ..dependencies import DB
from ..models.story import Story
from ..schemas.story import StoryResponse

router = APIRouter(prefix="/stories", tags=["Stories"])


@router.get("", response_model=List[StoryResponse])
async def list_active_stories(db: DB):
    """
    Get all active stories with their slides for the mobile app highlights section.
    Ordered by the 'order' field.
    """
    # Using selectinload to load slides efficiently
    from sqlalchemy.orm import selectinload
    
    query = (
        select(Story)
        .where(Story.is_active == True)
        .order_by(Story.order.asc())
        .options(selectinload(Story.slides))
    )
    
    result = await db.execute(query)
    stories = result.scalars().all()
    
    return stories
