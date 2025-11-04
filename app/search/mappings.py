"""
Elasticsearch configuration and mappings.
"""

from typing import Dict, Any


# Resume index mapping
RESUME_INDEX_MAPPING: Dict[str, Any] = {
    "settings": {
        "number_of_shards": 2,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "custom_text_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding", "stop", "snowball"]
                },
                "skill_analyzer": {
                    "type": "custom",
                    "tokenizer": "keyword",
                    "filter": ["lowercase"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "resume_id": {"type": "keyword"},
            "file_name": {"type": "text"},
            "processing_status": {"type": "keyword"},
            "uploaded_at": {"type": "date"},
            "processed_at": {"type": "date"},
            
            # Personal info
            "full_name": {
                "type": "text",
                "analyzer": "custom_text_analyzer",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "email": {"type": "keyword"},
            "phone": {"type": "keyword"},
            "location": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}}
            },
            
            # Experience
            "total_experience_years": {"type": "integer"},
            "current_job_title": {
                "type": "text",
                "analyzer": "custom_text_analyzer",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "current_company": {
                "type": "text",
                "analyzer": "custom_text_analyzer",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "work_experiences": {
                "type": "nested",
                "properties": {
                    "job_title": {"type": "text", "analyzer": "custom_text_analyzer"},
                    "company_name": {"type": "text", "analyzer": "custom_text_analyzer"},
                    "description": {"type": "text", "analyzer": "custom_text_analyzer"},
                    "technologies": {"type": "keyword"},
                    "start_date": {"type": "date"},
                    "end_date": {"type": "date"},
                    "is_current": {"type": "boolean"}
                }
            },
            
            # Education
            "highest_degree": {"type": "keyword"},
            "field_of_study": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "institutions": {"type": "keyword"},
            "education": {
                "type": "nested",
                "properties": {
                    "degree": {"type": "keyword"},
                    "field_of_study": {"type": "text"},
                    "institution": {"type": "text"},
                    "graduation_date": {"type": "date"},
                    "gpa": {"type": "float"}
                }
            },
            
            # Skills
            "skills": {
                "type": "keyword",
                "fields": {
                    "text": {
                        "type": "text",
                        "analyzer": "skill_analyzer"
                    }
                }
            },
            "skill_categories": {"type": "keyword"},
            "primary_skills": {"type": "keyword"},
            
            # AI Analysis
            "quality_score": {"type": "integer"},
            "completeness_score": {"type": "integer"},
            "career_level": {"type": "keyword"},
            "industry_classifications": {"type": "object"},
            "salary_estimate": {"type": "object"},
            
            # Full text
            "raw_text": {
                "type": "text",
                "analyzer": "custom_text_analyzer"
            },
            
            # Vector embeddings for semantic search
            "text_embedding": {
                "type": "dense_vector",
                "dims": 768,
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}


# Job index mapping
JOB_INDEX_MAPPING: Dict[str, Any] = {
    "settings": {
        "number_of_shards": 2,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "custom_text_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding", "stop", "snowball"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "job_id": {"type": "keyword"},
            "title": {
                "type": "text",
                "analyzer": "custom_text_analyzer",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "company": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "location": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "description": {
                "type": "text",
                "analyzer": "custom_text_analyzer"
            },
            "requirements": {
                "type": "nested",
                "properties": {
                    "required": {"type": "keyword"},
                    "preferred": {"type": "keyword"}
                }
            },
            "skills_required": {"type": "keyword"},
            "skills_preferred": {"type": "keyword"},
            "experience_min": {"type": "integer"},
            "experience_max": {"type": "integer"},
            "salary_min": {"type": "integer"},
            "salary_max": {"type": "integer"},
            "industry": {"type": "keyword"},
            "created_at": {"type": "date"},
            
            # Vector embedding
            "text_embedding": {
                "type": "dense_vector",
                "dims": 768,
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}


# Index names
RESUME_INDEX = "resumes"
JOB_INDEX = "jobs"
