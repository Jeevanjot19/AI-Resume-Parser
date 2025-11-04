"""
Celery tasks for async resume processing.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any
from celery import Task
from loguru import logger

from app.worker.celery import celery
from app.document_processors import DocumentProcessorFactory
from app.ai import NERExtractor, TextClassifier, EmbeddingGenerator


class CallbackTask(Task):
    """Base task with callbacks."""
    
    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")


@celery.task(base=CallbackTask, bind=True)
def process_resume_task(self, file_path: str, resume_id: str) -> Dict[str, Any]:
    """
    Process resume asynchronously.
    
    Args:
        file_path: Path to uploaded resume file
        resume_id: Resume UUID
        
    Returns:
        Processing results
    """
    logger.info(f"Starting resume processing for {resume_id}")
    
    try:
        # Update task progress
        self.update_state(state='PROCESSING', meta={'progress': 10})
        
        # Process document
        loop = asyncio.get_event_loop()
        processor_factory = DocumentProcessorFactory(use_tika=True)
        
        document_data = loop.run_until_complete(
            processor_factory.process_file(Path(file_path))
        )
        
        text = document_data.get('text', '')
        metadata = document_data.get('metadata', {})
        
        self.update_state(state='PROCESSING', meta={'progress': 30})
        
        # Extract entities
        ner_extractor = NERExtractor()
        entities = loop.run_until_complete(
            ner_extractor.extract_entities(text)
        )
        
        self.update_state(state='PROCESSING', meta={'progress': 50})
        
        # Extract skills
        skills = loop.run_until_complete(
            ner_extractor.extract_skills(text)
        )
        
        self.update_state(state='PROCESSING', meta={'progress': 60})
        
        # Classify industry and role
        classifier = TextClassifier()
        industry_classification = loop.run_until_complete(
            classifier.classify_industry(text)
        )
        
        role_classification = loop.run_until_complete(
            classifier.classify_job_role(text)
        )
        
        self.update_state(state='PROCESSING', meta={'progress': 75})
        
        # Generate embedding
        embedding_gen = EmbeddingGenerator()
        embedding = loop.run_until_complete(
            embedding_gen.generate_embedding(text)
        )
        
        self.update_state(state='PROCESSING', meta={'progress': 90})
        
        result = {
            'resume_id': resume_id,
            'text': text,
            'metadata': metadata,
            'entities': entities,
            'skills': skills,
            'industry_classification': industry_classification,
            'role_classification': role_classification,
            'embedding': embedding,
            'status': 'completed'
        }
        
        logger.info(f"Resume processing completed for {resume_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing resume {resume_id}: {e}")
        return {
            'resume_id': resume_id,
            'status': 'failed',
            'error': str(e)
        }


@celery.task(base=CallbackTask)
def calculate_match_score_task(resume_id: str, job_id: str, resume_data: Dict, job_data: Dict) -> Dict[str, Any]:
    """
    Calculate resume-job match score asynchronously.
    
    Args:
        resume_id: Resume UUID
        job_id: Job ID
        resume_data: Resume structured data
        job_data: Job description data
        
    Returns:
        Match calculation results
    """
    logger.info(f"Calculating match score for resume {resume_id} and job {job_id}")
    
    try:
        loop = asyncio.get_event_loop()
        
        # Generate embeddings
        embedding_gen = EmbeddingGenerator()
        
        resume_text = resume_data.get('text', '')
        job_text = job_data.get('description', '')
        
        similarity = loop.run_until_complete(
            embedding_gen.calculate_similarity(resume_text, job_text)
        )
        
        # Calculate component scores
        skills_match = calculate_skills_match(
            resume_data.get('skills', []),
            job_data.get('required_skills', [])
        )
        
        experience_match = calculate_experience_match(
            resume_data.get('experience', []),
            job_data.get('required_experience', 0)
        )
        
        # Calculate overall score
        overall_score = int(
            similarity * 40 +
            skills_match * 35 +
            experience_match * 25
        )
        
        return {
            'resume_id': resume_id,
            'job_id': job_id,
            'overall_score': overall_score,
            'similarity_score': similarity,
            'skills_match': skills_match,
            'experience_match': experience_match,
            'status': 'completed'
        }
        
    except Exception as e:
        logger.error(f"Error calculating match score: {e}")
        return {
            'resume_id': resume_id,
            'job_id': job_id,
            'status': 'failed',
            'error': str(e)
        }


def calculate_skills_match(resume_skills: list, required_skills: list) -> float:
    """Calculate skills match percentage."""
    if not required_skills:
        return 100.0
    
    resume_skills_lower = [s.lower() for s in resume_skills]
    required_skills_lower = [s.lower() for s in required_skills]
    
    matched = sum(1 for skill in required_skills_lower if skill in resume_skills_lower)
    
    return (matched / len(required_skills)) * 100


def calculate_experience_match(work_experience: list, required_years: int) -> float:
    """Calculate experience match percentage."""
    if not required_years:
        return 100.0
    
    # Simple calculation - this should be more sophisticated
    total_years = len(work_experience) * 2  # Rough estimate
    
    if total_years >= required_years:
        return 100.0
    else:
        return (total_years / required_years) * 100
