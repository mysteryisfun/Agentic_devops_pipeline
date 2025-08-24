# 🚀 Agentic AI-Powered Self-Healing CI/CD Pipeline

## Overview

The Agentic CI/CD Pipeline is an advanced AI-driven DevOps automation platform that provides intelligent self-healing capabilities for your continuous integration and deployment workflows. The system automatically detects, analyzes, and fixes code issues in real-time using cutting-edge AI agents, ensuring continuous delivery without manual intervention.

## 🌟 Key Features

- **🤖 Multi-Agent Architecture**: Specialized AI agents for build, analysis, fixing, and testing
- **🔄 Self-Healing Pipeline**: Automatically detects and resolves issues
- **📡 Real-Time Streaming**: Live terminal output and pipeline status via WebSocket
- **🔍 Intelligent Analysis**: Advanced vulnerability detection and code quality assessment
- **⚡ Instant Fixes**: AI-powered automatic code remediation
- **🌐 WebSocket Integration**: Real-time communication with frontend applications
- **📊 Comprehensive Reporting**: Detailed pipeline results and analytics

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub PR     │───▶│  Pipeline Agent  │───▶│   Build Agent   │
│   Webhook       │    │  Orchestrator    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Test Agent    │◀───│  Analysis Agent  │───▶│    Fix Agent    │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                     ┌──────────────────┐
                     │  WebSocket API   │
                     │  Real-time UI    │
                     └──────────────────┘
```

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.8+**
- **Node.js 16+** (for frontend)
- **Git**
- **GitHub Account** with repository access
- **Google AI Studio API Key** (Gemini)

### 1. Clone Repository

```bash
git clone https://github.com/mysteryisfun/Agentic_devops_pipeline.git
cd Agentic_devops_pipeline
```

### 2. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Frontend dependencies (if using)
cd frontend
npm install
cd ..
```

### 3. Environment Configuration

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` file:

```env
# GitHub Configuration
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_PAT=ghp_your_personal_access_token

# Google AI (Gemini) Configuration
GOOGLE_API_KEY=your_gemini_api_key_here

# Server Configuration
PORT=8000
HOST=0.0.0.0

# Webhook Configuration
WEBHOOK_SECRET=your_webhook_secret_here
```

### 4. Start the Application

```bash
python src/main.py
```

The server will start on `http://localhost:8000`

## 🌐 Ngrok Setup for Webhooks

To receive GitHub webhooks during development, you'll need to expose your local server using ngrok:

### 1. Install Ngrok

```bash
# Using npm
npm install -g ngrok

# Or download from https://ngrok.com/download
```

### 2. Start Ngrok Tunnel

```bash
# Start ngrok on port 8000 (same as your FastAPI server)
ngrok http 8000
```

You'll see output like:
```
Session Status    online
Account           your-email@example.com
Version           3.x.x
Region            United States (us)
Forwarding        https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the `https://abc123.ngrok.io` URL - this is your public webhook URL.**

### 3. Configure GitHub Webhook

1. **Go to your GitHub repository**
2. **Navigate to Settings → Webhooks → Add webhook**
3. **Configure the webhook:**
   - **Payload URL**: `https://abc123.ngrok.io/webhook/github`
   - **Content type**: `application/json`
   - **Secret**: Enter the same secret from your `.env` file
   - **Events**: Select "Pull requests" and "Push"
   - **Active**: ✅ Checked

### 4. Test Webhook

Create a pull request in your repository. You should see webhook events in your terminal and the pipeline should automatically start.

## 📡 WebSocket Endpoints

The system provides real-time communication through multiple WebSocket endpoints:

### Pipeline WebSockets

- **All Pipelines**: `ws://localhost:8000/ws/all`
  - Receives updates from all active pipelines
  - Ideal for monitoring dashboards

- **Specific Pipeline**: `ws://localhost:8000/ws/{pipeline_id}`
  - Connects to a specific pipeline instance
  - Real-time status updates and results

### Terminal WebSockets

- **All Terminals**: `ws://localhost:8000/ws/terminal/all`
  - Live output from all terminal sessions
  - Global terminal monitoring

- **Specific Terminal**: `ws://localhost:8000/ws/terminal/{session_id}`
  - Real-time output from specific command execution
  - Perfect for debugging and monitoring

### Example WebSocket Message

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

## 🔌 REST API Endpoints

### Webhook Endpoints
- `POST /webhook/github` - GitHub webhook receiver
- `POST /webhook/results` - Pipeline results webhook

### Pipeline Management
- `GET /pipelines/active` - List active pipelines
- `GET /pipeline/{pipeline_id}/status` - Get pipeline status

### Terminal Management
- `POST /terminal/start` - Start new terminal session
- `GET /terminal/sessions` - List active terminal sessions
- `GET /terminal/{session_id}` - Get terminal session status
- `POST /terminal/{session_id}/terminate` - Terminate session

## 🔄 Pipeline Flow

1. **Webhook Trigger**: GitHub PR/Push event triggers the pipeline
2. **Build Stage**: Clone repository and prepare environment
3. **Analysis Stage**: AI-powered code analysis and vulnerability detection
4. **Fix Stage**: Automatic issue resolution using AI
5. **Test Stage**: Validation and testing of fixes
6. **Results**: Comprehensive results sent via WebSocket
7. **GitHub Update**: Automatic PR comments and status updates

## 📊 Real-Time Monitoring

### Frontend Integration Example

```javascript
// Connect to pipeline WebSocket
const pipelineWs = new WebSocket('ws://localhost:8000/ws/all');

pipelineWs.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'pipeline_start':
      console.log(`Pipeline ${data.pipeline_id} started`);
      break;
    case 'stage_complete':
      console.log(`Stage ${data.stage} completed`);
      break;
    case 'pipeline_results_complete':
      console.log('Pipeline finished:', data.results);
      break;
  }
};

// Connect to terminal WebSocket
const terminalWs = new WebSocket('ws://localhost:8000/ws/terminal/all');

terminalWs.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'terminal_output') {
    appendToTerminal(data.output, data.stream === 'stderr');
  }
};
```

## 🛡️ Security Features

- **Webhook Signature Verification**: Validates GitHub webhook authenticity
- **Environment Variable Protection**: Sensitive data stored securely
- **Token-based Authentication**: Secure GitHub API access
- **CORS Configuration**: Proper cross-origin resource sharing

## 📁 Project Structure

```
Agentic_devops_pipeline/
├── src/
│   ├── agents/           # AI agent implementations
│   ├── config/           # Configuration management
│   ├── services/         # External service integrations
│   ├── utils/           # Utility functions and helpers
│   └── main.py          # FastAPI application entry point
├── tests/               # Test suites
├── docs/               # Documentation
├── frontend/           # Frontend application (optional)
├── requirements.txt    # Python dependencies
└── .env.example       # Environment configuration template
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_complete_pipeline.py

# Test WebSocket functionality
python tests/test_terminal_websocket_streaming.py
```

## 🚀 Deployment

### Production Setup

1. **Use a proper reverse proxy** (nginx/Apache)
2. **Configure SSL certificates** for HTTPS
3. **Set up proper domain** instead of ngrok
4. **Configure environment variables** securely
5. **Use process managers** like PM2 or systemd

### Docker Deployment (Optional)

```bash
# Build Docker image
docker build -t agentic-pipeline .

# Run container
docker run -p 8000:8000 --env-file .env agentic-pipeline
```

## 📚 Documentation

- [WebSocket Protocol Guide](docs/websocket_complete_protocol.md)
- [Terminal Streaming System](docs/terminal_websocket_system.md)
- [Pipeline Architecture](docs/masterplan.md)
- [API Documentation](docs/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/mysteryisfun/Agentic_devops_pipeline/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mysteryisfun/Agentic_devops_pipeline/discussions)
- **Documentation**: [Project Docs](docs/)

## ⭐ Acknowledgments

- **Google AI (Gemini)** for powerful language model capabilities
- **FastAPI** for the excellent web framework
- **GitHub** for webhook and API support
- **Ngrok** for seamless local development tunneling

---

**🔥 Ready to revolutionize your DevOps workflow with AI-powered automation!**
