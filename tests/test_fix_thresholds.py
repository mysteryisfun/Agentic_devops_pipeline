#!/usr/bin/env python3
"""
Final Fix Agent validation test
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.fix_agent import get_fix_agent
from src.agents.analyze_agent import AnalysisResult

def test_confidence_thresholds():
    """Test various confidence levels to validate thresholds"""
    
    print("🧪 Testing confidence thresholds...")
    
    test_cases = [
        # Should NOT be fixed (below thresholds)
        {"type": "vuln", "confidence": 30, "should_fix": False},
        {"type": "security", "confidence": 35, "should_fix": False}, 
        {"type": "quality", "confidence": 45, "should_fix": False},
        
        # Should be fixed (above thresholds)
        {"type": "vuln", "confidence": 50, "should_fix": True},
        {"type": "security", "confidence": 45, "should_fix": True},
        {"type": "quality", "confidence": 55, "should_fix": True},
    ]
    
    for i, case in enumerate(test_cases):
        # Create single issue analysis
        if case["type"] == "vuln":
            analysis = AnalysisResult(
                success=True,
                vulnerabilities=[{"confidence": case["confidence"], "filename": f"test{i}.py", "type": "test"}],
                security_issues=[], quality_issues=[], recommendations=[],
                overall_risk="LOW", files_analyzed=1, total_issues=1, confidence_scores={}
            )
        elif case["type"] == "security":
            analysis = AnalysisResult(
                success=True, vulnerabilities=[],
                security_issues=[{"confidence": case["confidence"], "filename": f"test{i}.py", "type": "test"}],
                quality_issues=[], recommendations=[], overall_risk="LOW", files_analyzed=1, total_issues=1, confidence_scores={}
            )
        else:  # quality
            analysis = AnalysisResult(
                success=True, vulnerabilities=[], security_issues=[],
                quality_issues=[{"confidence": case["confidence"], "filename": f"test{i}.py", "type": "test"}],
                recommendations=[], overall_risk="LOW", files_analyzed=1, total_issues=1, confidence_scores={}
            )
        
        # Test filtering
        fix_agent = get_fix_agent()
        fixable = fix_agent._filter_high_confidence_issues(analysis)
        
        is_fixable = len(fixable) > 0
        expected = case["should_fix"]
        status = "✅" if is_fixable == expected else "❌"
        
        print(f"{status} {case['type']} confidence={case['confidence']}% -> fixable={is_fixable} (expected={expected})")
    
    print("\n🎯 Threshold validation complete!")

if __name__ == "__main__":
    test_confidence_thresholds()
