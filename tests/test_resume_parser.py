import pytest
from fastapi import UploadFile
import io
from app.services.resume_parser import ResumeParserService
from docx import Document
import os

@pytest.mark.asyncio
async def test_pdf_parsing():
    """Test PDF resume parsing"""
    parser = ResumeParserService()
    content = b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>/Contents 4 0 R>>\nendobj\n4 0 obj\n<</Length 22>>stream\nBT /F1 12 Tf 72 712 Td (Test Resume) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000015 00000 n\n0000000061 00000 n\n0000000115 00000 n\n0000000210 00000 n\ntrailer <</Root 1 0 R/Size 5>>\nstartxref\n350\n%%EOF"
    file = UploadFile(
        filename="test.pdf",
        file=io.BytesIO(content)
    )
    
    result = await parser.parse_resume(file)
    assert result is not None
    assert "text" in result
    assert "extracted" in result

@pytest.mark.asyncio
async def test_docx_parsing(tmp_path):
    """Test DOCX resume parsing"""
    # Create a test DOCX file
    doc = Document()
    doc.add_paragraph("Test Resume Content")
    test_docx = os.path.join(tmp_path, "test.docx")
    doc.save(test_docx)
    
    with open(test_docx, "rb") as f:
        content = f.read()
    
    parser = ResumeParserService()
    file = UploadFile(
        filename="test.docx",
        file=io.BytesIO(content)
    )
    
    result = await parser.parse_resume(file)
    assert result is not None
    assert "text" in result
    assert "extracted" in result

@pytest.mark.asyncio
async def test_txt_parsing():
    """Test TXT resume parsing"""
    parser = ResumeParserService()
    content = b"Test resume content"
    file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(content)
    )
    
    result = await parser.parse_resume(file)
    assert result is not None
    assert "text" in result
    assert "extracted" in result

@pytest.mark.asyncio
async def test_invalid_file_type():
    """Test handling of invalid file type"""
    parser = ResumeParserService()
    content = b"Test content"
    file = UploadFile(
        filename="test.invalid",
        file=io.BytesIO(content)
    )
    
    with pytest.raises(ValueError):
        await parser.parse_resume(file)

@pytest.mark.asyncio
async def test_empty_file():
    """Test handling of empty file"""
    parser = ResumeParserService()
    content = b""
    file = UploadFile(
        filename="test.pdf",
        file=io.BytesIO(content)
    )
    
    result = await parser.parse_resume(file)
    assert result is not None
    assert "text" in result
    assert "extracted" in result
    assert result["text"] == ""
    assert result["extracted"] == {}

@pytest.mark.asyncio
async def test_corrupted_pdf():
    """Test handling of corrupted PDF file"""
    parser = ResumeParserService()
    content = b"%PDF-1.4\nCorrupted content"
    file = UploadFile(
        filename="test.pdf",
        file=io.BytesIO(content)
    )
    
    with pytest.raises(ValueError) as exc_info:
        await parser.parse_resume(file)
    assert "Error parsing PDF" in str(exc_info.value)

@pytest.mark.asyncio
async def test_corrupted_docx():
    """Test handling of corrupted DOCX file"""
    parser = ResumeParserService()
    content = b"PK\x03\x04Corrupted content"
    file = UploadFile(
        filename="test.docx",
        file=io.BytesIO(content)
    )
    
    with pytest.raises(ValueError) as exc_info:
        await parser.parse_resume(file)
    assert "Error parsing DOCX" in str(exc_info.value)