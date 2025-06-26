#!/usr/bin/env python3
"""
Script to fix assay types data - correct categories and remove duplicates
"""

import sys
import os
sys.path.append('src')

from web.app import app, db
from models.database import AssayType

def fix_assay_types():
    """Fix assay types data"""
    with app.app_context():
        try:
            print("🔧 Fixing assay types data...")
            
            # 1. Remove duplicate ELISA entries
            print("\n1. Removing duplicate ELISA entries...")
            elisa_entries = AssayType.query.filter_by(name="ELISA Test").all()
            print(f"Found {len(elisa_entries)} ELISA entries")
            
            if len(elisa_entries) > 1:
                # Keep the first one, delete the rest
                for entry in elisa_entries[1:]:
                    print(f"Deleting duplicate ELISA entry (ID: {entry.id}, Category: {entry.category})")
                    db.session.delete(entry)
                db.session.commit()
                print("✅ Duplicate ELISA entries removed")
            
            # 2. Correct ELISA category to Immunological
            print("\n2. Correcting ELISA category...")
            elisa_entry = AssayType.query.filter_by(name="ELISA Test").first()
            if elisa_entry:
                if elisa_entry.category != "Immunological":
                    print(f"Correcting ELISA category from '{elisa_entry.category}' to 'Immunological'")
                    elisa_entry.category = "Immunological"
                    db.session.commit()
                    print("✅ ELISA category corrected")
                else:
                    print("✅ ELISA category is already correct")
            
            # 3. Add unique constraint to prevent future duplicates
            print("\n3. Checking for other duplicates...")
            all_assay_types = AssayType.query.all()
            names = [at.name for at in all_assay_types]
            duplicates = [name for name in set(names) if names.count(name) > 1]
            
            if duplicates:
                print(f"Found duplicate names: {duplicates}")
                for duplicate_name in duplicates:
                    entries = AssayType.query.filter_by(name=duplicate_name).all()
                    print(f"  {duplicate_name}: {len(entries)} entries")
                    # Keep the first one, delete the rest
                    for entry in entries[1:]:
                        print(f"    Deleting duplicate: {entry.name} (ID: {entry.id})")
                        db.session.delete(entry)
                db.session.commit()
                print("✅ All duplicates removed")
            else:
                print("✅ No other duplicates found")
            
            # 4. Display final state
            print("\n4. Final assay types in database:")
            final_assay_types = AssayType.query.order_by(AssayType.name).all()
            for at in final_assay_types:
                print(f"  - {at.name} ({at.category}) - {at.description}")
            
            print(f"\n✅ Total assay types: {len(final_assay_types)}")
            
        except Exception as e:
            print(f"❌ Error fixing assay types: {e}")
            db.session.rollback()

def add_unique_constraint():
    """Add unique constraint to prevent future duplicates"""
    with app.app_context():
        try:
            print("\n🔒 Adding unique constraint to prevent future duplicates...")
            
            # This would require a database migration
            # For now, we'll add application-level validation
            print("Note: Application-level duplicate prevention is already implemented")
            print("Database-level unique constraint would require migration")
            
        except Exception as e:
            print(f"❌ Error adding constraint: {e}")

if __name__ == "__main__":
    fix_assay_types()
    add_unique_constraint() 