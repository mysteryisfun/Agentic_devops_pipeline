"""
Test Complete Autonomous Analysis Pipeline
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.analyze_agent import get_analyze_agent

async def test_complete_autonomous_analysis():
    """Test the complete autonomous analysis with real file analysis"""
    
    print("🔬 Testing Complete Autonomous Analysis Pipeline")
    print("=" * 60)
    
    agent = get_analyze_agent()
    
    # Create a realistic test file with vulnerabilities
    test_file_data = {
        "filename": "test_vulnerable_api.py",
        "file_extension": "py",
        "status": "added",
        "added_lines": [
            {"line_number": 1, "content": "@app.route('/api/user/<user_id>')"},
            {"line_number": 2, "content": "def get_user(user_id):"},
            {"line_number": 3, "content": "    # SQL injection vulnerability"},
            {"line_number": 4, "content": "    query = f\"SELECT * FROM users WHERE id = {user_id}\""},
            {"line_number": 5, "content": "    result = db.execute(query)"},
            {"line_number": 6, "content": "    "},
            {"line_number": 7, "content": "    # Command injection vulnerability"},
            {"line_number": 8, "content": "    cmd = request.args.get('cmd', '')"},
            {"line_number": 9, "content": "    os.system(f'echo {cmd}')"},
            {"line_number": 10, "content": "    "},
            {"line_number": 11, "content": "    # Hardcoded secret"},
            {"line_number": 12, "content": "    api_key = 'sk-1234567890abcdef'"},
            {"line_number": 13, "content": "    "},
            {"line_number": 14, "content": "    return jsonify(result)"}
        ],
        "context_lines": []
    }
    
    build_context = {
        "metadata": {"project_type": "flask_api"},
        "dependencies": ["flask", "sqlalchemy", "requests"]
    }
    
    print(f"📄 Analyzing: {test_file_data['filename']}")
    print("💻 Code with multiple vulnerabilities:")
    for line in test_file_data['added_lines']:
        print(f"  {line['line_number']:2d}: {line['content']}")
    
    print("\n🤖 Starting Autonomous Analysis...")
    print("-" * 30)
    
    try:
        # Run the complete analysis with autonomous MCP tool selection
        result = await agent._analyze_single_file(test_file_data, build_context)
        
        print("\n📊 Analysis Results:")
        print("=" * 30)
        
        vulnerabilities = result.get('vulnerabilities', [])
        security_issues = result.get('security_issues', [])
        quality_issues = result.get('quality_issues', [])
        recommendations = result.get('recommendations', [])
        
        print(f"🚨 Vulnerabilities Found: {len(vulnerabilities)}")
        for i, vuln in enumerate(vulnerabilities, 1):
            print(f"  {i}. {vuln.get('type', 'Unknown')}: {vuln.get('description', 'No description')}")
            print(f"     Severity: {vuln.get('severity', 'Unknown')}")
            print(f"     Line: {vuln.get('line_number', 'Unknown')}")
        
        print(f"\n🔒 Security Issues Found: {len(security_issues)}")
        for i, issue in enumerate(security_issues, 1):
            print(f"  {i}. {issue.get('type', 'Unknown')}: {issue.get('description', 'No description')}")
        
        print(f"\n📝 Quality Issues Found: {len(quality_issues)}")
        for i, issue in enumerate(quality_issues, 1):
            print(f"  {i}. {issue.get('type', 'Unknown')}: {issue.get('description', 'No description')}")
        
        print(f"\n💡 Recommendations: {len(recommendations)}")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Verify autonomous tool selection worked
        total_issues = len(vulnerabilities) + len(security_issues) + len(quality_issues)
        
        print(f"\n🎯 Analysis Summary:")
        print(f"   Total Issues Found: {total_issues}")
        print(f"   Autonomous Tool Selection: {'✅ Working' if total_issues > 0 else '❓ Check logs'}")
        
        # Expected vulnerabilities:
        expected_vulns = ["SQL Injection", "Command Injection", "Hardcoded Secret"]
        found_vulns = [v.get('type', '') for v in vulnerabilities]
        
        print(f"\n🧪 Expected vs Found:")
        for expected in expected_vulns:
            found = any(expected.lower() in fv.lower() for fv in found_vulns)
            status = "✅" if found else "❌"
            print(f"   {status} {expected}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_autonomous_analysis())
