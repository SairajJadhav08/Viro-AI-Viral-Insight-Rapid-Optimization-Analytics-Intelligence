"""
Migration script to create auth_tokens table
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, Base
from app.models.token import AuthToken

def create_token_table():
    """Create auth_tokens table"""
    print("Creating auth_tokens table...")
    Base.metadata.create_all(bind=engine, tables=[AuthToken.__table__])
    print("[OK] auth_tokens table created successfully!")

if __name__ == "__main__":
    create_token_table()

