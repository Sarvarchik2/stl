
import asyncio
from app.database import AsyncSessionLocal
from app.models.blacklist import Blacklist
from sqlalchemy import select

async def check_blacklist():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Blacklist))
        items = result.scalars().all()
        print(f"Total in blacklist: {len(items)}")
        for item in items:
            print(f"ID: {item.id}, Phone: {item.phone}, Reason: {item.reason}")

if __name__ == "__main__":
    asyncio.run(check_blacklist())
