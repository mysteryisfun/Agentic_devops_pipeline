"""
Test file for real GitHub PR testing
This file contains intentional issues for the AI pipeline to detect and fix
"""

import os
import sys

def test_function_with_issues(name):
    # Missing type hints
    # Syntax error: missing closing quote
    print("Processing: {name}
    
    # Security issue: using eval
    result = eval(f"len('{name}')")
    
    # Unused variable
    unused_var = "this is not used"
    
    return result

class TestClass:
    def __init__(self):
        # Missing type hints
        self.data = []
    
    def add_data(self, item):
        # No validation
        self.data.append(item)
        return len(self.data)

# Missing main guard
if __name__ == "__main__":
    test_function_with_issues("test")
    print("Done")
