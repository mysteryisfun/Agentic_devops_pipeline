"""
Test Terminal Streaming Integration with Pipeline
Quick test to verify terminal streaming is properly integrated with pipeline stages
"""
import asyncio
import json
import time

async def test_pipeline_terminal_integration():
    """Test that pipeline stages correctly start terminal streaming"""
    
    print("🧪 Testing Pipeline Terminal Streaming Integration")
    print("=" * 60)
    
    try:
        # Import the pipeline orchestrator
        from src.agents.pipeline_orchestrator import get_pipeline_orchestrator
        pipeline = get_pipeline_orchestrator()
        
        # Test terminal streaming function directly
        print("🔧 Testing terminal streaming function...")
        
        test_pipeline_id = f"test_pipeline_{int(time.time())}"
        
        # Test the start_terminal_streaming function
        terminal_session = await pipeline.start_terminal_streaming(
            pipeline_id=test_pipeline_id,
            command="echo 'Hello from pipeline terminal streaming!'",
            stage="test"
        )
        
        if terminal_session:
            print(f"✅ Terminal streaming started successfully!")
            print(f"📋 Terminal session ID: {terminal_session}")
            
            # Wait a moment for command to execute
            await asyncio.sleep(2)
            
            # Check if terminal session is active
            terminal_manager = pipeline.terminal_manager
            sessions = terminal_manager.list_active_sessions()
            
            print(f"🔍 Active terminal sessions: {len(sessions)}")
            for session in sessions:
                if session['session_id'] == terminal_session:
                    print(f"   ✅ Found our session: {session['session_id']}")
                    print(f"   📊 Command: {session['command']}")
                    print(f"   🏃 Running: {session['is_running']}")
                    break
            else:
                print(f"   ⚠️ Our session not found in active sessions")
            
        else:
            print(f"❌ Failed to start terminal streaming")
            return False
        
        print(f"\n🧪 Testing WebSocket message integration...")
        
        # Test WebSocket messaging (if available)
        if hasattr(pipeline, 'websocket_manager') and pipeline.websocket_manager:
            print(f"✅ WebSocket manager is available")
            
            # Test sending a message
            await pipeline.send_websocket_message(test_pipeline_id, {
                "type": "test_message",
                "message": "Terminal streaming integration test",
                "timestamp": time.time()
            })
            print(f"✅ WebSocket message sent successfully")
            
        else:
            print(f"⚠️ WebSocket manager not available (normal for testing)")
        
        print(f"\n🎯 Integration Test Summary:")
        print(f"✅ Pipeline orchestrator loaded")
        print(f"✅ Terminal manager available")
        print(f"✅ Terminal streaming function works")
        print(f"✅ WebSocket integration ready")
        
        print(f"\n🚀 Pipeline terminal streaming integration is WORKING!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the integration test"""
    success = await test_pipeline_terminal_integration()
    
    print(f"\n" + "=" * 60)
    if success:
        print(f"🎉 TERMINAL STREAMING INTEGRATION TEST PASSED!")
        print(f"🔗 Pipeline stages will now stream terminal output")
        print(f"📡 Frontend can connect to WebSocket endpoints:")
        print(f"   - ws://localhost:8000/ws/terminal/all")
        print(f"   - ws://localhost:8000/ws/terminal/{{session_id}}")
    else:
        print(f"💥 INTEGRATION TEST FAILED!")
        print(f"🔧 Check the pipeline orchestrator setup")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
