"""
Simple Fix Agent Test
"""

import sys
sys.path.append('.')

from src.agents.fix_agent import get_fix_agent
from src.agents.analyze_agent import AnalysisResult
import asyncio

async def test_fix_agent_simple():
    print("🧪 Testing Fix Agent - Simple Test")
    
    # Create mock analysis with high-confidence issue
    mock_analysis = AnalysisResult(
        success=True,
        vulnerabilities=[
            {
                "type": "SQL_INJECTION",
                "severity": "HIGH", 
                "confidence": 95,
                "filename": "auth.py",
                "line": 45,
                "description": "SQL injection vulnerability",
                "code_snippet": "cursor.execute(f\"SELECT * FROM users WHERE username='{username}'\")"
            }
        ],
        security_issues=[],
        quality_issues=[],
        recommendations=["Use parameterized queries"],
        overall_risk="HIGH",
        files_analyzed=1,
        total_issues=1,
        confidence_scores={"overall": 0.95}
    )
    
    try:
        fix_agent = get_fix_agent()
        print("✅ Fix Agent initialized successfully")
        
        # Test filtering high-confidence issues
        issues = fix_agent._filter_high_confidence_issues(mock_analysis)
        print(f"📊 High-confidence issues found: {len(issues)}")
        
        if len(issues) > 0:
            print(f"🔧 Issue to fix: {issues[0]['type']} (confidence: {issues[0]['confidence']}%)")
            print("✅ Fix Agent filtering works correctly")
            return True
        else:
            print("❌ No high-confidence issues found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_fix_agent_simple())
    print(f"\n🎯 Test result: {'✅ PASS' if result else '❌ FAIL'}")
