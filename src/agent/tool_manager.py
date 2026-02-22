"""
Tool manager for registering and executing agent tools.
"""

from typing import Dict, List, Callable, Any
import re


class ToolManager:
    """
    Manages tools that the agent can use to perform actions.
    """
    
    def __init__(self):
        """Initialize tool manager with default tools."""
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools available to the agent."""
        
        # Search knowledge base tool
        self.register_tool(
            name="search_knowledge_base",
            function=self._search_kb_placeholder,
            description="Search the knowledge base for relevant information"
        )
        
        # Calculate tool
        self.register_tool(
            name="calculate",
            function=self._calculate,
            description="Perform mathematical calculations"
        )
        
        # Compare concepts tool
        self.register_tool(
            name="compare_concepts",
            function=self._compare_placeholder,
            description="Compare two concepts from the knowledge base"
        )
        
        # Get examples tool
        self.register_tool(
            name="get_examples",
            function=self._examples_placeholder,
            description="Find examples of a concept from the knowledge base"
        )
        
        # Summarize section tool
        self.register_tool(
            name="summarize_section",
            function=self._summarize_placeholder,
            description="Summarize a specific section or topic"
        )
    
    def register_tool(
        self,
        name: str,
        function: Callable,
        description: str
    ):
        """
        Register a new tool.
        
        Args:
            name: Tool name
            function: Function to execute
            description: Tool description
        """
        self.tools[name] = {
            "function": function,
            "description": description
        }
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool parameters
        
        Returns:
            Dictionary with execution results
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "result": None
            }
        
        try:
            tool = self.tools[tool_name]
            result = tool["function"](**kwargs)
            
            return {
                "success": True,
                "error": None,
                "result": result,
                "tool": tool_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": None,
                "tool": tool_name
            }
    
    def execute_tools(self, tool_requests: List[Dict]) -> List[Dict]:
        """
        Execute multiple tools.
        
        Args:
            tool_requests: List of tool execution requests
        
        Returns:
            List of execution results
        """
        results = []
        
        for request in tool_requests:
            tool_name = request.get("tool")
            params = request.get("params", {})
            
            result = self.execute_tool(tool_name, **params)
            results.append(result)
        
        return results
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all available tools.
        
        Returns:
            Dictionary mapping tool names to descriptions
        """
        return {
            name: tool["description"]
            for name, tool in self.tools.items()
        }
    
    def list_tools(self) -> List[str]:
        """
        List all available tool names.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    # Tool implementations
    
    def _search_kb_placeholder(self, query: str) -> str:
        """
        Placeholder for knowledge base search.
        This would be connected to the retriever in actual implementation.
        
        Args:
            query: Search query
        
        Returns:
            Search results
        """
        return f"Searching knowledge base for: {query}"
    
    def _calculate(self, expression: str) -> str:
        """
        Perform mathematical calculation.
        
        Args:
            expression: Mathematical expression
        
        Returns:
            Calculation result
        """
        try:
            # Safe evaluation of mathematical expressions
            # Remove any non-mathematical characters
            safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            result = eval(safe_expr)
            return f"Result: {result}"
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    def _compare_placeholder(self, concept1: str, concept2: str) -> str:
        """
        Placeholder for concept comparison.
        
        Args:
            concept1: First concept
            concept2: Second concept
        
        Returns:
            Comparison result
        """
        return f"Comparing {concept1} and {concept2}"
    
    def _examples_placeholder(self, concept: str) -> str:
        """
        Placeholder for finding examples.
        
        Args:
            concept: Concept to find examples for
        
        Returns:
            Examples
        """
        return f"Finding examples of: {concept}"
    
    def _summarize_placeholder(self, section: str) -> str:
        """
        Placeholder for section summarization.
        
        Args:
            section: Section to summarize
        
        Returns:
            Summary
        """
        return f"Summarizing section: {section}"
