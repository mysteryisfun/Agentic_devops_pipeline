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
except ModuleNotFoundError:
    # Fallback for when running from src directory
    from agents.pipeline_orchestrator import get_pipeline_orchestrator

app = FastAPI(
    title="Hackademia AI Pipeline",
    description="AI-Powered Self-Healing CI/CD Pipeline with Multi-Agent Architecture",
    version="1.0.0"
)

# Get global instances
pipeline = get_pipeline_orchestrator()

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
        
        print(f"🚀 Processing PR #{pr_number}: {pr_title} in {repo_name}")
        
        # Start multi-agent pipeline
        pipeline_id = await pipeline.start_pipeline(pr_number, repo_name)
        
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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
