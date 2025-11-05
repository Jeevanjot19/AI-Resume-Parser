"""
Create database tables directly without migrations.
This is a simple script to initialize the SQLite database for local development.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import engine
from app.db.base_class import Base

# Import all models directly to register them with Base (avoid circular imports)
import app.models.resume
import app.models.person_info
import app.models.work_experience
import app.models.education
import app.models.skills
import app.models.ai_analysis
import app.models.resume_job_match

def init_db():
    """Initialize database by creating all tables."""
    print("Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print(f"   Database: {engine.url}")
        print(f"   Tables created: {len(Base.metadata.tables)}")
        for table_name in Base.metadata.tables.keys():
            print(f"   - {table_name}")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
