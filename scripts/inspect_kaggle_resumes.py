"""
Check what the actual Kaggle resumes look like
"""

import asyncio
from app.core.database import get_async_db
from app.models import Resume
from sqlalchemy import select


async def inspect_resumes():
    """Inspect a few resumes to see their content."""
    print("=" * 80)
    print("INSPECTING ACTUAL KAGGLE RESUMES")
    print("=" * 80)
    
    async for db in get_async_db():
        result = await db.execute(
            select(Resume).limit(5)
        )
        resumes = result.scalars().all()
        
        if not resumes:
            print("No resumes found!")
            return
        
        for i, resume in enumerate(resumes, 1):
            print(f"\n{'=' * 80}")
            print(f"RESUME {i}")
            print(f"{'=' * 80}")
            print(f"File: {resume.file_name}")
            print(f"Length: {len(resume.raw_text)} characters")
            print(f"\nFirst 1000 characters:")
            print("-" * 80)
            print(resume.raw_text[:1000])
            print("-" * 80)
            
            # Check if it contains contact-like patterns
            has_at = '@' in resume.raw_text
            has_phone_digits = any(resume.raw_text.count(str(d)) > 5 for d in range(10))
            
            print(f"\nQuick check:")
            print(f"  Contains '@' symbol: {has_at}")
            print(f"  Has many digits (potential phone): {has_phone_digits}")
        
        break


if __name__ == "__main__":
    asyncio.run(inspect_resumes())
