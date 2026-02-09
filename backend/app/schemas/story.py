"""Pydantic Schemas - Stories and Slides."""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID


# --- Localized Fields ---

class LocalizedString(BaseModel):
    ru: str
    uz: str
    en: str


class OptionalLocalizedString(BaseModel):
    ru: Optional[str] = None
    uz: Optional[str] = None
    en: Optional[str] = None


# --- Slide Schemas ---

class SlideBase(BaseModel):
    title: LocalizedString
    content: LocalizedString
    image_url: str
    button_text: Optional[LocalizedString] = None
    button_link: Optional[str] = None
    order: int = 0


class SlideCreate(SlideBase):
    pass


class SlideUpdate(BaseModel):
    title: Optional[LocalizedString] = None
    content: Optional[LocalizedString] = None
    image_url: Optional[str] = None
    button_text: Optional[LocalizedString] = None
    button_link: Optional[str] = None
    order: Optional[int] = None


class SlideResponse(SlideBase):
    id: UUID
    story_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Story Schemas ---

class StoryBase(BaseModel):
    title: LocalizedString
    preview_image: str
    order: int = 0
    is_active: bool = True


class StoryCreate(StoryBase):
    pass


class StoryUpdate(BaseModel):
    title: Optional[LocalizedString] = None
    preview_image: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class StoryResponse(StoryBase):
    id: UUID
    slides: List[SlideResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StoryBriefResponse(StoryBase):
    """Brief version for lists without full slide details if needed, or keeping it as requested."""
    id: UUID
    slides: List[SlideResponse] = []

    class Config:
        from_attributes = True
