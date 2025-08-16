#!/usr/bin/env python3
"""
Simple API debug script to check what's wrong
"""

import requests
import traceback

def check_api():
    """Check basic API connectivity"""
    base_url = "http://localhost:5000"
    
    print("🔍 Debugging API...")
    
    # Test basic Flask app
    try:
        print("\n1. Testing basic Flask app...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test API docs endpoint
    try:
        print("\n2. Testing API docs endpoint...")
        response = requests.get(f"{base_url}/api/v1/docs/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test species endpoint
    try:
        print("\n3. Testing species endpoint...")
        response = requests.get(f"{base_url}/api/v1/species/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        else:
            print(f"   Success! Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    check_api()
