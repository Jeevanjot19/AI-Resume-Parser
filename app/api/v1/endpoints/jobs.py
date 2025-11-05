from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.resume import Resume
from app.schemas.job import JobDescription, JobMatchResponse
from app.utils.transform import transform_job_match_to_api_response
import uuid

router = APIRouter()

@router.post("/{resume_id}/match", response_model=JobMatchResponse)
def match_resume_with_job(
    resume_id: str,
    job_description: JobDescription = Body(...),
    db: Session = Depends(get_db)
):
    """
    Match a resume with a job description and provide detailed scoring
    """
    # Convert string ID to UUID
    try:
        resume_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid resume ID format")
    
    # Get resume from database
    resume = db.query(Resume).filter(Resume.id == resume_uuid).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if resume.processing_status != "COMPLETED":
        raise HTTPException(
            status_code=400, 
            detail=f"Resume processing not completed. Current status: {resume.processing_status}"
        )
    
    try:
        # Transform to match response using the utility function
        match_result = transform_job_match_to_api_response(resume, job_description)
        return match_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching resume: {str(e)}")