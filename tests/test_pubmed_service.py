#!/usr/bin/env python3
"""
Test script for PubMed Service Module
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.pubmed_service import PubMedService, get_species_pubmed_count

def test_pubmed_service():
    """Test the PubMed service functionality"""
    print("Testing PubMed Service...")
    print("=" * 50)
    
    try:
        # Create service instance
        service = PubMedService(email="test@invivodb.com")
        print("✓ Service created successfully")
        
        # Test simple article count
        count = service.get_article_count("cancer")
        print(f"✓ Article count for 'cancer': {count}")
        
        # Test species-specific search
        species_tests = ["Mus musculus", "Rattus norvegicus"]
        
        for species in species_tests:
            count = service.get_species_article_count(species)
            print(f"✓ {species}: {count} articles")
        
        # Test convenience function
        mouse_count = get_species_pubmed_count("Mus musculus")
        print(f"✓ Convenience function - Mouse articles: {mouse_count}")
        
        print("\n" + "=" * 50)
        print("✓ All tests passed! PubMed service is working correctly.")
        
    except Exception as e:
        print(f"✗ Error testing PubMed service: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_pubmed_service()
    sys.exit(0 if success else 1) 