"""
Apache Tika processor for robust document extraction.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
import httpx

from app.document_processors.base_processor import BaseProcessor
from app.core.config import settings


class TikaProcessor(BaseProcessor):
    """Apache Tika document processor."""
    
    def __init__(self):
        self.tika_url = "http://localhost:9998"  # Tika server URL
        self.timeout = 30.0
    
    async def extract_text(self, file_path: Path) -> str:
        """Extract text using Tika."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                with open(file_path, 'rb') as f:
                    files = {'file': (file_path.name, f, 'application/octet-stream')}
                    response = await client.put(
                        f"{self.tika_url}/tika",
                        files=files,
                        headers={"Accept": "text/plain"}
                    )
                    
                    if response.status_code == 200:
                        return response.text
                    else:
                        logger.error(f"Tika extraction failed: {response.status_code}")
                        return ""
        except Exception as e:
            logger.error(f"Tika extraction error: {e}")
            return ""
    
    async def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata using Tika."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                with open(file_path, 'rb') as f:
                    files = {'file': (file_path.name, f, 'application/octet-stream')}
                    response = await client.put(
                        f"{self.tika_url}/meta",
                        files=files,
                        headers={"Accept": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        return response.json()
                    else:
                        logger.error(f"Tika metadata extraction failed: {response.status_code}")
                        return {}
        except Exception as e:
            logger.error(f"Tika metadata error: {e}")
            return {}
    
    def validate(self, file_path: Path) -> bool:
        """Validate file."""
        return file_path.exists() and file_path.is_file()
