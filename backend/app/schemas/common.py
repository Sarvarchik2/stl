"""Pydantic Schemas - Payments, Documents, Blacklist, Settings."""
from pydantic import BaseModel, Field, computed_field
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from ..models.enums import (
    PaymentMethod, PaymentStatus, DocumentType, 
    BlockType, BlacklistReason
)


# --- Payment Schemas ---

class PaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    method: PaymentMethod
    invoice_number: Optional[str] = None


class PaymentResponse(BaseModel):
    id: UUID
    application_id: UUID
    invoice_number: Optional[str]
    amount: Decimal
    method: PaymentMethod
    status: PaymentStatus
    receipt_file_path: Optional[str]
    confirmed_by: Optional[UUID]
    confirmed_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentConfirm(BaseModel):
    confirmed: bool = True


class PaymentReject(BaseModel):
    reason: str = Field(..., min_length=5)


# --- Document Schemas ---

class DocumentResponse(BaseModel):
    id: UUID
    application_id: UUID
    type: DocumentType
    original_filename: Optional[str]
    mime_type: Optional[str]
    file_size: Optional[str]
    file_hash: Optional[str]
    uploaded_by: UUID
    version: str
    created_at: datetime

    @computed_field
    @property
    def download_url(self) -> str:
        return f"/api/v1/documents/{self.id}/download"

    class Config:
        from_attributes = True


class DocumentUpload(BaseModel):
    type: DocumentType
    version: Optional[str] = "1.0"


# --- Blacklist Schemas ---

class BlacklistCreate(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    reason: BlacklistReason
    reason_note: Optional[str] = None
    block_type: Optional[BlockType] = BlockType.DAYS_7


class BlacklistUpdate(BaseModel):
    block_type: Optional[BlockType] = None
    reason_note: Optional[str] = None


class BlacklistResponse(BaseModel):
    id: UUID
    phone: str
    reason: BlacklistReason
    reason_note: Optional[str]
    strike_count: int
    block_type: Optional[BlockType]
    blocked_until: Optional[datetime]
    added_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlacklistListResponse(BaseModel):
    items: List[BlacklistResponse]
    total: int
    page: int
    per_page: int
    pages: int


# --- Settings Schemas ---

class SettingResponse(BaseModel):
    id: UUID
    key: str
    value: str
    description: Optional[str]
    updated_by: Optional[UUID]
    updated_at: datetime

    class Config:
        from_attributes = True


class SettingUpdate(BaseModel):
    value: Any
    reason: Optional[str] = None


# --- Audit Log Schemas ---

class AuditLogResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    ip_address: Optional[str]
    action: str
    entity_type: str
    entity_id: Optional[UUID]
    old_value: Optional[dict]
    new_value: Optional[dict]
    reason: Optional[str]
    details: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListParams(BaseModel):
    user_id: Optional[UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    action: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=200)


class AuditLogListResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    per_page: int
    pages: int


# --- Admin Override Schemas ---

class PriceOverrideRequest(BaseModel):
    new_final_price: Decimal = Field(..., gt=0)
    reason: str = Field(..., min_length=10)


class StatusOverrideRequest(BaseModel):
    new_status: str
    reason: str = Field(..., min_length=10)
