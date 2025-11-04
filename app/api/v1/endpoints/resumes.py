"""
Resume API endpoints.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from pathlib import Path
import uuid
import aiofiles
from loguru import logger
from datetime import datetime

from app.core.database import get_db
from app.services.resume_parser import ResumeParserService
from app.services.ai_enhancer import AIEnhancerService
from app.services.job_matcher import JobMatcherService
from app.models import Resume, ProcessingStatus
from app.schemas.resume import (
    ResumeResponse, 
    ResumeAnalysis, 
    ResumeUploadResponse,
    JobMatchRequest,
    JobMatchResponse
)
from app.worker.tasks import process_resume_task, calculate_match_score_task
from app.cache import CacheClient
from app.search import SearchClient
from app.core.config import settings


router = APIRouter()

# Service dependencies
def get_resume_parser():
    return ResumeParserService()

def get_ai_enhancer():
    return AIEnhancerService()

def get_job_matcher():
    return JobMatcherService()

def get_cache():
    return CacheClient()

def get_search():
    return SearchClient()


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_resume(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    cache: CacheClient = Depends(get_cache)
):
    """
    Upload and parse a resume file (async processing).
    
    - **file**: Resume file (PDF, DOCX, TXT, or image)
    - Returns: Resume ID and processing status
    """
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.jpg', '.jpeg', '.png'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 10MB limit"
            )
        
        # Generate resume ID
        resume_id = str(uuid.uuid4())
        
        # Save file temporarily
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"{resume_id}{file_ext}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Create resume record with PENDING status
        resume = Resume(
            id=resume_id,
            file_name=file.filename,
            file_type=file_ext[1:],  # Remove dot
            file_size=len(content),
            file_path=str(file_path),
            processing_status=ProcessingStatus.PENDING
        )
        db.add(resume)
        await db.commit()
        
        logger.info(f"Resume uploaded: {resume_id} - {file.filename}")
        
        # Trigger async processing
        process_resume_task.delay(resume_id, str(file_path))
        
        return ResumeUploadResponse(
            id=resume_id,
            filename=file.filename,
            status=ProcessingStatus.PENDING.value,
            message="Resume uploaded successfully. Processing started.",
            uploaded_at=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {str(e)}"
        )


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    cache: CacheClient = Depends(get_cache)
):
    """
    Retrieve parsed resume data by ID.
    
    - **resume_id**: Resume UUID
    - Returns: Complete resume data with AI enhancements
    """
    try:
        # Check cache first
        cache_key = f"resume:{resume_id}"
        cached_data = await cache.get(cache_key)
        
        if cached_data:
            logger.info(f"Resume {resume_id} served from cache")
            return JSONResponse(content=cached_data)
        
        # Fetch from database
        query = select(Resume).where(Resume.id == resume_id)
        result = await db.execute(query)
        resume = result.scalar_one_or_none()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume {resume_id} not found"
            )
        
        # Build response
        response_data = {
            'id': resume.id,
            'filename': resume.file_name,
            'file_type': resume.file_type,
            'processing_status': resume.processing_status.value,
            'raw_text': resume.raw_text,
            'structured_data': resume.structured_data,
            'ai_enhancements': resume.ai_enhancements,
            'created_at': resume.created_at.isoformat() if resume.created_at else None,
            'updated_at': resume.updated_at.isoformat() if resume.updated_at else None
        }
        
        # Cache for 1 hour if processing is complete
        if resume.processing_status == ProcessingStatus.COMPLETED:
            await cache.set(cache_key, response_data, ttl=3600)
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving resume {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve resume: {str(e)}"
        )


@router.get("/{resume_id}/status")
async def get_resume_status(
    resume_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get processing status of a resume.
    
    - **resume_id**: Resume UUID
    - Returns: Current processing status
    """
    try:
        query = select(Resume.processing_status, Resume.error_message).where(Resume.id == resume_id)
        result = await db.execute(query)
        row = result.one_or_none()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume {resume_id} not found"
            )
        
        return {
            'resume_id': resume_id,
            'status': row[0].value,
            'error': row[1] if row[0] == ProcessingStatus.FAILED else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for resume {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysis)
async def get_resume_analysis(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    ai_enhancer: AIEnhancerService = Depends(get_ai_enhancer)
):
    """
    Get detailed AI analysis of a resume.
    
    - **resume_id**: Resume UUID
    - Returns: AI-powered analysis including quality score, industry fit, skill gaps, etc.
    """
    try:
        # Initialize service
        await ai_enhancer.initialize()
        
        # Get analysis
        analysis = await ai_enhancer.get_resume_analysis(resume_id, db)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis not found for resume {resume_id}"
            )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis for resume {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis: {str(e)}"
        )


@router.post("/{resume_id}/match", response_model=JobMatchResponse)
async def match_resume_with_job(
    resume_id: str,
    job_data: JobMatchRequest,
    db: AsyncSession = Depends(get_db),
    job_matcher: JobMatcherService = Depends(get_job_matcher)
):
    """
    Match a resume with a job description.
    
    - **resume_id**: Resume UUID
    - **job_data**: Job description and requirements
    - Returns: Match score, gap analysis, and recommendations
    """
    try:
        # Verify resume exists
        query = select(Resume).where(Resume.id == resume_id)
        result = await db.execute(query)
        resume = result.scalar_one_or_none()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume {resume_id} not found"
            )
        
        if resume.processing_status != ProcessingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resume is still processing. Status: {resume.processing_status.value}"
            )
        
        # Initialize matcher
        await job_matcher.initialize()
        
        # Perform matching
        match_result = await job_matcher.match_resume_with_job(
            resume_id,
            job_data.dict(),
            db
        )
        
        return match_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching resume {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to match resume: {str(e)}"
        )


@router.post("/search", response_model=List[ResumeResponse])
async def search_resumes(
    query: str,
    top_k: int = 10,
    db: AsyncSession = Depends(get_db),
    search_client: SearchClient = Depends(get_search)
):
    """
    Search resumes by text query (semantic search).
    
    - **query**: Search query text
    - **top_k**: Number of results to return (default: 10)
    - Returns: List of matching resumes
    """
    try:
        # Perform semantic search
        results = await search_client.search_resumes(query, size=top_k)
        
        # Fetch full resume data
        resume_ids = [r['_source']['resume_id'] for r in results.get('hits', {}).get('hits', [])]
        
        if not resume_ids:
            return []
        
        query_db = select(Resume).where(Resume.id.in_(resume_ids))
        result = await db.execute(query_db)
        resumes = result.scalars().all()
        
        # Build responses
        response_data = []
        for resume in resumes:
            response_data.append({
                'id': resume.id,
                'filename': resume.file_name,
                'file_type': resume.file_type,
                'processing_status': resume.processing_status.value,
                'structured_data': resume.structured_data,
                'ai_enhancements': resume.ai_enhancements,
                'created_at': resume.created_at.isoformat() if resume.created_at else None
            })
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error searching resumes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    cache: CacheClient = Depends(get_cache),
    search_client: SearchClient = Depends(get_search)
):
    """
    Delete a resume and all related data.
    
    - **resume_id**: Resume UUID
    """
    try:
        # Fetch resume
        query = select(Resume).where(Resume.id == resume_id)
        result = await db.execute(query)
        resume = result.scalar_one_or_none()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume {resume_id} not found"
            )
        
        # Delete file from disk
        if resume.file_path and Path(resume.file_path).exists():
            Path(resume.file_path).unlink()
        
        # Delete from database (cascade delete will handle related records)
        await db.delete(resume)
        await db.commit()
        
        # Delete from cache
        await cache.delete(f"resume:{resume_id}")
        
        # Delete from Elasticsearch
        await search_client.delete_resume(resume_id)
        
        logger.info(f"Resume deleted: {resume_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting resume {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete resume: {str(e)}"
        )
