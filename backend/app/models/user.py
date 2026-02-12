"""SQLAlchemy Models - Users."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base
from .enums import Role


class User(Base):
    """User model for clients and staff."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(SQLEnum(Role), default=Role.CLIENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    applications = relationship("Application", back_populates="client", foreign_keys="Application.client_id")
    assigned_applications = relationship("Application", back_populates="operator", foreign_keys="Application.operator_id")
    managed_applications = relationship("Application", back_populates="manager", foreign_keys="Application.manager_id")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def has_permission(self, required_role: Role) -> bool:
        """Check if user has at least the required role level."""
        from .enums import ROLE_HIERARCHY
        return ROLE_HIERARCHY.get(self.role, 0) >= ROLE_HIERARCHY.get(required_role, 99)
