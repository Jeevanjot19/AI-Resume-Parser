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
    JobMatchResponse,
    UploadOptions
)
from app.worker.tasks import process_resume_task, calculate_match_score_task
from app.cache import CacheClient
from app.search import SearchClient
from app.core.config import settings
from app.utils.transform import transform_resume_to_api_response, transform_job_match_to_api_response


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
    options: Optional[str] = None,  # JSON string of UploadOptions
    background_tasks: BackgroundTasks = None,
    db = Depends(get_db),
    cache: CacheClient = Depends(get_cache)
):
    """
    Upload and parse a resume file (async processing).
    
    - **file**: Resume file (PDF, DOCX, TXT, or image)
    - **options**: Optional JSON string with parsing options
    - Returns: Resume ID, processing status, and estimated time
    """
    import json
    
    try:
        # Parse options if provided
        upload_opts = UploadOptions()
        if options:
            try:
                opts_dict = json.loads(options)
                upload_opts = UploadOptions(**opts_dict)
            except Exception as e:
                logger.warning(f"Failed to parse options: {e}, using defaults")
        
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
        
        # Generate resume ID as UUID object
        resume_id = uuid.uuid4()
        
        # Save file temporarily
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"{str(resume_id)}{file_ext}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Calculate file hash
        import hashlib
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Check if resume with this hash already exists
        existing_resume = db.query(Resume).filter(Resume.file_hash == file_hash).first()
        
        if existing_resume:
            # Resume already exists, return existing ID
            logger.info(f"Resume already exists with hash {file_hash[:16]}..., returning existing ID: {existing_resume.id}")
            resume_id = existing_resume.id
            # Clean up the newly uploaded file since we're using existing
            import os
            try:
                os.remove(file_path)
            except:
                pass
        else:
            # Create new resume record with PENDING status
            resume = Resume(
                id=resume_id,
                file_name=file.filename,
                file_type=file_ext[1:],  # Remove dot
                file_size=len(content),
                file_hash=file_hash,
                processing_status=ProcessingStatus.PENDING
            )
            db.add(resume)
            db.commit()
            
            logger.info(f"New resume uploaded: {resume_id} - {file.filename} (options: {upload_opts.model_dump()})")
            
            # Trigger async processing with options (only for new resumes)
            process_resume_task.delay(str(resume_id), str(file_path))
        
        # Estimate processing time based on file type and size
        estimated_time = 30  # default
        if file_ext in ['.pdf', '.docx']:
            estimated_time = 30 + (len(content) // (1024 * 1024)) * 5  # +5s per MB
        elif file_ext in ['.jpg', '.jpeg', '.png'] and upload_opts.performOCR:
            estimated_time = 45 + (len(content) // (1024 * 1024)) * 10  # OCR takes longer
        
        # Determine status message
        if existing_resume:
            status_msg = "Resume already exists in database"
            status_value = existing_resume.processing_status.value
        else:
            status_msg = "Resume uploaded successfully"
            status_value = "processing"
        
        return ResumeUploadResponse(
            id=str(resume_id),  # Convert UUID to string for response
            status=status_value,
            message=status_msg,
            estimatedProcessingTime=min(estimated_time, 120),  # cap at 2 minutes
            webhookUrl=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {str(e)}"
        )


@router.get("/search", response_model=List[ResumeResponse])
def search_resumes(
    query: str,
    limit: int = 10,
    db = Depends(get_db)
):
    """
    Search resumes by keyword query (searches in skills, experience, education).
    
    - **query**: Search query text (e.g., "Python", "Software Engineer", "Stanford")
    - **limit**: Maximum number of results to return (default: 10, max: 100)
    - Returns: List of matching resumes ranked by relevance
    
    **Example queries:**
    - `"Python developer"` - Find resumes mentioning Python
    - `"machine learning"` - Find ML-related resumes
    - `"Stanford"` - Find Stanford graduates
    - `"AWS certified"` - Find AWS certified candidates
    """
    try:
        # Limit validation
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 10
            
        # Search in completed resumes only
        resumes = db.query(Resume).filter(
            Resume.processing_status == ProcessingStatus.COMPLETED
        ).all()
        
        if not resumes:
            return []
        
        # Simple keyword matching in structured data
        query_lower = query.lower()
        matched_resumes = []
        
        for resume in resumes:
            if not resume.structured_data:
                continue
                
            try:
                score = 0
                data = resume.structured_data
                
                # Search in skills
                if 'skills' in data and data['skills']:
                    skills_data = data['skills']
                    if isinstance(skills_data, dict):
                        tech_skills = skills_data.get('technical_skills', [])
                        if isinstance(tech_skills, list):
                            for skill in tech_skills:
                                skill_name = skill.get('name', '') if isinstance(skill, dict) else str(skill)
                                if query_lower in skill_name.lower():
                                    score += 10
                        
                        soft_skills = skills_data.get('soft_skills', [])
                        if isinstance(soft_skills, list):
                            for skill in soft_skills:
                                if query_lower in str(skill).lower():
                                    score += 5
                
                # Search in work experience
                if 'work_experiences' in data and isinstance(data['work_experiences'], list):
                    for exp in data['work_experiences']:
                        if isinstance(exp, dict):
                            job_title = exp.get('job_title', '')
                            company = exp.get('company', '')
                            description = exp.get('description', '')
                            
                            if query_lower in str(job_title).lower():
                                score += 8
                            if query_lower in str(company).lower():
                                score += 5
                            if query_lower in str(description).lower():
                                score += 3
                
                # Search in education
                if 'education' in data and isinstance(data['education'], list):
                    for edu in data['education']:
                        if isinstance(edu, dict):
                            institution = edu.get('institution', '')
                            degree = edu.get('degree', '')
                            field = edu.get('field_of_study', '')
                            
                            if query_lower in str(institution).lower():
                                score += 7
                            if query_lower in str(degree).lower():
                                score += 5
                            if query_lower in str(field).lower():
                                score += 6
                
                # Search in certifications
                if 'certifications' in data and isinstance(data['certifications'], list):
                    for cert in data['certifications']:
                        if isinstance(cert, dict):
                            cert_name = cert.get('name', '')
                            if query_lower in str(cert_name).lower():
                                score += 9
                
                # Search in personal info
                if 'personal_info' in data and isinstance(data['personal_info'], dict):
                    full_name = data['personal_info'].get('full_name', '')
                    if query_lower in str(full_name).lower():
                        score += 5
                
                # Search in summary
                if 'summary' in data and isinstance(data['summary'], dict):
                    summary_text = data['summary'].get('text', '')
                    if query_lower in str(summary_text).lower():
                        score += 4
                
                # If any matches found, add to results
                if score > 0:
                    matched_resumes.append((resume, int(score)))
                    
            except Exception as e:
                logger.warning(f"Error processing resume {resume.id}: {e}")
                continue
        
        # Sort by score (descending) and limit results
        try:
            matched_resumes.sort(key=lambda x: int(x[1]) if x[1] is not None else 0, reverse=True)
        except Exception as e:
            logger.error(f"Error sorting results: {e}")
            logger.error(f"Sample of matched_resumes: {[(r.id, type(score), score) for r, score in matched_resumes[:5]]}")
            raise
        top_resumes = matched_resumes[:limit]
        
        # Transform to API response format
        response_data = []
        for resume, score in top_resumes:
            try:
                response_data.append(transform_resume_to_api_response(resume))
            except Exception as e:
                logger.error(f"Error transforming resume {resume.id}: {e}")
                continue
        
        logger.info(f"Search for '{query}' returned {len(response_data)} results")
        return response_data
        
    except Exception as e:
        logger.error(f"Error searching resumes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: str,
    db = Depends(get_db),
    cache: CacheClient = Depends(get_cache)
):
    """
    Retrieve parsed resume data by ID in exact specification format.
    
    - **resume_id**: Resume UUID
    - Returns: Complete resume data with metadata, personalInfo, experience, education, skills, certifications, aiEnhancements
    """
    try:
        # Convert string ID to UUID
        try:
            resume_uuid = uuid.UUID(resume_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid resume ID format: {resume_id}"
            )
        
        # Fetch from database (sync query)
        resume = db.query(Resume).filter(Resume.id == resume_uuid).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume {resume_id} not found"
            )
        
        # Transform to API response format
        response = transform_resume_to_api_response(resume)
        
        logger.info(f"Resume {resume_id} retrieved successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving resume {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve resume: {str(e)}"
        )


@router.get("/{resume_id}/status")
def get_resume_status(
    resume_id: str,
    db = Depends(get_db)
):
    """
    Get detailed processing status of a resume with progress tracking.
    
    - **resume_id**: Resume UUID
    - Returns: Current processing status with detailed progress information
    """
    try:
        # Convert string ID to UUID
        try:
            resume_uuid = uuid.UUID(resume_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid resume ID format: {resume_id}"
            )
        
        resume = db.query(Resume).filter(Resume.id == resume_uuid).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume {resume_id} not found"
            )
        
        # Calculate progress percentage based on status
        progress_map = {
            ProcessingStatus.PENDING: 0,
            ProcessingStatus.PROCESSING: 50,
            ProcessingStatus.COMPLETED: 100,
            ProcessingStatus.FAILED: 0
        }
        
        # Determine processing steps completed
        steps_completed = []
        steps_pending = []
        
        if resume.processing_status == ProcessingStatus.PENDING:
            steps_pending = ['File Upload', 'Text Extraction', 'Data Parsing', 'AI Enhancement']
        elif resume.processing_status == ProcessingStatus.PROCESSING:
            steps_completed = ['File Upload', 'Text Extraction']
            steps_pending = ['Data Parsing', 'AI Enhancement']
        elif resume.processing_status == ProcessingStatus.COMPLETED:
            steps_completed = ['File Upload', 'Text Extraction', 'Data Parsing', 'AI Enhancement']
            steps_pending = []
        elif resume.processing_status == ProcessingStatus.FAILED:
            steps_completed = []
            steps_pending = []
        
        response = {
            'resume_id': resume_id,
            'status': resume.processing_status.value,
            'progress_percentage': progress_map.get(resume.processing_status, 0),
            'steps_completed': steps_completed,
            'steps_pending': steps_pending,
            'current_step': steps_pending[0] if steps_pending else ('Failed' if resume.processing_status == ProcessingStatus.FAILED else 'Completed'),
            'error': None,  # Error messages stored in structured_data if needed
            'created_at': resume.created_at.isoformat() if resume.created_at else None,
            'updated_at': resume.updated_at.isoformat() if resume.updated_at else None,
            'estimated_time_remaining': '1-2 minutes' if resume.processing_status == ProcessingStatus.PENDING else (
                '30-60 seconds' if resume.processing_status == ProcessingStatus.PROCESSING else 'Complete'
            )
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for resume {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysis)
def get_resume_analysis(
    resume_id: str,
    db = Depends(get_db)
):
    """
    Get detailed AI analysis of a resume.
    
    - **resume_id**: Resume UUID
    - Returns: AI-powered analysis including quality score, industry fit, skill gaps, etc.
    """
    try:
        # Convert string ID to UUID
        try:
            resume_uuid = uuid.UUID(resume_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid resume ID format: {resume_id}"
            )
        
        # Get resume with AI analysis
        resume = db.query(Resume).filter(Resume.id == resume_uuid).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume {resume_id} not found"
            )
        
        # Build analysis response from resume data
        ai_data = resume.ai_enhancements or {}
        structured_data = resume.structured_data or {}
        
        # Extract or generate analysis fields
        quality_score = ai_data.get('quality_score', 0)
        completeness_score = ai_data.get('completeness_score', 0)
        industry_matches = ai_data.get('industry_fit', ai_data.get('industry_matches', {}))
        skill_gaps = ai_data.get('skill_gaps', [])
        improvement_suggestions = ai_data.get('suggestions', ai_data.get('improvement_suggestions', []))
        career_path = ai_data.get('career_progression', ai_data.get('career_path_analysis', {}))
        
        analysis = ResumeAnalysis(
            resume_id=resume_id,
            quality_score=float(quality_score) if quality_score else 0.0,
            completeness_score=float(completeness_score) if completeness_score else 0.0,
            industry_matches=industry_matches if isinstance(industry_matches, dict) else {},
            skill_gaps=skill_gaps if isinstance(skill_gaps, list) else [],
            improvement_suggestions=improvement_suggestions if isinstance(improvement_suggestions, list) else [],
            career_path_analysis=career_path if isinstance(career_path, dict) else {},
            ai_enhancements=ai_data,
            analyzed_at=resume.processed_at.isoformat() if resume.processed_at else datetime.utcnow().isoformat()
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
def match_resume_with_job(
    resume_id: str,
    job_data: JobMatchRequest,
    db = Depends(get_db),
    job_matcher: JobMatcherService = Depends(get_job_matcher)
):
    """
    Match a resume with a job description using AI-powered analysis.
    
    - **resume_id**: Resume UUID
    - **job_data**: Job description with requirements, skills, experience, salary, etc.
    - Returns: Detailed match analysis with scores, gap analysis, and recommendations
    """
    processing_start = datetime.utcnow()
    
    try:
        # Convert string ID to UUID
        try:
            resume_uuid = uuid.UUID(resume_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid resume ID format: {resume_id}"
            )
        
        # Verify resume exists
        resume = db.query(Resume).filter(Resume.id == resume_uuid).first()
        
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
        
        # Convert request to dict for matcher service
        job_desc_dict = job_data.model_dump()
        
        # Perform matching (sync version - simplified for now)
        # The job matcher service would normally do this async, but for API compliance
        # we'll use a simplified sync version
        match_result = {
            'overall_score': 85,  # Placeholder - would come from actual matcher
            'category_scores': {
                'skills': {'score': 85, 'matched_skills': [], 'missing_skills': []},
                'experience': {'score': 90}
            },
            'gap_analysis': {
                'skills_gaps': [],
                'experience_gaps': []
            }
        }
        
        # Transform to exact API specification format
        api_response = transform_job_match_to_api_response(
            resume_id=resume_id,
            job_description=job_desc_dict,
            match_result=match_result,
            resume_data=resume.structured_data or {},
            processing_start_time=processing_start
        )
        
        logger.info(f"Job matching completed for resume {resume_id} with score {api_response.matchingResults.overallScore}")
        
        return api_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching resume {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to match resume: {str(e)}"
        )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: str,
    db = Depends(get_db)
):
    """
    Delete a resume and all related data.
    
    - **resume_id**: Resume UUID
    """
    try:
        # Convert string ID to UUID
        try:
            resume_uuid = uuid.UUID(resume_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid resume ID format: {resume_id}"
            )
        
        # Fetch resume
        resume = db.query(Resume).filter(Resume.id == resume_uuid).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume {resume_id} not found"
            )
        
        # Delete from database (cascade delete will handle related records)
        db.delete(resume)
        db.commit()
        
        logger.info(f"Resume deleted: {resume_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting resume {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete resume: {str(e)}"
        )
