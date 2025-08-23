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

from src.config.settings import settings

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
        """Get list of files changed in PR"""
        try:
            pr = self.get_pull_request(repo_name, pr_number)
            if pr:
                files = []
                for file in pr.get_files():
                    files.append({
                        "filename": file.filename,
                        "status": file.status,
                        "additions": file.additions,
                        "deletions": file.deletions,
                        "changes": file.changes,
                        "patch": file.patch,
                        "raw_url": file.raw_url
                    })
                return files
            return []
        except Exception as e:
            print(f"❌ Error getting PR files: {str(e)}")
            return []
    
    def get_file_content(self, repo_name: str, file_path: str, ref: str = "main"):
        """Get content of a specific file"""
        try:
            repo = self.get_repository(repo_name)
            if repo:
                file_content = repo.get_contents(file_path, ref=ref)
                return file_content.decoded_content.decode('utf-8')
            return None
        except Exception as e:
            print(f"❌ Error getting file content: {str(e)}")
            return None
    
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
