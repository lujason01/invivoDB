#!/usr/bin/env python3
"""
Script to check database structure and assay type data
"""

import sqlite3
import os

def check_database():
    db_path = 'src/web/instance/invivodb.db'
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Database tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "="*50)
        
        # Check assay_types table structure
        print("Assay Types table structure:")
        cursor.execute("PRAGMA table_info(assay_types)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        print("\n" + "="*50)
        
        # Check assay_types data
        print("Assay Types data:")
        cursor.execute("SELECT * FROM assay_types")
        assay_types = cursor.fetchall()
        
        if assay_types:
            for assay_type in assay_types:
                print(f"  ID: {assay_type[0]}")
                print(f"  Name: {assay_type[1]}")
                print(f"  Category: {assay_type[2]}")
                print(f"  Description: {assay_type[3]}")
                print(f"  Standard Protocol: {assay_type[4]}")
                print(f"  Units: {assay_type[5]}")
                print(f"  Created: {assay_type[6]}")
                print("  ---")
        else:
            print("  No assay types found in database")
        
        print("\n" + "="*50)
        
        # Check assays table
        print("Assays data:")
        cursor.execute("SELECT COUNT(*) FROM assays")
        assay_count = cursor.fetchone()[0]
        print(f"  Total assays: {assay_count}")
        
        # Check assay_measurements table
        print("Assay Measurements data:")
        cursor.execute("SELECT COUNT(*) FROM assay_measurements")
        measurement_count = cursor.fetchone()[0]
        print(f"  Total measurements: {measurement_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database() 