"""
Elasticsearch client and utilities.
"""

from typing import Dict, Any, List, Optional
from elasticsearch import AsyncElasticsearch
from loguru import logger

from app.core.config import settings
from app.search.mappings import (
    RESUME_INDEX,
    JOB_INDEX,
    RESUME_INDEX_MAPPING,
    JOB_INDEX_MAPPING
)


class SearchClient:
    """Elasticsearch client wrapper."""
    
    def __init__(self):
        self.client: Optional[AsyncElasticsearch] = None
        
    async def connect(self):
        """Connect to Elasticsearch."""
        try:
            self.client = AsyncElasticsearch(
                [str(settings.get_elasticsearch_url())],
                retry_on_timeout=True,
                max_retries=3
            )
            
            # Check connection
            if await self.client.ping():
                logger.info("Successfully connected to Elasticsearch")
                await self.create_indices()
            else:
                logger.error("Failed to connect to Elasticsearch")
        except Exception as e:
            logger.error(f"Elasticsearch connection error: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Elasticsearch."""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Elasticsearch")
    
    async def create_indices(self):
        """Create indices if they don't exist."""
        try:
            # Create resume index
            if not await self.client.indices.exists(index=RESUME_INDEX):
                await self.client.indices.create(
                    index=RESUME_INDEX,
                    body=RESUME_INDEX_MAPPING
                )
                logger.info(f"Created index: {RESUME_INDEX}")
            
            # Create job index
            if not await self.client.indices.exists(index=JOB_INDEX):
                await self.client.indices.create(
                    index=JOB_INDEX,
                    body=JOB_INDEX_MAPPING
                )
                logger.info(f"Created index: {JOB_INDEX}")
        except Exception as e:
            logger.error(f"Error creating indices: {e}")
    
    async def index_resume(self, resume_id: str, document: Dict[str, Any]):
        """Index a resume document."""
        if self.client is None:
            logger.warning(f"Elasticsearch not available, skipping indexing for resume {resume_id}")
            return
            
        try:
            await self.client.index(
                index=RESUME_INDEX,
                id=resume_id,
                document=document
            )
            logger.info(f"Indexed resume: {resume_id}")
        except Exception as e:
            logger.error(f"Error indexing resume {resume_id}: {e}")
            # Don't raise - make ES indexing optional
            logger.warning(f"Elasticsearch indexing failed for {resume_id}, continuing without ES")
    
    async def search_resumes(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        size: int = 10,
        from_: int = 0
    ) -> Dict[str, Any]:
        """Search resumes with optional filters."""
        try:
            body: Dict[str, Any] = {
                "size": size,
                "from": from_
            }
            
            # Build query
            if query or filters:
                must_clauses = []
                
                if query:
                    must_clauses.append({
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "full_name^3",
                                "current_job_title^2",
                                "skills^2",
                                "raw_text"
                            ],
                            "type": "best_fields",
                            "operator": "or"
                        }
                    })
                
                if filters:
                    for key, value in filters.items():
                        must_clauses.append({"term": {key: value}})
                
                body["query"] = {"bool": {"must": must_clauses}}
            else:
                body["query"] = {"match_all": {}}
            
            results = await self.client.search(index=RESUME_INDEX, body=body)
            return results
        except Exception as e:
            logger.error(f"Error searching resumes: {e}")
            raise
    
    async def semantic_search(
        self,
        embedding: List[float],
        index: str = RESUME_INDEX,
        size: int = 10
    ) -> Dict[str, Any]:
        """Perform semantic search using vector embeddings."""
        try:
            body = {
                "size": size,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'text_embedding') + 1.0",
                            "params": {"query_vector": embedding}
                        }
                    }
                }
            }
            
            results = await self.client.search(index=index, body=body)
            return results
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise
    
    async def delete_resume(self, resume_id: str):
        """Delete a resume document."""
        try:
            await self.client.delete(index=RESUME_INDEX, id=resume_id)
            logger.info(f"Deleted resume: {resume_id}")
        except Exception as e:
            logger.error(f"Error deleting resume {resume_id}: {e}")
            raise


# Global search client instance
search_client = SearchClient()


async def get_search_client() -> SearchClient:
    """Get search client instance."""
    return search_client
