# filepath: c:\projects\AI Academy\CapstoneProject\src\agent\rag_agent_base.py
import sys
import logging
from pathlib import Path
from typing import Any

# Add project root to Python path because
# when running locally, Python needs to know where to find the src module
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.embeddings.vector_store import ChromaVectorStore
from src.embeddings.embedding_generator import OllamaEmbeddings
from src.retrieval.retriever import Retriever
from src.llm.llm_client import OllamaClient
from src.llm.prompt_templates import PromptTemplates
from src.agent.reasoning_engine import ReasoningEngine
from src.agent.tool_manager import ToolManager
from src.agent.reflection_module import ReflectionModule
from src.evaluation.evaluator import Evaluator
from src.agent.post_generator import LinkedInPostGenerator

from src.config.constants import (
    OLLAMA_BASE_URL,
    OLLAMA_EMBEDDING_MODEL,
    OLLAMA_MODEL,
    CHROMA_HOST,
    CHROMA_PORT,
    CHROMA_COLLECTION_NAME,
    MAX_TOKENS,
    TEMPERATURE,
    TOP_K,
    INCLUDE_REASONING,
    CONFIDENCE,
    ANSWER_ERROR_MESSAGE,
    VERBOSE,
    GENERATE_LINKEDIN_POSTS,
    LINKEDIN_POST_TONE,
    LINKEDIN_POST_LENGTH,
    LINKEDIN_POST_MAX_CHARS,
    USE_TOOLS
)

logger = logging.getLogger(__name__)

class RAGAgentBase:
    """Shared RAG pipeline logic for CLI and API."""

    def __init__(self):
        """Initialize all components."""
        logger.info("Initializing RAG Agent...")
        self.PromptTemplates = PromptTemplates
        self.TOP_K = TOP_K
        self.MAX_TOKENS = MAX_TOKENS
        self.TEMPERATURE = TEMPERATURE
        self.CONFIDENCE = CONFIDENCE
        self.LINKEDIN_POST_MAX_CHARS = LINKEDIN_POST_MAX_CHARS

        try:
            # Initialize components
            self.vector_store = ChromaVectorStore(
                host=CHROMA_HOST,
                port=CHROMA_PORT,
                collection_name=CHROMA_COLLECTION_NAME
            )

            self.embeddings = OllamaEmbeddings(
                base_url=OLLAMA_BASE_URL,
                model=OLLAMA_EMBEDDING_MODEL
            )

            self.retriever = Retriever(self.vector_store, self.embeddings)

            self.llm_client = OllamaClient(
                base_url=OLLAMA_BASE_URL,
                model=OLLAMA_MODEL
            )

            self.reasoning_engine = ReasoningEngine(self.llm_client)
            self.tool_manager = ToolManager()
            self.reflection_module = ReflectionModule(self.llm_client)
            self.post_generator = LinkedInPostGenerator(self.llm_client)
            self.evaluator = Evaluator()

            logger.info("✓ RAG Agent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RAG Agent: {e}", exc_info=True)
            raise

    def logPrint(self, message: str = "") -> None:
        print(message, file=sys.stderr, flush=True)
        logger.info(message)

    def _process_query_common(
        self,
        question: str,
        include_reasoning: bool,
        verbose: bool,
        generate_linkedin_post: bool,
        post_tone: str,
        post_length: str,
        return_post_as_answer: bool,
    ):
        if verbose:
            self.logPrint(f"Question: {question}")

        # 1. Analyze query
        if verbose:
            self.logPrint("\n" + "━" * 60)
            self.logPrint("🔍 1. Analyze query...")
        analysis = self.reasoning_engine.analyze_query(question)
        if verbose:
            self.logPrint(f"   Intent: {analysis.get('intent', 'unknown')}")
            self.logPrint(f"   Complexity: {analysis.get('complexity', 'unknown')}")
            self.logPrint("")

        # 2. Retrieve context
        if verbose:
            self.logPrint("\n" + "━" * 60)
            self.logPrint("📚 2. Retrieving context...")
        context = self.retriever.retrieve(question, top_k=self.TOP_K)
        if context and verbose:
            self.logPrint(f" Retrieved {len(context)} relevant chunks")
            self.logPrint("\n📖 Sources:")
            for i, ctx in enumerate(context, 1):
                metadata = ctx.get('metadata', {})
                source = metadata.get('source', 'Unknown')
                doc_id = metadata.get('documentid', 'N/A')
                similarity = ctx.get('similarity', 0.0)
                document = ctx.get('document', '')
                self.logPrint(f"\n\n   {i}. {source} (ID: {doc_id}) (similarity: {similarity:.2%}):\n{document}")

        # 3. Determine if tools needed
        tool_results = []
        if USE_TOOLS:
            if verbose:
                self.logPrint("\n" + "━" * 60)
                self.logPrint(" # 3. Determine if tools needed")
            if analysis.get('requires_tools', False):
                tools = analysis.get('suggested_tools', [])
                for tool_name in tools:
                    result = self.tool_manager.execute_tool(tool_name, query=question)
                    if result.get('success'):
                        tool_results.append(result)
                        if verbose:
                            self.logPrint(f"Needed tool: {tool_name}, Result: {result}")

        # 4. Generate answer
        context_text = self.PromptTemplates.format_context(context)
        prompt = self.PromptTemplates.rag_query_template(context_text, question)
        answer = self.llm_client.generate(
            prompt,
            max_tokens=self.MAX_TOKENS,
            temperature=self.TEMPERATURE
        )

        if verbose:
            self.logPrint("\n" + "━" * 60)
            self.logPrint(f"Generated Answer: {answer}\n")

        # 5. Reflect on answer
        reflection = self.reflection_module.reflect(question, context, answer)
        if reflection.get('issues') and verbose:
            self.logPrint("\n" + "━" * 60)
            self.logPrint(f"⚠ Issues identified: {', '.join(reflection['issues'])}")

        # 6. Self-correct if needed
        if reflection.get('needs_correction', False):
            answer = self.self_correct(question, context, answer, reflection)
            reflection = self.reflection_module.reflect(question, context, answer)
            if verbose:
                self.logPrint("\n" + "━" * 60)
                self.logPrint(f"Answer after self-correction: {answer}\n")

        # 7. Generate LinkedIn post
        post = None
        if generate_linkedin_post:
            if verbose:
                self.logPrint("\n" + "━" * 60)
                self.logPrint("📱 Generating LinkedIn post...")
            try:
                linkedin_prompt = (
                    "Create a LinkedIn post based on the following content.\n"
                    f"Tone: {post_tone}\n"
                    f"Length: {post_length}\n"
                    "Keep it professional, clear, and engaging.\nAlso mention that it was done as final step of Ciklum AI Academy\n\n"
                    f"Content:\n{answer}"
                )
                post = self.post_generator.generate_custom_post(
                    custom_prompt=linkedin_prompt
                )
                if verbose:
                    self.logPrint("\n" + "━" * 60)
                    self.logPrint("📱 LinkedIn Post:")
                    self.logPrint("━" * 60 + "\n")

                    if post:
                        self.logPrint(post + "\n")
                        self.logPrint("━" * 60)
                        self.logPrint(f"Characters: {len(post)}/{self.LINKEDIN_POST_MAX_CHARS}")
                    else:
                        self.logPrint("Generation failed.\n")
                    self.logPrint("")
            except Exception as e:
                if verbose:
                    self.logPrint(f"LinkedIn post generation error: {e}\n")

        if return_post_as_answer and post:
            answer = post

        result = {
            "answer": answer,
            "confidence": reflection.get('confidence', self.CONFIDENCE),
            "sources": [
                {
                    "source": c.get('metadata', {}).get('source', 'Unknown'),
                    "similarity": c.get('similarity', 0.0)
                }
                for c in context
            ]
        }

        if include_reasoning:
            result.update({
                "reasoning": {
                    "intent": analysis.get('intent'),
                    "complexity": analysis.get('complexity'),
                    "key_concepts": analysis.get('key_concepts', [])
                },
                "reflection": {
                    "scores": reflection.get('scores', {}),
                    "issues": reflection.get('issues', [])
                },
                "context_count": len(context),
                "tools_used": [t.get('tool') for t in tool_results]
            })

        return result
