"""
Multi-Agent Pipeline Orchestrator
Coordinates the workflow between Build, Analyze, Fix, and Test agents
"""

import asyncio
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import json
import time
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.agents.build_agent import get_build_agent
from src.agents.analyze_agent import get_analyze_agent
from src.agents.fix_agent import get_fix_agent
from src.agents.test_agent import get_test_agent
from src.utils.github_client import get_github_client

class PipelineStage(Enum):
    """Pipeline execution stages"""
    PENDING = "pending"
    BUILD = "build"
    ANALYZE = "analyze" 
    FIX = "fix"
    TEST = "test"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass
class PipelineContext:
    """Context shared between all agents"""
    pr_number: int
    repo_name: str
    branch: str
    files_changed: List[Dict[str, Any]]
    stage: PipelineStage
    results: Dict[str, Any]
    errors: List[str]
    start_time: float
    
class MultiAgentPipeline:
    """
    Orchestrates the multi-agent workflow:
    Build → Analyze → Fix → Test
    """
    
    def __init__(self):
        self.build_agent = get_build_agent()
        self.analyze_agent = get_analyze_agent()
        self.fix_agent = get_fix_agent()
        self.test_agent = get_test_agent()
        self.github_client = get_github_client()
        self.active_pipelines: Dict[str, PipelineContext] = {}
        self.websocket_manager = None
        
    def set_websocket_manager(self, manager):
        """Set the WebSocket manager for real-time updates"""
        self.websocket_manager = manager
        
    async def send_websocket_message(self, pipeline_id: str, message: dict):
        """Send WebSocket message if manager is available"""
        if self.websocket_manager:
            await self.websocket_manager.send_message(pipeline_id, message)
    
    async def start_pipeline(self, pr_number: int, repo_name: str) -> str:
        """
        Start the multi-agent pipeline for a PR
        
        Returns:
            pipeline_id: Unique identifier for tracking
        """
        pipeline_id = f"{repo_name}_{pr_number}_{int(time.time())}"
        
        try:
            print(f"🚀 Starting pipeline {pipeline_id}")
            
            # Get PR information
            pr = self.github_client.get_pull_request(repo_name, pr_number)
            if not pr:
                raise Exception(f"Could not access PR #{pr_number}")
            
            # Get changed files
            files_changed = self.github_client.get_pr_files(repo_name, pr_number)
            
            # Initialize pipeline context
            context = PipelineContext(
                pr_number=pr_number,
                repo_name=repo_name,
                branch=pr.head.ref,
                files_changed=files_changed,
                stage=PipelineStage.PENDING,
                results={},
                errors=[],
                start_time=time.time()
            )
            
            self.active_pipelines[pipeline_id] = context
            
            # Send pipeline_start WebSocket message
            await self.send_websocket_message(pipeline_id, {
                "type": "pipeline_start",
                "pipeline_id": pipeline_id,
                "pr_number": pr_number,
                "repo_name": repo_name,
                "branch": context.branch,
                "stages": ["build", "analyze", "fix", "test"]
            })
            
            # Start async pipeline execution
            asyncio.create_task(self._execute_pipeline(pipeline_id))
            
            return pipeline_id
            
        except Exception as e:
            error_msg = f"Failed to start pipeline: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    async def _execute_pipeline(self, pipeline_id: str):
        """Execute the complete multi-agent pipeline"""
        context = self.active_pipelines[pipeline_id]
        
        try:
            print(f"🔄 Executing pipeline {pipeline_id}")
            
            # Get pipeline_id for WebSocket messages
            pipeline_id = f"{context.repo_name}_{context.pr_number}_{int(context.start_time)}"
            
            # Stage 1: Build Agent (REAL)
            await self._run_build_stage(context)
            
            # Stage 2: Analyze Agent (REAL) - Only if build succeeded
            if context.stage != PipelineStage.FAILED:
                await self._run_analyze_stage(context)
            
            # Stage 3: Fix Agent (NEW) - Only if analyze found issues
            if context.stage != PipelineStage.FAILED and context.results.get('analyze', {}).get('total_issues', 0) > 0:
                await self._run_fix_stage(context, pipeline_id)
            
            # Stage 4: Test Agent (Complete 3-phase implementation)
            if context.stage != PipelineStage.FAILED:
                await self._run_test_stage_complete(context, pipeline_id)
            
            # Complete pipeline
            context.stage = PipelineStage.COMPLETE
            
            # Send pipeline_complete message
            total_duration = time.time() - context.start_time
            await self.send_websocket_message(pipeline_id, {
                "type": "pipeline_complete",
                "status": "success",
                "total_duration": round(total_duration, 2),
                "summary": {
                    "build": {"status": "success" if context.results.get('build', {}).get('success', False) else "failed"},
                    "analyze": {"status": "success" if context.results.get('analyze', {}).get('success', False) else "failed", "issues_found": context.results.get('analyze', {}).get('total_issues', 0)},
                    "fix": {"status": "success" if context.results.get('fix', {}).get('success', False) else "skipped", "fixes_applied": context.results.get('fix', {}).get('fixes_applied', 0)},
                    "test": {
                        "status": "success" if context.results.get('test', {}).get('success', False) else "failed", 
                        "functions_discovered": context.results.get('test', {}).get('functions_discovered', 0), 
                        "questions_generated": context.results.get('test', {}).get('questions_generated', 0),
                        "tests_generated": context.results.get('test', {}).get('tests_generated', 0),
                        "tests_executed": context.results.get('test', {}).get('tests_executed', 0),
                        "tests_passed": context.results.get('test', {}).get('tests_passed', 0),
                        "execution_success": context.results.get('test', {}).get('execution_success', False)
                    }
                }
            })
            
            await self._post_results_to_pr(context)
            
            print(f"✅ Pipeline {pipeline_id} completed successfully")
            
            # Clean up completed pipeline from active pipelines
            if pipeline_id in self.active_pipelines:
                del self.active_pipelines[pipeline_id]
                print(f"🧹 Cleaned up pipeline {pipeline_id} from active pipelines")
            
        except Exception as e:
            context.stage = PipelineStage.FAILED
            context.errors.append(str(e))
            
            # Send error message  
            total_duration = time.time() - context.start_time
            await self.send_websocket_message(pipeline_id, {
                "type": "error",
                "stage": "pipeline",
                "message": f"Pipeline failed: {str(e)}",
                "error_code": "PIPELINE_FAILED",
                "details": str(e)
            })
            
            await self.send_websocket_message(pipeline_id, {
                "type": "pipeline_complete", 
                "status": "failed",
                "total_duration": round(total_duration, 2),
                "summary": {
                    "build": {"status": "failed"},
                    "analyze": {"status": "skipped"},
                    "fix": {"status": "skipped"},
                    "test": {"status": "skipped"}
                }
            })
            
            print(f"❌ Pipeline {pipeline_id} failed: {str(e)}")
            await self._post_results_to_pr(context)
            
            # Clean up failed pipeline from active pipelines  
            if pipeline_id in self.active_pipelines:
                del self.active_pipelines[pipeline_id]
                print(f"🧹 Cleaned up failed pipeline {pipeline_id} from active pipelines")
    
    async def _run_build_stage(self, context: PipelineContext):
        """Run Build Agent stage"""
        print(f"🔨 Running Build stage for {context.repo_name}#{context.pr_number}")
        context.stage = PipelineStage.BUILD
        
        # Get pipeline_id for WebSocket messages
        pipeline_id = f"{context.repo_name}_{context.pr_number}_{int(context.start_time)}"
        
        # Send stage_start message
        await self.send_websocket_message(pipeline_id, {
            "type": "stage_start",
            "stage": "build",
            "stage_index": 1,
            "message": f"Starting build stage for PR #{context.pr_number}..."
        })
        
        stage_start_time = time.time()
        
        # Use new PR branch cloning and building
        build_result = await self.build_agent.build_pr_branch(
            repo_name=context.repo_name,
            branch=context.branch,
            pr_number=context.pr_number,
            progress_callback=lambda msg: self.send_websocket_message(pipeline_id, msg)
        )
        
        # Store results
        context.results['build'] = {
            "success": build_result.success,
            "metadata": build_result.metadata,
            "errors": build_result.errors,
            "warnings": build_result.warnings,
            "dependencies": build_result.dependencies,
            "file_info": build_result.file_info,
            "build_logs": build_result.build_logs,
            "agent_context": self.build_agent.prepare_context_for_agents(build_result, repo_name=context.repo_name, pr_number=context.pr_number)
        }
        
        stage_duration = time.time() - stage_start_time
        
        # Send stage_complete message
        await self.send_websocket_message(pipeline_id, {
            "type": "stage_complete",
            "stage": "build",
            "status": "success" if build_result.success else "failed",
            "duration": round(stage_duration, 2),
            "results": {
                "build_logs": build_result.build_logs[-5:] if build_result.build_logs else [],
                "errors": build_result.errors,
                "metadata": {
                    "files_analyzed": len(build_result.file_info),
                    "dependencies_found": len(build_result.dependencies),
                    "project_type": build_result.metadata.get("project_type", "unknown")
                }
            }
        })
        
        print(f"✅ Build stage completed - Success: {build_result.success}")
        if build_result.build_logs:
            print("📋 Build logs:")
            for log in build_result.build_logs[-3:]:  # Show last 3 logs
                print(f"   {log}")
        
        if not build_result.success:
            print(f"❌ Build errors: {build_result.errors}")
            # Don't continue to other stages if build failed
            context.stage = PipelineStage.FAILED
            context.errors.extend(build_result.errors)
    
    async def _run_analyze_stage(self, context: PipelineContext):
        """Run Analyze Agent stage with real AI analysis"""
        print(f"🔍 Running AI Analysis stage for {context.repo_name}#{context.pr_number}")
        context.stage = PipelineStage.ANALYZE
        
        # Get pipeline_id for WebSocket messages
        pipeline_id = f"{context.repo_name}_{context.pr_number}_{int(context.start_time)}"
        
        # Send stage_start message
        await self.send_websocket_message(pipeline_id, {
            "type": "stage_start",
            "stage": "analyze",
            "stage_index": 2,
            "message": f"🧠 Starting AI-powered code analysis..."
        })
        
        stage_start_time = time.time()
        
        try:
            # Get PR diff data for analysis
            diff_data = self.github_client.get_pr_diff_content(context.repo_name, context.pr_number)
            
            if not diff_data:
                raise Exception("Could not retrieve PR diff data")
            
            # Get build context
            build_context = context.results.get('build', {})
            
            # Run AI analysis
            analysis_result = await self.analyze_agent.analyze_pr_diff(
                diff_data=diff_data,
                build_context=build_context,
                progress_callback=lambda msg: self.send_websocket_message(pipeline_id, msg)
            )
            
            # Store results
            context.results['analyze'] = {
                "success": analysis_result.success,
                "vulnerabilities": analysis_result.vulnerabilities,
                "security_issues": analysis_result.security_issues,
                "quality_issues": analysis_result.quality_issues,
                "recommendations": analysis_result.recommendations,
                "overall_risk": analysis_result.overall_risk,
                "files_analyzed": analysis_result.files_analyzed,
                "total_issues": analysis_result.total_issues,
                "confidence_scores": analysis_result.confidence_scores,
                "fix_agent_context": self.analyze_agent.prepare_context_for_fix_agent(analysis_result)
            }
            
            stage_duration = time.time() - stage_start_time
            
            # Send stage_complete message with comprehensive analysis results
            await self.send_websocket_message(pipeline_id, {
                "type": "stage_complete",
                "stage": "analyze",
                "status": "success" if analysis_result.success else "failed",
                "duration": round(stage_duration, 2),
                "results": {
                    "files_analyzed": analysis_result.files_analyzed,
                    "total_issues": analysis_result.total_issues,
                    "vulnerabilities": [
                        {
                            "type": vuln.get("type", "UNKNOWN"),
                            "severity": vuln.get("severity", "UNKNOWN"), 
                            "file": vuln.get("file", "unknown"),
                            "line": vuln.get("line_number", 0),
                            "description": vuln.get("description", "No description")[:100] + "..." if len(vuln.get("description", "")) > 100 else vuln.get("description", "")
                        }
                        for vuln in analysis_result.vulnerabilities[:5]  # Limit to top 5 for WebSocket message size
                    ],
                    "security_issues": [
                        {
                            "type": issue.get("type", "UNKNOWN"),
                            "severity": issue.get("severity", "UNKNOWN"),
                            "file": issue.get("file", "unknown"), 
                            "line": issue.get("line_number", 0)
                        }
                        for issue in analysis_result.security_issues[:5]
                    ],
                    "quality_issues": [
                        {
                            "type": issue.get("type", "UNKNOWN"),
                            "severity": issue.get("severity", "UNKNOWN"),
                            "file": issue.get("file", "unknown"),
                            "line": issue.get("line_number", 0)
                        }
                        for issue in analysis_result.quality_issues[:5]
                    ],
                    "recommendations": analysis_result.recommendations[:5],
                    "next_stage": "fix" if analysis_result.total_issues > 0 else "test",
                    "metadata": {
                        "mcp_questions_asked": getattr(analysis_result, 'mcp_questions_asked', 'unknown'),
                        "context_gathered": getattr(analysis_result, 'context_gathered', 'unknown'),
                        "analysis_time": round(stage_duration, 2),
                        "ai_model": "Gemini 2.5 Flash",
                        "overall_risk": analysis_result.overall_risk,
                        "confidence_scores": analysis_result.confidence_scores
                    }
                }
            })
            
            print(f"✅ Analysis stage completed - {analysis_result.total_issues} issues found")
            print(f"🎯 Risk Level: {analysis_result.overall_risk}")
            
            if not analysis_result.success:
                print(f"⚠️ Analysis completed with warnings")
                context.stage = PipelineStage.FAILED
                context.errors.append("Analysis stage had issues")
        
        except Exception as e:
            print(f"❌ Analysis stage failed: {str(e)}")
            stage_duration = time.time() - stage_start_time
            
            # Send error message
            await self.send_websocket_message(pipeline_id, {
                "type": "error",
                "stage": "analyze",
                "message": f"Analysis failed: {str(e)}",
                "error_code": "ANALYZE_FAILED",
                "details": str(e)
            })
            
            # Send stage_complete with failure
            await self.send_websocket_message(pipeline_id, {
                "type": "stage_complete",
                "stage": "analyze", 
                "status": "failed",
                "duration": round(stage_duration, 2),
                "results": {"error": str(e)}
            })
            
            context.stage = PipelineStage.FAILED
            context.errors.append(f"Analysis failed: {str(e)}")
            
            # Store failed result
            context.results['analyze'] = {
                "success": False,
                "error": str(e),
                "total_issues": 0,
                "message": f"AI analysis failed: {str(e)}"
            }
    
    async def _run_fix_stage(self, context: PipelineContext, pipeline_id: str):
        """Run Fix Agent stage for high-confidence issues"""
        print(f"🔧 Running AI Fix stage for {context.repo_name}#{context.pr_number}")
        context.stage = PipelineStage.FIX
        
        stage_start_time = time.time()
        
        try:
            # Get analysis results
            analysis_result = context.results.get('analyze', {})
            
            if not analysis_result.get('success', False):
                print("⏭️ Skipping fix stage - analysis failed")
                return
            
            # Convert analysis results to AnalysisResult object for Fix Agent
            from src.agents.analyze_agent import AnalysisResult
            analysis_obj = AnalysisResult(
                success=analysis_result.get('success', False),
                vulnerabilities=analysis_result.get('vulnerabilities', []),
                security_issues=analysis_result.get('security_issues', []),
                quality_issues=analysis_result.get('quality_issues', []),
                recommendations=analysis_result.get('recommendations', []),
                overall_risk=analysis_result.get('overall_risk', 'LOW'),
                files_analyzed=analysis_result.get('files_analyzed', 0),
                total_issues=analysis_result.get('total_issues', 0),
                confidence_scores=analysis_result.get('confidence_scores', {})
            )
            
            # Run Fix Agent
            fix_result = await self.fix_agent.apply_fixes(
                analysis_result=analysis_obj,
                repo_name=context.repo_name,
                branch=context.branch,
                progress_callback=lambda msg: self.send_websocket_message(pipeline_id, msg)
            )
            
            # Store results
            context.results['fix'] = {
                "success": fix_result.success,
                "fixes_applied": fix_result.fixes_applied,
                "files_modified": fix_result.files_modified,
                "commits_made": fix_result.commits_made,
                "fixes_summary": fix_result.fixes_summary,
                "errors": fix_result.errors,
                "duration": fix_result.duration,
                "message": f"Applied {fix_result.fixes_applied} fixes to {fix_result.files_modified} files"
            }
            
            print(f"✅ Fix stage completed - {fix_result.fixes_applied} fixes applied")
            
            if not fix_result.success:
                print(f"⚠️ Fix stage completed with errors: {fix_result.errors}")
        
        except Exception as e:
            print(f"❌ Fix stage failed: {str(e)}")
            stage_duration = time.time() - stage_start_time
            
            # Send error message
            await self.send_websocket_message(pipeline_id, {
                "type": "error",
                "stage": "fix",
                "message": f"Fix stage failed: {str(e)}",
                "error_code": "FIX_FAILED",
                "details": str(e)
            })
            
            # Send stage_complete with failure
            await self.send_websocket_message(pipeline_id, {
                "type": "stage_complete",
                "stage": "fix",
                "status": "failed",
                "duration": round(stage_duration, 2),
                "results": {"error": str(e)}
            })
            
            context.stage = PipelineStage.FAILED
            context.errors.append(f"Fix failed: {str(e)}")
            
            # Store failed result
            context.results['fix'] = {
                "success": False,
                "error": str(e),
                "fixes_applied": 0,
                "message": f"AI fixing failed: {str(e)}"
            }
    
    async def _run_test_stage_complete(self, context: PipelineContext, pipeline_id: str):
        """Run complete Test Agent: Phase 1 (function discovery) + Phase 2 (CodeRM-8B test generation) + Phase 3 (execution)"""
        print(f"🧪 Running Complete Test Stage for {context.repo_name}#{context.pr_number}")
        context.stage = PipelineStage.TEST
        
        try:
            # Send stage start message
            await self.send_websocket_message(pipeline_id, {
                "type": "stage_start",
                "stage": "test",
                "stage_index": 4,
                "message": f"Starting test generation stage for PR #{context.pr_number}...",
                "details": {
                    "phase": "starting",
                    "description": "AI-powered unit test generation with CodeRM-8B"
                }
            })
            
            stage_start_time = time.time()
            
            # Get diff data and fix results from previous stages
            diff_data = context.results.get('build', {}).get('agent_context', {})
            if not diff_data or not diff_data.get('changed_files'):
                print(f"⚠️ No diff data from build agent, fetching from GitHub directly...")
                # Fallback: Get diff data from GitHub directly
                diff_data = self.github_client.get_pr_diff_content(context.repo_name, context.pr_number)
                print(f"📊 Fetched diff data: {len(diff_data.get('changed_files', []))} changed files")
            else:
                print(f"📊 Using build agent diff data: {len(diff_data.get('changed_files', []))} changed files")
            
            fix_results = context.results.get('fix', {})
            
            # Phase 1: Function discovery and question generation
            print(f"🔍 Starting Phase 1: Function Discovery...")
            test_result_phase1 = await self.test_agent.run_test_stage_phase1(
                diff_data=diff_data,
                fix_results=fix_results,
                repo_name=context.repo_name,
                branch=context.branch,
                progress_callback=lambda msg: self.send_websocket_message(pipeline_id, msg)
            )
            
            if not test_result_phase1.success:
                print(f"❌ Test Agent Phase 1 failed: {test_result_phase1.errors}")
                
                # Store failed results
                context.results['test'] = {
                    "success": False,
                    "phase": "phase1_failed",
                    "functions_discovered": 0,
                    "questions_generated": 0,
                    "tests_generated": 0,
                    "errors": test_result_phase1.errors,
                    "duration": time.time() - stage_start_time
                }
                
                await self.send_websocket_message(pipeline_id, {
                    "type": "stage_complete",
                    "stage": "test",
                    "status": "failed",
                    "duration": round(time.time() - stage_start_time, 2),
                    "message": f"❌ Test generation failed in Phase 1: {'; '.join(test_result_phase1.errors)}"
                })
                return
            
            print(f"✅ Phase 1 completed: {test_result_phase1.functions_discovered} functions, {test_result_phase1.questions_generated} questions")
            
            # Initialize generated_tests to prevent reference error
            generated_tests = []
            
            # Phase 2: CodeRM-8B test generation
            if test_result_phase1.functions_with_questions:
                print(f"🤖 Starting Phase 2: CodeRM-8B Test Generation...")
                
                await self.send_websocket_message(pipeline_id, {
                    "type": "status_update",
                    "stage": "test",
                    "status": "in_progress",
                    "message": f"🤖 Phase 2: Generating tests with CodeRM-8B for {len(test_result_phase1.functions_with_questions)} functions...",
                    "progress": 65,
                    "details": {
                        "phase": "test_generation",
                        "functions_to_test": len(test_result_phase1.functions_with_questions)
                    }
                })
                
                generated_tests = await self.test_agent.run_test_stage_phase2(
                    function_questions=test_result_phase1.functions_with_questions,
                    progress_callback=lambda msg: self.send_websocket_message(pipeline_id, msg)
                )
                
                print(f"✅ Phase 2 completed: {len(generated_tests)} tests generated")
            
            # Phase 3: Test execution
            if generated_tests:
                print(f"🧪 Starting Phase 3: Test Execution...")
                
                await self.send_websocket_message(pipeline_id, {
                    "type": "status_update",
                    "stage": "test",
                    "status": "in_progress",
                    "message": f"🧪 Phase 3: Executing {len(generated_tests)} generated unit tests...",
                    "progress": 80,
                    "details": {
                        "phase": "test_execution",
                        "tests_to_execute": len(generated_tests)
                    }
                })
                
                execution_result = await self.test_agent.run_test_stage_phase3(
                    generated_tests=generated_tests,
                    progress_callback=lambda msg: self.send_websocket_message(pipeline_id, msg)
                )
                
                print(f"✅ Phase 3 completed: Tests executed with {execution_result.success} success")
                
                # Update results with execution data
                tests_executed = len(generated_tests)
                tests_passed = tests_executed if execution_result.success else 0
                
                execution_summary = f"Executed {tests_executed} test files"
                
            else:
                print(f"⚠️ No generated tests to execute, skipping Phase 3")
                execution_result = None
                tests_executed = 0
                tests_passed = 0
                execution_summary = "No tests to execute"
            
            # Store complete results (all 3 phases)
            context.results['test'] = {
                "success": True,
                "phase": "complete_with_execution",
                "functions_discovered": test_result_phase1.functions_discovered,
                "questions_generated": test_result_phase1.questions_generated,
                "tests_generated": len(generated_tests),
                "tests_executed": tests_executed,
                "tests_passed": tests_passed,
                "execution_success": execution_result.success if execution_result else False,
                "functions_with_questions": [
                    {
                        "filename": fq.function.filename,
                        "function_name": fq.function.function_name,
                        "question": fq.question,
                        "start_line": fq.function.start_line,
                        "end_line": fq.function.end_line,
                        "is_class_method": fq.function.is_class_method,
                        "class_name": fq.function.class_name
                    }
                    for fq in test_result_phase1.functions_with_questions
                ],
                "generated_tests": [
                    {
                        "filename": test.function.filename,
                        "function_name": test.function.function_name,
                        "test_name": test.test_name,
                        "test_code": test.test_code,
                        "confidence_score": test.confidence_score,
                        "question": test.question
                    }
                    for test in generated_tests
                ],
                "errors": test_result_phase1.errors,
                "duration": time.time() - stage_start_time,
                "message": f"Complete test pipeline: {test_result_phase1.functions_discovered} functions → {len(generated_tests)} tests → {execution_summary}",
                "execution_summary": execution_summary
            }
            
            # Send completion message with all phases
            await self.send_websocket_message(pipeline_id, {
                "type": "stage_complete",
                "stage": "test",
                "status": "success",
                "duration": round(time.time() - stage_start_time, 2),
                "message": f"✅ Complete test pipeline finished: {len(generated_tests)} tests generated and executed",
                "details": {
                    "functions_discovered": test_result_phase1.functions_discovered,
                    "questions_generated": test_result_phase1.questions_generated,
                    "tests_generated": len(generated_tests),
                    "tests_executed": tests_executed,
                    "tests_passed": tests_passed,
                    "execution_success": execution_result.success if execution_result else False,
                    "phase": "complete_with_execution"
                }
            })
            
            print(f"✅ Test stage completed successfully")
            
        except Exception as e:
            error_msg = f"Test Stage failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Store failed results
            context.results['test'] = {
                "success": False,
                "phase": "failed",
                "functions_discovered": 0,
                "questions_generated": 0,
                "tests_generated": 0,
                "errors": [error_msg],
                "duration": time.time() - stage_start_time
            }
            
            await self.send_websocket_message(pipeline_id, {
                "type": "stage_complete",
                "stage": "test",
                "status": "failed",
                "duration": round(time.time() - stage_start_time, 2),
                "message": error_msg
            })
            
            print(f"❌ Test stage failed: {str(e)}")
    
    async def _post_results_to_pr(self, context: PipelineContext):
        """Post comprehensive results to PR"""
        try:
            # Generate results summary
            duration = time.time() - context.start_time
            
            comment = self._generate_results_comment(context, duration)
            
            # Post to GitHub
            success = self.github_client.create_comment(
                context.repo_name, 
                context.pr_number, 
                comment
            )
            
            if success:
                print(f"✅ Results posted to PR #{context.pr_number}")
            else:
                print(f"❌ Failed to post results to PR")
                
        except Exception as e:
            print(f"❌ Error posting results: {str(e)}")
    
    def _generate_results_comment(self, context: PipelineContext, duration: float) -> str:
        """Generate markdown comment for PR"""
        status_emoji = "✅" if context.stage == PipelineStage.COMPLETE else "❌"
        
        comment = f"""
# {status_emoji} Hackademia AI Pipeline Results

**Pipeline ID**: `{context.repo_name}_{context.pr_number}`  
**Duration**: {duration:.2f} seconds  
**Status**: {context.stage.value}

## 🔨 Build Agent Results
"""
        
        if 'build' in context.results:
            build = context.results['build']
            meta = build.get('metadata', {}) or {}
            comment += f"""
- **Status**: {'✅ Success' if build.get('success') else '❌ Failed'}
- **Files Analyzed**: {meta.get('total_files', 0)}
- **Functions Found**: {meta.get('total_functions', 0)}
- **Classes Found**: {meta.get('total_classes', 0)}
- **Dependencies**: {meta.get('unique_dependencies', 0)}
"""
            
            if build.get('errors'):
                comment += f"\n**Build Errors:**\n"
                for error in build.get('errors', []):
                    comment += f"- ❌ {error}\n"
        
        comment += f"""
## 🔍 Analyze Agent Results
"""
        
        if 'analyze' in context.results:
            analyze = context.results['analyze']
            if analyze['success']:
                comment += f"""- **Status**: ✅ AI Analysis Complete
- **Files Analyzed**: {analyze.get('files_analyzed', 0)}
- **Total Issues Found**: {analyze.get('total_issues', 0)}
- **Overall Risk Level**: {analyze.get('overall_risk', 'UNKNOWN')}
- **Vulnerabilities**: {len(analyze.get('vulnerabilities', []))}
- **Security Issues**: {len(analyze.get('security_issues', []))}
- **Quality Issues**: {len(analyze.get('quality_issues', []))}

**🚨 Critical Issues Found:**
"""
                # Show critical vulnerabilities
                for vuln in analyze.get('vulnerabilities', [])[:3]:  # Top 3
                    if vuln.get('severity') == 'HIGH':
                        comment += f"- ⚠️ **{vuln.get('type', 'Unknown')}** (Line {vuln.get('line_number', '?')}): {vuln.get('description', 'No description')}\n"
                
                # Show recommendations
                if analyze.get('recommendations'):
                    comment += f"\n**💡 AI Recommendations:**\n"
                    for rec in analyze.get('recommendations', [])[:3]:  # Top 3
                        comment += f"- {rec}\n"
            else:
                comment += f"- **Status**: ❌ Analysis Failed\n- **Error**: {analyze.get('error', 'Unknown error')}\n"
        else:
            comment += "- **Status**: ⏭️ Skipped\n"

        comment += f"""
## 🔧 Fix Agent Results  
{context.results.get('fix', {}).get('message', 'Not executed')}

## 🧪 Test Agent Results
{context.results.get('test', {}).get('message', 'Not executed')}

---
*Powered by Hackademia Multi-Agent AI Pipeline* 🚀
"""
        
        return comment
    
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get current status of a pipeline"""
        if pipeline_id not in self.active_pipelines:
            return {"error": "Pipeline not found"}
        
        context = self.active_pipelines[pipeline_id]
        return {
            "pipeline_id": pipeline_id,
            "stage": context.stage.value,
            "pr_number": context.pr_number,
            "repo_name": context.repo_name,
            "duration": time.time() - context.start_time,
            "results": context.results,
            "errors": context.errors
        }

# Global pipeline orchestrator
pipeline_orchestrator = MultiAgentPipeline()

def get_pipeline_orchestrator() -> MultiAgentPipeline:
    """Get the global pipeline orchestrator"""
    return pipeline_orchestrator
