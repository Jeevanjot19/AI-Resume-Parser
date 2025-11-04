"""
Document processor factory.
"""

from pathlib import Path
from typing import Optional
from loguru import logger

from app.document_processors.base_processor import BaseProcessor
from app.document_processors.pdf_processor import PDFProcessor
from app.document_processors.docx_processor import DOCXProcessor
from app.document_processors.txt_processor import TXTProcessor
from app.document_processors.image_processor import ImageProcessor
from app.document_processors.tika_processor import TikaProcessor


class DocumentProcessorFactory:
    """Factory for creating document processors."""
    
    def __init__(self, use_tika: bool = False):
        """
        Initialize factory.
        
        Args:
            use_tika: Whether to use Tika as primary processor
        """
        self.use_tika = use_tika
        self._processors = {
            '.pdf': PDFProcessor(),
            '.docx': DOCXProcessor(),
            '.doc': DOCXProcessor(),
            '.txt': TXTProcessor(),
            '.jpg': ImageProcessor(),
            '.jpeg': ImageProcessor(),
            '.png': ImageProcessor(),
        }
        
        if use_tika:
            self._tika_processor = TikaProcessor()
    
    def get_processor(self, file_path: Path) -> Optional[BaseProcessor]:
        """
        Get appropriate processor for file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Processor instance or None if unsupported
        """
        suffix = file_path.suffix.lower()
        
        # Use Tika as primary if enabled
        if self.use_tika:
            logger.info(f"Using Tika processor for {file_path.name}")
            return self._tika_processor
        
        # Use specific processor
        processor = self._processors.get(suffix)
        
        if processor:
            logger.info(f"Using {processor.__class__.__name__} for {file_path.name}")
            return processor
        
        logger.warning(f"No processor found for file type: {suffix}")
        return None
    
    async def process_file(self, file_path: Path) -> dict:
        """
        Process file with appropriate processor.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Processed document data
        """
        processor = self.get_processor(file_path)
        
        if not processor:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        try:
            # Try primary processor
            result = await processor.process(file_path)
            
            # If Tika failed or returned empty, try fallback
            if self.use_tika and (not result.get('text') or len(result['text']) < 50):
                logger.warning("Tika processing returned insufficient text, using fallback")
                fallback_processor = self._processors.get(file_path.suffix.lower())
                if fallback_processor:
                    result = await fallback_processor.process(file_path)
            
            return result
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            
            # Try fallback if primary failed
            if self.use_tika:
                fallback_processor = self._processors.get(file_path.suffix.lower())
                if fallback_processor:
                    logger.info("Attempting fallback processor")
                    return await fallback_processor.process(file_path)
            
            raise
