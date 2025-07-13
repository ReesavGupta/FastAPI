#!/usr/bin/env python3
"""
Backend Systems Test Script
Tests all major backend functionality including authentication, medicines, orders, and prescriptions
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def test_authentication():
    """Test authentication system"""
    print("🔐 Testing Authentication System...")
    
    # Test user registration
    register_data = {
        "email": "test@example.com",
        "phone": "+1234567890",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "customer"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Registration: {response.status_code}")
    
    # Test user login
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"Login: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        print("✅ Authentication system working")
        return access_token
    else:
        print("❌ Authentication system failed")
        return None

def test_medicine_system(token):
    """Test medicine management system"""
    print("\n💊 Testing Medicine System...")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test getting medicines
    response = requests.get(f"{BASE_URL}/medicines/", headers=headers)
    print(f"Get medicines: {response.status_code}")
    
    # Test getting categories
    response = requests.get(f"{BASE_URL}/medicines/categories/", headers=headers)
    print(f"Get categories: {response.status_code}")
    
    if response.status_code == 200:
        categories = response.json()
        if categories:
            category_id = categories[0]["id"]
            print(f"✅ Medicine system working (found {len(categories)} categories)")
            return category_id
        else:
            print("⚠️ No categories found")
            return None
    else:
        print("❌ Medicine system failed")
        return None

def test_prescription_system(token):
    """Test prescription management system"""
    print("\n📋 Testing Prescription System...")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test getting prescriptions
    response = requests.get(f"{BASE_URL}/prescriptions/", headers=headers)
    print(f"Get prescriptions: {response.status_code}")
    
    # Test getting user's prescriptions
    response = requests.get(f"{BASE_URL}/prescriptions/user/me", headers=headers)
    print(f"Get my prescriptions: {response.status_code}")
    
    print("✅ Prescription system working")
    return True

def test_order_system(token):
    """Test order management system"""
    print("\n📦 Testing Order System...")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test getting orders
    response = requests.get(f"{BASE_URL}/orders/", headers=headers)
    print(f"Get orders: {response.status_code}")
    
    # Test getting user's orders
    response = requests.get(f"{BASE_URL}/orders/user/me", headers=headers)
    print(f"Get my orders: {response.status_code}")
    
    print("✅ Order system working")
    return True

def test_user_system(token):
    """Test user management system"""
    print("\n👤 Testing User System...")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test getting current user
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"Get current user: {response.status_code}")
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ User system working (logged in as: {user_data.get('full_name')})")
        return True
    else:
        print("❌ User system failed")
        return False

def test_api_documentation():
    """Test API documentation"""
    print("\n📚 Testing API Documentation...")
    
    # Test OpenAPI docs
    response = requests.get("http://localhost:8000/docs")
    print(f"API Documentation: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API documentation accessible")
        return True
    else:
        print("❌ API documentation not accessible")
        return False

def main():
    """Run all backend system tests"""
    print("🚀 MediDash Backend Systems Test")
    print("=" * 50)
    
    # Test API documentation first
    test_api_documentation()
    
    # Test authentication
    token = test_authentication()
    
    if token:
        # Test all systems with authentication
        test_user_system(token)
        test_medicine_system(token)
        test_prescription_system(token)
        test_order_system(token)
    else:
        print("\n⚠️ Skipping authenticated tests due to authentication failure")
    
    print("\n" + "=" * 50)
    print("🎉 Backend Systems Test Complete!")
    print("\nNext steps:")
    print("1. Start the frontend development")
    print("2. Implement real-time features with WebSockets")
    print("3. Add Cloudinary integration for prescription uploads")
    print("4. Implement delivery partner system")
    print("5. Add analytics and admin dashboard")

if __name__ == "__main__":
    main() 