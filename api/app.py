"""
Flask API Backend for the AI-Agentic RAG System.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path because
# when running locally, Python needs to know where to find the src module
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from src.embeddings.vector_store import ChromaVectorStore
from src.embeddings.embedding_generator import OllamaEmbeddings
from src.retrieval.retriever import Retriever
from src.llm.llm_client import OllamaClient
from src.llm.prompt_templates import PromptTemplates
from src.agent.reasoning_engine import ReasoningEngine
from src.agent.tool_manager import ToolManager
from src.agent.reflection_module import ReflectionModule
from src.evaluation.evaluator import Evaluator
from src.config.constants import (
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_OLLAMA_EMBEDDING_MODEL,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_CHROMA_HOST,
    DEFAULT_CHROMA_PORT,
    DEFAULT_CHROMA_COLLECTION_NAME,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_K,
    DEFAULT_INCLUDE_REASONING,
    DEFAULT_CHAT_INCLUDE_REASONING,
    DEFAULT_CONFIDENCE,
    DEFAULT_FLASK_PORT,
    DEFAULT_ANSWER_ERROR_MESSAGE,
)

app = Flask(__name__)
CORS(app)  # Enable CORS for Open WebUI

# Initialize
class RAGAgent:
    """RAG Agent with all components."""

    def __init__(self):
        """Initialize all components."""
        print("Initializing RAG Agent...")

        # Initialize components
        self.vector_store = ChromaVectorStore(
            host=os.getenv("CHROMA_HOST", DEFAULT_CHROMA_HOST),
            port=int(os.getenv("CHROMA_PORT", DEFAULT_CHROMA_PORT)),
            collection_name=os.getenv("CHROMA_COLLECTION_NAME", DEFAULT_CHROMA_COLLECTION_NAME)
        )

        self.embeddings = OllamaEmbeddings(
            base_url=os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL),
            model=os.getenv("OLLAMA_EMBEDDING_MODEL", DEFAULT_OLLAMA_EMBEDDING_MODEL)
        )

        self.retriever = Retriever(self.vector_store, self.embeddings)

        self.llm_client = OllamaClient(
            base_url=os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL),
            model=os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
        )

        self.reasoning_engine = ReasoningEngine(self.llm_client)
        self.tool_manager = ToolManager()
        self.reflection_module = ReflectionModule(self.llm_client)
        self.evaluator = Evaluator()

        print("✓ RAG Agent initialized")

    def process_query(self, question: str, include_reasoning: bool = DEFAULT_INCLUDE_REASONING):
        """
        Process a query through the RAG pipeline.

        Args:
            question: User's question
            include_reasoning: Whether to include reasoning details

        Returns:
            Dictionary with answer and metadata
        """
        try:
            # 1. Analyze query
            analysis = self.reasoning_engine.analyze_query(question)

            # 2. Retrieve context
            context = self.retriever.retrieve(question, top_k=DEFAULT_TOP_K)

            # 3. Determine if tools needed
            tool_results = []
            if analysis.get('requires_tools', False):
                tools = analysis.get('suggested_tools', [])
                for tool_name in tools:
                    result = self.tool_manager.execute_tool(tool_name, query=question)
                    if result.get('success'):
                        tool_results.append(result)

            # 4. Generate answer
            context_text = PromptTemplates.format_context(context)
            prompt = PromptTemplates.rag_query_template(context_text, question)
            answer = self.llm_client.generate(
                prompt,
                max_tokens=int(os.getenv("MAX_TOKENS", DEFAULT_MAX_TOKENS)),
                temperature=float(os.getenv("TEMPERATURE", DEFAULT_TEMPERATURE))
            )

            # 5. Reflect on answer
            reflection = self.reflection_module.reflect(question, context, answer)

            # 6. Self-correct if needed
            if reflection.get('needs_correction', False):
                answer = self.self_correct(question, context, answer, reflection)
                # Re-reflect on corrected answer
                reflection = self.reflection_module.reflect(question, context, answer)

            # Build response
            result = {
                "answer": answer,
                "confidence": reflection.get('confidence', DEFAULT_CONFIDENCE),
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

        except Exception as e:
            return {
                "error": str(e),
                "answer": DEFAULT_ANSWER_ERROR_MESSAGE,
                "confidence": DEFAULT_CONFIDENCE
            }

    def self_correct(self, question, context, answer, reflection):
        """
        Self-correction mechanism.

        Args:
            question: Original question
            context: Retrieved context
            answer: Original answer
            reflection: Reflection results

        Returns:
            Corrected answer
        """
        issues = reflection.get('issues', [])
        if not issues:
            return answer

        context_text = PromptTemplates.format_context(context)
        prompt = PromptTemplates.self_correction_template(
            question=question,
            original_answer=answer,
            issues=', '.join(issues),
            context=context_text
        )

        try:
            corrected_answer = self.llm_client.generate(prompt, max_tokens=DEFAULT_MAX_TOKENS)
            return corrected_answer
        except:
            return answer  # Return original if correction fails


# Initialize agent
print("Starting Flask API...")
agent = RAGAgent()

# Routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        ollama_status = agent.llm_client.test_connection()
        chroma_status = agent.vector_store.get_collection_stats() is not None

        return jsonify({
            "status": "healthy",
            "services": {
                "ollama": ollama_status,
                "chromadb": chroma_status
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint for conversational queries."""
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' in request"}), 400

        message = data['message']
        include_reasoning = data.get('include_reasoning', DEFAULT_CHAT_INCLUDE_REASONING)

        result = agent.process_query(message, include_reasoning)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rag/query', methods=['POST'])
def rag_query():
    """RAG query endpoint with full agent capabilities."""
    try:
        data = request.get_json()
        question = data.get('question')
        include_reasoning = data.get('include_reasoning', DEFAULT_INCLUDE_REASONING)

        if not question:
            return jsonify({"error": "Missing 'question' parameter"}), 400

        result = agent.process_query(question, include_reasoning)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rag/retrieve', methods=['POST'])
def retrieve_context():
    """Retrieve relevant context without generating answer."""
    try:
        data = request.get_json()
        query = data.get('query')
        top_k = data.get('top_k', DEFAULT_TOP_K)

        if not query:
            return jsonify({"error": "Missing 'query' parameter"}), 400

        context = agent.retriever.retrieve(query, top_k=top_k)

        return jsonify({
            "context": context,
            "count": len(context)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    """Evaluate RAG system performance."""
    try:
        data = request.get_json()
        test_questions = data.get('test_questions', [])

        results = []
        for item in test_questions:
            question = item.get('question')
            result = agent.process_query(question, include_reasoning=False)
            results.append({
                "question": question,
                "answer": result.get('answer'),
                "confidence": result.get('confidence', DEFAULT_CONFIDENCE)
            })

        return jsonify({
            "results": results,
            "total": len(results)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    """Get vector store statistics."""
    try:
        stats = agent.vector_store.get_collection_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/models', methods=['GET'])
def list_models():
    """OpenAI-compatible models endpoint required by Open WebUI."""
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": "rag-agent",
                "object": "model",
                "created": 1700000000,
                "owned_by": "local",
                "name": "RAG Agent"
            }
        ]
    }), 200


@app.route('/api/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI-compatible chat completions endpoint for Open WebUI."""
    try:
        data = request.get_json()

        # Extract last user message from OpenAI format
        messages = data.get('messages', [])
        user_message = next(
            (m['content'] for m in reversed(messages) if m['role'] == 'user'),
            None
        )

        if not user_message:
            return jsonify({"error": "No user message found"}), 400

        # Process through your RAG pipeline
        result = agent.process_query(user_message, include_reasoning=False)
        answer = result.get('answer', 'No answer generated')

        # Return in OpenAI-compatible format
        return jsonify({
            "id": "chatcmpl-rag",
            "object": "chat.completion",
            "created": 1700000000,
            "model": "rag-agent",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": answer
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    """API information endpoint."""
    return jsonify({
        "name": "AI-Agentic RAG System API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "rag_query": "/api/rag/query",
            "retrieve": "/api/rag/retrieve",
            "evaluate": "/api/evaluate",
            "stats": "/api/admin/stats"
        }
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', DEFAULT_FLASK_PORT))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'

    print(f"\n{'='*60}")
    print(f"Flask API running on http://0.0.0.0:{port}")
    print(f"{'='*60}\n")

    app.run(host='0.0.0.0', port=port, debug=debug)
