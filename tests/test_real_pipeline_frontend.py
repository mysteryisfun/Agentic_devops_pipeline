"""
Real Pipeline Frontend Test - Trigger actual pipeline with WebSocket communication
"""

import asyncio
import json
import requests
import websockets
from datetime import datetime

async def test_real_pipeline_with_frontend():
    """
    Test the complete flow:
    1. Trigger real pipeline via HTTP endpoint
    2. Connect to WebSocket to receive real messages
    3. Display messages for frontend testing
    """
    
    print("🧪 Real Pipeline Frontend Test")
    print("=" * 60)
    print("📋 This will:")
    print("   1. Trigger the REAL pipeline via /webhook endpoint")
    print("   2. Connect to WebSocket to receive REAL messages")
    print("   3. Show you actual pipeline progress!")
    print()
    
    # Step 1: Trigger the actual pipeline
    print("🚀 Step 1: Triggering real pipeline...")
    
    try:
        response = requests.post("http://localhost:8000/webhook")
        response.raise_for_status()
        
        result = response.json()
        pipeline_id = result["pipeline_id"]
        repo_name = result["repo"]
        pr_number = result["pr_number"]
        
        print(f"✅ Pipeline triggered successfully!")
        print(f"   Pipeline ID: {pipeline_id}")
        print(f"   Repository: {repo_name}")
        print(f"   PR Number: {pr_number}")
        print(f"   WebSocket URL: {result['websocket_url']}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to trigger pipeline: {e}")
        print("📋 Make sure the server is running on localhost:8000")
        return
    
    # Step 2: Connect to WebSocket and receive real messages
    print("🔌 Step 2: Connecting to WebSocket for real-time updates...")
    
    uri = f"ws://localhost:8000/ws/{pipeline_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to WebSocket: {uri}")
            print(f"🌐 Now open test_websocket.html and connect to pipeline: {pipeline_id}")
            print()
            print("📡 Real-time Pipeline Messages:")
            print("-" * 60)
            
            message_count = 0
            start_time = datetime.now()
            
            try:
                while True:
                    # Receive actual messages from the pipeline
                    message_text = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    message = json.loads(message_text)
                    
                    message_count += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"[{timestamp}] 📨 Message #{message_count}:")
                    print(f"   Type: {message.get('type', 'unknown')}")
                    
                    if message.get('type') == 'pipeline_start':
                        print(f"   🚀 Pipeline started for PR #{message.get('pr_number')}")
                        print(f"   📂 Repository: {message.get('repo_name')}")
                        print(f"   🌿 Branch: {message.get('branch')}")
                        print(f"   📋 Stages: {message.get('stages')}")
                    
                    elif message.get('type') == 'stage_start':
                        stage = message.get('stage')
                        print(f"   🎯 Stage '{stage}' starting...")
                        print(f"   💬 Message: {message.get('message')}")
                    
                    elif message.get('type') == 'status_update':
                        stage = message.get('stage')
                        progress = message.get('progress', 0)
                        status_msg = message.get('message')
                        print(f"   📊 Stage '{stage}' progress: {progress}%")
                        print(f"   💬 Status: {status_msg}")
                        
                        # Show details if available
                        if 'details' in message:
                            details = message['details']
                            print(f"   📋 Details: {json.dumps(details, indent=6)}")
                    
                    elif message.get('type') == 'stage_complete':
                        stage = message.get('stage')
                        status = message.get('status')
                        duration = message.get('duration')
                        print(f"   ✅ Stage '{stage}' completed with status: {status}")
                        print(f"   ⏱️ Duration: {duration}s")
                        
                        # Show results if available
                        if 'results' in message:
                            results = message['results']
                            print(f"   📋 Results:")
                            for key, value in results.items():
                                if isinstance(value, (list, dict)):
                                    print(f"      {key}: {len(value) if isinstance(value, list) else 'object'}")
                                else:
                                    print(f"      {key}: {value}")
                    
                    elif message.get('type') == 'pipeline_complete':
                        status = message.get('status')
                        duration = message.get('total_duration')
                        print(f"   🎉 Pipeline completed with status: {status}")
                        print(f"   ⏱️ Total duration: {duration}s")
                        
                        if 'summary' in message:
                            summary = message['summary']
                            print(f"   📋 Summary:")
                            for stage, info in summary.items():
                                print(f"      {stage}: {info.get('status', 'unknown')}")
                        
                        print("\n🎉 Pipeline execution complete!")
                        break
                    
                    elif message.get('type') == 'error':
                        print(f"   ❌ Error in stage '{message.get('stage')}':")
                        print(f"   💬 Error: {message.get('error')}")
                        print(f"   📋 Details: {message.get('details', 'No details')}")
                    
                    else:
                        print(f"   📄 Raw message: {json.dumps(message, indent=6)}")
                    
                    print()  # Empty line for readability
                    
            except asyncio.TimeoutError:
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"⏰ No more messages received after {elapsed:.1f}s")
                print(f"📊 Total messages received: {message_count}")
                
                if message_count == 0:
                    print("🤔 This might mean:")
                    print("   - Pipeline is still starting up")
                    print("   - Pipeline completed very quickly") 
                    print("   - There was an issue with the pipeline")
                else:
                    print("✅ Successfully received real-time pipeline messages!")
            
            print()
            print("📋 Frontend Testing Results:")
            print(f"   ✅ Pipeline triggered: {pipeline_id}")
            print(f"   ✅ WebSocket connected: {uri}")
            print(f"   ✅ Messages received: {message_count}")
            print(f"   🌐 Frontend URL: test_websocket.html with pipeline ID: {pipeline_id}")
            print()
            print("🧪 To test frontend:")
            print("   1. Open test_websocket.html in your browser")
            print(f"   2. Enter pipeline ID: {pipeline_id}")
            print("   3. Click Connect to see the same messages!")
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        print("📋 Possible issues:")
        print("   - Server not running on localhost:8000")
        print("   - WebSocket endpoint not available")
        print("   - Pipeline ID incorrect")

if __name__ == "__main__":
    print("🌐 Starting Real Pipeline Frontend Test...")
    print("⚠️  Make sure:")
    print("   1. FastAPI server is running (localhost:8000)")
    print("   2. You have internet connection (for GitHub API)")
    print("   3. Environment variables are configured")
    print()
    
    asyncio.run(test_real_pipeline_with_frontend())
