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


    def _get_fallback_post(self) -> str:
        """Get fallback post if generation fails."""
        return "Sorry, I couldn't generate the LinkedIn post at this time. Please try again later."

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
