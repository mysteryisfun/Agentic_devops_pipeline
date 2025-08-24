"""
Test Fix Agent - AI-Powered Code Fixing
Tests the Fix Agent with mock analysis results
"""

import sys
import os
import asyncio
from typing import Dict, Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.agents.fix_agent import get_fix_agent
from src.agents.analyze_agent import AnalysisResult

async def test_fix_agent():
    """Test Fix Agent with mock analysis results"""
    
    print("🧪 Testing Fix Agent Implementation")
    
    # Create mock analysis result with high-confidence issues
    mock_analysis = AnalysisResult(
        success=True,
        vulnerabilities=[
            {
                "type": "SQL_INJECTION",
                "severity": "HIGH",
                "confidence": 95,
                "filename": "auth.py",
                "line": 45,
                "description": "SQL injection vulnerability - string concatenation used for query construction",
                "code_snippet": "cursor.execute(f\"SELECT * FROM users WHERE username='{username}'\")",
                "recommendation": "Use parameterized queries to prevent SQL injection"
            }
        ],
        security_issues=[
            {
                "type": "WEAK_CRYPTO",
                "severity": "MEDIUM", 
                "confidence": 88,
                "filename": "crypto.py",
                "line": 23,
                "description": "Weak password hashing algorithm MD5 detected",
                "code_snippet": "hashlib.md5(password.encode()).hexdigest()",
                "recommendation": "Use bcrypt or scrypt for password hashing"
            }
        ],
        quality_issues=[
            {
                "type": "CODE_QUALITY",
                "severity": "LOW",
                "confidence": 70,
                "filename": "utils.py", 
                "line": 12,
                "description": "Function too complex",
                "recommendation": "Break down into smaller functions"
            }
        ],
        recommendations=[
            "Implement parameterized queries for all database operations",
            "Upgrade to secure password hashing algorithms",
            "Add input validation for user-controlled data"
        ],
        overall_risk="HIGH",
        files_analyzed=3,
        total_issues=3,
        confidence_scores={"overall": 0.85}
    )
    
    # Mock WebSocket callback
    websocket_messages = []
    
    async def mock_progress_callback(message: Dict[str, Any]):
        websocket_messages.append(message)
        print(f"📡 WebSocket: {message.get('type')} - {message.get('message', '')}")
        if message.get('details'):
            print(f"   Details: {message['details']}")
    
    try:
        # Initialize Fix Agent
        fix_agent = get_fix_agent()
        print("✅ Fix Agent initialized successfully")
        
        # Test with mock data
        repo_name = "mysteryisfun/test-repo"
        branch = "feature/test-fixes"
        
        print(f"\n🔧 Testing Fix Agent with:")
        print(f"   Repository: {repo_name}")
        print(f"   Branch: {branch}")
        print(f"   Issues to fix: {mock_analysis.total_issues}")
        print(f"   High-confidence issues: {len([v for v in mock_analysis.vulnerabilities if v.get('confidence', 0) > 80])}")
        
        # Apply fixes
        fix_result = await fix_agent.apply_fixes(
            analysis_result=mock_analysis,
            repo_name=repo_name,
            branch=branch,
            progress_callback=mock_progress_callback
        )
        
        print(f"\n📊 Fix Results:")
        print(f"   Success: {fix_result.success}")
        print(f"   Fixes Applied: {fix_result.fixes_applied}")
        print(f"   Files Modified: {fix_result.files_modified}")
        print(f"   Commits Made: {fix_result.commits_made}")
        print(f"   Duration: {fix_result.duration:.2f}s")
        
        if fix_result.fixes_summary:
            print(f"\n🔧 Applied Fixes:")
            for fix in fix_result.fixes_summary:
                print(f"   - {fix['filename']}: {fix['summary']} (confidence: {fix.get('confidence', 'unknown')}%)")
        
        if fix_result.errors:
            print(f"\n❌ Errors:")
            for error in fix_result.errors:
                print(f"   - {error}")
        
        print(f"\n📡 WebSocket Messages Sent: {len(websocket_messages)}")
        for i, msg in enumerate(websocket_messages):
            print(f"   {i+1}. {msg['type']}: {msg.get('message', '')}")
        
        return fix_result.success
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_fix_agent_no_issues():
    """Test Fix Agent when no high-confidence issues found"""
    
    print("\n🧪 Testing Fix Agent with no high-confidence issues")
    
    # Create mock analysis result with no high-confidence issues
    mock_analysis = AnalysisResult(
        success=True,
        vulnerabilities=[],
        security_issues=[],
        quality_issues=[
            {
                "type": "CODE_STYLE",
                "severity": "LOW",
                "confidence": 60,  # Below threshold
                "filename": "style.py",
                "description": "Minor style issue"
            }
        ],
        recommendations=[],
        overall_risk="LOW",
        files_analyzed=1,
        total_issues=1,
        confidence_scores={"overall": 0.60}
    )
    
    websocket_messages = []
    
    async def mock_progress_callback(message: Dict[str, Any]):
        websocket_messages.append(message)
        print(f"📡 WebSocket: {message.get('type')} - {message.get('message', '')}")
    
    try:
        fix_agent = get_fix_agent()
        
        fix_result = await fix_agent.apply_fixes(
            analysis_result=mock_analysis,
            repo_name="mysteryisfun/test-repo",
            branch="feature/no-fixes",
            progress_callback=mock_progress_callback
        )
        
        print(f"📊 No-Issues Test Results:")
        print(f"   Success: {fix_result.success}")
        print(f"   Fixes Applied: {fix_result.fixes_applied}")
        print(f"   Should be 0: {fix_result.fixes_applied == 0}")
        
        return fix_result.success and fix_result.fixes_applied == 0
        
    except Exception as e:
        print(f"❌ No-issues test failed: {str(e)}")
        return False

if __name__ == "__main__":
    async def run_tests():
        print("🚀 Starting Fix Agent Tests\n")
        
        # Test 1: Normal operation with issues
        test1_result = await test_fix_agent()
        
        # Test 2: No high-confidence issues
        test2_result = await test_fix_agent_no_issues()
        
        print(f"\n📋 Test Summary:")
        print(f"   Test 1 (With Issues): {'✅ PASS' if test1_result else '❌ FAIL'}")
        print(f"   Test 2 (No Issues): {'✅ PASS' if test2_result else '❌ FAIL'}")
        
        if test1_result and test2_result:
            print(f"\n🎉 All Fix Agent tests passed!")
        else:
            print(f"\n❌ Some tests failed. Check implementation.")
    
    asyncio.run(run_tests())
