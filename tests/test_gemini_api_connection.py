#!/usr/bin/env python3
"""
Test Gemini API Connection for Hackademia Pipeline
This test validates the Gemini API key and connection before implementing AI agents
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def test_gemini_connection():
    """Test basic Gemini API connection"""
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False, "❌ No GEMINI_API_KEY found in environment"
    
    print(f"🔑 Using API Key: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test with a simple prompt
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        test_prompt = """
        Analyze this simple Python code for potential issues:
        
        ```python
        def login(username, password):
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            return execute_query(query)
        ```
        
        Identify security vulnerabilities and provide a brief analysis.
        """
        
        print("🧪 Testing Gemini with code analysis prompt...")
        response = model.generate_content(test_prompt)
        
        if response and response.text:
            print("✅ Gemini API connection successful!")
            print(f"📝 Response preview: {response.text[:200]}...")
            return True, response.text
        else:
            return False, "❌ Empty response from Gemini"
            
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            return False, f"❌ Invalid API Key: {error_msg}"
        else:
            return False, f"❌ Gemini connection failed: {error_msg}"

def test_gemini_code_analysis():
    """Test Gemini's ability to analyze code"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False, "No API key available"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Test with actual vulnerability detection
        vulnerable_code = """
        import os
        import subprocess
        
        def execute_command(user_input):
            # Direct command execution - potential security risk
            result = subprocess.run(user_input, shell=True, capture_output=True)
            return result.stdout
        
        def get_user_data(user_id):
            # SQL injection vulnerability
            query = f"SELECT * FROM users WHERE id = {user_id}"
            return database.execute(query)
        
        def save_file(filename, content):
            # Path traversal vulnerability
            with open(f"uploads/{filename}", "w") as f:
                f.write(content)
        """
        
        analysis_prompt = f"""
        As a security-focused code analyzer, examine this Python code and:
        
        1. Identify ALL security vulnerabilities
        2. Classify severity (HIGH/MEDIUM/LOW)
        3. Suggest specific fixes for each issue
        4. Provide improved code examples
        
        Code to analyze:
        ```python
        {vulnerable_code}
        ```
        
        Format your response as JSON with this structure:
        {{
            "vulnerabilities": [
                {{
                    "function": "function_name",
                    "vulnerability": "type of vulnerability",
                    "severity": "HIGH/MEDIUM/LOW",
                    "description": "detailed description",
                    "line_numbers": [1, 2, 3],
                    "fix_suggestion": "how to fix it",
                    "fixed_code": "improved code example"
                }}
            ],
            "overall_risk": "assessment",
            "recommendations": ["list of recommendations"]
        }}
        """
        
        print("🔍 Testing vulnerability detection capabilities...")
        response = model.generate_content(analysis_prompt)
        
        if response and response.text:
            print("✅ Code analysis test successful!")
            print(f"📋 Analysis result: {response.text[:300]}...")
            return True, response.text
        else:
            return False, "Empty analysis response"
            
    except Exception as e:
        return False, f"Code analysis test failed: {str(e)}"

if __name__ == "__main__":
    print("🚀 GEMINI API CONNECTION TEST")
    print("=" * 50)
    
    # Test 1: Basic connection
    print("\n1️⃣ Testing basic API connection...")
    success, result = test_gemini_connection()
    if not success:
        print(result)
        print("\n❌ Cannot proceed without valid Gemini API key!")
        print("📝 Please update your .env file with a valid GEMINI_API_KEY")
        sys.exit(1)
    
    print(result[:200] + "...")
    
    # Test 2: Code analysis capabilities
    print("\n2️⃣ Testing code analysis capabilities...")
    success, result = test_gemini_code_analysis()
    if success:
        print("✅ Gemini is ready for vulnerability detection!")
    else:
        print(f"⚠️ Code analysis test issue: {result}")
    
    print("\n🎉 Gemini API tests completed!")
    print("🚀 Ready to implement AI agents!")
