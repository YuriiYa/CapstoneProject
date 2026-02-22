"""
Test questions for evaluating the RAG agent.
These questions are based on the knowledge base content.
"""

# Required test questions from the assignment
REQUIRED_QUESTIONS = [
    {
        "question": "What are the production 'Do's' for RAG?",
        "expected_topics": ["production", "best practices", "RAG", "dos"],
        "difficulty": "medium",
        "category": "best_practices"
    },
    {
        "question": "What is the difference between standard retrieval and the ColPali approach?",
        "expected_topics": ["ColPali", "retrieval", "comparison", "standard"],
        "difficulty": "hard",
        "category": "technical_comparison"
    },
    {
        "question": "Why is hybrid search better than vector-only search?",
        "expected_topics": ["hybrid search", "vector search", "advantages", "comparison"],
        "difficulty": "medium",
        "category": "technical_concepts"
    }
]

# Additional test questions for comprehensive evaluation
ADDITIONAL_QUESTIONS = [
    {
        "question": "What databases are recommended for GenAI applications?",
        "expected_topics": ["databases", "GenAI", "recommendations"],
        "difficulty": "easy",
        "category": "databases"
    },
    {
        "question": "Explain the RAG architecture and its main components.",
        "expected_topics": ["RAG", "architecture", "components"],
        "difficulty": "medium",
        "category": "architecture"
    },
    {
        "question": "What are the key considerations for enterprise RAG deployment?",
        "expected_topics": ["enterprise", "deployment", "considerations"],
        "difficulty": "hard",
        "category": "enterprise"
    },
    {
        "question": "How does vector similarity search work?",
        "expected_topics": ["vector", "similarity", "search", "embeddings"],
        "difficulty": "medium",
        "category": "technical_concepts"
    },
    {
        "question": "What are the common challenges in RAG systems?",
        "expected_topics": ["challenges", "RAG", "problems"],
        "difficulty": "medium",
        "category": "challenges"
    },
    {
        "question": "Compare ChromaDB and Qdrant for RAG applications.",
        "expected_topics": ["ChromaDB", "Qdrant", "comparison", "vector database"],
        "difficulty": "hard",
        "category": "technical_comparison"
    },
    {
        "question": "What is chunking and why is it important in RAG?",
        "expected_topics": ["chunking", "RAG", "importance", "text processing"],
        "difficulty": "easy",
        "category": "data_processing"
    }
]

# All test questions combined
ALL_QUESTIONS = REQUIRED_QUESTIONS + ADDITIONAL_QUESTIONS


def get_required_questions():
    """Get the three required test questions."""
    return REQUIRED_QUESTIONS


def get_all_questions():
    """Get all test questions."""
    return ALL_QUESTIONS


def get_questions_by_difficulty(difficulty: str):
    """
    Get questions filtered by difficulty.
    
    Args:
        difficulty: 'easy', 'medium', or 'hard'
    
    Returns:
        List of questions matching the difficulty
    """
    return [q for q in ALL_QUESTIONS if q['difficulty'] == difficulty]


def get_questions_by_category(category: str):
    """
    Get questions filtered by category.
    
    Args:
        category: Category name
    
    Returns:
        List of questions in that category
    """
    return [q for q in ALL_QUESTIONS if q['category'] == category]


if __name__ == "__main__":
    print("Required Test Questions:")
    print("=" * 60)
    for i, q in enumerate(REQUIRED_QUESTIONS, 1):
        print(f"\n{i}. {q['question']}")
        print(f"   Difficulty: {q['difficulty']}")
        print(f"   Category: {q['category']}")
    
    print(f"\n\nTotal Questions: {len(ALL_QUESTIONS)}")
    print(f"Required: {len(REQUIRED_QUESTIONS)}")
    print(f"Additional: {len(ADDITIONAL_QUESTIONS)}")
