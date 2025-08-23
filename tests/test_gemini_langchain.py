"""
Gemini AI Connection Test using LangChain
Tests Google Gemini API connectivity through LangChain
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

def test_gemini_langchain_connection():
    """Test Gemini AI API connection via LangChain"""
    
    print("🤖 Testing Gemini AI Connection (LangChain)...")
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
        
        print("1. Configuring LangChain Gemini...")
        # Initialize LangChain Gemini model
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.1
        )
        print("✅ LangChain Gemini model configured")
        
        # Test simple generation
        print("\n2. Testing code analysis capability...")
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
        
        print("   Sending test prompt to Gemini...")
        response = llm.invoke(prompt)
        
        if response and response.content:
            print("✅ Gemini analysis test successful!")
            print(f"Response: {response.content[:200]}...")
        else:
            print("❌ No response from Gemini")
            return False
            
        print("\n" + "=" * 50)
        print("🤖 LangChain Gemini connection test PASSED!")
        print("Ready to use LangChain Gemini for code analysis and fixes.")
        return True
        
    except Exception as e:
        print(f"\n❌ Gemini connection test FAILED: {str(e)}")
        print("\nPossible issues:")
        print("- Invalid Gemini API key")
        print("- API quota exceeded")
        print("- Network connectivity issues")
        print("- LangChain configuration issues")
        return False

if __name__ == "__main__":
    success = test_gemini_langchain_connection()
    sys.exit(0 if success else 1)
