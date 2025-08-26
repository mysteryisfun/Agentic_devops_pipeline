"""
Pipeline Results Webhook System
Handles comprehensive pipeline result aggregation and webhook delivery
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
import os
from enum import Enum

class PipelineStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"

class SeverityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class WebhookTrigger:
    """Information about what triggered the pipeline"""
    trigger_type: str  # "webhook", "manual", "scheduled"
    triggered_by: str  # GitHub username or system
    event_type: str    # "pull_request.opened", "pull_request.synchronize"
    timestamp: str

@dataclass
class BuildResults:
    """Build stage results"""
    success: bool
    duration: float
    files_downloaded: int
    file_types_processed: List[str]
    build_errors: List[str]
    files_analyzed: int

@dataclass
class VulnerabilityDetail:
    """Individual vulnerability details"""
    type: str
    description: str
    severity: str
    file_path: str
    line_number: int
    confidence_score: float
    category: str  # "security", "performance", "code_quality"

@dataclass
class AnalysisResults:
    """Analysis stage results"""
    success: bool
    duration: float
    files_analyzed: int
    total_issues: int
    vulnerabilities: List[VulnerabilityDetail]
    severity_breakdown: Dict[str, int]  # critical: 2, high: 5, etc.
    categories_breakdown: Dict[str, int]  # security: 3, performance: 2, etc.
    overall_risk_level: str
    ai_confidence_score: float
    recommendations: List[str]

@dataclass
class FixDetail:
    """Individual fix details"""
    function_name: str
    file_path: str
    fix_type: str
    description: str
    confidence_score: float
    lines_changed: int

@dataclass
class FixResults:
    """Fix stage results"""
    success: bool
    duration: float
    files_modified: int
    functions_fixed: List[FixDetail]
    commit_sha: Optional[str]
    commit_message: str
    total_lines_changed: int
    fix_confidence_average: float

@dataclass
class TestFunction:
    """Individual test function details"""
    function_name: str
    file_path: str
    test_name: str
    status: str  # "passed", "failed", "skipped"
    execution_time: float
    error_message: Optional[str]

@dataclass
class TestResults:
    """Test stage results"""
    success: bool
    duration: float
    functions_discovered: int
    test_functions: List[TestFunction]
    tests_generated: int
    tests_executed: int
    tests_passed: int
    tests_failed: int
    test_coverage_percentage: float
    execution_time_total: float

@dataclass
class ResourceMetrics:
    """Resource usage metrics"""
    total_api_calls: int
    gemini_api_calls: int
    github_api_calls: int
    total_processing_time: float
    memory_usage_peak: float
    
@dataclass
class PipelineResultsComplete:
    """Complete pipeline results structure"""
    # Pipeline Metadata
    pipeline_id: str
    repository_name: str
    branch_name: str
    pr_number: int
    pipeline_status: PipelineStatus
    
    # Timestamps
    start_timestamp: str
    end_timestamp: str
    total_duration: float
    
    # Webhook trigger information
    trigger_info: WebhookTrigger
    
    # Stage Results
    build_results: BuildResults
    analysis_results: AnalysisResults
    fix_results: FixResults
    test_results: TestResults
    
    # Overall Metrics
    success_rate: float  # Percentage of stages completed successfully
    resource_metrics: ResourceMetrics
    
    # Comparison (if available)
    previous_run_comparison: Optional[Dict[str, Any]]
    
    # Error Information
    errors: List[str]
    warnings: List[str]

class ResultsWebhookSender:
    """Handles sending comprehensive results via webhook"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv('PIPELINE_RESULTS_WEBHOOK_URL')
        
    async def send_results(self, results: PipelineResultsComplete) -> bool:
        """Send comprehensive results to configured webhook"""
        if not self.webhook_url:
            print("⚠️ No webhook URL configured for results")
            return False
            
        try:
            # Convert dataclass to dict for JSON serialization
            results_dict = asdict(results)
            
            # Add metadata
            payload = {
                "event_type": "pipeline_complete",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0",
                "results": results_dict
            }
            
            print(f"🚀 Sending pipeline results to webhook: {self.webhook_url[:50]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Hackademia-Pipeline/1.0"
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        print(f"✅ Results webhook sent successfully")
                        return True
                    else:
                        print(f"❌ Webhook failed with status {response.status}")
                        response_text = await response.text()
                        print(f"Response: {response_text}")
                        return False
                        
        except asyncio.TimeoutError:
            print(f"❌ Webhook timeout after 30 seconds")
            return False
        except Exception as e:
            print(f"❌ Error sending webhook: {str(e)}")
            return False
    
    def save_results_to_file(self, results: PipelineResultsComplete, filepath: Optional[str] = None):
        """Save results to JSON file as backup"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"pipeline_results_{results.pipeline_id.replace('/', '_')}_{timestamp}.json"
            
        try:
            # Use asdict and handle enums properly
            from dataclasses import asdict
            results_dict = asdict(results)
            
            # Convert enums to their values
            def serialize_enums(obj):
                if hasattr(obj, 'value'):
                    return obj.value
                elif isinstance(obj, dict):
                    return {key: serialize_enums(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [serialize_enums(item) for item in obj]
                else:
                    return obj
            
            serialized_results = serialize_enums(results_dict)
            
            with open(filepath, 'w') as f:
                json.dump(serialized_results, f, indent=2, default=str)
            print(f"✅ Results saved to {filepath}")
        except Exception as e:
            print(f"❌ Error saving results to file: {str(e)}")

class ResultsAggregator:
    """Aggregates results from all pipeline stages"""
    
    @staticmethod
    def aggregate_pipeline_results(context, pipeline_id: str, trigger_info: Dict[str, Any]) -> PipelineResultsComplete:
        """Convert pipeline context to comprehensive results"""
        
        # Calculate timestamps
        start_time = context.start_time
        end_time = time.time()
        duration = end_time - start_time
        
        # Build Results
        build_data = context.results.get('build', {})
        build_results = BuildResults(
            success=build_data.get('success', False),
            duration=build_data.get('duration', 0.0),
            files_downloaded=build_data.get('metadata', {}).get('total_files', 0),
            file_types_processed=build_data.get('metadata', {}).get('file_types', []),
            build_errors=build_data.get('errors', []),
            files_analyzed=build_data.get('metadata', {}).get('total_files', 0)
        )
        
        # Analysis Results
        analysis_data = context.results.get('analyze', {})
        vulnerabilities = []
        if analysis_data.get('vulnerabilities'):
            vulnerabilities = [
                VulnerabilityDetail(
                    type=v.get('type', 'Unknown'),
                    description=v.get('description', ''),
                    severity=v.get('severity', 'unknown'),
                    file_path=v.get('file_path', ''),
                    line_number=v.get('line_number', 0),
                    confidence_score=v.get('confidence_score', 0.0),
                    category=v.get('category', 'unknown')
                )
                for v in analysis_data['vulnerabilities']
            ]
        
        # Calculate severity breakdown
        severity_breakdown = {}
        categories_breakdown = {}
        for v in vulnerabilities:
            severity_breakdown[v.severity] = severity_breakdown.get(v.severity, 0) + 1
            categories_breakdown[v.category] = categories_breakdown.get(v.category, 0) + 1
        
        analysis_results = AnalysisResults(
            success=analysis_data.get('success', False),
            duration=analysis_data.get('duration', 0.0),
            files_analyzed=analysis_data.get('files_analyzed', 0),
            total_issues=analysis_data.get('total_issues', 0),
            vulnerabilities=vulnerabilities,
            severity_breakdown=severity_breakdown,
            categories_breakdown=categories_breakdown,
            overall_risk_level=analysis_data.get('overall_risk', 'UNKNOWN'),
            ai_confidence_score=analysis_data.get('confidence_score', 0.0),
            recommendations=analysis_data.get('recommendations', [])
        )
        
        # Fix Results
        fix_data = context.results.get('fix', {})
        fix_details = []
        if fix_data.get('fixes'):
            fix_details = [
                FixDetail(
                    function_name=f.get('function_name', ''),
                    file_path=f.get('file_path', ''),
                    fix_type=f.get('fix_type', ''),
                    description=f.get('description', ''),
                    confidence_score=f.get('confidence_score', 0.0),
                    lines_changed=f.get('lines_changed', 0)
                )
                for f in fix_data['fixes']
            ]
        
        fix_results = FixResults(
            success=fix_data.get('success', False),
            duration=fix_data.get('duration', 0.0),
            files_modified=fix_data.get('files_modified', 0),
            functions_fixed=fix_details,
            commit_sha=fix_data.get('commit_sha'),
            commit_message=fix_data.get('commit_message', ''),
            total_lines_changed=sum(f.lines_changed for f in fix_details),
            fix_confidence_average=sum(f.confidence_score for f in fix_details) / len(fix_details) if fix_details else 0.0
        )
        
        # Test Results
        test_data = context.results.get('test', {})
        test_functions = []
        if test_data.get('generated_tests'):
            test_functions = [
                TestFunction(
                    function_name=t.get('function_name', ''),
                    file_path=t.get('filename', ''),
                    test_name=t.get('test_name', ''),
                    status='generated',  # We'll update this after execution
                    execution_time=0.0,
                    error_message=None
                )
                for t in test_data['generated_tests']
            ]
        
        test_results = TestResults(
            success=test_data.get('success', False),
            duration=test_data.get('duration', 0.0),
            functions_discovered=test_data.get('functions_discovered', 0),
            test_functions=test_functions,
            tests_generated=test_data.get('tests_generated', 0),
            tests_executed=test_data.get('tests_executed', 0),
            tests_passed=test_data.get('tests_passed', 0),
            tests_failed=test_data.get('tests_executed', 0) - test_data.get('tests_passed', 0),
            test_coverage_percentage=test_data.get('coverage_percentage', 0.0),
            execution_time_total=test_data.get('execution_time', 0.0)
        )
        
        # Resource Metrics (placeholder - we'd need to track these)
        resource_metrics = ResourceMetrics(
            total_api_calls=0,  # We'd need to track this
            gemini_api_calls=0,
            github_api_calls=0,
            total_processing_time=duration,
            memory_usage_peak=0.0
        )
        
        # Determine overall pipeline status
        stages_success = [
            build_results.success,
            analysis_results.success,
            fix_results.success,
            test_results.success
        ]
        
        if all(stages_success):
            status = PipelineStatus.SUCCESS
        elif any(stages_success):
            status = PipelineStatus.PARTIAL
        else:
            status = PipelineStatus.FAILED
            
        success_rate = sum(stages_success) / len(stages_success) * 100
        
        # Create trigger info
        webhook_trigger = WebhookTrigger(
            trigger_type=trigger_info.get('trigger_type', 'webhook'),
            triggered_by=trigger_info.get('triggered_by', 'system'),
            event_type=trigger_info.get('event_type', 'pull_request'),
            timestamp=datetime.fromtimestamp(start_time).isoformat()
        )
        
        return PipelineResultsComplete(
            pipeline_id=pipeline_id,
            repository_name=context.repo_name,
            branch_name=context.branch,
            pr_number=context.pr_number,
            pipeline_status=status,
            start_timestamp=datetime.fromtimestamp(start_time).isoformat(),
            end_timestamp=datetime.fromtimestamp(end_time).isoformat(),
            total_duration=duration,
            trigger_info=webhook_trigger,
            build_results=build_results,
            analysis_results=analysis_results,
            fix_results=fix_results,
            test_results=test_results,
            success_rate=success_rate,
            resource_metrics=resource_metrics,
            previous_run_comparison=None,  # We'd implement this later
            errors=context.errors,
            warnings=[]  # We'd need to track warnings
        )

# Global results webhook sender
results_webhook_sender = ResultsWebhookSender()

def get_results_webhook_sender() -> ResultsWebhookSender:
    """Get the global results webhook sender"""
    return results_webhook_sender
