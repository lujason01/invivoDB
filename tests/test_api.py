#!/usr/bin/env python3
"""
InvivoDB REST API Test Script

This script demonstrates how to test the REST API endpoints.
Make sure the Flask app is running before executing this script.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5000/api/v1"
HEADERS = {"Content-Type": "application/json"}

def print_response(response, title):
    """Pretty print API response"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        print("Response:")
        print(json.dumps(data, indent=2))
    except:
        print("Response Text:", response.text)

def test_species_api():
    """Test Species API endpoints"""
    print("\n🧬 TESTING SPECIES API")
    
    # 1. Get all species
    response = requests.get(f"{BASE_URL}/species/")
    print_response(response, "GET /species/ - List all species")
    
    # 2. Create a new species
    new_species = {
        "common_name": "Golden Hamster",
        "scientific_name": "Mesocricetus auratus",
        "taxonomy_id": "10036",
        "description": "A small rodent commonly used in research"
    }
    
    response = requests.post(f"{BASE_URL}/species/", 
                           json=new_species, 
                           headers=HEADERS)
    print_response(response, "POST /species/ - Create new species")
    
    if response.status_code == 201:
        species_id = response.json().get('id')
        
        # 3. Get specific species
        response = requests.get(f"{BASE_URL}/species/{species_id}")
        print_response(response, f"GET /species/{species_id} - Get specific species")
        
        # 4. Update species
        update_data = {
            "description": "Updated: A small rodent commonly used in biomedical research"
        }
        response = requests.put(f"{BASE_URL}/species/{species_id}", 
                              json=update_data, 
                              headers=HEADERS)
        print_response(response, f"PUT /species/{species_id} - Update species")

def test_animals_api():
    """Test Animals API endpoints"""
    print("\n🐭 TESTING ANIMALS API")
    
    # 1. Get all animals
    response = requests.get(f"{BASE_URL}/animals/")
    print_response(response, "GET /animals/ - List all animals")
    
    # 2. Generate accession number
    response = requests.get(f"{BASE_URL}/animals/generate-accession?species_id=1")
    print_response(response, "GET /animals/generate-accession - Generate accession number")
    
    # 3. Create a new animal
    new_animal = {
        "species_id": 1,
        "strain": "C57BL/6",
        "age_at_start": 8.0,
        "weight_at_start": 25.5,
        "sex": "Male",
        "genetic_background": "Inbred",
        "housing_conditions": "Standard laboratory conditions",
        "ethical_approval": "IACUC-2025-001"
    }
    
    response = requests.post(f"{BASE_URL}/animals/", 
                           json=new_animal, 
                           headers=HEADERS)
    print_response(response, "POST /animals/ - Create new animal")
    
    if response.status_code == 201:
        animal_id = response.json().get('id')
        accession_number = response.json().get('accession_number')
        
        # 4. Get specific animal
        response = requests.get(f"{BASE_URL}/animals/{animal_id}")
        print_response(response, f"GET /animals/{animal_id} - Get specific animal")
        
        # 5. Get animal by accession number
        response = requests.get(f"{BASE_URL}/animals/accession/{accession_number}")
        print_response(response, f"GET /animals/accession/{accession_number} - Get by accession")
        
        return animal_id
    
    return None

def test_experiments_api(animal_id=None):
    """Test Experiments API endpoints"""
    print("\n🧪 TESTING EXPERIMENTS API")
    
    # 1. Get all experiments
    response = requests.get(f"{BASE_URL}/experiments/")
    print_response(response, "GET /experiments/ - List all experiments")
    
    # 2. Create a new experiment (if we have an animal)
    if animal_id:
        new_experiment = {
            "title": "Test Experiment - Drug Efficacy Study",
            "animal_id": animal_id,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "study_design": "Randomized",
            "primary_endpoint": "Tumor size reduction",
            "secondary_endpoints": "Survival rate, side effects",
            "sample_size": 10,
            "blinding": True,
            "randomization": True,
            "notes": "This is a test experiment created via API",
            "data_availability": "Private"
        }
        
        response = requests.post(f"{BASE_URL}/experiments/", 
                               json=new_experiment, 
                               headers=HEADERS)
        print_response(response, "POST /experiments/ - Create new experiment")
        
        if response.status_code == 201:
            experiment_id = response.json().get('id')
            
            # 3. Get specific experiment
            response = requests.get(f"{BASE_URL}/experiments/{experiment_id}")
            print_response(response, f"GET /experiments/{experiment_id} - Get specific experiment")
            
            # 4. Update experiment
            update_data = {
                "notes": "Updated: This experiment was modified via API"
            }
            response = requests.put(f"{BASE_URL}/experiments/{experiment_id}", 
                                  json=update_data, 
                                  headers=HEADERS)
            print_response(response, f"PUT /experiments/{experiment_id} - Update experiment")

def test_filtering_and_pagination():
    """Test filtering and pagination features"""
    print("\n🔍 TESTING FILTERING & PAGINATION")
    
    # Test pagination
    response = requests.get(f"{BASE_URL}/animals/?page=1&per_page=5")
    print_response(response, "GET /animals/?page=1&per_page=5 - Pagination test")
    
    # Test search
    response = requests.get(f"{BASE_URL}/experiments/?search=test")
    print_response(response, "GET /experiments/?search=test - Search test")
    
    # Test filtering
    response = requests.get(f"{BASE_URL}/animals/?species_id=1&sex=Male")
    print_response(response, "GET /animals/?species_id=1&sex=Male - Filter test")

def test_error_handling():
    """Test error handling"""
    print("\n❌ TESTING ERROR HANDLING")
    
    # Test 404 errors
    response = requests.get(f"{BASE_URL}/species/99999")
    print_response(response, "GET /species/99999 - Test 404 error")
    
    # Test validation errors
    invalid_animal = {
        "species_id": "invalid",  # Should be integer
        "age_at_start": -5        # Should be positive
    }
    
    response = requests.post(f"{BASE_URL}/animals/", 
                           json=invalid_animal, 
                           headers=HEADERS)
    print_response(response, "POST /animals/ (invalid data) - Test validation error")

def main():
    """Run all API tests"""
    print("🚀 STARTING API TESTS")
    print("Make sure the Flask app is running at http://localhost:5000")
    print("Visit http://localhost:5000/api/v1/docs/ for interactive API documentation")
    
    try:
        # Test if API is accessible
        response = requests.get(f"{BASE_URL}/species/", timeout=5)
        if response.status_code != 200:
            print(f"❌ API not accessible. Status: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure to start the Flask app first:")
        print("   cd src/web")
        print("   python app.py")
        return
    
    # Run tests
    test_species_api()
    animal_id = test_animals_api()
    test_experiments_api(animal_id)
    test_filtering_and_pagination()
    test_error_handling()
    
    print(f"\n{'='*50}")
    print("🎉 API TESTS COMPLETED")
    print("Visit http://localhost:5000/api/v1/docs/ for interactive testing")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
