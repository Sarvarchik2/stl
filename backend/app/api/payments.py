"""Payments API routes."""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from datetime import datetime

from ..dependencies import DB, CurrentUser, ManagerUser
from ..models.payment import Payment
from ..models.application import Application
from ..models.enums import PaymentStatus, ApplicationStatus
from ..schemas.common import (
    PaymentCreate, PaymentResponse, PaymentConfirm, PaymentReject,
    PaymentListResponse
)
from ..services.audit import log_action

router = APIRouter(prefix="/applications/{app_id}/payments", tags=["Payments"])

# Global payments router for admin view
global_router = APIRouter(prefix="/payments", tags=["Payments Global"])

@global_router.get("", response_model=PaymentListResponse)
async def list_all_payments(
    db: DB,
    user: ManagerUser,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """List all payments across all applications (Manager/Admin only)."""
    from ..models.car import Car
    from ..models.user import User
    from sqlalchemy import func
    
    # Count total
    total_query = select(func.count(Payment.id))
    total = (await db.execute(total_query)).scalar() or 0
    
    query = (
        select(Payment, Application, Car, User)
        .join(Application, Payment.application_id == Application.id)
        .join(Car, Application.car_id == Car.id)
        .join(User, Application.client_id == User.id)
        .order_by(Payment.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    
    items = []
    for row in result.all():
        payment, app, car, client = row
        # Add virtual fields for the response model
        res = PaymentResponse.model_validate(payment)
        res.car_name = f"{car.brand} {car.model}"
        res.client_name = f"{client.first_name} {client.last_name}"
        res.type = "income" # Default for now
        items.append(res)
        
    return {
        "items": items,
        "total": total
    }

@global_router.get("/stats")
async def get_payment_stats(db: DB, user: ManagerUser):
    """Get overall payment statistics for the payments page."""
    from sqlalchemy import func
    
    # Financial states: PAID, DELIVERED, COMPLETED
    financial_statuses = [
        ApplicationStatus.PAID,
        ApplicationStatus.DELIVERED,
        ApplicationStatus.COMPLETED
    ]
    
    # Turnover (Sum of final_price for deals that are paid or delivered)
    turnover_query = select(func.sum(Application.final_price)).where(
        Application.status.in_(financial_statuses)
    )
    turnover = (await db.execute(turnover_query)).scalar() or 0
    
    # Profit (Sum of final_price - source_price_snapshot)
    profit_expr = Application.final_price - func.coalesce(Application.source_price_snapshot, 0)
    profit_query = select(func.sum(profit_expr)).where(
        Application.status.in_(financial_statuses)
    )
    profit = (await db.execute(profit_query)).scalar() or 0
    
    # Pending volume (Sum of Applications with status CONFIRMED)
    # These are deals that are "expected" to be paid soon.
    pending_query = select(func.sum(Application.final_price)).where(
        Application.status == ApplicationStatus.CONFIRMED
    )
    pending_total = (await db.execute(pending_query)).scalar() or 0
    
    return {
        "turnover": float(turnover),
        "profit": float(profit),
        "pending_total": float(pending_total)
    }


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    app_id: UUID,
    request: PaymentCreate,
    current_user: ManagerUser,
    db: DB
):
    """Create a new payment invoice (Manager only)."""
    # Check application
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    payment = Payment(
        application_id=app.id,
        amount=request.amount,
        method=request.method,
        invoice_number=request.invoice_number,
        created_by=current_user.id,
        status=PaymentStatus.PENDING
    )
    db.add(payment)
    await db.flush()
    
    # Update app status if needed
    if app.status == ApplicationStatus.CONFIRMED:
        app.status = ApplicationStatus.WAITING_PAYMENT
        
    await log_action(
        db=db,
        action="payment_invoice_created",
        entity_type="payment",
        entity_id=payment.id,
        user_id=current_user.id,
        new_value={"amount": str(request.amount), "invoice": request.invoice_number}
    )
    
    await db.commit()
    await db.refresh(payment)
    return payment


@router.post("/{payment_id}/receipt", response_model=PaymentResponse)
async def upload_receipt(
    app_id: UUID,
    payment_id: UUID,
    current_user: CurrentUser,
    db: DB,
    file: UploadFile = File(...)
):
    """Upload payment receipt (Client or Manager)."""
    # Verify payment exists
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        
    # Verify access
    if current_user.role == "client":
        # Check if app belongs to client
        app_res = await db.execute(select(Application).where(Application.id == app_id))
        app = app_res.scalar_one_or_none()
        if not app or app.client_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            
    # Save file (Mock implementation for now)
    # In real app: save to disk/S3 and store path
    file_path = f"uploads/receipts/{payment_id}_{file.filename}"
    
    payment.receipt_file_path = file_path
    
    await db.commit()
    await db.refresh(payment)
    return payment


@router.patch("/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
    app_id: UUID,
    payment_id: UUID,
    request: PaymentConfirm,
    current_user: ManagerUser,
    db: DB
):
    """Confirm payment (Manager only)."""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        
    payment.status = PaymentStatus.CONFIRMED
    payment.confirmed_by = current_user.id
    payment.confirmed_at = datetime.utcnow()
    
    await log_action(
        db=db,
        action="payment_confirmed",
        entity_type="payment",
        entity_id=payment.id,
        user_id=current_user.id
    )
    
    await db.commit()
    await db.refresh(payment)
    return payment


@router.patch("/{payment_id}/reject", response_model=PaymentResponse)
async def reject_payment(
    app_id: UUID,
    payment_id: UUID,
    request: PaymentReject,
    current_user: ManagerUser,
    db: DB
):
    """Reject payment (Manager only)."""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        
    payment.status = PaymentStatus.REJECTED
    payment.rejection_reason = request.reason
    payment.confirmed_by = current_user.id
    payment.confirmed_at = datetime.utcnow()
    
    await log_action(
        db=db,
        action="payment_rejected",
        entity_type="payment",
        entity_id=payment.id,
        user_id=current_user.id,
        reason=request.reason
    )
    
    await db.commit()
    await db.refresh(payment)
    return payment
