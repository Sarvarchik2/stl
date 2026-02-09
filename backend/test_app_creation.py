
import asyncio
from uuid import UUID
from app.database import AsyncSessionLocal
from app.models.application import Application
from app.models.user import User
from app.models.car import Car
from app.models.enums import ApplicationStatus, Role, ContactStatus
from sqlalchemy import select

async def test_create_app():
    async with AsyncSessionLocal() as db:
        # Get an admin
        res = await db.execute(select(User).where(User.role == Role.ADMIN).limit(1))
        admin = res.scalar_one()
        
        # Get a car
        res = await db.execute(select(Car).limit(1))
        car = res.scalar_one()
        
        # Get a client
        res = await db.execute(select(User).where(User.role == Role.CLIENT).limit(1))
        client = res.scalar_one()
        
        app = Application(
            client_id=client.id,
            car_id=car.id,
            operator_id=admin.id,
            source_price_snapshot=car.source_price_usd,
            markup_percent=10,
            final_price=car.source_price_usd * 1.1,
            status=ApplicationStatus.NEW,
            contact_status=ContactStatus.CONTACTED,
            internal_note="Test manual creation",
            checklist={
                "confirmed_interest": True,
                "confirmed_budget": False,
                "confirmed_timeline": False,
                "agreed_visit": False,
                "agreed_contract": False
            }
        )
        db.add(app)
        await db.commit()
        print(f"Created app with ID: {app.id}")

if __name__ == "__main__":
    asyncio.run(test_create_app())
