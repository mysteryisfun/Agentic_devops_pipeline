"""
Simple Server Starter
Starts the FastAPI server with correct environment setup
"""

import os
import sys
import subprocess

def start_server():
    """Start the FastAPI server properly"""
    
    # Get project root (where this script is located)
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_root, 'src')
    
    print(f"🚀 Starting FastAPI server...")
    print(f"   Project root: {project_root}")
    print(f"   Source dir: {src_dir}")
    
    # Verify src directory exists
    if not os.path.exists(src_dir):
        print(f"❌ Source directory not found: {src_dir}")
        return False
    
    # Change to src directory
    os.chdir(src_dir)
    
    # Add project root to Python path
    os.environ['PYTHONPATH'] = project_root
    
    # Start server
    cmd = ["python", "main.py"]
    
    try:
        print(f"   Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⏹️  Server stopped by user")
        return True
    
    return True

if __name__ == "__main__":
    start_server()
