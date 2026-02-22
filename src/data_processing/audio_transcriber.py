import requests
import os
from pathlib import Path
from typing import Dict, List
import json
import argparse
import subprocess
import tempfile


class WhisperTranscriber:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("WHISPER_BASE_URL", "http://localhost:9000")
        
    def extract_audio_to_wav(self, video_path: str, output_path: str = None) -> str:
        """Extract audio from video file to WAV format for better Whisper compatibility"""
        if output_path is None:
            # Create temp file
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, f"{Path(video_path).stem}_audio.wav")
        
        print(f"    Extracting audio to WAV format...")
        
        # Use ffmpeg to extract audio: 16kHz mono WAV (optimal for Whisper)
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vn',  # No video
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',  # Mono
            '-f', 'wav',  # WAV format
            '-y',  # Overwrite
            output_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"    Audio extracted: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"    Error extracting audio: {e.stderr}")
            raise
        
    def transcribe_audio(self, audio_path: str, extract_audio: bool = True) -> Dict:
        """Transcribe audio file using Whisper service
        
        Args:
            audio_path: Path to audio/video file
            extract_audio: If True and file is MP4, extract audio to WAV first
        """
        original_path = audio_path
        temp_wav = None
        
        try:
            # For MP4 files, extract audio to WAV first for better compatibility
            if extract_audio and audio_path.lower().endswith('.mp4'):
                print(f"    Processing MP4 file (size: {os.path.getsize(audio_path) / 1024 / 1024:.1f} MB)")
                temp_wav = self.extract_audio_to_wav(audio_path)
                audio_path = temp_wav
            else:
                print(f"    Uploading file... (size: {os.path.getsize(audio_path) / 1024 / 1024:.1f} MB)")
            
            with open(audio_path, 'rb') as audio_file:
                files = {'audio_file': audio_file}
                
                # Long timeout for large files (30 minutes)
                print(f"    Transcribing... (this can take 5-30 minutes for large files)")
                response = requests.post(
                    f"{self.base_url}/asr",
                    files=files,
                    params={'task': 'transcribe', 'output': 'json'},
                    timeout=1800  # 30 minutes timeout
                )
                response.raise_for_status()
                result = response.json()
                
                # Check if transcription is empty
                text = result.get('text', '')
                if not text or len(text.strip()) == 0:
                    print(f"    WARNING: Transcription returned empty text!")
                    print(f"    Response: {result}")
                else:
                    print(f"    Transcription complete! ({len(text)} characters)")
                
                return result
                
        finally:
            # Clean up temp WAV file
            if temp_wav and os.path.exists(temp_wav):
                try:
                    os.remove(temp_wav)
                    print(f"    Cleaned up temporary WAV file")
                except:
                    pass
    
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
    
    def process_audio_files(self, audio_dir: str, output_dir: str, extract_audio: bool = True):
        """Process all audio files in directory
        
        Args:
            audio_dir: Directory containing audio/video files
            output_dir: Directory to save transcriptions
            extract_audio: If True, extract audio from MP4 to WAV first
        """
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
                # Use transcribe_audio which handles MP4 extraction
                result = self.transcribe_audio(str(audio_file), extract_audio=extract_audio)
                
                # Save full JSON result
                json_output = output_dir / f"{audio_file.stem}_full.json"
                with open(json_output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                # Extract and save clean text
                text = result.get('text', '')
                text_output = output_dir / f"{audio_file.stem}.txt"
                with open(text_output, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                if text and len(text.strip()) > 0:
                    print(f"✓ Saved {len(text)} characters to: {text_output}")
                else:
                    print(f"⚠ WARNING: Empty transcription saved to: {text_output}")
                
            except Exception as e:
                print(f"✗ Error transcribing {audio_file.name}: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe audio files using Whisper')
    parser.add_argument('--input', default='./resources', help='Input directory containing audio files')
    parser.add_argument('--output', default='./data/processed/audio_transcripts', help='Output directory for transcriptions')
    
    args = parser.parse_args()
    
    transcriber = WhisperTranscriber()
    transcriber.process_audio_files(args.input, args.output)
