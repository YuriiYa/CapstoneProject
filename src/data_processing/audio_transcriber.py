import requests
import os
from pathlib import Path
from typing import Dict, List
import json
import argparse


class WhisperTranscriber:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("WHISPER_BASE_URL", "http://localhost:9000")
        
    def transcribe_audio(self, audio_path: str) -> Dict:
        """Transcribe audio file using Whisper service"""
        with open(audio_path, 'rb') as audio_file:
            files = {'audio_file': audio_file}
            response = requests.post(
                f"{self.base_url}/asr",
                files=files,
                params={'task': 'transcribe', 'output': 'json'}
            )
            response.raise_for_status()
            return response.json()
    
    def transcribe_with_timestamps(self, audio_path: str) -> Dict:
        """Transcribe with word-level timestamps"""
        with open(audio_path, 'rb') as audio_file:
            files = {'audio_file': audio_file}
            response = requests.post(
                f"{self.base_url}/asr",
                files=files,
                params={
                    'task': 'transcribe',
                    'output': 'json',
                    'word_timestamps': 'true'
                }
            )
            response.raise_for_status()
            return response.json()
    
    def process_audio_files(self, audio_dir: str, output_dir: str):
        """Process all audio files in directory"""
        audio_dir = Path(audio_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        audio_extensions = ['.mp3', '.mp4', '.wav', '.m4a']
        audio_files = [
            f for f in audio_dir.iterdir() 
            if f.suffix.lower() in audio_extensions
        ]
        
        if not audio_files:
            print(f"No audio files found in {audio_dir}")
            return
        
        for audio_file in audio_files:
            print(f"Transcribing: {audio_file.name}")
            
            try:
                result = self.transcribe_with_timestamps(str(audio_file))
                
                # Save full JSON result
                json_output = output_dir / f"{audio_file.stem}_full.json"
                with open(json_output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                # Save clean text
                text_output = output_dir / f"{audio_file.stem}.txt"
                with open(text_output, 'w', encoding='utf-8') as f:
                    f.write(result.get('text', ''))
                
                print(f"✓ Saved to: {text_output}")
                
            except Exception as e:
                print(f"✗ Error transcribing {audio_file.name}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe audio files using Whisper')
    parser.add_argument('--input', default='./resources', help='Input directory containing audio files')
    parser.add_argument('--output', default='./data/processed/audio_transcripts', help='Output directory for transcriptions')
    
    args = parser.parse_args()
    
    transcriber = WhisperTranscriber()
    transcriber.process_audio_files(args.input, args.output)
