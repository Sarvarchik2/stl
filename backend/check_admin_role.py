
import asyncio
from app.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def check_admin():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for user in users:
            print(f"User: {user.first_name} {user.last_name}, Role: {user.role}, Active: {user.is_active}")

if __name__ == "__main__":
    asyncio.run(check_admin())
