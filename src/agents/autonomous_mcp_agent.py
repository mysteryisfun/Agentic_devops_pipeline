"""
Autonomous MCP Tool Agent - Lets AI decide which MCP tools to use
"""

import json
from typing import Dict, Any, List, Optional

class AutonomousMCPAgent:
    """
    Agent that allows Gemini to autonomously decide which MCP tools to use
    """
    
    def __init__(self, mcp_client, gemini_model):
        self.mcp_client = mcp_client
        self.model = gemini_model
        self.available_tools = [
            {
                "name": "ask_codebase",
                "description": "Ask any natural language question about the codebase. AI decides what to ask based on analysis needs.",
                "parameters": ["question"],
                "examples": [
                    "Where is the function 'execute_sql' defined?",
                    "Find all SQL injection vulnerabilities in database functions",
                    "How is user authentication handled in this project?",
                    "What cryptographic libraries are used for password hashing?",
                    "Show me all API endpoints that handle user input",
                    "Are there any hardcoded secrets or API keys?",
                    "Find similar security patterns to this function"
                ]
            }
        ]
    
    async def autonomous_analysis(self, filename: str, code_snippet: str, context: Dict[str, Any], 
                                  progress_callback=None) -> Dict[str, Any]:
        """
        Let Gemini autonomously decide which MCP tools to use for analysis
        """
        
        # Step 1: Ask Gemini which tools it wants to use
        tool_selection_prompt = f"""
        You are analyzing a code file for security vulnerabilities. You have access to MCP tools to gather more context from the codebase.
        
        **File**: {filename}
        **Code Changes**:
        ```
        {code_snippet}
        ```
        
        **Available MCP Tool**:
        {json.dumps(self.available_tools, indent=2)}
        
        **🎯 Smart Analysis Guidelines:**
        - **Any changes**: Ask 1 specific, targeted question about the most critical security aspect
        - **Focus on the highest risk**: Prioritize the most dangerous vulnerability pattern you see
        - **Be precise**: Ask about the exact function, pattern, or security concern you identify
        
        **🎨 Question Examples for Different Code Types:**
        
        **For Database Code:**
        - "Where is the execute_query function defined and does it use prepared statements?"
        - "Find all SQL queries that use string concatenation or f-strings"
        
        **For Authentication Code:**  
        - "How is password hashing implemented in this project?"
        - "Are there other authentication methods besides this one?"
        
        **For API Endpoints:**
        - "What input validation is used for user-controlled parameters?"
        - "Find all API routes that handle sensitive operations"
        
        **For Crypto/Security:**
        - "What cryptographic libraries are used for encryption?"
        - "Are there any hardcoded secrets or configuration issues?"
        
        **Your Task**: 
        1. **Analyze the scope** of the code changes (small/medium/large)
        2. **Ask 1 specific question** about the highest priority security concern you identify
        3. **Be targeted** - ask about the specific function/pattern that poses the greatest risk
        4. **Focus on critical security implications** of the actual code being changed
        
        **Respond with JSON only**:
        {{
            "scope_assessment": "small|medium|large - based on lines of code changed",
            "questions_to_ask": [
                {{
                    "question": "Where is the execute_sql function defined and what SQL injection protections does it have?",
                    "reasoning": "This is the highest risk - direct SQL execution without clear protection"
                }}
            ],
            "analysis_focus": "What specific security concern is most critical based on the code"
        }}
        """
        
        print(f"🤖 Asking Gemini to select MCP tools for {filename}...")
        
        try:
            # Get tool selection from Gemini
            response = self.model.generate_content(tool_selection_prompt)
            if not response or not response.text:
                print("⚠️ No tool selection response from Gemini")
                return {}
            
            # Parse the question selection
            question_selection = self._extract_json_from_response(response.text)
            selected_questions = json.loads(question_selection)
            
            scope = selected_questions.get('scope_assessment', 'medium')
            questions = selected_questions.get('questions_to_ask', [])
            
            print(f"🎯 AI assessed scope as: {scope}")
            print(f"🔧 AI wants to ask {len(questions)} questions")
            
            # Execute the selected questions with smart limits
            max_questions = self._get_max_questions_for_scope(scope)
            limited_questions = questions[:max_questions]
            
            if len(questions) > max_questions:
                print(f"⚠️ Limited to {max_questions} questions for {scope} scope (was {len(questions)})")
            
            mcp_results = {}
            total_context_chars = 0
            max_context_budget = 15000  # Reasonable context limit
            
            for i, question_spec in enumerate(limited_questions):
                question = question_spec.get('question', '')
                reasoning = question_spec.get('reasoning', '')
                
                print(f"🔍 Question {i+1}: {question}")
                print(f"💭 Reasoning: {reasoning}")
                
                # Send progress update if callback provided
                if progress_callback:
                    await progress_callback({
                        'questions_asked': i + 1,
                        'total_questions': len(limited_questions),
                        'current_question': question,
                        'reasoning': reasoning,
                        'scope_assessment': scope
                    })
                
                # Execute the question
                result = await self._execute_mcp_question(question)
                
                # Check context budget
                result_chars = len(str(result.get('content', '')))
                if total_context_chars + result_chars > max_context_budget:
                    print(f"⚠️ Context budget reached ({total_context_chars}/{max_context_budget} chars) - stopping")
                    break
                
                total_context_chars += result_chars
                
                # Print response (limited)
                if result and 'content' in result:
                    content_preview = str(result['content'])[:200]
                    print(f"📄 Response ({result_chars} chars): {content_preview}...")
                    
                    # Check for generic/repeated responses
                    if self._is_generic_response(result['content']):
                        print(f"⚠️ Generic response detected - may skip similar questions")
                elif result and 'error' in result:
                    print(f"❌ Error: {result['error']}")
                
                mcp_results[f"question_{i+1}"] = {
                    "question": question,
                    "result": result,
                    "reasoning": reasoning
                }
            
            print(f"📊 Total context gathered: {total_context_chars} characters")
            
            return {
                "scope_assessment": scope,
                "questions_asked": limited_questions,
                "mcp_results": mcp_results,
                "analysis_focus": selected_questions.get('analysis_focus', ''),
                "total_context_chars": total_context_chars
            }
            
        except Exception as e:
            print(f"❌ Autonomous MCP question execution failed: {str(e)}")
            return {}
    
    def _get_max_questions_for_scope(self, scope: str) -> int:
        """Get maximum number of questions based on code change scope - LIMITED TO 1"""
        # Always return 1 to limit to single query per call
        return 1
    
    def _is_generic_response(self, content: str) -> bool:
        """Check if the MCP response is generic/repeated"""
        content_str = str(content).lower()
        generic_indicators = [
            "repository mysteryisfun/test",
            "similar node information found",
            "no valid subpaths found",
            "information about method"
        ]
        return any(indicator in content_str for indicator in generic_indicators)
    
    async def _execute_mcp_question(self, question: str) -> Dict[str, Any]:
        """Execute a natural language question against the MCP client"""
        
        if not self.mcp_client:
            return {"error": "MCP client not available"}
        
        try:
            # Use search_code as the backend for natural language questions
            # In a more sophisticated setup, this could route to different MCP tools
            # based on question type, but for now we keep it simple
            result = self.mcp_client.search_code(question, 10)
            
            # Extract content from MCP result
            content = self.mcp_client.get_content_from_result(result)
            return {
                "content": content,
                "raw_result": result
            }
            
        except Exception as e:
            return {"error": f"Question execution failed: {str(e)}"}
    
    async def _execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy method - kept for compatibility but now routes to question execution"""
        
        if not self.mcp_client:
            return {"error": "MCP client not available"}
        
        try:
            if tool_name == "ask_codebase":
                # New single tool approach
                question = parameters.get('question', '')
                return await self._execute_mcp_question(question)
            else:
                # Legacy support - deprecated
                return {"error": f"Tool {tool_name} deprecated - use ask_codebase instead"}
            
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from Gemini response"""
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            return response_text[start:end].strip()
        elif '{' in response_text and '}' in response_text:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            return response_text[start:end]
        else:
            return '{"scope_assessment": "medium", "questions_to_ask": [], "analysis_focus": "Failed to parse question selection"}'
