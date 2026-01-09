"""
Setup script to initialize the database and seed test data
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.utils.db_init import init_db, seed_members

if __name__ == "__main__":
    print("=" * 50)
    print("Plum OPD Claim Adjudication - Database Setup")
    print("=" * 50)
    
    print("\n1. Creating database tables...")
    init_db()
    
    print("\n2. Seeding test members...")
    seed_members()
    
    print("\n" + "=" * 50)
    print("[SUCCESS] Setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Create .env file from .env.example")
    print("2. Add your GEMINI_API_KEY to .env")
    print("3. Run: python run.py")
    print("\nAPI will be available at: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
