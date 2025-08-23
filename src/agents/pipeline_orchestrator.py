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
        self.github_client = get_github_client()
        self.active_pipelines: Dict[str, PipelineContext] = {}
    
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
            
            # Stage 1: Build Agent
            await self._run_build_stage(context)
            
            # Stage 2: Analyze Agent (placeholder for now)
            await self._run_analyze_stage(context)
            
            # Stage 3: Fix Agent (placeholder for now)
            await self._run_fix_stage(context)
            
            # Stage 4: Test Agent (placeholder for now)
            await self._run_test_stage(context)
            
            # Complete pipeline
            context.stage = PipelineStage.COMPLETE
            await self._post_results_to_pr(context)
            
            print(f"✅ Pipeline {pipeline_id} completed successfully")
            
        except Exception as e:
            context.stage = PipelineStage.FAILED
            context.errors.append(str(e))
            print(f"❌ Pipeline {pipeline_id} failed: {str(e)}")
            await self._post_results_to_pr(context)
    
    async def _run_build_stage(self, context: PipelineContext):
        """Run Build Agent stage"""
        print(f"🔨 Running Build stage for {context.repo_name}#{context.pr_number}")
        context.stage = PipelineStage.BUILD
        
        # Get file contents for changed files
        files_content = {}
        for file_info in context.files_changed:
            if file_info['status'] != 'removed':
                content = self.github_client.get_file_content(
                    context.repo_name, 
                    file_info['filename'], 
                    context.branch
                )
                if content:
                    files_content[file_info['filename']] = content
        
        # Run build analysis
        build_result = self.build_agent.compile_and_validate(files_content)
        
        # Store results
        context.results['build'] = {
            "success": build_result.success,
            "metadata": build_result.metadata,
            "errors": build_result.errors,
            "warnings": build_result.warnings,
            "dependencies": build_result.dependencies,
            "file_info": build_result.file_info,
            "agent_context": self.build_agent.prepare_context_for_agents(build_result)
        }
        
        print(f"✅ Build stage completed - Success: {build_result.success}")
    
    async def _run_analyze_stage(self, context: PipelineContext):
        """Run Analyze Agent stage (placeholder)"""
        print(f"🔍 Running Analyze stage for {context.repo_name}#{context.pr_number}")
        context.stage = PipelineStage.ANALYZE
        
        # TODO: Implement Analyze Agent with Gemini
        context.results['analyze'] = {
            "success": True,
            "issues_found": [],
            "security_issues": [],
            "quality_issues": [],
            "message": "Analyze Agent placeholder - will be implemented with Gemini"
        }
        
        print("✅ Analyze stage completed (placeholder)")
    
    async def _run_fix_stage(self, context: PipelineContext):
        """Run Fix Agent stage (placeholder)"""
        print(f"🔧 Running Fix stage for {context.repo_name}#{context.pr_number}")
        context.stage = PipelineStage.FIX
        
        # TODO: Implement Fix Agent with Gemini
        context.results['fix'] = {
            "success": True,
            "fixes_applied": [],
            "commits_made": [],
            "message": "Fix Agent placeholder - will apply automated fixes"
        }
        
        print("✅ Fix stage completed (placeholder)")
    
    async def _run_test_stage(self, context: PipelineContext):
        """Run Test Agent stage (placeholder)"""
        print(f"🧪 Running Test stage for {context.repo_name}#{context.pr_number}")
        context.stage = PipelineStage.TEST
        
        # TODO: Implement Test Agent with Qwen model
        context.results['test'] = {
            "success": True,
            "tests_generated": [],
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage": 0,
            "message": "Test Agent placeholder - will generate and run tests"
        }
        
        print("✅ Test stage completed (placeholder)")
    
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
            comment += f"""
- **Status**: {'✅ Success' if build['success'] else '❌ Failed'}
- **Files Analyzed**: {build['metadata']['total_files']}
- **Functions Found**: {build['metadata']['total_functions']}
- **Classes Found**: {build['metadata']['total_classes']}
- **Dependencies**: {build['metadata']['unique_dependencies']}
"""
            
            if build['errors']:
                comment += f"\n**Build Errors:**\n"
                for error in build['errors']:
                    comment += f"- ❌ {error}\n"
        
        comment += f"""
## 🔍 Analyze Agent Results
{context.results.get('analyze', {}).get('message', 'Not executed')}

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
