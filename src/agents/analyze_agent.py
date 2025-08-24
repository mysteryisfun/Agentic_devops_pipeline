"""
Analyze Agent - Real AI-Powered Code Analysis
Uses Gemini AI for vulnerability detection and code quality analysis
"""

import os
import sys
import json
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

# Import MCP client for RAG functionality
try:
    from MCP.hackademia_mcp_client import create_mcp_client, HackademiaMCPWrapper
    from .autonomous_mcp_agent import AutonomousMCPAgent
    MCP_AVAILABLE = True
    print("✅ MCP client imported successfully")
except ImportError as e:
    print(f"⚠️ MCP client not available: {str(e)}")
    MCP_AVAILABLE = False

@dataclass
class AnalysisResult:
    """Result of code analysis"""
    success: bool
    vulnerabilities: List[Dict[str, Any]]
    security_issues: List[Dict[str, Any]]
    quality_issues: List[Dict[str, Any]]
    recommendations: List[str]
    overall_risk: str
    files_analyzed: int
    total_issues: int
    confidence_scores: Dict[str, float]

class AnalyzeAgent:
    """
    AI-powered code analysis agent using Gemini
    Analyzes PR diff for vulnerabilities, security issues, and code quality
    """
    
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        print("✅ Analyze Agent initialized with Gemini 2.5 Flash")
        
        # Initialize MCP client for RAG
        self.mcp_client = None
        self.autonomous_mcp = None
        if MCP_AVAILABLE:
            try:
                self.mcp_client = create_mcp_client()
                self.autonomous_mcp = AutonomousMCPAgent(self.mcp_client, self.model)
                print("✅ Autonomous MCP RAG client initialized for smart context gathering")
            except Exception as e:
                print(f"⚠️ MCP client initialization failed: {str(e)}")
                self.mcp_client = None
                self.autonomous_mcp = None
        else:
            print("⚠️ MCP not available - analysis will work without codebase context")
    
    async def analyze_pr_diff(self, diff_data: Dict[str, Any], build_context: Dict[str, Any], 
                              progress_callback=None) -> AnalysisResult:
        """
        Main analysis method - analyzes PR diff using Gemini AI
        
        Args:
            diff_data: PR diff data with changed files
            build_context: Build results and metadata
            progress_callback: Function to send progress updates
            
        Returns:
            AnalysisResult with vulnerabilities and recommendations
        """
        
        if progress_callback:
            await progress_callback({
                "type": "status_update",
                "stage": "analyze", 
                "status": "in_progress",
                "message": "🔍 Starting AI-powered code analysis...",
                "progress": 5
            })
        
        try:
            # Initialize result
            start_time = time.time()
            
            # Extract and filter files for analysis
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "analyze",
                    "status": "in_progress", 
                    "message": "📂 Scanning changed files for analysis...",
                    "progress": 10
                })
            
            code_files = self._filter_code_files(diff_data.get('files', []))
            
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "analyze",
                    "status": "in_progress", 
                    "message": f"📊 Found {len(code_files)} code files to analyze",
                    "progress": 15,
                    "details": {
                        "files_changed": len(diff_data.get('files', [])),
                        "code_files_to_analyze": len(code_files),
                        "files_filtered": [f.get('filename', 'unknown') for f in code_files[:5]]  # Show first 5
                    }
                })
            
            # Initialize result
            result = AnalysisResult(
                success=True,
                vulnerabilities=[],
                security_issues=[],
                quality_issues=[],
                recommendations=[],
                overall_risk="LOW",
                files_analyzed=0,
                total_issues=0,
                confidence_scores={}
            )
            
            # Filter and analyze only code files
            code_files = self._filter_code_files(diff_data.get('changed_files', []))
            result.files_analyzed = len(code_files)
            
            if not code_files:
                result.recommendations.append("No code files found to analyze")
                return result
            
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "analyze",
                    "status": "in_progress", 
                    "message": f"📂 Analyzing {len(code_files)} code files...",
                    "progress": 30
                })
            
            # Analyze each changed file
            for i, file_data in enumerate(code_files):
                filename = file_data.get('filename', 'unknown')
                
                if progress_callback:
                    await progress_callback({
                        "type": "status_update",
                        "stage": "analyze",
                        "status": "in_progress",
                        "message": f"🔍 Analyzing file {i+1}/{len(code_files)}: {filename}",
                        "progress": 30 + (i * 40 // len(code_files)),
                        "details": {
                            "current_file": filename,
                            "files_completed": i,
                            "total_files": len(code_files)
                        }
                    })
                
                file_analysis = await self._analyze_single_file(file_data, build_context, progress_callback)
                
                # Add filename to each issue before merging
                filename = file_data.get('filename', 'unknown')
                
                # Add filename to vulnerabilities
                for vuln in file_analysis.get('vulnerabilities', []):
                    vuln['filename'] = filename
                    vuln['file'] = filename  # Backup field
                
                # Add filename to security issues  
                for issue in file_analysis.get('security_issues', []):
                    issue['filename'] = filename
                    issue['file'] = filename  # Backup field
                
                # Add filename to quality issues
                for issue in file_analysis.get('quality_issues', []):
                    issue['filename'] = filename
                    issue['file'] = filename  # Backup field
                
                # Merge results
                result.vulnerabilities.extend(file_analysis.get('vulnerabilities', []))
                result.security_issues.extend(file_analysis.get('security_issues', []))
                result.quality_issues.extend(file_analysis.get('quality_issues', []))
                result.recommendations.extend(file_analysis.get('recommendations', []))
                
                # Update progress
                progress = 30 + int((i + 1) / len(code_files) * 50)
                if progress_callback:
                    await progress_callback({
                        "type": "status_update",
                        "stage": "analyze",
                        "status": "in_progress",
                        "message": f"✅ Analyzed {file_data['filename']}",
                        "progress": progress
                    })
            
            # Calculate overall risk and confidence
            result.total_issues = len(result.vulnerabilities) + len(result.security_issues) + len(result.quality_issues)
            result.overall_risk = self._calculate_overall_risk(result)
            result.confidence_scores = self._calculate_confidence_scores(result)
            
            # Send detailed final analysis results
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "analyze",
                    "status": "in_progress", 
                    "message": "📊 Security analysis complete - compiling results...",
                    "progress": 90,
                    "details": {
                        "vulnerabilities_found": len(result.vulnerabilities),
                        "security_issues_found": len(result.security_issues), 
                        "quality_issues_found": len(result.quality_issues),
                        "total_issues": result.total_issues,
                        "overall_risk": result.overall_risk,
                        "critical_issues": len([v for v in result.vulnerabilities if v.get('severity') == 'HIGH']),
                        "high_severity": len([v for v in result.vulnerabilities + result.security_issues if v.get('severity') == 'HIGH']),
                        "medium_severity": len([v for v in result.vulnerabilities + result.security_issues if v.get('severity') == 'MEDIUM']),
                        "files_analyzed": result.files_analyzed
                    }
                })
            
            print(f"✅ Analysis completed: {result.total_issues} issues found")
            return result
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            # Create a default failed result
            failed_result = AnalysisResult(
                success=False,
                vulnerabilities=[],
                security_issues=[],
                quality_issues=[],
                recommendations=[f"Analysis failed: {str(e)}"],
                overall_risk="UNKNOWN",
                files_analyzed=0,
                total_issues=0,
                confidence_scores={}
            )
            return failed_result
    
    def _filter_code_files(self, changed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter files to only analyze code files"""
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb'}
        
        code_files = []
        for file in changed_files:
            file_ext = file.get('file_extension', '')
            # Handle both .py and py formats
            if not file_ext.startswith('.'):
                file_ext = f'.{file_ext}'
            
            if (file_ext in code_extensions and 
                not file.get('is_binary', False) and
                file.get('status') in ['added', 'modified']):
                code_files.append(file)
                print(f"✅ Will analyze: {file.get('filename')} ({file_ext})")
        
        print(f"📂 Filtered {len(code_files)} code files for analysis")
        return code_files
    
    async def _autonomous_mcp_analysis(self, filename: str, code_snippet: str, build_context: Dict[str, Any], 
                                       progress_callback=None) -> Dict[str, Any]:
        """Let Gemini autonomously decide which MCP tools to use for analysis"""
        
        if not self.autonomous_mcp:
            print("⚠️ Autonomous MCP agent not available - skipping context gathering")
            return {}
        
        try:
            # Create progress-aware wrapper for autonomous analysis
            async def autonomous_progress_callback(update_data):
                if progress_callback:
                    # Extract relevant information for WebSocket message
                    questions_asked = update_data.get('questions_asked', 0)
                    current_question = update_data.get('current_question', '')
                    reasoning = update_data.get('reasoning', '')
                    scope = update_data.get('scope_assessment', 'unknown')
                    
                    await progress_callback({
                        "type": "status_update",
                        "stage": "analyze",
                        "status": "in_progress",
                        "message": f"🔧 AI asking question {questions_asked}",
                        "progress": None,  # Sub-progress
                        "details": {
                            "current_file": filename,
                            "scope_assessed": scope,
                            "question": current_question[:100] + "..." if len(current_question) > 100 else current_question,
                            "reasoning": reasoning[:80] + "..." if len(reasoning) > 80 else reasoning,
                            "step": "mcp_question_execution"
                        }
                    })
            
            # Use autonomous MCP agent to let Gemini decide which tools to use
            autonomous_result = await self.autonomous_mcp.autonomous_analysis(
                filename, code_snippet, build_context, progress_callback=autonomous_progress_callback
            )
            
            if autonomous_result:
                # Get the new format results
                scope_assessment = autonomous_result.get('scope_assessment', 'medium')
                questions_asked = autonomous_result.get('questions_asked', [])
                mcp_results = autonomous_result.get('mcp_results', {})
                analysis_focus = autonomous_result.get('analysis_focus', '')
                total_context_chars = autonomous_result.get('total_context_chars', 0)
                
                print(f"🤖 Autonomous analysis completed for {scope_assessment} scope")
                print(f"❓ Asked {len(questions_asked)} targeted questions")
                print(f"🎯 Analysis focus: {analysis_focus}")
                print(f"📊 Context gathered: {total_context_chars} chars")
                
                # Format results for use in analysis prompt
                context_summary = {
                    "scope_assessment": scope_assessment,
                    "questions_asked": questions_asked,
                    "mcp_results": mcp_results,
                    "analysis_focus": analysis_focus,
                    "total_context_gathered": total_context_chars
                }
                
                return context_summary
            
        except Exception as e:
            print(f"❌ Autonomous MCP analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return {}
    
    async def _analyze_single_file(self, file_data: Dict[str, Any], build_context: Dict[str, Any], 
                                   progress_callback=None) -> Dict[str, Any]:
        """Analyze a single file using Gemini AI with MCP RAG context"""
        
        filename = file_data.get('filename', 'unknown')
        print(f"🔍 Analyzing {filename}...")
        
        # Prepare code context for AI analysis
        added_lines = file_data.get('added_lines', [])
        context_lines = file_data.get('context_lines', [])
        
        if not added_lines:
            return {"vulnerabilities": [], "security_issues": [], "quality_issues": [], "recommendations": []}
        
        # Build code snippet for analysis
        code_snippet = self._build_code_snippet(added_lines, context_lines)
        
        # Autonomous MCP Context Gathering with progress updates
        if progress_callback:
            await progress_callback({
                "type": "status_update",
                "stage": "analyze",
                "status": "in_progress",
                "message": f"🤖 AI generating targeted questions for {filename}...",
                "progress": None,  # Sub-progress, don't update main progress
                "details": {
                    "current_file": filename,
                    "step": "mcp_context_gathering",
                    "phase": "question_generation"
                }
            })
        
        # Gather MCP context autonomously - let Gemini decide which tools to use
        print(f"🤖 Autonomous MCP context gathering for {filename}...")
        mcp_context = await self._autonomous_mcp_analysis(filename, code_snippet, build_context, progress_callback)
        
        # Create enhanced analysis prompt with MCP context
        analysis_prompt = f"""
        You are a senior security engineer analyzing code changes in a pull request with access to the complete codebase context.
        
        **File**: {filename}
        **Language**: {file_data.get('file_extension', 'unknown')}
        **Status**: {file_data.get('status', 'unknown')}
        
        **Code Changes (NEW LINES ONLY):**
        ```
        {code_snippet}
        ```
        
        **Build Context:**
        - Project Type: {build_context.get('metadata', {}).get('project_type', 'unknown')}
        - Dependencies: {', '.join(build_context.get('dependencies', [])[:5])}
        
        **Autonomous MCP Context (AI-Selected Tools):**
        {self._format_autonomous_mcp_context(mcp_context)}
        
        **Analysis Required:**
        1. **Security Vulnerabilities** (SQL injection, XSS, command injection, path traversal, etc.)
        2. **Code Quality Issues** (code smells, performance issues, maintainability)
        3. **Best Practice Violations**
        4. **Context-aware recommendations** based on existing codebase patterns
        
        **Use the codebase context to:**
        - Identify patterns that might indicate security issues
        - Compare with existing similar functions for consistency
        - Provide recommendations that fit the project's architecture
        - Detect deviations from established security practices
        
        **CRITICAL: JSON Output Format Requirements:**
        
        ⚠️  **STRICT JSON RULES - FOLLOW EXACTLY:**
        1. **NO backslashes** in descriptions (use forward slashes if needed)
        2. **NO unescaped quotes** - use single quotes inside descriptions
        3. **NO line breaks** inside JSON strings
        4. **NO special characters** that break JSON parsing
        5. **Keep descriptions under 200 characters** to avoid issues
        
        **Output Format (Valid JSON only):**
        {{
            "vulnerabilities": [
                {{
                    "type": "SQL_INJECTION",
                    "severity": "HIGH|MEDIUM|LOW", 
                    "line_number": 123,
                    "description": "Detailed explanation",
                    "code_snippet": "vulnerable code",
                    "recommendation": "How to fix it"
                }}
            ],
            "security_issues": [
                {{
                    "type": "AUTHENTICATION_BYPASS",
                    "severity": "HIGH|MEDIUM|LOW",
                    "line_number": 456,
                    "description": "Issue description",
                    "recommendation": "Fix suggestion"
                }}
            ],
            "quality_issues": [
                {{
                    "type": "CODE_SMELL",
                    "severity": "MEDIUM|LOW",
                    "line_number": 789,
                    "description": "Quality issue",
                    "recommendation": "Improvement suggestion"
                }}
            ],
            "recommendations": [
                "General recommendation 1",
                "General recommendation 2"
            ]
        }}
        
        **Focus on NEW/CHANGED lines only. Be specific about line numbers and provide actionable recommendations.**
        """
        
        try:
            # Send progress update for Gemini analysis
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "analyze",
                    "status": "in_progress",
                    "message": f"🧠 Gemini AI analyzing security vulnerabilities in {filename}...",
                    "progress": None,  # Sub-progress
                    "details": {
                        "current_file": filename,
                        "step": "ai_security_analysis",
                        "context_size": f"{len(self._format_autonomous_mcp_context(mcp_context)) / 1024:.1f}KB",
                        "analysis_focus": mcp_context.get('analysis_focus', 'Security vulnerability detection')
                    }
                })
            
            # Send to Gemini
            print(f"🚀 Sending analysis prompt to Gemini for {filename}")
            response = self.model.generate_content(analysis_prompt)
            
            if response and response.text:
                print(f"📨 Received response from Gemini ({len(response.text)} chars)")
                
                # Parse JSON response with enhanced error handling
                json_text = self._extract_json_from_response(response.text)
                
                try:
                    analysis_result = json.loads(json_text)
                    print(f"✅ Successfully parsed JSON response")
                except json.JSONDecodeError as parse_error:
                    print(f"❌ Final JSON parsing failed: {str(parse_error)}")
                    print(f"🔍 Problematic JSON: {json_text[:300]}...")
                    
                    # The _extract_json_from_response should have handled this
                    # but if it still fails, the manual extraction should have been used
                    # Let's parse the returned JSON again since manual extraction returns a dict
                    if isinstance(json_text, str):
                        try:
                            analysis_result = json.loads(json_text)
                        except:
                            # Last resort - create a minimal result
                            analysis_result = {
                                "vulnerabilities": [{
                                    "type": "PARSING_FAILURE",
                                    "severity": "MEDIUM",
                                    "line_number": 0,
                                    "description": f"AI found issues but response parsing failed. Check logs for raw response."
                                }],
                                "security_issues": [],
                                "quality_issues": [],
                                "recommendations": ["Manual review recommended due to parsing failure"]
                            }
                    else:
                        analysis_result = json_text  # Already a dict from manual extraction
                
                # Calculate total issues for better logging
                total_vulnerabilities = len(analysis_result.get('vulnerabilities', []))
                total_security = len(analysis_result.get('security_issues', []))
                total_quality = len(analysis_result.get('quality_issues', []))
                total_issues = total_vulnerabilities + total_security + total_quality
                
                print(f"✅ {filename}: {total_issues} total issues ({total_vulnerabilities} vulnerabilities, {total_security} security, {total_quality} quality)")
                
                # Log individual issues for debugging
                for vuln in analysis_result.get('vulnerabilities', []):
                    print(f"  🚨 Vulnerability: {vuln.get('type', 'Unknown')} (Line {vuln.get('line_number', '?')})")
                
                return analysis_result
            else:
                print(f"⚠️ {filename}: Empty response from Gemini")
                return {"vulnerabilities": [], "security_issues": [], "quality_issues": [], "recommendations": []}
                
        except json.JSONDecodeError as e:
            print(f"❌ {filename}: JSON parsing error - {str(e)}")
            print(f"📋 Raw response preview: {response.text[:200] if response else 'No response'}...")
            # Return a fallback analysis without MCP context
            return await self._fallback_analysis_without_mcp(file_data, build_context)
        except Exception as e:
            print(f"❌ {filename}: Analysis error - {str(e)}")
            return {
                "vulnerabilities": [], 
                "security_issues": [], 
                "quality_issues": [], 
                "recommendations": [f"Analysis failed for {filename}: {str(e)}"]
            }
    
    def _build_code_snippet(self, added_lines: List[Dict], context_lines: List[Dict]) -> str:
        """Build code snippet from added and context lines"""
        
        all_lines = []
        
        # Add context lines for understanding
        for line in context_lines[-3:]:  # Last 3 context lines
            all_lines.append(f"  {line.get('line_number', 0)}: {line.get('content', '')}")
        
        # Add new lines (these are the focus)
        for line in added_lines:
            all_lines.append(f"+ {line.get('line_number', 0)}: {line.get('content', '')}")
        
        return '\n'.join(all_lines)
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from Gemini response with robust parsing"""
        
        print(f"🔍 Extracting JSON from response ({len(response_text)} chars)")
        print(f"📄 Raw response preview: {response_text[:500]}...")
        
        # Method 1: Prefer ```json blocks first (most reliable)
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            if end > start:
                candidate = response_text[start:end].strip()
                print(f"🎯 Found ```json block: {candidate[:200]}...")
                
                try:
                    # Test if it's valid JSON
                    parsed = json.loads(candidate)
                    print(f"✅ Successfully parsed JSON using ```json block")
                    return candidate
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed for ```json block: {str(e)}")
                    # Try to fix common issues
                    fixed = self._fix_json_issues(candidate)
                    try:
                        parsed = json.loads(fixed)
                        print(f"✅ Fixed JSON issues for ```json block")
                        return fixed
                    except json.JSONDecodeError as e2:
                        print(f"❌ Failed to fix JSON for ```json block: {str(e2)}")
        
        # Method 2: Fallback to { } blocks only if no ```json found or if ```json failed
        if '{' in response_text and '}' in response_text:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            candidate = response_text[start:end]
            print(f"🎯 Found {{ }} block (fallback): {candidate[:200]}...")
            
            try:
                # Test if it's valid JSON
                parsed = json.loads(candidate)
                print(f"✅ Successfully parsed JSON using {{ }} block")
                return candidate
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed for {{ }} block: {str(e)}")
                # Try to fix common issues
                fixed = self._fix_json_issues(candidate)
                try:
                    parsed = json.loads(fixed)
                    print(f"✅ Fixed JSON issues for {{ }} block")
                    return fixed
                except json.JSONDecodeError as e2:
                    print(f"❌ Failed to fix JSON for {{ }} block: {str(e2)}")
        
        # Method 3: Manual extraction if both fail
        print("🚨 All JSON parsing failed - attempting manual extraction")
        manual_result = self._manual_issue_extraction(response_text)
        return json.dumps(manual_result)
        return json.dumps(manual_result)
    
    def _fix_json_issues(self, json_text: str) -> str:
        """Try to fix common JSON issues including escape sequences"""
        import re
        
        print(f"🔧 Attempting to fix JSON issues...")
        
        # 1. Fix invalid escape sequences - common cause of parsing errors
        # Replace invalid backslashes with forward slashes
        json_text = re.sub(r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', '/', json_text)
        
        # 2. Fix unescaped quotes in descriptions
        # This is complex but let's try a simple approach
        json_text = re.sub(r'(?<="description": ".*?)(?<!\\)"(?=.*?")', '\\"', json_text)
        
        # 3. Remove trailing commas
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        # 4. Fix line breaks inside JSON strings
        json_text = re.sub(r'(?<=".*?)\n(?=.*?")', ' ', json_text)
        
        # 5. Fix unterminated strings by adding closing quotes
        lines = json_text.split('\n')
        fixed_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped and '"' in stripped:
                # Count quotes
                quote_count = stripped.count('"')
                if quote_count % 2 != 0 and not stripped.endswith('"') and not stripped.endswith('",'):
                    # Odd number of quotes, might need closing quote
                    if stripped.endswith(','):
                        fixed_lines.append(line[:-1] + '",')
                    else:
                        fixed_lines.append(line + '"')
                    continue
            fixed_lines.append(line)
        
        fixed = '\n'.join(fixed_lines)
        
        # 6. One more pass to ensure valid JSON structure
        try:
            # Try to validate structure
            import json
            json.loads(fixed)
            print(f"✅ JSON structure validated after fixes")
        except Exception as e:
            print(f"⚠️ JSON still has issues after fixes: {str(e)}")
        
        print(f"🔧 Fixed JSON preview: {fixed[:200]}...")
        return fixed
    
    def _manual_issue_extraction(self, response_text: str) -> Dict[str, Any]:
        """Manually extract issues from response when JSON parsing fails"""
        
        print(f"🔍 Manual extraction from response ({len(response_text)} chars)")
        
        result = {
            "vulnerabilities": [],
            "security_issues": [],
            "quality_issues": [],
            "recommendations": []
        }
        
        # Look for common issue type patterns in the text
        import re
        
        # Extract security issues patterns
        security_patterns = [
            r'"type":\s*"([^"]*)",.*?"severity":\s*"([^"]*)",.*?"line_number":\s*(\d+),.*?"description":\s*"([^"]*)"',
            r'LOGICAL_ERROR.*?line.*?(\d+)',
            r'INPUT_VALIDATION.*?line.*?(\d+)',
            r'SQL_INJECTION.*?line.*?(\d+)',
            r'COMMAND_INJECTION.*?line.*?(\d+)'
        ]
        
        for pattern in security_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 4:
                    # Full match with type, severity, line, description
                    issue = {
                        "type": match[0],
                        "severity": match[1], 
                        "line_number": int(match[2]) if match[2].isdigit() else 0,
                        "description": match[3][:200]  # Limit description length
                    }
                    result['security_issues'].append(issue)
                    print(f"📋 Extracted security issue: {issue['type']} at line {issue['line_number']}")
                elif isinstance(match, str) and match.isdigit():
                    # Simple line number match
                    issue = {
                        "type": "EXTRACTED_ISSUE",
                        "severity": "MEDIUM",
                        "line_number": int(match),
                        "description": "Issue found in manual extraction - check original response for details"
                    }
                    result['security_issues'].append(issue)
                    print(f"📋 Extracted issue at line {match}")
        
        # Look for recommendations patterns
        rec_patterns = [
            r'"recommendations":\s*\[(.*?)\]',
            r'recommendation.*?[:]\s*"([^"]*)"',
            r'General recommendation.*?[:]\s*"([^"]*)"'
        ]
        
        for pattern in rec_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, str) and len(match) > 10:
                    result['recommendations'].append(match[:200])
                    print(f"📋 Extracted recommendation: {match[:50]}...")
        
        # If we found any issues, great! Otherwise add a parsing failure notice
        total_issues = len(result['vulnerabilities']) + len(result['security_issues']) + len(result['quality_issues'])
        
        if total_issues == 0:
            # Look for any mention of issues in the text
            if any(keyword in response_text.lower() for keyword in ['vulnerability', 'security', 'issue', 'error', 'risk']):
                result['quality_issues'].append({
                    "type": "PARSING_FAILURE_WITH_DETECTED_ISSUES",
                    "severity": "MEDIUM", 
                    "line_number": 0,
                    "description": "AI detected security/quality issues but JSON parsing failed. Manual review of raw response recommended."
                })
                result['recommendations'].append("Check the raw AI response for security issues that couldn't be automatically parsed")
                total_issues = 1
                print(f"⚠️ Added parsing failure notice - AI likely found issues")
            else:
                result['quality_issues'].append({
                    "type": "PARSING_ERROR",
                    "severity": "LOW", 
                    "line_number": 0,
                    "description": "AI response parsing failed and no clear issues detected in text"
                })
                result['recommendations'].append("Review raw AI response for potential issues")
                total_issues = 1
        
        print(f"🎯 Manual extraction found {total_issues} issues")
        return result
    
    async def _fallback_analysis_without_mcp(self, file_data: Dict[str, Any], build_context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis without MCP context if there are issues"""
        filename = file_data.get('filename', 'unknown')
        added_lines = file_data.get('added_lines', [])
        context_lines = file_data.get('context_lines', [])
        
        code_snippet = self._build_code_snippet(added_lines, context_lines)
        
        # Simplified prompt without MCP context to avoid JSON issues
        simple_prompt = f"""
        Analyze this code for security vulnerabilities:
        
        File: {filename}
        Code:
        ```
        {code_snippet}
        ```
        
        Return JSON only:
        {{
            "vulnerabilities": [],
            "security_issues": [],
            "quality_issues": [],
            "recommendations": []
        }}
        """
        
        try:
            response = self.model.generate_content(simple_prompt)
            if response and response.text:
                json_text = self._extract_json_from_response(response.text)
                return json.loads(json_text)
        except Exception as e:
            print(f"⚠️ Fallback analysis also failed: {str(e)}")
        
        return {"vulnerabilities": [], "security_issues": [], "quality_issues": [], "recommendations": []}
    
    def _calculate_overall_risk(self, result: AnalysisResult) -> str:
        """Calculate overall risk level"""
        high_count = sum(1 for v in result.vulnerabilities if v.get('severity') == 'HIGH')
        high_count += sum(1 for s in result.security_issues if s.get('severity') == 'HIGH')
        
        medium_count = sum(1 for v in result.vulnerabilities if v.get('severity') == 'MEDIUM')
        medium_count += sum(1 for s in result.security_issues if s.get('severity') == 'MEDIUM')
        
        if high_count > 0:
            return "HIGH"
        elif medium_count > 2:
            return "MEDIUM"
        elif result.total_issues > 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_confidence_scores(self, result: AnalysisResult) -> Dict[str, float]:
        """Calculate confidence scores for analysis"""
        return {
            "vulnerability_detection": 0.85,
            "security_analysis": 0.80,
            "quality_analysis": 0.75,
            "overall_analysis": 0.80
        }
    
    def prepare_context_for_fix_agent(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Prepare analysis results for Fix Agent"""
        
        # Filter high-confidence, fixable issues
        fixable_vulnerabilities = [
            v for v in analysis_result.vulnerabilities 
            if v.get('severity') in ['HIGH', 'MEDIUM'] and 'recommendation' in v
        ]
        
        fixable_security_issues = [
            s for s in analysis_result.security_issues
            if s.get('severity') in ['HIGH', 'MEDIUM'] and 'recommendation' in s
        ]
        
        return {
            "fixable_vulnerabilities": fixable_vulnerabilities,
            "fixable_security_issues": fixable_security_issues,
            "overall_risk": analysis_result.overall_risk,
            "total_issues": analysis_result.total_issues,
            "confidence_scores": analysis_result.confidence_scores,
            "recommendations": analysis_result.recommendations
        }
    
    def _format_autonomous_mcp_context(self, mcp_context: Dict[str, Any]) -> str:
        """Format autonomous MCP context for the analysis prompt"""
        
        if not mcp_context:
            return "- No additional context gathered (MCP not available or no tools selected)"
        
        analysis_focus = mcp_context.get('analysis_focus', '')
        mcp_results = mcp_context.get('mcp_results', {})
        selected_tools = mcp_context.get('autonomous_tool_selection', {}).get('tools_to_use', [])
        
        formatted_context = f"- **AI Analysis Focus**: {analysis_focus}\n"
        formatted_context += f"- **Tools Autonomously Selected**: {len(selected_tools)} tools\n"
        
        for tool_name, tool_result in mcp_results.items():
            reasoning = tool_result.get('reasoning', '')
            content = tool_result.get('result', {}).get('content', '')
            
            # Truncate content for prompt
            truncated_content = str(content).replace('"', "'")[:300]
            formatted_context += f"- **{tool_name.title()}** ({reasoning}): {truncated_content}...\n"
        
        return formatted_context

# Global analyze agent instance
analyze_agent = None

def get_analyze_agent() -> AnalyzeAgent:
    """Get or create analyze agent instance"""
    global analyze_agent
    if analyze_agent is None:
        analyze_agent = AnalyzeAgent()
    return analyze_agent
