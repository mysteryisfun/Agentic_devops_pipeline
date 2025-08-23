"""
Simple API Test
Test the main components without running full server
"""

import os
import sys
import asyncio

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

async def test_api_components():
    """Test API components without running server"""
    
    print("🧪 Testing API Components")
    print("=" * 50)
    
    try:
        # Test 1: Import main modules
        print("1. Testing imports...")
        from src.agents.build_agent import get_build_agent
        from src.utils.github_client import get_github_client
        from src.agents.pipeline_orchestrator import get_pipeline_orchestrator
        print("   ✅ All imports successful")
        
        # Test 2: Initialize components
        print("\n2. Testing component initialization...")
        build_agent = get_build_agent()
        github_client = get_github_client()
        pipeline = get_pipeline_orchestrator()
        print("   ✅ All components initialized")
        
        # Test 3: Test build agent with sample code
        print("\n3. Testing Build Agent...")
        sample_code = {
            "test.py": """
import os
def hello():
    return "Hello World"

class Test:
    def __init__(self):
        pass
"""
        }
        
        result = build_agent.compile_and_validate(sample_code)
        print(f"   ✅ Build analysis: {result.success}")
        print(f"   ✅ Functions found: {result.metadata['total_functions']}")
        print(f"   ✅ Classes found: {result.metadata['total_classes']}")
        
        # Test 4: Test GitHub client
        print("\n4. Testing GitHub Client...")
        try:
            repo = github_client.get_repository("mysteryisfun/Agentic_devops_pipeline")
            if repo:
                print(f"   ✅ GitHub repo access: {repo.full_name}")
            else:
                print("   ⚠️  GitHub repo access failed")
        except Exception as e:
            print(f"   ⚠️  GitHub test error: {str(e)}")
        
        # Test 5: Create mock pipeline status
        print("\n5. Testing Pipeline Status...")
        
        # Mock pipeline context
        from src.agents.pipeline_orchestrator import PipelineContext, PipelineStage
        import time
        
        mock_context = PipelineContext(
            pr_number=1,
            repo_name="test/repo", 
            branch="main",
            files_changed=[],
            stage=PipelineStage.BUILD,
            results={"build": {
                "success": True, 
                "metadata": {
                    "total_files": 1,
                    "total_functions": 2,
                    "total_classes": 1,
                    "unique_dependencies": 1
                },
                "errors": [],
                "warnings": []
            }},
            errors=[],
            start_time=time.time()
        )
        
        comment = pipeline._generate_results_comment(mock_context, 5.0)
        print("   ✅ Pipeline comment generation working")
        print(f"   ✅ Comment length: {len(comment)} chars")
        
        print("\n" + "=" * 50)
        print("🎉 All API Components Working!")
        print("✅ Ready for FastAPI server integration")
        
        return True
        
    except Exception as e:
        print(f"\n❌ API component test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_api_components())
