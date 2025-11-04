"""
Embedding generator for semantic similarity and search.
"""

from typing import List, Optional
import torch
from sentence_transformers import SentenceTransformer
from loguru import logger

from app.core.config import settings


class EmbeddingGenerator:
    """Generate embeddings for semantic search and similarity."""
    
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize embedding model."""
        if self._initialized:
            return
        
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.model = self.model.to('cuda')
                logger.info("Using GPU for embeddings")
            
            self._initialized = True
            logger.info("Embedding model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_tensor=True)
            
            # Convert to list
            if torch.cuda.is_available():
                embedding = embedding.cpu()
            
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    async def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_tensor=True,
                show_progress_bar=len(texts) > 100
            )
            
            if torch.cuda.is_available():
                embeddings = embeddings.cpu()
            
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return []
    
    async def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0 to 1)
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            embeddings = self.model.encode([text1, text2], convert_to_tensor=True)
            
            # Calculate cosine similarity
            similarity = torch.nn.functional.cosine_similarity(
                embeddings[0].unsqueeze(0),
                embeddings[1].unsqueeze(0)
            )
            
            return float(similarity.item())
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    async def find_most_similar(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5
    ) -> List[tuple]:
        """
        Find most similar texts from candidates.
        
        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Generate embeddings
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            candidate_embeddings = self.model.encode(candidates, convert_to_tensor=True)
            
            # Calculate similarities
            similarities = torch.nn.functional.cosine_similarity(
                query_embedding.unsqueeze(0),
                candidate_embeddings
            )
            
            # Get top k
            top_results = torch.topk(similarities, k=min(top_k, len(candidates)))
            
            results = []
            for idx, score in zip(top_results.indices, top_results.values):
                results.append((int(idx), float(score)))
            
            return results
        except Exception as e:
            logger.error(f"Error finding similar texts: {e}")
            return []
