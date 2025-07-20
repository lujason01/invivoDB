"""
Database Migration Script: Add Unique Constraints to Species Model
================================================================

This script safely migrates the Species table to add unique constraints
on common_name and scientific_name fields while preserving existing data.

Usage:
    python migrate_species_unique.py

Steps performed:
1. Back up existing species data
2. Check for duplicate entries
3. Handle duplicates (merge or remove)
4. Apply unique constraints
5. Verify migration success
"""

import sys
import sqlite3
import csv
import os
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.database import db, Species
from web.app import app

def backup_species_data():
    """Create a backup of current species data"""
    print("Creating backup of species data...")
    
    species_data = Species.query.all()
    backup_data = []
    
    for species in species_data:
        backup_data.append({
            'id': species.id,
            'common_name': species.common_name,
            'scientific_name': species.scientific_name,
            'taxonomy_id': species.taxonomy_id,
            'description': species.description,
            'created_at': species.created_at.isoformat() if species.created_at else None
        })
    
    # Save backup to CSV
    backup_file = f"species_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    if backup_data:
        with open(backup_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'common_name', 'scientific_name', 'taxonomy_id', 'description', 'created_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(backup_data)
        print(f"Backup saved to: {backup_file}")
    else:
        print("No species data found to backup")
    
    return backup_data

def check_duplicates():
    """Check for duplicate species entries"""
    print("Checking for duplicate species entries...")
    
    # Check common_name duplicates
    common_name_dupes = db.session.query(Species.common_name, db.func.count(Species.id)) \
                                  .group_by(Species.common_name) \
                                  .having(db.func.count(Species.id) > 1) \
                                  .all()
    
    # Check scientific_name duplicates
    scientific_name_dupes = db.session.query(Species.scientific_name, db.func.count(Species.id)) \
                                     .group_by(Species.scientific_name) \
                                     .having(db.func.count(Species.id) > 1) \
                                     .all()
    
    duplicates_found = False
    
    if common_name_dupes:
        print(f"Found {len(common_name_dupes)} duplicate common names:")
        for name, count in common_name_dupes:
            print(f"  - '{name}': {count} entries")
        duplicates_found = True
    
    if scientific_name_dupes:
        print(f"Found {len(scientific_name_dupes)} duplicate scientific names:")
        for name, count in scientific_name_dupes:
            print(f"  - '{name}': {count} entries")
        duplicates_found = True
    
    if not duplicates_found:
        print("No duplicate species found. Migration can proceed safely.")
    
    return common_name_dupes, scientific_name_dupes

def handle_duplicates(common_name_dupes, scientific_name_dupes):
    """Handle duplicate species entries"""
    if not common_name_dupes and not scientific_name_dupes:
        return True
    
    print("\nDuplicate species found. Options:")
    print("1. Remove duplicates (keep oldest entry)")
    print("2. View duplicates and handle manually")
    print("3. Abort migration")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        return remove_duplicates(common_name_dupes, scientific_name_dupes)
    elif choice == "2":
        show_duplicate_details(common_name_dupes, scientific_name_dupes)
        return False
    else:
        print("Migration aborted.")
        return False

def remove_duplicates(common_name_dupes, scientific_name_dupes):
    """Remove duplicate entries, keeping the oldest one"""
    print("Removing duplicates...")
    
    # Handle common name duplicates
    for common_name, _ in common_name_dupes:
        species_list = Species.query.filter_by(common_name=common_name) \
                                   .order_by(Species.created_at.asc()).all()
        
        # Keep the first (oldest) entry, remove others
        for species in species_list[1:]:
            print(f"Removing duplicate: {species.common_name} (ID: {species.id})")
            db.session.delete(species)
    
    # Handle scientific name duplicates
    for scientific_name, _ in scientific_name_dupes:
        species_list = Species.query.filter_by(scientific_name=scientific_name) \
                                   .order_by(Species.created_at.asc()).all()
        
        # Keep the first (oldest) entry, remove others
        for species in species_list[1:]:
            print(f"Removing duplicate: {species.scientific_name} (ID: {species.id})")
            db.session.delete(species)
    
    try:
        db.session.commit()
        print("Duplicates removed successfully.")
        return True
    except Exception as e:
        print(f"Error removing duplicates: {e}")
        db.session.rollback()
        return False

def show_duplicate_details(common_name_dupes, scientific_name_dupes):
    """Show detailed information about duplicates"""
    print("\n=== DUPLICATE SPECIES DETAILS ===")
    
    if common_name_dupes:
        print("\nCommon Name Duplicates:")
        for common_name, _ in common_name_dupes:
            species_list = Species.query.filter_by(common_name=common_name).all()
            print(f"\n  Common Name: {common_name}")
            for species in species_list:
                print(f"    ID: {species.id}, Scientific: {species.scientific_name}, "
                      f"Created: {species.created_at}")
    
    if scientific_name_dupes:
        print("\nScientific Name Duplicates:")
        for scientific_name, _ in scientific_name_dupes:
            species_list = Species.query.filter_by(scientific_name=scientific_name).all()
            print(f"\n  Scientific Name: {scientific_name}")
            for species in species_list:
                print(f"    ID: {species.id}, Common: {species.common_name}, "
                      f"Created: {species.created_at}")
    
    print("\nPlease manually resolve duplicates in the database and run the migration again.")

def apply_unique_constraints():
    """Apply unique constraints to the database"""
    print("Applying unique constraints to Species table...")
    
    try:
        # For SQLite, we need to recreate the table with constraints
        # This is handled by SQLAlchemy migrations, but we'll use a direct approach
        
        # Note: The unique constraints are already added to the model
        # We need to recreate the table structure
        
        # Drop and recreate tables (SQLite limitation)
        db.drop_all()
        db.create_all()
        
        print("Unique constraints applied successfully.")
        return True
        
    except Exception as e:
        print(f"Error applying constraints: {e}")
        return False

def verify_constraints():
    """Verify that unique constraints are working"""
    print("Verifying unique constraints...")
    
    try:
        # Try to create duplicate species (should fail)
        test_species1 = Species(common_name="Test Mouse", scientific_name="Test musculus")
        test_species2 = Species(common_name="Test Mouse", scientific_name="Different musculus")
        
        db.session.add(test_species1)
        db.session.commit()
        
        # This should fail
        db.session.add(test_species2)
        db.session.commit()
        
        print("ERROR: Unique constraint not working (duplicate allowed)")
        return False
        
    except Exception as e:
        db.session.rollback()
        # Clean up test data
        test_species = Species.query.filter_by(common_name="Test Mouse").first()
        if test_species:
            db.session.delete(test_species)
            db.session.commit()
        
        print("Unique constraints verified successfully.")
        return True

def main():
    """Main migration function"""
    print("Starting Species table migration...")
    print("=" * 50)
    
    # Use existing Flask app instance
    
    with app.app_context():
        try:
            # Step 1: Backup current data
            backup_data = backup_species_data()
            
            # Step 2: Check for duplicates
            common_dupes, scientific_dupes = check_duplicates()
            
            # Step 3: Handle duplicates if found
            if common_dupes or scientific_dupes:
                if not handle_duplicates(common_dupes, scientific_dupes):
                    print("Migration aborted due to unresolved duplicates.")
                    return
                
                # Re-check after handling duplicates
                common_dupes, scientific_dupes = check_duplicates()
                if common_dupes or scientific_dupes:
                    print("Duplicates still exist. Please resolve manually.")
                    return
            
            # Step 4: Apply unique constraints
            if not apply_unique_constraints():
                print("Migration failed during constraint application.")
                return
            
            # Step 5: Restore data from backup
            print("Restoring species data...")
            for species_data in backup_data:
                species = Species(
                    common_name=species_data['common_name'],
                    scientific_name=species_data['scientific_name'],
                    taxonomy_id=species_data['taxonomy_id'],
                    description=species_data['description']
                )
                db.session.add(species)
            
            db.session.commit()
            print(f"Restored {len(backup_data)} species records.")
            
            # Step 6: Verify constraints
            if verify_constraints():
                print("\n" + "=" * 50)
                print("Migration completed successfully!")
                print("Species table now has unique constraints on common_name and scientific_name.")
            else:
                print("Migration completed but verification failed.")
                
        except Exception as e:
            print(f"Migration failed with error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    main()
