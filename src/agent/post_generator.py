"""
LinkedIn post generator for creating professional social media content.
"""

from typing import Dict


class LinkedInPostGenerator:
    """
    Generates professional LinkedIn posts about the AI agent.
    """

    def __init__(self, llm_client):
        """
        Initialize post generator with LLM client.

        Args:
            llm_client: OllamaClient instance
        """
        self.llm = llm_client

    def generate_post(
        self,
        agent_description: str = None,
        tech_stack: str = None,
        achievements: str = None
    ) -> str:
        """
        Generate a LinkedIn post about the AI agent.

        Args:
            agent_description: Description of what the agent does
            tech_stack: Technologies used
            achievements: Key accomplishments

        Returns:
            Generated LinkedIn post
        """
        from src.llm.prompt_templates import PromptTemplates

        # Use defaults if not provided
        if not agent_description:
            agent_description = self._get_default_description()

        if not tech_stack:
            tech_stack = self._get_default_tech_stack()

        if not achievements:
            achievements = self._get_default_achievements()

        # Generate post
        prompt = PromptTemplates.linkedin_post_template(
            agent_description=agent_description,
            tech_stack=tech_stack,
            achievements=achievements
        )
        print(f"Generating LinkedIn post \nprompt: {prompt}\n {agent_description}\n {tech_stack}\n {achievements}")

        try:
            post = self.llm.generate(
                prompt,
                max_tokens=400,
                temperature=0.7
            )

            return post.strip()

        except Exception as e:
            print(f"Error generating LinkedIn post: {e}")
            return self._get_fallback_post()

    def _get_default_description(self) -> str:
        """Get default agent description."""
        return """An AI-Agentic RAG system that processes multi-format knowledge bases (PDFs and audio),
retrieves relevant context using hybrid search, and generates intelligent responses with autonomous
reasoning, tool-calling, and self-reflection capabilities."""

    def _get_default_tech_stack(self) -> str:
        """Get default technology stack."""
        return """Ollama (Gemma 3 12B), ChromaDB, Whisper, Flask, Python, Docker/Podman,
nomic-embed-text embeddings, Open WebUI"""

    def _get_default_achievements(self) -> str:
        """Get default achievements."""
        return """Successfully implemented end-to-end RAG pipeline with agentic capabilities including
query analysis, chain-of-thought reasoning, tool execution, and self-reflection. The system processes
both PDF documents and audio lectures, performs hybrid search for better retrieval, and provides
confidence-scored answers with source citations."""

    def _get_fallback_post(self) -> str:
        """Get fallback post if generation fails."""
        return """🚀 Excited to share my AI-Agentic RAG System!

Just completed building an intelligent RAG chatbot as part of the Ciklum AI Academy Engineering Track.
This system goes beyond simple retrieval - it features autonomous reasoning, self-reflection, and
tool-calling capabilities.

Key highlights:
✅ Processes PDFs and audio lectures using Whisper
✅ Hybrid search with ChromaDB for better retrieval
✅ Powered by Gemma 3 12B via Ollama
✅ Self-reflects on answer quality with confidence scoring
✅ Containerized deployment with Docker/Podman

The journey taught me so much about building production-ready AI systems with proper evaluation
and agentic capabilities. Grateful for the learning opportunity at Ciklum AI Academy!

#AI #MachineLearning #RAG #Ciklum #AIAcademy #LLM"""

    def generate_custom_post(
        self,
        custom_prompt: str
    ) -> str:
        """
        Generate a post with a custom prompt.

        Args:
            custom_prompt: Custom prompt for post generation

        Returns:
            Generated post
        """
        try:
            post = self.llm.generate(
                custom_prompt,
                max_tokens=400,
                temperature=0.7
            )
            return post.strip()
        except Exception as e:
            print(f"Error generating custom post: {e}")
            return self._get_fallback_post()

    def save_post(self, post: str, filename: str = "linkedin_post.txt"):
        """
        Save generated post to file.

        Args:
            post: Generated post content
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(post)
            print(f"✓ Post saved to {filename}")
        except Exception as e:
            print(f"Error saving post: {e}")
