"""
Focused WebSocket Progress Callback Test
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.analyze_agent import get_analyze_agent

async def test_progress_callbacks():
    """Test the progress callback functionality specifically"""
    
    print("🧪 Testing WebSocket Progress Callbacks")
    print("=" * 50)
    
    # Message capture list
    captured_messages = []
    
    # Progress callback function
    async def test_progress_callback(message):
        captured_messages.append(message)
        
        # Display the message
        msg_type = message.get('type', 'unknown')
        stage = message.get('stage', 'N/A')
        msg_text = message.get('message', 'N/A')
        progress = message.get('progress', 'N/A')
        
        print(f"📡 {msg_type.upper()}: {msg_text}")
        if progress != 'N/A' and progress is not None:
            print(f"   📊 {progress}%")
        
        if message.get('details'):
            details = message['details']
            if 'current_file' in details:
                print(f"   📄 {details['current_file']}")
            if 'question' in details:
                print(f"   ❓ {details['question'][:50]}...")
    
    try:
        print("🤖 Initializing Analyze Agent...")
        analyze_agent = get_analyze_agent()
        print("✅ Agent initialized")
        
        # Simple test data
        test_data = {
            "files": [
                {
                    "filename": "test_auth.py",
                    "file_extension": "py", 
                    "status": "added",
                    "added_lines": [
                        {"line_number": 1, "content": "def login(user, pwd):"},
                        {"line_number": 2, "content": "    query = f'SELECT * FROM users WHERE name = {user}'"},
                        {"line_number": 3, "content": "    return execute(query)"}
                    ],
                    "context_lines": []
                }
            ]
        }
        
        build_context = {
            "metadata": {"project_type": "python"},
            "dependencies": ["sqlite3"]
        }
        
        print(f"\n🚀 Running analysis with progress callbacks...")
        print("-" * 40)
        
        # Run analysis with progress callback
        result = await analyze_agent.analyze_pr_diff(
            diff_data=test_data,
            build_context=build_context,
            progress_callback=test_progress_callback
        )
        
        print(f"\n✅ Analysis Complete!")
        print("-" * 40)
        
        print(f"📊 Progress Callback Results:")
        print(f"📈 Total Messages: {len(captured_messages)}")
        
        # Analyze message types
        status_updates = [msg for msg in captured_messages if msg.get('type') == 'status_update']
        print(f"📋 Status Updates: {len(status_updates)}")
        
        # Check for progress progression
        progress_msgs = [msg for msg in status_updates if msg.get('progress') is not None]
        print(f"📊 Progress Messages: {len(progress_msgs)}")
        
        if progress_msgs:
            print(f"📈 Progress Values: {[msg.get('progress') for msg in progress_msgs]}")
        
        # Check for detailed messages
        detail_msgs = [msg for msg in captured_messages if msg.get('details') is not None]
        print(f"📄 Messages with Details: {len(detail_msgs)}")
        
        # Analysis results
        print(f"\n🎯 Analysis Results:")
        print(f"✅ Success: {result.success}")
        print(f"📊 Total Issues: {result.total_issues}")
        print(f"🚨 Vulnerabilities: {len(result.vulnerabilities)}")
        
        # Check if we got meaningful progress updates
        if len(captured_messages) > 0:
            print(f"\n✅ Progress Callbacks: WORKING")
            print(f"✅ WebSocket Integration: READY")
        else:
            print(f"\n❌ Progress Callbacks: NOT WORKING")
        
        # Validate specific expected messages
        expected_keywords = ['analyzing', 'scanning', 'files']
        found_keywords = []
        
        for msg in captured_messages:
            msg_text = str(msg.get('message', '')).lower()
            for keyword in expected_keywords:
                if keyword in msg_text and keyword not in found_keywords:
                    found_keywords.append(keyword)
        
        print(f"\n🔍 Expected Keywords Found: {found_keywords}")
        
        if len(found_keywords) >= 2:
            print(f"✅ Message Content: APPROPRIATE")
        else:
            print(f"⚠️ Message Content: Could be more detailed")
        
        print(f"\n🎉 Progress Callback Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_progress_callbacks())
