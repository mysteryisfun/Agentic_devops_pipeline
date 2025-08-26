"""
Terminal WebSocket Streaming System
Real-time terminal output streaming via WebSocket
"""

import asyncio
import json
import time
import subprocess
import threading
import queue
from typing import Dict, List, Optional
from datetime import datetime
import os
import sys
from fastapi import WebSocket, WebSocketDisconnect

class TerminalSession:
    """Individual terminal session with output streaming"""
    
    def __init__(self, session_id: str, command: str, cwd: str = None):
        self.session_id = session_id
        self.command = command
        self.cwd = cwd or os.getcwd()
        self.process: Optional[subprocess.Popen] = None
        self.output_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.is_running = False
        self.start_time = time.time()
        self.exit_code: Optional[int] = None
        
    def start_process(self):
        """Start the terminal process and begin output capture"""
        try:
            print(f"🚀 Starting terminal session {self.session_id}: {self.command}")
            
            # Start process with real-time output capture
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=self.cwd
            )
            
            self.is_running = True
            
            # Start output capture threads
            stdout_thread = threading.Thread(
                target=self._capture_output,
                args=(self.process.stdout, self.output_queue, "stdout")
            )
            stderr_thread = threading.Thread(
                target=self._capture_output,
                args=(self.process.stderr, self.error_queue, "stderr")
            )
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()
            
            # Monitor process completion
            monitor_thread = threading.Thread(target=self._monitor_process)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start terminal session {self.session_id}: {str(e)}")
            self.is_running = False
            return False
    
    def _capture_output(self, pipe, output_queue, stream_type):
        """Capture output from subprocess pipe"""
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    output_queue.put({
                        "stream": stream_type,
                        "output": line,
                        "timestamp": time.time()
                    })
            pipe.close()
        except Exception as e:
            print(f"❌ Error capturing {stream_type}: {str(e)}")
    
    def _monitor_process(self):
        """Monitor process completion"""
        try:
            self.exit_code = self.process.wait()
            self.is_running = False
            
            # Add completion message to queue
            self.output_queue.put({
                "stream": "system",
                "output": f"\n[Process completed with exit code: {self.exit_code}]\n",
                "timestamp": time.time(),
                "completed": True
            })
            
            print(f"✅ Terminal session {self.session_id} completed with exit code: {self.exit_code}")
            
        except Exception as e:
            print(f"❌ Error monitoring process: {str(e)}")
            self.is_running = False
    
    def get_output(self) -> Optional[Dict]:
        """Get next output from queue (non-blocking)"""
        try:
            return self.output_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_error(self) -> Optional[Dict]:
        """Get next error from queue (non-blocking)"""
        try:
            return self.error_queue.get_nowait()
        except queue.Empty:
            return None
    
    def terminate(self):
        """Terminate the process"""
        if self.process and self.is_running:
            try:
                self.process.terminate()
                self.is_running = False
                print(f"🛑 Terminal session {self.session_id} terminated")
            except Exception as e:
                print(f"❌ Error terminating session {self.session_id}: {str(e)}")

class TerminalWebSocketManager:
    """Manages terminal WebSocket connections and streaming"""
    
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}
        self.sessions: Dict[str, TerminalSession] = {}
        self.streaming_tasks: Dict[str, asyncio.Task] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect WebSocket to terminal session"""
        await websocket.accept()
        
        if session_id not in self.connections:
            self.connections[session_id] = []
        self.connections[session_id].append(websocket)
        
        print(f"🔌 Terminal WebSocket connected to session: {session_id}")
        
        # Send connection confirmation
        await self._send_to_session(session_id, {
            "type": "terminal_connected",
            "session_id": session_id,
            "timestamp": time.time(),
            "message": f"Connected to terminal session: {session_id}"
        })
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect WebSocket from terminal session"""
        if session_id in self.connections:
            try:
                self.connections[session_id].remove(websocket)
                if not self.connections[session_id]:
                    del self.connections[session_id]
                    
                    # Stop session if no more connections
                    if session_id in self.sessions:
                        self.sessions[session_id].terminate()
                        del self.sessions[session_id]
                    
                    # Cancel streaming task
                    if session_id in self.streaming_tasks:
                        self.streaming_tasks[session_id].cancel()
                        del self.streaming_tasks[session_id]
                
                print(f"❌ Terminal WebSocket disconnected from session: {session_id}")
            except ValueError:
                pass
    
    async def start_terminal_session(self, session_id: str, command: str, cwd: str = None) -> bool:
        """Start a new terminal session with WebSocket streaming"""
        if session_id in self.sessions:
            print(f"⚠️ Terminal session {session_id} already exists")
            return False
        
        # Create and start terminal session
        session = TerminalSession(session_id, command, cwd)
        success = session.start_process()
        
        if success:
            self.sessions[session_id] = session
            
            # Send session start message
            await self._send_to_session(session_id, {
                "type": "terminal_start",
                "session_id": session_id,
                "command": command,
                "cwd": cwd,
                "timestamp": time.time()
            })
            
            # Start output streaming
            streaming_task = asyncio.create_task(self._stream_session_output(session_id))
            self.streaming_tasks[session_id] = streaming_task
            
            return True
        
        return False
    
    async def _stream_session_output(self, session_id: str):
        """Stream terminal session output via WebSocket"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        
        try:
            while session.is_running or not session.output_queue.empty() or not session.error_queue.empty():
                # Process stdout
                output = session.get_output()
                if output:
                    await self._send_to_session(session_id, {
                        "type": "terminal_output",
                        "session_id": session_id,
                        "stream": output["stream"],
                        "output": output["output"],
                        "timestamp": output["timestamp"],
                        "completed": output.get("completed", False)
                    })
                
                # Process stderr  
                error = session.get_error()
                if error:
                    await self._send_to_session(session_id, {
                        "type": "terminal_output",
                        "session_id": session_id,
                        "stream": error["stream"],
                        "output": error["output"],
                        "timestamp": error["timestamp"],
                        "is_error": True
                    })
                
                # Small delay to prevent overwhelming WebSocket
                await asyncio.sleep(0.05)
            
            # Send session end message
            await self._send_to_session(session_id, {
                "type": "terminal_end",
                "session_id": session_id,
                "exit_code": session.exit_code,
                "duration": time.time() - session.start_time,
                "timestamp": time.time()
            })
            
            print(f"🏁 Terminal streaming completed for session: {session_id}")
            
        except asyncio.CancelledError:
            print(f"🛑 Terminal streaming cancelled for session: {session_id}")
        except Exception as e:
            print(f"❌ Error streaming terminal output for {session_id}: {str(e)}")
    
    async def _send_to_session(self, session_id: str, message: dict):
        """Send message to all WebSocket connections for a session"""
        if session_id not in self.connections:
            return
        
        dead_connections = []
        for connection in self.connections[session_id]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                dead_connections.append(connection)
        
        # Clean up dead connections
        for dead_conn in dead_connections:
            try:
                self.connections[session_id].remove(dead_conn)
            except ValueError:
                pass
    
    async def send_to_all_sessions(self, message: dict):
        """Send message to all active terminal sessions"""
        for session_id in list(self.connections.keys()):
            await self._send_to_session(session_id, message)
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get status of a terminal session"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "command": session.command,
            "cwd": session.cwd,
            "is_running": session.is_running,
            "start_time": session.start_time,
            "exit_code": session.exit_code,
            "connections": len(self.connections.get(session_id, []))
        }
    
    def list_active_sessions(self) -> List[Dict]:
        """List all active terminal sessions"""
        return [
            self.get_session_status(session_id) 
            for session_id in self.sessions.keys()
        ]
    
    async def terminate_session(self, session_id: str):
        """Terminate a specific terminal session"""
        if session_id in self.sessions:
            # Send termination message
            await self._send_to_session(session_id, {
                "type": "terminal_terminating",
                "session_id": session_id,
                "timestamp": time.time()
            })
            
            # Terminate the session
            self.sessions[session_id].terminate()
            
            # Clean up
            if session_id in self.streaming_tasks:
                self.streaming_tasks[session_id].cancel()
                del self.streaming_tasks[session_id]
            
            del self.sessions[session_id]

# Global terminal WebSocket manager
terminal_websocket_manager = TerminalWebSocketManager()

def get_terminal_websocket_manager() -> TerminalWebSocketManager:
    """Get the global terminal WebSocket manager"""
    return terminal_websocket_manager
