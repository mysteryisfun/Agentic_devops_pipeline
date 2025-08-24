"""
Build Agent - Code Compilation and Metadata Extraction
Part of the Hackademia AI Pipeline Multi-Agent System
"""

import ast
import os
import sys
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import asyncio
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
    build_logs: List[str] = field(default_factory=list)
    temp_dir: Optional[str] = None

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
        # Build command candidates per project type (ordered by preference)
        self.python_build_commands = [
            [sys.executable, '-m', 'build'],  # Requires build package
            [sys.executable, 'setup.py', 'build']
        ]
        self.generic_build_commands = [
            ['make', 'build'],
        ]

    # ------------------------------------------------------------
    # Core new build system methods (async orchestration)
    # ------------------------------------------------------------
    async def build_pr_branch(self, repo_name: str, branch: str, pr_number: int, progress_callback=None) -> BuildResult:
        """Clone the PR branch, detect project type, install deps, build, analyze.

        Args:
            repo_name: owner/repo
            branch: PR head ref
            pr_number: PR number (for logging only)
            progress_callback: async-aware callable accepting dict or str messages
        """
        build_logs: List[str] = []
        errors: List[str] = []
        warnings: List[str] = []
        temp_dir: Optional[str] = None
        file_info: Dict[str, Any] = {}
        metadata: Dict[str, Any] = {}
        dependencies: List[str] = []

        def log(msg: str, type_: str = 'status_update', progress: Optional[int] = None):
            clean = msg.replace('\n', ' ').strip()
            build_logs.append(clean)
            if progress_callback:
                payload: Dict[str, Any] = {"type": type_, "stage": "build", "message": clean}
                if progress is not None:
                    payload["progress"] = progress
                # Fire and forget (support sync/async)
                maybe_coro = progress_callback(payload)
                if asyncio.iscoroutine(maybe_coro):
                    asyncio.create_task(maybe_coro)  # do not await to avoid blocking

        log(f"🔄 Starting build for PR #{pr_number} (branch {branch})", progress=5)

        # 1. Clone repository
        try:
            temp_dir = await self.clone_repository(repo_name, branch)
            log("✅ Repository cloned", progress=20)
        except Exception as e:
            error_detail = str(e).strip() or "unknown git error (check repo name / branch / token permissions)"
            error_msg = f"Repository clone failed: {error_detail}"
            errors.append(error_msg)
            log(f"❌ {error_msg}", progress=100)
            # Provide baseline metadata so downstream code doesn't KeyError
            failure_metadata = {
                "project_type": "unknown",
                "total_files": 0,
                "supported_files": 0,
                "total_functions": 0,
                "total_classes": 0,
                "unique_dependencies": 0
            }
            return BuildResult(False, failure_metadata, errors, warnings, [], {}, build_logs, temp_dir)

        # 2. Detect project type
        project_type = self.detect_project_type(temp_dir)
        metadata['project_type'] = project_type
        log(f"🔍 Detected project type: {project_type}", progress=30)

        # 3. Install dependencies
        try:
            dep_install_success = await self.install_dependencies(temp_dir, project_type, log)
            if dep_install_success:
                log("✅ Dependencies installed", progress=45)
            else:
                warnings.append("Some dependency installation steps failed")
                log("⚠️ Dependency installation issues (continuing)", progress=45)
        except Exception as e:
            warnings.append(f"Dependency installation error: {e}")
            log(f"⚠️ Dependency installation error: {e}", progress=45)

        # 4. Run build commands
        try:
            build_success = await self.run_project_build(temp_dir, project_type, log)
            if build_success:
                log("✅ Build succeeded", progress=70)
            else:
                warnings.append("Build commands failed; proceeding with analysis")
                log("⚠️ Build commands failed; continuing", progress=70)
        except Exception as e:
            warnings.append(f"Build execution error: {e}")
            log(f"⚠️ Build execution error: {e}", progress=70)

        # 5. Analyze files for agent context
        try:
            log("🔍 Analyzing code files...", progress=85)
            processed = await self.process_files(temp_dir)
            file_info = processed['file_info']
            dependencies = processed['dependencies']
            metadata.update({
                "total_files": processed['total_files'],
                "supported_files": processed['supported_files'],
                "total_functions": processed['total_functions'],
                "total_classes": processed['total_classes'],
                "unique_dependencies": len(dependencies)
            })
            log("📊 Analysis complete", progress=95)
        except Exception as e:
            errors.append(f"File analysis failed: {e}")
            log(f"❌ File analysis failed: {e}", progress=95)

        success = len(errors) == 0
        log("🎉 Build completed!" if success else "🚫 Build finished with errors", progress=100)

        return BuildResult(success, metadata, errors, warnings, dependencies, file_info, build_logs, temp_dir)

    async def clone_repository(self, repo_name: str, branch: str) -> str:
        """Clone the given GitHub repo branch into a temp directory and return path.

        Raises detailed exception on failure for diagnostics.
        """
        temp_dir = tempfile.mkdtemp(prefix="build_agent_")
        print(f"🔍 DEBUG: Attempting to clone repo_name='{repo_name}' branch='{branch}'")
        
        # Validate repo name format
        if '/' not in repo_name:
            raise Exception(f"Invalid repo name '{repo_name}' (expected 'owner/repo')")
        
        # Prefer settings for token if available
        try:
            from src.config.settings import settings  # type: ignore
        except ModuleNotFoundError:
            try:
                from config.settings import settings  # type: ignore
            except Exception:
                settings = None  # type: ignore
        
        token = (os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PAT') or (settings.github_token if settings else None))
        print(f"🔑 DEBUG: Token available: {'Yes' if token else 'No'}")
        if token:
            print(f"🔑 DEBUG: Token starts with: {token[:8]}...")
        
        # Use token directly in URL - this method works reliably
        if token:
            auth_url = f"https://{token}@github.com/{repo_name}.git"
            cmd = ["git", "clone", "--depth", "1", "--branch", branch, auth_url, temp_dir]
        else:
            repo_url = f"https://github.com/{repo_name}.git"
            cmd = ["git", "clone", "--depth", "1", "--branch", branch, repo_url, temp_dir]
        
        print(f"⚙️ DEBUG: Git command: git clone --depth 1 --branch {branch} [AUTHENTICATED_URL] {temp_dir}")
        print(f"⚙️ DEBUG: Temp directory: {temp_dir}")
        
        try:
            # Use thread executor for Windows compatibility (asyncio.create_subprocess_exec has issues on Windows)
            import subprocess
            import concurrent.futures
            
            def run_git_clone():
                return subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 min timeout
            
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, run_git_clone)
            
            print(f"🔄 DEBUG: Git process completed with exit code: {result.returncode}")
            
            if result.returncode != 0:
                print(f"❌ DEBUG: Git clone failed with exit code {result.returncode}")
                print(f"❌ DEBUG: stderr: '{result.stderr}'")
                print(f"❌ DEBUG: stdout: '{result.stdout}'")
                
                # Return the actual error instead of generic message
                actual_error = result.stderr or result.stdout or 'no output from git command'
                raise Exception(f"git clone failed (exit {result.returncode}) for {repo_name}@{branch}: {actual_error}")
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Git clone timed out after 5 minutes for {repo_name}@{branch}")
        except Exception as e:
            print(f"❌ DEBUG: Failed to execute git command: {e}")
            import traceback
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to execute git clone command: {e}")
        
        print(f"✅ DEBUG: Repository cloned successfully to {temp_dir}")
        
        # Verify the clone worked by checking if files exist
        try:
            files = os.listdir(temp_dir)
            print(f"✅ DEBUG: Clone verification - files found: {len(files)} files")
            if len(files) == 0:
                raise Exception(f"Repository cloned but directory is empty: {temp_dir}")
        except Exception as e:
            print(f"⚠️ DEBUG: Could not verify clone contents: {e}")
        
        return temp_dir

    def detect_project_type(self, root_dir: str) -> str:
        if os.path.exists(os.path.join(root_dir, 'pyproject.toml')) or os.path.exists(os.path.join(root_dir, 'requirements.txt')):
            return 'python'
        if os.path.exists(os.path.join(root_dir, 'package.json')):
            return 'node'
        return 'generic'

    async def install_dependencies(self, root_dir: str, project_type: str, log) -> bool:
        """Install dependencies; return True if succeeded (best-effort)."""
        success = True
        if project_type == 'python':
            req_file = os.path.join(root_dir, 'requirements.txt')
            if os.path.exists(req_file):
                cmd = [sys.executable, '-m', 'pip', 'install', '-r', req_file]
                ok = await self.run_command(cmd, cwd=root_dir, log=log, label='pip install')
                success = success and ok
        elif project_type == 'node':
            if os.path.exists(os.path.join(root_dir, 'package.json')):
                cmd = ['npm', 'install', '--no-audit', '--no-fund']
                ok = await self.run_command(cmd, cwd=root_dir, log=log, label='npm install')
                success = success and ok
        else:
            # Generic: nothing to install
            pass
        return success

    async def run_project_build(self, root_dir: str, project_type: str, log) -> bool:
        """Attempt project-type-specific build commands; returns True if one succeeds or none needed."""
        if project_type == 'python':
            for cmd in self.python_build_commands:
                if not await self.run_command(cmd, cwd=root_dir, log=log, label='python build', allow_failure=True):
                    continue
                return True
            return False
        if project_type == 'node':
            # Try common build script
            package_json = os.path.join(root_dir, 'package.json')
            if os.path.exists(package_json):
                # Run npm run build if build script exists
                try:
                    import json as _json
                    with open(package_json, 'r', encoding='utf-8') as f:
                        data = _json.load(f)
                    scripts = data.get('scripts', {})
                    if 'build' in scripts:
                        return await self.run_command(['npm', 'run', 'build'], cwd=root_dir, log=log, label='npm build', allow_failure=True)
                except Exception:
                    return False
            return False
        # Generic project
        for cmd in self.generic_build_commands:
            if await self.run_command(cmd, cwd=root_dir, log=log, label='generic build', allow_failure=True):
                return True
        return True  # No build needed

    async def run_command(self, cmd: List[str], cwd: str, log, label: str, allow_failure: bool = False) -> bool:
        """Run a subprocess command asynchronously using thread executor for Windows compatibility."""
        try:
            log(f"⚙️ Running: {' '.join(cmd)}")
            
            import subprocess
            import concurrent.futures
            
            def run_subprocess():
                return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
            
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, run_subprocess)
            
            if result.stdout:
                log(f"📝 {label} stdout: {result.stdout.strip()[:500]}")
            if result.stderr:
                log(f"🛑 {label} stderr: {result.stderr.strip()[:500]}")
            if result.returncode != 0:
                log(f"❌ Command failed with exit {result.returncode}")
                return False if not allow_failure else False
            return True
        except subprocess.TimeoutExpired:
            log(f"❌ Command timed out after 5 minutes")
            return False
        except FileNotFoundError:
            log(f"❌ Command not found: {cmd[0]}")
            return False
        except Exception as e:
            log(f"❌ Command error: {e}")
            return False

    async def process_files(self, root_dir: str) -> Dict[str, Any]:
        """Walk repository, analyze supported files, collect metadata for agents."""
        files_content: Dict[str, str] = {}
        for dirpath, _, filenames in os.walk(root_dir):
            # Skip typical build / dependency dirs
            if any(skip in dirpath for skip in ('node_modules', '.git', '__pycache__', 'dist', 'build')):
                continue
            for fn in filenames:
                ext = os.path.splitext(fn)[1]
                if ext in self.supported_extensions:
                    fpath = os.path.join(dirpath, fn)
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
                            files_content[fpath] = fh.read()
                    except Exception:
                        continue
        build_result = self.compile_and_validate(files_content)
        return {
            "file_info": build_result.file_info,
            "dependencies": build_result.dependencies,
            "total_files": build_result.metadata.get('total_files', 0),
            "supported_files": build_result.metadata.get('supported_files', 0),
            "total_functions": build_result.metadata.get('total_functions', 0),
            "total_classes": build_result.metadata.get('total_classes', 0)
        }
    
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
            file_info={},
            build_logs=[],
            temp_dir=None
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
    
    def prepare_context_for_agents(self, build_result: BuildResult, repo_name: str | None = None, pr_number: int | None = None):
        """Prepare build context for other agents.

        Optionally augments with PR diff data if repo/pr provided and GitHub client available.
        """
        context: Dict[str, Any] = {
            "build_status": "success" if build_result.success else "failed",
            "metadata": build_result.metadata,
            "file_info": build_result.file_info,
            "dependencies": build_result.dependencies,
            "errors": build_result.errors,
            "warnings": build_result.warnings,
            "agent": "build",
            "changed_files": [],  # for downstream agents (analyze/test)
            "total_additions": 0,
            "total_deletions": 0
        }
        # Lazy import to avoid circular
        if repo_name and pr_number is not None:
            try:
                from src.utils.github_client import get_github_client  # type: ignore
            except ModuleNotFoundError:
                try:
                    from utils.github_client import get_github_client  # type: ignore
                except Exception:
                    get_github_client = None  # type: ignore
            try:
                if 'get_github_client' in locals():
                    gh = get_github_client()
                    diff_data = gh.get_pr_diff_content(repo_name, pr_number)
                    # Merge minimal diff view
                    context.update({
                        "changed_files": diff_data.get('changed_files', []),
                        "total_additions": diff_data.get('total_additions', 0),
                        "total_deletions": diff_data.get('total_deletions', 0),
                        "pr_info": diff_data.get('pr_info', {})
                    })
            except Exception as e:
                context.setdefault('warnings', []).append(f"Could not enrich with PR diff: {e}")
        return context

# Global build agent instance
build_agent = BuildAgent()

def get_build_agent() -> BuildAgent:
    """Get the global build agent instance"""
    return build_agent
