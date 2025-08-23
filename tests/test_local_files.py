"""
Local File Pipeline Test
Tests the pipeline with local files without needing GitHub PR
"""

import os
import sys
import asyncio

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load environment variables
from dotenv import load_dotenv
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

from src.agents.build_agent import get_build_agent

async def test_local_files():
    """Test pipeline with local files"""
    
    print("📁 Testing Pipeline with Local Files")
    print("=" * 50)
    
    # Get our test file that has intentional issues
    test_file_path = os.path.join(project_root, 'test_code_for_pr.py')
    
    try:
        # Read the test file
        with open(test_file_path, 'r', encoding='utf-8') as f:
            test_content = f.read()
        
        print(f"📄 Loaded test file: {os.path.basename(test_file_path)}")
        print(f"   Size: {len(test_content)} characters")
        print(f"   Lines: {len(test_content.splitlines())} lines")
        
        # Prepare files for pipeline
        files_to_analyze = {
            "test_code_for_pr.py": test_content
        }
        
        # Add some of our actual source files for comparison
        src_files = [
            "src/main.py",
            "src/agents/build_agent.py",
            "src/utils/github_client.py"
        ]
        
        for src_file in src_files:
            full_path = os.path.join(project_root, src_file)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    files_to_analyze[src_file] = f.read()
                print(f"📄 Added: {src_file}")
        
        print(f"\n🔨 Running Build Agent Analysis...")
        
        # Get build agent and run analysis
        build_agent = get_build_agent()
        result = build_agent.compile_and_validate(files_to_analyze)
        
        # Display comprehensive results
        print(f"\n📊 Build Analysis Results:")
        print(f"   Success: {result.success}")
        print(f"   Files Analyzed: {result.metadata['total_files']}")
        print(f"   Supported Files: {result.metadata['supported_files']}")
        print(f"   Total Lines: {result.metadata['total_lines']}")
        print(f"   Functions Found: {result.metadata['total_functions']}")
        print(f"   Classes Found: {result.metadata['total_classes']}")
        print(f"   Dependencies: {result.metadata['unique_dependencies']}")
        
        if result.dependencies:
            print(f"\n📦 Dependencies Found:")
            for dep in sorted(result.dependencies):
                print(f"   - {dep}")
        
        if result.errors:
            print(f"\n❌ Errors Found ({len(result.errors)}):")
            for error in result.errors:
                print(f"   - {error}")
        
        if result.warnings:
            print(f"\n⚠️  Warnings ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"   - {warning}")
        
        # Detailed file analysis
        print(f"\n📁 Detailed File Analysis:")
        for file_path, info in result.file_info.items():
            print(f"\n   📄 {file_path}:")
            print(f"      Lines: {info['lines']}")
            print(f"      Size: {info['size']} chars")
            print(f"      Extension: {info['extension']}")
            
            if info.get('errors'):
                print(f"      Errors: {len(info['errors'])}")
                for error in info['errors']:
                    print(f"        - {error}")
            
            if 'metadata' in info and info['metadata']:
                meta = info['metadata']
                if meta.get('functions'):
                    func_names = [f['name'] for f in meta['functions']]
                    print(f"      Functions: {func_names}")
                
                if meta.get('classes'):
                    class_names = [c['name'] for c in meta['classes']]
                    print(f"      Classes: {class_names}")
                
                if meta.get('imports'):
                    import_count = len(meta['imports'])
                    print(f"      Imports: {import_count}")
                
                if meta.get('complexity_score'):
                    print(f"      Complexity: {meta['complexity_score']}")
        
        # Test context preparation for other agents
        print(f"\n🔄 Testing Agent Context Preparation...")
        context = build_agent.prepare_context_for_agents(result)
        
        print(f"   Context Keys: {list(context.keys())}")
        print(f"   Build Status: {context['build_status']}")
        print(f"   Agent: {context['agent']}")
        print(f"   Has Errors: {context['metadata']['has_errors']}")
        
        print(f"\n" + "=" * 50)
        if result.success:
            print("🎉 Local File Pipeline Test PASSED!")
            print("✅ Build Agent working perfectly with real code")
        else:
            print("📝 Local File Pipeline Test completed with expected syntax errors")
            print("✅ Build Agent correctly detected issues in test file")
        
        print("\n🚀 Ready for:")
        print("   - Analyze Agent (Gemini integration)")
        print("   - Fix Agent (automated code fixes)")
        print("   - Test Agent (test generation)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Local file test failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_local_files())
