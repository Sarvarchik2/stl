import httpx
import asyncio
import json

async def test_login():
    url = "http://localhost:8000/api/v1/auth/login"
    payload = {
        "phone": "+998901111111",
        "password": "admin123"
    }
    
    print(f"Sending POST to {url}")
    print(f"Payload: {json.dumps(payload)}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            print(f"Status: {response.status_code}")
            print("Response Body:")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_login())
