import asyncio
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.database import AsyncSessionLocal
from backend.app.models.user import User
from sqlalchemy import select

async def check_users():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        print(f"Total Users: {len(users)}")
        for user in users:
            print(f"ID: {user.id}, Phone: {user.phone}, Role: {user.role.value}, Active: {user.is_active}")

if __name__ == "__main__":
    asyncio.run(check_users())
