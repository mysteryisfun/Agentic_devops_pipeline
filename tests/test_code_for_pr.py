"""
Test Python file with intentional issues for pipeline testing
This file will be used to create a test PR
"""

import os
import sys
# Missing import: from typing import List

def buggy_function(name):
    # Missing type hints
    # Syntax error below (missing closing quote)
    print("Hello, {name}")
    return name.upper()

class TestClass:
    def __init__(self):
        self.data = []
    
    def add_item(self, item):
        # No type hints
        # Potential bug: no validation
        self.data.append(item)
        return len(self.data)
    
    def get_items(self):
        # Should return List[str] but no type hint
        return self.data

# Function with no docstring and poor naming
def calc(a, b):
    return a + b

# Unused import (os is imported but not used)
# Security issue: using eval (if we add it)
def dangerous_eval(code):
    return eval(code)  # This should be flagged as security issue

if __name__ == "__main__":
    # Code that will run
    result = buggy_function("Test")
    print(result)
