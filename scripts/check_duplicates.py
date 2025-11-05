"""Check for duplicate resumes in database."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.resume import Resume
from sqlalchemy import select, func


async def check_duplicates():
    """Check if resumes are unique."""
    async with AsyncSessionLocal() as db:
        # Total count
        result = await db.execute(select(func.count(Resume.id)))
        total = result.scalar()
        
        # Unique file hashes
        result = await db.execute(select(func.count(func.distinct(Resume.file_hash))))
        unique_hashes = result.scalar()
        
        # Unique filenames
        result = await db.execute(select(func.count(func.distinct(Resume.file_name))))
        unique_names = result.scalar()
        
        print("\n" + "="*60)
        print("Database Resume Analysis")
        print("="*60)
        print(f"Total resumes in database: {total}")
        print(f"Unique file hashes: {unique_hashes}")
        print(f"Unique file names: {unique_names}")
        print(f"\nDuplicates by hash: {total - unique_hashes}")
        print(f"Duplicates by name: {total - unique_names}")
        print("="*60)
        
        if total == unique_hashes:
            print("\n✓ All resumes are UNIQUE - no duplicates!")
        else:
            print(f"\n⚠ Found {total - unique_hashes} duplicate resumes")
        
        # Show sample filenames
        result = await db.execute(select(Resume.file_name).limit(30))
        names = [r[0] for r in result.fetchall()]
        
        print(f"\nFirst 30 filenames:")
        for i, name in enumerate(names, 1):
            print(f"  {i:2}. {name}")


if __name__ == "__main__":
    asyncio.run(check_duplicates())
