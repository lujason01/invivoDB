#!/usr/bin/env python3
"""
Test script to verify assay type functionality
"""

import sys
import os
sys.path.append('src')

from web.app import app, db
from models.database import AssayType

def test_add_assay_type():
    """Test adding a new assay type"""
    with app.app_context():
        try:
            # Check current count
            initial_count = AssayType.query.count()
            print(f"Initial assay types count: {initial_count}")
            
            # Create a new assay type
            new_assay_type = AssayType(
                name="ELISA Test",
                category="Immunological",
                description="Enzyme-linked immunosorbent assay for protein detection",
                standard_protocol="Standard ELISA protocol with 96-well plates",
                units="ng/mL"
            )
            
            # Add to database
            db.session.add(new_assay_type)
            db.session.commit()
            
            # Check new count
            new_count = AssayType.query.count()
            print(f"New assay types count: {new_count}")
            
            # Verify the new assay type was added
            added_assay_type = AssayType.query.filter_by(name="ELISA Test").first()
            if added_assay_type:
                print("✅ Successfully added assay type:")
                print(f"  ID: {added_assay_type.id}")
                print(f"  Name: {added_assay_type.name}")
                print(f"  Category: {added_assay_type.category}")
                print(f"  Description: {added_assay_type.description}")
                print(f"  Protocol: {added_assay_type.standard_protocol}")
                print(f"  Units: {added_assay_type.units}")
                print(f"  Created: {added_assay_type.created_at}")
            else:
                print("❌ Failed to find added assay type")
            
            # Test duplicate prevention
            duplicate_assay_type = AssayType(
                name="ELISA Test",  # Same name
                category="Molecular",
                description="Duplicate test"
            )
            
            db.session.add(duplicate_assay_type)
            try:
                db.session.commit()
                print("❌ Duplicate assay type was added (should have been prevented)")
            except Exception as e:
                print(f"✅ Duplicate prevention working: {e}")
                db.session.rollback()
            
            # List all assay types
            print("\nAll assay types in database:")
            all_assay_types = AssayType.query.all()
            for at in all_assay_types:
                print(f"  - {at.name} ({at.category})")
            
        except Exception as e:
            print(f"❌ Error testing assay type functionality: {e}")
            db.session.rollback()

if __name__ == "__main__":
    test_add_assay_type() 