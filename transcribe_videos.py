"""
Dedicated script to transcribe the two MP4 video files.
This extracts audio to WAV format first for better Whisper compatibility.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.dirname(__file__))

from src.data_processing.audio_transcriber import WhisperTranscriber

def main():
    print("="*60)
    print("Video Transcription Script")
    print("="*60)
    print()
    
    # Files to transcribe
    video_files = [
        "resources/1_part_RAG_Intro.mp4",
        "resources/2_part_Databases_for_GenAI.mp4"
    ]
    
    output_dir = Path("data/processed/audio_transcripts")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    transcriber = WhisperTranscriber(base_url="http://localhost:9000")
    
    for video_file in video_files:
        video_path = Path(video_file)
        
        if not video_path.exists():
            print(f"⚠ File not found: {video_file}")
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing: {video_path.name}")
        print(f"Size: {video_path.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"{'='*60}")
        
        try:
            # Transcribe with audio extraction
            result = transcriber.transcribe_audio(str(video_path), extract_audio=True)
            
            # Save results
            text = result.get('text', '')
            
            if text and len(text.strip()) > 0:
                # Save text
                text_output = output_dir / f"{video_path.stem}.txt"
                with open(text_output, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                # Save full JSON
                import json
                json_output = output_dir / f"{video_path.stem}_full.json"
                with open(json_output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"\n✓ SUCCESS!")
                print(f"  Transcribed: {len(text)} characters")
                print(f"  Saved to: {text_output}")
            else:
                print(f"\n✗ FAILED: Whisper returned empty transcription")
                print(f"  Response: {result}")
                
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("Transcription Complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
