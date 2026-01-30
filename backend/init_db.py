import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base
import os

print("Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
    
    if os.path.exists("teisinis_ai.db"):
        print("✅ teisinis_ai.db file found.")
    else:
        print("❌ teisinis_ai.db file NOT found.")
        
except Exception as e:
    print(f"❌ Error creating tables: {e}")
