"""
AI enhancement service.
"""

import asyncio
from typing import Any, Dict, Optional, List
from loguru import logger
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.ai import LLMOrchestrator, TextClassifier, EmbeddingGenerator
from app.models import Resume, AIAnalysis
from app.core.config import settings


class AIEnhancerService:
    """Service for AI-powered resume enhancements."""
    
    def __init__(self):
        self.llm = LLMOrchestrator()
        self.classifier = TextClassifier()
        self.embedding_gen = EmbeddingGenerator()
        self._initialized = False
    
    async def initialize(self):
        """Initialize AI components."""
        if self._initialized:
            return
        
        logger.info("Initializing AI enhancer service...")
        await self.llm.initialize()
        await self.classifier.initialize()
        await self.embedding_gen.initialize()
        self._initialized = True
        logger.info("AI enhancer service initialized")
    
    async def enhance_resume(
        self,
        resume_id: str,
        resume_text: str,
        structured_data: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Enhance resume data with AI-powered insights.
        
        Args:
            resume_id: Resume ID
            resume_text: Raw resume text
            structured_data: Parsed structured data
            db: Database session
            
        Returns:
            AI enhancements data
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.info(f"Enhancing resume: {resume_id}")
            
            # Generate all enhancements in parallel
            quality_analysis, industry_fit, career_analysis, suggestions = await asyncio.gather(
                self.llm.analyze_resume_quality(resume_text, structured_data),
                self._analyze_industry_fit(resume_text),
                self._analyze_career_path(resume_text, structured_data),
                self._generate_suggestions(resume_text, structured_data)
            )
            
            # Validate that all required data is in correct format
            if not isinstance(quality_analysis, dict):
                logger.error(f"quality_analysis is not a dict: {type(quality_analysis)}")
                quality_analysis = {'overall_score': 0, 'strengths': [], 'weaknesses': []}
            
            if not isinstance(industry_fit, dict):
                logger.error(f"industry_fit is not a dict: {type(industry_fit)}")
                industry_fit = {'top_industry': 'Unknown', 'confidence': 0.0, 'all_industries': []}
            
            if not isinstance(career_analysis, dict):
                logger.error(f"career_analysis is not a dict: {type(career_analysis)}")
                career_analysis = {}
            
            if not isinstance(suggestions, list):
                logger.error(f"suggestions is not a list: {type(suggestions)}")
                suggestions = []
            
            # Calculate completeness score
            completeness = self._calculate_completeness_score(structured_data)
            
            # Prepare enhancements
            skill_gaps = await self._identify_skill_gaps(
                structured_data.get('skills', []),
                industry_fit.get('top_industry')
            )
            
            enhancements = {
                'quality_score': quality_analysis.get('overall_score', 0),
                'completeness_score': completeness,
                'industry_fit': industry_fit,
                'career_analysis': career_analysis,
                'suggestions': suggestions,
                'strengths': quality_analysis.get('strengths', []),
                'weaknesses': quality_analysis.get('weaknesses', []),
                'skill_gaps': skill_gaps
            }
            
            # Prepare confidence scores
            confidence_scores = {
                'quality': quality_analysis.get('overall_score', 0) / 100.0,
                'industry_fit': industry_fit.get('confidence', 0.0),
                'career_level': career_analysis.get('confidence', 0.0)
            }
            
            # Save to database with correct field names
            ai_analysis = AIAnalysis(
                resume_id=resume_id,
                quality_score=enhancements['quality_score'],
                completeness_score=completeness,
                industry_classifications=industry_fit,  # Changed from industry_matches
                career_level=career_analysis.get('current_level', 'mid'),  # Changed from career_path_analysis
                suggestions=suggestions,  # Changed from improvement_suggestions
                confidence_scores=confidence_scores  # Added confidence scores
            )
            db.add(ai_analysis)
            await db.commit()
            
            logger.info(f"Resume enhancement completed: {resume_id}")
            return enhancements
            return enhancements
            
        except Exception as e:
            logger.error(f"Error enhancing resume: {e}", exc_info=True)
            raise
    
    async def get_resume_analysis(
        self,
        resume_id: str,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Get detailed AI analysis of a resume."""
        query = select(AIAnalysis).where(AIAnalysis.resume_id == resume_id)
        result = await db.execute(query)
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            return None
        
        return {
            'resume_id': resume_id,
            'quality_score': analysis.quality_score,
            'completeness_score': analysis.completeness_score,
            'industry_matches': analysis.industry_matches,
            'skill_gaps': analysis.skill_gaps,
            'improvement_suggestions': analysis.improvement_suggestions,
            'career_path_analysis': analysis.career_path_analysis,
            'ai_enhancements': analysis.ai_enhancements,
            'analyzed_at': analysis.created_at.isoformat()
        }
    
    async def _analyze_industry_fit(self, text: str) -> Dict[str, Any]:
        """Analyze industry fit with confidence scores."""
        try:
            # Get top industries with scores
            industry_scores = await self.classifier.classify_industry(text)
            
            # Handle case where classify_industry returns unexpected type
            if not isinstance(industry_scores, dict):
                logger.warning(f"classify_industry returned unexpected type: {type(industry_scores)}")
                industry_scores = {"Unknown": 0.5}
            
            # Get all industries sorted by score
            industries_sorted = sorted(
                industry_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Get top industry
            top_industry, top_score = industries_sorted[0] if industries_sorted else ("Unknown", 0.0)
            
            return {
                'top_industry': top_industry,
                'confidence': float(top_score),
                'all_industries': [
                    {'industry': ind, 'score': float(score)}
                    for ind, score in industries_sorted[:5]
                ]
            }
        except Exception as e:
            logger.error(f"Error in _analyze_industry_fit: {e}")
            return {
                'top_industry': 'Unknown',
                'confidence': 0.0,
                'all_industries': []
            }
    
    async def _analyze_career_path(
        self,
        text: str,
        structured_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze career path and progression."""
        try:
            career_level = await self.classifier.determine_career_level(
                text,
                structured_data.get('total_experience_years')
            )
            
            # career_level is a string, not a dict
            if not isinstance(career_level, str):
                logger.warning(f"career_level is not a string: {type(career_level)}")
                career_level = "mid"
            
            # Define career progression paths
            progression_map = {
                'entry': ['mid', 'senior'],
                'mid': ['senior', 'lead'],
                'senior': ['lead', 'principal'],
                'lead': ['principal', 'director'],
                'principal': ['director', 'vp'],
                'director': ['vp', 'executive'],
                'vp': ['executive', 'c-level'],
                'executive': ['board member', 'advisor'],
                'c-level': ['board member', 'advisor']
            }
            
            career_level_lower = career_level.lower()
            next_steps = progression_map.get(career_level_lower, ['senior', 'lead'])
            
            return {
                'current_level': career_level,
                'confidence': 0.7,  # Default confidence since we don't get it from classifier
                'next_steps': next_steps,
                'recommended_timeline': '2-3 years' if career_level_lower in ['entry', 'junior'] else '3-5 years'
            }
        except Exception as e:
            logger.error(f"Error in _analyze_career_path: {e}")
            return {
                'current_level': 'mid',
                'confidence': 0.5,
                'next_steps': ['senior', 'lead'],
                'recommended_timeline': '3-5 years'
            }
    
    async def _generate_suggestions(
        self,
        text: str,
        structured_data: Dict[str, Any]
    ) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        # Check completeness
        personal_info = structured_data.get('personal_info', {})
        if not personal_info.get('email'):
            suggestions.append("Add email address for better visibility")
        if not personal_info.get('phone'):
            suggestions.append("Include phone number for direct contact")
        
        # Check experience details
        experiences = structured_data.get('work_experience', [])
        if len(experiences) < 2:
            suggestions.append("Add more work experience details to strengthen your profile")
        
        # Check skills
        skills = structured_data.get('skills', [])
        if len(skills) < 5:
            suggestions.append("List more skills to improve searchability")
        
        # Check education
        education = structured_data.get('education', [])
        if not education:
            suggestions.append("Include educational background")
        
        # Text length check
        if len(text) < 500:
            suggestions.append("Expand resume content with more details and achievements")
        
        return suggestions
    
    def _calculate_completeness_score(self, structured_data: Dict[str, Any]) -> float:
        """Calculate completeness score based on available fields."""
        score = 0.0
        max_score = 100.0
        
        personal_info = structured_data.get('personal_info', {})
        
        # Personal info (30 points)
        if personal_info.get('full_name'):
            score += 10
        if personal_info.get('email'):
            score += 10
        if personal_info.get('phone'):
            score += 10
        
        # Work experience (30 points)
        experiences = structured_data.get('work_experience', [])
        score += min(30, len(experiences) * 10)
        
        # Education (20 points)
        education = structured_data.get('education', [])
        score += min(20, len(education) * 10)
        
        # Skills (20 points)
        skills = structured_data.get('skills', [])
        score += min(20, len(skills) * 2)
        
        return round(score, 2)
    
    async def _identify_skill_gaps(
        self,
        current_skills: List[str],
        target_industry: Optional[str]
    ) -> List[str]:
        """Identify skill gaps for target industry."""
        if not target_industry:
            return []
        
        # Industry-specific skill requirements
        industry_skills = {
            'Software Engineering': ['Python', 'JavaScript', 'Git', 'Docker', 'Kubernetes', 'AWS', 'CI/CD'],
            'Data Science': ['Python', 'R', 'SQL', 'Machine Learning', 'Statistics', 'TensorFlow', 'PyTorch'],
            'Product Management': ['Agile', 'Scrum', 'Product Strategy', 'Analytics', 'User Research'],
            'Marketing': ['SEO', 'Content Marketing', 'Analytics', 'Social Media', 'Email Marketing'],
            'Finance': ['Excel', 'Financial Modeling', 'SQL', 'Python', 'Risk Management']
        }
        
        required_skills = industry_skills.get(target_industry, [])
        current_skills_lower = [s.lower() for s in current_skills]
        
        gaps = [
            skill for skill in required_skills
            if skill.lower() not in current_skills_lower
        ]
        
        return gaps[:5]  # Return top 5 gaps
