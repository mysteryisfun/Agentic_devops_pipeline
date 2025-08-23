"""
Build Agent - Code Compilation and Metadata Extraction
Part of the Hackademia AI Pipeline Multi-Agent System
"""

import ast
import os
import sys
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import tempfile
import json

@dataclass
class BuildResult:
    """Result of build operation"""
    success: bool
    metadata: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    dependencies: List[str]
    file_info: Dict[str, Any]

class BuildAgent:
    """
    Build Agent responsible for:
    - Code compilation and syntax validation
    - Metadata extraction (functions, classes, imports)
    - Dependency analysis
    - Build context preparation for other agents
    """
    
    def __init__(self):
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c'}
    
    def analyze_python_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze Python file using AST"""
        try:
            tree = ast.parse(content, filename=file_path)
            
            metadata = {
                "functions": [],
                "classes": [],
                "imports": [],
                "variables": [],
                "complexity_score": 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metadata["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [ast.unparse(dec) for dec in node.decorator_list] if node.decorator_list else []
                    })
                    
                elif isinstance(node, ast.ClassDef):
                    metadata["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "bases": [ast.unparse(base) for base in node.bases],
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                    
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        metadata["imports"].append({
                            "module": alias.name,
                            "alias": alias.asname,
                            "type": "import"
                        })
                        
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        metadata["imports"].append({
                            "module": node.module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "type": "from_import"
                        })
                        
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            metadata["variables"].append({
                                "name": target.id,
                                "line": node.lineno
                            })
            
            # Simple complexity calculation
            metadata["complexity_score"] = len(metadata["functions"]) + len(metadata["classes"]) * 2
            
            return metadata
            
        except SyntaxError as e:
            raise Exception(f"Python syntax error: {e}")
        except Exception as e:
            raise Exception(f"AST analysis failed: {e}")
    
    def check_python_syntax(self, content: str) -> List[str]:
        """Check Python syntax and return errors"""
        errors = []
        try:
            ast.parse(content)
        except SyntaxError as e:
            errors.append(f"Syntax Error at line {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"Parse Error: {str(e)}")
        
        return errors
    
    def extract_dependencies(self, file_path: str, content: str) -> List[str]:
        """Extract dependencies from file"""
        dependencies = []
        
        if file_path.endswith('.py'):
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        dependencies.extend([alias.name.split('.')[0] for alias in node.names])
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        dependencies.append(node.module.split('.')[0])
            except:
                pass
                
        elif file_path.endswith('.js') or file_path.endswith('.ts'):
            # Simple regex-based extraction for JS/TS
            import re
            import_pattern = r'(?:import|require)\s*\(?[\'"]([^\'"]+)[\'"]'
            matches = re.findall(import_pattern, content)
            dependencies.extend(matches)
        
        return list(set(dependencies))  # Remove duplicates
    
    def compile_and_validate(self, files: Dict[str, str]) -> BuildResult:
        """
        Compile and validate code files
        
        Args:
            files: Dict mapping file_path -> file_content
            
        Returns:
            BuildResult with compilation status and metadata
        """
        result = BuildResult(
            success=True,
            metadata={},
            errors=[],
            warnings=[],
            dependencies=[],
            file_info={}
        )
        
        all_dependencies = set()
        
        for file_path, content in files.items():
            try:
                print(f"🔍 Analyzing {file_path}...")
                
                # File extension check
                ext = os.path.splitext(file_path)[1]
                if ext not in self.supported_extensions:
                    result.warnings.append(f"Unsupported file type: {file_path}")
                    continue
                
                file_metadata = {}
                file_errors = []
                
                # Python-specific analysis
                if ext == '.py':
                    syntax_errors = self.check_python_syntax(content)
                    if syntax_errors:
                        file_errors.extend(syntax_errors)
                        result.success = False
                    else:
                        file_metadata = self.analyze_python_file(file_path, content)
                
                # Extract dependencies
                deps = self.extract_dependencies(file_path, content)
                all_dependencies.update(deps)
                
                # Store file info
                result.file_info[file_path] = {
                    "size": len(content),
                    "lines": len(content.splitlines()),
                    "extension": ext,
                    "metadata": file_metadata,
                    "errors": file_errors,
                    "dependencies": deps
                }
                
                result.errors.extend(file_errors)
                
            except Exception as e:
                error_msg = f"Error analyzing {file_path}: {str(e)}"
                result.errors.append(error_msg)
                result.success = False
        
        result.dependencies = list(all_dependencies)
        
        # Overall project metadata
        result.metadata = {
            "total_files": len(files),
            "supported_files": len([f for f in files.keys() if os.path.splitext(f)[1] in self.supported_extensions]),
            "total_lines": sum(info.get("lines", 0) for info in result.file_info.values()),
            "total_functions": sum(len(info.get("metadata", {}).get("functions", [])) for info in result.file_info.values()),
            "total_classes": sum(len(info.get("metadata", {}).get("classes", [])) for info in result.file_info.values()),
            "unique_dependencies": len(result.dependencies),
            "has_errors": len(result.errors) > 0
        }
        
        return result
    
    def prepare_context_for_agents(self, build_result: BuildResult) -> Dict[str, Any]:
        """
        Prepare build context for other agents (Analyze, Fix, Test)
        """
        context = {
            "build_status": "success" if build_result.success else "failed",
            "metadata": build_result.metadata,
            "file_info": build_result.file_info,
            "dependencies": build_result.dependencies,
            "errors": build_result.errors,
            "warnings": build_result.warnings,
            "agent": "build"
        }
        
        return context

# Global build agent instance
build_agent = BuildAgent()

def get_build_agent() -> BuildAgent:
    """Get the global build agent instance"""
    return build_agent
