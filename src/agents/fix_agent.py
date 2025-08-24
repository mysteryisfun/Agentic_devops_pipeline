"""
Fix Agent - AI-Powered Code Fixing
Automatically applies fixes to code issues found by Analyze Agent
"""

import os
import sys
import json
import base64
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import MCP client for context gathering
try:
    from MCP.hackademia_mcp_client import create_mcp_client, HackademiaMCPWrapper
    from .autonomous_mcp_agent import AutonomousMCPAgent
    MCP_AVAILABLE = True
    print("✅ MCP client imported successfully for Fix Agent")
except ImportError as e:
    print(f"⚠️ MCP client not available for Fix Agent: {str(e)}")
    MCP_AVAILABLE = False

from src.utils.github_client import get_github_client

@dataclass
class FixResult:
    """Result of a single fix operation"""
    success: bool
    filename: str
    function_name: str
    fix_summary: str
    issue_type: str
    confidence: int
    lines_affected: str
    old_code: str
    new_code: str
    commit_sha: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class FixStageResult:
    """Result of entire fix stage"""
    success: bool
    fixes_applied: int
    files_modified: int
    commits_made: int
    fixes_summary: List[Dict[str, Any]]
    errors: List[str]
    duration: float

class FixAgent:
    """
    AI-powered code fixing agent using Gemini
    Applies automated fixes to issues found by Analyze Agent
    """
    
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Initialize GitHub client
        self.github_client = get_github_client()
        
        print("✅ Fix Agent initialized with Gemini 2.5 Flash")
        
        # Initialize MCP client for context gathering
        self.mcp_client = None
        self.autonomous_mcp = None
        if MCP_AVAILABLE:
            try:
                self.mcp_client = create_mcp_client()
                self.autonomous_mcp = AutonomousMCPAgent(self.mcp_client, self.model)
                print("✅ MCP client initialized for Fix Agent context gathering")
            except Exception as e:
                print(f"⚠️ MCP client initialization failed for Fix Agent: {str(e)}")
                self.mcp_client = None
                self.autonomous_mcp = None
        else:
            print("⚠️ MCP not available - fixes will work without codebase context")
    
    async def apply_fixes(self, analysis_result, repo_name: str, branch: str, 
                         progress_callback=None) -> FixStageResult:
        """
        Main fix application method - applies fixes for high-confidence issues
        
        Args:
            analysis_result: Result from Analyze Agent
            repo_name: GitHub repository name
            branch: PR branch name
            progress_callback: Function to send progress updates
            
        Returns:
            FixStageResult with applied fixes and results
        """
        
        start_time = time.time()
        
        print(f"🔧 FIX AGENT: Starting apply_fixes for {repo_name}#{branch}")
        print(f"🔧 FIX AGENT: Analysis found {analysis_result.total_issues} total issues")
        
        if progress_callback:
            await progress_callback({
                "type": "stage_start",
                "stage": "fix",
                "stage_index": 3,
                "message": "🔧 Starting AI-powered code fixing...",
                "details": {
                    "total_issues": analysis_result.total_issues,
                    "repo_name": repo_name,
                    "branch": branch
                }
            })
            print(f"🔧 FIX AGENT: Sent stage_start WebSocket message")
        
        try:
            # Filter high-confidence issues only
            fixable_issues = self._filter_high_confidence_issues(analysis_result)
            
            if not fixable_issues:
                if progress_callback:
                    await progress_callback({
                        "type": "stage_complete",
                        "stage": "fix", 
                        "status": "skipped",
                        "duration": round(time.time() - start_time, 2),
                        "message": "No high-confidence issues found to fix"
                    })
                
                return FixStageResult(
                    success=True,
                    fixes_applied=0,
                    files_modified=0,
                    commits_made=0,
                    fixes_summary=[],
                    errors=[],
                    duration=time.time() - start_time
                )
            
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "fix",
                    "status": "in_progress",
                    "message": f"🔍 Found {len(fixable_issues)} high-confidence issues to fix",
                    "progress": 10,
                    "details": {
                        "fixable_issues": len(fixable_issues),
                        "issue_types": list(set([issue.get('type', 'unknown') for issue in fixable_issues]))
                    }
                })
            
            # Apply fixes
            fixes_applied = []
            files_modified = set()
            commits_made = 0
            errors = []
            
            for i, issue in enumerate(fixable_issues):
                try:
                    if progress_callback:
                        await progress_callback({
                            "type": "status_update",
                            "stage": "fix",
                            "status": "in_progress", 
                            "message": f"🔧 Generating fix {i+1}/{len(fixable_issues)} for {issue.get('filename', 'unknown')}",
                            "progress": 15 + (i * 60 // len(fixable_issues))
                        })
                    
                    fix_result = await self._apply_single_fix(issue, repo_name, branch, progress_callback)
                    
                    if fix_result.success:
                        fixes_applied.append(fix_result)
                        files_modified.add(fix_result.filename)
                        if fix_result.commit_sha:
                            commits_made += 1
                            
                        if progress_callback:
                            await progress_callback({
                                "type": "status_update",
                                "stage": "fix",
                                "status": "in_progress",
                                "message": f"✅ Applied fix to {fix_result.function_name}() in {fix_result.filename}",
                                "progress": 15 + ((i + 1) * 60 // len(fixable_issues)),
                                "details": {
                                    "filename": fix_result.filename,
                                    "function_name": fix_result.function_name,
                                    "fix_summary": fix_result.fix_summary,
                                    "issue_type": fix_result.issue_type,
                                    "confidence": fix_result.confidence,
                                    "old_code": fix_result.old_code[:100] + "..." if len(fix_result.old_code) > 100 else fix_result.old_code,
                                    "new_code": fix_result.new_code[:100] + "..." if len(fix_result.new_code) > 100 else fix_result.new_code,
                                    "lines_changed": fix_result.lines_affected,
                                    "commit_sha": fix_result.commit_sha,
                                    "repo_name": repo_name,
                                    "branch": branch
                                }
                            })
                            print(f"🔧 FIX AGENT: Sent progress update - fixed {fix_result.filename}")
                    else:
                        errors.append(f"Failed to fix {issue.get('filename', 'unknown')}: {fix_result.error_message}")
                        print(f"🔧 FIX AGENT: Fix failed for {issue.get('filename', 'unknown')}: {fix_result.error_message}")
                        
                except Exception as e:
                    error_msg = f"Error fixing issue in {issue.get('filename', 'unknown')}: {str(e)}"
                    errors.append(error_msg)
                    print(f"❌ {error_msg}")
            
            # Create summary
            fixes_summary = []
            for fix in fixes_applied:
                fixes_summary.append({
                    "filename": fix.filename,
                    "function": fix.function_name,
                    "fix_type": fix.issue_type,
                    "summary": fix.fix_summary,
                    "confidence": fix.confidence,
                    "commit_sha": fix.commit_sha
                })
            
            duration = time.time() - start_time
            
            # Send completion message
            if progress_callback:
                await progress_callback({
                    "type": "stage_complete",
                    "stage": "fix",
                    "status": "success" if fixes_applied else "warning",
                    "duration": round(duration, 2),
                    "results": {
                        "fixes_applied": len(fixes_applied),
                        "files_modified": len(files_modified),
                        "commits_made": commits_made,
                        "fixes_summary": fixes_summary,
                        "errors": errors,
                        "repo_name": repo_name,
                        "branch": branch
                    }
                })
                print(f"🔧 FIX AGENT: Sent stage_complete WebSocket message - {len(fixes_applied)} fixes applied")
            
            print(f"🔧 FIX AGENT: Completed successfully - {len(fixes_applied)} fixes, {len(files_modified)} files, {commits_made} commits")
            
            return FixStageResult(
                success=True,
                fixes_applied=len(fixes_applied),
                files_modified=len(files_modified),
                commits_made=commits_made,
                fixes_summary=fixes_summary,
                errors=errors,
                duration=duration
            )
            
        except Exception as e:
            error_msg = f"Fix stage failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            if progress_callback:
                await progress_callback({
                    "type": "error",
                    "stage": "fix",
                    "message": error_msg,
                    "error_code": "FIX_STAGE_FAILED"
                })
            
            return FixStageResult(
                success=False,
                fixes_applied=0,
                files_modified=0,
                commits_made=0,
                fixes_summary=[],
                errors=[error_msg],
                duration=time.time() - start_time
            )
    
    def _filter_high_confidence_issues(self, analysis_result) -> List[Dict[str, Any]]:
        """Send ALL issues to Gemini for fixing - no confidence filtering"""
        all_issues = []
        
        print(f"🔍 Preparing ALL issues for Gemini fixing:")
        print(f"   Vulnerabilities: {len(analysis_result.vulnerabilities)}")
        print(f"   Security issues: {len(analysis_result.security_issues)}")
        print(f"   Quality issues: {len(analysis_result.quality_issues)}")
        
        # Process ALL vulnerabilities
        for i, vuln in enumerate(analysis_result.vulnerabilities):
            vuln['type'] = 'vulnerability'
            if 'filename' not in vuln and 'file' in vuln:
                vuln['filename'] = vuln['file']
            filename = vuln.get('filename', vuln.get('file', 'unknown'))
            all_issues.append(vuln)
            print(f"   ✅ Vulnerability {i+1}: file='{filename}' -> SENDING TO GEMINI")
        
        # Process ALL security issues
        for i, issue in enumerate(analysis_result.security_issues):
            issue['type'] = 'security_issue'
            if 'filename' not in issue and 'file' in issue:
                issue['filename'] = issue['file']
            filename = issue.get('filename', issue.get('file', 'unknown'))
            all_issues.append(issue)
            print(f"   ✅ Security issue {i+1}: file='{filename}' -> SENDING TO GEMINI")
        
        # Process ALL quality issues
        for i, issue in enumerate(analysis_result.quality_issues):
            issue['type'] = 'quality_issue'
            if 'filename' not in issue and 'file' in issue:
                issue['filename'] = issue['file']
            filename = issue.get('filename', issue.get('file', 'unknown'))
            all_issues.append(issue)
            print(f"   ✅ Quality issue {i+1}: file='{filename}' -> SENDING TO GEMINI")
        
        print(f"🎯 Total issues going to Gemini: {len(all_issues)}")
        return all_issues
    
    async def _apply_single_fix(self, issue: Dict[str, Any], repo_name: str, branch: str,
                               progress_callback=None) -> FixResult:
        """Apply a single fix to a specific issue"""
        
        try:
            filename = issue.get('filename', '')
            issue_type = issue.get('type', 'unknown')
            description = issue.get('description', '')
            confidence = issue.get('confidence', 0)
            
            print(f"🔧 Attempting to fix issue:")
            print(f"   Filename: '{filename}'")
            print(f"   Issue type: '{issue_type}'")
            print(f"   Description: '{description}'")
            
            # Skip if filename is missing or 'unknown'
            if not filename or filename == 'unknown':
                print(f"❌ Cannot fix issue - filename is missing or unknown")
                return FixResult(
                    success=False, filename=filename, function_name="unknown",
                    fix_summary="", issue_type=issue_type, confidence=confidence,
                    lines_affected="", old_code="", new_code="",
                    error_message="Filename is missing or unknown - cannot apply fix"
                )
            
            print(f"📥 Getting file content from GitHub: {repo_name}/{filename}")
            
            # Get current file content from GitHub
            file_content = self.github_client.get_file_content(repo_name, filename, branch)
            
            if not file_content:
                print(f"❌ Could not retrieve file content for {filename}")
                return FixResult(
                    success=False, filename=filename, function_name="unknown",
                    fix_summary="", issue_type=issue_type, confidence=confidence,
                    lines_affected="", old_code="", new_code="",
                    error_message=f"Could not retrieve file content for {filename}"
                )
            
            current_content = base64.b64decode(file_content.content).decode('utf-8')
            print(f"✅ Retrieved {len(current_content)} characters of file content")
            
            # Gather MCP context if available
            mcp_context = ""
            if self.autonomous_mcp:
                try:
                    print(f"🤖 Gathering MCP context...")
                    context_result = await self.autonomous_mcp.autonomous_analysis(
                        filename, issue.get('code_snippet', ''), {}, progress_callback
                    )
                    mcp_context = context_result.get('context_gathered', '')
                    print(f"✅ MCP context gathered: {len(mcp_context)} characters")
                except Exception as e:
                    print(f"⚠️ MCP context gathering failed: {str(e)}")
            
            print(f"🧠 Calling Gemini to generate fix...")
            
            # Send progress update that we're calling Gemini
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "fix",
                    "status": "in_progress",
                    "message": f"🧠 Gemini AI generating fix for {filename}...",
                    "progress": None,  # Sub-progress
                    "details": {
                        "current_file": filename,
                        "step": "ai_fix_generation",
                        "issue_type": issue_type,
                        "description": description[:100] + "..." if len(description) > 100 else description
                    }
                })
            
            # Generate fix using Gemini
            fix_data = await self._generate_fix_with_gemini(
                filename, current_content, issue, mcp_context
            )
            
            if not fix_data:
                print(f"❌ Gemini failed to generate fix data")
                return FixResult(
                    success=False, filename=filename, function_name="unknown",
                    fix_summary="", issue_type=issue_type, confidence=confidence,
                    lines_affected="", old_code="", new_code="",
                    error_message="Failed to generate fix"
                )
            
            print(f"✅ Gemini generated fix: {fix_data.get('fix_summary', 'No summary')}")
            print(f"   Function: {fix_data.get('function_name', 'unknown')}")
            print(f"   Lines affected: {fix_data.get('lines_affected', 'unknown')}")
            
            # Apply fix to content
            print(f"🔄 Applying fix to file content...")
            fixed_content = self._apply_fix_to_content(current_content, fix_data)
            
            if fixed_content == current_content:
                print(f"⚠️ No changes were made to the file content")
                return FixResult(
                    success=False, filename=filename, function_name=fix_data.get('function_name', 'unknown'),
                    fix_summary=fix_data.get('fix_summary', ''), issue_type=issue_type, confidence=confidence,
                    lines_affected=fix_data.get('lines_affected', ''), 
                    old_code=fix_data.get('old_code', ''), new_code=fix_data.get('new_code', ''),
                    error_message="Fix could not be applied - no changes made to file"
                )
            
            print(f"✅ Fix applied successfully, committing to GitHub...")
            
            # Commit via GitHub API with bot-identifiable message
            commit_message = f"🤖 AI Fix: {fix_data['fix_summary']} [skip-pipeline]"
            commit_result = self.github_client.update_file(
                repo_name=repo_name,
                filename=filename,
                content=fixed_content,
                message=commit_message,
                branch=branch,
                sha=file_content.sha
            )
            
            print(f"✅ Committed fix to GitHub: {commit_result.get('commit', {}).get('sha', 'unknown')}")
            
            return FixResult(
                success=True,
                filename=filename,
                function_name=fix_data.get('function_name', 'unknown'),
                fix_summary=fix_data.get('fix_summary', ''),
                issue_type=issue_type,
                confidence=confidence,
                lines_affected=fix_data.get('lines_affected', ''),
                old_code=fix_data.get('old_code', ''),
                new_code=fix_data.get('new_code', ''),
                commit_sha=commit_result.get('commit', {}).get('sha')
            )
            
        except Exception as e:
            return FixResult(
                success=False,
                filename=issue.get('filename', ''),
                function_name="unknown",
                fix_summary="",
                issue_type=issue.get('type', 'unknown'),
                confidence=issue.get('confidence', 0),
                lines_affected="",
                old_code="",
                new_code="",
                error_message=str(e)
            )
    
    async def _generate_fix_with_gemini(self, filename: str, content: str, 
                                       issue: Dict[str, Any], mcp_context: str) -> Dict[str, Any]:
        """Generate fix using Gemini with MCP context"""
        
        prompt = f"""You are an expert code security fixer. Fix the following issue with MINIMAL changes.

**Issue Details**:
- File: {filename}
- Issue Type: {issue.get('type', 'unknown')}
- Description: {issue.get('description', '')}
- Confidence: {issue.get('confidence', 0)}%
- Line: {issue.get('line', 'unknown')}

**Current File Content**:
```
{content}
```

**Codebase Context** (from MCP):
{mcp_context}

**STRICT REQUIREMENTS**:
1. Apply ONLY the minimal fix needed
2. Preserve exact code style, indentation, variable names
3. Keep all existing functionality intact
4. Match patterns used elsewhere in codebase
5. Fix only the specific security/quality issue mentioned
6. Identify the exact function/method being fixed

**OUTPUT FORMAT** (JSON only, no explanations):
{{
  "function_name": "authenticate_user",
  "fix_summary": "Replace SQL string concatenation with parameterized query",
  "issue_type": "{issue.get('type', 'unknown')}",
  "confidence": {issue.get('confidence', 0)},
  "lines_affected": "45-47",
  "old_code": "cursor.execute(f\\"SELECT * FROM users WHERE username='{{username}}\\"\\)",
  "new_code": "cursor.execute(\\"SELECT * FROM users WHERE username=%s\\", (username,))",
  "explanation": "Prevents SQL injection by using parameterized queries"
}}"""

        try:
            print(f"🧠 Sending prompt to Gemini (length: {len(prompt)} chars)")
            response = self.model.generate_content(prompt)
            print(f"✅ Gemini responded with: {len(response.text)} characters")
            print(f"📄 Gemini response preview: {response.text[:200]}...")
            
            parsed_fix = self._parse_gemini_fix_response(response.text)
            if parsed_fix:
                print(f"✅ Successfully parsed Gemini fix response")
            else:
                print(f"❌ Failed to parse Gemini fix response")
            
            return parsed_fix
        except Exception as e:
            print(f"❌ Gemini fix generation failed: {str(e)}")
            return None
    
    def _parse_gemini_fix_response(self, response: str) -> Dict[str, Any]:
        """Extract and validate JSON from Gemini response"""
        try:
            # Find JSON in response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end <= json_start:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            fix_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['function_name', 'fix_summary', 'old_code', 'new_code', 'lines_affected']
            for field in required_fields:
                if field not in fix_data:
                    raise ValueError(f"Missing required field: {field}")
            
            return fix_data
            
        except Exception as e:
            print(f"❌ Failed to parse Gemini response: {str(e)}")
            return None
    
    def _apply_fix_to_content(self, content: str, fix_data: Dict[str, Any]) -> str:
        """Apply fix to file content"""
        try:
            # Simple replacement approach
            old_code = fix_data['old_code']
            new_code = fix_data['new_code']
            
            if old_code in content:
                return content.replace(old_code, new_code)
            else:
                # Fallback: try to find similar code patterns
                lines = content.split('\n')
                old_lines = old_code.split('\n')
                
                # Find the best match
                for i in range(len(lines) - len(old_lines) + 1):
                    match_score = 0
                    for j, old_line in enumerate(old_lines):
                        if old_line.strip() in lines[i + j].strip():
                            match_score += 1
                    
                    if match_score >= len(old_lines) * 0.8:  # 80% match threshold
                        # Replace these lines
                        new_lines = new_code.split('\n')
                        lines[i:i + len(old_lines)] = new_lines
                        return '\n'.join(lines)
                
                # If no good match found, return original content
                print(f"⚠️ Could not find exact match for fix, skipping")
                return content
                
        except Exception as e:
            print(f"❌ Error applying fix: {str(e)}")
            return content

# Global instance
_fix_agent_instance = None

def get_fix_agent():
    """Get global Fix Agent instance"""
    global _fix_agent_instance
    if _fix_agent_instance is None:
        _fix_agent_instance = FixAgent()
    return _fix_agent_instance
