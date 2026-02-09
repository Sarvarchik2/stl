
import asyncio
from app.database import AsyncSessionLocal
from app.models.car import Car
from app.models.application import Application
from app.models.user import User
from app.models.enums import ApplicationStatus
from sqlalchemy import select

async def seed_data():
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding data...")
        
        # 1. Create a Car
        result = await db.execute(select(Car).where(Car.vin == "TESTVIN123456789"))
        if not result.scalar_one_or_none():
            car = Car(
                brand="BYD",
                make="BYD",
                model="Song Plus Champion",
                year=2024,
                vin="TESTVIN123456789",
                source_price_usd=28000.00,
                final_price_usd=32500.00,
                image_url="https://w7.pngwing.com/pngs/38/708/png-transparent-car-mercedes-car-love-compact-car-vehicle-thumbnail.png",
                features=["Panaromic Roof", "360 Camera", "Leather Seats"],
                photos=["https://w7.pngwing.com/pngs/38/708/png-transparent-car-mercedes-car-love-compact-car-vehicle-thumbnail.png"]
            )
            db.add(car)
            await db.flush() # get ID
            print(f"✅ Created car: {car.brand} {car.model}")
            
            # 2. Get User
            result = await db.execute(select(User).where(User.phone == "+998901111111"))
            user = result.scalar_one_or_none()
            
            # 3. Create Application
            if user:
                app = Application(
                   client_id=user.id,
                   car_id=car.id,
                   status=ApplicationStatus.NEW,
                   final_price=32500.00,
                   source_price_snapshot=28000.00
                )
                db.add(app)
                print(f"✅ Created application for user: {user.first_name}")
                
        await db.commit()
        print("🎉 Seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_data())
