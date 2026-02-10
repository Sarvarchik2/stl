
import asyncio
from backend.app.database import AsyncSessionLocal
from backend.app.models.car import Car
from sqlalchemy import select

async def check_urls():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Car))
        cars = result.scalars().all()
        for c in cars:
            print(f"{c.brand} {c.model}: {c.image_url}")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(check_urls())
