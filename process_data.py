"""
Data processing script to prepare the knowledge base.
This script processes all PDFs and audio files from ./resources folder.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.dirname(__file__))

from src.data_processing.pdf_loader import PDFLoader
from src.data_processing.audio_transcriber import WhisperTranscriber
from src.data_processing.text_chunker import TextChunker
from src.embeddings.embedding_generator import OllamaEmbeddings
from src.embeddings.vector_store import ChromaVectorStore


def main():
    """Main data processing pipeline."""
    print("="*60)
    print("AI-Agentic RAG System - Data Processing")
    print("="*60)
    print()
    
    # Define paths
    resources_dir = Path("./resources")
    processed_dir = Path("./data/processed")
    pdf_output = processed_dir / "pdf_text"
    audio_output = processed_dir / "audio_transcripts"
    chunks_output = processed_dir / "chunks"
    
    # Create directories
    pdf_output.mkdir(parents=True, exist_ok=True)
    audio_output.mkdir(parents=True, exist_ok=True)
    chunks_output.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Process PDFs
    print("Step 1: Processing PDF files...")
    print("-"*60)
    pdf_loader = PDFLoader()
    pdf_files = list(resources_dir.glob("*.pdf"))
    
    if pdf_files:
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            try:
                text = pdf_loader.load_pdf(str(pdf_file))
                output_file = pdf_output / f"{pdf_file.stem}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"✓ Saved to: {output_file}")
            except Exception as e:
                print(f"✗ Error: {e}")
        print(f"\n✓ Processed {len(pdf_files)} PDF files\n")
    else:
        print("No PDF files found in ./resources\n")
    
    # Step 2: Transcribe audio files
    print("Step 2: Transcribing audio/video files...")
    print("-"*60)
    
    whisper_url = os.getenv("WHISPER_BASE_URL", "http://localhost:9000")
    print(f"Using Whisper service at: {whisper_url}")
    
    try:
        transcriber = WhisperTranscriber(base_url=whisper_url)
        audio_files = list(resources_dir.glob("*.mp3")) + \
                     list(resources_dir.glob("*.mp4")) + \
                     list(resources_dir.glob("*.wav"))
        
        if audio_files:
            for audio_file in audio_files:
                print(f"Transcribing: {audio_file.name}")
                try:
                    result = transcriber.transcribe_audio(str(audio_file))
                    text = result.get('text', '')
                    
                    output_file = audio_output / f"{audio_file.stem}.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    print(f"✓ Saved to: {output_file}")
                except Exception as e:
                    print(f"✗ Error: {e}")
            print(f"\n✓ Transcribed {len(audio_files)} audio files\n")
        else:
            print("No audio files found in ./resources\n")
    except Exception as e:
        print(f"✗ Whisper service error: {e}")
        print("Make sure Whisper service is running at http://localhost:9000\n")
    
    # Step 3: Chunk all text
    print("Step 3: Chunking text...")
    print("-"*60)
    
    chunk_size = int(os.getenv("CHUNK_SIZE", 800))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 150))
    
    chunker = TextChunker(chunk_size=chunk_size, overlap=chunk_overlap)
    
    all_text_files = list(pdf_output.glob("*.txt")) + list(audio_output.glob("*.txt"))
    all_chunks = []
    
    for text_file in all_text_files:
        print(f"Chunking: {text_file.name}")
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            chunks = chunker.chunk_text(text)
            
            # Add metadata
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    'text': chunk,
                    'source': text_file.name,
                    'chunk_id': f"{text_file.stem}_{i}"
                })
            
            print(f"✓ Created {len(chunks)} chunks")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n✓ Total chunks created: {len(all_chunks)}\n")
    
    # Step 4: Generate embeddings and store in ChromaDB
    print("Step 4: Generating embeddings and populating vector store...")
    print("-"*60)
    
    try:
        # Initialize components
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = int(os.getenv("CHROMA_PORT", 8000))
        
        print(f"Ollama: {ollama_url}")
        print(f"ChromaDB: {chroma_host}:{chroma_port}")
        print()
        
        embeddings = OllamaEmbeddings(
            base_url=ollama_url,
            model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        )
        
        vector_store = ChromaVectorStore(
            host=chroma_host,
            port=chroma_port,
            collection_name=os.getenv("CHROMA_COLLECTION_NAME", "rag_knowledge_base")
        )
        
        # Generate embeddings in batches
        print("Generating embeddings...")
        texts = [chunk['text'] for chunk in all_chunks]
        metadatas = [{'source': chunk['source'], 'chunk_id': chunk['chunk_id']} 
                     for chunk in all_chunks]
        ids = [chunk['chunk_id'] for chunk in all_chunks]
        
        chunk_embeddings = embeddings.embed_batch(texts, batch_size=32)
        
        # Add to vector store
        print("\nAdding to vector store...")
        vector_store.add_documents(
            documents=texts,
            embeddings=chunk_embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        # Get stats
        stats = vector_store.get_collection_stats()
        print(f"\n✓ Vector store populated!")
        print(f"  Collection: {stats.get('name')}")
        print(f"  Documents: {stats.get('count')}")
        print()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure services are running:")
        print("  - Ollama: http://localhost:11434")
        print("  - ChromaDB: http://localhost:8000")
        print()
        return
    
    # Summary
    print("="*60)
    print("Data Processing Complete!")
    print("="*60)
    print(f"\nProcessed:")
    print(f"  - {len(pdf_files)} PDF files")
    print(f"  - {len(audio_files) if 'audio_files' in locals() else 0} audio files")
    print(f"  - {len(all_chunks)} text chunks")
    print(f"  - {len(all_chunks)} embeddings")
    print(f"\nVector store ready for queries!")
    print()


if __name__ == "__main__":
    main()
