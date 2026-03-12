"""

Configuration constants for the RAG system.

These constants check environment variables first, then fall back to default values.
"""

import os



def get_env_or_default(env_var: str, default_value):
    """

    Get value from environment variable or return default.

    Handles type conversion for int, float, and bool.
    """

    value = os.getenv(env_var)

    if value is None:
        return default_value


    # Type conversion based on default value type

    if isinstance(default_value, bool):

        return value.lower() in ('true', '1', 'yes')

    elif isinstance(default_value, int):
        return int(value)

    elif isinstance(default_value, float):
        return float(value)

    else:
        return value



# Ollama Configuration

OLLAMA_BASE_URL = get_env_or_default("OLLAMA_BASE_URL", "http://localhost:11434")

OLLAMA_EMBEDDING_MODEL = get_env_or_default("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

OLLAMA_MODEL = get_env_or_default("OLLAMA_MODEL", "kwangsuklee/gemma-3-12b-it-Q4_K_M:latest")


# ChromaDB Configuration

CHROMA_HOST = get_env_or_default("CHROMA_HOST", "localhost")

CHROMA_PORT = get_env_or_default("CHROMA_PORT", 8000)

CHROMA_COLLECTION_NAME = get_env_or_default("CHROMA_COLLECTION_NAME", "rag_knowledge_base")


# LLM Generation Parameters

MAX_TOKENS = get_env_or_default("MAX_TOKENS", 600)

TEMPERATURE = get_env_or_default("TEMPERATURE", 0.7)

TOP_P = get_env_or_default("TOP_P", 0.9)

TOP_K = get_env_or_default("TOP_K_RETRIEVAL", 5)


# Retrieval Parameters

SIMILARITY_THRESHOLD = get_env_or_default("SIMILARITY_THRESHOLD", 0.7)


# Text Chunking Parameters

CHUNK_SIZE = get_env_or_default("CHUNK_SIZE", 800)

CHUNK_OVERLAP = get_env_or_default("CHUNK_OVERLAP", 150)


# Application Configuration
INCLUDE_REASONING = get_env_or_default("INCLUDE_REASONING", True)
CONFIDENCE = get_env_or_default("CONFIDENCE", 0.7)
FLASK_PORT = get_env_or_default("FLASK_PORT", 5000)
ANSWER_ERROR_MESSAGE = get_env_or_default("ANSWER_ERROR_MESSAGE", "An error occurred while processing your question.")

# LinkedIn Post Generation
LINKEDIN_POST_TONE = get_env_or_default("LINKEDIN_POST_TONE", "professional") # ["professional", "casual", "technical"]
LINKEDIN_POST_LENGTH = get_env_or_default("LINKEDIN_POST_LENGTH", "medium")
LINKEDIN_POST_MAX_CHARS = get_env_or_default("LINKEDIN_POST_MAX_CHARS", 1300)
VERBOSE = get_env_or_default("VERBOSE", True)
GENERATE_LINKEDIN_POSTS = get_env_or_default("GENERATE_LINKEDIN_POSTS", True)
USE_TOOLS = get_env_or_default("USE_TOOLS", False)

