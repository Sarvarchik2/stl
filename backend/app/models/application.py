"""SQLAlchemy Models - Applications (core business entity)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Numeric, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base
from .enums import ApplicationStatus, ContactStatus, RejectionReason


class Application(Base):
    """Application - the main business entity connecting client, car, and process."""
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relations
    client_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    car_id = Column(UUID(as_uuid=True), ForeignKey("cars_catalog.id"), nullable=False, index=True)
    operator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Price snapshot at creation time
    source_price_snapshot = Column(Numeric(12, 2), nullable=False)
    markup_percent = Column(Numeric(5, 2), default=12.0, nullable=False)
    final_price = Column(Numeric(12, 2), nullable=False)
    
    # Statuses
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.NEW, nullable=False, index=True)
    contact_status = Column(SQLEnum(ContactStatus), default=ContactStatus.NOT_TOUCHED, nullable=False)
    
    # CRM checklist (JSON object)
    checklist = Column(JSON, default=dict)
    # Expected structure:
    # {
    #     "confirmed_interest": false,
    #     "confirmed_budget": false,
    #     "confirmed_timeline": false,
    #     "agreed_visit": false,
    #     "agreed_contract": false
    # }
    
    # Rejection info
    rejection_reason = Column(SQLEnum(RejectionReason), nullable=True)
    rejection_note = Column(Text, nullable=True)
    
    # Comments
    operator_comment = Column(Text, nullable=True)  # Visible to manager
    internal_note = Column(Text, nullable=True)  # Visible to admin
    
    # Car confirmation
    car_confirmed = Column(Boolean, default=False)
    car_confirmed_by = Column(UUID(as_uuid=True), nullable=True)
    car_confirmed_at = Column(DateTime, nullable=True)
    
    # Logistics
    cargo_booking_number = Column(String(100), nullable=True)
    cargo_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    client = relationship("User", back_populates="applications", foreign_keys=[client_id])
    operator = relationship("User", back_populates="assigned_applications", foreign_keys=[operator_id])
    car = relationship("Car", back_populates="applications")
    payments = relationship("Payment", back_populates="application")
    documents = relationship("Document", back_populates="application")
    status_history = relationship("StatusHistory", back_populates="application", order_by="StatusHistory.created_at.desc()")
    comments = relationship("ApplicationComment", back_populates="application", order_by="ApplicationComment.created_at.desc()")


class StatusHistory(Base):
    """Status history for tracking all status changes."""
    __tablename__ = "application_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False, index=True)
    old_status = Column(SQLEnum(ApplicationStatus), nullable=True)
    new_status = Column(SQLEnum(ApplicationStatus), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    application = relationship("Application", back_populates="status_history")


class ApplicationComment(Base):
    """Comments on applications."""
    __tablename__ = "application_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # If true, only visible to admins/managers
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    application = relationship("Application", back_populates="comments")
    user = relationship("User")
