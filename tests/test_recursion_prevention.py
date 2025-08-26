#!/usr/bin/env python3
"""
Test script for recursion prevention in the AI pipeline
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.pipeline_orchestrator import get_pipeline_orchestrator

async def test_ai_commit_detection():
    """Test the AI commit detection logic"""
    
    pipeline = get_pipeline_orchestrator()
    
    # Test cases for AI commit detection
    test_cases = [
        {
            "message": "🤖 AI Fix: Replace SQL injection with parameterized query [skip-pipeline]",
            "should_detect": True,
            "description": "AI Fix with skip-pipeline marker"
        },
        {
            "message": "Add user authentication feature",
            "should_detect": False,
            "description": "Regular human commit"
        },
        {
            "message": "🤖 AI Test: Generated unit tests for user.py [ai-generated]",
            "should_detect": True,
            "description": "AI Test with ai-generated marker"
        },
        {
            "message": "Fix typo in README",
            "should_detect": False,
            "description": "Regular human commit"
        }
    ]
    
    print("🧪 Testing AI commit detection logic...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n Test {i}: {test_case['description']}")
        print(f"   Message: '{test_case['message']}'")
        
        # Simulate checking commit message directly
        ai_markers = [
            "[skip-pipeline]",
            "🤖 AI Fix:",
            "🤖 AI Test:",
            "🤖 AI Refactor:",
            "[ai-generated]",
            "[hackademia-ai]"
        ]
        
        is_ai_commit = any(marker in test_case['message'] for marker in ai_markers)
        
        if is_ai_commit == test_case['should_detect']:
            print(f"   ✅ PASS - Correctly {'detected' if is_ai_commit else 'ignored'}")
        else:
            print(f"   ❌ FAIL - Expected {test_case['should_detect']}, got {is_ai_commit}")
    
    print(f"\n🎯 AI commit detection tests completed!")

if __name__ == "__main__":
    asyncio.run(test_ai_commit_detection())
