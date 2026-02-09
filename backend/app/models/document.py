"""SQLAlchemy Models - Documents."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base
from .enums import DocumentType


class Document(Base):
    """Documents attached to applications (contracts, videos, etc)."""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False, index=True)
    
    # Document info
    type = Column(SQLEnum(DocumentType), nullable=False)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(String(50), nullable=True)
    
    # Integrity check
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash
    
    # Upload info
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    version = Column(String(20), default="1.0", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    application = relationship("Application", back_populates="documents")
