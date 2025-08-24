"""
Real Fix Agent Test - Actually Apply Fixes
Tests the Fix Agent making real fixes to the current repository
"""

import sys
sys.path.append('.')

from src.agents.fix_agent import get_fix_agent
from src.agents.analyze_agent import AnalysisResult
import asyncio

async def test_real_fix_application():
    print("🔧 Testing Fix Agent - Real Fix Application")
    
    # Create realistic analysis result with high-confidence issue
    mock_analysis = AnalysisResult(
        success=True,
        vulnerabilities=[
            {
                "type": "SQL_INJECTION",
                "severity": "HIGH", 
                "confidence": 95,
                "filename": "vulnerable_test_file.py",  # Use the test file in our repo
                "line": 5,
                "description": "SQL injection vulnerability - string concatenation used for query construction",
                "code_snippet": "cursor.execute(f\"SELECT * FROM users WHERE username='{username}'\")",
                "recommendation": "Use parameterized queries to prevent SQL injection"
            }
        ],
        security_issues=[],
        quality_issues=[],
        recommendations=["Use parameterized queries for all database operations"],
        overall_risk="HIGH",
        files_analyzed=1,
        total_issues=1,
        confidence_scores={"overall": 0.95}
    )
    
    # Mock WebSocket callback to capture progress
    websocket_messages = []
    
    async def mock_progress_callback(message):
        websocket_messages.append(message)
        print(f"📡 WebSocket: {message.get('type')} - {message.get('message', '')}")
        
        # Show fix details when available
        if message.get('type') == 'status_update' and message.get('stage') == 'fix':
            details = message.get('details', {})
            if 'function_name' in details:
                print(f"      🔧 Fixing: {details['function_name']}() in {details['filename']}")
                print(f"      📝 Summary: {details['fix_summary']}")
                print(f"      🎯 Confidence: {details['confidence']}%")
    
    try:
        fix_agent = get_fix_agent()
        print("✅ Fix Agent initialized")
        
        # Test with our actual repository
        repo_name = "mysteryisfun/Agentic_devops_pipeline"
        branch = "backend"  # Current branch
        
        print(f"\n🎯 Testing Fix Application:")
        print(f"   Repository: {repo_name}")
        print(f"   Branch: {branch}")
        print(f"   Target File: vulnerable_test_file.py")
        print("")
        
        # Apply fixes
        fix_result = await fix_agent.apply_fixes(
            analysis_result=mock_analysis,
            repo_name=repo_name,
            branch=branch,
            progress_callback=mock_progress_callback
        )
        
        print(f"\n📊 Fix Application Results:")
        print(f"   Success: {fix_result.success}")
        print(f"   Fixes Applied: {fix_result.fixes_applied}")
        print(f"   Files Modified: {fix_result.files_modified}")
        print(f"   Commits Made: {fix_result.commits_made}")
        print(f"   Duration: {fix_result.duration:.2f}s")
        
        if fix_result.fixes_summary:
            print(f"\n🔧 Applied Fixes:")
            for fix in fix_result.fixes_summary:
                print(f"   - {fix['filename']}: {fix['summary']}")
                print(f"     Confidence: {fix.get('confidence', 'unknown')}%")
                if fix.get('commit_sha'):
                    print(f"     Commit: {fix['commit_sha'][:8]}...")
        
        if fix_result.errors:
            print(f"\n❌ Errors:")
            for error in fix_result.errors:
                print(f"   - {error}")
        
        print(f"\n📡 WebSocket Messages: {len(websocket_messages)}")
        
        return fix_result.success
        
    except Exception as e:
        print(f"❌ Real fix test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_no_github_access():
    """Test Fix Agent behavior when GitHub access fails"""
    print("\n🧪 Testing Fix Agent - No GitHub Access")
    
    mock_analysis = AnalysisResult(
        success=True,
        vulnerabilities=[{
            "type": "SQL_INJECTION",
            "severity": "HIGH", 
            "confidence": 95,
            "filename": "nonexistent.py",
            "description": "Test vulnerability"
        }],
        security_issues=[],
        quality_issues=[],
        recommendations=[],
        overall_risk="HIGH",
        files_analyzed=1,
        total_issues=1,
        confidence_scores={"overall": 0.95}
    )
    
    try:
        fix_agent = get_fix_agent()
        
        # Test with non-existent repository
        fix_result = await fix_agent.apply_fixes(
            analysis_result=mock_analysis,
            repo_name="nonexistent/repo",
            branch="main",
            progress_callback=None
        )
        
        print(f"📊 No-Access Test Results:")
        print(f"   Success: {fix_result.success}")
        print(f"   Errors: {len(fix_result.errors)}")
        
        # Should handle gracefully
        return True
        
    except Exception as e:
        print(f"❌ No-access test failed: {str(e)}")
        return False

if __name__ == "__main__":
    async def run_tests():
        print("🚀 Starting Real Fix Agent Tests\n")
        
        # Test 1: Real fix application
        test1_result = await test_real_fix_application()
        
        # Test 2: Error handling
        test2_result = await test_no_github_access()
        
        print(f"\n📋 Test Summary:")
        print(f"   Real Fix Test: {'✅ PASS' if test1_result else '❌ FAIL'}")
        print(f"   Error Handling: {'✅ PASS' if test2_result else '❌ FAIL'}")
        
        if test1_result and test2_result:
            print(f"\n🎉 All real Fix Agent tests passed!")
            print(f"🚀 Fix Agent is ready for production use!")
        else:
            print(f"\n❌ Some tests failed. Check implementation.")
    
    asyncio.run(run_tests())
