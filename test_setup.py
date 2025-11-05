"""
Test basic imports and configuration for local development.
Run this to verify the setup is working before starting the server.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from app.core.config import settings
        print("✅ Config module imported")
        print(f"   - Database: {settings.sync_database_url}")
        print(f"   - Debug mode: {settings.DEBUG}")
        print(f"   - Redis enabled: {getattr(settings, 'REDIS_ENABLED', True)}")
        print(f"   - Elasticsearch enabled: {getattr(settings, 'ELASTICSEARCH_ENABLED', True)}")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from app.core.database import engine, SessionLocal
        print("✅ Database module imported")
        print(f"   - Engine: {engine.url}")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        from fastapi import FastAPI
        print("✅ FastAPI imported")
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        from pydantic import BaseModel
        print("✅ Pydantic imported")
    except Exception as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    try:
        from sqlalchemy.orm import Session
        print("✅ SQLAlchemy imported")
    except Exception as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    return True

def test_directories():
    """Test that required directories exist."""
    print("\nTesting directories...")
    
    directories = ["data", "data/uploads", "models", "logs"]
    all_exist = True
    
    for dir_path in directories:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"❌ {dir_path}/ missing")
            all_exist = False
    
    return all_exist

def test_env_file():
    """Test that environment file exists."""
    print("\nTesting environment configuration...")
    
    if Path(".env").exists():
        print("✅ .env file exists")
        return True
    elif Path(".env.local").exists():
        print("⚠️  .env file not found, but .env.local exists")
        print("   Copy .env.local to .env:")
        print("   cp .env.local .env  (Linux/Mac)")
        print("   Copy-Item .env.local .env  (Windows)")
        return False
    else:
        print("❌ No environment file found")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Resume Parser AI - Local Setup Verification")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Directories", test_directories),
        ("Environment", test_env_file),
    ]
    
    results = {}
    for name, test_func in tests:
        results[name] = test_func()
        print()
    
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to start the server.")
        print("\nRun: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before starting.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
