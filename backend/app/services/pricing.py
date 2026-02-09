"""Pricing service."""
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.audit import Setting
from ..config import settings as app_settings


async def get_markup_percent(db: AsyncSession) -> Decimal:
    """Get the current markup percentage from settings."""
    result = await db.execute(
        select(Setting).where(Setting.key == "markup_percent")
    )
    setting = result.scalar_one_or_none()
    
    if setting:
        return Decimal(setting.value)
    return Decimal(str(app_settings.DEFAULT_MARKUP_PERCENT))


def calculate_final_price(source_price: Decimal, markup_percent: Decimal) -> Decimal:
    """Calculate final price with markup."""
    multiplier = 1 + (markup_percent / 100)
    return (source_price * multiplier).quantize(Decimal("0.01"))


async def get_final_price(db: AsyncSession, source_price: Decimal) -> tuple[Decimal, Decimal]:
    """Get final price and markup percent."""
    markup = await get_markup_percent(db)
    final = calculate_final_price(source_price, markup)
    return final, markup
