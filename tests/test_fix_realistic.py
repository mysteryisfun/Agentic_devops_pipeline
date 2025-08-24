#!/usr/bin/env python3
"""
Test Fix Agent with real pipeline-like scenario
"""

import os
import sys
import asyncio

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.fix_agent import get_fix_agent
from src.agents.analyze_agent import AnalysisResult

async def test_real_pipeline_scenario():
    """Test with issues that might have lower confidence scores like real analysis"""
    
    print("🧪 Testing Fix Agent with realistic confidence scores...")
    
    # Create analysis result with lower confidence scores (more realistic)
    mock_analysis = AnalysisResult(
        success=True,
        vulnerabilities=[
            {
                "type": "potential_sql_injection", 
                "confidence": 45,  # Lower confidence, realistic
                "filename": "test_file.py",
                "file": "test_file.py",
                "description": "Potential SQL injection vulnerability",
                "line": 42,
                "code_snippet": "query = f'SELECT * FROM users WHERE id = {user_id}'"
            }
        ],
        security_issues=[
            {
                "type": "weak_validation",
                "confidence": 55,  # Lower confidence
                "filename": "auth.py",
                "file": "auth.py", 
                "description": "Weak input validation",
                "line": 15,
                "code_snippet": "if username: return True"
            }
        ],
        quality_issues=[],
        recommendations=["Use parameterized queries", "Strengthen input validation"],
        overall_risk="LOW",
        files_analyzed=2,
        total_issues=2,
        confidence_scores={"sql_injection": 45, "validation": 55}
    )
    
    print(f"📊 Analysis Input:")
    print(f"   Total issues: {mock_analysis.total_issues}")
    print(f"   Vulnerabilities: {len(mock_analysis.vulnerabilities)}")
    print(f"   Security issues: {len(mock_analysis.security_issues)}")
    print(f"   Quality issues: {len(mock_analysis.quality_issues)}")
    
    # Test with current thresholds
    fix_agent = get_fix_agent()
    
    print(f"\n🔧 Testing Fix Agent apply_fixes (dry run mode)...")
    
    # Simulate the pipeline call
    try:
        # This would normally call GitHub API, but we'll catch the error
        fix_result = await fix_agent.apply_fixes(
            analysis_result=mock_analysis,
            repo_name="test/repo", 
            branch="test-branch"
        )
        
        print(f"\n📊 Fix Results:")
        print(f"   Success: {fix_result.success}")
        print(f"   Fixes applied: {fix_result.fixes_applied}")
        print(f"   Files modified: {fix_result.files_modified}")
        print(f"   Errors: {fix_result.errors}")
        
    except Exception as e:
        print(f"❌ Error during fix application: {str(e)}")
        print("   This is expected since we're not calling real GitHub API")

if __name__ == "__main__":
    asyncio.run(test_real_pipeline_scenario())
