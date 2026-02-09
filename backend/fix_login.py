
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.services.auth import get_password_hash, verify_password

async def fix_admin_user():
    async with AsyncSessionLocal() as db:
        print("🔍 Checking users...")
        
        # Ищем админа
        result = await db.execute(select(User).where(User.phone == "+998901111111"))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"✅ Users found: ID={user.id}, Role={user.role}")
            
            # Проверяем пароль
            is_valid = verify_password("admin123", user.password_hash)
            print(f"🔑 Password 'admin123' valid? {is_valid}")
            
            if not is_valid:
                print("⚠️ Password mismatch! Resetting password to 'admin123'...")
                user.password_hash = get_password_hash("admin123")
                db.add(user)
                await db.commit()
                print("✅ Password reset successfully.")
            else:
                print("✅ Password is correct.")
                
        else:
            print("❌ User +998901111111 not found! Creating...")
            from app.models.enums import Role
            new_admin = User(
                phone="+998901111111",
                password_hash=get_password_hash("admin123"),
                first_name="Admin",
                last_name="System",
                role=Role.ADMIN,
                is_active=True
            )
            db.add(new_admin)
            await db.commit()
            print("✅ Admin user created successfully.")

if __name__ == "__main__":
    asyncio.run(fix_admin_user())
