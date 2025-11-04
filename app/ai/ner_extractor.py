"""
Named Entity Recognition (NER) extractor for resume parsing.
"""

import re
from typing import Dict, List, Any, Optional
import spacy
from transformers import pipeline
from loguru import logger

from app.core.config import settings


class NERExtractor:
    """Hybrid NER system using spaCy and Transformers."""
    
    def __init__(self):
        self.spacy_nlp: Optional[spacy.Language] = None
        self.transformer_ner: Optional[Any] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize NER models."""
        if self._initialized:
            return
        
        try:
            # Load spaCy model for fast NER
            logger.info("Loading spaCy model...")
            self.spacy_nlp = spacy.load("en_core_web_sm")
            
            # Load transformer model for complex NER
            logger.info("Loading transformer NER model...")
            self.transformer_ner = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                grouped_entities=True
            )
            
            self._initialized = True
            logger.info("NER models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NER models: {e}")
            raise
    
    async def extract_entities(self, text: str, use_transformer: bool = False) -> Dict[str, Any]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text
            use_transformer: Whether to use transformer model
            
        Returns:
            Dictionary containing extracted entities
        """
        if not self._initialized:
            await self.initialize()
        
        if use_transformer:
            return await self._extract_with_transformer(text)
        else:
            return await self._extract_with_spacy(text)
    
    async def _extract_with_spacy(self, text: str) -> Dict[str, Any]:
        """Extract entities using spaCy."""
        doc = self.spacy_nlp(text)
        
        entities = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "emails": [],
            "phones": [],
            "urls": [],
        }
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["persons"].append(ent.text)
            elif ent.label_ in ["ORG", "NORP"]:
                entities["organizations"].append(ent.text)
            elif ent.label_ in ["GPE", "LOC"]:
                entities["locations"].append(ent.text)
            elif ent.label_ == "DATE":
                entities["dates"].append(ent.text)
        
        # Extract contact information using regex
        entities["emails"].extend(self._extract_emails(text))
        entities["phones"].extend(self._extract_phones(text))
        entities["urls"].extend(self._extract_urls(text))
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    async def _extract_with_transformer(self, text: str) -> Dict[str, Any]:
        """Extract entities using transformer model."""
        try:
            results = self.transformer_ner(text[:512])  # Limit to 512 tokens
            
            entities = {
                "persons": [],
                "organizations": [],
                "locations": [],
                "miscellaneous": [],
                "emails": [],
                "phones": [],
                "urls": [],
            }
            
            for entity in results:
                entity_type = entity['entity_group']
                entity_text = entity['word']
                
                if entity_type == "PER":
                    entities["persons"].append(entity_text)
                elif entity_type == "ORG":
                    entities["organizations"].append(entity_text)
                elif entity_type == "LOC":
                    entities["locations"].append(entity_text)
                elif entity_type == "MISC":
                    entities["miscellaneous"].append(entity_text)
            
            # Extract contact information
            entities["emails"].extend(self._extract_emails(text))
            entities["phones"].extend(self._extract_phones(text))
            entities["urls"].extend(self._extract_urls(text))
            
            # Remove duplicates
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            return entities
        except Exception as e:
            logger.error(f"Transformer NER error: {e}")
            # Fallback to spaCy
            return await self._extract_with_spacy(text)
    
    @staticmethod
    def _extract_emails(text: str) -> List[str]:
        """Extract email addresses."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    @staticmethod
    def _extract_phones(text: str) -> List[str]:
        """Extract phone numbers."""
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        return phones
    
    @staticmethod
    def _extract_urls(text: str) -> List[str]:
        """Extract URLs."""
        url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
        return re.findall(url_pattern, text)
    
    async def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text."""
        if not self._initialized:
            await self.initialize()
        
        # Predefined skill keywords (this should be expanded or use a skill taxonomy)
        skill_keywords = {
            # Programming languages
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "swift", "kotlin",
            "go", "rust", "scala", "r", "matlab", "perl", "shell", "bash",
            
            # Frameworks & Libraries
            "django", "flask", "fastapi", "react", "angular", "vue", "node.js", "express",
            "spring", "hibernate", "tensorflow", "pytorch", "keras", "scikit-learn",
            "pandas", "numpy", "matplotlib", "seaborn",
            
            # Databases
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
            "dynamodb", "oracle", "sql server", "sqlite",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "gitlab ci",
            "terraform", "ansible", "ci/cd",
            
            # Other tech skills
            "git", "linux", "agile", "scrum", "rest api", "graphql", "microservices",
            "machine learning", "deep learning", "nlp", "computer vision"
        }
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))
    
    async def extract_dates(self, text: str) -> List[Dict[str, str]]:
        """Extract and parse dates from text."""
        if not self._initialized:
            await self.initialize()
        
        doc = self.spacy_nlp(text)
        dates = []
        
        for ent in doc.ents:
            if ent.label_ == "DATE":
                dates.append({
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
        
        return dates
