"""
Script to download and import Kaggle resume dataset.
https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset
"""

import os
import pandas as pd
import asyncio
from pathlib import Path
from loguru import logger
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.resume_parser import ResumeParserService
from app.services.ai_enhancer import AIEnhancerService
from app.models import Resume, ProcessingStatus
from app.search import SearchClient


async def import_kaggle_dataset():
    """Import resumes from Kaggle dataset."""
    
    # Path to the dataset
    dataset_path = Path("data/kaggle_resume_dataset/Resume.csv")
    resume_files_dir = Path("data/kaggle_resume_dataset/data")  # Folder with actual resume files
    
    if not dataset_path.exists():
        logger.error(f"Dataset not found at {dataset_path}")
        logger.info("Please download the dataset from:")
        logger.info("https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset")
        logger.info("And place Resume.csv in data/kaggle_resume_dataset/")
        return
    
    # Check if resume files directory exists
    has_resume_files = resume_files_dir.exists()
    if not has_resume_files:
        logger.warning(f"Resume files directory not found at {resume_files_dir}")
        logger.warning("Will process text-only data from CSV")
        logger.info("For full processing with actual files, also extract the 'data' folder from Kaggle dataset")
    else:
        logger.info(f"✓ Found resume files directory: {resume_files_dir}")
    
    # Read the dataset
    logger.info(f"Reading dataset from {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    logger.info(f"Dataset loaded: {len(df)} resumes found")
    logger.info(f"Columns: {df.columns.tolist()}")
    
    # Display sample
    logger.info("\nSample data:")
    logger.info(df.head(2))
    
    # Count existing resumes before import
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select, func
        result = await db.execute(select(func.count(Resume.id)))
        initial_count = result.scalar()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Resumes already in database: {initial_count}")
    logger.info(f"{'='*60}\n")
    
    # Initialize services (disable Tika)
    parser = ResumeParserService(use_tika=False)  # Fixed: disable Tika
    enhancer = AIEnhancerService()
    search_client = SearchClient()
    
    await parser.initialize()
    await enhancer.initialize()
    
    # Process each resume
    processed_count = 0
    failed_count = 0
    skipped_count = 0
    
    async with AsyncSessionLocal() as db:
        for idx, row in df.iterrows():
            try:
                resume_text = row['Resume_str'] if 'Resume_str' in df.columns else row.get('Resume', '')
                category = row['Category'] if 'Category' in df.columns else 'Unknown'
                
                if not resume_text or len(resume_text) < 50:
                    logger.warning(f"Skipping resume {idx}: insufficient text")
                    continue
                
                logger.info(f"\nProcessing resume {idx + 1}/{len(df)} - Category: {category}")
                
                # Try to find actual resume file first
                file_path = None
                file_type = "txt"
                
                if has_resume_files:
                    # Look for resume file in category folder
                    category_folder = resume_files_dir / category.upper().replace(' ', '')
                    if category_folder.exists():
                        # Find any file with matching index or first file
                        resume_files = list(category_folder.glob("*"))
                        if resume_files and idx < len(resume_files):
                            file_path = resume_files[idx % len(resume_files)]
                            file_type = file_path.suffix[1:] if file_path.suffix else "txt"
                            logger.info(f"Found actual resume file: {file_path.name}")
                
                # If no actual file found, create temporary text file
                if not file_path:
                    temp_file = Path(settings.UPLOAD_DIR) / f"kaggle_resume_{idx}.txt"
                    temp_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(resume_text)
                    
                    file_path = temp_file
                    file_type = "txt"
                
                # Parse resume using the actual file
                parsed_data = await parser.parse_resume(file_path, db)
                
                # Check if resume already exists by file_hash
                file_hash = parsed_data.get('file_hash')
                from sqlalchemy import select
                existing_resume = await db.execute(
                    select(Resume).where(Resume.file_hash == file_hash)
                )
                if existing_resume.scalar_one_or_none():
                    logger.info(f"⊙ Resume {idx + 1} already exists (hash: {file_hash[:16]}...), skipping")
                    skipped_count += 1
                    continue
                
                # Create resume record
                resume = Resume(
                    file_name=file_path.name,
                    file_type=file_type,
                    file_size=file_path.stat().st_size if file_path.exists() else len(resume_text),
                    file_hash=file_hash,
                    raw_text=resume_text,  # Use CSV text as fallback
                    structured_data=parsed_data.get('structured_data'),
                    processing_status=ProcessingStatus.COMPLETED,
                    file_metadata={
                        'source': 'kaggle',
                        'category': category,
                        'index': idx,
                        'original_file_path': str(file_path),
                        'has_actual_file': file_path != temp_file if 'temp_file' in locals() else True
                    }
                )
                
                db.add(resume)
                await db.flush()
                
                # Enhance with AI
                logger.info(f"Enhancing resume {resume.id} with AI...")
                enhancements = await enhancer.enhance_resume(
                    resume.id,
                    parsed_data.get('raw_text', resume_text),  # Use parsed text if available
                    parsed_data.get('structured_data', {}),
                    db
                )
                
                # Update resume with enhancements
                resume.ai_enhancements = enhancements
                
                # Index in Elasticsearch (optional - skip if not available)
                try:
                    logger.info(f"Indexing resume {resume.id} in Elasticsearch...")
                    await search_client.index_resume(
                        resume_id=str(resume.id),
                        document={
                            'text': parsed_data.get('raw_text', resume_text),
                            'structured_data': parsed_data.get('structured_data', {}),
                            'embedding': parsed_data.get('embedding', []),
                            'metadata': {
                                'category': category,
                                'filename': file_path.name if file_path else f'resume_{idx}.txt',
                                'processed_at': datetime.utcnow().isoformat()
                            }
                        }
                    )
                except Exception as es_error:
                    logger.warning(f"Elasticsearch indexing skipped (not running): {es_error}")
                
                await db.commit()
                
                processed_count += 1
                logger.info(f"✓ Resume {idx + 1} processed successfully (ID: {resume.id})")
                
                # Progress update every 5 resumes
                if processed_count % 5 == 0:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Progress: {processed_count} resumes processed so far...")
                    logger.info(f"{'='*60}\n")
                
            except Exception as e:
                logger.error(f"✗ Failed to process resume {idx}: {e}")
                failed_count += 1
                await db.rollback()
                continue
    
    # Get final count
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select, func
        result = await db.execute(select(func.count(Resume.id)))
        final_count = result.scalar()
    
    logger.info("\n" + "="*60)
    logger.info("Dataset Import Summary")
    logger.info("="*60)
    logger.info(f"Total resumes in Kaggle dataset: {len(df)}")
    logger.info(f"Resumes before this import: {initial_count}")
    logger.info(f"Successfully processed (this run): {processed_count}")
    logger.info(f"Skipped (duplicates): {skipped_count}")
    logger.info(f"Failed (this run): {failed_count}")
    logger.info(f"Total resumes in database now: {final_count}")
    logger.info(f"New resumes added: {final_count - initial_count}")
    logger.info(f"Processing mode: {'With actual files' if has_resume_files else 'Text-only from CSV'}")
    logger.info("="*60)


async def verify_import():
    """Verify imported data."""
    from sqlalchemy import select, func
    
    async with AsyncSessionLocal() as db:
        # Count total resumes
        result = await db.execute(select(func.count(Resume.id)))
        total = result.scalar()
        
        logger.info(f"\nTotal resumes in database: {total}")
        
        # Get sample resumes
        result = await db.execute(
            select(Resume).limit(5)
        )
        resumes = result.scalars().all()
        
        logger.info("\nSample resumes:")
        for resume in resumes:
            # file_metadata is already a dict (JSON field)
            category = resume.file_metadata.get('category', 'N/A') if resume.file_metadata else 'N/A'
            logger.info(f"- {resume.id}: {resume.file_name} (Category: {category})")
            if resume.structured_data:
                skills_data = resume.structured_data.get('skills', {})
                # Skills is a dict with categories, get all skills as a flat list
                if isinstance(skills_data, dict):
                    all_skills = []
                    for category_skills in skills_data.values():
                        if isinstance(category_skills, list):
                            all_skills.extend(category_skills)
                    logger.info(f"  Skills ({len(all_skills)}): {all_skills[:5] if len(all_skills) > 5 else all_skills}")
                else:
                    logger.info(f"  Skills: {skills_data}")


if __name__ == "__main__":
    logger.info("Kaggle Resume Dataset Import")
    logger.info("="*60)
    
    # Run import
    asyncio.run(import_kaggle_dataset())
    
    # Verify
    asyncio.run(verify_import())
