"""
Test Complete Pipeline with Fix Agent
Tests the full Build -> Analyze -> Fix pipeline flow
"""

import sys
import os
import asyncio
from typing import Dict, Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.agents.pipeline_orchestrator import get_pipeline_orchestrator

async def test_complete_pipeline_with_fixes():
    """Test complete pipeline including Fix Agent"""
    
    print("🚀 Testing Complete Pipeline with Fix Agent")
    
    # Mock WebSocket callback to capture all messages
    websocket_messages = []
    
    class MockWebSocketManager:
        async def send_message(self, pipeline_id: str, message: dict):
            websocket_messages.append(message)
            msg_type = message.get('type', 'unknown')
            stage = message.get('stage', '')
            msg_text = message.get('message', '')
            
            if msg_type == 'pipeline_start':
                print(f"🚀 Pipeline Started: {pipeline_id}")
                print(f"   Stages: {message.get('stages', [])}")
            elif msg_type == 'stage_start':
                print(f"🔄 Stage Started: {stage} - {msg_text}")
            elif msg_type == 'status_update':
                progress = message.get('progress', 'N/A')
                print(f"📈 Progress Update [{stage}]: {msg_text} ({progress}%)")
                
                # Show fix details if available
                if stage == 'fix' and message.get('details'):
                    details = message['details']
                    if 'function_name' in details:
                        print(f"      🔧 Fixing: {details['function_name']}() in {details['filename']}")
                        print(f"      📝 Summary: {details['fix_summary']}")
                        
            elif msg_type == 'stage_complete':
                status = message.get('status', 'unknown')
                duration = message.get('duration', 0)
                print(f"✅ Stage Complete [{stage}]: {status} ({duration}s)")
                
                # Show stage results
                results = message.get('results', {})
                if stage == 'build' and results:
                    print(f"      Files analyzed: {results.get('metadata', {}).get('files_analyzed', 0)}")
                elif stage == 'analyze' and results:
                    print(f"      Issues found: {results.get('total_issues', 0)}")
                elif stage == 'fix' and results:
                    print(f"      Fixes applied: {results.get('fixes_applied', 0)}")
                    print(f"      Files modified: {results.get('files_modified', 0)}")
                    
            elif msg_type == 'pipeline_complete':
                status = message.get('status', 'unknown')
                duration = message.get('total_duration', 0)
                print(f"🎉 Pipeline Complete: {status} ({duration}s)")
                
                # Show summary
                summary = message.get('summary', {})
                for stage_name, stage_info in summary.items():
                    stage_status = stage_info.get('status', 'unknown')
                    print(f"      {stage_name}: {stage_status}")
                    
            elif msg_type == 'error':
                print(f"❌ Error [{stage}]: {msg_text}")
    
    try:
        # Initialize pipeline
        pipeline = get_pipeline_orchestrator()
        pipeline.set_websocket_manager(MockWebSocketManager())
        
        # Test with a sample repository
        repo_name = "mysteryisfun/sample-fastapi-project"  # Use your test repo
        pr_number = 1
        
        print(f"📊 Testing Pipeline:")
        print(f"   Repository: {repo_name}")
        print(f"   PR Number: {pr_number}")
        print(f"   Expected Stages: Build → Analyze → Fix")
        print("")
        
        # Start pipeline
        pipeline_id = await pipeline.start_pipeline(pr_number, repo_name)
        
        print(f"Pipeline ID: {pipeline_id}")
        print("")
        
        # Wait for completion (simulate real scenario)
        await asyncio.sleep(2)  # Give time for initial messages
        
        # Check if pipeline is still running
        max_wait = 180  # 3 minutes max
        wait_time = 0
        
        while wait_time < max_wait:
            await asyncio.sleep(5)
            wait_time += 5
            
            # Check if pipeline completed
            if any(msg.get('type') == 'pipeline_complete' for msg in websocket_messages):
                break
                
            print(f"⏳ Waiting for pipeline completion... ({wait_time}/{max_wait}s)")
        
        # Analyze results
        print(f"\n📋 Pipeline Analysis:")
        print(f"   Total WebSocket messages: {len(websocket_messages)}")
        
        # Count messages by type
        message_types = {}
        for msg in websocket_messages:
            msg_type = msg.get('type', 'unknown')
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        print(f"   Message breakdown: {message_types}")
        
        # Check if Fix stage ran
        fix_messages = [msg for msg in websocket_messages if msg.get('stage') == 'fix']
        print(f"   Fix stage messages: {len(fix_messages)}")
        
        # Get final status
        pipeline_complete_msgs = [msg for msg in websocket_messages if msg.get('type') == 'pipeline_complete']
        
        if pipeline_complete_msgs:
            final_msg = pipeline_complete_msgs[-1]
            final_status = final_msg.get('status', 'unknown')
            summary = final_msg.get('summary', {})
            
            print(f"\n🎯 Final Results:")
            print(f"   Pipeline Status: {final_status}")
            
            for stage_name, stage_info in summary.items():
                stage_status = stage_info.get('status', 'unknown')
                print(f"   {stage_name.title()}: {stage_status}")
                
                if stage_name == 'fix' and 'fixes_applied' in stage_info:
                    print(f"      Fixes applied: {stage_info['fixes_applied']}")
            
            return final_status == 'success'
        else:
            print(f"❌ Pipeline did not complete within timeout")
            return False
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_pipeline_stages_individually():
    """Test individual stages to isolate issues"""
    
    print("\n🔬 Testing Pipeline Stages Individually")
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from src.agents.build_agent import get_build_agent
        from src.agents.analyze_agent import get_analyze_agent
        from src.agents.fix_agent import get_fix_agent
        print("✅ All agent imports successful")
        
        # Test agent initialization
        print("🏗️ Testing agent initialization...")
        build_agent = get_build_agent()
        analyze_agent = get_analyze_agent()
        fix_agent = get_fix_agent()
        print("✅ All agents initialized successfully")
        
        # Test GitHub client
        print("🐙 Testing GitHub client...")
        from src.utils.github_client import get_github_client
        github_client = get_github_client()
        print("✅ GitHub client initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Individual stage test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    async def run_tests():
        print("🚀 Starting Complete Pipeline Tests with Fix Agent\n")
        
        # Test 1: Individual components
        test1_result = await test_pipeline_stages_individually()
        
        if test1_result:
            # Test 2: Complete pipeline
            test2_result = await test_complete_pipeline_with_fixes()
        else:
            test2_result = False
        
        print(f"\n📋 Test Summary:")
        print(f"   Component Tests: {'✅ PASS' if test1_result else '❌ FAIL'}")
        print(f"   Pipeline Test: {'✅ PASS' if test2_result else '❌ FAIL'}")
        
        if test1_result and test2_result:
            print(f"\n🎉 All pipeline tests with Fix Agent passed!")
            print(f"\n🚀 Ready for demo: Build → Analyze → Fix pipeline is operational!")
        else:
            print(f"\n❌ Some tests failed. Check implementation.")
    
    asyncio.run(run_tests())
