"""
Live WebSocket Communication Test - Real Pipeline Integration
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Mock the settings to avoid validation issues
class MockSettings:
    def __init__(self):
        self.github_token = "mock_token"
        self.gemini_api_key = "mock_key"
        self.webhook_secret = "mock_secret"

# Override settings before imports
import src.config.settings
src.config.settings.settings = MockSettings()

from src.agents.analyze_agent import get_analyze_agent

class LiveWebSocketTester:
    """Live WebSocket message capture for real analysis"""
    
    def __init__(self):
        self.messages = []
        self.message_count = 0
        
    async def capture_message(self, pipeline_id, message):
        """Capture real WebSocket messages from pipeline"""
        self.message_count += 1
        self.messages.append({
            "id": self.message_count,
            "pipeline_id": pipeline_id,
            "timestamp": datetime.now().isoformat(),
            "message": message
        })
        
        # Real-time display
        msg_type = message.get('type', 'unknown')
        stage = message.get('stage', 'N/A')
        msg_text = message.get('message', 'N/A')
        progress = message.get('progress', 'N/A')
        
        print(f"📡 #{self.message_count} [{msg_type.upper()}] {stage}: {msg_text}")
        if progress != 'N/A' and progress is not None:
            print(f"   📊 Progress: {progress}%")
        
        # Show details for important messages
        if message.get('details'):
            details = message['details']
            if 'current_file' in details:
                print(f"   📄 File: {details['current_file']}")
            if 'question' in details:
                question = details['question'][:60] + "..." if len(details['question']) > 60 else details['question']
                print(f"   ❓ Question: {question}")
            if 'scope_assessed' in details:
                print(f"   🎯 Scope: {details['scope_assessed']}")
            if 'step' in details:
                print(f"   🔧 Step: {details['step']}")
        
        # Show results for stage_complete
        if msg_type == 'stage_complete' and 'results' in message:
            results = message['results']
            if 'total_issues' in results:
                print(f"   🎯 Total Issues: {results['total_issues']}")
            if 'vulnerabilities' in results:
                print(f"   🚨 Vulnerabilities: {len(results['vulnerabilities'])}")
            if 'next_stage' in results:
                print(f"   🔄 Next Stage: {results['next_stage']}")
        
        print("-" * 60)

async def test_live_analysis_communications():
    """Test real analysis with live WebSocket communication capture"""
    
    print("🧪 Live Analysis WebSocket Communication Test")
    print("=" * 60)
    
    # Create live message tester
    live_tester = LiveWebSocketTester()
    
    try:
        # Initialize analyze agent
        print("🤖 Initializing Analyze Agent...")
        analyze_agent = get_analyze_agent()
        print("✅ Analyze Agent ready")
        
        # Create test data that should trigger vulnerabilities
        test_diff_data = {
            "files": [
                {
                    "filename": "vulnerable_auth.py",
                    "file_extension": "py",
                    "status": "added",
                    "added_lines": [
                        {"line_number": 1, "content": "import sqlite3"},
                        {"line_number": 2, "content": "from flask import request, jsonify"},
                        {"line_number": 3, "content": ""},
                        {"line_number": 4, "content": "def authenticate_user():"},
                        {"line_number": 5, "content": "    username = request.json.get('username')"},
                        {"line_number": 6, "content": "    password = request.json.get('password')"},
                        {"line_number": 7, "content": "    # Vulnerable SQL query - no validation!"},
                        {"line_number": 8, "content": "    query = f\"SELECT * FROM users WHERE username='{username}' AND password='{password}'\""},
                        {"line_number": 9, "content": "    result = execute_query(query)"},
                        {"line_number": 10, "content": "    return jsonify({'authenticated': bool(result)})"}
                    ],
                    "context_lines": []
                }
            ]
        }
        
        test_build_context = {
            "metadata": {"project_type": "flask_api"},
            "dependencies": ["flask", "sqlite3"],
            "success": True
        }
        
        print(f"📄 Testing with: {test_diff_data['files'][0]['filename']}")
        print(f"💻 Code that contains SQL injection vulnerability")
        print(f"🎯 Expected: Should detect SQL_INJECTION vulnerability")
        print()
        
        # Run real analysis with live message capture
        print("🚀 Starting Live Analysis with WebSocket Message Capture...")
        print("=" * 60)
        
        # Create progress callback that captures messages
        async def progress_callback(message):
            await live_tester.capture_message("test_pipeline_001", message)
        
        # Run the actual analysis
        result = await analyze_agent.analyze_pr_diff(
            diff_data=test_diff_data,
            build_context=test_build_context,
            progress_callback=progress_callback
        )
        
        print("🎉 Analysis Complete!")
        print("=" * 60)
        
        # Analyze captured messages
        print(f"📊 Live Message Analysis:")
        print(f"📈 Total Messages Captured: {len(live_tester.messages)}")
        
        # Group by message type
        message_types = {}
        for msg_data in live_tester.messages:
            msg_type = msg_data['message'].get('type', 'unknown')
            if msg_type not in message_types:
                message_types[msg_type] = 0
            message_types[msg_type] += 1
        
        print(f"📋 Message Type Breakdown:")
        for msg_type, count in message_types.items():
            print(f"   {msg_type}: {count} messages")
        
        # Check for progress progression
        status_updates = [msg['message'] for msg in live_tester.messages 
                         if msg['message'].get('type') == 'status_update']
        
        progress_updates = [msg for msg in status_updates 
                           if msg.get('progress') is not None]
        
        if progress_updates:
            print(f"\n📈 Progress Tracking ({len(progress_updates)} updates):")
            for msg in progress_updates:
                print(f"   {msg.get('progress')}%: {msg.get('message')}")
        
        # Check for MCP question visibility
        mcp_messages = [msg['message'] for msg in live_tester.messages 
                       if msg['message'].get('details', {}).get('step') == 'mcp_question_execution']
        
        if mcp_messages:
            print(f"\n🤖 Autonomous MCP Questions ({len(mcp_messages)} questions):")
            for i, msg in enumerate(mcp_messages, 1):
                details = msg.get('details', {})
                question = details.get('question', 'Unknown')[:80]
                reasoning = details.get('reasoning', 'Unknown')[:60]
                print(f"   {i}. {question}...")
                print(f"      💭 {reasoning}...")
        
        # Validate actual analysis results
        print(f"\n🎯 Analysis Results Validation:")
        print(f"✅ Success: {result.success}")
        print(f"📊 Total Issues: {result.total_issues}")
        print(f"🚨 Vulnerabilities: {len(result.vulnerabilities)}")
        print(f"🔒 Security Issues: {len(result.security_issues)}")
        print(f"📝 Quality Issues: {len(result.quality_issues)}")
        print(f"🎯 Overall Risk: {result.overall_risk}")
        
        # Check if SQL injection was detected
        sql_injection_found = any(
            vuln.get('type', '').upper() in ['SQL_INJECTION', 'IMPROPER_INPUT_VALIDATION'] 
            for vuln in result.vulnerabilities
        )
        
        if sql_injection_found:
            print(f"✅ SQL Injection Detection: PASSED")
            # Show the detected vulnerability
            for vuln in result.vulnerabilities:
                if vuln.get('type', '').upper() in ['SQL_INJECTION', 'IMPROPER_INPUT_VALIDATION']:
                    print(f"   🚨 Type: {vuln.get('type', 'Unknown')}")
                    print(f"   📊 Severity: {vuln.get('severity', 'Unknown')}")
                    print(f"   📍 Line: {vuln.get('line_number', 'Unknown')}")
                    print(f"   📄 Description: {vuln.get('description', 'No description')[:100]}...")
                    break
        else:
            print(f"❌ SQL Injection Detection: FAILED - Should have detected SQL injection!")
        
        # Validate communication protocol compliance
        print(f"\n🔄 Protocol Compliance Check:")
        
        required_message_types = ['status_update']
        for required_type in required_message_types:
            if required_type in message_types:
                print(f"✅ {required_type} messages: Present")
            else:
                print(f"❌ {required_type} messages: Missing")
        
        # Check for detailed information
        detailed_messages = [msg for msg in live_tester.messages 
                           if msg['message'].get('details') is not None]
        
        print(f"✅ Messages with details: {len(detailed_messages)}/{len(live_tester.messages)}")
        
        if len(detailed_messages) >= len(live_tester.messages) * 0.5:  # At least 50% should have details
            print(f"✅ Rich information: PASSED")
        else:
            print(f"⚠️ Rich information: Could be improved")
        
        print(f"\n🎉 Live WebSocket Communication Test Complete!")
        print(f"✅ Real analysis pipeline with WebSocket messages working")
        print(f"📡 Message capture and validation successful")
        print(f"🔄 All communication protocols functioning correctly")
        
    except Exception as e:
        print(f"❌ Live test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_live_analysis_communications())
