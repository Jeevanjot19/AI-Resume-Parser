"""
Base document processor interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path


class BaseProcessor(ABC):
    """Base class for all document processors."""
    
    @abstractmethod
    async def extract_text(self, file_path: Path) -> str:
        """Extract text from document.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content
        """
        pass
    
    @abstractmethod
    async def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from document.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing metadata
        """
        pass
    
    @abstractmethod
    def validate(self, file_path: Path) -> bool:
        """Validate if file can be processed.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            True if file is valid, False otherwise
        """
        pass
    
    async def process(self, file_path: Path) -> Dict[str, Any]:
        """Process document and extract all information.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing text and metadata
        """
        if not self.validate(file_path):
            raise ValueError(f"Invalid file: {file_path}")
        
        text = await self.extract_text(file_path)
        metadata = await self.extract_metadata(file_path)
        
        return {
            "text": text,
            "metadata": metadata
        }
