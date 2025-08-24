"""
Test Enhanced Autonomous MCP with Generic Query Tool
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.analyze_agent import get_analyze_agent

async def test_enhanced_autonomous_analysis():
    """Test the enhanced autonomous analysis with generic query tool and response printing"""
    
    print("🚀 Testing Enhanced Autonomous MCP with Generic Query Tool")
    print("=" * 70)
    
    agent = get_analyze_agent()
    
    # Test with code that should trigger specific questions
    test_file_data = {
        "filename": "suspicious_auth.py",
        "file_extension": "py", 
        "status": "added",
        "added_lines": [
            {"line_number": 1, "content": "import hashlib"},
            {"line_number": 2, "content": "from database import execute_query  # Where is this from?"},
            {"line_number": 3, "content": "from utils.crypto import encrypt_password  # Custom crypto?"},
            {"line_number": 4, "content": ""},
            {"line_number": 5, "content": "def authenticate_user(username, password):"},
            {"line_number": 6, "content": "    # Is this the only auth method?"},
            {"line_number": 7, "content": "    hashed = hashlib.md5(password.encode()).hexdigest()"},
            {"line_number": 8, "content": "    query = f\"SELECT * FROM users WHERE username='{username}' AND password_hash='{hashed}'\""},
            {"line_number": 9, "content": "    result = execute_query(query)"},
            {"line_number": 10, "content": "    "},
            {"line_number": 11, "content": "    if result:"},
            {"line_number": 12, "content": "        # What other sensitive operations happen here?"},
            {"line_number": 13, "content": "        session_token = encrypt_password(f'{username}:{password}')"},
            {"line_number": 14, "content": "        return session_token"},
            {"line_number": 15, "content": "    return None"}
        ],
        "context_lines": []
    }
    
    build_context = {
        "metadata": {"project_type": "authentication_service"},
        "dependencies": ["flask", "hashlib", "custom_crypto"]
    }
    
    print(f"📄 Analyzing: {test_file_data['filename']}")
    print("💻 Code with suspicious patterns and imports:")
    for line in test_file_data['added_lines']:
        print(f"  {line['line_number']:2d}: {line['content']}")
    
    print(f"\n🤖 This code should trigger specific questions like:")
    print(f"   - 'Where is execute_query imported from?'")
    print(f"   - 'How does encrypt_password work?'")
    print(f"   - 'Are there other authentication methods?'")
    print(f"   - 'What other sensitive operations use similar patterns?'")
    
    print("\n🚀 Starting Enhanced Autonomous Analysis...")
    print("-" * 50)
    
    try:
        # Run the complete analysis
        result = await agent._analyze_single_file(test_file_data, build_context)
        
        print("\n📊 Final Analysis Results:")
        print("=" * 40)
        
        vulnerabilities = result.get('vulnerabilities', [])
        security_issues = result.get('security_issues', [])
        quality_issues = result.get('quality_issues', [])
        recommendations = result.get('recommendations', [])
        
        total_issues = len(vulnerabilities) + len(security_issues) + len(quality_issues)
        
        print(f"🎯 Total Issues Found: {total_issues}")
        print(f"   🚨 Vulnerabilities: {len(vulnerabilities)}")
        print(f"   🔒 Security Issues: {len(security_issues)}")
        print(f"   📝 Quality Issues: {len(quality_issues)}")
        print(f"   💡 Recommendations: {len(recommendations)}")
        
        # Check if we got good analysis
        expected_issues = ["MD5", "SQL", "injection", "weak", "hashing"]
        found_issues = str(result).lower()
        
        print(f"\n🧪 Analysis Quality Check:")
        for issue in expected_issues:
            found = issue in found_issues
            status = "✅" if found else "❌"
            print(f"   {status} Detected '{issue}' related issues")
        
        print(f"\n🎉 Enhanced Autonomous Analysis Complete!")
        print(f"✅ Generic query tool should enable more targeted exploration")
        print(f"✅ Response printing should show what MCP tools return")
        print(f"✅ AI should ask specific questions about imports and patterns")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_autonomous_analysis())
