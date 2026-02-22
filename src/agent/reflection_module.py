"""
Reflection module for self-assessment of generated answers.
"""

import re
from typing import Dict, List


class ReflectionModule:
    """
    Reflection module that evaluates answer quality and confidence.
    """
    
    def __init__(self, llm_client):
        """
        Initialize reflection module with LLM client.
        
        Args:
            llm_client: OllamaClient instance
        """
        self.llm = llm_client
    
    def reflect(
        self,
        question: str,
        context: List[Dict],
        answer: str
    ) -> Dict:
        """
        Reflect on the quality of a generated answer.
        
        Args:
            question: Original question
            context: Retrieved context
            answer: Generated answer
        
        Returns:
            Dictionary with reflection results
        """
        from src.llm.prompt_templates import PromptTemplates
        
        # Format context
        context_text = PromptTemplates.format_context(context)
        
        # Generate reflection prompt
        prompt = PromptTemplates.reflection_template(
            question=question,
            context=context_text,
            answer=answer
        )
        
        try:
            reflection_text = self.llm.generate(
                prompt,
                max_tokens=400,
                temperature=0.3
            )
            
            # Parse reflection
            scores = self._parse_reflection(reflection_text)
            
            # Calculate overall confidence
            confidence = self._calculate_confidence(scores)
            
            # Identify issues
            issues = self._extract_issues(reflection_text)
            
            return {
                "confidence": confidence,
                "scores": scores,
                "issues": issues,
                "reflection_text": reflection_text,
                "needs_correction": confidence < 0.7
            }
            
        except Exception as e:
            print(f"Error in reflection: {e}")
            return {
                "confidence": 0.5,
                "scores": {},
                "issues": ["Reflection failed"],
                "reflection_text": "",
                "needs_correction": True
            }
    
    def _parse_reflection(self, reflection_text: str) -> Dict[str, float]:
        """
        Parse reflection scores from text.
        
        Args:
            reflection_text: Reflection output
        
        Returns:
            Dictionary of scores
        """
        scores = {}
        
        # Look for patterns like "Relevance: 85%"
        patterns = {
            'relevance': r'Relevance:\s*(\d+)%',
            'accuracy': r'Accuracy:\s*(\d+)%',
            'completeness': r'Completeness:\s*(\d+)%',
            'confidence': r'Confidence:\s*(\d+)%'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, reflection_text, re.IGNORECASE)
            if match:
                scores[key] = float(match.group(1)) / 100.0
        
        return scores
    
    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """
        Calculate overall confidence from individual scores.
        
        Args:
            scores: Dictionary of individual scores
        
        Returns:
            Overall confidence score (0-1)
        """
        if not scores:
            return 0.5  # Default medium confidence
        
        # Weighted average of scores
        weights = {
            'relevance': 0.3,
            'accuracy': 0.4,
            'completeness': 0.2,
            'confidence': 0.1
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for key, weight in weights.items():
            if key in scores:
                total_score += scores[key] * weight
                total_weight += weight
        
        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0.5
    
    def _extract_issues(self, reflection_text: str) -> List[str]:
        """
        Extract identified issues from reflection.
        
        Args:
            reflection_text: Reflection output
        
        Returns:
            List of issues
        """
        issues = []
        
        # Look for "Issues:" section
        issues_match = re.search(
            r'Issues?:\s*(.+?)(?:\n\n|\Z)',
            reflection_text,
            re.IGNORECASE | re.DOTALL
        )
        
        if issues_match:
            issues_text = issues_match.group(1)
            # Split by newlines or bullet points
            issue_lines = re.split(r'[\n•\-\*]', issues_text)
            issues = [line.strip() for line in issue_lines if line.strip()]
        
        return issues
    
    def assess_context_relevance(
        self,
        question: str,
        context: List[Dict]
    ) -> Dict:
        """
        Assess how relevant the retrieved context is to the question.
        
        Args:
            question: User's question
            context: Retrieved context chunks
        
        Returns:
            Dictionary with relevance assessment
        """
        if not context:
            return {
                "overall_relevance": 0.0,
                "relevant_chunks": 0,
                "total_chunks": 0
            }
        
        # Simple relevance check based on similarity scores
        relevant_chunks = 0
        total_similarity = 0.0
        
        for ctx in context:
            similarity = ctx.get('similarity', 0.0)
            total_similarity += similarity
            
            if similarity >= 0.7:
                relevant_chunks += 1
        
        overall_relevance = total_similarity / len(context) if context else 0.0
        
        return {
            "overall_relevance": overall_relevance,
            "relevant_chunks": relevant_chunks,
            "total_chunks": len(context),
            "average_similarity": overall_relevance
        }
    
    def suggest_improvements(
        self,
        question: str,
        answer: str,
        issues: List[str]
    ) -> List[str]:
        """
        Suggest improvements based on identified issues.
        
        Args:
            question: Original question
            answer: Generated answer
            issues: List of identified issues
        
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        if not issues:
            return suggestions
        
        # Generate suggestions based on common issues
        for issue in issues:
            issue_lower = issue.lower()
            
            if "incomplete" in issue_lower or "missing" in issue_lower:
                suggestions.append("Retrieve more context or expand the answer")
            
            if "not relevant" in issue_lower or "off-topic" in issue_lower:
                suggestions.append("Refine the query and retrieve more focused context")
            
            if "inaccurate" in issue_lower or "incorrect" in issue_lower:
                suggestions.append("Verify answer against context and correct errors")
            
            if "unclear" in issue_lower or "confusing" in issue_lower:
                suggestions.append("Rephrase the answer for better clarity")
        
        return suggestions if suggestions else ["Review and regenerate the answer"]
