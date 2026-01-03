"""
Semantic Cache Module

Provides semantic similarity-based caching for NL2SQL queries using sentence transformers.
Matches questions based on meaning rather than exact text, reducing redundant AI model calls.
"""

import hashlib
import json
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticCache:
    """
    Semantic caching engine using sentence embeddings for similarity matching.
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        similarity_threshold: float = 0.85,
        max_cache_size: int = 1000
    ):
        """
        Initialize semantic cache with embedding model.
        
        Args:
            model_name: HuggingFace model for embeddings
            similarity_threshold: Minimum similarity score (0-1) for cache hit
            max_cache_size: Maximum cached queries per schema
        """
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.max_cache_size = max_cache_size
        self._model = None  # Lazy loading
        
    @property
    def model(self):
        """Lazy load the sentence transformer model."""
        if self._model is None:
            print(f"Loading semantic cache model: {self.model_name}...")
            try:
                self._model = SentenceTransformer(self.model_name)
                print("Model loaded successfully!")
            except Exception as e:
                print(f"WARNING: Failed to load semantic cache model: {e}")
                print("Semantic cache will be DISABLED for this session.")
                self._model = False # Mark as failed to avoid retrying
        return self._model
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate semantic embedding for text.
        
        Args:
            text: Input text (question)
            
        Returns:
            Embedding vector as list of floats
        """
        if not self.model: # Check if model loaded successfully
             # Return dummy zero vector if model failed
             # Size 384 is typical for all-MiniLM-L6-v2
             return [0.0] * 384
             
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 384
    
    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1, where 1 is identical)
        """
        emb1 = np.array(embedding1).reshape(1, -1)
        emb2 = np.array(embedding2).reshape(1, -1)
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def generate_schema_hash(
        self,
        tables: List[Any],
        relationships: List[Any],
        dialect: str
    ) -> str:
        """
        Generate unique hash for schema context.
        
        Different schemas get different cache spaces to ensure accuracy.
        
        Args:
            tables: List of TableDef objects
            relationships: List of RelationshipDef objects
            dialect: Database dialect (MySQL, PostgreSQL, etc.)
            
        Returns:
            SHA-256 hash of schema structure
        """
        # Create deterministic representation
        schema_dict = {
            "tables": sorted([{
                "name": t.name,
                "columns": sorted([{
                    "name": c.name,
                    "type": c.type
                } for c in t.columns], key=lambda x: x["name"])
            } for t in tables], key=lambda x: x["name"]),
            "relationships": sorted([{
                "from": f"{r.from_table}.{r.from_column}",
                "to": f"{r.to_table}.{r.to_column}"
            } for r in relationships], key=lambda x: (x["from"], x["to"])),
            "dialect": dialect
        }
        
        # Generate hash
        schema_json = json.dumps(schema_dict, sort_keys=True)
        return hashlib.sha256(schema_json.encode()).hexdigest()
    
    def find_similar_query(
        self,
        question: str,
        question_embedding: List[float],
        schema_hash: str,
        cached_queries: List[Dict[str, Any]]
    ) -> Optional[Tuple[Dict[str, Any], float]]:
        """
        Find most similar cached query above threshold.
        
        Args:
            question: New question text
            question_embedding: Embedding of new question
            schema_hash: Hash of current schema
            cached_queries: List of cached query dicts with embeddings
            
        Returns:
            Tuple of (best_match, similarity_score) or None if no match
        """
        if not cached_queries:
            return (None, 0.0)
            
        # Check for zero vector (model failed)
        if not any(question_embedding):
            print("DEBUG: Zero vector detected (Semantic Cache Disabled)")
            return (None, 0.0)
        
        best_match = None
        best_similarity = 0.0
        
        for i, cached in enumerate(cached_queries):
            is_first = (i == 0)
            if is_first:
                print(f"DEBUG: Checking first candidate ID={cached.get('id')}")
            
            # Skip if different schema
            if cached.get('schema_hash') != schema_hash:
                if is_first: print(f"DEBUG: Schema mismatch! {cached.get('schema_hash')} != {schema_hash}")
                continue
            
            # Calculate similarity
            cached_embedding = cached.get('question_embedding')
            
            # AUTO-FIX: If embedding is a string (common in SQLite), parse it
            if isinstance(cached_embedding, str):
                try:
                    cached_embedding = json.loads(cached_embedding)
                    cached['question_embedding'] = cached_embedding 
                except json.JSONDecodeError:
                    if is_first: print("DEBUG: JSON decode error")
                    continue

            if not cached_embedding:
                if is_first: print("DEBUG: No embedding found")
                continue
                
            similarity = self.compute_similarity(
                question_embedding,
                cached_embedding
            )
            
            if is_first:
                print(f"DEBUG: Calculated Similarity: {similarity}")

            # Track best match
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = cached
        
        # Return tuple with best match (or None) and score
        if best_similarity >= self.similarity_threshold:
            return (best_match, best_similarity)
        
        return (None, best_similarity)
    
    def should_cache(self, question: str) -> bool:
        """
        Determine if question should be cached.
        
        Args:
            question: Question text
            
        Returns:
            True if should cache, False otherwise
        """
        # Skip very short questions
        if len(question.strip()) < 5:
            return False
        
        # Skip questions with only special characters
        if not any(c.isalnum() for c in question):
            return False
        
        return True


# Global cache instance (singleton)
_semantic_cache_instance = None


def get_semantic_cache() -> SemanticCache:
    """Get or create global semantic cache instance."""
    global _semantic_cache_instance
    if _semantic_cache_instance is None:
        _semantic_cache_instance = SemanticCache()
    return _semantic_cache_instance
