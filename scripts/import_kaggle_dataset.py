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
    
    if not dataset_path.exists():
        logger.error(f"Dataset not found at {dataset_path}")
        logger.info("Please download the dataset from:")
        logger.info("https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset")
        logger.info("And place Resume.csv in data/kaggle_resume_dataset/")
        return
    
    # Read the dataset
    logger.info(f"Reading dataset from {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    logger.info(f"Dataset loaded: {len(df)} resumes found")
    logger.info(f"Columns: {df.columns.tolist()}")
    
    # Display sample
    logger.info("\nSample data:")
    logger.info(df.head(2))
    
    # Initialize services
    parser = ResumeParserService()
    enhancer = AIEnhancerService()
    search_client = SearchClient()
    
    await parser.initialize()
    await enhancer.initialize()
    
    # Process each resume
    processed_count = 0
    failed_count = 0
    
    async with AsyncSessionLocal() as db:
        for idx, row in df.iterrows():
            try:
                resume_text = row['Resume_str'] if 'Resume_str' in df.columns else row.get('Resume', '')
                category = row['Category'] if 'Category' in df.columns else 'Unknown'
                
                if not resume_text or len(resume_text) < 50:
                    logger.warning(f"Skipping resume {idx}: insufficient text")
                    continue
                
                logger.info(f"\nProcessing resume {idx + 1}/{len(df)} - Category: {category}")
                
                # Create temporary file
                temp_file = Path(settings.UPLOAD_DIR) / f"kaggle_resume_{idx}.txt"
                temp_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(resume_text)
                
                # Parse resume
                parsed_data = await parser.parse_resume(temp_file, db)
                
                # Create resume record
                resume = Resume(
                    file_name=f"kaggle_resume_{idx}.txt",
                    file_type="txt",
                    file_size=len(resume_text),
                    file_path=str(temp_file),
                    file_hash=parsed_data.get('file_hash'),
                    raw_text=resume_text,
                    structured_data=parsed_data.get('structured_data'),
                    processing_status=ProcessingStatus.COMPLETED,
                    metadata={'source': 'kaggle', 'category': category, 'index': idx}
                )
                
                db.add(resume)
                await db.flush()
                
                # Enhance with AI
                logger.info(f"Enhancing resume {resume.id} with AI...")
                enhancements = await enhancer.enhance_resume(
                    resume.id,
                    resume_text,
                    parsed_data.get('structured_data', {}),
                    db
                )
                
                # Update resume with enhancements
                resume.ai_enhancements = enhancements
                
                # Index in Elasticsearch
                logger.info(f"Indexing resume {resume.id} in Elasticsearch...")
                await search_client.index_resume(
                    resume_id=resume.id,
                    text=resume_text,
                    structured_data=parsed_data.get('structured_data', {}),
                    embedding=parsed_data.get('embedding', [])
                )
                
                await db.commit()
                
                processed_count += 1
                logger.info(f"✓ Resume {idx} processed successfully (ID: {resume.id})")
                
                # Limit for testing
                if processed_count >= 50:  # Process first 50 resumes
                    logger.info(f"\nReached processing limit of 50 resumes")
                    break
                
            except Exception as e:
                logger.error(f"✗ Failed to process resume {idx}: {e}")
                failed_count += 1
                await db.rollback()
                continue
    
    logger.info("\n" + "="*60)
    logger.info("Dataset Import Summary")
    logger.info("="*60)
    logger.info(f"Total resumes in dataset: {len(df)}")
    logger.info(f"Successfully processed: {processed_count}")
    logger.info(f"Failed: {failed_count}")
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
            logger.info(f"- {resume.id}: {resume.file_name} (Category: {resume.metadata.get('category', 'N/A')})")
            if resume.structured_data:
                skills = resume.structured_data.get('skills', [])
                logger.info(f"  Skills: {skills[:5] if len(skills) > 5 else skills}")


if __name__ == "__main__":
    logger.info("Kaggle Resume Dataset Import")
    logger.info("="*60)
    
    # Run import
    asyncio.run(import_kaggle_dataset())
    
    # Verify
    asyncio.run(verify_import())
