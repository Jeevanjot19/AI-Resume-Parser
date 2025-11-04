"""
Image processor with OCR support.
"""

from pathlib import Path
from typing import Dict, Any
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from loguru import logger

from app.document_processors.base_processor import BaseProcessor
from app.core.config import settings


class ImageProcessor(BaseProcessor):
    """Image processor with OCR capabilities."""
    
    def __init__(self):
        # Set tesseract path if configured
        if settings.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
    
    async def extract_text(self, file_path: Path) -> str:
        """Extract text from image using OCR."""
        try:
            # Handle PDF images
            if file_path.suffix.lower() == '.pdf':
                return await self._extract_from_pdf_image(file_path)
            
            # Handle regular images
            image = Image.open(file_path)
            
            # Preprocess image for better OCR
            image = self._preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(
                image,
                lang=settings.OCR_LANG,
                config='--oem 3 --psm 6'
            )
            
            return text.strip()
        except Exception as e:
            logger.error(f"Image OCR error: {e}")
            return ""
    
    async def _extract_from_pdf_image(self, file_path: Path) -> str:
        """Extract text from scanned PDF."""
        try:
            # Convert PDF to images
            images = convert_from_path(file_path, dpi=300)
            
            text_parts = []
            for i, image in enumerate(images):
                # Preprocess
                image = self._preprocess_image(image)
                
                # OCR
                page_text = pytesseract.image_to_string(
                    image,
                    lang=settings.OCR_LANG,
                    config='--oem 3 --psm 6'
                )
                
                if page_text.strip():
                    text_parts.append(page_text.strip())
            
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"PDF image OCR error: {e}")
            return ""
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results."""
        try:
            # Convert to grayscale
            image = image.convert('L')
            
            # Increase contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            return image
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            return image
    
    async def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract image metadata."""
        try:
            if file_path.suffix.lower() == '.pdf':
                images = convert_from_path(file_path, dpi=300)
                return {
                    "format": "pdf_image",
                    "page_count": len(images),
                    "ocr_enabled": True
                }
            
            image = Image.open(file_path)
            
            metadata = {
                "format": file_path.suffix[1:].lower(),
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
                "ocr_enabled": True
            }
            
            # Extract EXIF data if available
            if hasattr(image, '_getexif') and image._getexif():
                exif_data = image._getexif()
                if exif_data:
                    metadata["exif"] = {k: str(v) for k, v in exif_data.items()}
            
            return metadata
        except Exception as e:
            logger.error(f"Image metadata extraction error: {e}")
            return {"format": "image", "ocr_enabled": True}
    
    def validate(self, file_path: Path) -> bool:
        """Validate image file."""
        if not file_path.exists() or not file_path.is_file():
            return False
        
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf']
        if file_path.suffix.lower() not in valid_extensions:
            return False
        
        try:
            if file_path.suffix.lower() == '.pdf':
                # For PDFs, just check if it exists
                return True
            else:
                # For images, try to open
                Image.open(file_path)
                return True
        except Exception:
            return False
