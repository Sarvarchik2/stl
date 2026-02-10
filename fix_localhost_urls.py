
import asyncio
from backend.app.database import AsyncSessionLocal
from backend.app.models.car import Car
from sqlalchemy import select, update
import json

async def fix_urls():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Car))
        cars = result.scalars().all()
        for car in cars:
            if car.image_url and "localhost" in car.image_url:
                car.image_url = car.image_url.replace("localhost", "127.0.0.1")
            
            if car.photos:
                new_photos = []
                for p in car.photos:
                    if isinstance(p, str) and "localhost" in p:
                        new_photos.append(p.replace("localhost", "127.0.0.1"))
                    else:
                        new_photos.append(p)
                car.photos = new_photos
        
        await db.commit()
        print("Patched localhost to 127.0.0.1 in database.")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(fix_urls())
