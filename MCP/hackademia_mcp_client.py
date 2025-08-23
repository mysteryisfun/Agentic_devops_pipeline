#!/usr/bin/env python3
"""
HACKADEMIA MCP Client Wrapper
A simple interface to use the HACKADEMIA MCP Code Graph functionality in other parts of the project
"""
import os
import sys
from typing import Dict, Any, List, Optional

# Add the current directory to the path to import hackademia_Graph_MCP
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hackademia_Graph_MCP import MCPCodeGraphClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HackademiaMCPWrapper:
    """
    A wrapper class that provides easy-to-use methods for HACKADEMIA MCP functionality
    """
    
    def __init__(self, mcp_server_path: Optional[str] = None):
        """
        Initialize the HACKADEMIA MCP wrapper
        
        Args:
            mcp_server_path: Path to the MCP server. If None, uses default path.
        """
        if mcp_server_path is None:
            # Default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            mcp_server_path = os.path.join(current_dir, "mcp-code-graph")
        
        self.client = MCPCodeGraphClient(mcp_server_path)
        
        # Validate environment variables
        required_vars = ["CODEGPT_API_KEY", "CODEGPT_ORG_ID", "CODEGPT_GRAPH_ID"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}. Please check your .env file.")
    
    def search_code(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search for code functions/classes using semantic search
        
        Args:
            query: Search query (e.g., "authentication login security")
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing search results
        """
        return self.client.query_graph("nodes-semantic-search", query=query, limit=limit)
    
    def search_documentation(self, query: str) -> Dict[str, Any]:
        """
        Search documentation using semantic search
        
        Args:
            query: Search query for documentation
            
        Returns:
            Dictionary containing documentation search results
        """
        return self.client.query_graph("docs-semantic-search", query=query)
    
    def get_folder_structure(self, path: str = "src") -> Dict[str, Any]:
        """
        Get folder structure of the repository
        
        Args:
            path: Folder path to analyze (default: "src")
            
        Returns:
            Dictionary containing folder structure
        """
        return self.client.query_graph("folder-tree-structure", path=path)
    
    def get_code_by_id(self, node_id: str) -> Dict[str, Any]:
        """
        Get specific code by node ID
        
        Args:
            node_id: The node ID of the code to retrieve
            
        Returns:
            Dictionary containing the code
        """
        return self.client.query_graph("get-code", node_id=node_id)
    
    def find_connections(self, node_id: str) -> Dict[str, Any]:
        """
        Find direct connections/dependencies for a code node
        
        Args:
            node_id: The node ID to find connections for
            
        Returns:
            Dictionary containing connections information
        """
        return self.client.query_graph("find-direct-connections", node_id=node_id)
    
    def list_graphs(self) -> Dict[str, Any]:
        """
        List available code graphs
        
        Returns:
            Dictionary containing available graphs
        """
        return self.client.query_graph("list-graphs")
    
    def analyze_security(self, limit: int = 10) -> Dict[str, Any]:
        """
        Analyze repository for security-sensitive code
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing security analysis results
        """
        return self.client.query_graph(
            "nodes-semantic-search",
            query="password authentication security validation input sanitization",
            limit=limit
        )
    
    def analyze_api_endpoints(self, limit: int = 5) -> Dict[str, Any]:
        """
        Analyze repository for API endpoints and routes
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing API endpoint analysis results
        """
        return self.client.query_graph(
            "nodes-semantic-search", 
            query="api endpoint route handler express fastapi",
            limit=limit
        )
    
    def analyze_database_operations(self, limit: int = 5) -> Dict[str, Any]:
        """
        Analyze repository for database operations
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing database operations analysis results
        """
        return self.client.query_graph(
            "nodes-semantic-search",
            query="database query SQL injection mongodb prisma",
            limit=limit
        )
    
    def find_vulnerabilities(self, limit: int = 10) -> Dict[str, Any]:
        """
        Search for potential vulnerabilities in the code
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing vulnerability analysis results
        """
        return self.client.query_graph(
            "nodes-semantic-search",
            query="vulnerability error bug security risk injection",
            limit=limit
        )
    
    def analyze_components(self, framework: str = "react", limit: int = 5) -> Dict[str, Any]:
        """
        Analyze components based on framework
        
        Args:
            framework: Framework to search for (e.g., "react", "vue", "angular")
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing component analysis results
        """
        query = f"{framework} component tsx jsx"
        return self.client.query_graph("nodes-semantic-search", query=query, limit=limit)
    
    def get_content_from_result(self, result: Dict[str, Any]) -> str:
        """
        Extract text content from MCP result
        
        Args:
            result: Result dictionary from MCP query
            
        Returns:
            Extracted text content or error message
        """
        if "content" in result and result["content"]:
            return result["content"][0].get("text", "No content available")
        elif "error" in result:
            return f"Error: {result['error']}"
        else:
            return "No results found"
    
    def comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Perform a comprehensive analysis of the repository
        
        Returns:
            Dictionary containing results from multiple analysis types
        """
        results = {
            "graphs": self.list_graphs(),
            "security": self.analyze_security(),
            "api_endpoints": self.analyze_api_endpoints(),
            "database_operations": self.analyze_database_operations(),
            "vulnerabilities": self.find_vulnerabilities(),
            "folder_structure": self.get_folder_structure(),
            "react_components": self.analyze_components("react")
        }
        
        return results

# Convenience functions for easy import and use
def create_mcp_client(mcp_server_path: Optional[str] = None) -> HackademiaMCPWrapper:
    """
    Create a new HACKADEMIA MCP client
    
    Args:
        mcp_server_path: Path to the MCP server. If None, uses default path.
        
    Returns:
        HackademiaMCPWrapper instance
    """
    return HackademiaMCPWrapper(mcp_server_path)

def quick_security_scan() -> str:
    """
    Perform a quick security scan and return results as text
    
    Returns:
        Security scan results as formatted text
    """
    try:
        client = create_mcp_client()
        result = client.analyze_security()
        return client.get_content_from_result(result)
    except Exception as e:
        return f"Security scan failed: {str(e)}"

def quick_code_search(query: str, limit: int = 5) -> str:
    """
    Perform a quick code search and return results as text
    
    Args:
        query: Search query
        limit: Maximum number of results
        
    Returns:
        Search results as formatted text
    """
    try:
        client = create_mcp_client()
        result = client.search_code(query, limit)
        return client.get_content_from_result(result)
    except Exception as e:
        return f"Code search failed: {str(e)}"

def quick_vulnerability_check() -> str:
    """
    Perform a quick vulnerability check and return results as text
    
    Returns:
        Vulnerability check results as formatted text
    """
    try:
        client = create_mcp_client()
        result = client.find_vulnerabilities()
        return client.get_content_from_result(result)
    except Exception as e:
        return f"Vulnerability check failed: {str(e)}"

# Example usage and testing
if __name__ == "__main__":
    print("🔧 HACKADEMIA MCP Wrapper - Testing Functionality")
    print("=" * 60)
    
    try:
        # Create client
        client = create_mcp_client()
        print("✅ MCP Client created successfully")
        
        # Test connection
        graphs = client.list_graphs()
        print(f"✅ Connection test: {client.get_content_from_result(graphs)[:100]}...")
        
        # Quick security scan
        print("\n🔍 Quick Security Scan:")
        security_result = quick_security_scan()
        print(security_result[:200] + "..." if len(security_result) > 200 else security_result)
        
        # Quick code search
        print("\n📝 Quick Code Search (functions):")
        code_result = quick_code_search("functions", 3)
        print(code_result[:200] + "..." if len(code_result) > 200 else code_result)
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
