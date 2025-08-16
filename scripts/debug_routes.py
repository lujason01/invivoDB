#!/usr/bin/env python3
"""
Debug Flask routes to see what's registered
"""

import requests

def list_routes():
    """List all available routes from the Flask app"""
    base_url = "http://localhost:5000"
    
    print("📋 Available Routes:")
    print("=" * 50)
    
    # Try to get route info from a simple endpoint
    routes_to_test = [
        "/",
        "/dashboard", 
        "/api/v1/",
        "/api/v1/docs/",
        "/api/v1/species/",
        "/api/v1/animals/",
        "/api/v1/experiments/"
    ]
    
    for route in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            status = "✅" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"{status} {route}")
        except Exception as e:
            print(f"❌ {route} - Error: {e}")

if __name__ == "__main__":
    list_routes()
