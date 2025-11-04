"""
Download Kaggle resume dataset.
"""

import os
import subprocess
from pathlib import Path
from loguru import logger


def setup_kaggle_credentials():
    """Setup Kaggle API credentials."""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if not kaggle_json.exists():
        logger.warning("Kaggle credentials not found!")
        logger.info("\nTo download Kaggle datasets, you need to:")
        logger.info("1. Go to https://www.kaggle.com/settings/account")
        logger.info("2. Scroll to 'API' section")
        logger.info("3. Click 'Create New API Token'")
        logger.info(f"4. Place the downloaded kaggle.json in: {kaggle_dir}")
        logger.info("\nAlternatively, you can manually download from:")
        logger.info("https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset")
        return False
    
    logger.info(f"✓ Kaggle credentials found at {kaggle_json}")
    
    # Set permissions (Unix-like systems)
    if os.name != 'nt':  # Not Windows
        os.chmod(kaggle_json, 0o600)
    
    return True


def download_dataset():
    """Download the resume dataset from Kaggle."""
    
    # Create data directory
    data_dir = Path("data/kaggle_resume_dataset")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Data directory: {data_dir.absolute()}")
    
    # Check if dataset already exists
    resume_csv = data_dir / "Resume.csv"
    if resume_csv.exists():
        logger.info(f"✓ Dataset already exists at {resume_csv}")
        logger.info(f"File size: {resume_csv.stat().st_size / 1024:.2f} KB")
        return True
    
    # Check Kaggle credentials
    if not setup_kaggle_credentials():
        return False
    
    try:
        # Install kaggle package if not installed
        logger.info("Checking kaggle package...")
        try:
            import kaggle
            logger.info("✓ Kaggle package installed")
        except ImportError:
            logger.info("Installing kaggle package...")
            subprocess.run(["pip", "install", "kaggle"], check=True)
            import kaggle
        
        # Download dataset
        logger.info("\nDownloading resume dataset from Kaggle...")
        logger.info("Dataset: snehaanbhawal/resume-dataset")
        
        subprocess.run([
            "kaggle", "datasets", "download",
            "-d", "snehaanbhawal/resume-dataset",
            "-p", str(data_dir),
            "--unzip"
        ], check=True)
        
        logger.info("✓ Dataset downloaded successfully!")
        
        # Verify files
        files = list(data_dir.glob("*"))
        logger.info(f"\nDownloaded files ({len(files)}):")
        for f in files:
            logger.info(f"  - {f.name} ({f.stat().st_size / 1024:.2f} KB)")
        
        if resume_csv.exists():
            logger.info(f"\n✓ Resume.csv found!")
            
            # Quick preview
            import pandas as pd
            df = pd.read_csv(resume_csv)
            logger.info(f"\nDataset info:")
            logger.info(f"  Rows: {len(df)}")
            logger.info(f"  Columns: {df.columns.tolist()}")
            
            if 'Category' in df.columns:
                logger.info(f"\nCategories:")
                for cat, count in df['Category'].value_counts().head(10).items():
                    logger.info(f"  - {cat}: {count} resumes")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download dataset: {e}")
        logger.info("\nPlease download manually from:")
        logger.info("https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset")
        logger.info(f"And place Resume.csv in: {data_dir.absolute()}")
        return False
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


if __name__ == "__main__":
    logger.info("Kaggle Resume Dataset Downloader")
    logger.info("="*60)
    
    success = download_dataset()
    
    if success:
        logger.info("\n" + "="*60)
        logger.info("✓ Dataset ready!")
        logger.info("Next step: Run 'python scripts/import_kaggle_dataset.py'")
        logger.info("="*60)
    else:
        logger.info("\n" + "="*60)
        logger.info("✗ Download failed")
        logger.info("Please download manually and place in data/kaggle_resume_dataset/")
        logger.info("="*60)
