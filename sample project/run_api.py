"""
Simple start script for the Sample API
Can be used as an alternative entry point
"""

import uvicorn
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the application"""
    print("🚀 Starting Sample API for CI/CD Pipeline Testing...")
    print("📋 Project: FastAPI with CRUD operations and database")
    print("🔧 Build Agent Compatible: ✅")
    print("")
    
    try:
        # Import and run the FastAPI app
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
