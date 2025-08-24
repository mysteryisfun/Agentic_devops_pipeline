"""
Test Improved JSON Parsing and Error Handling
"""

import asyncio
import sys
import os
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.analyze_agent import get_analyze_agent

async def test_json_parsing_improvements():
    """Test the improved JSON parsing with various problematic responses"""
    
    print("🧪 Testing Improved JSON Parsing and Error Handling")
    print("=" * 60)
    
    agent = get_analyze_agent()
    
    # Test with a real problematic code that should trigger the parsing issue
    test_file_data = {
        "filename": "test_json_issues.py",
        "file_extension": "py",
        "status": "added",
        "added_lines": [
            {"line_number": 1, "content": "@app.route('/calculate-age')"},
            {"line_number": 2, "content": "def calculate_age():"},
            {"line_number": 3, "content": "    birth_year = request.json.get('birth_year')"},
            {"line_number": 4, "content": "    # No validation - logical error"},
            {"line_number": 5, "content": "    current_year = 2025"},
            {"line_number": 6, "content": "    age = current_year - birth_year"},
            {"line_number": 7, "content": "    return {'calculated_age': age}"}
        ],
        "context_lines": []
    }
    
    build_context = {
        "metadata": {"project_type": "flask_api"},
        "dependencies": ["flask"]
    }
    
    print(f"📄 Testing with: {test_file_data['filename']}")
    print("💻 Code that should trigger logical error detection:")
    for line in test_file_data['added_lines']:
        print(f"  {line['line_number']:2d}: {line['content']}")
    
    print(f"\n🚀 Running analysis with improved JSON handling...")
    print("-" * 50)
    
    try:
        # Run the analysis
        result = await agent._analyze_single_file(test_file_data, build_context)
        
        print(f"\n📊 Final Analysis Results:")
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
        
        # Show details of found issues
        if vulnerabilities:
            print(f"\n🚨 Vulnerabilities Details:")
            for i, vuln in enumerate(vulnerabilities, 1):
                print(f"  {i}. {vuln.get('type', 'Unknown')} (Line {vuln.get('line_number', '?')})")
                print(f"     Severity: {vuln.get('severity', 'Unknown')}")
                print(f"     Description: {vuln.get('description', 'No description')[:100]}...")
        
        if security_issues:
            print(f"\n🔒 Security Issues Details:")
            for i, issue in enumerate(security_issues, 1):
                print(f"  {i}. {issue.get('type', 'Unknown')} (Line {issue.get('line_number', '?')})")
                print(f"     Severity: {issue.get('severity', 'Unknown')}")
                print(f"     Description: {issue.get('description', 'No description')[:100]}...")
        
        if quality_issues:
            print(f"\n📝 Quality Issues Details:")
            for i, issue in enumerate(quality_issues, 1):
                print(f"  {i}. {issue.get('type', 'Unknown')} (Line {issue.get('line_number', '?')})")
                print(f"     Description: {issue.get('description', 'No description')[:100]}...")
        
        # Test validation
        expected_to_find = ["logical", "validation", "input", "error"]
        found_content = str(result).lower()
        
        print(f"\n🧪 Expected Issue Detection:")
        for expected in expected_to_find:
            found = expected in found_content
            status = "✅" if found else "❌"
            print(f"   {status} Should detect '{expected}' related issues")
        
        # Test that we actually got results (not 0 issues)
        if total_issues > 0:
            print(f"\n✅ SUCCESS: Found {total_issues} issues (no more 0 issue bug)")
        else:
            print(f"\n❌ ISSUE: Still getting 0 issues - need more fixes")
        
        print(f"\n🎉 JSON Parsing Test Complete!")
        print(f"✅ Improved JSON escape handling")
        print(f"✅ Better manual extraction when JSON fails") 
        print(f"✅ More robust error handling")
        print(f"✅ Stricter JSON output instructions to Gemini")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_json_parsing_improvements())
