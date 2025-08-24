"""
Complete Pipeline Test with Real Fix Agent
Tests the entire Build -> Analyze -> Fix pipeline with real repository data
"""

import sys
sys.path.append('.')

from src.agents.pipeline_orchestrator import get_pipeline_orchestrator
import asyncio

async def test_complete_pipeline_with_real_fix():
    """Test the complete pipeline with real repository and Fix Agent"""
    
    print("🚀 Testing Complete Pipeline: Build → Analyze → Fix")
    
    # Track all WebSocket messages
    websocket_messages = []
    
    class MockWebSocketManager:
        async def send_message(self, pipeline_id: str, message: dict):
            websocket_messages.append(message)
            msg_type = message.get('type', 'unknown')
            stage = message.get('stage', '')
            msg_text = message.get('message', '')
            
            print(f"📡 {msg_type.upper()}: {msg_text}")
            
            if msg_type == 'status_update' and stage == 'fix':
                details = message.get('details', {})
                if 'function_name' in details:
                    print(f"      🔧 Fixing: {details['function_name']}() in {details['filename']}")
                    print(f"      📝 Summary: {details['fix_summary']}")
                    print(f"      📊 Old: {details.get('old_code', '')[:50]}...")
                    print(f"      ✨ New: {details.get('new_code', '')[:50]}...")
            
            elif msg_type == 'stage_complete':
                results = message.get('results', {})
                if stage == 'build':
                    print(f"      📊 Files analyzed: {results.get('metadata', {}).get('files_analyzed', 0)}")
                elif stage == 'analyze':
                    print(f"      🔍 Issues found: {results.get('total_issues', 0)}")
                elif stage == 'fix':
                    print(f"      🔧 Fixes applied: {results.get('fixes_applied', 0)}")
                    print(f"      📁 Files modified: {results.get('files_modified', 0)}")
                    if results.get('fixes_summary'):
                        for fix in results['fixes_summary']:
                            print(f"         ✅ {fix['filename']}: {fix['summary']}")
    
    try:
        # Initialize pipeline with real orchestrator
        pipeline = get_pipeline_orchestrator()
        pipeline.set_websocket_manager(MockWebSocketManager())
        
        print("✅ Pipeline orchestrator initialized")
        
        # Use the current repository for testing
        repo_name = "mysteryisfun/Agentic_devops_pipeline"
        pr_number = 1  # We'll create a test PR or use existing one
        
        print(f"\n🎯 Starting Real Pipeline Test:")
        print(f"   Repository: {repo_name}")
        print(f"   PR Number: {pr_number}")
        print(f"   Expected Flow: Build → Analyze → Fix")
        print("")
        
        # Start the real pipeline
        pipeline_id = await pipeline.start_pipeline(pr_number, repo_name)
        
        print(f"📋 Pipeline ID: {pipeline_id}")
        print("")
        
        # Wait for pipeline completion
        max_wait = 300  # 5 minutes max
        wait_time = 0
        
        while wait_time < max_wait:
            await asyncio.sleep(5)
            wait_time += 5
            
            # Check if pipeline completed
            if any(msg.get('type') == 'pipeline_complete' for msg in websocket_messages):
                break
                
            print(f"⏳ Pipeline running... ({wait_time}/{max_wait}s)")
        
        # Analyze results
        print(f"\n📊 Pipeline Analysis:")
        print(f"   Total messages: {len(websocket_messages)}")
        
        # Check stages
        stages_run = set()
        for msg in websocket_messages:
            if msg.get('type') == 'stage_start':
                stages_run.add(msg.get('stage'))
        
        print(f"   Stages executed: {list(stages_run)}")
        
        # Check Fix stage specifically
        fix_messages = [msg for msg in websocket_messages if msg.get('stage') == 'fix']
        print(f"   Fix stage messages: {len(fix_messages)}")
        
        # Get final results
        pipeline_complete_msgs = [msg for msg in websocket_messages if msg.get('type') == 'pipeline_complete']
        
        if pipeline_complete_msgs:
            final_msg = pipeline_complete_msgs[-1]
            summary = final_msg.get('summary', {})
            
            print(f"\n🎯 Final Pipeline Results:")
            for stage_name, stage_info in summary.items():
                status = stage_info.get('status', 'unknown')
                print(f"   {stage_name.title()}: {status}")
                
                if stage_name == 'fix' and status == 'success':
                    fixes_applied = stage_info.get('fixes_applied', 0)
                    print(f"      🔧 Real fixes applied: {fixes_applied}")
                    
                    if fixes_applied > 0:
                        print("      🎉 FIX AGENT SUCCESSFULLY APPLIED REAL FIXES!")
                        return True
        
        # Check if Fix Agent actually ran
        fix_ran = any(msg.get('stage') == 'fix' and msg.get('type') == 'stage_start' for msg in websocket_messages)
        
        if fix_ran:
            print("✅ Fix Agent was executed in the pipeline")
        else:
            print("⚠️ Fix Agent was not executed (no issues found or skipped)")
        
        return fix_ran
        
    except Exception as e:
        print(f"❌ Complete pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    async def run_test():
        print("🚀 Starting Complete Pipeline Test with Real Fix Agent\n")
        
        result = await test_complete_pipeline_with_real_fix()
        
        print(f"\n📋 Test Summary:")
        print(f"   Complete Pipeline Test: {'✅ PASS' if result else '❌ FAIL'}")
        
        if result:
            print(f"\n🎉 Complete pipeline with Fix Agent is working!")
            print(f"🚀 Ready for real-world testing!")
        else:
            print(f"\n❌ Pipeline test failed or Fix Agent didn't run.")
    
    asyncio.run(run_test())
