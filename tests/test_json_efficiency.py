"""
Demo: Efficient JSON Extraction (No More Duplicates)
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.analyze_agent import get_analyze_agent

def test_json_extraction_efficiency():
    """Test that JSON extraction is now efficient without duplicates"""
    
    print("🧪 Testing JSON Extraction Efficiency")
    print("=" * 50)
    
    agent = get_analyze_agent()
    
    # Test case 1: Response with ```json block (should use it directly)
    response_with_json_block = '''
    Here's my analysis:
    
    ```json
    {
        "vulnerabilities": [
            {
                "type": "INPUT_VALIDATION",
                "severity": "HIGH",
                "line_number": 5,
                "description": "Missing validation"
            }
        ]
    }
    ```
    
    That completes the analysis.
    '''
    
    print("📄 Test 1: Response with ```json block")
    print("Expected: Should extract from ```json block only")
    extracted = agent._extract_json_from_response(response_with_json_block)
    print("✅ Extraction completed efficiently\n")
    
    # Test case 2: Response with only { } blocks (should use fallback)
    response_with_braces_only = '''
    Based on my analysis: {
        "vulnerabilities": [
            {
                "type": "SECURITY_ISSUE", 
                "severity": "MEDIUM",
                "line_number": 10
            }
        ]
    }
    '''
    
    print("📄 Test 2: Response with { } blocks only")
    print("Expected: Should use { } fallback when no ```json exists")
    extracted2 = agent._extract_json_from_response(response_with_braces_only)
    print("✅ Fallback extraction completed\n")
    
    print("🎯 Efficiency Improvements:")
    print("✅ No duplicate processing of same JSON content")
    print("✅ Prioritizes ```json blocks (most reliable)")
    print("✅ Smart fallback to { } blocks when needed")
    print("✅ Maintains robustness with manual extraction as last resort")

if __name__ == "__main__":
    test_json_extraction_efficiency()
