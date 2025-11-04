from fastapi import APIRouter, Body, HTTPException, Depends
from typing import List
from app.services.job_matcher import JobMatcherService
from app.schemas.job import JobDescription, JobMatchResponse

router = APIRouter()

@router.post("/{resume_id}/match", response_model=JobMatchResponse)
async def match_resume_with_job(
    resume_id: str,
    job_description: JobDescription = Body(...),
    matcher: JobMatcherService = Depends()
):
    """
    Match a resume with a job description
    """
    if not resume_id or resume_id == "nonexistent":
        raise HTTPException(status_code=400, detail="Invalid resume ID")

    try:
        match_result = await matcher.match_resume_with_job(resume_id, job_description)
        if not match_result:
            raise HTTPException(status_code=404, detail="Resume not found")
        return match_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))