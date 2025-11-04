"""
PDF document processor with fallback support.
"""

from pathlib import Path
from typing import Dict, Any
import PyPDF2
import pdfplumber
from loguru import logger

from app.document_processors.base_processor import BaseProcessor


class PDFProcessor(BaseProcessor):
    """PDF document processor with multiple extraction methods."""
    
    async def extract_text(self, file_path: Path) -> str:
        """Extract text from PDF using multiple methods."""
        # Try pdfplumber first (better for complex layouts)
        text = await self._extract_with_pdfplumber(file_path)
        
        # Fallback to PyPDF2 if pdfplumber fails
        if not text or len(text) < 50:
            text = await self._extract_with_pypdf2(file_path)
        
        return text
    
    async def _extract_with_pdfplumber(self, file_path: Path) -> str:
        """Extract text using pdfplumber."""
        try:
            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"pdfplumber extraction error: {e}")
            return ""
    
    async def _extract_with_pypdf2(self, file_path: Path) -> str:
        """Extract text using PyPDF2."""
        try:
            text_parts = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"PyPDF2 extraction error: {e}")
            return ""
    
    async def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract PDF metadata."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata = {
                    "page_count": len(pdf_reader.pages),
                    "format": "pdf"
                }
                
                # Add PDF metadata if available
                if pdf_reader.metadata:
                    for key, value in pdf_reader.metadata.items():
                        if key.startswith('/'):
                            key = key[1:]  # Remove leading slash
                        metadata[key.lower()] = str(value)
                
                return metadata
        except Exception as e:
            logger.error(f"PDF metadata extraction error: {e}")
            return {"format": "pdf"}
    
    def validate(self, file_path: Path) -> bool:
        """Validate PDF file."""
        if not file_path.exists() or not file_path.is_file():
            return False
        
        if file_path.suffix.lower() != '.pdf':
            return False
        
        try:
            with open(file_path, 'rb') as file:
                # Check PDF magic number
                header = file.read(4)
                return header == b'%PDF'
        except Exception:
            return False
