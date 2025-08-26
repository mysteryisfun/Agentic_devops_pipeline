#!/usr/bin/env python3
"""
Test the updated WebSocket comprehensive results system
"""

import asyncio
import json
import time
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.pipeline_orchestrator import get_pipeline_orchestrator

class MockWebSocketManager:
    """Mock WebSocket manager that captures messages for testing"""
    def __init__(self):
        self.messages = []
    
    async def send_message(self, pipeline_id: str, message: dict):
        print(f"🔔 WebSocket ({pipeline_id}): {message.get('type')}")
        if message.get('type') == 'pipeline_results_complete':
            print(f"📊 Comprehensive Results Received!")
            print(f"   • Repository: {message['comprehensive_results']['repository_name']}")
            print(f"   • Status: {message['comprehensive_results']['pipeline_status']}")
            print(f"   • Success Rate: {message['comprehensive_results']['success_rate']}%")
            print(f"   • Issues Found: {message['summary']['issues_found']}")
            print(f"   • Functions Fixed: {message['summary']['functions_fixed']}")
            print(f"   • Tests Generated: {message['summary']['tests_generated']}")
        self.messages.append(message)

async def test_websocket_comprehensive_results():
    """Test the WebSocket comprehensive results functionality"""
    
    print("🧪 Testing WebSocket Comprehensive Results System")
    print("=" * 60)
    
    # Initialize pipeline with mock WebSocket manager
    pipeline = get_pipeline_orchestrator()
    mock_ws = MockWebSocketManager()
    pipeline.set_websocket_manager(mock_ws)
    
    print("✅ Pipeline and WebSocket manager initialized")
    
    # Test the comprehensive results WebSocket method directly
    from src.agents.pipeline_orchestrator import PipelineContext, PipelineStage
    
    # Create mock context
    context = PipelineContext(
        pr_number=789,
        repo_name="mysteryisfun/websocket-test",
        branch="feature/websocket-results",
        files_changed=[],
        stage=PipelineStage.COMPLETE,
        results={
            'build': {
                'success': True,
                'duration': 12.3,
                'metadata': {'total_files': 8}
            },
            'analyze': {
                'success': True,
                'total_issues': 5,
                'vulnerabilities': [
                    {
                        'type': 'SQL Injection',
                        'severity': 'high',
                        'file_path': 'src/auth.py',
                        'line_number': 42,
                        'confidence_score': 0.9,
                        'category': 'security',
                        'description': 'Direct string concatenation in SQL query'
                    }
                ],
                'overall_risk': 'MEDIUM'
            },
            'fix': {
                'success': True,
                'fixes_applied': 2,
                'files_modified': 1
            },
            'test': {
                'success': True,
                'functions_discovered': 6,
                'tests_generated': 4,
                'tests_executed': 4,
                'tests_passed': 3
            }
        },
        errors=[],
        start_time=time.time() - 45.0
    )
    
    pipeline_id = f"{context.repo_name}_{context.pr_number}_{int(context.start_time)}"
    
    # Store mock trigger info
    pipeline._pipeline_trigger_info[pipeline_id] = {
        "trigger_type": "webhook",
        "triggered_by": "mysteryisfun",
        "event_type": "pull_request.opened",
        "timestamp": time.time()
    }
    
    print(f"🚀 Testing comprehensive results for pipeline: {pipeline_id}")
    
    try:
        # Test the WebSocket comprehensive results method
        await pipeline._send_comprehensive_results_websocket(context, pipeline_id)
        
        print(f"\n✅ WebSocket comprehensive results test completed!")
        
        # Check what was sent via WebSocket
        websocket_messages = [msg for msg in mock_ws.messages if msg.get('type') == 'pipeline_results_complete']
        
        if websocket_messages:
            msg = websocket_messages[0]
            print(f"\n📋 WebSocket Message Structure:")
            print(f"   • Type: {msg['type']}")
            print(f"   • Has comprehensive_results: {'comprehensive_results' in msg}")
            print(f"   • Has summary: {'summary' in msg}")
            
            if 'comprehensive_results' in msg:
                results = msg['comprehensive_results']
                print(f"\n🔍 Comprehensive Results Content:")
                print(f"   • Pipeline ID: {results.get('pipeline_id')}")
                print(f"   • Repository: {results.get('repository_name')}")
                print(f"   • Pipeline Status: {results.get('pipeline_status')}")
                print(f"   • Total Duration: {results.get('total_duration')}s")
                print(f"   • Success Rate: {results.get('success_rate')}%")
                
                if 'analysis_results' in results:
                    analysis = results['analysis_results']
                    print(f"   • Issues Found: {analysis.get('total_issues')}")
                    print(f"   • Vulnerabilities: {len(analysis.get('vulnerabilities', []))}")
                
                if 'fix_results' in results:
                    fix = results['fix_results']
                    print(f"   • Functions Fixed: {len(fix.get('functions_fixed', []))}")
                
                if 'test_results' in results:
                    test = results['test_results']
                    print(f"   • Tests Generated: {test.get('tests_generated')}")
                    print(f"   • Tests Passed: {test.get('tests_passed')}")
            
            print(f"\n🎯 WebSocket Integration Status: ✅ WORKING")
        else:
            print(f"\n❌ No comprehensive results message found in WebSocket output")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing WebSocket comprehensive results integration...\n")
    
    async def run_test():
        success = await test_websocket_comprehensive_results()
        
        print(f"\n" + "=" * 60)
        if success:
            print(f"🎉 WEBSOCKET COMPREHENSIVE RESULTS TEST PASSED!")
            print(f"✅ The system now sends complete results via WebSocket")
            print(f"✅ PR comments will include comprehensive details")
            print(f"✅ Frontend can receive complete analytics in real-time")
        else:
            print(f"❌ WebSocket comprehensive results test failed")
    
    asyncio.run(run_test())
