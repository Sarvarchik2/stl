"""Blacklist API routes."""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ..dependencies import DB, AdminUser
from ..models.blacklist import Blacklist
from ..schemas.common import (
    BlacklistCreate, BlacklistUpdate, BlacklistListResponse, BlacklistResponse
)
from ..services.blacklist import increment_strike
from ..services.audit import log_action

router = APIRouter(prefix="/blacklist", tags=["Blacklist"])


@router.get("", response_model=BlacklistListResponse)
async def list_blacklist(
    db: DB,
    user: AdminUser,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """List blacklisted numbers."""
    query = select(Blacklist).order_by(Blacklist.created_at.desc())
    
    # Count
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()
    
    # Pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return BlacklistListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page
    )


@router.post("", response_model=BlacklistResponse)
async def add_to_blacklist(
    request: BlacklistCreate,
    current_user: AdminUser,
    db: DB
):
    """Manually add number to blacklist."""
    # Check if exists
    result = await db.execute(select(Blacklist).where(Blacklist.phone == request.phone))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already in blacklist")
        
    entry = Blacklist(
        phone=request.phone,
        reason=request.reason,
        reason_note=request.reason_note,
        block_type=request.block_type,
        added_by=current_user.id
    )
    
    # Calculate blocked_until based on type
    from ..services.blacklist import get_block_expiry
    entry.blocked_until = get_block_expiry(request.block_type)
    
    db.add(entry)
    await db.flush()
    
    await log_action(
        db=db,
        action="blacklist_added",
        entity_type="blacklist",
        entity_id=entry.id,
        user_id=current_user.id,
        new_value={"phone": request.phone, "reason": request.reason.value}
    )
    
    await db.commit()
    await db.refresh(entry)
    return entry


@router.patch("/{blacklist_id}/unblock", response_model=BlacklistResponse)
async def unblock_number(
    blacklist_id: UUID,
    current_user: AdminUser,
    db: DB
):
    """Unblock a number (Admin only)."""
    result = await db.execute(select(Blacklist).where(Blacklist.id == blacklist_id))
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blacklist entry not found")
        
    entry.block_type = None
    entry.blocked_until = None
    
    await log_action(
        db=db,
        action="blacklist_unblocked",
        entity_type="blacklist",
        entity_id=entry.id,
        user_id=current_user.id
    )
    
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/by-phone/{phone}")
async def unblock_by_phone(
    phone: str,
    current_user: AdminUser,
    db: DB
):
    """Unblock a number by phone (Admin only). Used when activating users."""
    result = await db.execute(select(Blacklist).where(Blacklist.phone == phone))
    entry = result.scalar_one_or_none()
    
    if not entry:
        # Not in blacklist, that's fine
        return {"status": "ok", "message": "Phone not in blacklist"}
    
    # Remove from blacklist completely
    await db.delete(entry)
    
    await log_action(
        db=db,
        action="blacklist_removed",
        entity_type="blacklist",
        entity_id=entry.id,
        user_id=current_user.id,
        old_value={"phone": phone}
    )
    
    await db.commit()
    return {"status": "ok", "message": "Phone removed from blacklist"}
