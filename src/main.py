"""
Hackademia - AI-Powered Self-Healing CI/CD Pipeline
Main FastAPI application entry point
"""

# Load environment variables FIRST
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any, List
import json
import asyncio
import time

# Import our agents
import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Try both import patterns for flexibility
try:
    from src.agents.pipeline_orchestrator import get_pipeline_orchestrator
    from src.utils.terminal_websocket import get_terminal_websocket_manager
except ModuleNotFoundError:
    # Fallback for when running from src directory
    from agents.pipeline_orchestrator import get_pipeline_orchestrator
    from utils.terminal_websocket import get_terminal_websocket_manager

app = FastAPI(
    title="Hackademia AI Pipeline",
    description="AI-Powered Self-Healing CI/CD Pipeline with Multi-Agent Architecture",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get global instances
pipeline = get_pipeline_orchestrator()
terminal_manager = get_terminal_websocket_manager()

class WebSocketManager:
    """Enhanced WebSocket connection manager with broadcast support"""
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, pipeline_id: str):
        await websocket.accept()
        if pipeline_id not in self.connections:
            self.connections[pipeline_id] = []
        self.connections[pipeline_id].append(websocket)
        print(f"✅ WebSocket connected to {pipeline_id}")
        
    def disconnect(self, websocket: WebSocket, pipeline_id: str):
        if pipeline_id in self.connections:
            try:
                self.connections[pipeline_id].remove(websocket)
                if not self.connections[pipeline_id]:
                    del self.connections[pipeline_id]
                print(f"❌ WebSocket disconnected from {pipeline_id}")
            except ValueError:
                pass  # Connection already removed
        
    async def send_message(self, pipeline_id: str, message: dict):
        """Send message to specific pipeline listeners and broadcast to all listeners"""
        # Send to specific pipeline listeners
        if pipeline_id in self.connections:
            await self._send_to_connections(self.connections[pipeline_id], message)
        
        # Also send to "all_pipelines" listeners with pipeline context
        if "all_pipelines" in self.connections:
            message_with_id = {**message, "pipeline_id": pipeline_id}
            await self._send_to_connections(self.connections["all_pipelines"], message_with_id)
    
    async def _send_to_connections(self, connections: List[WebSocket], message: dict):
        """Helper method to send messages to a list of connections"""
        dead_connections = []
        for connection in connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                dead_connections.append(connection)
        
        # Clean up dead connections
        for dead_conn in dead_connections:
            try:
                connections.remove(dead_conn)
            except ValueError:
                pass  # Already removed
    
    def get_connection_stats(self) -> Dict[str, int]:
        """Get connection statistics"""
        return {
            pipeline_id: len(connections) 
            for pipeline_id, connections in self.connections.items()
        }

websocket_manager = WebSocketManager()
pipeline.set_websocket_manager(websocket_manager)

class WebhookPayload(BaseModel):
    """GitHub webhook payload model"""
    action: str
    pull_request: Dict[str, Any]
    repository: Dict[str, Any]

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Hackademia AI Pipeline is running!",
        "status": "healthy",
        "agents": ["build", "analyze", "fix", "test"]
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "pipeline": "ready",
        "agents_available": True
    }

@app.post("/webhook/results")
async def pipeline_results_webhook(request: Request):
    """
    Webhook endpoint to receive comprehensive pipeline results
    This can be used by external systems to process pipeline outcomes
    """
    try:
        payload = await request.json()
        
        # Validate the payload structure
        if "event_type" not in payload or payload["event_type"] != "pipeline_complete":
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid webhook payload - missing event_type"}
            )
        
        results = payload.get("results")
        if not results:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid webhook payload - missing results"}
            )
        
        # Extract key information
        pipeline_id = results.get("pipeline_id")
        repo_name = results.get("repository_name")
        pipeline_status = results.get("pipeline_status")
        total_duration = results.get("total_duration")
        
        print(f"📥 Received pipeline results webhook:")
        print(f"   Pipeline ID: {pipeline_id}")
        print(f"   Repository: {repo_name}")
        print(f"   Status: {pipeline_status}")
        print(f"   Duration: {total_duration:.2f}s")
        
        # Log key metrics
        build_success = results.get("build_results", {}).get("success", False)
        analysis_issues = len(results.get("analysis_results", {}).get("vulnerabilities", []))
        fixes_applied = len(results.get("fix_results", {}).get("functions_fixed", []))
        tests_generated = results.get("test_results", {}).get("tests_generated", 0)
        
        print(f"   Build: {'✅' if build_success else '❌'}")
        print(f"   Issues Found: {analysis_issues}")
        print(f"   Fixes Applied: {fixes_applied}")
        print(f"   Tests Generated: {tests_generated}")
        
        # Here you could integrate with external systems:
        # - Send to monitoring systems
        # - Update dashboards
        # - Trigger notifications
        # - Log to analytics platforms
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Pipeline results received successfully",
                "pipeline_id": pipeline_id,
                "processed": True
            }
        )
        
    except Exception as e:
        print(f"❌ Error processing pipeline results webhook: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process webhook: {str(e)}"}
        )

@app.post("/webhook/github")
async def github_webhook(request: Request):
    """
    GitHub webhook endpoint for PR events
    Triggers the multi-agent AI pipeline
    """
    try:
        payload = await request.json()
        
        # Verify this is a pull request event
        if "pull_request" not in payload:
            return JSONResponse(
                status_code=200,
                content={"message": "Not a pull request event, ignoring"}
            )
        
        action = payload.get("action")
        pr_data = payload.get("pull_request")
        repo_data = payload.get("repository")
        
        # Only process opened and synchronize events
        if action not in ["opened", "synchronize"]:
            return JSONResponse(
                status_code=200,
                content={"message": f"Action '{action}' not processed"}
            )
        
        # Extract basic PR info
        pr_number = pr_data.get("number")
        pr_title = pr_data.get("title")
        repo_name = repo_data.get("full_name")
        
        # 🚫 RECURSION PREVENTION: Check if this is triggered by AI-generated commits
        if action == "synchronize":
            # Get the latest commit from the webhook payload
            head_commit = pr_data.get("head", {}).get("sha")
            if head_commit:
                # Check if the latest commits are AI-generated
                is_ai_commit = await pipeline.is_ai_generated_commit(repo_name, head_commit)
                if is_ai_commit:
                    print(f"🚫 Skipping pipeline - triggered by AI-generated commit: {head_commit[:8]}")
                    return JSONResponse(
                        status_code=200,
                        content={
                            "message": "Skipping pipeline - triggered by AI commit",
                            "pr_number": pr_number,
                            "repo": repo_name,
                            "commit_sha": head_commit,
                            "reason": "ai_generated_commit"
                        }
                    )
        
        print(f"🚀 Processing PR #{pr_number}: {pr_title} in {repo_name}")
        
        # Gather trigger information for the results webhook
        sender_info = payload.get("sender", {})
        trigger_info = {
            "trigger_type": "webhook",
            "triggered_by": sender_info.get("login", "github"),
            "event_type": f"pull_request.{action}",
            "timestamp": time.time()
        }
        
        # Start multi-agent pipeline with trigger information
        pipeline_id = await pipeline.start_pipeline(pr_number, repo_name, trigger_info)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "PR processing initiated",
                "pr_number": pr_number,
                "repo": repo_name,
                "pipeline_id": pipeline_id,
                "pipeline_status": "starting"
            }
        )
        
    except Exception as e:
        print(f"❌ Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/trigger")
async def trigger_agents_manually(pr_data: Dict[str, Any]):
    """
    Manual trigger for testing agents without GitHub webhook
    """
    try:
        pr_number = pr_data.get("pr_number")
        repo_name = pr_data.get("repo_name")
        
        if not pr_number or not repo_name:
            raise HTTPException(status_code=400, detail="pr_number and repo_name required")
        
        # Start pipeline manually
        pipeline_id = await pipeline.start_pipeline(pr_number, repo_name)
        
        return {
            "message": "Manual agent triggering successful",
            "pipeline_id": pipeline_id,
            "status": "initiated",
            "agents": ["build", "analyze", "fix", "test"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pipeline/{pipeline_id}")
async def get_pipeline_status(pipeline_id: str):
    """Get status of a running pipeline"""
    try:
        status = pipeline.get_pipeline_status(pipeline_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Terminal Management Endpoints

@app.post("/terminal/start")
async def start_terminal_session(request: Request):
    """Start a new terminal session"""
    try:
        payload = await request.json()
        session_id = payload.get("session_id", f"terminal_{int(time.time())}")
        command = payload.get("command", "")
        cwd = payload.get("cwd")
        
        if not command:
            return JSONResponse(
                status_code=400,
                content={"error": "Command is required"}
            )
        
        success = await terminal_manager.start_terminal_session(session_id, command, cwd)
        
        return JSONResponse(
            status_code=200 if success else 400,
            content={
                "success": success,
                "session_id": session_id,
                "command": command,
                "cwd": cwd,
                "message": "Terminal session started" if success else "Failed to start session"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to start terminal session: {str(e)}"}
        )

@app.get("/terminal/sessions")
async def list_terminal_sessions():
    """List all active terminal sessions"""
    try:
        sessions = terminal_manager.list_active_sessions()
        return JSONResponse(
            status_code=200,
            content={
                "sessions": sessions,
                "total": len(sessions)
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to list sessions: {str(e)}"}
        )

@app.get("/terminal/{session_id}")
async def get_terminal_session_status(session_id: str):
    """Get status of a specific terminal session"""
    try:
        status = terminal_manager.get_session_status(session_id)
        
        if status is None:
            return JSONResponse(
                status_code=404,
                content={"error": f"Session {session_id} not found"}
            )
        
        return JSONResponse(
            status_code=200,
            content={"status": status}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get session status: {str(e)}"}
        )

@app.post("/terminal/{session_id}/terminate")
async def terminate_terminal_session(session_id: str):
    """Terminate a specific terminal session"""
    try:
        await terminal_manager.terminate_session(session_id)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "session_id": session_id,
                "message": "Session terminated"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to terminate session: {str(e)}"}
        )

@app.get("/pipelines/active")
async def get_active_pipelines():
    """Get list of currently active pipeline connections"""
    stats = websocket_manager.get_connection_stats()
    return {
        "active_connections": stats,
        "total_connections": sum(stats.values()),
        "pipeline_count": len([k for k in stats.keys() if k != "all_pipelines"])
    }

@app.websocket("/ws/all")
async def websocket_all_pipelines(websocket: WebSocket):
    """WebSocket endpoint for all pipeline updates - clients connect here to monitor everything"""
    await websocket_manager.connect(websocket, "all_pipelines")
    try:
        while True:
            try:
                data = await websocket.receive_text()
                # Send acknowledgment for any received messages
                await websocket.send_text(json.dumps({
                    "type": "ack", 
                    "message": "Connected to all pipelines - you will receive updates from all active pipelines",
                    "timestamp": time.time(),
                    "connection_stats": websocket_manager.get_connection_stats()
                }))
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket /ws/all error: {e}")
                break
    except WebSocketDisconnect:
        pass
    finally:
        websocket_manager.disconnect(websocket, "all_pipelines")

@app.websocket("/ws/{pipeline_id}")
async def websocket_endpoint(websocket: WebSocket, pipeline_id: str):
    """WebSocket endpoint for specific pipeline updates"""
    await websocket_manager.connect(websocket, pipeline_id)
    try:
        # Just keep the connection alive - no automatic demo messages
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back for ping/pong or send acknowledgment
                await websocket.send_text(json.dumps({
                    "type": "ack", 
                    "message": f"Connected to pipeline {pipeline_id}",
                    "timestamp": time.time()
                }))
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error for {pipeline_id}: {e}")
                break
    except WebSocketDisconnect:
        pass
    finally:
        websocket_manager.disconnect(websocket, pipeline_id)

@app.websocket("/ws/terminal/all")
async def terminal_websocket_all(websocket: WebSocket):
    """WebSocket endpoint for all terminal sessions"""
    await terminal_manager.connect(websocket, "all_terminals")
    try:
        while True:
            try:
                data = await websocket.receive_text()
                # Handle terminal commands or ping/pong
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": time.time()
                    }))
                elif message.get("type") == "list_sessions":
                    sessions = terminal_manager.list_active_sessions()
                    await websocket.send_text(json.dumps({
                        "type": "session_list",
                        "sessions": sessions,
                        "timestamp": time.time()
                    }))
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Terminal WebSocket /ws/terminal/all error: {e}")
                break
    except WebSocketDisconnect:
        pass
    finally:
        terminal_manager.disconnect(websocket, "all_terminals")

@app.websocket("/ws/terminal/{session_id}")
async def terminal_websocket_session(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for specific terminal session"""
    await terminal_manager.connect(websocket, session_id)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "session_id": session_id,
                        "timestamp": time.time()
                    }))
                elif message.get("type") == "start_session":
                    command = message.get("command", "")
                    cwd = message.get("cwd")
                    if command:
                        success = await terminal_manager.start_terminal_session(session_id, command, cwd)
                        await websocket.send_text(json.dumps({
                            "type": "session_start_response",
                            "session_id": session_id,
                            "success": success,
                            "command": command,
                            "timestamp": time.time()
                        }))
                elif message.get("type") == "terminate_session":
                    await terminal_manager.terminate_session(session_id)
                elif message.get("type") == "get_status":
                    status = terminal_manager.get_session_status(session_id)
                    await websocket.send_text(json.dumps({
                        "type": "session_status",
                        "status": status,
                        "timestamp": time.time()
                    }))
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Terminal WebSocket error for {session_id}: {e}")
                break
    except WebSocketDisconnect:
        pass
    finally:
        terminal_manager.disconnect(websocket, session_id)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
