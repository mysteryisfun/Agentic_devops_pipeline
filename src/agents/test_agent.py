"""
Test Agent - AI-Powered Unit Test Generation and Execution
Phase 1: Function Discovery and Question Generation
"""

import os
import sys
import ast
import json
import time
import httpx
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.utils.github_client import get_github_client

@dataclass
class ChangedFunction:
    """Information about a function that has been modified"""
    filename: str
    function_name: str
    start_line: int
    end_line: int
    full_source_code: str
    is_class_method: bool = False
    class_name: Optional[str] = None
    decorators: List[str] = None
    docstring: Optional[str] = None

@dataclass
class FunctionQuestion:
    """Generated question for a function"""
    function: ChangedFunction
    question: str
    reasoning: str

@dataclass
class GeneratedTest:
    """Represents a generated unit test"""
    function: ChangedFunction
    question: str
    test_code: str
    test_name: str
    confidence_score: float = 0.0

@dataclass
class TestStageResult:
    """Result of the test stage"""
    success: bool
    functions_discovered: int
    questions_generated: int
    tests_generated: int
    functions_with_questions: List[FunctionQuestion]
    generated_tests: List[GeneratedTest]
    errors: List[str]
    duration: float

class TestAgent:
    """
    AI-powered test generation agent
    Phase 1: Function discovery and question generation
    """
    
    def __init__(self):
        # Configure Gemini for question generation
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Configure LM Studio for CodeRM-8B test generation
        self.lm_studio_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
        self.coderm_model = os.getenv("CODERM_MODEL", "microsoft/CodeRM-8B-instruct")
        
        # Initialize GitHub client
        self.github_client = get_github_client()
        
        print("✅ Test Agent initialized (Phase 1: Function Discovery, Phase 2: CodeRM-8B)")
        print(f"   - Gemini: gemini-2.5-flash")
        print(f"   - CodeRM-8B via LM Studio: {self.lm_studio_url}")
    
    async def run_test_stage_phase1(self, diff_data: Dict[str, Any], fix_results: Dict[str, Any],
                                   repo_name: str, branch: str, progress_callback=None) -> TestStageResult:
        """
        Run Phase 1 of test stage: Function discovery and question generation
        
        Args:
            diff_data: PR diff data from analyze agent
            fix_results: Results from fix agent
            repo_name: GitHub repository name
            branch: PR branch name
            progress_callback: Function to send progress updates
            
        Returns:
            TestStageResult with discovered functions and generated questions
        """
        
        start_time = time.time()
        
        print(f"🧪 TEST AGENT Phase 1: Starting for {repo_name}#{branch}")
        
        # Send test start message - new protocol
        if progress_callback:
            await progress_callback({
                "type": "test_start",
                "stage": "test",
                "stage_index": 4,
                "message": "🧪 Starting AI-powered test generation...",
                "details": {
                    "phase": "function_discovery",
                    "repo_name": repo_name,
                    "branch": branch,
                    "pipeline_phase": "test_execution"
                }
            })
        
        try:
            # Step 1: Discover changed functions
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "test",
                    "status": "in_progress",
                    "message": "🔍 Discovering functions in changed files...",
                    "progress": 10
                })
            
            changed_functions = await self._discover_changed_functions(diff_data, repo_name, branch, progress_callback)
            
            if not changed_functions:
                # No functions to test
                if progress_callback:
                    await progress_callback({
                        "type": "stage_complete",
                        "stage": "test",
                        "status": "skipped",
                        "duration": round(time.time() - start_time, 2),
                        "message": "No functions found in changed files to test"
                    })
                
                return TestStageResult(
                    success=True,
                    functions_discovered=0,
                    questions_generated=0,
                    tests_generated=0,
                    functions_with_questions=[],
                    generated_tests=[],
                    errors=[],
                    duration=time.time() - start_time
                )
            
            if progress_callback:
                # Send function discovery results with detailed function information
                function_names = [f.function_name for f in changed_functions]
                await progress_callback({
                    "type": "functions_discovered",
                    "stage": "test",
                    "status": "in_progress",
                    "message": f"📊 Found {len(changed_functions)} functions to test",
                    "progress": 30,
                    "details": {
                        "functions_count": len(changed_functions),
                        "function_names": function_names,
                        "files_with_changes": len(set(f.filename for f in changed_functions)),
                        "functions_by_file": {
                            filename: [f.function_name for f in changed_functions if f.filename == filename]
                            for filename in set(f.filename for f in changed_functions)
                        }
                    }
                })
            
            # Step 2: Generate questions for all functions
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "test",
                    "status": "in_progress",
                    "message": "🧠 Gemini AI generating test descriptions...",
                    "progress": 50
                })
            
            function_questions = await self._generate_function_questions(changed_functions, fix_results, progress_callback)
            
            # Final phase 1 results
            duration = time.time() - start_time
            
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "test",
                    "status": "in_progress",
                    "message": f"✅ Phase 1 complete - {len(function_questions)} functions ready for test generation",
                    "progress": 75,
                    "details": {
                        "phase_1_complete": True,
                        "functions_discovered": len(changed_functions),
                        "questions_generated": len(function_questions),
                        "ready_for_test_generation": len(function_questions),
                        "phase_1_duration": round(duration, 2),
                        "next_phase": "test_generation_with_coderm"
                    }
                })
            
            print(f"✅ TEST AGENT Phase 1 completed - {len(function_questions)} functions ready")
            
            return TestStageResult(
                success=True,
                functions_discovered=len(changed_functions),
                questions_generated=len(function_questions),
                tests_generated=0,  # Phase 1 doesn't generate tests yet
                functions_with_questions=function_questions,
                generated_tests=[],  # Phase 1 doesn't generate tests yet
                errors=[],
                duration=duration
            )
            
        except Exception as e:
            error_msg = f"Test Agent Phase 1 failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            if progress_callback:
                await progress_callback({
                    "type": "error",
                    "stage": "test",
                    "message": error_msg,
                    "error_code": "TEST_PHASE1_FAILED"
                })
            
            return TestStageResult(
                success=False,
                functions_discovered=0,
                questions_generated=0,
                tests_generated=0,
                functions_with_questions=[],
                generated_tests=[],
                errors=[error_msg],
                duration=time.time() - start_time
            )
    
    async def _discover_changed_functions(self, diff_data: Dict[str, Any], repo_name: str, branch: str,
                                         progress_callback=None) -> List[ChangedFunction]:
        """Discover all functions that have been modified in the PR"""
        
        changed_functions = []
        changed_files = diff_data.get('changed_files', [])
        
        print(f"🔍 Analyzing {len(changed_files)} changed files for function discovery")
        
        if not changed_files:
            print(f"⚠️ No changed files found in diff_data. Available keys: {list(diff_data.keys())}")
            return []
        
        for i, file_data in enumerate(changed_files):
            filename = file_data.get('filename', '')
            
            print(f"📁 Processing file {i+1}/{len(changed_files)}: {filename}")
            
            # Only analyze Python files
            if not filename.endswith('.py'):
                print(f"   ⏭️ Skipping non-Python file: {filename}")
                continue
            
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "test",
                    "status": "in_progress",
                    "message": f"🔍 Analyzing functions in {filename}...",
                    "progress": 15 + (i * 15 // len(changed_files))
                })
            
            # Get the current file content from GitHub
            try:
                file_content_obj = self.github_client.get_file_content(repo_name, filename, branch)
                if not file_content_obj:
                    print(f"⚠️ Could not retrieve content for {filename}")
                    continue
                
                import base64
                file_content = base64.b64decode(file_content_obj.content).decode('utf-8')
                
                # Get changed line numbers from diff
                changed_lines = set()
                added_lines = file_data.get('added_lines', [])
                print(f"   📈 Found {len(added_lines)} added lines in {filename}")
                
                for line_data in added_lines:
                    line_number = line_data.get('line_number', 0)
                    if line_number > 0:  # Valid line number
                        changed_lines.add(line_number)
                        print(f"      Line {line_number}: {line_data.get('content', '')[:50]}...")
                
                if not changed_lines:
                    print(f"   ⚠️ No valid changed lines found in {filename}, skipping")
                    continue
                
                # Validate that changed lines are within file bounds
                file_lines = file_content.split('\n')
                valid_changed_lines = {line for line in changed_lines if 1 <= line <= len(file_lines)}
                
                if not valid_changed_lines:
                    print(f"   ⚠️ Changed lines {changed_lines} are outside file bounds (1-{len(file_lines)}) for {filename}")
                    print(f"   📄 This may indicate a diff/content mismatch - skipping file")
                    continue
                
                if valid_changed_lines != changed_lines:
                    print(f"   ⚠️ Some changed lines were invalid, using valid subset: {valid_changed_lines}")
                    changed_lines = valid_changed_lines
                
                # Parse file with AST and find functions containing changed lines
                file_functions = self._extract_functions_from_file(filename, file_content, changed_lines)
                
                if file_functions:
                    changed_functions.extend(file_functions)
                    print(f"📝 {filename}: Found {len(file_functions)} functions with changes")
                else:
                    print(f"📝 {filename}: Found 0 functions with changes (lines {changed_lines} may not be in any function)")
                
            except Exception as e:
                print(f"❌ Error analyzing {filename}: {str(e)}")
                import traceback
                print(f"   🐛 Traceback: {traceback.format_exc()}")
                continue
        
        print(f"📊 Total functions discovered: {len(changed_functions)}")
        return changed_functions
    
    def _extract_functions_from_file(self, filename: str, content: str, changed_lines: set) -> List[ChangedFunction]:
        """Extract functions from a file that contain changed lines"""
        
        functions = []
        
        try:
            tree = ast.parse(content)
            lines = content.split('\n')
            total_lines = len(lines)
            
            print(f"   🔍 Parsing {filename}: {total_lines} total lines, looking for functions containing lines {changed_lines}")
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    start_line = node.lineno
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                    
                    # Check if any changed line falls within this function
                    function_lines = set(range(start_line, end_line + 1))
                    intersection = changed_lines.intersection(function_lines)
                    
                    print(f"      📋 Function '{node.name}' at lines {start_line}-{end_line}, changed lines intersection: {intersection}")
                    
                    if intersection:
                        
                        # Extract function source code
                        function_source = '\n'.join(lines[start_line-1:end_line])
                        
                        # Get docstring if available
                        docstring = ast.get_docstring(node)
                        
                        # Get decorators
                        decorators = [ast.unparse(dec) for dec in node.decorator_list] if node.decorator_list else []
                        
                        # Check if it's a class method
                        is_class_method = False
                        class_name = None
                        for parent in ast.walk(tree):
                            if isinstance(parent, ast.ClassDef):
                                for child in parent.body:
                                    if child == node:
                                        is_class_method = True
                                        class_name = parent.name
                                        break
                        
                        function = ChangedFunction(
                            filename=filename,
                            function_name=node.name,
                            start_line=start_line,
                            end_line=end_line,
                            full_source_code=function_source,
                            is_class_method=is_class_method,
                            class_name=class_name,
                            decorators=decorators,
                            docstring=docstring
                        )
                        
                        functions.append(function)
                        print(f"   ✅ Function: {node.name} (lines {start_line}-{end_line}) contains changes at lines {intersection}")
            
            if not functions and changed_lines:
                print(f"   ⚠️ No functions found containing changed lines {changed_lines}")
                print(f"   📋 Available functions in file:")
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        start_line = node.lineno
                        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                        print(f"      - {node.name} (lines {start_line}-{end_line})")
                        
        except SyntaxError as e:
            print(f"❌ Syntax error in {filename}: {e}")
        except Exception as e:
            print(f"❌ Error parsing {filename}: {e}")
            import traceback
            print(f"   🐛 Traceback: {traceback.format_exc()}")
        
        return functions
    
    async def _generate_function_questions(self, functions: List[ChangedFunction], fix_results: Dict[str, Any],
                                          progress_callback=None) -> List[FunctionQuestion]:
        """Generate descriptive questions for all functions using Gemini in batch"""
        
        if not functions:
            return []
        
        print(f"🧠 Generating questions for {len(functions)} functions using Gemini...")
        
        # Prepare batch prompt for Gemini
        functions_info = []
        for func in functions:
            func_info = {
                "filename": func.filename,
                "function_name": func.function_name,
                "is_class_method": func.is_class_method,
                "class_name": func.class_name,
                "docstring": func.docstring,
                "source_code": func.full_source_code[:500] + "..." if len(func.full_source_code) > 500 else func.full_source_code
            }
            functions_info.append(func_info)
        
        # Check if any functions were fixed
        fix_context = ""
        if fix_results.get('fixes_applied', 0) > 0:
            fix_context = f"\nNote: {fix_results['fixes_applied']} functions were automatically fixed for security/quality issues."
        
        batch_prompt = f"""You are an expert AI assistant analyzing code functions to generate test descriptions for unit test creation.

TASK: For each function below, create a concise, clear question that describes what the function does and its expected behavior.

CONTEXT: These questions will be used by CodeRM-8B model to generate actual unit tests, so they should be specific and actionable.

{fix_context}

FUNCTIONS TO ANALYZE:
{json.dumps(functions_info, indent=2)}

REQUIRED OUTPUT FORMAT (strict JSON):
{{
    "function_questions": [
        {{
            "filename": "exact_filename_from_input",
            "function_name": "exact_function_name_from_input",
            "question": "Clear, specific description of what the function should do",
            "reasoning": "Brief explanation of why this function needs testing"
        }}
    ]
}}

GUIDELINES:
- Keep questions concise but descriptive (1-2 sentences)
- Focus on WHAT the function does, not HOW it does it
- Include edge cases or important behaviors to test
- Use the exact filename and function_name from the input
- Make questions actionable for test generation

Respond with ONLY the JSON object, no additional text."""

        try:
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "test",
                    "status": "in_progress",
                    "message": "🧠 Gemini AI analyzing functions and generating descriptions...",
                    "progress": 60
                })
            
            response = self.model.generate_content(batch_prompt)
            
            if not response or not response.text:
                print("❌ No response from Gemini for question generation")
                return []
            
            # Parse the JSON response
            json_text = self._extract_json_from_response(response.text)
            questions_data = json.loads(json_text)
            
            # Create FunctionQuestion objects
            function_questions = []
            questions_list = questions_data.get('function_questions', [])
            
            # Match questions with functions
            for question_data in questions_list:
                question_filename = question_data.get('filename', '')
                question_func_name = question_data.get('function_name', '')
                
                # Find matching function
                matching_function = None
                for func in functions:
                    if func.filename == question_filename and func.function_name == question_func_name:
                        matching_function = func
                        break
                
                if matching_function:
                    func_question = FunctionQuestion(
                        function=matching_function,
                        question=question_data.get('question', ''),
                        reasoning=question_data.get('reasoning', '')
                    )
                    function_questions.append(func_question)
                    print(f"   ✅ {question_func_name}: {question_data.get('question', '')[:60]}...")
            
            print(f"✅ Generated {len(function_questions)} function questions")
            return function_questions
            
        except Exception as e:
            print(f"❌ Error generating function questions: {str(e)}")
            return []
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from Gemini response with improved parsing"""
        
        # Remove any markdown formatting
        text = response_text.strip()
        
        # Method 1: Look for ```json blocks
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            if end > start:
                json_content = text[start:end].strip()
                # Validate it's actually JSON
                try:
                    json.loads(json_content)
                    return json_content
                except:
                    pass
        
        # Method 2: Look for ```JSON blocks (case insensitive)
        if '```JSON' in text or '```Json' in text:
            for variant in ['```JSON', '```Json']:
                if variant in text:
                    start = text.find(variant) + len(variant)
                    end = text.find('```', start)
                    if end > start:
                        json_content = text[start:end].strip()
                        try:
                            json.loads(json_content)
                            return json_content
                        except:
                            pass
        
        # Method 3: Look for any code block with JSON
        if '```' in text:
            lines = text.split('\n')
            in_code_block = False
            json_lines = []
            
            for line in lines:
                if line.strip().startswith('```'):
                    if in_code_block:
                        # End of block - try to parse
                        potential_json = '\n'.join(json_lines)
                        try:
                            json.loads(potential_json)
                            return potential_json
                        except:
                            json_lines = []
                    in_code_block = not in_code_block
                elif in_code_block:
                    json_lines.append(line)
        
        # Method 4: Find JSON object boundaries
        if '{' in text and '}' in text:
            start = text.find('{')
            
            # Find the matching closing brace
            brace_count = 0
            end = start
            
            for i in range(start, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            if end > start:
                json_content = text[start:end]
                try:
                    json.loads(json_content)
                    return json_content
                except:
                    pass
        
        # Fallback - create empty structure
        print("⚠️ Could not extract valid JSON from Gemini response, using fallback")
        return '{"function_questions": []}'

    async def run_test_stage_phase2(self, function_questions: List[FunctionQuestion], 
                                   progress_callback=None) -> List[GeneratedTest]:
        """Phase 2: Generate unit tests using CodeRM-8B via LM Studio"""
        
        if not function_questions:
            print("⚠️ No function questions provided for Phase 2")
            return []
        
        print(f"🧪 Starting Phase 2: Generating unit tests for {len(function_questions)} functions")
        start_time = time.time()
        
        generated_tests = []
        
        if progress_callback:
            await progress_callback({
                "type": "status_update",
                "stage": "test",
                "status": "in_progress",
                "message": "🤖 CodeRM-8B generating unit tests...",
                "progress": 70
            })
        
        try:
            # Test LM Studio connection
            if not await self._test_lm_studio_connection():
                print("❌ LM Studio connection failed")
                return []
            
            # Generate tests for each function
            for i, func_question in enumerate(function_questions):
                function_name = func_question.function.function_name
                
                if progress_callback:
                    progress = 70 + (i * 20 // len(function_questions))
                    await progress_callback({
                        "type": "test_generation_start",
                        "stage": "test",
                        "status": "in_progress",
                        "message": f"🧪 Generating test for {function_name}...",
                        "progress": progress,
                        "details": {
                            "current_function": function_name,
                            "function_index": i + 1,
                            "total_functions": len(function_questions),
                            "phase": "coderm_generation"
                        }
                    })
                
                test = await self._generate_single_test(func_question)
                if test:
                    generated_tests.append(test)
                    
                    # Send test generation completion message for this function
                    if progress_callback:
                        await progress_callback({
                            "type": "test_generated",
                            "stage": "test",
                            "status": "in_progress",
                            "message": f"✅ Generated test for {function_name}",
                            "details": {
                                "function_name": function_name,
                                "test_name": test.test_name,
                                "confidence_score": test.confidence_score,
                                "test_generated": True,
                                "ready_for_execution": True
                            }
                        })
                    
                    print(f"   ✅ Generated test for {function_name}")
                else:
                    # Send test generation failure message
                    if progress_callback:
                        await progress_callback({
                            "type": "test_generation_failed",
                            "stage": "test",
                            "status": "in_progress",
                            "message": f"❌ Failed to generate test for {function_name}",
                            "details": {
                                "function_name": function_name,
                                "test_generated": False,
                                "error": "Test generation failed"
                            }
                        })
                    
                    print(f"   ❌ Failed to generate test for {function_name}")
            
            duration = time.time() - start_time
            print(f"✅ Phase 2 completed: {len(generated_tests)}/{len(function_questions)} tests generated in {duration:.2f}s")
            
            return generated_tests
            
        except Exception as e:
            print(f"❌ Phase 2 failed: {str(e)}")
            return []

    async def _test_lm_studio_connection(self) -> bool:
        """Test connection to LM Studio server"""
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.lm_studio_url}/models")
                
                if response.status_code == 200:
                    models = response.json()
                    print(f"✅ LM Studio connected. Available models: {len(models.get('data', []))}")
                    return True
                else:
                    print(f"❌ LM Studio responded with status {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ LM Studio connection failed: {str(e)}")
            print(f"   Make sure LM Studio is running on {self.lm_studio_url}")
            return False

    async def _generate_single_test(self, func_question: FunctionQuestion) -> Optional[GeneratedTest]:
        """Generate a single unit test using CodeRM-8B"""
        
        # Prepare the prompt for CodeRM-8B
        prompt = self._create_coderm_prompt(func_question)
        
        try:
            print(f"🔄 Sending request to CodeRM-8B for {func_question.function.function_name}...")
            async with httpx.AsyncClient(timeout=None) as client:  # No timeout - wait as long as needed
                payload = {
                    "model": self.coderm_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1500,
                    "stream": False
                }
                
                print(f"📤 Making API call to {self.lm_studio_url}/chat/completions...")
                response = await client.post(
                    f"{self.lm_studio_url}/chat/completions",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"📥 Received response with status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"✅ Parsing JSON response...")
                    result = response.json()
                    test_code = result['choices'][0]['message']['content']
                    
                    print(f"🔍 Raw CodeRM-8B response for {func_question.function.function_name}:")
                    print(f"   Length: {len(test_code)} characters")
                    print(f"   Full content:")
                    print("=" * 60)
                    print(test_code)
                    print("=" * 60)
                    
                    # Extract and clean the test code
                    print(f"🧹 Cleaning test code...")
                    cleaned_code = self._clean_test_code(test_code)
                    
                    # Always accept the response, even if it seems short
                    if not cleaned_code:
                        print(f"⚠️ Cleaned code is empty, using raw response")
                        cleaned_code = test_code.strip()
                    
                    print(f"🏷️ Extracting test name...")
                    test_name = self._extract_test_name(cleaned_code, func_question.function.function_name)
                    
                    print(f"✅ Successfully processed test for {func_question.function.function_name}")
                    print(f"   Test name: {test_name}")
                    print(f"   Final code length: {len(cleaned_code)} characters")
                    
                    return GeneratedTest(
                        function=func_question.function,
                        question=func_question.question,
                        test_code=cleaned_code,
                        test_name=test_name,
                        confidence_score=0.8
                    )
                else:
                    print(f"❌ CodeRM-8B API error: {response.status_code}")
                    print(f"   Response text: {response.text[:500]}")
                    return None
                    
        except httpx.ConnectError:
            print(f"❌ Connection error to LM Studio for {func_question.function.function_name}")
            print(f"   Make sure LM Studio is running on {self.lm_studio_url}")
            return None
        except Exception as e:
            print(f"❌ Error generating test for {func_question.function.function_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _create_coderm_prompt(self, func_question: FunctionQuestion) -> str:
        """Create a concise prompt for CodeRM-8B to generate unit tests"""
        
        func = func_question.function
        
        prompt = f"""Generate a Python unit test for this function:

FUNCTION:
```python
{func.full_source_code}
```

TASK: {func_question.question}

Generate a complete test using pytest or unittest. Include:
- Import statements
- Test function with descriptive name
- Multiple test cases (normal, edge cases, errors)
- Clear assertions

Example format:
```python
import pytest

def test_{func.function_name}():
    # Normal case
    assert function_name("input") == expected
    
    # Edge case
    assert function_name("") == expected_edge
    
    # Error case
    with pytest.raises(ValueError):
        function_name(None)
```

Generate the complete test code:"""

        return prompt

    def _clean_test_code(self, raw_code: str) -> str:
        """Clean and format the generated test code - preserve as much as possible"""
        
        if not raw_code:
            return ""
        
        code = raw_code.strip()
        
        # Remove markdown formatting if present
        if '```python' in code:
            start = code.find('```python') + 9
            end = code.find('```', start)
            if end > start:
                code = code[start:end].strip()
            else:
                # No closing ```, take everything after ```python
                code = code[start:].strip()
        elif '```' in code:
            start = code.find('```') + 3
            end = code.find('```', start)
            if end > start:
                code = code[start:end].strip()
            else:
                # No closing ```, take everything after ```
                code = code[start:].strip()
        
        # If no markdown was found, use the original code
        if not code or len(code) < len(raw_code.strip()) // 2:
            print(f"   Using raw code (no markdown or markdown extraction failed)")
            code = raw_code.strip()
        
        # Just clean up basic whitespace, don't filter based on content
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Only skip empty lines at the very beginning
            if not cleaned_lines and not line.strip():
                continue
            cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        
        print(f"   Cleaned code: {len(result)} characters")
        return result

    def _extract_test_name(self, test_code: str, function_name: str) -> str:
        """Extract the main test function name from generated code"""
        
        lines = test_code.split('\n')
        found_names = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('def test_'):
                # Extract function name
                if '(' in line:
                    test_name = line.split('(')[0].replace('def ', '')
                    found_names.append(test_name)
        
        # Return the first test function found, or one that matches the function name
        for name in found_names:
            if function_name.lower() in name.lower():
                return name
        
        # Return first test function found
        if found_names:
            return found_names[0]
        
        # Check for class-based tests
        for line in lines:
            line = line.strip()
            if line.startswith('class Test') and 'unittest.TestCase' in line:
                class_name = line.split('(')[0].replace('class ', '')
                return f"{class_name}.test_{function_name}"
        
        # Fallback: generate a test name
        return f"test_{function_name}"

    async def run_test_stage_phase3(self, generated_tests: List[GeneratedTest], 
                                   progress_callback=None) -> TestStageResult:
        """
        Run Phase 3 of test stage: Execute generated tests and collect results
        
        Args:
            generated_tests: List of GeneratedTest objects from Phase 2
            progress_callback: Function to send progress updates
            
        Returns:
            TestStageResult with execution results
        """
        import tempfile
        import subprocess
        import json
        import os
        import re
        
        start_time = time.time()
        
        if progress_callback:
            await progress_callback({
                "type": "status_update",
                "stage": "test",
                "status": "in_progress",
                "message": f"🧪 Phase 3: Executing {len(generated_tests)} generated tests...",
                "progress": 5,
                "details": {
                    "phase": "test_execution",
                    "tests_to_execute": len(generated_tests)
                }
            })
        
        if not generated_tests:
            return TestStageResult(
                success=True,
                functions_discovered=0,
                questions_generated=0,
                tests_generated=0,
                functions_with_questions=[],
                generated_tests=[],
                errors=["No tests to execute"],
                duration=time.time() - start_time
            )
        
        try:
            # Create temporary directory for test execution
            temp_dir = tempfile.mkdtemp(prefix="test_execution_")
            
            # Create __init__.py to make it a package
            init_file = os.path.join(temp_dir, "__init__.py")
            with open(init_file, 'w') as f:
                f.write('# Generated test package\n')
            
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "test",
                    "status": "in_progress",
                    "message": f"📁 Created test environment, writing {len(generated_tests)} test files...",
                    "progress": 10
                })
            
            # Write test files
            test_files = []
            execution_results = []
            
            for i, test in enumerate(generated_tests):
                # Create filename based on function and test name
                function_name = test.function.function_name
                test_filename = f"test_{function_name}_{i}.py"
                test_path = os.path.join(temp_dir, test_filename)
                
                # Ensure test has proper imports for LM Studio generated code
                test_code = test.test_code
                if 'import unittest' not in test_code:
                    test_code = "import unittest\nimport sys\nimport os\n\n" + test_code
                
                # Add function import if needed (mock the function being tested)
                if function_name not in test_code and f"def {function_name}" not in test_code:
                    mock_function = f"""
def {function_name}(*args, **kwargs):
    '''Mock function for testing - replace with actual implementation'''
    if len(args) == 2 and all(isinstance(arg, (int, float)) for arg in args):
        return args[0] + args[1]  # Simple addition for demo
    return None

"""
                    test_code = test_code.replace("import unittest", f"import unittest\n{mock_function}")
                
                with open(test_path, 'w', encoding='utf-8') as f:
                    f.write(test_code)
                
                test_files.append(test_path)
            
            # Execute tests
            total_methods_passed = 0
            total_methods_failed = 0
            total_methods_errored = 0
            
            for i, (test_file, test_data) in enumerate(zip(test_files, generated_tests)):
                function_name = test_data.function.function_name
                
                if progress_callback:
                    await progress_callback({
                        "type": "status_update",
                        "stage": "test",
                        "status": "in_progress",
                        "message": f"🔄 Executing test {i+1}/{len(test_files)}: {function_name}",
                        "progress": 10 + (i * 70 // len(test_files)),
                        "details": {
                            "current_test": function_name,
                            "tests_completed": i,
                            "total_tests": len(test_files)
                        }
                    })
                
                # Execute single test
                test_result = await self._execute_single_test_file(test_file, test_data, progress_callback)
                execution_results.append(test_result)
                
                # Send individual test case results for this function
                if progress_callback:
                    individual_test_cases = test_result.get('individual_tests', [])
                    await progress_callback({
                        "type": "test_execution_result",
                        "stage": "test",
                        "status": "in_progress",
                        "message": f"📊 Test results for {function_name}: {len([t for t in individual_test_cases if t['status'] == 'PASSED'])}/{len(individual_test_cases)} methods passed",
                        "details": {
                            "function_name": function_name,
                            "file_status": test_result.get('status'),
                            "execution_time": test_result.get('execution_time', 0),
                            "individual_test_cases": individual_test_cases,
                            "total_methods": len(individual_test_cases),
                            "methods_passed": len([t for t in individual_test_cases if t['status'] == 'PASSED']),
                            "methods_failed": len([t for t in individual_test_cases if t['status'] == 'FAILED']),
                            "methods_errored": len([t for t in individual_test_cases if t['status'] == 'ERROR'])
                        }
                    })
                
                # Count individual test methods
                if 'individual_tests' in test_result:
                    for method in test_result['individual_tests']:
                        if method['status'] == 'PASSED':
                            total_methods_passed += 1
                        elif method['status'] == 'FAILED':
                            total_methods_failed += 1
                        else:
                            total_methods_errored += 1
            
            # Calculate final statistics
            tests_executed = len(execution_results)
            tests_passed = len([r for r in execution_results if r.get('status') == 'PASSED'])
            tests_failed = len([r for r in execution_results if r.get('status') == 'FAILED'])
            tests_errored = len([r for r in execution_results if r.get('status') == 'ERROR'])
            
            total_methods = total_methods_passed + total_methods_failed + total_methods_errored
            method_success_rate = (total_methods_passed / total_methods * 100) if total_methods > 0 else 0
            
            duration = time.time() - start_time
            
            # Send final progress update
            if progress_callback:
                await progress_callback({
                    "type": "status_update",
                    "stage": "test",
                    "status": "in_progress",
                    "message": f"✅ Test execution complete: {tests_passed}/{tests_executed} files passed, {total_methods_passed}/{total_methods} methods passed",
                    "progress": 90,
                    "details": {
                        "tests_executed": tests_executed,
                        "tests_passed": tests_passed,
                        "tests_failed": tests_failed,
                        "tests_errored": tests_errored,
                        "total_methods": total_methods,
                        "methods_passed": total_methods_passed,
                        "methods_failed": total_methods_failed,
                        "methods_errored": total_methods_errored,
                        "method_success_rate": f"{method_success_rate:.1f}%"
                    }
                })
            
            # Clean up temporary directory
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass
            
            return TestStageResult(
                success=True,
                functions_discovered=len(generated_tests),
                questions_generated=len(generated_tests),
                tests_generated=len(generated_tests),
                functions_with_questions=[],  # Not applicable for Phase 3
                generated_tests=generated_tests,
                errors=[],
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Test execution failed: {str(e)}"
            
            return TestStageResult(
                success=False,
                functions_discovered=0,
                questions_generated=0,
                tests_generated=0,
                functions_with_questions=[],
                generated_tests=[],
                errors=[error_msg],
                duration=duration
            )

    async def _execute_single_test_file(self, test_file: str, test_data: GeneratedTest, 
                                       progress_callback=None) -> Dict[str, Any]:
        """Execute a single test file and return detailed results"""
        import subprocess
        import json
        import os
        
        test_name = os.path.basename(test_file)
        start_time = time.time()
        
        try:
            # Execute test using pytest with verbose output
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v",  # Verbose output to see individual methods
                "--tb=short",  # Short traceback
                "-s"  # Don't capture output (show print statements)
            ], 
            capture_output=True, 
            text=True, 
            timeout=30,  # 30 second timeout per test
            cwd=os.path.dirname(test_file)
            )
            
            execution_time = time.time() - start_time
            
            # Parse pytest output to extract individual test method results
            individual_tests = self._parse_pytest_output(result.stdout, result.stderr)
            
            # Determine overall file status
            if result.returncode == 0:
                status = "PASSED"
                error_message = None
            else:
                # Check if it's a test failure or error
                if "FAILED" in result.stdout or "AssertionError" in result.stderr:
                    status = "FAILED"
                    error_message = self._extract_failure_reason(result.stdout, result.stderr)
                else:
                    status = "ERROR"
                    error_message = self._extract_error_reason(result.stdout, result.stderr)
            
            return {
                "test_name": test_name,
                "function_name": test_data.function.function_name,
                "filename": test_file,
                "status": status,
                "execution_time": execution_time,
                "error_message": error_message,
                "individual_tests": individual_tests,
                "pytest_stdout": result.stdout,
                "pytest_stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                "test_name": test_name,
                "function_name": test_data.function.function_name,
                "filename": test_file,
                "status": "ERROR",
                "execution_time": execution_time,
                "error_message": "Test execution timeout (30s)",
                "individual_tests": [],
                "pytest_stdout": "",
                "pytest_stderr": "Timeout"
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "test_name": test_name,
                "function_name": test_data.function.function_name,
                "filename": test_file,
                "status": "ERROR",
                "execution_time": execution_time,
                "error_message": f"Execution exception: {str(e)}",
                "individual_tests": [],
                "pytest_stdout": "",
                "pytest_stderr": str(e)
            }

    def _parse_pytest_output(self, stdout: str, stderr: str) -> List[Dict[str, Any]]:
        """Parse pytest output to extract individual test method results"""
        individual_tests = []
        lines = stdout.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for test method execution lines in pytest verbose format
            # Format: path/file.py::ClassName::test_method_name PASSED/FAILED [percentage%]
            if "::" in line and any(status in line for status in ["PASSED", "FAILED", "ERROR", "SKIPPED"]):
                try:
                    # Split by :: to get components
                    parts = line.split("::")
                    if len(parts) >= 3:  # file::class::method status
                        file_part = parts[0]
                        class_name = parts[1] 
                        method_and_status = parts[2]
                        
                        # Extract method name and status
                        if "PASSED" in method_and_status:
                            method_name = method_and_status.split("PASSED")[0].strip()
                            status = "PASSED"
                        elif "FAILED" in method_and_status:
                            method_name = method_and_status.split("FAILED")[0].strip()
                            status = "FAILED"
                        elif "ERROR" in method_and_status:
                            method_name = method_and_status.split("ERROR")[0].strip()
                            status = "ERROR"
                        elif "SKIPPED" in method_and_status:
                            method_name = method_and_status.split("SKIPPED")[0].strip()
                            status = "SKIPPED"
                        else:
                            continue
                        
                        individual_tests.append({
                            "name": f"{class_name}::{method_name}",
                            "method": method_name,
                            "class": class_name,
                            "status": status,
                            "file": os.path.basename(file_part) if file_part else "unknown"
                        })
                        
                except Exception:
                    # Skip lines that can't be parsed
                    continue
        
        return individual_tests

    def _extract_failure_reason(self, stdout: str, stderr: str) -> str:
        """Extract meaningful failure reason from pytest output"""
        lines = (stdout + "\n" + stderr).split('\n')
        
        for line in lines:
            if "AssertionError" in line:
                return line.strip()
            elif "FAILED" in line and "::" in line:
                return line.split("::")[-1].strip()
        
        return "Test assertion failed"
    
    def _extract_error_reason(self, stdout: str, stderr: str) -> str:
        """Extract error reason from pytest output"""
        lines = (stdout + "\n" + stderr).split('\n')
        
        for line in lines:
            if any(error in line for error in ["ImportError", "ModuleNotFoundError", "SyntaxError", "AttributeError"]):
                return line.strip()
            elif "ERROR" in line and "::" in line:
                return line.split("::")[-1].strip()
        
        return "Test execution error"

# Global instance
_test_agent_instance = None

def get_test_agent():
    """Get global Test Agent instance"""
    global _test_agent_instance
    if _test_agent_instance is None:
        _test_agent_instance = TestAgent()
    return _test_agent_instance
