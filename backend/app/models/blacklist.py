"""SQLAlchemy Models - Blacklist."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base
from .enums import BlockType, BlacklistReason


class Blacklist(Base):
    """Blacklist for anti-fraud phone blocking."""
    __tablename__ = "blacklist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    
    # Blocking info
    reason = Column(SQLEnum(BlacklistReason), nullable=False)
    reason_note = Column(Text, nullable=True)
    strike_count = Column(Integer, default=1, nullable=False)
    block_type = Column(SQLEnum(BlockType), nullable=True)
    blocked_until = Column(DateTime, nullable=True)  # null for permanent
    
    # Who added/modified
    added_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
