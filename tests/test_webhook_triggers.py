"""
Test script to understand what webhook events are triggered when AI makes commits
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils.github_client import get_github_client
from src.config.settings import settings

async def test_webhook_triggers():
    """Test what webhook events are triggered when we make commits"""
    
    print("🔍 Testing webhook triggers from AI commits...")
    
    # Get GitHub client
    github_client = get_github_client()
    
    # Test repository and PR details
    repo_name = "mysteryisfun/Agentic_devops_pipeline"
    
    print(f"📁 Repository: {repo_name}")
    
    # Get repository to check current state
    repo = github_client.get_repository(repo_name)
    if not repo:
        print("❌ Could not access repository")
        return
    
    print(f"✅ Repository accessed successfully")
    print(f"   Default branch: {repo.default_branch}")
    print(f"   Current branch: backend")
    
    # Get recent commits to see their structure
    print("\n📜 Recent commits:")
    commits = repo.get_commits(sha="backend")
    for i, commit in enumerate(commits):
        if i >= 5:  # Only show last 5
            break
        print(f"   {commit.sha[:8]}: {commit.commit.message.split(chr(10))[0]}")
        print(f"      Author: {commit.commit.author.name} <{commit.commit.author.email}>")
        print(f"      Committer: {commit.commit.committer.name} <{commit.commit.committer.email}>")
        
        # Check if it's our AI commit
        if "🤖 AI Fix:" in commit.commit.message:
            print(f"      🤖 THIS IS AN AI COMMIT!")
        print()
    
    # Get recent PRs to see their state
    print("\n🔀 Recent Pull Requests:")
    prs = repo.get_pulls(state="all", sort="updated", direction="desc")
    for i, pr in enumerate(prs):
        if i >= 3:  # Only show last 3
            break
        print(f"   PR #{pr.number}: {pr.title}")
        print(f"      State: {pr.state}")
        print(f"      Base: {pr.base.ref} <- Head: {pr.head.ref}")
        print(f"      Author: {pr.user.login}")
        print(f"      Last updated: {pr.updated_at}")
        
        # Get recent commits in this PR
        print(f"      Recent commits:")
        pr_commits = pr.get_commits()
        for j, commit in enumerate(pr_commits):
            if j >= 3:  # Only show last 3 commits in PR
                break
            print(f"        {commit.sha[:8]}: {commit.commit.message.split(chr(10))[0]}")
            print(f"          Author: {commit.commit.author.name}")
            if "🤖 AI Fix:" in commit.commit.message:
                print(f"          🤖 AI COMMIT DETECTED!")
        print()
    
    print("🔍 Analysis complete!")
    print("\n💡 Key insights:")
    print("   1. Check if AI commits have specific author patterns")
    print("   2. See if commit messages contain our markers")
    print("   3. Understand which webhook events fire for direct commits vs PR updates")

if __name__ == "__main__":
    asyncio.run(test_webhook_triggers())
