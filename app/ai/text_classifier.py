"""
Text classifier for industry and job role classification.
"""

from typing import Dict, List, Optional, Any
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from loguru import logger

from app.core.config import settings


class TextClassifier:
    """Text classification for resumes and job descriptions."""
    
    def __init__(self):
        self.industry_classifier: Optional[Any] = None
        self.job_role_classifier: Optional[Any] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize classification models."""
        if self._initialized:
            return
        
        try:
            logger.info("Loading text classification models...")
            
            # Use zero-shot classification for flexibility
            self.industry_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            
            self.job_role_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            
            self._initialized = True
            logger.info("Text classifiers initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing classifiers: {e}")
            raise
    
    async def classify_industry(self, text: str) -> Dict[str, float]:
        """
        Classify text into industry categories.
        
        Args:
            text: Input text (resume or job description)
            
        Returns:
            Dictionary of industry labels with confidence scores
        """
        if not self._initialized:
            await self.initialize()
        
        industries = [
            "Technology & Software",
            "Finance & Banking",
            "Healthcare & Medical",
            "Retail & E-commerce",
            "Manufacturing",
            "Education",
            "Consulting",
            "Marketing & Advertising",
            "Real Estate",
            "Entertainment & Media",
            "Energy & Utilities",
            "Transportation & Logistics",
            "Telecommunications",
            "Legal Services",
            "Government & Public Sector"
        ]
        
        try:
            # Limit text length for efficiency
            text_sample = text[:500]
            
            result = self.industry_classifier(
                text_sample,
                candidate_labels=industries,
                multi_label=True
            )
            
            # Create dictionary of results
            classifications = {}
            for label, score in zip(result['labels'], result['scores']):
                classifications[label] = float(score)
            
            return classifications
        except Exception as e:
            logger.error(f"Industry classification error: {e}")
            return {}
    
    async def classify_job_role(self, text: str) -> Dict[str, float]:
        """
        Classify text into job role categories.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of job role labels with confidence scores
        """
        if not self._initialized:
            await self.initialize()
        
        job_roles = [
            "Software Engineer",
            "Data Scientist",
            "Product Manager",
            "Business Analyst",
            "Project Manager",
            "DevOps Engineer",
            "Frontend Developer",
            "Backend Developer",
            "Full Stack Developer",
            "UX/UI Designer",
            "Marketing Manager",
            "Sales Executive",
            "Human Resources",
            "Financial Analyst",
            "Customer Support"
        ]
        
        try:
            text_sample = text[:500]
            
            result = self.job_role_classifier(
                text_sample,
                candidate_labels=job_roles,
                multi_label=True
            )
            
            classifications = {}
            for label, score in zip(result['labels'], result['scores']):
                classifications[label] = float(score)
            
            return classifications
        except Exception as e:
            logger.error(f"Job role classification error: {e}")
            return {}
    
    async def determine_career_level(self, text: str, years_of_experience: Optional[int] = None) -> str:
        """
        Determine career level from resume text.
        
        Args:
            text: Resume text
            years_of_experience: Calculated years of experience
            
        Returns:
            Career level (entry, mid, senior, executive)
        """
        if not self._initialized:
            await self.initialize()
        
        # Keywords for different levels
        senior_keywords = ["senior", "lead", "principal", "architect", "director", "head of", "vp", "chief"]
        mid_keywords = ["specialist", "engineer", "analyst", "consultant", "coordinator"]
        entry_keywords = ["junior", "intern", "trainee", "graduate", "assistant"]
        executive_keywords = ["ceo", "cto", "cfo", "coo", "president", "executive", "c-level"]
        
        text_lower = text.lower()
        
        # Check executive level first
        if any(keyword in text_lower for keyword in executive_keywords):
            return "executive"
        
        # Use years of experience if available
        if years_of_experience is not None:
            if years_of_experience < 2:
                return "entry"
            elif years_of_experience < 5:
                return "mid"
            elif years_of_experience < 10:
                return "senior"
            else:
                return "executive"
        
        # Fall back to keyword matching
        if any(keyword in text_lower for keyword in senior_keywords):
            return "senior"
        elif any(keyword in text_lower for keyword in mid_keywords):
            return "mid"
        elif any(keyword in text_lower for keyword in entry_keywords):
            return "entry"
        
        # Default to mid if unclear
        return "mid"
    
    async def classify_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text (useful for cover letters, summaries).
        
        Args:
            text: Input text
            
        Returns:
            Sentiment analysis results
        """
        try:
            sentiment_analyzer = pipeline("sentiment-analysis")
            result = sentiment_analyzer(text[:512])[0]
            
            return {
                "label": result["label"],
                "score": float(result["score"])
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"label": "NEUTRAL", "score": 0.5}
