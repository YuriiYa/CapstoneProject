import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid
import os
from src.config.constants import (
    CHROMA_HOST,
    CHROMA_PORT,
    CHROMA_COLLECTION_NAME,
    TOP_K,
    SIMILARITY_THRESHOLD
)


class ChromaVectorStore:
    def __init__(
        self,
        host: str = None,
        port: int = None,
        collection_name: str = None
    ):
        host = host or CHROMA_HOST
        port = port or CHROMA_PORT
        collection_name = collection_name or CHROMA_COLLECTION_NAME
        
        # Connect to containerized ChromaDB
        # Use v2 API compatible settings
        try:
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        except Exception as e:
            print(f"Warning: Could not connect to ChromaDB with v2 settings: {e}")
            # Fallback to basic connection
            self.client = chromadb.HttpClient(
                host=host,
                port=port
            )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ):
        """Add documents with embeddings to the vector store"""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to vector store")
    
    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = TOP_K,
        filter_dict: Optional[Dict] = None
    ) -> Dict:
        """Search for similar documents"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict
        )
        return results
    
    def similarity_search_with_score(
        self,
        query_embedding: List[float],
        top_k: int = TOP_K,
        similarity_threshold: float = SIMILARITY_THRESHOLD
    ) -> List[Dict]:
        """Search with similarity score filtering"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Filter by similarity threshold
        filtered_results = []
        for i, distance in enumerate(results['distances'][0]):
            similarity = 1 - distance  # Convert distance to similarity
            if similarity >= similarity_threshold:
                filtered_results.append({
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity': similarity,
                    'id': results['ids'][0][i]
                })
        
        return filtered_results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        return {
            'name': self.collection.name,
            'count': self.collection.count(),
            'metadata': self.collection.metadata
        }
    
    def clear_collection(self):
        """Delete all documents from the collection"""
        try:
            self.client.delete_collection(self.collection.name)
            print(f"✓ Deleted collection: {self.collection.name}")
            # Recreate the collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection.name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"✓ Recreated empty collection: {self.collection.name}")
        except Exception as e:
            print(f"✗ Error clearing collection: {e}")
    
    def delete_by_filter(self, filter_dict: Dict):
        """Delete documents matching filter criteria"""
        try:
            self.collection.delete(where=filter_dict)
            print(f"✓ Deleted documents matching filter: {filter_dict}")
        except Exception as e:
            print(f"✗ Error deleting documents: {e}")
