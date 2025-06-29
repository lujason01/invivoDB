"""
Migration script to convert accession numbers from old format to new format

Old format: MM-001-2024
New format: MM2024000001A5

This script will:
1. Convert existing accession numbers to the new format
2. Update the database schema
3. Validate the conversion
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.database import (
    db, Animal, Species, generate_accession_number, get_species_code,
    validate_accession_number, parse_accession_number
)
from app import app


def convert_old_accession_number(old_number: str) -> str:
    """
    Convert old accession number format to new format
    
    Old: MM-001-2024
    New: MM2024000001A5
    """
    if not old_number or '-' not in old_number:
        return old_number
    
    try:
        parts = old_number.split('-')
        if len(parts) != 3:
            return old_number
        
        species_code = parts[0]
        sequence = int(parts[1])
        year = int(parts[2])
        
        # Generate new accession number
        new_number = generate_accession_number(species_code, year, sequence)
        
        # Validate the new number
        if validate_accession_number(new_number):
            return new_number
        else:
            print(f"Warning: Generated invalid accession number for {old_number}")
            return old_number
            
    except (ValueError, IndexError) as e:
        print(f"Error converting {old_number}: {e}")
        return old_number


def migrate_accession_numbers():
    """Migrate all existing accession numbers to the new format"""
    with app.app_context():
        try:
            # Get all animals
            animals = Animal.query.all()
            
            print(f"Found {len(animals)} animals to migrate")
            
            migrated_count = 0
            error_count = 0
            
            for animal in animals:
                old_number = animal.accession_number
                
                # Check if already in new format
                if validate_accession_number(old_number):
                    print(f"✓ {old_number} already in new format")
                    continue
                
                # Convert to new format
                new_number = convert_old_accession_number(old_number)
                
                if new_number != old_number:
                    # Check if new number already exists
                    existing = Animal.query.filter_by(accession_number=new_number).first()
                    if existing and existing.id != animal.id:
                        print(f"✗ Conflict: {new_number} already exists")
                        error_count += 1
                        continue
                    
                    # Update the accession number
                    animal.accession_number = new_number
                    print(f"✓ {old_number} → {new_number}")
                    migrated_count += 1
                else:
                    print(f"✗ Could not convert {old_number}")
                    error_count += 1
            
            # Commit changes
            if migrated_count > 0:
                db.session.commit()
                print(f"\nMigration completed:")
                print(f"  ✓ Successfully migrated: {migrated_count}")
                print(f"  ✗ Errors: {error_count}")
            else:
                print("\nNo migration needed - all accession numbers are already in new format")
                
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")
            raise


def validate_all_accession_numbers():
    """Validate all accession numbers in the database"""
    with app.app_context():
        animals = Animal.query.all()
        
        valid_count = 0
        invalid_count = 0
        
        for animal in animals:
            if validate_accession_number(animal.accession_number):
                valid_count += 1
            else:
                print(f"Invalid accession number: {animal.accession_number}")
                invalid_count += 1
        
        print(f"\nValidation results:")
        print(f"  ✓ Valid: {valid_count}")
        print(f"  ✗ Invalid: {invalid_count}")
        
        return invalid_count == 0


def test_new_accession_number_generation():
    """Test the new accession number generation system"""
    print("Testing new accession number generation:")
    
    # Test different species and sequences
    test_cases = [
        ("MM", 2025, 1),
        ("MM", 2025, 42),
        ("RN", 2025, 1),
        ("MAC", 2025, 1),
        ("CAN", 2025, 1),
    ]
    
    for species_code, year, sequence in test_cases:
        accession_number = generate_accession_number(species_code, year, sequence)
        is_valid = validate_accession_number(accession_number)
        
        print(f"  {species_code}{year}{sequence:06d} → {accession_number} {'✓' if is_valid else '✗'}")
        
        if is_valid:
            # Test parsing
            parsed = parse_accession_number(accession_number)
            print(f"    Parsed: {parsed}")


if __name__ == "__main__":
    print("InvivoDB Accession Number Migration Tool")
    print("=" * 50)
    
    # Test the new system first
    print("\n1. Testing new accession number generation:")
    test_new_accession_number_generation()
    
    # Validate existing data
    print("\n2. Validating existing accession numbers:")
    all_valid = validate_all_accession_numbers()
    
    if not all_valid:
        # Perform migration
        print("\n3. Migrating accession numbers:")
        migrate_accession_numbers()
        
        # Validate again
        print("\n4. Validating after migration:")
        validate_all_accession_numbers()
    else:
        print("\n3. No migration needed - all accession numbers are valid")
    
    print("\nMigration tool completed!") 