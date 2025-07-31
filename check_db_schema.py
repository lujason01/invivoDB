#!/usr/bin/env python3
"""
Script to check the actual database schema and compare with model definitions
"""
import sqlite3
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_schema():
    db_path = 'src/web/invivo_data.db'
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get table schema
        print("=== ACTUAL DATABASE SCHEMA ===")
        cursor.execute("PRAGMA table_info(species)")
        columns = cursor.fetchall()
        
        print("Species table columns:")
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'} {'PRIMARY KEY' if col[5] else ''}")
        
        # Check for indexes
        print("\nIndexes on species table:")
        cursor.execute("PRAGMA index_list(species)")
        indexes = cursor.fetchall()
        for idx in indexes:
            print(f"  {idx[1]} ({'UNIQUE' if idx[2] else 'NON-UNIQUE'})")
            cursor.execute(f"PRAGMA index_info({idx[1]})")
            idx_info = cursor.fetchall()
            for info in idx_info:
                cursor.execute("PRAGMA table_info(species)")
                cols = cursor.fetchall()
                col_name = cols[info[1]][1]  # Get column name by position
                print(f"    Column: {col_name}")
        
        # Check current data
        print(f"\nTotal species records: ", end="")
        cursor.execute("SELECT COUNT(*) FROM species")
        count = cursor.fetchone()[0]
        print(count)
        
        if count > 0:
            print("\nSample records:")
            cursor.execute("SELECT * FROM species LIMIT 3")
            records = cursor.fetchall()
            for record in records:
                print(f"  {record}")
                
    except Exception as e:
        print(f"Error checking schema: {e}")
    finally:
        conn.close()

def check_model_definition():
    print("\n=== MODEL DEFINITION ===")
    try:
        from models.database import Species
        print("Species model fields:")
        # Get SQLAlchemy table columns
        for column in Species.__table__.columns:
            print(f"  {column.name} {column.type} {'NOT NULL' if not column.nullable else 'NULL'} {'PRIMARY KEY' if column.primary_key else ''}")
        
        # Check constraints
        print("\nModel constraints:")
        for constraint in Species.__table__.constraints:
            print(f"  {type(constraint).__name__}: {constraint}")
            
    except Exception as e:
        print(f"Error loading model: {e}")

if __name__ == "__main__":
    check_schema()
    check_model_definition()
