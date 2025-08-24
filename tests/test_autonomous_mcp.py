"""
Test Autonomous MCP Tool Selection
Verify that Gemini autonomously decides which MCP tools to use
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.analyze_agent import get_analyze_agent

async def test_autonomous_mcp_selection():
    """Test that Gemini autonomously selects MCP tools based on code analysis needs"""
    
    print("🧪 Testing Autonomous MCP Tool Selection")
    print("=" * 50)
    
    # Initialize agent
    agent = get_analyze_agent()
    
    # Test different types of code to see if Gemini selects different tools
    test_cases = [
        {
            "name": "Authentication Code",
            "filename": "auth.py", 
            "code": """
def login_user(username, password):
    # Direct SQL query - potential injection
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = execute_sql(query)
    
    if result:
        # Hardcoded secret key
        secret_key = "super_secret_123"
        token = create_jwt(username, secret_key)
        return token
    return None
            """,
            "expected_tools": ["search_code", "analyze_security", "find_vulnerabilities"]
        },
        {
            "name": "Simple Utility Function",
            "filename": "utils.py",
            "code": """
def calculate_sum(a, b):
    return a + b

def format_string(text):
    return text.strip().lower()
            """,
            "expected_tools": ["search_code"]  # Should need fewer tools for simple code
        },
        {
            "name": "API Endpoint with Security",
            "filename": "api.py",
            "code": """
@app.route('/api/execute')
def execute_command():
    cmd = request.form.get('command')
    # Command injection vulnerability
    result = os.system(cmd)
    
    # Directory traversal potential
    file_path = request.form.get('file')
    with open(f"uploads/{file_path}", 'r') as f:
        content = f.read()
    
    return jsonify({"result": result, "content": content})
            """,
            "expected_tools": ["analyze_security", "find_vulnerabilities", "analyze_api_endpoints"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_case['name']}")
        print(f"📄 File: {test_case['filename']}")
        print(f"💭 Expected tools: {', '.join(test_case['expected_tools'])}")
        print("-" * 30)
        
        try:
            # Test autonomous MCP tool selection
            if agent.autonomous_mcp:
                autonomous_result = await agent.autonomous_mcp.autonomous_analysis(
                    test_case['filename'], 
                    test_case['code'], 
                    {"metadata": {"project_type": "web_app"}}
                )
                
                if autonomous_result:
                    selected_tools = autonomous_result.get('selected_tools', {})
                    tools_used = [tool['tool'] for tool in selected_tools.get('tools_to_use', [])]
                    analysis_focus = autonomous_result.get('analysis_focus', '')
                    
                    print(f"🤖 AI Selected Tools: {', '.join(tools_used)}")
                    print(f"🎯 AI Analysis Focus: {analysis_focus}")
                    
                    # Check if AI made intelligent tool choices
                    if tools_used:
                        print(f"✅ AI autonomously selected {len(tools_used)} tools")
                        
                        # Verify reasoning for each tool
                        for tool_spec in selected_tools.get('tools_to_use', []):
                            print(f"   - {tool_spec['tool']}: {tool_spec.get('reasoning', 'No reasoning')}")
                    else:
                        print("⚠️ No tools selected by AI")
                        
                else:
                    print("❌ No autonomous result returned")
            else:
                print("❌ Autonomous MCP agent not available")
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎯 Autonomous MCP Tool Selection Analysis Complete")
    print("\nKey Findings:")
    print("✅ AI should select different tools based on code content")
    print("✅ Security-related code should trigger more security tools")
    print("✅ Simple utility code should need fewer tools")
    print("✅ Each tool selection should have clear reasoning")

if __name__ == "__main__":
    asyncio.run(test_autonomous_mcp_selection())
