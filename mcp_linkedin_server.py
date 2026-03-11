"""
MCP Server for AI-Agentic RAG System.

Exposes the RAG pipeline and LinkedIn post generation as MCP tools.
Can be run as a standalone MCP server (stdio transport) or imported directly
for testing.

Run standalone:
    python mcp_linkedin_server.py
"""

import sys
import logging
import asyncio
from pathlib import Path
from typing import Any

# Make src importable regardless of working directory
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Log to file — mcpo captures subprocess stderr, so file logging is needed
_log_file = project_root / "mcp_server.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(_log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger(__name__)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

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
    LINKEDIN_POST_TONE,
    LINKEDIN_POST_LENGTH,
    LINKEDIN_POST_MAX_CHARS,
    GENERATE_LINKEDIN_POSTS,
    VERBOSE,
)


# ---------------------------------------------------------------------------
# RAG Agent — same structure as app.py RAGAgent, wired for MCP
# ---------------------------------------------------------------------------

class RAGAgentMCP(RAGAgentBase):
    """RAG Agent initialised for use inside the MCP server."""

    def __init__(self):
        self.PromptTemplates = PromptTemplates
        self.TOP_K = TOP_K
        self.MAX_TOKENS = MAX_TOKENS
        self.TEMPERATURE = TEMPERATURE
        self.CONFIDENCE = CONFIDENCE
        self.LINKEDIN_POST_MAX_CHARS = LINKEDIN_POST_MAX_CHARS

        self.vector_store = ChromaVectorStore(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
            collection_name=CHROMA_COLLECTION_NAME,
        )
        self.embeddings = OllamaEmbeddings(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_EMBEDDING_MODEL,
        )
        self.retriever = Retriever(self.vector_store, self.embeddings)
        self.llm_client = OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
        self.reasoning_engine = ReasoningEngine(self.llm_client)
        self.tool_manager = ToolManager()
        self.reflection_module = ReflectionModule(self.llm_client)
        self.post_generator = LinkedInPostGenerator(self.llm_client)

    def self_correct(self, question: str, context, answer: str, reflection: dict) -> str:
        issues = reflection.get("issues", [])
        if not issues:
            return answer
        context_text = PromptTemplates.format_context(context)
        prompt = PromptTemplates.self_correction_template(
            question=question,
            original_answer=answer,
            issues=", ".join(issues),
            context=context_text,
        )
        try:
            return self.llm_client.generate(prompt, max_tokens=MAX_TOKENS)
        except Exception:
            return answer

    def process_query(
        self,
        question: str,
        include_reasoning: bool = INCLUDE_REASONING,
        verbose: bool = VERBOSE,
        generate_linkedin_post: bool = GENERATE_LINKEDIN_POSTS,
        post_tone: str = LINKEDIN_POST_TONE,
        post_length: str = LINKEDIN_POST_LENGTH,
        return_post_as_answer: bool = GENERATE_LINKEDIN_POSTS,
    ) -> dict:
        try:
            return self._process_query_common(
                question=question,
                include_reasoning=include_reasoning,
                verbose=verbose,
                generate_linkedin_post=generate_linkedin_post,
                post_tone=post_tone,
                post_length=post_length,
                return_post_as_answer=return_post_as_answer,
            )
        except Exception as e:
            return {
                "error": str(e),
                "answer": ANSWER_ERROR_MESSAGE,
                "confidence": CONFIDENCE,
            }


# ---------------------------------------------------------------------------
# Lazy singleton — avoids loading models at import time (e.g. during testing)
# ---------------------------------------------------------------------------

_agent: RAGAgentMCP | None = None


def _get_agent() -> RAGAgentMCP:
    global _agent
    if _agent is None:
        logger.info("Initializing RAGAgentMCP...")
        _agent = RAGAgentMCP()
        logger.info("RAGAgentMCP initialized successfully")
    return _agent


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

server = Server("rag-linkedin-agent")

_TOOLS = [
    types.Tool(
        name="rag_query",
        description=(
            "Query the RAG knowledge base. Returns an answer grounded in retrieved "
            "documents together with source references and a confidence score."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question to answer using the knowledge base.",
                },
                "include_reasoning": {
                    "type": "boolean",
                    "description": "Include intent, complexity, and reflection details in the response.",
                    "default": INCLUDE_REASONING,
                },
            },
            "required": ["question"],
        },
    ),
    types.Tool(
        name="generate_linkedin_post",
        description=(
            "Run the full RAG pipeline on a topic and return the result formatted "
            "as a LinkedIn post. Optionally provide agent_description, tech_stack, "
            "and achievements to personalise the post content."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Topic question that drives the RAG knowledge lookup.",
                },
                "agent_description": {
                    "type": "string",
                    "description": "Short description of the AI agent or project.",
                },
                "tech_stack": {
                    "type": "string",
                    "description": "Technologies used (e.g. 'Python, Ollama, ChromaDB').",
                },
                "achievements": {
                    "type": "string",
                    "description": "Key achievements or outcomes to highlight in the post.",
                },
                "tone": {
                    "type": "string",
                    "description": "Post tone: professional | casual | technical.",
                    "default": LINKEDIN_POST_TONE,
                },
                "length": {
                    "type": "string",
                    "description": "Post length: short | medium | long.",
                    "default": LINKEDIN_POST_LENGTH,
                },
            },
        },
    ),
    types.Tool(
        name="generate_custom_linkedin_post",
        description=(
            "Generate a LinkedIn post directly from a custom prompt, bypassing the "
            "RAG pipeline. Use this when you already have content and just need it "
            "formatted as a LinkedIn post."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Custom prompt describing the LinkedIn post to generate.",
                },
            },
            "required": ["prompt"],
        },
    ),
]


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """Return the list of available MCP tools."""
    return _TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """Dispatch a tool call to the appropriate handler."""
    logger.info("Tool called: %s | args: %s", name, arguments)
    agent = _get_agent()

    if name == "rag_query":
        question = arguments["question"]
        include_reasoning = arguments.get("include_reasoning", INCLUDE_REASONING)
        result = agent.process_query(question=question, include_reasoning=include_reasoning)

        if "error" in result:
            logger.error("rag_query failed: %s", result["error"])
            return [types.TextContent(type="text", text=f"Error: {result['error']}")]

        answer = result.get("answer", "No answer generated.")
        confidence = result.get("confidence", CONFIDENCE)
        sources = result.get("sources", [])

        lines = [answer, "", f"Confidence: {confidence:.1%}"]
        if sources:
            lines += ["", "Sources:"]
            for s in sources:
                lines.append(f"  - {s['source']} (similarity: {s['similarity']:.2%})")
        if include_reasoning and "reasoning" in result:
            r = result["reasoning"]
            lines += [
                "",
                "Reasoning:",
                f"  Intent: {r.get('intent')}",
                f"  Complexity: {r.get('complexity')}",
                f"  Key concepts: {', '.join(r.get('key_concepts', []))}",
            ]

        return [types.TextContent(type="text", text="\n".join(lines))]

    elif name == "generate_linkedin_post":
        agent_description = arguments.get("agent_description", "an AI-powered RAG system")
        tech_stack = arguments.get("tech_stack", "Python, Ollama, ChromaDB")
        achievements = arguments.get("achievements", "")
        tone = arguments.get("tone", LINKEDIN_POST_TONE)
        length = arguments.get("length", LINKEDIN_POST_LENGTH)
        question = arguments.get("question", "")

        if not question:
            question = f"Tell me about {agent_description} built with {tech_stack}"
            if achievements:
                question += f". Key achievements: {achievements}"

        result = agent.process_query(
            question=question,
            include_reasoning=INCLUDE_REASONING,
            verbose=VERBOSE,
            generate_linkedin_post=GENERATE_LINKEDIN_POSTS,
            post_tone=tone,
            post_length=length,
            return_post_as_answer=GENERATE_LINKEDIN_POSTS,
        )
        post = result.get("answer", "")
        return [types.TextContent(type="text", text=post or "Post generation failed.")]

    elif name == "generate_custom_linkedin_post":
        prompt = arguments["prompt"]
        post = agent.post_generator.generate_custom_post(custom_prompt=prompt)
        return [types.TextContent(type="text", text=post or "Post generation failed.")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


# ---------------------------------------------------------------------------
# Entry-point: run as a standalone MCP server over stdio
# ---------------------------------------------------------------------------

async def _run_server() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(_run_server())
