
import asyncio
from backend.app.database import AsyncSessionLocal
from backend.app.models.car import Car
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

async def update_car_photos():
    # High quality Unsplash car placeholders
    car_interior = "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1024&q=80"
    car_dash = "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1024&q=80"
    car_wheel = "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1024&q=80"
    ev_charge = "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=1024&q=80"

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Car))
        cars = result.scalars().all()
        
        for car in cars:
            photos = car.photos or []
            if car.image_url and car.image_url not in photos:
                photos.insert(0, car.image_url)
            
            # Fill up to at least 3
            if len(photos) < 2:
                photos.append(car_interior)
            if len(photos) < 3:
                photos.append(car_dash if car.brand != "BYD" else ev_charge)
                
            car.photos = photos
            flag_modified(car, "photos")
            print(f"Updated {car.brand} {car.model}: {len(car.photos)} photos")
        
        await db.commit()
        print("All car photos updated successfully.")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(update_car_photos())
