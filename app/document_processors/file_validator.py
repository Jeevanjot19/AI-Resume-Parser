"""
File validation and sanitization utilities.
"""

import hashlib
import magic
from pathlib import Path
from typing import Tuple, Optional
from loguru import logger

from app.core.config import settings


class FileValidator:
    """File validation and sanitization."""
    
    ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.txt', '.jpg', '.jpeg', '.png']
    
    MIME_TYPES = {
        'application/pdf': ['.pdf'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        'application/msword': ['.doc'],
        'text/plain': ['.txt'],
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
    }
    
    @staticmethod
    def validate_file_size(file_path: Path) -> bool:
        """Validate file size."""
        try:
            file_size = file_path.stat().st_size
            if file_size > settings.MAX_FILE_SIZE:
                logger.warning(f"File too large: {file_size} bytes")
                return False
            if file_size == 0:
                logger.warning("File is empty")
                return False
            return True
        except Exception as e:
            logger.error(f"Error checking file size: {e}")
            return False
    
    @staticmethod
    def validate_file_extension(file_path: Path) -> bool:
        """Validate file extension."""
        extension = file_path.suffix.lower()
        if extension not in FileValidator.ALLOWED_EXTENSIONS:
            logger.warning(f"Invalid file extension: {extension}")
            return False
        return True
    
    @staticmethod
    def validate_mime_type(file_path: Path) -> bool:
        """Validate MIME type matches extension."""
        try:
            # Detect MIME type
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(str(file_path))
            
            # Check if MIME type is allowed
            allowed_extensions = FileValidator.MIME_TYPES.get(mime_type, [])
            
            if not allowed_extensions:
                logger.warning(f"Unknown MIME type: {mime_type}")
                return False
            
            # Check if extension matches MIME type
            extension = file_path.suffix.lower()
            if extension not in allowed_extensions:
                logger.warning(f"MIME type {mime_type} doesn't match extension {extension}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating MIME type: {e}")
            # Fall back to extension-only validation
            return FileValidator.validate_file_extension(file_path)
    
    @staticmethod
    def check_for_malware(file_path: Path) -> bool:
        """Basic malware checks."""
        try:
            # Check for suspicious patterns in file
            with open(file_path, 'rb') as f:
                content = f.read(1024)  # Read first KB
                
                # Check for common malware signatures
                suspicious_patterns = [
                    b'<script',
                    b'javascript:',
                    b'eval(',
                    b'exec(',
                ]
                
                for pattern in suspicious_patterns:
                    if pattern in content.lower():
                        logger.warning(f"Suspicious pattern found: {pattern}")
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking for malware: {e}")
            return False
    
    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        """Calculate SHA-256 hash of file."""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            raise
    
    @classmethod
    def validate_file(cls, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive file validation.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not file_path.exists():
            return False, "File does not exist"
        
        if not file_path.is_file():
            return False, "Path is not a file"
        
        # Validate file size
        if not cls.validate_file_size(file_path):
            return False, f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        
        # Validate extension
        if not cls.validate_file_extension(file_path):
            return False, f"File extension not allowed. Allowed: {', '.join(cls.ALLOWED_EXTENSIONS)}"
        
        # Validate MIME type
        if not cls.validate_mime_type(file_path):
            return False, "File type does not match extension"
        
        # Check for malware
        if not cls.check_for_malware(file_path):
            return False, "File failed security check"
        
        return True, None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal."""
        # Remove path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        dangerous_chars = ['..', '/', '\\', '\0', '<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1)
            filename = name[:250] + '.' + ext
        
        return filename
