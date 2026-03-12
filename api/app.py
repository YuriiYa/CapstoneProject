"""
Flask API Backend for the AI-Agentic RAG System.
"""

import os
import sys
from pathlib import Path

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
    FLASK_PORT,
    ANSWER_ERROR_MESSAGE,
    VERBOSE,
    GENERATE_LINKEDIN_POSTS,
    LINKEDIN_POST_TONE,
    LINKEDIN_POST_LENGTH,
    LINKEDIN_POST_MAX_CHARS
)

app = Flask(__name__)
CORS(app)  # Enable CORS for Open WebUI

# Initialize
class RAGAgent(RAGAgentBase):
    """RAG Agent with all components."""

    def __init__(self):
        super().__init__()


    def process_query(self, question: str,
                      include_reasoning: bool = INCLUDE_REASONING,
                      verbose: bool = VERBOSE,
                      generate_linkedin_post: bool = GENERATE_LINKEDIN_POSTS,
                      post_tone: str = LINKEDIN_POST_TONE,
                      post_length: str = LINKEDIN_POST_LENGTH):
        try:
            return self._process_query_common(
                question=question,
                include_reasoning=include_reasoning,
                verbose=verbose,
                generate_linkedin_post=generate_linkedin_post,
                post_tone=post_tone,
                post_length=post_length,
                return_post_as_answer=generate_linkedin_post
            )
        except Exception as e:
            return {
                "error": str(e),
                "answer": ANSWER_ERROR_MESSAGE,
                "confidence": CONFIDENCE
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
            corrected_answer = self.llm_client.generate(prompt, max_tokens=MAX_TOKENS)
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
        include_reasoning = data.get('include_reasoning', INCLUDE_REASONING)

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
        include_reasoning = data.get('include_reasoning', INCLUDE_REASONING)

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
        top_k = data.get('top_k', TOP_K)

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
                "confidence": result.get('confidence', CONFIDENCE)
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


@app.route('/v1/models', methods=['GET'])
def v1_list_models():
    """OpenAI-compatible /v1/models endpoint required by Open WebUI."""
    return list_models()


@app.route('/v1/chat/completions', methods=['POST'])
def v1_chat_completions():
    """OpenAI-compatible /v1/chat/completions endpoint required by Open WebUI."""
    return chat_completions()


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
    port = FLASK_PORT
    debug = os.getenv('FLASK_ENV', 'production') == 'development'

    print(f"\n{'='*60}")
    print(f"Flask API running on http://0.0.0.0:{port}")
    print(f"{'='*60}\n")

    app.run(host='0.0.0.0', port=port, debug=debug)

