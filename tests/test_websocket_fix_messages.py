#!/usr/bin/env python3
"""
Test WebSocket communication during Fix Agent operation
Monitor real-time messages sent to frontend during actual fixing
"""

import asyncio
import websockets
import json
import time
from typing import Dict, Any

class WebSocketFixTester:
    """Test WebSocket messages during fix agent operation"""
    
    def __init__(self, websocket_url="ws://localhost:8000/ws"):
        self.websocket_url = websocket_url
        self.received_messages = []
        self.fix_stage_messages = []
        
    async def connect_and_monitor(self, pipeline_id: str, duration: int = 120):
        """Connect to WebSocket and monitor fix stage messages"""
        
        try:
            print(f"🔌 Connecting to WebSocket: {self.websocket_url}")
            
            async with websockets.connect(self.websocket_url) as websocket:
                print(f"✅ Connected to WebSocket")
                print(f"📺 Monitoring pipeline: {pipeline_id}")
                print(f"⏱️ Duration: {duration} seconds")
                print("=" * 60)
                
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Wait for message with timeout
                        message = await asyncio.wait_for(
                            websocket.recv(), 
                            timeout=1.0
                        )
                        
                        # Parse message
                        try:
                            data = json.loads(message)
                            self.received_messages.append(data)
                            
                            # Filter fix stage messages
                            if data.get("stage") == "fix" or "fix" in data.get("type", "").lower():
                                self.fix_stage_messages.append(data)
                                self._print_fix_message(data)
                            elif data.get("type") == "pipeline_start":
                                print(f"🚀 Pipeline started: {data.get('pipeline_id', 'unknown')}")
                            elif data.get("type") == "stage_start" and data.get("stage") == "fix":
                                print(f"🔧 Fix stage starting...")
                                self._print_fix_message(data)
                            elif data.get("type") == "stage_complete" and data.get("stage") == "fix":
                                print(f"✅ Fix stage completed!")
                                self._print_fix_message(data)
                            elif data.get("type") == "error" and data.get("stage") == "fix":
                                print(f"❌ Fix stage error!")
                                self._print_fix_message(data)
                            
                        except json.JSONDecodeError:
                            print(f"⚠️ Invalid JSON received: {message[:100]}...")
                            
                    except asyncio.TimeoutError:
                        # No message received, continue
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        print(f"🔌 WebSocket connection closed")
                        break
                        
                print("=" * 60)
                print(f"📊 Monitoring complete!")
                self._print_summary()
                
        except Exception as e:
            print(f"❌ WebSocket connection error: {str(e)}")
            return False
            
        return True
    
    def _print_fix_message(self, data: Dict[str, Any]):
        """Print formatted fix stage message"""
        
        msg_type = data.get("type", "unknown")
        timestamp = time.strftime("%H:%M:%S")
        
        if msg_type == "stage_start":
            print(f"[{timestamp}] 🔧 FIX START: {data.get('message', 'Starting fix stage')}")
            if "details" in data:
                details = data["details"]
                print(f"    📋 Total issues: {details.get('total_issues', 0)}")
                print(f"    🎯 High confidence: {details.get('high_confidence_issues', 0)}")
                
        elif msg_type == "status_update":
            progress = data.get("progress", "?")
            message = data.get("message", "Working...")
            print(f"[{timestamp}] 📈 PROGRESS {progress}%: {message}")
            
            if "details" in data:
                details = data["details"]
                if "filename" in details:
                    print(f"    📁 File: {details['filename']}")
                if "fix_summary" in details:
                    print(f"    🔧 Fix: {details['fix_summary']}")
                if "commit_sha" in details:
                    print(f"    💾 Commit: {details['commit_sha'][:8]}...")
                    
        elif msg_type == "stage_complete":
            status = data.get("status", "unknown")
            duration = data.get("duration", 0)
            print(f"[{timestamp}] ✅ FIX COMPLETE: {status} (took {duration}s)")
            
            if "results" in data:
                results = data["results"]
                print(f"    🔧 Fixes applied: {results.get('fixes_applied', 0)}")
                print(f"    📁 Files modified: {results.get('files_modified', 0)}")
                print(f"    💾 Commits made: {results.get('commits_made', 0)}")
                
        elif msg_type == "error":
            error_msg = data.get("message", "Unknown error")
            error_code = data.get("error_code", "")
            print(f"[{timestamp}] ❌ ERROR ({error_code}): {error_msg}")
            
        else:
            print(f"[{timestamp}] 📨 {msg_type.upper()}: {data.get('message', str(data))}")
    
    def _print_summary(self):
        """Print summary of received messages"""
        
        total_messages = len(self.received_messages)
        fix_messages = len(self.fix_stage_messages)
        
        print(f"📊 WebSocket Message Summary:")
        print(f"   Total messages: {total_messages}")
        print(f"   Fix stage messages: {fix_messages}")
        
        if fix_messages > 0:
            print(f"\n🔧 Fix Stage Message Types:")
            fix_types = {}
            for msg in self.fix_stage_messages:
                msg_type = msg.get("type", "unknown")
                fix_types[msg_type] = fix_types.get(msg_type, 0) + 1
            
            for msg_type, count in fix_types.items():
                print(f"   {msg_type}: {count}")
        
        print(f"\n📋 All Fix Messages (JSON):")
        for i, msg in enumerate(self.fix_stage_messages):
            print(f"   {i+1}. {json.dumps(msg, indent=2)}")

async def test_websocket_fix_messages():
    """Test WebSocket messages during fix operation"""
    
    print("🧪 Testing WebSocket Fix Agent Messages")
    print("=" * 60)
    
    # Create tester
    tester = WebSocketFixTester()
    
    # Monitor for 2 minutes (enough time to trigger a fix)
    pipeline_id = "test_pipeline"  # Will capture any pipeline
    
    print("📋 Instructions:")
    print("1. Start the main server: python src/main.py")
    print("2. In another terminal, trigger a webhook to a repo with issues")
    print("3. This script will monitor fix stage WebSocket messages")
    print("4. Let it run until you see fix messages or timeout")
    print("")
    
    # Wait for user to start
    input("Press Enter when server is running and you're ready to trigger webhook...")
    
    # Monitor WebSocket
    success = await tester.connect_and_monitor(pipeline_id, duration=180)  # 3 minutes
    
    if success:
        print("✅ WebSocket monitoring completed successfully")
        
        # Save messages to file for analysis
        with open("websocket_fix_messages.json", "w") as f:
            json.dump({
                "total_messages": tester.received_messages,
                "fix_messages": tester.fix_stage_messages,
                "timestamp": time.time()
            }, f, indent=2)
        
        print("💾 Messages saved to websocket_fix_messages.json")
    else:
        print("❌ WebSocket monitoring failed")

if __name__ == "__main__":
    asyncio.run(test_websocket_fix_messages())
