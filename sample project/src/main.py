"""
FastAPI Sample Application for CI/CD Pipeline Testing
A complete real-world example with CRUD operations, database, and proper structure.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import structlog
from datetime import datetime
import os

# Import our custom modules
from .models import User, UserCreate, UserUpdate
from .database import get_db, init_db
from .config import settings

# Configure structured logging
logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="Sample API for CI/CD Testing",
    description="A comprehensive FastAPI example with CRUD operations, database integration, and proper structure for testing Build Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and log startup"""
    try:
        await init_db()
        logger.info("Database initialized successfully")
        logger.info(f"API started at {datetime.now()}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Sample API is running!",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "database": "connected",
        "environment": os.getenv("ENV", "development")
    }


@app.get("/users", response_model=List[User])
async def get_users(db=Depends(get_db)):
    """Get all users"""
    try:
        users = await db.get_all_users()
        logger.info(f"Retrieved {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve users")


@app.post("/users", response_model=User)
async def create_user(user: UserCreate, db=Depends(get_db)):
    """Create a new user"""
    try:
        new_user = await db.create_user(user)
        logger.info(f"Created user: {new_user.email}")
        return new_user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=400, detail="Failed to create user")


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, db=Depends(get_db)):
    """Get user by ID"""
    try:
        user = await db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user")


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserUpdate, db=Depends(get_db)):
    """Update user by ID"""
    try:
        updated_user = await db.update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Updated user: {user_id}")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")


@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db=Depends(get_db)):
    """Delete user by ID"""
    try:
        success = await db.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Deleted user: {user_id}")
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")


@app.get("/stats")
async def get_stats(db=Depends(get_db)):
    """Get application statistics"""
    try:
        user_count = await db.count_users()
        return {
            "total_users": user_count,
            "api_version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "status": "operational"
        }
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


# For development - run with uvicorn
def main():
    """Main entry point for console script"""
    import uvicorn
    print("🚀 Starting Sample API for CI/CD Pipeline Testing...")
    print("📋 FastAPI application with CRUD operations")
    print("🔧 Build Agent Compatible: ✅")
    print(f"📍 API will be available at: http://0.0.0.0:8000")
    print(f"📚 Documentation at: http://0.0.0.0:8000/docs")
    print("")
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()