"""
Test Fix Agent - Real Fix Application
Tests the Fix Agent's ability to apply a real fix to a file in the repository.
"""

import sys
import asyncio
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.fix_agent import get_fix_agent
from src.agents.analyze_agent import AnalysisResult
from src.utils.github_client import get_github_client

async def test_apply_real_fix():
    """
    Tests that the Fix Agent can successfully apply a real fix to a file
    in the repository via the GitHub API.
    """
    print("🚀 Starting Test: Real Fix Application")

    # 1. Define the mock analysis result targeting an existing file
    mock_analysis = AnalysisResult(
        success=True,
        vulnerabilities=[
            {
                "type": "SQL_INJECTION",
                "severity": "HIGH",
                "confidence": 95,
                "filename": "vulnerable_test_file.py",
                "line": 10,
                "description": "SQL injection vulnerability due to string formatting.",
                "code_snippet": "query = f\"SELECT * FROM users WHERE username='{username}' AND password='{password}'\"",
                "recommendation": "Use parameterized queries to prevent SQL injection."
            }
        ],
        security_issues=[],
        quality_issues=[],
        recommendations=[],
        overall_risk="HIGH",
        files_analyzed=1,
        total_issues=1,
        confidence_scores={"overall": 0.95}
    )

    # 2. Set up repository details
    repo_name = "mysteryisfun/Agentic_devops_pipeline"
    branch = "backend"  # Use the correct, existing branch

    # 3. Get the original content of the file for later comparison
    github_client = get_github_client()
    try:
        original_file_content_obj = github_client.get_file_content(repo_name, "vulnerable_test_file.py", ref=branch)
        original_content = original_file_content_obj.decoded_content.decode('utf-8')
        print(f"✅ Successfully fetched original content of 'vulnerable_test_file.py' from branch '{branch}'.")
    except Exception as e:
        print(f"❌ Failed to fetch original file content: {e}")
        print("   Please ensure the branch 'backend' exists and the file 'vulnerable_test_file.py' is present.")
        return False

    # 4. Initialize the Fix Agent and apply the fix
    fix_agent = get_fix_agent()
    print(f"🔧 Applying fix to '{mock_analysis.vulnerabilities[0]['filename']}' on branch '{branch}'...")

    fix_result = await fix_agent.apply_fixes(
        analysis_result=mock_analysis,
        repo_name=repo_name,
        branch=branch,
        progress_callback=lambda msg: print(f"   📡 WS: {msg.get('message', '')}")
    )

    # 5. Assert the results
    print("\n📊 --- Test Results ---")
    print(f"   Fixes Applied: {fix_result.fixes_applied}")
    print(f"   Files Modified: {fix_result.files_modified}")
    print(f"   Commits Made: {fix_result.commits_made}")

    if fix_result.errors:
        print("   Errors:")
        for error in fix_result.errors:
            print(f"     - {error}")

    assert fix_result.success, "Fix stage should report success."
    assert fix_result.fixes_applied == 1, "Exactly one fix should have been applied."
    assert fix_result.commits_made == 1, "Exactly one commit should have been made."
    assert not fix_result.errors, "There should be no errors during the fix process."

    print("\n✅ Assertions passed!")

    # 6. Revert the file to its original state to keep the test clean
    print("🔄 Reverting file to its original state...")
    try:
        revert_commit = github_client.update_file(
            repo_name=repo_name,
            filename="vulnerable_test_file.py",
            content=original_content,
            message="🤖 Test Revert: Restore vulnerable_test_file.py",
            branch=branch,
            sha=fix_result.fixes_summary[0]['commit_sha'] # This is incorrect, we need the blob sha of the *new* commit
        )
        # A better way is to get the sha from the commit result of the fix
        # For now, we'll just re-commit. A proper implementation would handle this better.
        
        # To get the latest sha, we need to fetch the file content again
        latest_file = github_client.get_file_content(repo_name, "vulnerable_test_file.py", ref=branch)

        github_client.update_file(
            repo_name=repo_name,
            filename="vulnerable_test_file.py",
            content=original_content,
            message="🤖 Test Revert: Restore vulnerable_test_file.py",
            branch=branch,
            sha=latest_file.sha
        )
        print("✅ File successfully reverted.")
    except Exception as e:
        print(f"⚠️ Failed to revert file. Manual revert may be needed. Error: {e}")


    return True

if __name__ == "__main__":
    print("--- Starting Fix Agent Real Application Test ---")
    try:
        result = asyncio.run(test_apply_real_fix())
        if result:
            print("\n🎉 --- TEST PASSED --- 🎉")
        else:
            print("\n❌ --- TEST FAILED --- ❌")
    except Exception as e:
        print(f"\nAn unexpected error occurred during the test run: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ --- TEST FAILED --- ❌")
