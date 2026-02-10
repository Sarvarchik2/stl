
import asyncio
from backend.app.database import AsyncSessionLocal
from backend.app.models.car import Car
from sqlalchemy import select, update

async def update_missing_images():
    image_map = {
        "Chevrolet Tracker": "http://127.0.0.1:8000/uploads/cars/tracker_1.png",
        "Kia K5": "http://127.0.0.1:8000/uploads/cars/k5_1.png",
        "Chevrolet Onix": "http://127.0.0.1:8000/uploads/cars/onix_1.png"
    }
    
    async with AsyncSessionLocal() as db:
        for brand_model, url in image_map.items():
            brand, model = brand_model.split(" ", 1)
            await db.execute(
                update(Car)
                .where(Car.brand == brand, Car.model == model)
                .values(image_url=url, photos=[url])
            )
        await db.commit()
        print("Updated images for Tracker, K5, and Onix.")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(update_missing_images())
