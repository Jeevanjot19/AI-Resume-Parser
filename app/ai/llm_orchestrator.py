"""
LLM orchestrator using LangChain for advanced reasoning and analysis.
"""

from typing import Dict, List, Any, Optional
# Temporarily disabling langchain imports until we can configure properly
# from langchain_openai import OpenAI
# from langchain.chains.llm import LLMChain
# from langchain.prompts import PromptTemplate
# from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from loguru import logger

from app.core.config import settings


class ResumeAnalysis(BaseModel):
    """Structured output for resume analysis."""
    quality_score: int = Field(description="Quality score from 0-100")
    completeness_score: int = Field(description="Completeness score from 0-100")
    strengths: List[str] = Field(description="Key strengths identified")
    improvements: List[str] = Field(description="Suggested improvements")
    summary: str = Field(description="Brief professional summary")


class MatchExplanation(BaseModel):
    """Structured output for job match explanation."""
    match_summary: str = Field(description="Summary of the match")
    key_alignments: List[str] = Field(description="Key areas of alignment")
    gaps: List[str] = Field(description="Identified gaps")
    recommendation: str = Field(description="Hiring recommendation")


class LLMOrchestrator:
    """LLM orchestrator for advanced analysis and reasoning."""
    
    def __init__(self):
        self.llm: Optional[Any] = None  # Changed from OpenAI type
        self._initialized = False
    
    async def initialize(self):
        """Initialize LLM."""
        if self._initialized:
            return
        
        try:
            logger.info("Initializing LLM orchestrator...")
            logger.warning("LLM features temporarily disabled - using fallback mode")
            # TODO: Properly configure OpenAI API key and initialize LangChain
            self._initialized = True
            logger.info("LLM orchestrator initialized in fallback mode")
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            self._initialized = False
    
    async def analyze_resume_quality(self, resume_text: str, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze resume quality using LLM.
        
        Args:
            resume_text: Full resume text
            structured_data: Extracted structured data
            
        Returns:
            Quality analysis results
        """
        if not self._initialized:
            await self.initialize()
        
        # Using fallback analysis for now
        return self._fallback_quality_analysis(structured_data)
        
        try:
            # Create parser
            parser = PydanticOutputParser(pydantic_object=ResumeAnalysis)
            
            # Create prompt
            prompt = PromptTemplate(
                template="""Analyze the following resume and provide a structured assessment.

Resume Text: {resume_text}

Structured Data: {structured_data}

{format_instructions}

Provide a thorough analysis focusing on:
1. Overall quality and professionalism
2. Completeness of information
3. Key strengths and achievements
4. Areas for improvement
""",
                input_variables=["resume_text", "structured_data"],
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )
            
            # Create chain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Run analysis
            result = chain.run(
                resume_text=resume_text[:1000],  # Limit length
                structured_data=str(structured_data)[:500]
            )
            
            # Parse result
            analysis = parser.parse(result)
            
            return {
                "quality_score": analysis.quality_score,
                "completeness_score": analysis.completeness_score,
                "strengths": analysis.strengths,
                "improvements": analysis.improvements,
                "summary": analysis.summary
            }
        except Exception as e:
            logger.error(f"LLM resume analysis error: {e}")
            return self._fallback_quality_analysis(structured_data)
    
    async def generate_match_explanation(
        self,
        resume_data: Dict[str, Any],
        job_description: str,
        match_scores: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate detailed explanation for resume-job match.
        
        Args:
            resume_data: Resume structured data
            job_description: Job description text
            match_scores: Calculated match scores
            
        Returns:
            Match explanation
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.llm:
            return self._fallback_match_explanation(match_scores)
        
        try:
            parser = PydanticOutputParser(pydantic_object=MatchExplanation)
            
            prompt = PromptTemplate(
                template="""Analyze the match between this candidate and job position.

Candidate Summary:
- Skills: {skills}
- Experience: {experience}
- Education: {education}

Job Description: {job_description}

Match Scores: {match_scores}

{format_instructions}

Provide a detailed explanation of:
1. Why this candidate is a good (or not good) fit
2. Key strengths that align with the job
3. Any gaps or missing qualifications
4. Hiring recommendation
""",
                input_variables=["skills", "experience", "education", "job_description", "match_scores"],
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            result = chain.run(
                skills=str(resume_data.get("skills", []))[:200],
                experience=str(resume_data.get("experience", []))[:300],
                education=str(resume_data.get("education", []))[:200],
                job_description=job_description[:500],
                match_scores=str(match_scores)
            )
            
            explanation = parser.parse(result)
            
            return {
                "summary": explanation.match_summary,
                "alignments": explanation.key_alignments,
                "gaps": explanation.gaps,
                "recommendation": explanation.recommendation
            }
        except Exception as e:
            logger.error(f"LLM match explanation error: {e}")
            return self._fallback_match_explanation(match_scores)
    
    async def extract_key_achievements(self, experience_text: str) -> List[str]:
        """
        Extract and highlight key achievements from experience text.
        
        Args:
            experience_text: Work experience text
            
        Returns:
            List of key achievements
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.llm:
            return []
        
        try:
            prompt = PromptTemplate(
                template="""Extract the most impressive achievements from this work experience.
Focus on quantifiable results, impact, and leadership.

Experience Text: {experience_text}

List 3-5 key achievements as bullet points.
""",
                input_variables=["experience_text"]
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(experience_text=experience_text[:800])
            
            # Parse bullet points
            achievements = [line.strip('- ').strip() for line in result.split('\n') if line.strip().startswith('-')]
            
            return achievements[:5]
        except Exception as e:
            logger.error(f"Achievement extraction error: {e}")
            return []
    
    def _fallback_quality_analysis(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback quality analysis without LLM."""
        # Simple rule-based analysis
        has_contact = bool(structured_data.get("email") or structured_data.get("phone"))
        has_experience = bool(structured_data.get("work_experience"))
        has_education = bool(structured_data.get("education"))
        has_skills = bool(structured_data.get("skills"))
        
        completeness_score = sum([has_contact, has_experience, has_education, has_skills]) * 25
        
        return {
            "overall_score": 70,  # Fixed: was quality_score
            "scores": {  # Fixed: added missing scores dict
                "completeness": completeness_score,
                "quality": 70
            },
            "strengths": ["Professional formatting", "Clear structure"],
            "weaknesses": ["Add more quantifiable achievements", "Expand skills section"],  # Fixed: was improvements
            "summary": "Resume demonstrates relevant experience and qualifications."
        }
    
    def _fallback_match_explanation(self, match_scores: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback match explanation without LLM."""
        overall_score = match_scores.get("overall_score", 0)
        
        if overall_score >= 80:
            recommendation = "Strong Match - Proceed with interview"
        elif overall_score >= 60:
            recommendation = "Good Match - Consider for interview"
        else:
            recommendation = "Weak Match - Review carefully"
        
        return {
            "summary": f"Candidate shows {overall_score}% match with job requirements.",
            "alignments": ["Skills alignment", "Experience level match"],
            "gaps": ["Some preferred qualifications missing"],
            "recommendation": recommendation
        }
