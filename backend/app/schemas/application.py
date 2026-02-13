"""Pydantic Schemas - Applications."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from ..models.enums import ApplicationStatus, ContactStatus, RejectionReason
from .user import UserResponse
from .car import CarResponse
from .common import DocumentResponse, PaymentResponse


# --- Checklist ---

class Checklist(BaseModel):
    agreed_visit: bool = False
    documents: bool = False


# --- Application Schemas ---

class ApplicationCreate(BaseModel):
    car_id: UUID
    agreed_terms: bool = Field(..., description="User must agree to terms")


class AdminApplicationCreate(BaseModel):
    car_id: UUID
    client_id: Optional[UUID] = None
    client_phone: Optional[str] = None
    client_name: Optional[str] = None
    source: Optional[str] = "Admin Panel"


class ApplicationResponse(BaseModel):
    id: UUID
    client_id: UUID
    car_id: UUID
    operator_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    
    # Price info
    source_price_snapshot: Decimal
    markup_percent: Decimal
    final_price: Decimal
    
    # Status
    status: ApplicationStatus
    contact_status: ContactStatus
    
    # CRM
    checklist: Optional[Dict[str, Any]] = None
    rejection_reason: Optional[RejectionReason] = None
    rejection_note: Optional[str] = None
    
    # Car confirmation
    car_confirmed: bool
    
    # Car info (denormalized for list)
    car_brand: Optional[str] = None
    car_model: Optional[str] = None
    car_year: Optional[int] = None
    car_image_url: Optional[str] = None
    
    # Client info (denormalized for list)
    client_first_name: Optional[str] = None
    client_last_name: Optional[str] = None
    client_phone: Optional[str] = None

    # Manager info (denormalized for client view)
    manager_first_name: Optional[str] = None
    manager_last_name: Optional[str] = None
    manager_phone: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True




class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    reason: Optional[str] = None


class ContactStatusUpdate(BaseModel):
    contact_status: ContactStatus
    note: Optional[str] = None


class ChecklistUpdate(BaseModel):
    checklist: Dict[str, bool]


class RejectionUpdate(BaseModel):
    rejection_reason: RejectionReason
    rejection_note: Optional[str] = None


class AssignOperatorRequest(BaseModel):
    operator_id: UUID

class AssignManagerRequest(BaseModel):
    manager_id: UUID


class AssignManagerRequest(BaseModel):
    manager_id: UUID


class CommentUpdate(BaseModel):
    operator_comment: Optional[str] = None


class InternalNoteUpdate(BaseModel):
    internal_note: Optional[str] = None


class ConfirmCarRequest(BaseModel):
    confirmed: bool = True


class CargoBookingRequest(BaseModel):
    cargo_booking_number: str
    cargo_notes: Optional[str] = None


class ApplicationListParams(BaseModel):
    # Filters
    status: Optional[ApplicationStatus] = None
    contact_status: Optional[ContactStatus] = None
    operator_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    # Special filters
    my_only: bool = False  # For operators - show only assigned
    unassigned: bool = False  # Show only unassigned
    
    # Sorting
    sort_by: str = "created_at"
    sort_order: str = "desc"
    
    # Pagination
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class ApplicationListResponse(BaseModel):
    items: List[ApplicationResponse]
    total: int
    page: int
    per_page: int
    pages: int


class StatusHistoryResponse(BaseModel):
    id: UUID
    old_status: Optional[ApplicationStatus]
    new_status: ApplicationStatus
    changed_by: UUID
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationDetailResponse(ApplicationResponse):
    """Full details including comments."""
    operator_comment: Optional[str] = None
    internal_note: Optional[str] = None
    cargo_notes: Optional[str] = None
    
    # Related data
    client: Optional[UserResponse] = None
    car: Optional[CarResponse] = None
    documents: List[DocumentResponse] = []
    payments: List[PaymentResponse] = []
    status_history: List[StatusHistoryResponse] = []

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1)
    is_internal: bool = False


class CommentResponse(BaseModel):
    id: UUID
    application_id: UUID
    user_id: UUID
    text: str
    is_internal: bool
    created_at: datetime

    class Config:
        from_attributes = True
