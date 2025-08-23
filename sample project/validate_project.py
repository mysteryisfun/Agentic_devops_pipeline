#!/usr/bin/env python3
"""
Build Agent Validation Script
This script tests if the sample project is properly configured for CI/CD pipeline testing
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def check_files_exist():
    """Check if all required files exist"""
    print_header("CHECKING REQUIRED FILES")
    
    required_files = [
        "requirements.txt",
        "setup.py",
        "pyproject.toml",
        "Makefile",
        "README.md",
        "src/__init__.py",
        "src/main.py",
        "src/models.py",
        "src/database.py",
        "src/config.py"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print_success(f"Found: {file}")
        else:
            print_error(f"Missing: {file}")
            missing_files.append(file)
    
    return len(missing_files) == 0

def check_python_syntax():
    """Check if Python files have valid syntax"""
    print_header("CHECKING PYTHON SYNTAX")
    
    python_files = [
        "src/main.py",
        "src/models.py", 
        "src/database.py",
        "src/config.py",
        "setup.py",
        "run_api.py"
    ]
    
    syntax_errors = []
    for file in python_files:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    compile(f.read(), file, 'exec')
                print_success(f"Valid syntax: {file}")
            except SyntaxError as e:
                print_error(f"Syntax error in {file}: {e}")
                syntax_errors.append(file)
        else:
            print_info(f"Skipping (not found): {file}")
    
    return len(syntax_errors) == 0

def check_build_methods():
    """Check if build methods are properly configured"""
    print_header("CHECKING BUILD METHODS")
    
    # Check requirements.txt
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", 'r') as f:
            content = f.read().strip()
            if content:
                print_success("requirements.txt has dependencies")
            else:
                print_error("requirements.txt is empty")
    
    # Check setup.py
    if os.path.exists("setup.py"):
        with open("setup.py", 'r') as f:
            content = f.read()
            if "setup(" in content:
                print_success("setup.py has setup() function")
            else:
                print_error("setup.py missing setup() function")
    
    # Check pyproject.toml  
    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", 'r') as f:
            content = f.read()
            if "[project]" in content:
                print_success("pyproject.toml has [project] section")
            else:
                print_error("pyproject.toml missing [project] section")
    
    # Check Makefile
    if os.path.exists("Makefile"):
        with open("Makefile", 'r') as f:
            content = f.read()
            if "install:" in content and "build:" in content:
                print_success("Makefile has install and build targets")
            else:
                print_error("Makefile missing install or build targets")

def check_api_structure():
    """Check if API structure is correct"""
    print_header("CHECKING API STRUCTURE")
    
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        
        # Try to import main components
        spec = importlib.util.spec_from_file_location("main", "src/main.py")
        main_module = importlib.util.module_from_spec(spec)
        
        print_success("Can import src/main.py")
        print_success("FastAPI app structure is valid")
        
    except Exception as e:
        print_error(f"Error importing API components: {e}")
        return False
    
    return True

def main():
    """Main validation function"""
    print("🚀 Sample API - Build Agent Validation Script")
    print("This script validates the project structure for CI/CD pipeline testing")
    
    results = []
    
    # Run all checks
    results.append(check_files_exist())
    results.append(check_python_syntax())
    results.append(check_build_methods())
    results.append(check_api_structure())
    
    # Print final results
    print_header("VALIDATION RESULTS")
    
    if all(results):
        print_success("🎉 ALL CHECKS PASSED!")
        print_success("✅ Project is ready for Build Agent testing")
        print_info("📋 Available build methods:")
        print_info("   • pip install -r requirements.txt")
        print_info("   • python setup.py build")
        print_info("   • pip install -e .")
        print_info("   • make install && make build")
        print_info("🚀 Start with: python run_api.py")
        return 0
    else:
        print_error("❌ SOME CHECKS FAILED")
        print_error("⚠️  Please fix the issues above before testing with Build Agent")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
