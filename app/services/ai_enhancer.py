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
            
            # Calculate completeness score
            completeness = self._calculate_completeness_score(structured_data)
            
            # Prepare enhancements
            enhancements = {
                'quality_score': quality_analysis.get('overall_score', 0),
                'completeness_score': completeness,
                'industry_fit': industry_fit,
                'career_analysis': career_analysis,
                'suggestions': suggestions,
                'strengths': quality_analysis.get('strengths', []),
                'weaknesses': quality_analysis.get('weaknesses', []),
                'skill_gaps': await self._identify_skill_gaps(
                    structured_data.get('skills', []),
                    industry_fit.get('top_industry')
                )
            }
            
            # Save to database
            ai_analysis = AIAnalysis(
                resume_id=resume_id,
                quality_score=enhancements['quality_score'],
                completeness_score=completeness,
                industry_matches=industry_fit,
                skill_gaps=enhancements['skill_gaps'],
                improvement_suggestions=suggestions,
                career_path_analysis=career_analysis,
                ai_enhancements=enhancements
            )
            db.add(ai_analysis)
            await db.commit()
            
            logger.info(f"Resume enhancement completed: {resume_id}")
            return enhancements
            
        except Exception as e:
            logger.error(f"Error enhancing resume: {e}")
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
        # Get top industries with scores
        industry_result = await self.classifier.classify_industry(text)
        
        # Get all industries sorted by score
        industries_sorted = sorted(
            industry_result['scores'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'top_industry': industry_result['label'],
            'confidence': industry_result['confidence'],
            'all_industries': [
                {'industry': ind, 'score': score}
                for ind, score in industries_sorted[:5]
            ]
        }
    
    async def _analyze_career_path(
        self,
        text: str,
        structured_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze career path and progression."""
        career_level = await self.classifier.determine_career_level(
            text,
            structured_data.get('total_experience_years')
        )
        
        # Define career progression paths
        progression_map = {
            'Entry Level': ['Junior', 'Mid-level'],
            'Junior': ['Mid-level', 'Senior'],
            'Mid-level': ['Senior', 'Lead'],
            'Senior': ['Lead', 'Principal'],
            'Lead': ['Principal', 'Director'],
            'Principal': ['Director', 'VP'],
            'Director': ['VP', 'C-Level'],
            'VP': ['C-Level', 'Executive'],
            'C-Level': ['Board Member', 'Advisor'],
            'Executive': ['Board Member', 'Advisor']
        }
        
        next_steps = progression_map.get(career_level['label'], [])
        
        return {
            'current_level': career_level['label'],
            'confidence': career_level['confidence'],
            'next_steps': next_steps,
            'recommended_timeline': '2-3 years' if career_level['label'] in ['Entry Level', 'Junior'] else '3-5 years'
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
