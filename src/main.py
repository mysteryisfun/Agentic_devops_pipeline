"""
Hackademia - AI-Powered Self-Healing CI/CD Pipeline
Main FastAPI application entry point
"""

# Load environment variables FIRST
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any

# Import our agents
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.pipeline_orchestrator import get_pipeline_orchestrator

app = FastAPI(
    title="Hackademia AI Pipeline",
    description="AI-Powered Self-Healing CI/CD Pipeline with Multi-Agent Architecture",
    version="1.0.0"
)

# Get global instances
pipeline = get_pipeline_orchestrator()

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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
