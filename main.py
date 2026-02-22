"""
Main CLI interface for the AI-Agentic RAG System.
"""

import sys
import os
from dotenv import load_dotenv

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


class RAGAgentCLI:
    """Command-line interface for the RAG Agent."""
    
    def __init__(self):
        """Initialize all RAG agent components."""
        print("Initializing RAG Agent...")
        print("-" * 60)
        
        # Initialize components
        try:
            self.vector_store = ChromaVectorStore(
                host=os.getenv("CHROMA_HOST", "localhost"),
                port=int(os.getenv("CHROMA_PORT", 8000)),
                collection_name=os.getenv("CHROMA_COLLECTION_NAME", "rag_knowledge_base")
            )
            print("✓ Vector store connected")
            
            self.embeddings = OllamaEmbeddings(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
            )
            print("✓ Embeddings generator initialized")
            
            self.retriever = Retriever(self.vector_store, self.embeddings)
            print("✓ Retriever initialized")
            
            self.llm_client = OllamaClient(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=os.getenv("OLLAMA_MODEL", "gemma3:12b-instruct-q4_K_M")
            )
            print("✓ LLM client initialized")
            
            self.reasoning_engine = ReasoningEngine(self.llm_client)
            print("✓ Reasoning engine initialized")
            
            self.tool_manager = ToolManager()
            print("✓ Tool manager initialized")
            
            self.reflection_module = ReflectionModule(self.llm_client)
            print("✓ Reflection module initialized")
            
            self.post_generator = LinkedInPostGenerator(self.llm_client)
            print("✓ Post generator initialized")
            
            print("-" * 60)
            print("✓ RAG Agent ready!\n")
            
        except Exception as e:
            print(f"✗ Error initializing RAG Agent: {e}")
            print("\nMake sure all services are running:")
            print("  - Ollama: http://localhost:11434")
            print("  - ChromaDB: http://localhost:8000")
            sys.exit(1)
    
    def process_query(self, question: str, verbose: bool = True):
        """
        Process a user query through the RAG pipeline.
        
        Args:
            question: User's question
            verbose: Whether to show detailed output
        """
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}\n")
        
        try:
            # 1. Analyze query
            if verbose:
                print("🔍 Analyzing query...")
            analysis = self.reasoning_engine.analyze_query(question)
            if verbose:
                print(f"   Intent: {analysis.get('intent', 'unknown')}")
                print(f"   Complexity: {analysis.get('complexity', 'unknown')}")
                print()
            
            # 2. Retrieve context
            if verbose:
                print("📚 Retrieving context...")
            context = self.retriever.retrieve(question, top_k=5)
            if verbose:
                print(f"   Retrieved {len(context)} relevant chunks")
                print()
            
            # 3. Generate answer
            if verbose:
                print("💭 Generating answer...")
            context_text = PromptTemplates.format_context(context)
            prompt = PromptTemplates.rag_query_template(context_text, question)
            answer = self.llm_client.generate(prompt, max_tokens=500, temperature=0.7)
            
            print(f"\n📝 Answer:\n{answer}\n")
            
            # 4. Reflect on answer
            if verbose:
                print("🤔 Reflecting on answer quality...")
            reflection = self.reflection_module.reflect(question, context, answer)
            confidence = reflection.get('confidence', 0.0)
            
            print(f"✓ Confidence: {confidence:.1%}")
            
            if reflection.get('issues'):
                print(f"⚠ Issues identified: {', '.join(reflection['issues'])}")
            
            # 5. Show sources
            if verbose and context:
                print(f"\n📖 Sources:")
                for i, ctx in enumerate(context[:3], 1):
                    metadata = ctx.get('metadata', {})
                    source = metadata.get('source', 'Unknown')
                    similarity = ctx.get('similarity', 0.0)
                    print(f"   {i}. {source} (similarity: {similarity:.2%})")
            
            print()
            
        except Exception as e:
            print(f"✗ Error processing query: {e}\n")
    
    def generate_linkedin_post(self):
        """Generate a LinkedIn post about the agent."""
        print("\n" + "="*60)
        print("Generating LinkedIn Post")
        print("="*60 + "\n")
        
        print("Generating post...")
        post = self.post_generator.generate_post()
        
        print("\n" + "-"*60)
        print(post)
        print("-"*60 + "\n")
        
        # Ask if user wants to save
        save = input("Save to file? (y/n): ").strip().lower()
        if save == 'y':
            self.post_generator.save_post(post)
    
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
        print("3. Generate LinkedIn post")
        print("4. Show vector store stats")
        print("5. Exit")
        print()
    
    def run(self):
        """Run the interactive CLI."""
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
                        self.generate_linkedin_post()
                    elif choice == '4':
                        self.show_stats()
                    elif choice == '5':
                        print("\nGoodbye!")
                        break
                
                elif user_input.lower() == 'test':
                    self.run_test_questions()
                
                elif user_input.lower() == 'post':
                    self.generate_linkedin_post()
                
                elif user_input.lower() == 'stats':
                    self.show_stats()
                
                else:
                    # Treat as a question
                    self.process_query(user_input)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")


if __name__ == "__main__":
    agent = RAGAgentCLI()
    agent.run()
