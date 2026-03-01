"""
Browse ChromaDB collection contents.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(__file__))

from src.embeddings.vector_store import ChromaVectorStore


def main():
    """Browse ChromaDB collection."""
    print("="*60)
    print("ChromaDB Collection Browser")
    print("="*60)
    print()
    
    # Connect to ChromaDB
    chroma_host = os.getenv("CHROMA_HOST", "localhost")
    chroma_port = int(os.getenv("CHROMA_PORT", 8000))
    collection_name = os.getenv("CHROMA_COLLECTION_NAME", "rag_knowledge_base")
    
    print(f"Connecting to ChromaDB at {chroma_host}:{chroma_port}")
    print(f"Collection: {collection_name}")
    print()
    
    try:
        vector_store = ChromaVectorStore(
            host=chroma_host,
            port=chroma_port,
            collection_name=collection_name
        )
        
        # Get collection stats
        stats = vector_store.get_collection_stats()
        print("Collection Statistics:")
        print("-"*60)
        print(f"Name: {stats.get('name', 'N/A')}")
        print(f"Total Documents: {stats.get('count', 0)}")
        print(f"Metadata: {stats.get('metadata', {})}")
        print()
        
        # Get all documents
        if stats.get('count', 0) > 0:
            print("Fetching documents...")
            print("-"*60)
            
            # Get all documents from collection
            results = vector_store.collection.get(
                limit=stats.get('count', 100),
                include=['documents', 'metadatas']
            )
            
            documents = results.get('documents', [])
            metadatas = results.get('metadatas', [])
            ids = results.get('ids', [])
            
            # Group by source
            sources = {}
            for i, (doc, meta, doc_id) in enumerate(zip(documents, metadatas, ids)):
                source = meta.get('source', 'Unknown')
                if source not in sources:
                    sources[source] = []
                sources[source].append({
                    'id': doc_id,
                    'text': doc[:100] + '...' if len(doc) > 100 else doc,
                    'full_text': doc
                })
            
            # Display summary by source
            print(f"\nDocuments by Source:")
            print("-"*60)
            for source, docs in sorted(sources.items()):
                print(f"\n📄 {source}")
                print(f"   Chunks: {len(docs)}")
                print(f"   Sample: {docs[0]['text']}")
            
            print()
            print("="*60)
            print(f"Total: {len(documents)} chunks from {len(sources)} sources")
            print("="*60)
            
            # Interactive mode
            print("\nOptions:")
            print("1. View full document by ID")
            print("2. Search by keyword")
            print("3. Exit")
            
            while True:
                choice = input("\nEnter choice (1-3): ").strip()
                
                if choice == '1':
                    doc_id = input("Enter document ID: ").strip()
                    found = False
                    for i, (doc, doc_id_check) in enumerate(zip(documents, ids)):
                        if doc_id in doc_id_check:
                            print("\n" + "="*60)
                            print(f"Document ID: {doc_id_check}")
                            print(f"Metadata: {metadatas[i]}")
                            print("-"*60)
                            print(doc)
                            print("="*60)
                            found = True
                            break
                    if not found:
                        print("Document not found!")
                
                elif choice == '2':
                    keyword = input("Enter keyword: ").strip().lower()
                    matches = []
                    for i, doc in enumerate(documents):
                        if keyword in doc.lower():
                            matches.append((ids[i], metadatas[i], doc))
                    
                    if matches:
                        print(f"\nFound {len(matches)} matches:")
                        print("-"*60)
                        for doc_id, meta, doc in matches[:5]:  # Show first 5
                            print(f"\nID: {doc_id}")
                            print(f"Source: {meta.get('source', 'Unknown')}")
                            print(f"Text: {doc[:200]}...")
                            print("-"*60)
                        if len(matches) > 5:
                            print(f"\n... and {len(matches) - 5} more matches")
                    else:
                        print("No matches found!")
                
                elif choice == '3':
                    print("\nGoodbye!")
                    break
                else:
                    print("Invalid choice!")
        
        else:
            print("⚠ Collection is empty!")
            print("\nRun 'python process_data.py' to populate the collection.")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure ChromaDB is running:")
        print(f"  docker ps | grep chromadb")
        print(f"  or")
        print(f"  podman ps | grep chromadb")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
