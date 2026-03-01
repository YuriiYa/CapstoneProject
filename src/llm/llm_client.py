import requests
from typing import List, Dict, Optional
import json
import os
from src.config.constants import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    TOP_P,
    TOP_K
)


class OllamaClient:
    def __init__(
        self,
        base_url: str = None,
        model: str = None
    ):
        self.base_url = base_url or OLLAMA_BASE_URL
        self.model = model or OLLAMA_MODEL
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE,
        stream: bool = False
    ) -> str:
        """Generate text using Ollama"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": TOP_P,
                    "top_k": TOP_K
                }
            }
        )
        response.raise_for_status()
        
        if stream:
            return self._handle_stream(response)
        else:
            return response.json()["response"]
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE
    ) -> str:
        """Chat completion format (recommended for Gemma 3)"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    
    def _handle_stream(self, response):
        """Handle streaming responses"""
        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if "response" in chunk:
                    full_response += chunk["response"]
                    print(chunk["response"], end="", flush=True)
        print()  # New line after streaming
        return full_response
    
    def test_connection(self) -> bool:
        """Test if Ollama is accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
