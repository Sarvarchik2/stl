
import requests
import json

def test_login():
    url = "http://localhost:8000/api/v1/auth/login"
    payload = {
        "phone": "+998901111111",
        "password": "admin123"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Testing login for {payload['phone']}...")
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✅ Login successful with +998901111111!")
        else:
            print("❌ Login failed!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
