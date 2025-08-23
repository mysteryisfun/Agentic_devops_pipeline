"""
GitHub Connection Test
Tests GitHub API connectivity and permissions
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from src.utils.github_client import GitHubClient

def test_github_connection():
    """Test GitHub API connection and basic operations"""
    
    print("🔍 Testing GitHub Connection...")
    print("=" * 50)
    
    # Load environment variables
    env_path = os.path.join(project_root, '.env')
    print(f"Loading .env from: {env_path}")
    load_dotenv(env_path)
    
    # Debug: Check if token is loaded
    token = os.getenv('GITHUB_TOKEN')
    print(f"Token loaded: {'Yes' if token else 'No'}")
    if token:
        print(f"Token preview: {token[:10]}...")
    
    try:
        # Initialize GitHub client
        print("\n1. Initializing GitHub client...")
        github_client = GitHubClient(token)
        print("✅ GitHub client initialized successfully")
        
        # Test basic connection
        print("\n2. Testing basic GitHub API access...")
        user = github_client.client.get_user()
        print(f"✅ Connected as: {user.login}")
        print(f"   Profile: {user.name or 'No name set'}")
        print(f"   Email: {user.email or 'Private'}")
        
        # Test repository access
        print("\n3. Testing repository access...")
        repo_name = "mysteryisfun/Agentic_devops_pipeline"
        repo = github_client.get_repository(repo_name)
        
        if repo:
            print(f"✅ Repository access successful: {repo.full_name}")
            print(f"   Description: {repo.description or 'No description'}")
            print(f"   Private: {repo.private}")
            print(f"   Default branch: {repo.default_branch}")
            
            # Test file access
            print("\n4. Testing file content access...")
            try:
                readme_content = github_client.get_file_content(repo_name, "README.md")
                if readme_content:
                    print(f"✅ File access successful (README.md: {len(readme_content)} chars)")
                else:
                    print("⚠️  README.md not found, trying other files...")
                    
                    # Try to get any file from the repo
                    contents = repo.get_contents("")
                    if contents:
                        test_file = contents[0].name
                        test_content = github_client.get_file_content(repo_name, test_file)
                        print(f"✅ File access successful ({test_file}: {len(test_content) if test_content else 0} chars)")
                    
            except Exception as e:
                print(f"⚠️  File access test failed: {str(e)}")
            
            # Test permissions
            print("\n5. Testing repository permissions...")
            permissions = repo.permissions
            print(f"   Admin: {permissions.admin}")
            print(f"   Push: {permissions.push}")
            print(f"   Pull: {permissions.pull}")
            
            if permissions.push:
                print("✅ Push permissions available - can commit changes")
            else:
                print("⚠️  No push permissions - cannot commit changes")
                
        else:
            print("❌ Repository access failed")
            return False
            
        print("\n" + "=" * 50)
        print("🎉 GitHub connection test PASSED!")
        print("Ready to proceed with webhook setup and agent development.")
        return True
        
    except Exception as e:
        print(f"\n❌ GitHub connection test FAILED: {str(e)}")
        print("\nPossible issues:")
        print("- Invalid GitHub token")
        print("- Token doesn't have required permissions")
        print("- Network connectivity issues")
        return False

if __name__ == "__main__":
    success = test_github_connection()
    sys.exit(0 if success else 1)
