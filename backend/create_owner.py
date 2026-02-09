"""Script to create initial owner user."""
import asyncio
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.enums import Role
from app.services.auth import get_password_hash
from sqlalchemy import select

async def create_owner():
    async with AsyncSessionLocal() as db:
        # Check if owner exists
        result = await db.execute(select(User).where(User.role == Role.OWNER))
        if result.scalar_one_or_none():
            print("Owner already exists.")
            return

        print("Creating Owner account...")
        phone = input("Enter Owner Phone (e.g. +998901234567): ")
        password = input("Enter Owner Password: ")
        
        user = User(
            phone=phone,
            password_hash=get_password_hash(password),
            first_name="Super",
            last_name="Owner",
            role=Role.OWNER,
            is_active=True
        )
        db.add(user)
        await db.commit()
        print(f"Owner created successfully! ID: {user.id}")

if __name__ == "__main__":
    asyncio.run(create_owner())
