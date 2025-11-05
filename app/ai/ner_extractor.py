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
            self.spacy_nlp = spacy.load("en_core_web_lg")  # Use the large model we have installed
            
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
        """Extract email addresses with improved patterns."""
        # Multiple patterns for robustness
        patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Standard email
            r'[Ee]mail\s*[:=]\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # Email: label
            r'[Ee]-?mail\s*[:=]\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # E-mail: label
        ]
        
        emails = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if isinstance(matches[0] if matches else None, tuple):
                emails.extend([m for m in matches if m])
            else:
                emails.extend(matches)
        
        # Clean and deduplicate
        cleaned = []
        for email in emails:
            email = email.strip().lower()
            # Filter out common false positives
            if email and '@' in email and '.' in email.split('@')[-1]:
                if not any(skip in email for skip in ['example.com', 'test.com', 'email.com']):
                    cleaned.append(email)
        
        return list(set(cleaned))
    
    @staticmethod
    def _extract_phones(text: str) -> List[str]:
        """Extract phone numbers with comprehensive international patterns."""
        phone_patterns = [
            # International formats
            r'\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # +1-234-567-8900
            # US/Canada formats
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890 or 123-456-7890
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # 123-456-7890
            # India formats
            r'\+?91[-.\s]?\d{10}',  # +91-9876543210
            r'\d{5}[-.\s]?\d{5}',  # 98765-43210
            # UK formats
            r'\+?44[-.\s]?\d{10}',  # +44-1234567890
            # Generic 10-digit
            r'\b\d{10}\b',  # 1234567890
            # With labels
            r'[Pp]hone\s*[:=]\s*([\d\s\-\+\(\)]+)',
            r'[Mm]obile\s*[:=]\s*([\d\s\-\+\(\)]+)',
            r'[Cc]ell\s*[:=]\s*([\d\s\-\+\(\)]+)',
            r'[Tt]el\s*[:=]\s*([\d\s\-\+\(\)]+)',
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        # Clean and validate phone numbers
        cleaned = []
        for phone in phones:
            # Remove whitespace and special chars for validation
            digits_only = re.sub(r'[^\d]', '', phone)
            # Valid phone numbers have 7-15 digits
            if 7 <= len(digits_only) <= 15:
                # Keep original formatting
                cleaned.append(phone.strip())
        
        return list(set(cleaned))
    
    @staticmethod
    def _extract_urls(text: str) -> List[str]:
        """Extract URLs including social profiles."""
        patterns = [
            # Full HTTP/HTTPS URLs
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
            # LinkedIn profiles (with and without http)
            r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+/?',
            # GitHub profiles
            r'(?:https?://)?(?:www\.)?github\.com/[\w\-]+/?',
            # Twitter
            r'(?:https?://)?(?:www\.)?twitter\.com/[\w\-]+/?',
            # Portfolio sites (www.domain.com)
            r'www\.[\w\-]+\.[a-z]{2,}(?:/[\w\-]*)*',
        ]
        
        urls = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            urls.extend(matches)
        
        # Clean and deduplicate
        cleaned = []
        for url in urls:
            url = url.strip().rstrip('/')
            # Ensure LinkedIn and GitHub URLs have https://
            if 'linkedin.com' in url and not url.startswith('http'):
                url = 'https://' + url
            elif 'github.com' in url and not url.startswith('http'):
                url = 'https://' + url
            elif 'twitter.com' in url and not url.startswith('http'):
                url = 'https://' + url
            
            cleaned.append(url)
        
        return list(set(cleaned))
    
    async def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text with comprehensive keyword list."""
        if not self._initialized:
            await self.initialize()
        
        # Comprehensive skill keywords - EXPANDED
        skill_keywords = {
            # Programming languages
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "swift", "kotlin",
            "go", "rust", "scala", "r", "matlab", "perl", "shell", "bash", "powershell", "objective-c",
            "dart", "lua", "haskell", "elixir", "clojure", "groovy", "vb.net", "cobol", "fortran",
            "assembly", "sql", "pl/sql", "t-sql", "vba", "scratch", "solidity",
            
            # Web Development
            "html", "css", "sass", "scss", "less", "bootstrap", "tailwind", "material-ui", "mui",
            "webpack", "vite", "parcel", "rollup", "babel", "jquery", "ajax", "xml", "json",
            
            # Frontend Frameworks & Libraries
            "react", "react.js", "angular", "vue", "vue.js", "svelte", "next.js", "nuxt.js", "gatsby",
            "ember", "backbone", "knockout", "polymer", "web components", "pwa", "redux", "mobx",
            "recoil", "zustand", "react native", "ionic", "flutter", "xamarin",
            
            # Backend Frameworks
            "django", "flask", "fastapi", "express", "express.js", "node.js", "spring", "spring boot",
            "hibernate", "asp.net", ".net core", "laravel", "symfony", "rails", "ruby on rails",
            "sinatra", "gin", "echo", "fiber", "nestjs", "koa", "hapi", "meteor",
            
            # Data Science & ML
            "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "scipy", "matplotlib",
            "seaborn", "plotly", "bokeh", "statsmodels", "xgboost", "lightgbm", "catboost",
            "opencv", "nltk", "spacy", "gensim", "hugging face", "transformers", "bert", "gpt",
            "machine learning", "deep learning", "nlp", "computer vision", "neural networks",
            "cnn", "rnn", "lstm", "gan", "reinforcement learning", "supervised learning",
            "unsupervised learning", "classification", "regression", "clustering", "dimensionality reduction",
            
            # Databases - SQL
            "postgresql", "mysql", "mariadb", "oracle", "sql server", "mssql", "sqlite", "db2",
            "sybase", "teradata", "snowflake", "redshift", "bigquery",
            
            # Databases - NoSQL
            "mongodb", "redis", "cassandra", "couchdb", "dynamodb", "neo4j", "orientdb",
            "arangodb", "rethinkdb", "firebase", "firestore", "hbase", "couchbase",
            
            # Search & Analytics
            "elasticsearch", "solr", "sphinx", "algolia", "opensearch", "kibana", "grafana",
            "tableau", "power bi", "looker", "metabase", "superset",
            
            # Cloud Platforms
            "aws", "amazon web services", "ec2", "s3", "lambda", "rds", "dynamodb", "cloudfront",
            "azure", "microsoft azure", "azure devops", "gcp", "google cloud", "google cloud platform",
            "firebase", "heroku", "digitalocean", "linode", "vultr", "ibm cloud", "oracle cloud",
            
            # Cloud Services
            "cloudformation", "terraform", "pulumi", "serverless", "api gateway", "cloud functions",
            "cloud run", "app engine", "elastic beanstalk", "ecs", "eks", "aks", "gke",
            
            # DevOps & CI/CD
            "docker", "kubernetes", "k8s", "jenkins", "gitlab ci", "github actions", "circleci",
            "travis ci", "bamboo", "teamcity", "argocd", "flux", "spinnaker", "helm", "kustomize",
            "vagrant", "packer", "consul", "vault", "prometheus", "datadog", "new relic",
            "splunk", "nagios", "zabbix", "elk stack", "fluentd", "logstash",
            
            # Infrastructure as Code
            "terraform", "ansible", "puppet", "chef", "saltstack", "cloudformation", "arm templates",
            
            # Version Control
            "git", "github", "gitlab", "bitbucket", "svn", "mercurial", "perforce", "cvs",
            "git flow", "github flow", "trunk based development",
            
            # Testing
            "junit", "pytest", "unittest", "nose", "jest", "mocha", "chai", "jasmine", "karma",
            "selenium", "cypress", "playwright", "puppeteer", "testcafe", "cucumber", "behave",
            "rspec", "minitest", "phpunit", "nunit", "xunit", "postman", "insomnia", "jmeter",
            "locust", "k6", "test driven development", "tdd", "bdd", "integration testing",
            "unit testing", "e2e testing", "load testing", "performance testing",
            
            # Architecture & Patterns
            "microservices", "monolith", "soa", "event driven", "cqrs", "event sourcing",
            "rest api", "restful", "graphql", "grpc", "soap", "websocket", "sse", "mqtt",
            "api design", "system design", "design patterns", "mvc", "mvvm", "clean architecture",
            "hexagonal architecture", "domain driven design", "ddd", "solid principles",
            
            # Message Queues & Streaming
            "kafka", "rabbitmq", "activemq", "zeromq", "nats", "pulsar", "kinesis", "pub/sub",
            "redis streams", "sqs", "sns", "azure service bus", "event hub",
            
            # Monitoring & Logging
            "prometheus", "grafana", "datadog", "new relic", "splunk", "elk", "elasticsearch",
            "logstash", "kibana", "fluentd", "sentry", "rollbar", "bugsnag", "cloudwatch",
            "stackdriver", "azure monitor", "application insights",
            
            # Security
            "oauth", "jwt", "saml", "openid", "ssl", "tls", "https", "encryption", "hashing",
            "penetration testing", "vulnerability assessment", "owasp", "security scanning",
            "sonarqube", "snyk", "veracode", "checkmarx", "iam", "rbac", "authentication",
            "authorization", "firewall", "waf", "vpn", "zero trust",
            
            # Mobile Development
            "android", "ios", "react native", "flutter", "xamarin", "ionic", "cordova",
            "swift", "kotlin", "objective-c", "java android", "swiftui", "jetpack compose",
            
            # Game Development
            "unity", "unreal engine", "godot", "pygame", "phaser", "three.js", "webgl", "opengl",
            "directx", "vulkan", "c# unity", "blueprints",
            
            # Big Data
            "hadoop", "spark", "hive", "pig", "hdfs", "mapreduce", "yarn", "flink", "storm",
            "presto", "impala", "databricks", "airflow", "luigi", "prefect", "dagster",
            "data pipeline", "etl", "elt", "data warehouse", "data lake", "lakehouse",
            
            # Blockchain
            "blockchain", "ethereum", "solidity", "smart contracts", "web3", "defi", "nft",
            "hyperledger", "bitcoin", "cryptocurrency", "consensus algorithms",
            
            # Operating Systems
            "linux", "unix", "ubuntu", "centos", "rhel", "debian", "fedora", "arch",
            "windows server", "macos", "freebsd", "solaris",
            
            # Methodologies
            "agile", "scrum", "kanban", "lean", "waterfall", "extreme programming", "xp",
            "safe", "devops", "devsecops", "gitops", "sre", "site reliability engineering",
            "incident management", "on-call", "postmortem", "retrospective", "sprint planning",
            
            # Other Technologies
            "redis", "memcached", "nginx", "apache", "tomcat", "iis", "load balancing",
            "cdn", "cloudflare", "akamai", "fastly", "caching", "session management",
            "webscraping", "beautifulsoup", "scrapy", "regex", "cron", "batch processing",
            "real-time processing", "streaming", "async", "multi-threading", "concurrency",
            "parallel processing", "distributed systems", "high availability", "fault tolerance",
            "disaster recovery", "backup", "replication", "sharding", "partitioning",
            
            # Business & Productivity Tools
            "jira", "confluence", "slack", "microsoft teams", "notion", "asana", "trello",
            "monday.com", "basecamp", "office 365", "google workspace", "sharepoint",
            "salesforce", "hubspot", "zendesk", "servicenow",
            
            # Soft Skills (commonly mentioned)
            "leadership", "communication", "problem solving", "teamwork", "collaboration",
            "project management", "time management", "critical thinking", "analytical thinking"
        }
        
        text_lower = text.lower()
        found_skills = []
        
        # Check each skill keyword
        for skill in skill_keywords:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                # Capitalize properly
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
