import asyncio
import asyncpg

DB_CONFIG = {
    "user": "postgres",
    "password": "admin123",
    "database": "postgres",
    "host": "localhost",
    "port": 5433
}

async def reset_db():
    conn = await asyncpg.connect(**DB_CONFIG)
    try:
        print("Dropping cars_catalog table to update schema...")
        await conn.execute("DROP TABLE IF EXISTS cars_catalog CASCADE")
        print("Table dropped successfully.")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(reset_db())
