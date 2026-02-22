"""
Prompt templates for different agent tasks.
"""


class PromptTemplates:
    """Collection of prompt templates for the RAG agent."""
    
    @staticmethod
    def rag_query_template(context: str, question: str) -> str:
        """
        Template for RAG query with context.
        
        Args:
            context: Retrieved context chunks
            question: User's question
        
        Returns:
            Formatted prompt
        """
        return f"""Context from knowledge base:
{context}

Question: {question}

Instructions: Answer the question based on the provided context. If the answer isn't in the context, say so clearly. Cite sources when possible by referring to the source numbers.

Answer:"""
    
    @staticmethod
    def reasoning_template(task: str, context: str) -> str:
        """
        Template for step-by-step reasoning.
        
        Args:
            task: Task description
            context: Available information
        
        Returns:
            Formatted prompt for reasoning
        """
        return f"""Task: {task}

Available Information:
{context}

Think step-by-step:
1. What information do I have?
2. What information do I need?
3. What actions should I take?
4. What is my confidence level?

Reasoning:"""
    
    @staticmethod
    def reflection_template(question: str, context: str, answer: str) -> str:
        """
        Template for self-reflection on generated answer.
        
        Args:
            question: Original question
            context: Retrieved context
            answer: Generated answer
        
        Returns:
            Formatted prompt for reflection
        """
        return f"""Question: {question}

Retrieved Context:
{context}

Generated Answer: {answer}

Evaluate the answer:
- Relevance: Does the answer address the question? (0-100%)
- Accuracy: Is the answer supported by the context? (0-100%)
- Completeness: Is anything important missing? (0-100%)
- Overall Confidence: How confident are you in this answer? (0-100%)

Provide your evaluation in this format:
Relevance: [score]%
Accuracy: [score]%
Completeness: [score]%
Confidence: [score]%
Issues: [list any problems or concerns]

Evaluation:"""
    
    @staticmethod
    def query_analysis_template(question: str) -> str:
        """
        Template for analyzing user query intent.
        
        Args:
            question: User's question
        
        Returns:
            Formatted prompt for query analysis
        """
        return f"""Analyze this question:
"{question}"

Determine:
1. Intent: What is the user trying to find out?
2. Key concepts: What are the main topics?
3. Complexity: Is this a simple fact lookup or complex reasoning?
4. Tools needed: Does this require any special tools? (search, calculate, compare, summarize)

Provide analysis in JSON format:
{{
    "intent": "...",
    "key_concepts": ["...", "..."],
    "complexity": "simple|medium|complex",
    "requires_tools": true|false,
    "suggested_tools": ["tool1", "tool2"]
}}

Analysis:"""
    
    @staticmethod
    def linkedin_post_template(
        agent_description: str,
        tech_stack: str,
        achievements: str
    ) -> str:
        """
        Template for generating LinkedIn post.
        
        Args:
            agent_description: Description of what the agent does
            tech_stack: Technologies used
            achievements: Key accomplishments
        
        Returns:
            Formatted prompt for LinkedIn post generation
        """
        return f"""Create a professional LinkedIn post about an AI agent I built.

Agent Description: {agent_description}

Technology Stack: {tech_stack}

Key Achievements: {achievements}

Context: This was built as part of the Ciklum AI Academy Engineering Track.

Requirements:
- 5-7 sentences
- Professional but engaging tone
- Mention Ciklum AI Academy
- Highlight technical aspects without being too technical
- Show enthusiasm and learning
- Include 3-5 relevant hashtags at the end

Post:"""
    
    @staticmethod
    def self_correction_template(
        question: str,
        original_answer: str,
        issues: str,
        context: str
    ) -> str:
        """
        Template for self-correction of answers.
        
        Args:
            question: Original question
            original_answer: First generated answer
            issues: Identified problems
            context: Retrieved context
        
        Returns:
            Formatted prompt for correction
        """
        return f"""Question: {question}

Original Answer: {original_answer}

Identified Issues: {issues}

Context:
{context}

Instructions: Generate an improved answer that addresses the identified issues. Make sure the answer is:
- More accurate and supported by context
- More complete
- More relevant to the question

Improved Answer:"""
    
    @staticmethod
    def format_context(context_list: list) -> str:
        """
        Format context chunks for inclusion in prompts.
        
        Args:
            context_list: List of context dictionaries
        
        Returns:
            Formatted context string
        """
        formatted = []
        for i, ctx in enumerate(context_list, 1):
            doc = ctx.get('document', '')
            metadata = ctx.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            
            formatted.append(f"[Source {i} - {source}]:\n{doc}")
        
        return "\n\n".join(formatted)
