"""
Data processing script to prepare the knowledge base.
This script processes all PDFs and audio files from ./resources folder.
"""

import os
import sys
import json
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
        processed_count = 0
        skipped_count = 0
        
        for pdf_file in pdf_files:
            output_file = pdf_output / f"{pdf_file.stem}.txt"
            
            # Check if already processed
            if output_file.exists() and output_file.stat().st_size > 0:
                print(f"⏭ Skipping (already processed): {pdf_file.name}")
                skipped_count += 1
                continue
            
            print(f"Processing: {pdf_file.name}")
            try:
                result = pdf_loader.load_pdf(str(pdf_file))
                
                # Extract text from the dictionary structure
                with open(output_file, 'w', encoding='utf-8') as f:
                    for page_data in result['content']:
                        f.write(f"=== Page {page_data['page']} ===\n")
                        f.write(page_data['text'])
                        f.write("\n\n")
                
                print(f"✓ Extracted {result['metadata']['pages']} pages to: {output_file}")
                processed_count += 1
            except Exception as e:
                print(f"✗ Error: {e}")
        
        print(f"\n✓ Processed {processed_count} new PDF files")
        if skipped_count > 0:
            print(f"⏭ Skipped {skipped_count} already processed files")
        print()
    else:
        print("No PDF files found in ./resources\n")
    
    # Step 2: Transcribe audio files
    print("Step 2: Transcribing audio/video files...")
    print("-"*60)
    
    whisper_url = os.getenv("WHISPER_BASE_URL", "http://localhost:9000")
    print(f"Using Whisper service at: {whisper_url}")
    print("NOTE: Video transcription can take 5-30 minutes per file!")
    print("INFO: MP4 files will be converted to WAV format first for better compatibility")
    print("INFO: Skipping files that have already been transcribed")
    print()
    
    try:
        transcriber = WhisperTranscriber(base_url=whisper_url)
        audio_files = list(resources_dir.glob("*.mp3")) + \
                     list(resources_dir.glob("*.mp4")) + \
                     list(resources_dir.glob("*.wav"))
        
        if audio_files:
            transcribed_count = 0
            skipped_count = 0
            
            for audio_file in audio_files:
                output_file = audio_output / f"{audio_file.stem}.txt"
                
                # Check if already transcribed
                if output_file.exists() and output_file.stat().st_size > 0:
                    print(f"⏭ Skipping (already transcribed): {audio_file.name}")
                    skipped_count += 1
                    continue
                
                print(f"Transcribing: {audio_file.name}")
                
                try:
                    # Use improved transcribe_audio with MP4 extraction
                    result = transcriber.transcribe_audio(str(audio_file), extract_audio=True)
                    
                    # Save full JSON result
                    json_output = audio_output / f"{audio_file.stem}_full.json"
                    with open(json_output, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    
                    # Extract text from response
                    text = result.get('text', '')
                    
                    if not text or len(text.strip()) == 0:
                        print(f"  ⚠ WARNING: Whisper returned empty transcription!")
                        print(f"  This usually means:")
                        print(f"    - The audio track is silent or corrupted")
                        print(f"    - The audio codec is not supported")
                        print(f"    - The file is too large for Whisper to process")
                        print(f"  Skipping this file...")
                        continue
                    
                    # Save clean text
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    
                    print(f"✓ Saved {len(text)} characters to: {output_file}")
                    transcribed_count += 1
                        
                except Exception as e:
                    print(f"✗ Error: {e}")
                    import traceback
                    traceback.print_exc()
            
            print(f"\n✓ Transcribed {transcribed_count} new audio files")
            if skipped_count > 0:
                print(f"⏭ Skipped {skipped_count} already transcribed files")
            print()
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
    
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    all_text_files = list(pdf_output.glob("*.txt")) + list(audio_output.glob("*.txt"))
    all_chunks = []
    
    for text_file in all_text_files:
        print(f"Chunking: {text_file.name}")
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # chunk_text returns list of dicts with 'text' and 'metadata' keys
            chunks = chunker.chunk_text(text)
            
            # Add source information to metadata
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    'text': chunk['text'],  # Extract text from chunk dict
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
