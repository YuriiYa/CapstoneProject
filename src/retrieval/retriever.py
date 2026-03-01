"""
Retrieval system with hybrid search capabilities.
Combines vector similarity search with keyword-based search for better results.
"""

from typing import List, Dict, Optional
import numpy as np
from src.config.constants import (
    TOP_K,
    SIMILARITY_THRESHOLD
)


class Retriever:
    """
    Retriever class that implements hybrid search combining vector and keyword search.
    """
    
    def __init__(self, vector_store, embeddings_generator):
        """
        Initialize retriever with vector store and embeddings generator.
        
        Args:
            vector_store: ChromaVectorStore instance
            embeddings_generator: OllamaEmbeddings instance
        """
        self.vector_store = vector_store
        self.embeddings = embeddings_generator
    
    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K,
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        use_hybrid: bool = False
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User's question
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity score
            use_hybrid: Whether to use hybrid search (vector + keyword)
        
        Returns:
            List of retrieved documents with metadata
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Perform vector search
        results = self.vector_store.similarity_search_with_score(
            query_embedding=query_embedding,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        
        # If hybrid search requested, combine with keyword search
        if use_hybrid:
            results = self._hybrid_search(query, results, top_k)
        
        return results
    
    def _hybrid_search(
        self,
        query: str,
        vector_results: List[Dict],
        top_k: int
    ) -> List[Dict]:
        """
        Combine vector search with keyword search (BM25-like).
        
        Args:
            query: User's question
            vector_results: Results from vector search
            top_k: Number of final results
        
        Returns:
            Reranked results combining both approaches
        """
        # Simple keyword matching for hybrid approach
        query_terms = set(query.lower().split())
        
        # Add keyword scores to vector results
        for result in vector_results:
            doc_text = result.get('document', '').lower()
            doc_terms = set(doc_text.split())
            
            # Calculate keyword overlap
            overlap = len(query_terms.intersection(doc_terms))
            keyword_score = overlap / len(query_terms) if query_terms else 0
            
            # Combine scores (weighted average)
            vector_score = result.get('similarity', 0)
            result['hybrid_score'] = 0.7 * vector_score + 0.3 * keyword_score
        
        # Sort by hybrid score
        vector_results.sort(key=lambda x: x.get('hybrid_score', 0), reverse=True)
        
        return vector_results[:top_k]
    
    def retrieve_with_context(
        self,
        query: str,
        top_k: int = TOP_K,
        expand_context: bool = True
    ) -> List[Dict]:
        """
        Retrieve documents with expanded context (surrounding chunks).
        
        Args:
            query: User's question
            top_k: Number of documents to retrieve
            expand_context: Whether to include surrounding chunks
        
        Returns:
            List of documents with expanded context
        """
        # Get initial results
        results = self.retrieve(query, top_k=top_k)
        
        if not expand_context:
            return results
        
        # Expand context by retrieving adjacent chunks
        expanded_results = []
        seen_ids = set()
        
        for result in results:
            chunk_id = result.get('id')
            if chunk_id in seen_ids:
                continue
            
            seen_ids.add(chunk_id)
            expanded_results.append(result)
            
            # Try to get adjacent chunks (simplified - would need chunk ordering metadata)
            # This is a placeholder for context expansion logic
        
        return expanded_results
    
    def retrieve_by_metadata(
        self,
        query: str,
        metadata_filter: Dict,
        top_k: int = TOP_K
    ) -> List[Dict]:
        """
        Retrieve documents filtered by metadata.
        
        Args:
            query: User's question
            metadata_filter: Dictionary of metadata filters
            top_k: Number of documents to retrieve
        
        Returns:
            Filtered list of documents
        """
        query_embedding = self.embeddings.embed_query(query)
        
        # Use ChromaDB's metadata filtering
        results = self.vector_store.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=metadata_filter
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'similarity': 1 - results['distances'][0][i]
            })
        
        return formatted_results
