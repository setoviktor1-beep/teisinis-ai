"""
Database setup script - creates tables and verifies connection
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine, Base

def setup_database():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables created successfully!")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\nCreated tables: {', '.join(tables)}")
        
        # Check if users table has correct schema
        if 'users' in tables:
            columns = [col['name'] for col in inspector.get_columns('users')]
            print(f"   Users columns: {', '.join(columns)}")
        
        if 'documents' in tables:
            columns = [col['name'] for col in inspector.get_columns('documents')]
            print(f"   Documents columns: {', '.join(columns)}")
            
        print("\n[OK] Database setup complete!")
        
    except Exception as e:
        print(f"[ERROR] Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()
