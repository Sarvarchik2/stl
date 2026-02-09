import asyncio
from sqlalchemy import update, select
from backend.app.database import AsyncSessionLocal
from backend.app.models.user import User
from backend.app.models.enums import Role
from backend.app.services.auth import get_password_hash

async def fix_roles():
    async with AsyncSessionLocal() as db:
        password_hash = get_password_hash("admin123")
        
        # Admin
        await db.execute(
            update(User)
            .where(User.phone == "+998901111111")
            .values(role=Role.ADMIN, password_hash=password_hash)
        )
        # Manager
        await db.execute(
            update(User)
            .where(User.phone == "+998902222222")
            .values(role=Role.MANAGER, password_hash=password_hash)
        )
        # Operator
        await db.execute(
            update(User)
            .where(User.phone == "+998903333333")
            .values(role=Role.OPERATOR, password_hash=password_hash)
        )
        # Supervisor
        await db.execute(
            update(User)
            .where(User.phone == "+998909999999")
            .values(role=Role.SUPERVISOR, password_hash=password_hash)
        )
        
        await db.commit()
        print("Roles and passwords updated successfully!")

if __name__ == "__main__":
    asyncio.run(fix_roles())
