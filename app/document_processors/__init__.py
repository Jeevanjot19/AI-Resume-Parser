"""
Document processor initialization.
"""

from app.document_processors.pdf_processor import PDFProcessor
from app.document_processors.docx_processor import DOCXProcessor
from app.document_processors.txt_processor import TXTProcessor
from app.document_processors.image_processor import ImageProcessor
from app.document_processors.tika_processor import TikaProcessor
from app.document_processors.processor_factory import DocumentProcessorFactory

__all__ = [
    "PDFProcessor",
    "DOCXProcessor",
    "TXTProcessor",
    "ImageProcessor",
    "TikaProcessor",
    "DocumentProcessorFactory",
]
