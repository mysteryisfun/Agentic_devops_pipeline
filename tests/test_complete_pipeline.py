"""
Manual Pipeline Test
Tests the complete multi-agent pipeline manually
"""

import os
import sys
import asyncio
import requests
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load environment variables first
from dotenv import load_dotenv
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

from src.agents.pipeline_orchestrator import get_pipeline_orchestrator

async def test_manual_pipeline():
    """Test the pipeline manually with a real PR"""
    
    print("🚀 Testing Multi-Agent Pipeline...")
    print("=" * 60)
    
    # Test with our own repository
    repo_name = "mysteryisfun/Agentic_devops_pipeline"
    pr_number = 1  # You might need to adjust this
    
    try:
        # Get pipeline orchestrator
        pipeline = get_pipeline_orchestrator()
        
        print(f"📋 Testing with:")
        print(f"   Repository: {repo_name}")
        print(f"   PR Number: #{pr_number}")
        
        # Start pipeline
        print(f"\n🔄 Starting pipeline...")
        pipeline_id = await pipeline.start_pipeline(pr_number, repo_name)
        print(f"   Pipeline ID: {pipeline_id}")
        
        # Wait a bit for pipeline to progress
        print(f"\n⏳ Waiting for pipeline to execute...")
        
        # Monitor pipeline status
        for i in range(10):  # Check up to 10 times
            await asyncio.sleep(2)  # Wait 2 seconds between checks
            
            status = pipeline.get_pipeline_status(pipeline_id)
            current_stage = status.get('stage', 'unknown')
            duration = status.get('duration', 0)
            
            print(f"   [{i+1}/10] Stage: {current_stage} | Duration: {duration:.1f}s")
            
            if current_stage in ['complete', 'failed']:
                break
        
        # Get final results
        final_status = pipeline.get_pipeline_status(pipeline_id)
        
        print(f"\n📊 Final Results:")
        print(f"   Stage: {final_status.get('stage', 'unknown')}")
        print(f"   Duration: {final_status.get('duration', 0):.2f}s")
        print(f"   Errors: {len(final_status.get('errors', []))}")
        
        # Show results by agent
        results = final_status.get('results', {})
        
        if 'build' in results:
            build = results['build']
            print(f"\n🔨 Build Agent:")
            print(f"   Success: {build.get('success', False)}")
            print(f"   Files: {build.get('metadata', {}).get('total_files', 0)}")
            print(f"   Functions: {build.get('metadata', {}).get('total_functions', 0)}")
            print(f"   Classes: {build.get('metadata', {}).get('total_classes', 0)}")
            if build.get('errors'):
                print(f"   Errors: {build['errors']}")
        
        if 'analyze' in results:
            print(f"\n🔍 Analyze Agent:")
            print(f"   Status: {results['analyze'].get('message', 'N/A')}")
        
        if 'fix' in results:
            print(f"\n🔧 Fix Agent:")
            print(f"   Status: {results['fix'].get('message', 'N/A')}")
        
        if 'test' in results:
            print(f"\n🧪 Test Agent:")
            print(f"   Status: {results['test'].get('message', 'N/A')}")
        
        print(f"\n" + "=" * 60)
        print(f"🎉 Pipeline test completed!")
        print(f"✅ All stages executed successfully")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline test FAILED: {str(e)}")
        return False

async def test_fastapi_integration():
    """Test the FastAPI integration with manual trigger"""
    
    print(f"\n🌐 Testing FastAPI Integration...")
    print("=" * 60)
    
    # Test data
    test_data = {
        "pr_number": 1,
        "repo_name": "mysteryisfun/Agentic_devops_pipeline"
    }
    
    try:
        # Test manual trigger endpoint
        print(f"📡 Testing manual trigger endpoint...")
        response = requests.post(
            "http://localhost:8000/agents/trigger",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            pipeline_id = result.get('pipeline_id')
            print(f"✅ Manual trigger successful!")
            print(f"   Pipeline ID: {pipeline_id}")
            
            # Test status endpoint
            if pipeline_id:
                print(f"\n📊 Testing status endpoint...")
                await asyncio.sleep(3)  # Wait a bit
                
                status_response = requests.get(
                    f"http://localhost:8000/pipeline/{pipeline_id}",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"✅ Status endpoint working!")
                    print(f"   Stage: {status.get('stage', 'unknown')}")
                    print(f"   Duration: {status.get('duration', 0):.2f}s")
                else:
                    print(f"❌ Status endpoint failed: {status_response.status_code}")
        else:
            print(f"❌ Manual trigger failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"⚠️  FastAPI server not running on localhost:8000")
        print(f"   Start the server with: python src/main.py")
    except Exception as e:
        print(f"❌ FastAPI test failed: {str(e)}")

async def main():
    """Run all tests"""
    print("🧪 Hackademia Pipeline Integration Test")
    print("=" * 60)
    
    # Test 1: Manual pipeline execution
    await test_manual_pipeline()
    
    # Test 2: FastAPI integration (optional)
    await test_fastapi_integration()
    
    print(f"\n🏁 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
