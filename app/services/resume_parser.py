"""
Integrated resume parser service.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
from loguru import logger

from app.document_processors import DocumentProcessorFactory
from app.document_processors.file_validator import FileValidator
from app.ai import NERExtractor, TextClassifier, EmbeddingGenerator, LLMOrchestrator
from app.models import Resume, PersonInfo, WorkExperience, Education, Skill, AIAnalysis
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession


class ResumeParserService:
    """Integrated resume parsing service."""
    
    def __init__(self):
        self.processor_factory = DocumentProcessorFactory(use_tika=True)
        self.ner_extractor = NERExtractor()
        self.classifier = TextClassifier()
        self.embedding_gen = EmbeddingGenerator()
        self.llm = LLMOrchestrator()
        self._initialized = False
    
    async def initialize(self):
        """Initialize all components."""
        if self._initialized:
            return
        
        logger.info("Initializing resume parser service...")
        await asyncio.gather(
            self.ner_extractor.initialize(),
            self.classifier.initialize(),
            self.embedding_gen.initialize(),
            self.llm.initialize()
        )
        self._initialized = True
        logger.info("Resume parser service initialized")
    
    async def parse_resume(
        self,
        file_path: Path,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Parse resume file and extract all information.
        
        Args:
            file_path: Path to uploaded resume file
            db: Database session
            
        Returns:
            Parsed resume data
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Validate file
            is_valid, error_msg = FileValidator.validate_file(file_path)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Calculate file hash
            file_hash = FileValidator.calculate_file_hash(file_path)
            
            # Process document
            logger.info(f"Processing document: {file_path.name}")
            document_data = await self.processor_factory.process_file(file_path)
            
            text = document_data.get('text', '')
            metadata = document_data.get('metadata', {})
            
            if not text or len(text) < 50:
                raise ValueError("Insufficient text extracted from document")
            
            # Extract all information in parallel
            logger.info("Extracting information from resume...")
            entities, skills, industry_class, role_class, embedding = await asyncio.gather(
                self.ner_extractor.extract_entities(text),
                self.ner_extractor.extract_skills(text),
                self.classifier.classify_industry(text),
                self.classifier.classify_job_role(text),
                self.embedding_gen.generate_embedding(text)
            )
            
            # Parse structured data
            structured_data = await self._parse_structured_data(text, entities, skills)
            
            # Determine career level
            career_level = await self.classifier.determine_career_level(
                text,
                structured_data.get('total_experience_years')
            )
            
            # Analyze quality with LLM
            quality_analysis = await self.llm.analyze_resume_quality(text, structured_data)
            
            # Prepare result
            result = {
                'file_name': file_path.name,
                'file_hash': file_hash,
                'file_size': file_path.stat().st_size,
                'file_type': file_path.suffix[1:],
                'raw_text': text,
                'metadata': metadata,
                'structured_data': structured_data,
                'entities': entities,
                'skills': skills,
                'industry_classification': industry_class,
                'role_classification': role_class,
                'career_level': career_level,
                'quality_analysis': quality_analysis,
                'embedding': embedding,
                'processed_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Resume parsing completed: {file_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            raise
    
    async def _parse_structured_data(
        self,
        text: str,
        entities: Dict[str, Any],
        skills: list
    ) -> Dict[str, Any]:
        """Parse structured data from text and entities."""
        
        # Extract personal info
        personal_info = {
            'full_name': entities.get('persons', [None])[0] if entities.get('persons') else None,
            'email': entities.get('emails', [None])[0] if entities.get('emails') else None,
            'phone': entities.get('phones', [None])[0] if entities.get('phones') else None,
            'location': entities.get('locations', [None])[0] if entities.get('locations') else None,
        }
        
        # Extract work experience (simplified - should use more sophisticated parsing)
        work_experience = await self._extract_work_experience(text, entities)
        
        # Extract education (simplified)
        education = await self._extract_education(text, entities)
        
        # Calculate total experience
        total_experience_years = len(work_experience) * 2  # Rough estimate
        
        return {
            'personal_info': personal_info,
            'work_experience': work_experience,
            'education': education,
            'skills': skills,
            'total_experience_years': total_experience_years
        }
    
    async def _extract_work_experience(
        self,
        text: str,
        entities: Dict[str, Any]
    ) -> list:
        """Extract work experience from text."""
        # Simplified extraction - in production, use more sophisticated NLP
        organizations = entities.get('organizations', [])
        dates = entities.get('dates', [])
        
        experiences = []
        for org in organizations[:5]:  # Limit to 5 companies
            experiences.append({
                'company': org,
                'title': 'Position',  # Should extract from context
                'description': '',
                'technologies': []
            })
        
        return experiences
    
    async def _extract_education(
        self,
        text: str,
        entities: Dict[str, Any]
    ) -> list:
        """Extract education from text."""
        # Simplified extraction
        education_keywords = ['university', 'college', 'institute', 'school']
        locations = entities.get('locations', [])
        
        education = []
        for loc in locations:
            if any(keyword in loc.lower() for keyword in education_keywords):
                education.append({
                    'institution': loc,
                    'degree': 'Degree',  # Should extract from context
                    'field': '',
                    'graduation_date': None
                })
        
        return education
