#!/usr/bin/env python3
"""
Real Webhook Test with Actual PR Data
This will capture and analyze real webhook data from your test repository
"""

import requests
import json
import time

def test_real_webhook_endpoint():
    """Test the actual webhook endpoint with real data"""
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Check if server is running
        print("1️⃣ Testing server connectivity...")
        health_response = requests.get(f"{base_url}/health", timeout=5)
        
        if health_response.status_code == 200:
            print("✅ Server is running and healthy")
            print(f"📋 Response: {health_response.json()}")
        else:
            print(f"❌ Server health check failed: {health_response.status_code}")
            return False
        
        # Test 2: Trigger test webhook to see the flow
        print("\n2️⃣ Testing internal webhook endpoint...")
        test_response = requests.post(f"{base_url}/webhook", timeout=10)
        
        if test_response.status_code == 200:
            print("✅ Test webhook triggered successfully")
            result = test_response.json()
            print(f"📋 Pipeline ID: {result.get('pipeline_id')}")
            print(f"🔗 WebSocket URL: {result.get('websocket_url')}")
            
            # Monitor WebSocket for real-time updates
            pipeline_id = result.get('pipeline_id')
            if pipeline_id:
                print(f"\n3️⃣ Monitoring pipeline {pipeline_id}...")
                print("💡 You can connect to WebSocket to see real-time updates:")
                print(f"   ws://localhost:8000/ws/{pipeline_id}")
                
                # Check pipeline status
                time.sleep(2)
                status_response = requests.get(f"{base_url}/pipeline/{pipeline_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"📊 Pipeline Status: {status_data.get('stage')}")
                    print(f"⏱️ Duration: {status_data.get('duration', 0):.2f}s")
                    
                    # Show build results if available
                    results = status_data.get('results', {})
                    if 'build' in results:
                        build_result = results['build']
                        print(f"🔨 Build Success: {build_result.get('success')}")
                        print(f"📂 Files Analyzed: {len(build_result.get('file_info', {}))}")
                        if build_result.get('build_logs'):
                            print("📋 Build Logs:")
                            for log in build_result['build_logs'][-3:]:
                                print(f"   {log}")
        else:
            print(f"❌ Test webhook failed: {test_response.status_code}")
            print(f"📋 Response: {test_response.text}")
            return False
        
        print("\n✅ Real webhook test completed!")
        print("\n🎯 Ready for your test repository webhook:")
        print(f"   POST {base_url}/webhook/github")
        print("   Make sure your test repo webhook points to your ngrok URL!")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def monitor_webhook_logs():
    """Instructions for monitoring real webhook from test repo"""
    
    print("\n🚀 READY FOR REAL TEST REPOSITORY WEBHOOK")
    print("=" * 60)
    print("1. Make sure your test repository webhook is configured:")
    print("   📡 Payload URL: https://your-ngrok-url.ngrok.io/webhook/github")
    print("   🔒 Content Type: application/json")
    print("   ⚡ Events: Pull request")
    print("")
    print("2. Create or update a PR in your test repository")
    print("3. Check the server logs to see real webhook data")
    print("4. Monitor WebSocket for real-time pipeline updates")
    print("")
    print("💡 Server endpoints available:")
    print("   GET  /health - Health check")
    print("   POST /webhook - Test endpoint")
    print("   POST /webhook/github - Real GitHub webhook")
    print("   WS   /ws/{pipeline_id} - Real-time updates")
    print("   GET  /pipeline/{pipeline_id} - Status check")

if __name__ == "__main__":
    print("🧪 REAL WEBHOOK TESTING")
    print("=" * 50)
    
    # Test current server
    success = test_real_webhook_endpoint()
    
    if success:
        # Show instructions for real test
        monitor_webhook_logs()
    else:
        print("\n❌ Fix server issues before testing with real repository")
