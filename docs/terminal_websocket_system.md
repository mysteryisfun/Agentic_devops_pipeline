# Terminal WebSocket Streaming System

## Overview
Real-time terminal output streaming system that broadcasts command execution output directly to frontend clients via WebSocket connections. This enables live monitoring of pipeline agent activities and manual terminal sessions.

## 🚀 **WebSocket Endpoints**

### **1. All Terminal Sessions**
```
ws://localhost:8000/ws/terminal/all
```
- Receives messages from all active terminal sessions
- Used for global terminal monitoring
- Ideal for admin dashboards

### **2. Specific Terminal Session**
```
ws://localhost:8000/ws/terminal/{session_id}
```
- Connects to a specific terminal session
- Real-time output streaming for that session only
- Used for focused monitoring

## 📊 **WebSocket Message Types**

### **Connection Messages**
```json
{
  "type": "terminal_connected",
  "session_id": "pipeline_123_build",
  "timestamp": 1703123456.789,
  "message": "Connected to terminal session: pipeline_123_build"
}
```

### **Session Start**
```json
{
  "type": "terminal_start", 
  "session_id": "pipeline_123_build",
  "command": "npm run build",
  "cwd": "/path/to/project",
  "timestamp": 1703123456.789
}
```

### **Real-time Output**
```json
{
  "type": "terminal_output",
  "session_id": "pipeline_123_build", 
  "stream": "stdout",
  "output": "Building project...\n",
  "timestamp": 1703123456.789,
  "is_error": false
}
```

### **Error Output**
```json
{
  "type": "terminal_output",
  "session_id": "pipeline_123_build",
  "stream": "stderr", 
  "output": "Warning: deprecated package\n",
  "timestamp": 1703123456.789,
  "is_error": true
}
```

### **Session End**
```json
{
  "type": "terminal_end",
  "session_id": "pipeline_123_build",
  "exit_code": 0,
  "duration": 45.2,
  "timestamp": 1703123456.789
}
```

### **Session Termination**
```json
{
  "type": "terminal_terminating",
  "session_id": "pipeline_123_build", 
  "timestamp": 1703123456.789
}
```

## 🌐 **REST API Endpoints**

### **Start New Terminal Session**
```http
POST /terminal/start
Content-Type: application/json

{
  "session_id": "my_session_123", 
  "command": "python manage.py test",
  "cwd": "/path/to/project"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "my_session_123",
  "command": "python manage.py test",
  "cwd": "/path/to/project",
  "message": "Terminal session started"
}
```

### **List Active Sessions**
```http
GET /terminal/sessions
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "pipeline_123_build",
      "command": "npm run build", 
      "cwd": "/path/to/project",
      "is_running": true,
      "start_time": 1703123456.789,
      "exit_code": null,
      "connections": 2
    }
  ],
  "total": 1
}
```

### **Get Session Status**
```http
GET /terminal/{session_id}
```

**Response:**
```json
{
  "status": {
    "session_id": "pipeline_123_build",
    "command": "npm run build",
    "is_running": false,
    "exit_code": 0,
    "connections": 1
  }
}
```

### **Terminate Session**
```http
POST /terminal/{session_id}/terminate
```

**Response:**
```json
{
  "success": true,
  "session_id": "pipeline_123_build",
  "message": "Session terminated"
}
```

## 🔧 **Frontend Integration Example**

### **JavaScript WebSocket Client**
```javascript
// Connect to specific terminal session
const terminalWs = new WebSocket('ws://localhost:8000/ws/terminal/my_session');

// Handle real-time output
terminalWs.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'terminal_output':
      // Append to terminal display
      appendToTerminal(data.output, data.stream === 'stderr');
      break;
      
    case 'terminal_start':
      console.log(`Started: ${data.command}`);
      break;
      
    case 'terminal_end':
      console.log(`Completed with exit code: ${data.exit_code}`);
      break;
  }
};

// Start a terminal session
async function startSession(command) {
  const response = await fetch('/terminal/start', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      session_id: 'my_session',
      command: command
    })
  });
  
  return response.json();
}
```

### **React Hook Example**
```javascript
import { useEffect, useState } from 'react';

export function useTerminalStream(sessionId) {
  const [output, setOutput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/terminal/${sessionId}`);
    
    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'terminal_output') {
        setOutput(prev => prev + data.output);
      }
    };
    
    return () => ws.close();
  }, [sessionId]);
  
  return { output, isConnected };
}
```

## 🎯 **Pipeline Integration**

The terminal streaming system automatically integrates with the pipeline orchestrator:

```python
# In pipeline agents, terminal streaming starts automatically
terminal_session_id = await pipeline.start_terminal_streaming(
    pipeline_id="repo_123_456",
    command="python manage.py test", 
    stage="test",
    cwd="/path/to/project"
)
```

This creates a terminal session with ID: `repo_123_456_test_1703123456`

## 🔄 **Message Flow**

```
Agent Starts Command → Terminal Session Created → WebSocket Streaming Begins
    ↓
Real-time Output → WebSocket Messages → Frontend Display
    ↓  
Command Completes → Session End Message → Cleanup
```

## 🛡️ **Error Handling**

- **Process Failures**: Captured and streamed as error output
- **WebSocket Disconnections**: Automatic cleanup and session termination
- **Session Cleanup**: Dead connections removed automatically
- **Timeout Protection**: Long-running processes can be terminated

## 🚀 **Features**

✅ **Real-time Streaming**: Live command output  
✅ **Multi-session Support**: Multiple terminals simultaneously  
✅ **Cross-platform**: Works on Windows, macOS, Linux  
✅ **Error Separation**: stdout and stderr differentiation  
✅ **Session Management**: Start, monitor, and terminate sessions  
✅ **Auto-cleanup**: Automatic resource management  
✅ **Pipeline Integration**: Seamless agent command streaming  

## 📝 **Usage Notes**

- **Session IDs** should be unique across the system
- **Long-running commands** are supported with automatic streaming
- **WebSocket connections** are cleaned up when clients disconnect
- **Terminal output** is captured in real-time with minimal latency
- **Command working directory** can be specified per session

The terminal WebSocket system provides complete visibility into all command executions with real-time streaming capabilities!
