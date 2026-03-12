"""
Main CLI interface for the AI-Agentic RAG System.
"""

import sys
import os
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.dirname(__file__))

from src.embeddings.vector_store import ChromaVectorStore
from src.embeddings.embedding_generator import OllamaEmbeddings
from src.retrieval.retriever import Retriever
from src.llm.llm_client import OllamaClient
from src.llm.prompt_templates import PromptTemplates
from src.agent.reasoning_engine import ReasoningEngine
from src.agent.tool_manager import ToolManager
from src.agent.reflection_module import ReflectionModule
from src.agent.post_generator import LinkedInPostGenerator
from src.agent.rag_base import RAGAgentBase
from src.config.constants import (
    CHROMA_HOST,
    CHROMA_PORT,
    CHROMA_COLLECTION_NAME,
    OLLAMA_BASE_URL,
    OLLAMA_EMBEDDING_MODEL,
    OLLAMA_MODEL,
    TOP_K,
    MAX_TOKENS,
    TEMPERATURE,
    CONFIDENCE,
    LINKEDIN_POST_TONE,
    LINKEDIN_POST_LENGTH,
    LINKEDIN_POST_MAX_CHARS,
    VERBOSE,
    GENERATE_LINKEDIN_POSTS,
)


class RAGAgentCLI(RAGAgentBase):
    """Command-line interface for the RAG Agent."""

    def __init__(self):
        """Initialize all RAG agent components."""
        try:
            super().__init__()
            print("-" * 60)
            print("✓ RAG Agent ready!\n")
        except Exception as e:
            print(f"✗ Error initializing RAG Agent: {e}")
            print("\nMake sure all services are running:")
            print("  - Ollama: http://localhost:11434")
            print("  - ChromaDB: http://localhost:8000")
            sys.exit(1)

    def process_query(
        self,
        question: str,
        verbose: bool = VERBOSE,
        generate_linkedin_post: bool = GENERATE_LINKEDIN_POSTS,
        post_tone: str = LINKEDIN_POST_TONE,
        post_length: str = LINKEDIN_POST_LENGTH,
    ):
        """
        Process a user query through the RAG pipeline.

        Args:
            question: User's question
            verbose: Whether to show detailed output
            generate_linkedin_post: Whether to generate a LinkedIn post
            post_tone: Tone for the LinkedIn post
            post_length: Length for the LinkedIn post
        """
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}\n")

        try:
            result = self._process_query_common(
                question=question,
                include_reasoning=INCLUDE_REASONING,
                verbose=verbose,
                generate_linkedin_post=generate_linkedin_post,
                post_tone=post_tone,
                post_length=post_length,
                return_post_as_answer=generate_linkedin_post
            )

            print(f"\n📝 Answer:\n{result.get('answer')}\n")
            print(f"✓ Confidence: {result.get('confidence', CONFIDENCE):.1%}")

        except Exception as e:
            print(f"✗ Error processing query: {e}\n")

    def show_stats(self):
        """Show vector store statistics."""
        print("\n" + "="*60)
        print("Vector Store Statistics")
        print("="*60 + "\n")

        try:
            stats = self.vector_store.get_collection_stats()
            print(f"Collection: {stats.get('name', 'N/A')}")
            print(f"Documents: {stats.get('count', 0)}")
            print(f"Metadata: {stats.get('metadata', {})}")
            print()
        except Exception as e:
            print(f"Error getting stats: {e}\n")

    def run_test_questions(self):
        """Run the required test questions."""
        from tests.test_questions import get_required_questions

        print("\n" + "="*60)
        print("Running Required Test Questions")
        print("="*60 + "\n")

        questions = get_required_questions()

        for i, test_case in enumerate(questions, 1):
            print(f"\nTest {i}/{len(questions)}")
            self.process_query(test_case['question'], verbose=False)

            if i < len(questions):
                input("Press Enter to continue to next question...")

    def show_menu(self):
        """Show interactive menu."""
        print("\n" + "="*60)
        print("AI-Agentic RAG System - Main Menu")
        print("="*60)
        print("\n1. Ask a question")
        print("2. Run test questions")
        print("3. vacant place")
        print("4. Show vector store stats")
        print("5. Exit")
        print()

    def run(self):
        """Run the interactive CLI."""
        parser = argparse.ArgumentParser(description="AI-Agentic RAG System CLI")
        parser.add_argument("question", nargs="?", help="Question to ask")
        args, unknown = parser.parse_known_args()

        if args.question:
            self.process_query(
                args.question
            )
            return

        print("\n" + "="*60)
        print("AI-Agentic RAG System - CLI Mode")
        print("="*60)
        print("\nType 'menu' to see options, 'quit' to exit\n")

        while True:
            try:
                user_input = input("Question (or command): ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break

                elif user_input.lower() == 'menu':
                    self.show_menu()
                    choice = input("Select option (1-5): ").strip()

                    if choice == '1':
                        question = input("\nYour question: ").strip()
                        if question:
                            self.process_query(question)
                    elif choice == '2':
                        self.run_test_questions()
                    elif choice == '3':
                        print("vacant place")
                    elif choice == '4':
                        self.show_stats()
                    elif choice == '5':
                        print("\nGoodbye!")
                        break

                elif user_input.lower() == 'test':
                    self.run_test_questions()

                elif user_input.lower() == 'post':
                    question = input("\nTopic/question for LinkedIn post: ").strip()
                    if question:
                        self.process_query(
                            question,
                            generate_linkedin_post=True,
                        )

                elif user_input.lower() == 'stats':
                    self.show_stats()

                else:
                    # Treat as a question
                    self.process_query(
                        user_input,
                        generate_linkedin_post=True,
                    )

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")


if __name__ == "__main__":
    agent = RAGAgentCLI()
    agent.run()
