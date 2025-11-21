"""
Apply complete database schema for VIRO-AI v2.0
Creates all required tables with all columns
"""

import sqlite3
import os
from pathlib import Path

def apply_schema():
    """Apply complete database schema"""
    
    # Get database path
    db_path = Path(__file__).parent / "viroai.db"
    schema_path = Path(__file__).parent / "create_complete_schema.sql"
    
    print("=" * 60)
    print("VIRO-AI v2.0 - Database Schema Application")
    print("=" * 60)
    print()
    
    # Read schema SQL
    print(f"[1/3] Reading schema from: {schema_path.name}")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    print("  ✓ Schema loaded")
    print()
    
    # Connect to database
    print(f"[2/3] Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("  ✓ Connected")
    print()
    
    # Execute schema (split by semicolon and execute each statement)
    print("[3/3] Applying schema...")
    try:
        # Execute the entire script at once
        cursor.executescript(schema_sql)
        conn.commit()
        print("  ✓ Schema applied successfully")
        print()
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print("=" * 60)
        print(f"CREATED TABLES ({len(tables)} total):")
        print("=" * 60)
        for table in tables:
            print(f"  ✓ {table[0]}")
        print()
        
        # Verify users table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("=" * 60)
        print("USERS TABLE COLUMNS:")
        print("=" * 60)
        critical_columns = ['id', 'email', 'password_hash', 'first_name', 'last_name', 
                           'phone', 'role', 'is_active', 'created_at']
        
        column_names = [col[1] for col in columns]
        
        for col_name in critical_columns:
            if col_name in column_names:
                print(f"  ✓ {col_name}")
            else:
                print(f"  ✗ {col_name} [MISSING!]")
        print()
        
        # Check if is_active column exists
        if 'is_active' in column_names:
            print("=" * 60)
            print("✓ SUCCESS: is_active column exists!")
            print("=" * 60)
            print()
            print("Database is ready for authentication!")
            print()
        else:
            print("=" * 60)
            print("✗ ERROR: is_active column is MISSING!")
            print("=" * 60)
            print()
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    success = apply_schema()
    if success:
        print("=" * 60)
        print("DATABASE SCHEMA READY!")
        print("=" * 60)
        print()
        print("You can now:")
        print("  1. Restart the backend server")
        print("  2. Try signing up again")
        print("  3. All required tables and columns are in place")
        print()
    else:
        print("Schema application failed. Please check errors above.")

