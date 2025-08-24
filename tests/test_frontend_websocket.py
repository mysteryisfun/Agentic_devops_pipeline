"""
WebSocket Message Sender - Send real messages to the frontend
"""

import asyncio
import json
import time
from datetime import datetime

async def send_test_messages_to_frontend():
    """Send realistic pipeline messages to test the frontend"""
    
    import websockets
    
    pipeline_id = "test_pipeline_123"
    uri = f"ws://localhost:8000/ws/{pipeline_id}"
    
    print(f"🔌 Connecting to WebSocket: {uri}")
    print(f"📡 Make sure your HTML file is connected to the same pipeline ID!")
    print(f"🌐 Open test_websocket.html in your browser and connect to: {pipeline_id}")
    print()
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server!")
            print("🚀 Starting to send test messages...")
            print("-" * 60)
            
            # 1. Pipeline Start
            message1 = {
                "type": "pipeline_start",
                "pipeline_id": pipeline_id,
                "pr_number": 123,
                "repo_name": "mysteryisfun/test-repo",
                "branch": "feature/websocket-test",
                "stages": ["build", "analyze", "fix", "test"]
            }
            
            await websocket.send(json.dumps(message1))
            print("📨 Sent: pipeline_start")
            await asyncio.sleep(2)
            
            # 2. Build Stage Start
            message2 = {
                "type": "stage_start", 
                "stage": "build",
                "stage_index": 1,
                "message": "Starting build stage..."
            }
            
            await websocket.send(json.dumps(message2))
            print("📨 Sent: build stage_start")
            await asyncio.sleep(1)
            
            # 3. Build Progress Updates
            build_updates = [
                (20, "Installing dependencies..."),
                (40, "Compiling source code..."),
                (60, "Running build scripts..."),
                (80, "Generating artifacts..."),
                (100, "Build completed successfully!")
            ]
            
            for progress, msg in build_updates:
                update_msg = {
                    "type": "status_update",
                    "stage": "build",
                    "status": "in_progress",
                    "message": msg,
                    "progress": progress
                }
                
                await websocket.send(json.dumps(update_msg))
                print(f"📨 Sent: build progress {progress}% - {msg}")
                await asyncio.sleep(1.5)
            
            # 4. Build Stage Complete
            message3 = {
                "type": "stage_complete",
                "stage": "build",
                "status": "success",
                "duration": 45.2,
                "results": {
                    "build_logs": ["✅ Dependencies installed", "✅ Build succeeded"],
                    "errors": [],
                    "metadata": {"files_analyzed": 12}
                }
            }
            
            await websocket.send(json.dumps(message3))
            print("📨 Sent: build stage_complete")
            await asyncio.sleep(2)
            
            # 5. Analysis Stage Start
            message4 = {
                "type": "stage_start", 
                "stage": "analyze",
                "stage_index": 2,
                "message": "🧠 Starting AI-powered code analysis..."
            }
            
            await websocket.send(json.dumps(message4))
            print("📨 Sent: analyze stage_start")
            await asyncio.sleep(1)
            
            # 6. Analysis Progress Updates (with details)
            analysis_updates = [
                (15, "📂 Scanning changed files for analysis...", {
                    "files_changed": 7,
                    "code_files_to_analyze": 5
                }),
                (25, "🔍 Analyzing file 1/5: auth.py", {
                    "current_file": "auth.py",
                    "files_completed": 0,
                    "total_files": 5
                }),
                (35, "🤖 AI generating targeted questions for auth.py...", {
                    "current_file": "auth.py",
                    "step": "mcp_context_gathering",
                    "phase": "question_generation"
                }),
                (45, "🔧 AI asking question 1", {
                    "current_file": "auth.py",
                    "scope_assessed": "medium",
                    "question": "Find all API endpoints that use request.json.get() without validation",
                    "reasoning": "Checking for input validation vulnerabilities",
                    "step": "mcp_question_execution"
                }),
                (55, "🧠 Gemini AI analyzing security vulnerabilities...", {
                    "current_file": "auth.py",
                    "step": "ai_security_analysis",
                    "context_size": "8.2KB",
                    "analysis_focus": "Input validation, SQL injection, authentication bypass"
                }),
                (70, "🔍 Analyzing file 2/5: utils.py", {
                    "current_file": "utils.py",
                    "files_completed": 1,
                    "total_files": 5
                }),
                (90, "🎯 Security analysis complete - compiling results...", {
                    "vulnerabilities_found": 2,
                    "security_issues_found": 1,
                    "quality_issues_found": 3,
                    "total_issues": 6
                })
            ]
            
            for progress, msg, details in analysis_updates:
                update_msg = {
                    "type": "status_update",
                    "stage": "analyze",
                    "status": "in_progress",
                    "message": msg,
                    "progress": progress,
                    "details": details
                }
                
                await websocket.send(json.dumps(update_msg))
                print(f"📨 Sent: analyze progress {progress}% - {msg[:50]}...")
                await asyncio.sleep(2)
            
            # 7. Analysis Stage Complete
            message5 = {
                "type": "stage_complete",
                "stage": "analyze",
                "status": "success",
                "duration": 67.8,
                "results": {
                    "files_analyzed": 5,
                    "total_issues": 6,
                    "vulnerabilities": [
                        {
                            "type": "SQL_INJECTION",
                            "severity": "HIGH", 
                            "file": "auth.py",
                            "line": 23,
                            "description": "User input not validated before database query"
                        },
                        {
                            "type": "IMPROPER_INPUT_VALIDATION",
                            "severity": "MEDIUM",
                            "file": "auth.py",
                            "line": 15,
                            "description": "Username parameter lacks validation"
                        }
                    ],
                    "security_issues": [
                        {
                            "type": "AUTHENTICATION_BYPASS",
                            "severity": "MEDIUM",
                            "file": "auth.py", 
                            "line": 45
                        }
                    ],
                    "quality_issues": [
                        {
                            "type": "CODE_SMELL",
                            "severity": "LOW",
                            "file": "utils.py",
                            "line": 12
                        }
                    ],
                    "recommendations": [
                        "Implement parameterized queries to prevent SQL injection",
                        "Add input validation for all user-provided data"
                    ],
                    "next_stage": "fix",
                    "metadata": {
                        "mcp_questions_asked": 8,
                        "context_gathered": "24.6KB",
                        "analysis_time": 67.8,
                        "ai_model": "Gemini 2.5 Flash",
                        "overall_risk": "HIGH"
                    }
                }
            }
            
            await websocket.send(json.dumps(message5))
            print("📨 Sent: analyze stage_complete")
            await asyncio.sleep(2)
            
            # 8. Pipeline Complete
            message6 = {
                "type": "pipeline_complete",
                "status": "success",
                "total_duration": 180.5,
                "summary": {
                    "build": {"status": "success"},
                    "analyze": {"status": "success", "issues_found": 6},
                    "fix": {"status": "skipped", "reason": "Demo ended"},
                    "test": {"status": "skipped", "reason": "Demo ended"}
                }
            }
            
            await websocket.send(json.dumps(message6))
            print("📨 Sent: pipeline_complete")
            
            print()
            print("🎉 All test messages sent!")
            print("🌐 Check your browser - you should see the pipeline progress!")
            print("📊 The frontend should show:")
            print("   ✅ Build stage completed (green)")
            print("   ✅ Analyze stage completed (green)")
            print("   📊 Progress bars animated")
            print("   📋 Real-time logs with timestamps")
            print("   🎯 Final results and issue counts")
            
            # Keep connection alive for a bit
            await asyncio.sleep(5)
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        print("📋 Make sure:")
        print("   1. The server is running on localhost:8000")
        print("   2. Your browser is connected to the same pipeline_id")
        print("   3. The WebSocket endpoint is working properly")

if __name__ == "__main__":
    print("🧪 WebSocket Frontend Test")
    print("=" * 50)
    print("📋 Instructions:")
    print("   1. Make sure the server is running (localhost:8000)")
    print("   2. Open test_websocket.html in your browser")
    print("   3. Connect to pipeline ID: test_pipeline_123")
    print("   4. Run this script to see real-time updates!")
    print()
    
    asyncio.run(send_test_messages_to_frontend())
