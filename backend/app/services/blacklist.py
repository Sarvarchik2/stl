"""Blacklist service."""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.blacklist import Blacklist
from ..models.enums import BlockType


async def is_phone_blocked(db: AsyncSession, phone: str) -> tuple[bool, Optional[str]]:
    """Check if a phone number is blocked. Returns (is_blocked, reason)."""
    result = await db.execute(
        select(Blacklist).where(Blacklist.phone == phone)
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        return False, None
    
    # Check if temporary block has expired
    if entry.blocked_until and entry.blocked_until < datetime.utcnow():
        return False, None
    
    # Permanent or still active block
    if entry.block_type == BlockType.PERMANENT or entry.blocked_until is None:
        return True, f"Phone permanently blocked: {entry.reason.value}"
    
    if entry.blocked_until >= datetime.utcnow():
        return True, f"Phone blocked until {entry.blocked_until}: {entry.reason.value}"
    
    return False, None


def get_block_expiry(block_type: BlockType) -> Optional[datetime]:
    """Get the expiry datetime for a block type."""
    if block_type == BlockType.DAYS_7:
        return datetime.utcnow() + timedelta(days=7)
    elif block_type == BlockType.DAYS_30:
        return datetime.utcnow() + timedelta(days=30)
    else:  # PERMANENT
        return None


async def increment_strike(
    db: AsyncSession, 
    phone: str, 
    reason: str,
    threshold: int = 3
) -> tuple[int, bool]:
    """Increment strike count for a phone. Returns (new_count, is_now_blocked)."""
    result = await db.execute(
        select(Blacklist).where(Blacklist.phone == phone)
    )
    entry = result.scalar_one_or_none()
    
    if entry:
        entry.strike_count += 1
        new_count = entry.strike_count
        
        # Auto-block if threshold reached
        if new_count >= threshold and not entry.block_type:
            entry.block_type = BlockType.DAYS_7
            entry.blocked_until = get_block_expiry(BlockType.DAYS_7)
            return new_count, True
        
        return new_count, False
    
    return 1, False
