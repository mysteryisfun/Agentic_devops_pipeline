"""
Test Simplified Single MCP Tool Approach
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.analyze_agent import get_analyze_agent

async def test_simplified_autonomous_analysis():
    """Test the simplified single MCP tool approach with smart scope detection"""
    
    print("🎯 Testing Simplified Single MCP Tool Approach")
    print("=" * 60)
    
    agent = get_analyze_agent()
    
    # Test cases of different scopes
    test_cases = [
        {
            "name": "Small Change - Simple Function",
            "lines": 3,
            "code": """
def calculate_tax(amount):
    return amount * 0.1
            """,
            "expected_scope": "small",
            "expected_questions": 1-2
        },
        {
            "name": "Medium Change - Auth Function", 
            "lines": 8,
            "code": """
def login_user(username, password):
    query = f"SELECT * FROM users WHERE name='{username}'"
    result = db.execute(query)
    if result and result[0]['password'] == password:
        return create_session_token(username)
    return None
            """,
            "expected_scope": "medium", 
            "expected_questions": 3-4
        },
        {
            "name": "Large Change - Complete API Endpoint",
            "lines": 25,
            "code": """
@app.route('/api/user/<user_id>')
def get_user_data(user_id):
    # SQL injection risk
    query = f"SELECT * FROM users WHERE id = {user_id}"
    user = db.execute(query)
    
    # Command injection risk  
    cmd = request.args.get('export_format', '')
    os.system(f'export_user_data --format {cmd}')
    
    # Hardcoded secret
    api_key = 'secret123'
    
    # Directory traversal risk
    file_path = request.args.get('template', '')
    with open(f'templates/{file_path}', 'r') as f:
        template = f.read()
    
    return render_template_string(template, user=user, api_key=api_key)
            """,
            "expected_scope": "large",
            "expected_questions": 5-6
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['name']}")
        print(f"📏 Lines of code: {test_case['lines']}")
        print(f"🎯 Expected scope: {test_case['expected_scope']}")
        print(f"❓ Expected questions: {test_case['expected_questions']}")
        print("-" * 40)
        
        # Create file data
        file_data = {
            "filename": f"test_case_{i}.py",
            "file_extension": "py",
            "status": "added", 
            "added_lines": [
                {"line_number": j, "content": line.strip()}
                for j, line in enumerate(test_case['code'].strip().split('\n'), 1)
            ],
            "context_lines": []
        }
        
        build_context = {"metadata": {"project_type": "web_app"}}
        
        try:
            if agent.autonomous_mcp:
                # Test just the autonomous MCP part
                result = await agent.autonomous_mcp.autonomous_analysis(
                    file_data['filename'],
                    test_case['code'], 
                    build_context
                )
                
                if result:
                    scope = result.get('scope_assessment', 'unknown')
                    questions = result.get('questions_asked', [])
                    total_context = result.get('total_context_chars', 0)
                    
                    print(f"🎯 AI Scope Assessment: {scope}")
                    print(f"❓ Questions Asked: {len(questions)}")
                    print(f"📊 Context Size: {total_context} chars")
                    
                    # Validate scope detection
                    scope_match = scope == test_case['expected_scope']
                    print(f"✅ Scope Detection: {'Correct' if scope_match else 'Incorrect'}")
                    
                    # Show questions asked
                    for j, q in enumerate(questions, 1):
                        question = q.get('question', 'No question')
                        reasoning = q.get('reasoning', 'No reasoning')
                        print(f"   {j}. {question}")
                        print(f"      💭 {reasoning}")
                    
                    # Validate efficiency  
                    if total_context < 20000:  # Reasonable context budget
                        print(f"✅ Context Efficiency: Good ({total_context} chars)")
                    else:
                        print(f"⚠️ Context Efficiency: High ({total_context} chars)")
                        
                else:
                    print("❌ No autonomous result returned")
            else:
                print("❌ Autonomous MCP agent not available")
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Simplified Single MCP Tool Testing Complete!")
    print("\n📊 Expected Benefits:")
    print("✅ Single tool instead of 7+ tools")
    print("✅ Scope-aware question limits")
    print("✅ Context budget management") 
    print("✅ AI asks specific questions it needs")
    print("✅ No more generic repeated responses")

if __name__ == "__main__":
    asyncio.run(test_simplified_autonomous_analysis())
