#!/usr/bin/env python3
"""
Debug test for Fix Agent - check what's happening with filtering
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.fix_agent import get_fix_agent
from src.agents.analyze_agent import AnalysisResult

def test_fix_filtering():
    """Test the fix agent filtering with mock data that should pass"""
    
    print("🧪 Testing Fix Agent filtering logic...")
    
    # Create mock analysis result with issues that should pass the filter
    mock_analysis = AnalysisResult(
        success=True,
        vulnerabilities=[
            {
                "type": "sql_injection", 
                "confidence": 75,  # Should pass 60% threshold
                "filename": "test_file.py",
                "file": "test_file.py",  # backup field
                "description": "SQL injection vulnerability",
                "line": 42
            }
        ],
        security_issues=[
            {
                "type": "hardcoded_secret",
                "confidence": 70,  # Should pass 60% threshold  
                "filename": "config.py",
                "file": "config.py",
                "description": "Hardcoded API key",
                "line": 15
            }
        ],
        quality_issues=[
            {
                "type": "code_duplication",
                "confidence": 80,  # Should pass 65% threshold
                "filename": "utils.py", 
                "file": "utils.py",
                "description": "Duplicate code block",
                "line": 25
            }
        ],
        recommendations=[],
        overall_risk="MEDIUM",
        files_analyzed=3,
        total_issues=3,
        confidence_scores={}
    )
    
    # Test filtering
    fix_agent = get_fix_agent()
    fixable_issues = fix_agent._filter_high_confidence_issues(mock_analysis)
    
    print(f"\n📊 Results:")
    print(f"   Total issues in analysis: {mock_analysis.total_issues}")
    print(f"   Fixable issues found: {len(fixable_issues)}")
    
    for i, issue in enumerate(fixable_issues):
        print(f"   Issue {i+1}: {issue.get('type')} - {issue.get('filename')} (confidence: {issue.get('confidence')}%)")
    
    # Expected: Should find 3 fixable issues
    if len(fixable_issues) == 3:
        print("✅ Filtering logic working correctly!")
        return True
    else:
        print(f"❌ Expected 3 fixable issues, got {len(fixable_issues)}")
        return False

if __name__ == "__main__":
    test_fix_filtering()
