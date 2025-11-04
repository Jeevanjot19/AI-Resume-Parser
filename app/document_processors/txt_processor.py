"""
TXT document processor.
"""

from pathlib import Path
from typing import Dict, Any
import chardet
from loguru import logger

from app.document_processors.base_processor import BaseProcessor


class TXTProcessor(BaseProcessor):
    """TXT document processor with encoding detection."""
    
    async def extract_text(self, file_path: Path) -> str:
        """Extract text from TXT file with encoding detection."""
        try:
            # Detect encoding
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
            
            # Read with detected encoding
            with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
                return file.read()
        except Exception as e:
            logger.error(f"TXT extraction error: {e}")
            return ""
    
    async def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract TXT metadata."""
        try:
            # Detect encoding
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
            
            # Count lines
            with open(file_path, 'r', encoding=result['encoding'] or 'utf-8', errors='ignore') as file:
                lines = file.readlines()
            
            return {
                "format": "txt",
                "encoding": result['encoding'],
                "encoding_confidence": result['confidence'],
                "line_count": len(lines),
                "char_count": len(raw_data)
            }
        except Exception as e:
            logger.error(f"TXT metadata extraction error: {e}")
            return {"format": "txt"}
    
    def validate(self, file_path: Path) -> bool:
        """Validate TXT file."""
        if not file_path.exists() or not file_path.is_file():
            return False
        
        if file_path.suffix.lower() != '.txt':
            return False
        
        return True
