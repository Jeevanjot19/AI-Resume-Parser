"""
Integrated resume parser service with enhanced extraction.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
import re
from loguru import logger

from app.document_processors import DocumentProcessorFactory
from app.document_processors.file_validator import FileValidator
from app.ai import NERExtractor, TextClassifier, EmbeddingGenerator, LLMOrchestrator
from app.models import Resume, PersonInfo, WorkExperience, Education, Skill, AIAnalysis
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession


# Skill standardization mapping
SKILL_ALIASES = {
    # Programming languages
    "js": "JavaScript",
    "ts": "TypeScript", 
    "py": "Python",
    "cpp": "C++",
    "c#": "C Sharp",
    "golang": "Go",
    "node": "Node.js",
    "react.js": "React",
    "vue.js": "Vue",
    "next.js": "Next.js",
    
    # Cloud & DevOps
    "k8s": "Kubernetes",
    "aws": "Amazon Web Services",
    "gcp": "Google Cloud Platform",
    "azure": "Microsoft Azure",
    
    # AI/ML
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "dl": "Deep Learning",
    "cv": "Computer Vision",
    "nlp": "Natural Language Processing",
    
    # Databases
    "postgres": "PostgreSQL",
    "mongo": "MongoDB",
    "sql": "SQL",
    "nosql": "NoSQL",
}

# Job title keywords for detection
JOB_TITLE_KEYWORDS = [
    "engineer", "developer", "programmer", "architect", "lead", "senior", "junior",
    "manager", "director", "analyst", "scientist", "designer", "consultant",
    "specialist", "administrator", "coordinator", "executive", "officer", "head",
    "intern", "associate", "principal", "staff", "team lead", "tech lead",
    "full stack", "frontend", "backend", "devops", "data", "software", "web"
]

# Degree patterns
DEGREE_PATTERNS = [
    r'\b(Bachelor(?:\'s)?|B\.?S\.?|B\.?A\.?|B\.?Tech\.?|B\.?E\.?)\s+(?:of|in|degree)?\s*([^,\n\.]+)',
    r'\b(Master(?:\'s)?|M\.?S\.?|M\.?A\.?|M\.?Tech\.?|M\.?E\.?|MBA)\s+(?:of|in|degree)?\s*([^,\n\.]+)',
    r'\b(Ph\.?D\.?|Doctorate|Doctoral)\s+(?:of|in|degree)?\s*([^,\n\.]+)',
    r'\b(Associate(?:\'s)?|A\.?S\.?|A\.?A\.?)\s+(?:of|in|degree)?\s*([^,\n\.]+)',
]

# Soft skills keywords
SOFT_SKILLS = [
    "leadership", "communication", "teamwork", "problem solving", "critical thinking",
    "collaboration", "time management", "adaptability", "creativity", "innovation",
    "interpersonal", "presentation", "negotiation", "conflict resolution",
    "emotional intelligence", "decision making", "strategic thinking", "analytical",
    "attention to detail", "organization", "multitasking", "flexibility"
]


class ResumeParserService:
    """Integrated resume parsing service."""
    
    def __init__(self, use_tika: bool = False):  # Fixed: default to False
        self.processor_factory = DocumentProcessorFactory(use_tika=use_tika)
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
        personal_info = await self._extract_personal_info(text, entities)
        
        # Extract professional summary
        summary = await self._extract_professional_summary(text)
        
        # Extract work experience (ENHANCED)
        work_experience = await self._extract_work_experience_enhanced(text, entities)
        
        # Extract education (ENHANCED)
        education = await self._extract_education_enhanced(text, entities)
        
        # Standardize and categorize skills (ENHANCED)
        categorized_skills = await self._categorize_skills(text, skills)
        
        # Calculate total experience from work history
        total_experience_years = self._calculate_total_experience(work_experience)
        
        return {
            'personal_info': personal_info,
            'professional_summary': summary,
            'work_experience': work_experience,
            'education': education,
            'skills': categorized_skills,
            'total_experience_years': total_experience_years
        }
    
    async def _extract_personal_info(
        self,
        text: str,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract comprehensive personal information."""
        # Get basic contact info
        emails = entities.get('emails', [])
        phones = entities.get('phones', [])
        persons = entities.get('persons', [])
        locations = entities.get('locations', [])
        urls = entities.get('urls', [])
        
        # Extract LinkedIn
        linkedin = None
        for url in urls:
            if 'linkedin.com/in/' in url.lower():
                linkedin = url
                break
        
        # Extract GitHub
        github = None
        for url in urls:
            if 'github.com/' in url.lower():
                github = url
                break
        
        # Get location (prefer cities over countries)
        location = None
        if locations:
            # Filter out common countries, prefer cities
            cities = [loc for loc in locations if loc.lower() not in ['usa', 'united states', 'india', 'uk', 'canada']]
            location = cities[0] if cities else locations[0]
        
        return {
            'full_name': persons[0] if persons else None,
            'email': emails[0] if emails else None,
            'phone': phones[0] if phones else None,
            'location': location,
            'linkedin': linkedin,
            'github': github,
        }
    
    async def _extract_professional_summary(self, text: str) -> Optional[str]:
        """Extract professional summary/objective."""
        # Find summary section
        summary_section = self._find_section(
            text,
            ['summary', 'objective', 'profile', 'about', 'introduction']
        )
        
        if summary_section:
            # Extract first paragraph (usually the summary)
            lines = summary_section.split('\n')
            summary_lines = []
            for line in lines[:5]:  # Max 5 lines
                line = line.strip()
                if len(line) > 20:  # Meaningful content
                    summary_lines.append(line)
            
            return ' '.join(summary_lines) if summary_lines else None
        
        return None
    
    async def _extract_work_experience_enhanced(
        self,
        text: str,
        entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Enhanced work experience extraction."""
        # Find experience section
        exp_section = self._find_section(
            text,
            ['experience', 'work history', 'employment', 'professional experience', 'work experience']
        )
        
        if not exp_section:
            exp_section = text  # Use full text as fallback
        
        experiences = []
        organizations = entities.get('organizations', [])
        
        # Extract dates from experience section
        date_pattern = r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\s*(?:-|–|to|till)?\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current)?\b'
        dates = re.findall(date_pattern, exp_section, re.IGNORECASE)
        
        # Extract job titles
        job_titles = self._extract_job_titles(exp_section)
        
        # Extract achievements with metrics
        achievements_pattern = r'(increased|reduced|improved|managed|led|developed|built|created|designed|implemented|launched|delivered|achieved|grew|saved|optimized|streamlined)[^.!?\n]*((?:\d+%|\$\d+[KMB]?|\d+\s*(?:people|users|clients|projects|systems|applications|million|thousand)))'
        achievements = re.findall(achievements_pattern, exp_section, re.IGNORECASE)
        
        # Extract technologies per experience
        tech_skills = await self.ner_extractor.extract_skills(exp_section)
        
        # Build experience entries
        for i, org in enumerate(organizations[:7]):  # Limit to 7 companies
            exp_entry = {
                'company': org,
                'title': job_titles[i] if i < len(job_titles) else 'Position',
                'start_date': dates[i][0] if i < len(dates) else None,
                'end_date': dates[i][1] if i < len(dates) and dates[i][1] else None,
                'description': '',
                'achievements': [],
                'technologies': []
            }
            
            # Add achievements for this company (rough heuristic)
            if achievements:
                exp_entry['achievements'] = [
                    f"{verb} {metric}".strip() 
                    for verb, metric in achievements[i*2:(i+1)*2]
                ]
            
            # Add technologies
            exp_entry['technologies'] = tech_skills[:5] if i == 0 else []
            
            experiences.append(exp_entry)
        
        return experiences
    
    def _extract_job_titles(self, text: str) -> List[str]:
        """Extract job titles from text."""
        titles = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Check if line contains job title keywords
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in JOB_TITLE_KEYWORDS):
                # Remove dates and company names
                clean_line = re.sub(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}', '', line)
                clean_line = re.sub(r'\d{4}\s*-\s*\d{4}', '', clean_line)
                clean_line = clean_line.strip(' -–|')
                
                if 20 < len(clean_line) < 100:  # Reasonable title length
                    titles.append(clean_line)
        
        return titles[:7]  # Max 7 titles
    
    async def _extract_education_enhanced(
        self,
        text: str,
        entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Enhanced education extraction."""
        # Find education section
        edu_section = self._find_section(
            text,
            ['education', 'academic', 'qualification', 'educational background']
        )
        
        if not edu_section:
            edu_section = text  # Fallback to full text
        
        education_entries = []
        
        # Extract degrees
        degrees_found = []
        for pattern in DEGREE_PATTERNS:
            matches = re.findall(pattern, edu_section, re.IGNORECASE)
            for match in matches:
                degree_type = match[0]
                field = match[1].strip() if len(match) > 1 else ''
                degrees_found.append((degree_type, field))
        
        # Extract universities (ORG entities in education section)
        universities = []
        if self.ner_extractor.spacy_nlp:
            doc = self.ner_extractor.spacy_nlp(edu_section)
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    uni_name = ent.text
                    # Check if it's likely a university
                    if any(keyword in uni_name.lower() for keyword in ['university', 'college', 'institute', 'school', 'academy']):
                        universities.append(uni_name)
        
        # Extract GPAs
        gpa_pattern = r'(?:GPA|CGPA|Grade)[\s:]*(\d\.\d+)\s*(?:/\s*(\d\.\d+))?'
        gpas = re.findall(gpa_pattern, edu_section, re.IGNORECASE)
        
        # Extract graduation years
        year_pattern = r'\b(19\d{2}|20\d{2})\b'
        years = re.findall(year_pattern, edu_section)
        
        # Extract certifications
        cert_keywords = ['certified', 'certification', 'certificate', 'license', 'credential']
        certifications = []
        for line in edu_section.split('\n'):
            if any(keyword in line.lower() for keyword in cert_keywords):
                clean_cert = line.strip()
                if 10 < len(clean_cert) < 150:
                    certifications.append(clean_cert)
        
        # Build education entries
        max_entries = max(len(degrees_found), len(universities), 1)
        for i in range(min(max_entries, 5)):  # Max 5 education entries
            entry = {
                'degree': degrees_found[i][0] if i < len(degrees_found) else None,
                'field': degrees_found[i][1] if i < len(degrees_found) else None,
                'institution': universities[i] if i < len(universities) else None,
                'graduation_date': years[i] if i < len(years) else None,
                'gpa': f"{gpas[i][0]}/{gpas[i][1]}" if i < len(gpas) and gpas[i][1] else (gpas[i][0] if i < len(gpas) else None),
                'certifications': certifications if i == 0 else []
            }
            
            # Only add if we have at least degree or institution
            if entry['degree'] or entry['institution']:
                education_entries.append(entry)
        
        return education_entries
    
    async def _categorize_skills(
        self,
        text: str,
        skills: List[str]
    ) -> Dict[str, List[str]]:
        """Categorize and standardize skills."""
        # Standardize skills
        standardized = []
        for skill in skills:
            skill_lower = skill.lower()
            standardized_skill = SKILL_ALIASES.get(skill_lower, skill)
            standardized.append(standardized_skill)
        
        # Remove duplicates
        standardized = list(set(standardized))
        
        # Detect soft skills from text
        text_lower = text.lower()
        detected_soft_skills = []
        for soft_skill in SOFT_SKILLS:
            if soft_skill in text_lower:
                detected_soft_skills.append(soft_skill.title())
        
        # Categorize
        technical_keywords = {
            'programming': ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Go', 'Rust', 'TypeScript'],
            'frameworks': ['Django', 'Flask', 'FastAPI', 'React', 'Angular', 'Vue', 'Spring', 'Express', 'Next.js'],
            'databases': ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Oracle', 'SQL Server'],
            'cloud': ['AWS', 'Amazon Web Services', 'Azure', 'Microsoft Azure', 'Google Cloud', 'GCP', 'Docker', 'Kubernetes'],
            'tools': ['Git', 'Jenkins', 'CI/CD', 'Terraform', 'Ansible', 'Linux', 'Agile', 'Scrum']
        }
        
        categorized = {
            'technical': standardized,
            'soft': detected_soft_skills,
            'programming': [],
            'frameworks': [],
            'databases': [],
            'cloud': [],
            'tools': []
        }
        
        # Sub-categorize technical skills
        for skill in standardized:
            for category, keywords in technical_keywords.items():
                if skill in keywords or any(keyword.lower() in skill.lower() for keyword in keywords):
                    categorized[category].append(skill)
        
        return categorized
    
    def _calculate_total_experience(self, work_experience: List[Dict]) -> float:
        """Calculate total years of experience from work history."""
        total_years = 0.0
        
        for exp in work_experience:
            start = exp.get('start_date')
            end = exp.get('end_date')
            
            if start:
                # Parse year from date string
                start_year = self._extract_year(start)
                end_year = self._extract_year(end) if end else datetime.now().year
                
                if start_year and end_year:
                    years = max(0, end_year - start_year)
                    total_years += years
        
        # If no dates found, estimate based on number of jobs
        if total_years == 0 and len(work_experience) > 0:
            total_years = len(work_experience) * 2.5  # Assume 2.5 years per job
        
        return round(total_years, 1)
    
    def _extract_year(self, date_str: Optional[str]) -> Optional[int]:
        """Extract year from date string."""
        if not date_str:
            return None
        
        # Handle "Present" or "Current"
        if date_str.lower() in ['present', 'current']:
            return datetime.now().year
        
        # Extract 4-digit year
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', str(date_str))
        return int(year_match.group(1)) if year_match else None
    
    def _find_section(self, text: str, section_names: List[str]) -> Optional[str]:
        """Find a section in resume text by section headers."""
        text_lower = text.lower()
        lines = text.split('\n')
        
        # Find section start
        section_start_idx = None
        for i, line in enumerate(lines):
            line_clean = line.strip().lower()
            # Check if line is a section header
            if any(name in line_clean for name in section_names):
                # Make sure it's likely a header (short line, possibly with formatting)
                if len(line_clean) < 50 and (line_clean.endswith(':') or len(line.strip()) == len(line_clean)):
                    section_start_idx = i
                    break
        
        if section_start_idx is None:
            return None
        
        # Find section end (next section header or end of document)
        common_sections = [
            'experience', 'education', 'skills', 'summary', 'objective',
            'projects', 'certifications', 'awards', 'publications', 'references',
            'interests', 'languages', 'hobbies'
        ]
        
        section_end_idx = len(lines)
        for i in range(section_start_idx + 1, len(lines)):
            line_clean = lines[i].strip().lower()
            # Check if this is a new section header
            if len(line_clean) < 50:
                if any(section in line_clean for section in common_sections):
                    # Make sure it's not part of the current section
                    if line_clean.endswith(':') or (line_clean.isupper() and len(line_clean) > 3):
                        section_end_idx = i
                        break
        
        # Extract section text
        section_lines = lines[section_start_idx + 1:section_end_idx]
        return '\n'.join(section_lines).strip()

