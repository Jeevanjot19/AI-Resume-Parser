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
        """Analyze career path and progression with detailed insights."""
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
                'junior': ['mid', 'senior'],
                'mid': ['senior', 'lead'],
                'senior': ['lead', 'principal', 'staff'],
                'lead': ['principal', 'staff', 'director'],
                'principal': ['director', 'distinguished'],
                'staff': ['principal', 'director'],
                'director': ['senior director', 'vp'],
                'vp': ['svp', 'executive'],
                'svp': ['executive', 'c-level'],
                'executive': ['c-level', 'board member'],
                'c-level': ['board member', 'advisor']
            }
            
            career_level_lower = career_level.lower()
            next_steps = progression_map.get(career_level_lower, ['senior', 'lead'])
            
            # Analyze career progression from work experience
            work_exp = structured_data.get('work_experience', [])
            progression_analysis = self._analyze_career_progression(work_exp)
            
            # Calculate experience level confidence based on years
            total_years = structured_data.get('total_experience_years', 0)
            confidence = self._calculate_career_confidence(career_level_lower, total_years)
            
            return {
                'current_level': career_level,
                'confidence': confidence,
                'next_steps': next_steps,
                'recommended_timeline': self._get_progression_timeline(career_level_lower),
                'progression_trajectory': progression_analysis.get('trajectory', 'steady'),
                'growth_rate': progression_analysis.get('growth_rate', 'normal'),
                'leadership_indicators': progression_analysis.get('leadership_indicators', [])
            }
        except Exception as e:
            logger.error(f"Error in _analyze_career_path: {e}")
            return {
                'current_level': 'mid',
                'confidence': 0.5,
                'next_steps': ['senior', 'lead'],
                'recommended_timeline': '3-5 years',
                'progression_trajectory': 'steady',
                'growth_rate': 'normal',
                'leadership_indicators': []
            }
    
    def _analyze_career_progression(self, work_experience: List[Dict]) -> Dict[str, Any]:
        """Analyze career progression from work history."""
        if not work_experience or len(work_experience) < 2:
            return {
                'trajectory': 'insufficient_data',
                'growth_rate': 'unknown',
                'leadership_indicators': []
            }
        
        # Extract seniority levels from job titles
        seniority_keywords = {
            'entry': ['intern', 'trainee', 'junior', 'associate'],
            'mid': ['engineer', 'developer', 'analyst', 'specialist'],
            'senior': ['senior', 'sr.', 'lead'],
            'leadership': ['manager', 'director', 'head of', 'vp', 'chief', 'principal', 'staff']
        }
        
        job_levels = []
        leadership_indicators = []
        
        for exp in work_experience:
            title = exp.get('title', '').lower()
            
            # Determine level
            if any(kw in title for kw in seniority_keywords['leadership']):
                job_levels.append(3)
                leadership_indicators.append(f"Leadership role: {exp.get('title')}")
            elif any(kw in title for kw in seniority_keywords['senior']):
                job_levels.append(2)
            elif any(kw in title for kw in seniority_keywords['entry']):
                job_levels.append(0)
            else:
                job_levels.append(1)  # mid-level
        
        # Analyze trajectory
        if len(job_levels) >= 2:
            if job_levels[-1] > job_levels[0]:
                trajectory = 'ascending'
                growth_rate = 'fast' if (job_levels[-1] - job_levels[0]) >= 2 else 'normal'
            elif job_levels[-1] < job_levels[0]:
                trajectory = 'descending'
                growth_rate = 'normal'
            else:
                trajectory = 'steady'
                growth_rate = 'normal'
        else:
            trajectory = 'steady'
            growth_rate = 'normal'
        
        return {
            'trajectory': trajectory,
            'growth_rate': growth_rate,
            'leadership_indicators': leadership_indicators
        }
    
    def _calculate_career_confidence(self, career_level: str, total_years: float) -> float:
        """Calculate confidence in career level determination."""
        expected_years = {
            'entry': (0, 2),
            'junior': (0, 3),
            'mid': (2, 7),
            'senior': (5, 12),
            'lead': (7, 15),
            'principal': (10, 20),
            'staff': (10, 20),
            'director': (12, 25),
            'vp': (15, 30),
            'executive': (20, 40)
        }
        
        if career_level not in expected_years:
            return 0.5
        
        min_years, max_years = expected_years[career_level]
        
        if min_years <= total_years <= max_years:
            return 0.9
        elif total_years < min_years:
            return 0.6  # Might be high performer
        else:
            return 0.7  # Experienced in level
    
    def _get_progression_timeline(self, career_level: str) -> str:
        """Get recommended timeline for next career step."""
        timelines = {
            'entry': '1-2 years',
            'junior': '2-3 years',
            'mid': '3-5 years',
            'senior': '4-6 years',
            'lead': '5-7 years',
            'principal': '5-10 years',
            'staff': '5-10 years',
            'director': '7-10 years',
            'vp': '10+ years',
            'executive': '10+ years'
        }
        return timelines.get(career_level, '3-5 years')
    
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
        """Identify skill gaps for target industry with priority levels."""
        if not target_industry:
            return []
        
        # Industry-specific skill requirements with priority levels
        industry_skills = {
            'Software Engineering': {
                'critical': ['Python', 'JavaScript', 'Git', 'SQL'],
                'important': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'React'],
                'emerging': ['Rust', 'Go', 'WebAssembly', 'Serverless']
            },
            'Data Science': {
                'critical': ['Python', 'SQL', 'Machine Learning', 'Statistics'],
                'important': ['R', 'TensorFlow', 'PyTorch', 'Pandas', 'Data Visualization'],
                'emerging': ['MLOps', 'AutoML', 'LLMs', 'Feature Engineering']
            },
            'Product Management': {
                'critical': ['Agile', 'Product Strategy', 'User Research'],
                'important': ['Scrum', 'Analytics', 'SQL', 'A/B Testing'],
                'emerging': ['AI Product Management', 'Growth Hacking', 'Product-Led Growth']
            },
            'Marketing': {
                'critical': ['SEO', 'Content Marketing', 'Analytics'],
                'important': ['Social Media', 'Email Marketing', 'Google Ads', 'Marketing Automation'],
                'emerging': ['AI Marketing', 'Influencer Marketing', 'Voice Search', 'Video Marketing']
            },
            'Finance': {
                'critical': ['Excel', 'Financial Modeling', 'Risk Management'],
                'important': ['SQL', 'Python', 'Bloomberg Terminal', 'VBA'],
                'emerging': ['Blockchain', 'DeFi', 'Algorithmic Trading', 'FinTech']
            },
            'Technology': {
                'critical': ['Programming', 'Software Development', 'APIs'],
                'important': ['Cloud Computing', 'DevOps', 'Security', 'Testing'],
                'emerging': ['AI/ML', 'Edge Computing', 'Quantum Computing']
            }
        }
        
        skill_requirements = industry_skills.get(target_industry, {
            'critical': [],
            'important': [],
            'emerging': []
        })
        
        current_skills_lower = [s.lower() for s in current_skills]
        gaps = []
        
        # Check critical skills first
        for skill in skill_requirements.get('critical', []):
            if skill.lower() not in current_skills_lower:
                gaps.append(f"{skill} [CRITICAL]")
        
        # Then important skills
        for skill in skill_requirements.get('important', [])[:3]:
            if skill.lower() not in current_skills_lower:
                gaps.append(f"{skill} [Important]")
        
        # Finally emerging skills
        for skill in skill_requirements.get('emerging', [])[:2]:
            if skill.lower() not in current_skills_lower:
                gaps.append(f"{skill} [Emerging Trend]")
        
        return gaps[:5]  # Return top 5 gaps
    
    def score_skill_relevance(
        self,
        skills: List[str],
        industry: str,
        job_level: str
    ) -> Dict[str, float]:
        """
        Score skill relevance for a given industry and job level.
        
        Args:
            skills: List of candidate skills
            industry: Target industry
            job_level: Career level (entry, mid, senior, etc.)
        
        Returns:
            Dictionary mapping skills to relevance scores (0.0 to 1.0)
        """
        skill_scores = {}
        
        # Industry relevance weights
        industry_weights = {
            'Software Engineering': {
                'Python': 0.95, 'JavaScript': 0.95, 'Git': 0.90, 'Docker': 0.85,
                'React': 0.85, 'SQL': 0.85, 'AWS': 0.90, 'Kubernetes': 0.80
            },
            'Data Science': {
                'Python': 0.98, 'Machine Learning': 0.95, 'SQL': 0.90, 'Statistics': 0.95,
                'TensorFlow': 0.85, 'PyTorch': 0.85, 'Pandas': 0.90, 'R': 0.80
            },
            'Finance': {
                'Excel': 0.95, 'Financial Modeling': 0.90, 'SQL': 0.80, 'Python': 0.75,
                'Risk Management': 0.85, 'VBA': 0.70
            },
            'Marketing': {
                'SEO': 0.90, 'Content Marketing': 0.85, 'Analytics': 0.85,
                'Social Media': 0.80, 'Email Marketing': 0.75
            },
            'Technology': {
                'Programming': 0.90, 'Cloud': 0.85, 'DevOps': 0.80, 'APIs': 0.85
            }
        }
        
        # Level-based multipliers (senior roles value breadth, entry values fundamentals)
        level_multipliers = {
            'entry': 0.7,
            'junior': 0.75,
            'mid': 0.85,
            'senior': 0.95,
            'lead': 1.0,
            'principal': 1.0,
            'staff': 1.0,
            'director': 0.9,  # Directors focus more on strategy
            'vp': 0.85,
            'executive': 0.80
        }
        
        industry_skill_weights = industry_weights.get(industry, {})
        level_mult = level_multipliers.get(job_level.lower(), 0.85)
        
        for skill in skills:
            # Get base relevance score for this skill in the industry
            base_score = industry_skill_weights.get(skill, 0.5)  # Default 0.5 for unknown
            
            # Apply level multiplier
            final_score = min(1.0, base_score * level_mult)
            skill_scores[skill] = round(final_score, 2)
        
        return skill_scores
