"""
Gemini AI Connection Test
Tests Google Gemini API connectivity
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_connection():
    """Test Gemini AI API connection"""
    
    print("🤖 Testing Gemini AI Connection...")
    print("=" * 50)
    
    # Load environment variables
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path)
    
    try:
        # Get API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        print("1. Configuring Gemini API...")
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured")
        
        # Test basic model access
        print("\n2. Testing model access...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Gemini Pro model loaded")
        
        # Test simple generation
        print("\n3. Testing code analysis capability...")
        test_code = """
def hello_world():
    print("Hello, World!")
    return "success"
"""
        
        prompt = f"""
        Analyze this Python code and identify any issues:
        
        {test_code}
        
        Provide a brief analysis in 2-3 sentences.
        """
        
        response = model.generate_content(prompt)
        
        if response and response.text:
            print("✅ Gemini analysis test successful!")
            print(f"Response: {response.text[:200]}...")
        else:
            print("❌ No response from Gemini")
            return False
            
        print("\n" + "=" * 50)
        print("🤖 Gemini AI connection test PASSED!")
        print("Ready to use Gemini for code analysis and fixes.")
        return True
        
    except Exception as e:
        print(f"\n❌ Gemini connection test FAILED: {str(e)}")
        print("\nPossible issues:")
        print("- Invalid Gemini API key")
        print("- API quota exceeded")
        print("- Network connectivity issues")
        return False

if __name__ == "__main__":
    success = test_gemini_connection()
    sys.exit(0 if success else 1)
