import asyncio
import httpx
import sys

# Backend URL
API_URL = "http://localhost:8000/api/v1"

async def test_otp_flow():
    print("🚀 Testing OTP Registration Flow")
    
    phone = input("Enter phone number (e.g., +998901234567): ").strip()
    if not phone:
        print("Phone number required.")
        return

    async with httpx.AsyncClient() as client:
        # 1. Send OTP
        print(f"\n📡 Requesting OTP for {phone}...")
        response = await client.post(f"{API_URL}/auth/send-otp", json={"phone": phone})
        
        if response.status_code == 200:
            print("✅ OTP request successful. Check Telegram!")
        else:
            print(f"❌ OTP request failed: {response.text}")
            return
        
        # 2. Verify OTP
        code = input("\n🔑 Enter the code received on Telegram: ").strip()
        
        print(f"📡 Verifying OTP {code}...")
        verify_response = await client.post(f"{API_URL}/auth/verify-otp", json={
            "phone": phone,
            "code": code
        })
        
        if verify_response.status_code == 200:
            token_data = verify_response.json()
            print("✅ OTP Verification Successful!")
            print(f"🎉 Access Token: {token_data.get('access_token')[:20]}...")
        else:
            print(f"❌ Verification failed: {verify_response.text}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_otp_flow())
