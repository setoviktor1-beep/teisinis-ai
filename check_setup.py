"""
Diagnostics script - checks all configuration and dependencies
"""
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_environment():
    """Check environment variables"""
    load_dotenv()
    
    print("[*] ENVIRONMENT VARIABLES CHECK")
    print("=" * 50)
    
    required_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET', 
        'GEMINI_API_KEY',
        'SECRET_KEY'
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            masked = value[:10] + '...' if len(value) > 10 else value
            print(f"[OK] {var}: {masked} (length: {len(value)})")
        else:
            print(f"[X] {var}: NOT SET")
            all_good = False
    
    return all_good

def check_dependencies():
    """Check if required packages are installed"""
    print("\n[*] DEPENDENCIES CHECK")
    print("=" * 50)
    
    # Package name mapping: (display_name, import_name)
    required_packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('sqlalchemy', 'sqlalchemy'),
        ('passlib', 'passlib'),
        ('python-jose', 'jose'),
        ('authlib', 'authlib'),
        ('python-multipart', 'multipart'),
        ('google-generativeai', 'google.generativeai')
    ]
    
    all_good = True
    for display_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"[OK] {display_name}")
        except ImportError:
            print(f"[X] {display_name} - NOT INSTALLED")
            all_good = False
    
    return all_good

def check_database():
    """Check database connection and tables"""
    print("\n[*] DATABASE CHECK")
    print("=" * 50)
    
    try:
        from backend.database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            print("[OK] Database connected")
            print(f"   Tables: {', '.join(tables)}")
        else:
            print("[!] Database connected but no tables found")
            print("   Run: python setup_db.py")
        
        return True
    except Exception as e:
        print(f"[X] Database error: {e}")
        return False

def check_google_oauth_setup():
    """Check Google OAuth configuration"""
    print("\n[*] GOOGLE OAUTH CHECK")
    print("=" * 50)
    
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("[X] Google OAuth not configured in .env")
        return False
    
    print("[OK] Google OAuth credentials found")
    print("\n[!] IMPORTANT: Verify in Google Cloud Console:")
    print("   1. Go to: https://console.cloud.google.com/apis/credentials")
    print("   2. Find your OAuth 2.0 Client ID")
    print("   3. Add authorized redirect URI:")
    print("      http://localhost:8000/api/v1/auth/google/callback")
    print("   4. If using a different port/domain, update accordingly")
    
    return True

def main():
    print("\n" + "=" * 50)
    print("TEISINIS AI - DIAGNOSTICS")
    print("=" * 50 + "\n")
    
    checks = [
        check_environment(),
        check_dependencies(),
        check_database(),
        check_google_oauth_setup()
    ]
    
    print("\n" + "=" * 50)
    if all(checks):
        print("[OK] ALL CHECKS PASSED!")
        print("\nYou can now start the server:")
        print("   uvicorn backend.main:app --reload")
    else:
        print("[X] SOME CHECKS FAILED")
        print("\nPlease fix the issues above before starting the server")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
