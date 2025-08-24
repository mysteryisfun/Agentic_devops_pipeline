#!/usr/bin/env python3
"""
Test PR Diff Extraction for Hackademia Pipeline
Tests the enhanced GitHub client to extract only changed code from PRs
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.utils.github_client import get_github_client

def test_pr_diff_extraction():
    """Test extracting diff content from a PR"""
    
    try:
        # Create GitHub client
        github_client = get_github_client()
        print("✅ GitHub client created successfully")
        
        # Test with a sample repository and PR
        repo_name = "mysteryisfun/Agentic_devops_pipeline"  # Using your actual repo
        pr_number = 1  # Replace with an actual PR number if exists
        
        print(f"🔍 Testing diff extraction for {repo_name} PR #{pr_number}")
        
        # Get basic PR files (existing method)
        print("\n1️⃣ Testing basic PR files extraction...")
        basic_files = github_client.get_pr_files(repo_name, pr_number)
        print(f"📂 Found {len(basic_files)} changed files")
        
        for file in basic_files[:2]:  # Show first 2 files
            print(f"   📄 {file['filename']} - {file['status']} (+{file['additions']} -{file['deletions']})")
        
        # Get detailed diff content (new method)
        print("\n2️⃣ Testing detailed diff content extraction...")
        diff_content = github_client.get_pr_diff_content(repo_name, pr_number)
        
        if diff_content:
            print(f"📊 PR Info: {diff_content['pr_info']['title']}")
            print(f"🔄 Base: {diff_content['pr_info']['base_branch']} → Head: {diff_content['pr_info']['head_branch']}")
            print(f"📈 Total changes: +{diff_content['total_additions']} -{diff_content['total_deletions']}")
            
            print("\n📋 Changed files analysis:")
            for file in diff_content['changed_files'][:3]:  # Show first 3 files
                print(f"\n   📄 {file['filename']} ({file['status']})")
                print(f"      📊 Changes: +{file['additions']} -{file['deletions']}")
                print(f"      🔤 Extension: {file['file_extension']}")
                print(f"      🔒 Binary: {file['is_binary']}")
                
                if file['added_lines']:
                    print(f"      ➕ Added lines: {len(file['added_lines'])}")
                    for line in file['added_lines'][:2]:  # Show first 2 added lines
                        print(f"         +{line['line_number']}: {line['content'][:50]}...")
                
                if file['removed_lines']:
                    print(f"      ➖ Removed lines: {len(file['removed_lines'])}")
                    
        else:
            print("❌ No diff content retrieved")
            return False
        
        print("\n✅ Diff extraction test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def create_sample_diff_for_analysis():
    """Create a sample diff structure for AI analysis testing"""
    
    sample_diff = {
        "pr_info": {
            "number": 123,
            "title": "Add user authentication with security fixes",
            "base_branch": "main",
            "head_branch": "feature/auth-security"
        },
        "changed_files": [
            {
                "filename": "auth.py",
                "status": "modified",
                "file_extension": "py",
                "added_lines": [
                    {
                        "line_number": 15,
                        "content": "def login(username, password):",
                        "type": "addition"
                    },
                    {
                        "line_number": 16,
                        "content": "    query = f\"SELECT * FROM users WHERE username='{username}'\"",
                        "type": "addition"
                    },
                    {
                        "line_number": 17,
                        "content": "    return execute_query(query)",
                        "type": "addition"
                    }
                ],
                "removed_lines": [],
                "context_lines": [
                    {
                        "line_number": 14,
                        "content": "import sqlite3",
                        "type": "context"
                    }
                ]
            }
        ]
    }
    
    print("📋 Sample diff structure for AI analysis:")
    print(json.dumps(sample_diff, indent=2))
    return sample_diff

if __name__ == "__main__":
    print("🚀 PR DIFF EXTRACTION TEST")
    print("=" * 50)
    
    # Test 1: Actual PR diff extraction (if repo exists)
    print("\n1️⃣ Testing actual PR diff extraction...")
    try:
        success = test_pr_diff_extraction()
        if not success:
            print("⚠️ Actual PR test failed, using sample data...")
    except Exception as e:
        print(f"⚠️ Actual PR test not possible: {str(e)}")
        print("💡 Using sample data for demonstration...")
    
    # Test 2: Sample diff structure
    print("\n2️⃣ Creating sample diff structure...")
    sample_diff = create_sample_diff_for_analysis()
    
    print("\n🎯 Key points for AI analysis:")
    print("   🔍 Focus on 'added_lines' for new vulnerability detection")
    print("   🔄 Use 'context_lines' for understanding code context")
    print("   📂 Filter by 'file_extension' for language-specific analysis")
    print("   ⚠️ Ignore 'is_binary' files for code analysis")
    
    print("\n✅ Ready for Step 3: MCP Integration!")
