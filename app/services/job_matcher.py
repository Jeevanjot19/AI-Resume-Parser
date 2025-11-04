"""
Job matching service.
"""

import asyncio
from typing import Any, Dict, Optional, List
from loguru import logger
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import numpy as np

from app.ai import EmbeddingGenerator, NERExtractor
from app.models import Resume, ResumeJobMatch
from app.search import SearchClient
from app.core.config import settings


class JobMatcherService:
    """Service for matching resumes with job descriptions."""
    
    def __init__(self):
        self.embedding_gen = EmbeddingGenerator()
        self.ner_extractor = NERExtractor()
        self.search_client = SearchClient()
        self._initialized = False
    
    async def initialize(self):
        """Initialize components."""
        if self._initialized:
            return
        
        logger.info("Initializing job matcher service...")
        await asyncio.gather(
            self.embedding_gen.initialize(),
            self.ner_extractor.initialize()
        )
        self._initialized = True
        logger.info("Job matcher service initialized")
    
    async def match_resume_with_job(
        self,
        resume_id: str,
        job_description: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Match resume with job description and provide detailed analysis.
        
        Args:
            resume_id: Resume ID
            job_description: Job description data
            db: Database session
            
        Returns:
            Match analysis with scores and recommendations
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Fetch resume
            query = select(Resume).where(Resume.id == resume_id)
            result = await db.execute(query)
            resume = result.scalar_one_or_none()
            
            if not resume:
                raise ValueError(f"Resume not found: {resume_id}")
            
            logger.info(f"Matching resume {resume_id} with job")
            
            # Extract job requirements
            job_text = self._build_job_text(job_description)
            job_skills = await self.ner_extractor.extract_skills(job_text)
            
            # Calculate scores in parallel
            semantic_score, skills_score, experience_score = await asyncio.gather(
                self._calculate_semantic_similarity(resume.raw_text, job_text),
                self._calculate_skills_match(resume.structured_data.get('skills', []), job_skills),
                self._calculate_experience_match(resume.structured_data, job_description)
            )
            
            # Calculate overall score (weighted average)
            overall_score = (
                semantic_score * 0.40 +  # 40% semantic similarity
                skills_score['score'] * 0.35 +  # 35% skills match
                experience_score['score'] * 0.25  # 25% experience match
            )
            
            # Gap analysis
            gap_analysis = await self._analyze_gaps(
                resume.structured_data,
                job_skills,
                job_description
            )
            
            # Recommendations
            recommendations = await self._generate_recommendations(
                resume.structured_data,
                gap_analysis,
                overall_score
            )
            
            # Prepare result
            match_result = {
                'resume_id': resume_id,
                'job_title': job_description.get('title', 'Unknown'),
                'overall_score': round(overall_score, 2),
                'category_scores': {
                    'semantic_similarity': round(semantic_score, 2),
                    'skills': skills_score,
                    'experience': experience_score
                },
                'gap_analysis': gap_analysis,
                'recommendations': recommendations,
                'matched_at': datetime.utcnow().isoformat()
            }
            
            # Save match result
            job_match = ResumeJobMatch(
                resume_id=resume_id,
                job_id=job_description.get('id', 'unknown'),
                job_title=job_description.get('title', 'Unknown'),
                overall_score=overall_score,
                skills_match_score=skills_score['score'],
                experience_match_score=experience_score['score'],
                semantic_similarity_score=semantic_score,
                matched_skills=skills_score.get('matched_skills', []),
                missing_skills=skills_score.get('missing_skills', []),
                match_details=match_result
            )
            db.add(job_match)
            await db.commit()
            
            logger.info(f"Match completed with score: {overall_score:.2f}")
            return match_result
            
        except Exception as e:
            logger.error(f"Error matching resume with job: {e}")
            raise
    
    async def find_similar_resumes(
        self,
        job_description: Dict[str, Any],
        top_k: int = 10,
        min_score: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find resumes similar to job description using semantic search.
        
        Args:
            job_description: Job description data
            top_k: Number of results to return
            min_score: Minimum match score threshold
            
        Returns:
            List of matching resumes with scores
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Build job text and generate embedding
            job_text = self._build_job_text(job_description)
            job_embedding = await self.embedding_gen.generate_embedding(job_text)
            
            # Search for similar resumes
            results = await self.search_client.semantic_search(
                query_embedding=job_embedding,
                top_k=top_k * 2  # Get more candidates for filtering
            )
            
            # Filter by score and return top results
            matches = [
                r for r in results
                if r.get('score', 0) >= min_score
            ][:top_k]
            
            logger.info(f"Found {len(matches)} matching resumes for job")
            return matches
            
        except Exception as e:
            logger.error(f"Error finding similar resumes: {e}")
            raise
    
    async def _calculate_semantic_similarity(
        self,
        resume_text: str,
        job_text: str
    ) -> float:
        """Calculate semantic similarity between resume and job."""
        # Generate embeddings
        resume_emb, job_emb = await asyncio.gather(
            self.embedding_gen.generate_embedding(resume_text),
            self.embedding_gen.generate_embedding(job_text)
        )
        
        # Calculate cosine similarity
        resume_vec = np.array(resume_emb).reshape(1, -1)
        job_vec = np.array(job_emb).reshape(1, -1)
        
        similarity = np.dot(resume_vec, job_vec.T) / (
            np.linalg.norm(resume_vec) * np.linalg.norm(job_vec)
        )
        
        # Convert to percentage (0-100)
        return float(similarity[0][0] * 100)
    
    async def _calculate_skills_match(
        self,
        resume_skills: List[str],
        job_skills: List[str]
    ) -> Dict[str, Any]:
        """Calculate skills match score."""
        if not job_skills:
            return {'score': 100.0, 'matched_skills': [], 'missing_skills': []}
        
        # Normalize skills for comparison
        resume_skills_lower = [s.lower().strip() for s in resume_skills]
        job_skills_lower = [s.lower().strip() for s in job_skills]
        
        # Find matches
        matched = [
            skill for skill in job_skills
            if skill.lower().strip() in resume_skills_lower
        ]
        
        missing = [
            skill for skill in job_skills
            if skill.lower().strip() not in resume_skills_lower
        ]
        
        # Calculate score
        score = (len(matched) / len(job_skills)) * 100 if job_skills else 100.0
        
        return {
            'score': round(score, 2),
            'matched_skills': matched,
            'missing_skills': missing,
            'total_required': len(job_skills),
            'total_matched': len(matched)
        }
    
    async def _calculate_experience_match(
        self,
        resume_data: Dict[str, Any],
        job_description: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate experience match score."""
        score = 100.0
        details = {}
        
        # Check years of experience
        resume_years = resume_data.get('total_experience_years', 0)
        required_years = job_description.get('required_experience_years', 0)
        
        if required_years > 0:
            if resume_years >= required_years:
                details['years_match'] = True
                details['years_score'] = 100.0
            else:
                gap = required_years - resume_years
                details['years_match'] = False
                details['years_gap'] = gap
                details['years_score'] = max(0, 100 - (gap * 20))  # -20% per year gap
                score -= gap * 10  # Reduce overall score
        
        # Check industry match
        resume_industry = resume_data.get('industry_classification', {}).get('label', '')
        job_industry = job_description.get('industry', '')
        
        if job_industry and resume_industry:
            if resume_industry.lower() == job_industry.lower():
                details['industry_match'] = True
            else:
                details['industry_match'] = False
                score -= 15  # -15% for industry mismatch
        
        # Check career level
        resume_level = resume_data.get('career_level', {}).get('label', '')
        job_level = job_description.get('level', '')
        
        if job_level and resume_level:
            level_order = ['Entry Level', 'Junior', 'Mid-level', 'Senior', 'Lead', 'Principal', 'Director', 'VP', 'C-Level']
            try:
                resume_idx = level_order.index(resume_level)
                job_idx = level_order.index(job_level)
                
                if resume_idx >= job_idx:
                    details['level_match'] = True
                else:
                    details['level_match'] = False
                    score -= 10  # -10% for level mismatch
            except ValueError:
                pass  # Level not in predefined list
        
        return {
            'score': max(0, round(score, 2)),
            **details
        }
    
    async def _analyze_gaps(
        self,
        resume_data: Dict[str, Any],
        job_skills: List[str],
        job_description: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze gaps between resume and job requirements."""
        gaps = {
            'critical_gaps': [],
            'improvement_areas': [],
            'strengths': []
        }
        
        # Skills gaps
        resume_skills = [s.lower() for s in resume_data.get('skills', [])]
        missing_skills = [
            skill for skill in job_skills
            if skill.lower() not in resume_skills
        ]
        
        if missing_skills:
            gaps['critical_gaps'].extend([
                f"Missing required skill: {skill}"
                for skill in missing_skills[:3]  # Top 3
            ])
        
        # Experience gap
        resume_years = resume_data.get('total_experience_years', 0)
        required_years = job_description.get('required_experience_years', 0)
        
        if required_years > resume_years:
            gap_years = required_years - resume_years
            gaps['improvement_areas'].append(
                f"Gain {gap_years} more year(s) of relevant experience"
            )
        else:
            gaps['strengths'].append(
                f"Meets experience requirement ({resume_years} years)"
            )
        
        # Education
        education = resume_data.get('education', [])
        required_degree = job_description.get('required_degree', '')
        
        if required_degree and not education:
            gaps['critical_gaps'].append(
                f"No education listed (requires: {required_degree})"
            )
        elif education:
            gaps['strengths'].append("Education background provided")
        
        return gaps
    
    async def _generate_recommendations(
        self,
        resume_data: Dict[str, Any],
        gap_analysis: Dict[str, Any],
        overall_score: float
    ) -> List[str]:
        """Generate recommendations for improvement."""
        recommendations = []
        
        # Based on score
        if overall_score < 70:
            recommendations.append(
                "Consider acquiring missing skills to improve match score"
            )
        
        # Based on gaps
        if gap_analysis['critical_gaps']:
            recommendations.append(
                "Address critical gaps: " + ", ".join(gap_analysis['critical_gaps'][:2])
            )
        
        # Based on improvement areas
        if gap_analysis['improvement_areas']:
            recommendations.extend(gap_analysis['improvement_areas'][:2])
        
        # Generic recommendations
        if overall_score >= 85:
            recommendations.append("Strong match! Consider applying for this position")
        elif overall_score >= 70:
            recommendations.append("Good match. Highlight relevant experience in your application")
        else:
            recommendations.append("Focus on building required skills before applying")
        
        return recommendations[:5]  # Return top 5
    
    def _build_job_text(self, job_description: Dict[str, Any]) -> str:
        """Build complete job text for analysis."""
        parts = []
        
        if job_description.get('title'):
            parts.append(f"Title: {job_description['title']}")
        
        if job_description.get('description'):
            parts.append(f"Description: {job_description['description']}")
        
        if job_description.get('requirements'):
            if isinstance(job_description['requirements'], list):
                parts.append("Requirements: " + ", ".join(job_description['requirements']))
            else:
                parts.append(f"Requirements: {job_description['requirements']}")
        
        if job_description.get('responsibilities'):
            if isinstance(job_description['responsibilities'], list):
                parts.append("Responsibilities: " + ", ".join(job_description['responsibilities']))
            else:
                parts.append(f"Responsibilities: {job_description['responsibilities']}")
        
        return "\n".join(parts)
