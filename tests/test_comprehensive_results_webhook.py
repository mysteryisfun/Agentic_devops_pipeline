#!/usr/bin/env python3
"""
Test script for the comprehensive pipeline results webhook system
Demonstrates the complete JSON structure and webhook functionality
"""

import json
import asyncio
import time
from datetime import datetime
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils.results_webhook import (
    PipelineResultsComplete, 
    WebhookTrigger, 
    BuildResults, 
    AnalysisResults,
    VulnerabilityDetail,
    FixResults, 
    FixDetail,
    TestResults, 
    TestFunction,
    ResourceMetrics,
    PipelineStatus,
    ResultsWebhookSender,
    ResultsAggregator
)

def create_sample_results() -> PipelineResultsComplete:
    """Create a comprehensive sample results structure"""
    
    # Mock trigger info
    trigger = WebhookTrigger(
        trigger_type="webhook",
        triggered_by="mysteryisfun",
        event_type="pull_request.opened",
        timestamp=datetime.now().isoformat()
    )
    
    # Mock build results
    build_results = BuildResults(
        success=True,
        duration=15.5,
        files_downloaded=12,
        file_types_processed=[".py", ".js", ".json", ".md"],
        build_errors=[],
        files_analyzed=12
    )
    
    # Mock vulnerabilities
    vulnerabilities = [
        VulnerabilityDetail(
            type="SQL Injection",
            description="Direct string concatenation in SQL query",
            severity="critical",
            file_path="src/database/user_service.py",
            line_number=45,
            confidence_score=0.95,
            category="security"
        ),
        VulnerabilityDetail(
            type="XSS Vulnerability",
            description="Unescaped user input in HTML template",
            severity="high",
            file_path="src/templates/user_profile.py",
            line_number=78,
            confidence_score=0.87,
            category="security"
        ),
        VulnerabilityDetail(
            type="Performance Issue",
            description="N+1 query pattern detected",
            severity="medium",
            file_path="src/models/order.py",
            line_number=123,
            confidence_score=0.72,
            category="performance"
        )
    ]
    
    # Mock analysis results
    analysis_results = AnalysisResults(
        success=True,
        duration=32.7,
        files_analyzed=12,
        total_issues=8,
        vulnerabilities=vulnerabilities,
        severity_breakdown={"critical": 1, "high": 2, "medium": 3, "low": 2},
        categories_breakdown={"security": 3, "performance": 2, "code_quality": 3},
        overall_risk_level="HIGH",
        ai_confidence_score=0.85,
        recommendations=[
            "Use parameterized queries to prevent SQL injection",
            "Implement proper input sanitization",
            "Optimize database queries to reduce N+1 patterns"
        ]
    )
    
    # Mock fix details
    fix_details = [
        FixDetail(
            function_name="get_user_data",
            file_path="src/database/user_service.py",
            fix_type="sql_injection_prevention",
            description="Replaced string concatenation with parameterized query",
            confidence_score=0.93,
            lines_changed=3
        ),
        FixDetail(
            function_name="render_profile",
            file_path="src/templates/user_profile.py", 
            fix_type="xss_prevention",
            description="Added HTML escaping for user input",
            confidence_score=0.89,
            lines_changed=2
        )
    ]
    
    # Mock fix results
    fix_results = FixResults(
        success=True,
        duration=18.3,
        files_modified=2,
        functions_fixed=fix_details,
        commit_sha="abc123def456",
        commit_message="🤖 AI Fix: Security vulnerabilities resolved [skip-pipeline]",
        total_lines_changed=5,
        fix_confidence_average=0.91
    )
    
    # Mock test functions
    test_functions = [
        TestFunction(
            function_name="test_get_user_data_sql_injection",
            file_path="tests/test_user_service.py",
            test_name="test_sql_injection_prevention",
            status="passed",
            execution_time=0.25,
            error_message=None
        ),
        TestFunction(
            function_name="test_render_profile_xss",
            file_path="tests/test_user_profile.py",
            test_name="test_xss_prevention",
            status="passed",
            execution_time=0.18,
            error_message=None
        ),
        TestFunction(
            function_name="test_order_performance",
            file_path="tests/test_order.py", 
            test_name="test_query_optimization",
            status="failed",
            execution_time=1.2,
            error_message="AssertionError: Query count exceeded threshold: 15 > 5"
        )
    ]
    
    # Mock test results
    test_results = TestResults(
        success=True,
        duration=45.6,
        functions_discovered=8,
        test_functions=test_functions,
        tests_generated=6,
        tests_executed=3,
        tests_passed=2,
        tests_failed=1,
        test_coverage_percentage=78.5,
        execution_time_total=1.63
    )
    
    # Mock resource metrics
    resource_metrics = ResourceMetrics(
        total_api_calls=47,
        gemini_api_calls=23,
        github_api_calls=24,
        total_processing_time=112.1,
        memory_usage_peak=256.7
    )
    
    # Create complete results
    return PipelineResultsComplete(
        pipeline_id="mysteryisfun/test-repo_123_1703123456",
        repository_name="mysteryisfun/test-repo",
        branch_name="feature/user-authentication",
        pr_number=123,
        pipeline_status=PipelineStatus.SUCCESS,
        start_timestamp=datetime.now().isoformat(),
        end_timestamp=datetime.now().isoformat(),
        total_duration=112.1,
        trigger_info=trigger,
        build_results=build_results,
        analysis_results=analysis_results,
        fix_results=fix_results,
        test_results=test_results,
        success_rate=75.0,  # 3/4 stages successful
        resource_metrics=resource_metrics,
        previous_run_comparison=None,
        errors=["Test execution timeout on performance test"],
        warnings=["API rate limit approaching"]
    )

async def test_webhook_system():
    """Test the complete webhook system"""
    
    print("🧪 Testing Comprehensive Pipeline Results Webhook System")
    print("=" * 60)
    
    # Create sample results
    print("📊 Creating sample pipeline results...")
    sample_results = create_sample_results()
    
    # Display the JSON structure
    print("\n📋 Complete Results JSON Structure:")
    print("-" * 40)
    
    # Use the built-in asdict function from dataclasses
    from dataclasses import asdict
    try:
        results_dict = asdict(sample_results)
        
        # Handle enums in the dict
        def serialize_enums(obj):
            if hasattr(obj, 'value'):
                return obj.value
            elif isinstance(obj, dict):
                return {key: serialize_enums(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [serialize_enums(item) for item in obj]
            else:
                return obj
        
        json_results = serialize_enums(results_dict)
        
        # Pretty print the JSON (truncated for readability)
        json_str = json.dumps(json_results, indent=2, default=str)
        if len(json_str) > 3000:
            print(json_str[:3000] + "\n... (truncated for readability)")
        else:
            print(json_str)
        
        print(f"\n📏 Total JSON size: {len(json_str)} characters")
        
    except Exception as e:
        print(f"Error serializing results: {e}")
        # Fallback to basic info
        print("Basic pipeline info:")
        print(f"  Pipeline ID: {sample_results.pipeline_id}")
        print(f"  Repository: {sample_results.repository_name}")
        print(f"  Status: {sample_results.pipeline_status.value}")
    
    # Key metrics summary
    print("\n📈 Key Pipeline Metrics:")
    print(f"   • Repository: {sample_results.repository_name}")
    print(f"   • PR Number: {sample_results.pr_number}")
    print(f"   • Pipeline Status: {sample_results.pipeline_status.value}")
    print(f"   • Total Duration: {sample_results.total_duration:.1f}s")
    print(f"   • Success Rate: {sample_results.success_rate:.1f}%")
    print(f"   • Issues Found: {len(sample_results.analysis_results.vulnerabilities)}")
    print(f"   • Functions Fixed: {len(sample_results.fix_results.functions_fixed)}")
    print(f"   • Tests Generated: {sample_results.test_results.tests_generated}")
    print(f"   • Tests Passed: {sample_results.test_results.tests_passed}")
    
    # Test webhook sender (without actually sending)
    print("\n📤 Testing Webhook Sender...")
    webhook_sender = ResultsWebhookSender()  # No URL configured, will save to file instead
    
    # Save results to file as demonstration
    webhook_sender.save_results_to_file(sample_results, "sample_pipeline_results.json")
    print("✅ Sample results saved to 'sample_pipeline_results.json'")
    
    print("\n🎯 Webhook System Test Complete!")
    print("\n💡 Next Steps:")
    print("   1. Set PIPELINE_RESULTS_WEBHOOK_URL environment variable")
    print("   2. Configure your external webhook endpoint")
    print("   3. The system will automatically send results after each pipeline")
    print("   4. Use /webhook/results endpoint to receive results in your application")

if __name__ == "__main__":
    asyncio.run(test_webhook_system())
