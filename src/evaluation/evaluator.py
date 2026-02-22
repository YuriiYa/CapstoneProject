"""
Evaluation system for measuring RAG agent performance.
"""

from typing import Dict, List
import time


class Evaluator:
    """
    Evaluates RAG system performance using various metrics.
    """
    
    def __init__(self):
        """Initialize evaluator."""
        self.results = []
    
    def evaluate_retrieval(
        self,
        query: str,
        retrieved_docs: List[Dict],
        relevant_doc_ids: List[str] = None
    ) -> Dict:
        """
        Evaluate retrieval quality.
        
        Args:
            query: Search query
            retrieved_docs: Retrieved documents
            relevant_doc_ids: Known relevant document IDs (if available)
        
        Returns:
            Dictionary with retrieval metrics
        """
        if not retrieved_docs:
            return {
                "precision": 0.0,
                "recall": 0.0,
                "mrr": 0.0,
                "retrieved_count": 0
            }
        
        metrics = {
            "retrieved_count": len(retrieved_docs),
            "average_similarity": self._calculate_avg_similarity(retrieved_docs)
        }
        
        # If we have ground truth, calculate precision/recall
        if relevant_doc_ids:
            retrieved_ids = [doc.get('id') for doc in retrieved_docs]
            
            # Precision: relevant retrieved / total retrieved
            relevant_retrieved = len(set(retrieved_ids) & set(relevant_doc_ids))
            metrics["precision"] = relevant_retrieved / len(retrieved_ids) if retrieved_ids else 0.0
            
            # Recall: relevant retrieved / total relevant
            metrics["recall"] = relevant_retrieved / len(relevant_doc_ids) if relevant_doc_ids else 0.0
            
            # MRR: Mean Reciprocal Rank
            metrics["mrr"] = self._calculate_mrr(retrieved_ids, relevant_doc_ids)
        
        return metrics
    
    def evaluate_generation(
        self,
        question: str,
        answer: str,
        context: List[Dict],
        expected_answer: str = None
    ) -> Dict:
        """
        Evaluate answer generation quality.
        
        Args:
            question: Original question
            answer: Generated answer
            context: Retrieved context
            expected_answer: Expected answer (if available)
        
        Returns:
            Dictionary with generation metrics
        """
        metrics = {
            "answer_length": len(answer.split()),
            "context_used": len(context),
            "has_answer": len(answer) > 0
        }
        
        # Check if answer references context
        metrics["cites_sources"] = self._check_source_citations(answer)
        
        # Check for uncertainty expressions
        metrics["expresses_uncertainty"] = self._check_uncertainty(answer)
        
        # If expected answer provided, calculate similarity
        if expected_answer:
            metrics["similarity_to_expected"] = self._calculate_text_similarity(
                answer, expected_answer
            )
        
        return metrics
    
    def evaluate_agent(
        self,
        question: str,
        answer: str,
        reasoning: Dict,
        reflection: Dict,
        tools_used: List[str] = None
    ) -> Dict:
        """
        Evaluate agentic capabilities.
        
        Args:
            question: Original question
            answer: Generated answer
            reasoning: Reasoning output
            reflection: Reflection output
            tools_used: List of tools used
        
        Returns:
            Dictionary with agent metrics
        """
        metrics = {
            "has_reasoning": bool(reasoning),
            "has_reflection": bool(reflection),
            "confidence_score": reflection.get('confidence', 0.0) if reflection else 0.0,
            "tools_used_count": len(tools_used) if tools_used else 0,
            "reasoning_steps": len(reasoning.get('steps', [])) if reasoning else 0
        }
        
        # Check if agent identified issues
        if reflection:
            metrics["identified_issues"] = len(reflection.get('issues', []))
            metrics["needs_correction"] = reflection.get('needs_correction', False)
        
        return metrics
    
    def evaluate_end_to_end(
        self,
        test_cases: List[Dict]
    ) -> Dict:
        """
        Evaluate system on multiple test cases.
        
        Args:
            test_cases: List of test case dictionaries with 'question' and optionally 'expected_answer'
        
        Returns:
            Dictionary with aggregate metrics
        """
        results = []
        total_time = 0.0
        
        for test_case in test_cases:
            start_time = time.time()
            
            # This would call the actual RAG agent
            # For now, just record the test case
            result = {
                "question": test_case.get('question'),
                "status": "pending"
            }
            
            elapsed_time = time.time() - start_time
            result["time"] = elapsed_time
            total_time += elapsed_time
            
            results.append(result)
        
        return {
            "total_cases": len(test_cases),
            "results": results,
            "average_time": total_time / len(test_cases) if test_cases else 0.0,
            "total_time": total_time
        }
    
    def _calculate_avg_similarity(self, docs: List[Dict]) -> float:
        """Calculate average similarity score."""
        if not docs:
            return 0.0
        
        similarities = [doc.get('similarity', 0.0) for doc in docs]
        return sum(similarities) / len(similarities)
    
    def _calculate_mrr(
        self,
        retrieved_ids: List[str],
        relevant_ids: List[str]
    ) -> float:
        """Calculate Mean Reciprocal Rank."""
        for i, doc_id in enumerate(retrieved_ids, 1):
            if doc_id in relevant_ids:
                return 1.0 / i
        return 0.0
    
    def _check_source_citations(self, answer: str) -> bool:
        """Check if answer cites sources."""
        citation_patterns = [
            'source', 'according to', 'based on',
            '[', 'reference', 'from the'
        ]
        answer_lower = answer.lower()
        return any(pattern in answer_lower for pattern in citation_patterns)
    
    def _check_uncertainty(self, answer: str) -> bool:
        """Check if answer expresses uncertainty when appropriate."""
        uncertainty_patterns = [
            "i don't know", "not sure", "unclear", "cannot find",
            "not in the context", "no information"
        ]
        answer_lower = answer.lower()
        return any(pattern in answer_lower for pattern in uncertainty_patterns)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity (word overlap).
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score (0-1)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def generate_report(self, results: List[Dict]) -> str:
        """
        Generate evaluation report.
        
        Args:
            results: List of evaluation results
        
        Returns:
            Formatted report string
        """
        report = ["=" * 60]
        report.append("RAG AGENT EVALUATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        if not results:
            report.append("No results to report.")
            return "\n".join(report)
        
        # Calculate aggregate metrics
        total_cases = len(results)
        successful = sum(1 for r in results if r.get('status') == 'success')
        
        report.append(f"Total Test Cases: {total_cases}")
        report.append(f"Successful: {successful}")
        report.append(f"Success Rate: {successful/total_cases*100:.1f}%")
        report.append("")
        
        # Individual results
        report.append("Individual Results:")
        report.append("-" * 60)
        
        for i, result in enumerate(results, 1):
            report.append(f"\n{i}. {result.get('question', 'N/A')}")
            report.append(f"   Status: {result.get('status', 'unknown')}")
            report.append(f"   Time: {result.get('time', 0):.2f}s")
            
            if 'confidence' in result:
                report.append(f"   Confidence: {result['confidence']:.2%}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
