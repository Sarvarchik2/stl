
import asyncio
import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import select
from backend.app.database import AsyncSessionLocal
from backend.app.models.car import Car

async def seed_cars():
    async with AsyncSessionLocal() as db:
        print("Seeding new cars with full information and photos...")
        
        cars_to_add = [
            {
                "brand": "Chevrolet",
                "make": "Chevrolet",
                "model": "Tahoe",
                "year": 2024,
                "trim": "High Country",
                "body_type": "SUV",
                "mileage": 0,
                "exterior_color": "Black",
                "interior_color": "Jet Black",
                "transmission": "10-Speed Automatic",
                "drivetrain": "4WD",
                "fuel_type": "Gasoline",
                "engine": "6.2L V8",
                "mpg_city": 14,
                "mpg_highway": 19,
                "source_price_usd": Decimal("82000.00"),
                "final_price_usd": Decimal("91840.00"),
                "dealer": "STL Premium Luxury",
                "location_city": "Tashkent",
                "image_url": "http://localhost:8000/uploads/cars/tahoe_1.png",
                "photos": [
                    "http://localhost:8000/uploads/cars/tahoe_2.png",
                    "http://localhost:8000/uploads/cars/tahoe_3.png",
                    "http://localhost:8000/uploads/cars/tahoe_4.png"
                ],
                "features": ["Panoramic Sunroof", "22-inch Wheels", "Super Cruise", "Air Suspension", "Bose Audio"],
                "is_active": True
            },
            {
                "brand": "Toyota",
                "make": "Toyota",
                "model": "Camry",
                "year": 2025,
                "trim": "XSE",
                "body_type": "Sedan",
                "mileage": 0,
                "exterior_color": "Wind Chill Pearl",
                "interior_color": "Light Gray Leather",
                "transmission": "eCVT",
                "drivetrain": "AWD",
                "fuel_type": "Hybrid",
                "engine": "2.5L Hybrid",
                "mpg_city": 44,
                "mpg_highway": 43,
                "source_price_usd": Decimal("36000.00"),
                "final_price_usd": Decimal("40320.00"),
                "dealer": "Toyo City",
                "location_city": "Tashkent",
                "image_url": "http://localhost:8000/uploads/cars/camry_1.png",
                "photos": [
                    "http://localhost:8000/uploads/cars/camry_2.png",
                    "http://localhost:8000/uploads/cars/camry_3.png",
                    "http://localhost:8000/uploads/cars/camry_4.png"
                ],
                "features": ["Dual-zone Climate", "JBL Sound System", "Wireless Charging", "Blind Spot Monitor"],
                "is_active": True
            },
            {
                "brand": "Hyundai",
                "make": "Hyundai",
                "model": "Santa Fe",
                "year": 2024,
                "trim": "Calligraphy",
                "body_type": "SUV",
                "mileage": 0,
                "exterior_color": "Ecotronic Gray",
                "interior_color": "Pecan Brown Leather",
                "transmission": "8-Speed DCT",
                "drivetrain": "HTRAC AWD",
                "fuel_type": "Gasoline",
                "engine": "2.5T I4",
                "mpg_city": 20,
                "mpg_highway": 28,
                "source_price_usd": Decimal("48000.00"),
                "final_price_usd": Decimal("53760.00"),
                "dealer": "Hyundai Tashkent Center",
                "location_city": "Tashkent",
                "image_url": "http://localhost:8000/uploads/cars/santa_1.png",
                "photos": [
                    "http://localhost:8000/uploads/cars/santa_2.png",
                    "http://localhost:8000/uploads/cars/santa_3.png",
                    "http://localhost:8000/uploads/cars/santa_4.png"
                ],
                "features": ["Nappa Leather", "Dual Wireless Charging", "Digital Key", "Surround View Monitor"],
                "is_active": True
            }
        ]

        for car_data in cars_to_add:
            car = Car(id=uuid.uuid4(), **car_data)
            db.add(car)
            print(f"Added {car.brand} {car.model} {car.year}")

        await db.commit()
        print("Success! Cars seeded.")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(seed_cars())
