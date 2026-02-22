"""
LLM module for language model interaction.
"""

from .llm_client import OllamaClient
from .prompt_templates import PromptTemplates

__all__ = ['OllamaClient', 'PromptTemplates']
