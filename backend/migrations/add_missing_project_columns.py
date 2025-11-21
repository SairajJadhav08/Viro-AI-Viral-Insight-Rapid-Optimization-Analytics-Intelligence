"""
Migration: Add missing columns to projects table
Adds: protein_files, clinical_files, assay_files, deadliness_score
"""
import sqlite3
import os
from pathlib import Path

# Get database path
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "Viroai_DataBase" / "viroai.db"

def run_migration():
    """Add missing columns to projects table"""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(projects)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Add missing columns
        migrations = []
        
        if 'protein_files' not in existing_columns:
            migrations.append("ALTER TABLE projects ADD COLUMN protein_files TEXT")
        
        if 'clinical_files' not in existing_columns:
            migrations.append("ALTER TABLE projects ADD COLUMN clinical_files TEXT")
        
        if 'assay_files' not in existing_columns:
            migrations.append("ALTER TABLE projects ADD COLUMN assay_files TEXT")
        
        if 'deadliness_score' not in existing_columns:
            migrations.append("ALTER TABLE projects ADD COLUMN deadliness_score DECIMAL(5, 2)")
        
        if migrations:
            print(f"Adding {len(migrations)} missing columns...")
            for migration in migrations:
                print(f"  Executing: {migration}")
                cursor.execute(migration)
            
            conn.commit()
            print("[OK] Migration completed successfully")
            return True
        else:
            print("[OK] All columns already exist")
            return True
            
    except Exception as e:
        print(f"[FAIL] Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()

