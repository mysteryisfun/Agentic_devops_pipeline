"""
Mock WebSocket Communication Test - Send mock data to test frontend
"""

import asyncio
import json
import websockets
from datetime import datetime
import time

async def send_mock_messages_to_websocket():
    """
    Send mock pipeline messages directly to WebSocket to test frontend communication
    """
    
    # Use a simple pipeline ID
    pipeline_id = "test_pipeline_123"
    uri = f"ws://localhost:8000/ws/{pipeline_id}"
    
    print("🧪 Mock WebSocket Communication Test")
    print("=" * 60)
    print(f"📡 Connecting to: {uri}")
    print(f"🌐 Make sure your HTML frontend connects to pipeline ID: {pipeline_id}")
    print()
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server!")
            print("🚀 Sending mock pipeline messages...")
            print("-" * 60)
            
            # Send mock messages with delays to see real-time updates
            
            # 1. Pipeline Start
            message1 = {
                "type": "pipeline_start",
                "pipeline_id": pipeline_id,
                "pr_number": 123,
                "repo_name": "mysteryisfun/test-repo",
                "branch": "feature/websocket-test",
                "stages": ["build", "analyze", "fix", "test"],
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(message1))
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📨 Sent: pipeline_start")
            await asyncio.sleep(2)
            
            # 2. Analyze Stage Start
            message2 = {
                "type": "stage_start", 
                "stage": "analyze",
                "stage_index": 1,
                "message": "🧠 Starting AI-powered security analysis...",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(message2))
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📨 Sent: analyze stage_start")
            await asyncio.sleep(1)
            
            # 3. Analyze Progress Updates with Details
            progress_updates = [
                (10, "📂 Scanning changed files...", {
                    "files_changed": 5,
                    "files_to_analyze": 3
                }),
                (25, "🔍 Analyzing auth.py...", {
                    "current_file": "auth.py",
                    "step": "file_analysis",
                    "files_completed": 0,
                    "total_files": 3
                }),
                (40, "🤖 AI generating targeted questions...", {
                    "current_file": "auth.py",
                    "step": "mcp_context_gathering",
                    "questions_generated": 3
                }),
                (55, "🔧 Executing MCP question 1/3", {
                    "question": "Find all API endpoints that accept user input",
                    "reasoning": "Checking for input validation vulnerabilities",
                    "step": "mcp_question_execution"
                }),
                (70, "🧠 Gemini AI analyzing security patterns...", {
                    "current_file": "auth.py",
                    "step": "ai_security_analysis",
                    "context_size": "8.2KB"
                }),
                (85, "📊 Compiling analysis results...", {
                    "vulnerabilities_found": 2,
                    "issues_found": 4,
                    "files_completed": 3
                })
            ]
            
            for progress, msg, details in progress_updates:
                update_msg = {
                    "type": "status_update",
                    "stage": "analyze",
                    "status": "in_progress",
                    "message": msg,
                    "progress": progress,
                    "details": details,
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(update_msg))
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 📨 Sent: progress {progress}% - {msg[:30]}...")
                await asyncio.sleep(2)
            
            # 4. Analyze Stage Complete with Full Results
            complete_msg = {
                "type": "stage_complete",
                "stage": "analyze",
                "status": "success",
                "duration": 45.2,
                "results": {
                    "files_analyzed": 3,
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
                            "file": "api.py",
                            "line": 15,
                            "description": "Missing input validation on username parameter"
                        }
                    ],
                    "security_issues": [
                        {
                            "type": "AUTHENTICATION_BYPASS",
                            "severity": "MEDIUM",
                            "file": "auth.py",
                            "line": 45,
                            "description": "Potential authentication bypass in login flow"
                        }
                    ],
                    "quality_issues": [
                        {
                            "type": "CODE_SMELL",
                            "severity": "LOW", 
                            "file": "utils.py",
                            "line": 12,
                            "description": "Unused import statement"
                        }
                    ],
                    "recommendations": [
                        "Implement parameterized queries to prevent SQL injection",
                        "Add comprehensive input validation for all user data",
                        "Review authentication logic for potential bypasses"
                    ],
                    "metadata": {
                        "mcp_questions_executed": 9,
                        "context_gathered": "24.6KB",
                        "ai_model": "Gemini 2.5 Flash",
                        "analysis_time": 45.2,
                        "overall_risk_level": "HIGH"
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(complete_msg))
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📨 Sent: analyze stage_complete")
            await asyncio.sleep(2)
            
            # 5. Pipeline Complete
            final_msg = {
                "type": "pipeline_complete",
                "status": "success",
                "total_duration": 67.8,
                "summary": {
                    "analyze": {
                        "status": "success",
                        "issues_found": 6,
                        "duration": 45.2
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(final_msg))
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📨 Sent: pipeline_complete")
            
            print()
            print("🎉 All mock messages sent successfully!")
            print("🌐 Your frontend should now show:")
            print("   ✅ Pipeline started")
            print("   ✅ Analyze stage progress (10% → 85%)")
            print("   ✅ Real-time status updates")
            print("   ✅ Final results with 6 issues found")
            print("   ✅ Stage completed successfully")
            
            # Keep connection alive so frontend can stay connected
            print()
            print("🔌 Keeping WebSocket alive for 30 seconds...")
            print("   Open your frontend now to see the messages!")
            await asyncio.sleep(30)
            
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        print("📋 Make sure:")
        print("   1. Server is running on localhost:8000")
        print("   2. WebSocket endpoint /ws/{pipeline_id} is available")

if __name__ == "__main__":
    print("🌐 Mock WebSocket Communication Test")
    print("📋 Instructions:")
    print("   1. Make sure server is running (localhost:8000)")
    print("   2. Open test_websocket.html in browser")
    print("   3. Connect to pipeline ID: test_pipeline_123")
    print("   4. Watch real-time messages appear!")
    print()
    
    asyncio.run(send_mock_messages_to_websocket())
