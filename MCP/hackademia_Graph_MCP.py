#!/usr/bin/env python3
"""
HACKADEMIA MCP Code Graph Demo
Demonstrates querying code graphs using MCP (Model Context Protocol)
"""
import json
import subprocess
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MCPCodeGraphClient:
    def __init__(self, mcp_server_path):
        self.mcp_server_path = mcp_server_path
        
    def query_graph(self, tool_name, **kwargs):
        """Query the MCP Code Graph server using a specific tool"""
        try:
            # Prepare the MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": kwargs
                }
            }
            
            # Set environment variables for the subprocess
            env = os.environ.copy()
            env.update({
                "CODEGPT_API_KEY": os.getenv("CODEGPT_API_KEY", ""),
                "CODEGPT_ORG_ID": os.getenv("CODEGPT_ORG_ID", ""),
                "CODEGPT_GRAPH_ID": os.getenv("CODEGPT_GRAPH_ID", "")
            })
            
            # Validate required environment variables
            required_vars = ["CODEGPT_API_KEY", "CODEGPT_ORG_ID", "CODEGPT_GRAPH_ID"]
            missing_vars = [var for var in required_vars if not env.get(var)]
            
            if missing_vars:
                return {"error": f"Missing required environment variables: {', '.join(missing_vars)}. Please check your .env file."}
            
            # Start the MCP server process
            process = subprocess.Popen(
                ["node", "dist/index.js"],
                cwd=self.mcp_server_path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # Send the request and get response
            request_str = json.dumps(request) + '\n'
            stdout, stderr = process.communicate(input=request_str, timeout=30)
            
            if process.returncode == 0:
                # Parse the response
                lines = stdout.strip().split('\n')
                for line in lines:
                    try:
                        response = json.loads(line)
                        if "result" in response:
                            return response["result"]
                    except json.JSONDecodeError:
                        continue
                        
            return {"error": f"Process failed with return code {process.returncode}", "stderr": stderr}
            
        except subprocess.TimeoutExpired:
            process.kill()
            return {"error": "Request timed out"}
        except Exception as e:
            return {"error": str(e)}

def hackademia_interactive_analysis():
    """Interactive HACKADEMIA code analysis with user input queries"""
    print("🚀 HACKADEMIA - Interactive Code Analysis Using MCP")
    print("=" * 60)
    
    # Initialize MCP client
    mcp_client = MCPCodeGraphClient("E:\\Github-adhi982\\Agentic_devops_pipeline\\MCP\\mcp-code-graph")
    
    # Step 1: List available graphs
    print("\n📊 Step 1: Getting available code graphs...")
    graphs = mcp_client.query_graph("list-graphs")
    
    if "content" in graphs:
        print("✅ Successfully connected to code graph!")
    else:
        print(f"⚠️  Graph connection issue: {graphs}")
    
    print("\n" + "="*60)
    print("🎯 Interactive Query Mode - Enter your own queries!")
    print("Type 'exit' to quit, 'help' for examples")
    print("="*60)
    
    while True:
        print("\n" + "-"*40)
        print("Available MCP Tools:")
        print("1. nodes-semantic-search - Search for code functions/classes")
        print("2. docs-semantic-search - Search documentation")
        print("3. folder-tree-structure - Get folder structure")
        print("4. get-code - Get specific code (needs node_id)")
        print("5. find-direct-connections - Find code dependencies")
        print("-"*40)
        
        # Get user input for tool selection
        tool_choice = input("\n🔧 Select tool (1-5) or type tool name: ").strip()
        
        if tool_choice.lower() in ['exit', 'quit', 'q']:
            print("� Exiting HACKADEMIA analysis. Goodbye!")
            break
        elif tool_choice.lower() == 'help':
            print("\n💡 Example queries:")
            print("• 'authentication login security' - Find auth functions")
            print("• 'api endpoint route handler' - Find API routes")
            print("• 'database SQL query' - Find DB operations")
            print("• 'bug vulnerability error' - Find potential issues")
            print("• 'component react typescript' - Find React components")
            continue
        
        # Map tool choices
        tool_map = {
            '1': 'nodes-semantic-search',
            '2': 'docs-semantic-search', 
            '3': 'folder-tree-structure',
            '4': 'get-code',
            '5': 'find-direct-connections'
        }
        
        selected_tool = tool_map.get(tool_choice, tool_choice)
        
        # Get parameters based on tool
        if selected_tool == 'nodes-semantic-search':
            query = input("🔍 Enter your search query: ").strip()
            if not query:
                continue
            limit = input("📊 Enter limit (default 5): ").strip() or "5"
            try:
                limit = int(limit)
            except:
                limit = 5
            
            print(f"\n🔄 Searching for: '{query}'...")
            result = mcp_client.query_graph(selected_tool, query=query, limit=limit)
            
        elif selected_tool == 'docs-semantic-search':
            query = input("📚 Enter documentation search query: ").strip()
            if not query:
                continue
            
            print(f"\n🔄 Searching documentation for: '{query}'...")
            result = mcp_client.query_graph(selected_tool, query=query)
            
        elif selected_tool == 'folder-tree-structure':
            path = input("📁 Enter folder path (default 'src'): ").strip() or "src"
            
            print(f"\n🔄 Getting structure for: '{path}'...")
            result = mcp_client.query_graph(selected_tool, path=path)
            
        elif selected_tool == 'get-code':
            node_id = input("🎯 Enter node ID: ").strip()
            if not node_id:
                print("❌ Node ID is required for get-code")
                continue
            
            print(f"\n🔄 Getting code for node: '{node_id}'...")
            result = mcp_client.query_graph(selected_tool, node_id=node_id)
            
        elif selected_tool == 'find-direct-connections':
            node_id = input("🔗 Enter node ID for connections: ").strip()
            if not node_id:
                print("❌ Node ID is required for find-direct-connections")
                continue
            
            print(f"\n🔄 Finding connections for node: '{node_id}'...")
            result = mcp_client.query_graph(selected_tool, node_id=node_id)
            
        else:
            print(f"❌ Unknown tool: {selected_tool}")
            continue
        
        # Display results
        if "content" in result:
            print("✅ Results found:")
            content = result["content"][0]["text"] if result["content"] else "No content"
            
            # Show first 1000 characters, ask if user wants to see more
            if len(content) > 1000:
                print(content[:1000] + "...")
                show_more = input("\n📖 Show full result? (y/n): ")

                if show_more in ['y', 'yes']:
                    print("\n" + "="*60)
                    print(content)
                    print("="*60)
            else:
                print(content)
        else:
            print(f"❌ Error or no results: {result}")
        
        # Ask if user wants to continue
        continue_analysis = input("\n🔄 Continue analysis? (y/n): ").strip().lower()
        if continue_analysis not in ['y', 'yes', '']:
            break
    
    print("\n✅ Interactive Analysis Complete!")
    print("🎯 Summary: Successfully used MCP to query your repository interactively!")
    print("🔄 Next: Use these insights for automated vulnerability detection!")
    
    # Initialize MCP client
    mcp_client = MCPCodeGraphClient("E:\\Github-adhi982\\Agentic_devops_pipeline\\MCP\\mcp-code-graph")
    
    # Step 1: List available graphs
    print("\n📊 Step 1: Getting available code graphs...")
    graphs = mcp_client.query_graph("list-graphs")
    
    if "content" in graphs:
        print("✅ Successfully connected to code graph!")
    else:
        print(f"⚠️  Graph connection issue: {graphs}")
    
    # Step 2: Search for security-sensitive functions
    print("\n🔍 Step 2: Searching for security-sensitive code...")
    security_search = mcp_client.query_graph(
        "nodes-semantic-search",
        query="password authentication security validation input sanitization",
        limit=10
    )
    
    if "content" in security_search:
        print("✅ Found security-related functions:")
        content = security_search["content"][0]["text"] if security_search["content"] else "No content"
        print(content[:500] + "..." if len(content) > 500 else content)
    
    # Step 3: Search for API endpoints
    print("\n🌐 Step 3: Searching for API endpoints and routes...")
    api_search = mcp_client.query_graph(
        "nodes-semantic-search", 
        query="api endpoint route handler express fastapi",
        limit=5
    )
    
    if "content" in api_search:
        print("✅ Found API-related code:")
        content = api_search["content"][0]["text"] if api_search["content"] else "No content"
        print(content[:500] + "..." if len(content) > 500 else content)
    
    # Step 4: Search for database operations
    print("\n💾 Step 4: Searching for database operations...")
    db_search = mcp_client.query_graph(
        "nodes-semantic-search",
        query="database query SQL injection mongodb prisma",
        limit=5
    )
    
    if "content" in db_search:
        print("✅ Found database-related code:")
        content = db_search["content"][0]["text"] if db_search["content"] else "No content"
        print(content[:500] + "..." if len(content) > 500 else content)
    
    # Step 5: Get repository structure
    print("\n📁 Step 5: Getting repository folder structure...")
    folder_structure = mcp_client.query_graph(
        "folder-tree-structure",
        path="src"
    )
    
    if "content" in folder_structure:
        print("✅ Repository structure:")
        content = folder_structure["content"][0]["text"] if folder_structure["content"] else "No content"
        print(content)
    
    # Step 6: Search for documentation
    print("\n� Step 6: Searching documentation for security guidelines...")
    docs_search = mcp_client.query_graph(
        "docs-semantic-search",
        query="security authentication authorization best practices"
    )
    
    if "content" in docs_search:
        print("✅ Found security documentation:")
        content = docs_search["content"][0]["text"] if docs_search["content"] else "No content"
        print(content[:500] + "..." if len(content) > 500 else content)
    
    print("\n✅ Real Code Analysis Complete!")
    print("\n🎯 Summary: Successfully analyzed ADmyBRAND_AI repository for:")
    print("   • Security-sensitive functions")
    print("   • API endpoints and routes") 
    print("   • Database operations")
    print("   • Repository structure")
    print("   • Security documentation")
    print("\n🔄 Next: Feed this data to Gemini AI for vulnerability detection!")

if __name__ == "__main__":
    hackademia_interactive_analysis()
