"""
Quick test to verify the RAG system is working with the transcribed data.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(__file__))

from src.embeddings.embedding_generator import OllamaEmbeddings
from src.embeddings.vector_store import ChromaVectorStore

def main():
    print("="*60)
    print("RAG System Test")
    print("="*60)
    print()
    
    # Initialize components
    embeddings = OllamaEmbeddings(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    )
    
    vector_store = ChromaVectorStore(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_PORT", 8000)),
        collection_name=os.getenv("CHROMA_COLLECTION_NAME", "rag_knowledge_base")
    )
    
    # Get collection stats
    stats = vector_store.get_collection_stats()
    print(f"Vector Store Stats:")
    print(f"  Collection: {stats.get('name')}")
    print(f"  Documents: {stats.get('count')}")
    print()
    
    # Test queries
    test_queries = [
        "What is RAG and why is it important?",
        "What are the different chunking strategies?",
        "What databases can be used for vector storage?"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        print("-"*60)
        
        # Generate query embedding
        query_embedding = embeddings.embed_query(query)
        
        # Search vector store
        results = vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=3
        )
        
        if results and 'documents' in results and results['documents']:
            for i, doc in enumerate(results['documents'][0][:3], 1):
                print(f"\nResult {i}:")
                print(f"  {doc[:200]}...")
                if 'metadatas' in results and results['metadatas']:
                    metadata = results['metadatas'][0][i-1]
                    print(f"  Source: {metadata.get('source', 'Unknown')}")
        else:
            print("  No results found")
        
        print()
    
    print("="*60)
    print("Test Complete!")
    print("="*60)

if __name__ == "__main__":
    main()
