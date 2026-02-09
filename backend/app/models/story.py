"""SQLAlchemy Models - Stories and Slides."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Story(Base):
    """
    Story model - group of slides for the highlights section on the home page.
    """
    __tablename__ = "stories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Title is localized: {"ru": "...", "uz": "...", "en": "..."}
    title = Column(JSON, nullable=False)
    
    preview_image = Column(Text, nullable=False)
    order = Column(Integer, default=0, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    slides = relationship("Slide", back_populates="story", cascade="all, delete-orphan", order_by="Slide.order")


class Slide(Base):
    """
    Slide model - individual slides within a Story group.
    """
    __tablename__ = "story_slides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Localized fields: {"ru": "...", "uz": "...", "en": "..."}
    title = Column(JSON, nullable=False)
    content = Column(JSON, nullable=False)
    button_text = Column(JSON, nullable=True)
    
    image_url = Column(Text, nullable=False)
    button_link = Column(Text, nullable=True)
    order = Column(Integer, default=0, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    story = relationship("Story", back_populates="slides")
