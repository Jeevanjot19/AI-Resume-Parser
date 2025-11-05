"""
Simple preview and statistics of Kaggle resume dataset.
No database or services required - just shows what's in the dataset.
"""

import pandas as pd
from pathlib import Path
from loguru import logger
import sys

def preview_dataset():
    """Preview the Kaggle resume dataset."""
    
    # Path to the dataset
    dataset_path = Path("data/kaggle_resume_dataset/Resume.csv")
    resume_files_dir = Path("data/kaggle_resume_dataset/data")
    
    logger.info("="*60)
    logger.info("Kaggle Resume Dataset Preview")
    logger.info("="*60)
    
    # Check if CSV exists
    if not dataset_path.exists():
        logger.error(f"❌ Dataset not found at {dataset_path}")
        logger.info("\nPlease:")
        logger.info("1. Download from: https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset")
        logger.info("2. Extract the zip file")
        logger.info("3. Place Resume.csv in: data/kaggle_resume_dataset/")
        return False
    
    logger.info(f"✓ Found Resume.csv at {dataset_path}")
    
    # Check if resume files directory exists
    has_resume_files = resume_files_dir.exists()
    if has_resume_files:
        logger.info(f"✓ Found resume files directory: {resume_files_dir}")
    else:
        logger.warning(f"⚠ Resume files directory not found at {resume_files_dir}")
        logger.info("  (Text-only processing will be available)")
    
    # Read the CSV
    logger.info(f"\nReading CSV file...")
    df = pd.read_csv(dataset_path)
    
    logger.info("\n" + "="*60)
    logger.info("Dataset Statistics")
    logger.info("="*60)
    logger.info(f"Total Resumes: {len(df)}")
    logger.info(f"Columns: {', '.join(df.columns.tolist())}")
    
    # Category breakdown
    if 'Category' in df.columns:
        logger.info(f"\nJob Categories ({df['Category'].nunique()} unique):")
        category_counts = df['Category'].value_counts()
        for i, (category, count) in enumerate(category_counts.items(), 1):
            logger.info(f"  {i:2d}. {category:30s} : {count:4d} resumes")
    
    # Text length statistics
    if 'Resume_str' in df.columns or 'Resume' in df.columns:
        text_col = 'Resume_str' if 'Resume_str' in df.columns else 'Resume'
        df['text_length'] = df[text_col].astype(str).str.len()
        
        logger.info(f"\nResume Text Statistics:")
        logger.info(f"  Average length: {df['text_length'].mean():.0f} characters")
        logger.info(f"  Minimum length: {df['text_length'].min():.0f} characters")
        logger.info(f"  Maximum length: {df['text_length'].max():.0f} characters")
        logger.info(f"  Median length:  {df['text_length'].median():.0f} characters")
    
    # Resume files statistics
    if has_resume_files:
        logger.info(f"\nResume Files Statistics:")
        total_files = 0
        category_folders = sorted(resume_files_dir.iterdir())
        
        for folder in category_folders:
            if folder.is_dir():
                files = list(folder.glob("*"))
                files = [f for f in files if f.is_file()]
                total_files += len(files)
        
        logger.info(f"  Total files: {total_files}")
        logger.info(f"  Category folders: {len(category_folders)}")
        
        # Show file types
        file_extensions = {}
        for folder in category_folders:
            if folder.is_dir():
                for file in folder.glob("*"):
                    if file.is_file():
                        ext = file.suffix.lower() or 'no_extension'
                        file_extensions[ext] = file_extensions.get(ext, 0) + 1
        
        if file_extensions:
            logger.info(f"\n  File types:")
            for ext, count in sorted(file_extensions.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"    {ext:15s}: {count:4d} files")
    
    # Sample resumes
    logger.info(f"\n" + "="*60)
    logger.info("Sample Resumes (First 3)")
    logger.info("="*60)
    
    text_col = 'Resume_str' if 'Resume_str' in df.columns else 'Resume'
    
    for idx in range(min(3, len(df))):
        row = df.iloc[idx]
        category = row.get('Category', 'Unknown')
        text = str(row.get(text_col, ''))
        
        logger.info(f"\nResume #{idx + 1}:")
        logger.info(f"  Category: {category}")
        logger.info(f"  Text length: {len(text)} characters")
        logger.info(f"  Preview: {text[:200]}...")
    
    logger.info("\n" + "="*60)
    logger.info("Dataset Ready for Import!")
    logger.info("="*60)
    logger.info("\nNext steps:")
    logger.info("1. Make sure all services are running (PostgreSQL, Elasticsearch, Redis)")
    logger.info("2. Run: python scripts/import_kaggle_dataset.py")
    logger.info("\nOr if you want to run without Docker:")
    logger.info("- The full import requires database and search services")
    logger.info("- You can start with the API and upload resumes manually")
    
    return True


if __name__ == "__main__":
    try:
        preview_dataset()
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
