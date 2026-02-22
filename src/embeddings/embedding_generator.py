import requests
from typing import List
import os


class OllamaEmbeddings:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        self.dimension = 768  # nomic-embed-text dimension
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents"""
        embeddings = []
        for text in texts:
            embedding = self._generate_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query"""
        return self._generate_embedding(text)
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Internal method to generate embedding"""
        # Skip empty texts
        if not text or not text.strip():
            return [0.0] * self.dimension
        
        # Truncate very long texts (Ollama has limits)
        max_length = 8000  # characters
        if len(text) > max_length:
            text = text[:max_length]
        
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except requests.exceptions.HTTPError as e:
            print(f"\nError generating embedding: {e}")
            print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
            print(f"Text length: {len(text)} characters")
            print(f"Model: {self.model}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings in batches for efficiency"""
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embed_documents(batch)
            embeddings.extend(batch_embeddings)
            print(f"Processed {min(i + batch_size, len(texts))}/{len(texts)} embeddings")
        return embeddings
