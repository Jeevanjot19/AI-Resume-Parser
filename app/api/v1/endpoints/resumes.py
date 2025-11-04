from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from app.services.resume_parser import ResumeParserService
from app.services.ai_enhancer import AIEnhancerService
from app.schemas.resume import ResumeResponse, ResumeAnalysis

router = APIRouter()

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    parser: ResumeParserService = Depends(),
    ai_enhancer: AIEnhancerService = Depends()
):
    """
    Upload and parse a resume file
    """
    try:
        # Parse resume
        parsed_data = await parser.parse_resume(file)
        
        # Enhance with AI
        enhanced_data = await ai_enhancer.enhance_resume(parsed_data)
        
        # Ensure all required fields are present
        if not enhanced_data.get('id'):
            enhanced_data['id'] = 'temp-' + file.filename
            
        if not enhanced_data.get('metadata'):
            enhanced_data['metadata'] = {'filename': file.filename}
            
        if not enhanced_data.get('personal_info'):
            enhanced_data['personal_info'] = {
                'first_name': '',
                'last_name': '',
                'full_name': '',
                'contact': {
                    'email': '',
                    'phone': '',
                    'address': {}
                }
            }
            
        if not enhanced_data.get('summary'):
            enhanced_data['summary'] = ''
            
        if not enhanced_data.get('experience'):
            enhanced_data['experience'] = []
            
        if not enhanced_data.get('education'):
            enhanced_data['education'] = []
            
        if not enhanced_data.get('skills'):
            enhanced_data['skills'] = {
                'technical': [],
                'soft': [],
                'languages': []
            }
            
        if not enhanced_data.get('certifications'):
            enhanced_data['certifications'] = []
            
        return enhanced_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    ai_enhancer: AIEnhancerService = Depends()
):
    """
    Retrieve parsed resume data by ID
    """
    try:
        resume_data = await ai_enhancer.get_resume(resume_id)
        if not resume_data:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume_data
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{resume_id}/analysis", response_model=ResumeAnalysis)
async def get_resume_analysis(
    resume_id: str,
    ai_enhancer: AIEnhancerService = Depends()
):
    """
    Get AI-enhanced analysis of a resume
    """
    try:
        analysis = await ai_enhancer.get_resume_analysis(resume_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Resume not found")
        return analysis
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))