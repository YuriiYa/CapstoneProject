from pathlib import Path
from typing import List, Dict
import re
import argparse
import os


class TextChunker:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or int(os.getenv("CHUNK_SIZE", 800))
        self.chunk_overlap = chunk_overlap or int(os.getenv("CHUNK_OVERLAP", 150))
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Split text into chunks with overlap"""
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'metadata': metadata or {}
                })
                
                # Start new chunk with overlap
                overlap_text = chunk_text[-self.chunk_overlap:] if len(chunk_text) > self.chunk_overlap else chunk_text
                current_chunk = [overlap_text, sentence]
                current_length = len(overlap_text) + sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'text': ' '.join(current_chunk),
                'metadata': metadata or {}
            })
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def process_directory(self, input_dir: str, output_dir: str):
        """Process all text files in directory"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Process all .txt files recursively
        text_files = list(input_path.rglob("*.txt"))
        
        if not text_files:
            print(f"No text files found in {input_dir}")
            return
        
        all_chunks = []
        
        for text_file in text_files:
            print(f"Chunking: {text_file.name}")
            
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Determine source type
                source_type = 'pdf' if 'pdf_text' in str(text_file.parent) else 'audio'
                
                metadata = {
                    'source': str(text_file.name),
                    'source_type': source_type,
                    'source_path': str(text_file)
                }
                
                chunks = self.chunk_text(text, metadata)
                all_chunks.extend(chunks)
                
                print(f"✓ Created {len(chunks)} chunks from {text_file.name}")
                
            except Exception as e:
                print(f"✗ Error processing {text_file.name}: {e}")
        
        # Save all chunks to a single file
        output_file = output_path / "all_chunks.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, chunk in enumerate(all_chunks):
                f.write(f"=== Chunk {i+1} ===\n")
                f.write(f"Source: {chunk['metadata'].get('source', 'unknown')}\n")
                f.write(f"Type: {chunk['metadata'].get('source_type', 'unknown')}\n")
                f.write(f"{chunk['text']}\n\n")
        
        print(f"\n✓ Total chunks created: {len(all_chunks)}")
        print(f"✓ Saved to: {output_file}")
        
        return all_chunks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chunk text files')
    parser.add_argument('--input', default='./data/processed', help='Input directory containing text files')
    parser.add_argument('--output', default='./data/processed/chunks', help='Output directory for chunks')
    parser.add_argument('--chunk-size', type=int, default=800, help='Chunk size in characters')
    parser.add_argument('--overlap', type=int, default=150, help='Overlap size in characters')
    
    args = parser.parse_args()
    
    chunker = TextChunker(chunk_size=args.chunk_size, chunk_overlap=args.overlap)
    chunker.process_directory(args.input, args.output)
