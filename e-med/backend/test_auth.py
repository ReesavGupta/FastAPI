import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_auth_flow():
    """Test the complete authentication flow"""
    
    # 1. Register a user
    register_data = {
        "email": "admin@medidash.com",
        "phone": "1234567890",
        "full_name": "Admin User",
        "role": "pharmacy_admin",
        "password": "Admin@123",
        "pharmacy_name": "MediDash Pharmacy",
        "pharmacy_address": "123 Main St",
        "license_number": "PH123456"
    }
    
    print("1. Registering user...")
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 200:
        print("✅ Registration successful")
        token_data = response.json()
        print(f"Token: {token_data['access_token'][:50]}...")
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(response.text)
        return
    
    # 2. Login to get a fresh token
    login_data = {
        "email": "admin@medidash.com",
        "password": "Admin@123"
    }
    
    print("\n2. Logging in...")
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        print("✅ Login successful")
        token_data = response.json()
        token = token_data['access_token']
        print(f"Token: {token[:50]}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return
    
    # 3. Test protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n3. Testing protected endpoint...")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if response.status_code == 200:
        print("✅ Protected endpoint access successful")
        user_data = response.json()
        print(f"User: {user_data['full_name']} ({user_data['role']})")
    else:
        print(f"❌ Protected endpoint failed: {response.status_code}")
        print(response.text)
    
    # 4. Test medicine creation (admin only)
    medicine_data = {
        "name": "Paracetamol",
        "generic_name": "Acetaminophen",
        "description": "Pain reliever and fever reducer",
        "manufacturer": "Generic Pharma",
        "dosage_form": "tablet",
        "strength": "500mg",
        "prescription_required": False,
        "price": 5.99,
        "stock_quantity": 100,
        "min_stock_level": 10
    }
    
    print("\n4. Testing medicine creation...")
    response = requests.post(f"{BASE_URL}/medicines/", json=medicine_data, headers=headers)
    if response.status_code == 200:
        print("✅ Medicine creation successful")
        medicine = response.json()
        print(f"Medicine: {medicine['name']} - ${medicine['price']}")
    else:
        print(f"❌ Medicine creation failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_auth_flow() 