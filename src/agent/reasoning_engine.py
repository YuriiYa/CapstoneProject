"""
Reasoning engine for query analysis and chain-of-thought reasoning.
"""

import json
import re
from typing import Dict, List, Optional


class ReasoningEngine:
    """
    Reasoning engine that analyzes queries and performs step-by-step reasoning.
    """
    
    def __init__(self, llm_client):
        """
        Initialize reasoning engine with LLM client.
        
        Args:
            llm_client: OllamaClient instance
        """
        self.llm = llm_client
    
    def analyze_query(self, question: str) -> Dict:
        """
        Analyze user query to understand intent and requirements.
        
        Args:
            question: User's question
        
        Returns:
            Dictionary with query analysis
        """
        from src.llm.prompt_templates import PromptTemplates
        
        prompt = PromptTemplates.query_analysis_template(question)
        
        try:
            response = self.llm.generate(prompt, max_tokens=300, temperature=0.3)
            
            # Try to extract JSON from response
            analysis = self._extract_json(response)
            
            if analysis:
                return analysis
            else:
                # Fallback to simple analysis
                return self._simple_analysis(question)
                
        except Exception as e:
            print(f"Error in query analysis: {e}")
            return self._simple_analysis(question)
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """
        Extract JSON from LLM response.
        
        Args:
            text: Response text
        
        Returns:
            Parsed JSON or None
        """
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return None
    
    def _simple_analysis(self, question: str) -> Dict:
        """
        Simple fallback analysis based on keywords.
        
        Args:
            question: User's question
        
        Returns:
            Basic analysis dictionary
        """
        question_lower = question.lower()
        
        # Detect complexity
        complexity = "simple"
        if any(word in question_lower for word in ["compare", "difference", "versus", "vs"]):
            complexity = "medium"
        if any(word in question_lower for word in ["why", "how", "explain", "analyze"]):
            complexity = "complex"
        
        # Detect if tools might be needed
        requires_tools = False
        suggested_tools = []
        
        if "compare" in question_lower or "difference" in question_lower:
            requires_tools = True
            suggested_tools.append("compare_concepts")
        
        if "example" in question_lower:
            requires_tools = True
            suggested_tools.append("get_examples")
        
        return {
            "intent": "information_retrieval",
            "key_concepts": self._extract_key_concepts(question),
            "complexity": complexity,
            "requires_tools": requires_tools,
            "suggested_tools": suggested_tools
        }
    
    def _extract_key_concepts(self, question: str) -> List[str]:
        """
        Extract key concepts from question.
        
        Args:
            question: User's question
        
        Returns:
            List of key concepts
        """
        # Simple extraction - remove common words
        stop_words = {
            'what', 'is', 'are', 'the', 'a', 'an', 'how', 'why', 'when',
            'where', 'which', 'who', 'does', 'do', 'can', 'could', 'would',
            'should', 'for', 'to', 'of', 'in', 'on', 'at', 'by', 'with'
        }
        
        words = question.lower().replace('?', '').split()
        concepts = [w for w in words if w not in stop_words and len(w) > 3]
        
        return concepts[:5]  # Return top 5 concepts
    
    def reason_step_by_step(self, task: str, context: str) -> Dict:
        """
        Perform chain-of-thought reasoning for a task.
        
        Args:
            task: Task description
            context: Available information
        
        Returns:
            Dictionary with reasoning steps and conclusion
        """
        from src.llm.prompt_templates import PromptTemplates
        
        prompt = PromptTemplates.reasoning_template(task, context)
        
        try:
            response = self.llm.generate(prompt, max_tokens=400, temperature=0.5)
            
            return {
                "reasoning": response,
                "steps": self._extract_steps(response),
                "confidence": self._estimate_confidence(response)
            }
        except Exception as e:
            print(f"Error in reasoning: {e}")
            return {
                "reasoning": "Unable to perform reasoning",
                "steps": [],
                "confidence": 0.0
            }
    
    def _extract_steps(self, reasoning_text: str) -> List[str]:
        """
        Extract reasoning steps from text.
        
        Args:
            reasoning_text: Reasoning output
        
        Returns:
            List of reasoning steps
        """
        # Look for numbered steps
        steps = []
        lines = reasoning_text.split('\n')
        
        for line in lines:
            # Match patterns like "1.", "1)", "Step 1:", etc.
            if re.match(r'^\s*\d+[\.):]', line):
                steps.append(line.strip())
        
        return steps
    
    def _estimate_confidence(self, text: str) -> float:
        """
        Estimate confidence from reasoning text.
        
        Args:
            text: Reasoning text
        
        Returns:
            Confidence score (0-1)
        """
        text_lower = text.lower()
        
        # High confidence indicators
        if any(word in text_lower for word in ["clearly", "definitely", "certain", "confident"]):
            return 0.9
        
        # Low confidence indicators
        if any(word in text_lower for word in ["uncertain", "unclear", "maybe", "possibly", "might"]):
            return 0.5
        
        # Medium confidence (default)
        return 0.7
