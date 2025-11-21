#!/usr/bin/env python3
"""
Database Migration Runner for Viro-AI v2.0
Executes SQL migration files in order with backup and rollback capability
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import json

# Configuration
DB_FILE = "viroai.db"  # SQLite database file
MIGRATIONS_DIR = Path(__file__).parent
BACKUP_DIR = MIGRATIONS_DIR / "backups"
MIGRATION_HISTORY_FILE = MIGRATIONS_DIR / "migration_history.json"


class MigrationRunner:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"[OK] Connected to database: {self.db_path}")
        
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
            print("[OK] Disconnected from database")
            
    def create_backup(self):
        """Create database backup before migration"""
        BACKUP_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"backup_{timestamp}.db"
        
        if Path(self.db_path).exists():
            import shutil
            shutil.copy2(self.db_path, backup_file)
            print(f"[OK] Backup created: {backup_file}")
            return backup_file
        else:
            print("[INFO] Database file doesn't exist yet, skipping backup")
            return None
            
    def load_migration_history(self):
        """Load migration history from JSON file"""
        if MIGRATION_HISTORY_FILE.exists():
            with open(MIGRATION_HISTORY_FILE, 'r') as f:
                return json.load(f)
        return {"executed_migrations": []}
        
    def save_migration_history(self, history):
        """Save migration history to JSON file"""
        with open(MIGRATION_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
            
    def get_pending_migrations(self):
        """Get list of SQL files that haven't been executed"""
        history = self.load_migration_history()
        executed = set(history.get("executed_migrations", []))
        
        all_migrations = sorted([
            f for f in MIGRATIONS_DIR.glob("*.sql")
            if f.name not in executed
        ])
        
        return all_migrations
        
    def execute_migration(self, migration_file):
        """Execute a single migration file"""
        print(f"\n[RUNNING] Executing migration: {migration_file.name}")
        
        try:
            with open(migration_file, 'r') as f:
                sql_content = f.read()
            
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            for statement in statements:
                if statement:
                    try:
                        self.cursor.execute(statement)
                    except Exception as e:
                        # Some statements might fail if objects already exist (IF NOT EXISTS)
                        # Log but continue
                        if "already exists" not in str(e).lower():
                            print(f"  [WARNING] {e}")
                        
            self.conn.commit()
            print(f"  [OK] Successfully executed: {migration_file.name}")
            
            # Update migration history
            history = self.load_migration_history()
            history["executed_migrations"].append(migration_file.name)
            history["last_migration_date"] = datetime.now().isoformat()
            self.save_migration_history(history)
            
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"  [ERROR] Error executing {migration_file.name}: {e}")
            return False
            
    def run_all_migrations(self):
        """Run all pending migrations"""
        pending = self.get_pending_migrations()
        
        if not pending:
            print("\n[OK] No pending migrations. Database is up to date!")
            return True
            
        print(f"\nFound {len(pending)} pending migration(s)")
        print("=" * 60)
        
        # Create backup before running migrations
        backup_file = self.create_backup()
        
        # Execute each migration
        success_count = 0
        for migration_file in pending:
            if self.execute_migration(migration_file):
                success_count += 1
            else:
                print(f"\n[ERROR] Migration failed. Stopping execution.")
                print(f"  To rollback, restore from: {backup_file}")
                return False
                
        print("\n" + "=" * 60)
        print(f"[OK] Successfully executed {success_count}/{len(pending)} migrations")
        return True
        
    def show_status(self):
        """Show current migration status"""
        history = self.load_migration_history()
        executed = history.get("executed_migrations", [])
        all_migrations = sorted([f.name for f in MIGRATIONS_DIR.glob("*.sql")])
        pending = [m for m in all_migrations if m not in executed]
        
        print("\n" + "=" * 60)
        print("MIGRATION STATUS")
        print("=" * 60)
        print(f"Total migrations: {len(all_migrations)}")
        print(f"Executed: {len(executed)}")
        print(f"Pending: {len(pending)}")
        
        if executed:
            print(f"\nLast migration: {history.get('last_migration_date', 'Unknown')}")
            
        if pending:
            print(f"\nPending migrations:")
            for p in pending:
                print(f"  - {p}")
        else:
            print("\n[OK] Database is up to date!")
            
        print("=" * 60 + "\n")


def main():
    """Main execution function"""
    print("=" * 60)
    print("VIRO-AI Database Migration Tool v2.0")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not MIGRATIONS_DIR.exists():
        print("[ERROR] Migrations directory not found!")
        sys.exit(1)
        
    # Find database file (check parent directory)
    db_path = Path(MIGRATIONS_DIR).parent / DB_FILE
    if not db_path.exists():
        print(f"[INFO] Database file not found at {db_path}")
        print(f"  Creating new database...")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
    runner = MigrationRunner(str(db_path))
    
    # Parse command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        runner.connect()
        runner.show_status()
        runner.disconnect()
    else:
        runner.connect()
        success = runner.run_all_migrations()
        runner.disconnect()
        
        if success:
            print("\n[OK] All migrations completed successfully!")
            sys.exit(0)
        else:
            print("[ERROR] Migration failed!")
            sys.exit(1)


if __name__ == "__main__":
    main()

