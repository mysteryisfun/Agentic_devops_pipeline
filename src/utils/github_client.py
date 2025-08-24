"""
GitHub API utilities for Hackademia AI Pipeline
"""

from github import Github
from typing import Dict, Any, List, Optional
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    from src.config.settings import settings
except ModuleNotFoundError:
    # Fallback for when running from src directory
    from config.settings import settings

class GitHubClient:
    """GitHub API client for repository operations"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.github_token
        if not self.token:
            raise ValueError("GitHub token is required")
        
        self.client = Github(self.token)
    
    def get_repository(self, repo_name: str):
        """Get repository object"""
        try:
            return self.client.get_repo(repo_name)
        except Exception as e:
            print(f"❌ Error accessing repository {repo_name}: {str(e)}")
            return None
    
    def get_pull_request(self, repo_name: str, pr_number: int):
        """Get pull request details"""
        try:
            repo = self.get_repository(repo_name)
            if repo:
                return repo.get_pull(pr_number)
            return None
        except Exception as e:
            print(f"❌ Error accessing PR #{pr_number}: {str(e)}")
            return None
    
    def get_pr_files(self, repo_name: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get list of files changed in PR with diff content"""
        try:
            pr = self.get_pull_request(repo_name, pr_number)
            if pr:
                files = []
                for file in pr.get_files():
                    files.append({
                        "filename": file.filename,
                        "status": file.status,  # added, modified, removed
                        "additions": file.additions,
                        "deletions": file.deletions,
                        "changes": file.changes,
                        "patch": file.patch,  # This contains the actual diff
                        "raw_url": file.raw_url,
                        "blob_url": file.blob_url
                    })
                return files
            return []
        except Exception as e:
            print(f"❌ Error getting PR files: {str(e)}")
            return []
    
    def get_pr_diff_content(self, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """Get detailed diff content for AI analysis"""
        try:
            pr = self.get_pull_request(repo_name, pr_number)
            if not pr:
                return {}
            
            diff_data = {
                "pr_info": {
                    "number": pr_number,
                    "title": pr.title,
                    "body": pr.body,
                    "base_branch": pr.base.ref,
                    "head_branch": pr.head.ref,
                    "author": pr.user.login
                },
                "changed_files": [],
                "total_additions": 0,
                "total_deletions": 0
            }
            
            for file in pr.get_files():
                file_data = {
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "patch": file.patch,
                    "file_extension": file.filename.split('.')[-1] if '.' in file.filename else '',
                    "is_binary": file.patch is None,
                    "added_lines": [],
                    "removed_lines": [],
                    "context_lines": []
                }
                
                # Parse the patch to extract actual changed lines
                if file.patch:
                    added_lines, removed_lines, context_lines = self._parse_patch(file.patch)
                    file_data.update({
                        "added_lines": added_lines,
                        "removed_lines": removed_lines, 
                        "context_lines": context_lines
                    })
                
                diff_data["changed_files"].append(file_data)
                diff_data["total_additions"] += file.additions
                diff_data["total_deletions"] += file.deletions
            
            return diff_data
            
        except Exception as e:
            print(f"❌ Error getting PR diff content: {str(e)}")
            return {}
    
    def _parse_patch(self, patch: str) -> tuple:
        """Parse patch content to extract added/removed/context lines"""
        added_lines = []
        removed_lines = []
        context_lines = []
        
        if not patch:
            return added_lines, removed_lines, context_lines
        
        lines = patch.split('\n')
        old_line_num = 0
        new_line_num = 0
        
        for line in lines:
            if line.startswith('@@'):
                # Parse line numbers from @@ -start,count +start,count @@
                import re
                match = re.search(r'@@\s*-(\d+)(?:,\d+)?\s*\+(\d+)(?:,\d+)?\s*@@', line)
                if match:
                    old_line_num = int(match.group(1))
                    new_line_num = int(match.group(2))
                continue
            elif line.startswith('+') and not line.startswith('+++'):
                # Added line (only exists in new version)
                added_lines.append({
                    "line_number": new_line_num,
                    "content": line[1:],  # Remove the + prefix
                    "type": "addition"
                })
                new_line_num += 1
            elif line.startswith('-') and not line.startswith('---'):
                # Removed line (only exists in old version)
                removed_lines.append({
                    "line_number": old_line_num,
                    "content": line[1:],  # Remove the - prefix
                    "type": "deletion"
                })
                old_line_num += 1
            else:
                # Context line (unchanged) - exists in both versions
                if line.startswith(' '):
                    content = line[1:]  # Remove space prefix
                else:
                    content = line
                
                context_lines.append({
                    "old_line_number": old_line_num,
                    "new_line_number": new_line_num,
                    "content": content,
                    "type": "context"
                })
                old_line_num += 1
                new_line_num += 1
        
        return added_lines, removed_lines, context_lines
    
    def get_file_content(self, repo_name: str, file_path: str, ref: str = "main"):
        """Get content of a specific file"""
        try:
            repo = self.get_repository(repo_name)
            if repo:
                file_content = repo.get_contents(file_path, ref=ref)
                return file_content
            return None
        except Exception as e:
            print(f"❌ Error getting file content: {str(e)}")
            return None
    
    def update_file(self, repo_name: str, filename: str, content: str, message: str, branch: str, sha: str):
        """Update a file via GitHub API"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return None
                
            result = repo.update_file(
                path=filename,
                message=message,
                content=content,
                sha=sha,
                branch=branch
            )
            
            print(f"✅ Successfully updated {filename} on branch {branch}")
            return {
                "commit": {
                    "sha": result["commit"].sha,
                    "url": result["commit"].html_url
                },
                "content": {
                    "sha": result["content"].sha
                }
            }
            
        except Exception as e:
            print(f"❌ Error updating file {filename}: {str(e)}")
            raise e
    
    def create_comment(self, repo_name: str, pr_number: int, comment: str):
        """Add comment to pull request"""
        try:
            pr = self.get_pull_request(repo_name, pr_number)
            if pr:
                pr.create_issue_comment(comment)
                return True
            return False
        except Exception as e:
            print(f"❌ Error creating comment: {str(e)}")
            return False
    
    def commit_changes(self, repo_name: str, branch: str, files_to_commit: Dict[str, str], commit_message: str):
        """Commit multiple file changes to a branch"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return False
            
            # Get the current commit SHA
            ref = repo.get_git_ref(f"heads/{branch}")
            commit_sha = ref.object.sha
            
            # Create blobs for each file
            blobs = []
            for file_path, content in files_to_commit.items():
                blob = repo.create_git_blob(content, "utf-8")
                blobs.append({
                    "path": file_path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob.sha
                })
            
            # Create tree
            tree = repo.create_git_tree(blobs, base_tree=repo.get_git_commit(commit_sha).tree)
            
            # Create commit
            commit = repo.create_git_commit(commit_message, tree, [repo.get_git_commit(commit_sha)])
            
            # Update reference
            ref.edit(commit.sha)
            
            print(f"✅ Successfully committed changes to {branch}")
            return True
            
        except Exception as e:
            print(f"❌ Error committing changes: {str(e)}")
            return False

# Global GitHub client instance
github_client = None

def get_github_client() -> GitHubClient:
    """Get or create GitHub client instance"""
    global github_client
    if github_client is None:
        github_client = GitHubClient()
    return github_client
