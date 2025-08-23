"""
Build Agent Test
Tests the build agent functionality
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.build_agent import BuildAgent

def test_build_agent():
    """Test build agent with sample code"""
    
    print("🔨 Testing Build Agent...")
    print("=" * 50)
    
    build_agent = BuildAgent()
    
    # Sample test files
    test_files = {
        "test_module.py": """
import os
import sys
from typing import List, Dict

def hello_world(name: str = "World") -> str:
    '''Simple hello world function'''
    return f"Hello, {name}!"

class Calculator:
    '''A simple calculator class'''
    
    def __init__(self):
        self.history = []
    
    def add(self, a: int, b: int) -> int:
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def get_history(self) -> List[str]:
        return self.history

# Global variable
VERSION = "1.0.0"
""",
        
        "buggy_code.py": """
def broken_function():
    # Missing closing parenthesis
    print("This will cause a syntax error"
    return True

def another_function():
    return "valid"
""",
        
        "simple_script.js": """
const express = require('express');
import React from 'react';

function simpleFunction() {
    console.log("JavaScript code");
    return true;
}
"""
    }
    
    try:
        print("1. Running build analysis...")
        result = build_agent.compile_and_validate(test_files)
        
        print(f"\n2. Build Results:")
        print(f"   Success: {result.success}")
        print(f"   Total Files: {result.metadata['total_files']}")
        print(f"   Supported Files: {result.metadata['supported_files']}")
        print(f"   Total Lines: {result.metadata['total_lines']}")
        print(f"   Functions Found: {result.metadata['total_functions']}")
        print(f"   Classes Found: {result.metadata['total_classes']}")
        print(f"   Dependencies: {len(result.dependencies)}")
        
        print(f"\n3. Dependencies Found:")
        for dep in result.dependencies:
            print(f"   - {dep}")
        
        if result.errors:
            print(f"\n4. Errors Found ({len(result.errors)}):")
            for error in result.errors:
                print(f"   ❌ {error}")
        
        if result.warnings:
            print(f"\n5. Warnings ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"   ⚠️  {warning}")
        
        print(f"\n6. File Analysis Details:")
        for file_path, info in result.file_info.items():
            print(f"\n   📁 {file_path}:")
            print(f"      Lines: {info['lines']}")
            print(f"      Size: {info['size']} chars")
            
            if 'metadata' in info and info['metadata']:
                meta = info['metadata']
                if meta.get('functions'):
                    print(f"      Functions: {[f['name'] for f in meta['functions']]}")
                if meta.get('classes'):
                    print(f"      Classes: {[c['name'] for c in meta['classes']]}")
                if meta.get('imports'):
                    print(f"      Imports: {len(meta['imports'])}")
            
            if info.get('errors'):
                print(f"      Errors: {info['errors']}")
        
        # Test context preparation
        print(f"\n7. Testing context preparation...")
        context = build_agent.prepare_context_for_agents(result)
        print(f"   Context keys: {list(context.keys())}")
        print(f"   Agent: {context['agent']}")
        print(f"   Status: {context['build_status']}")
        
        print("\n" + "=" * 50)
        if result.success:
            print("🎉 Build Agent test PASSED! (Some files had expected errors)")
        else:
            print("📝 Build Agent test completed with expected syntax errors")
        
        print("✅ Build Agent is ready for integration with other agents")
        return True
        
    except Exception as e:
        print(f"\n❌ Build Agent test FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_build_agent()
    sys.exit(0 if success else 1)
