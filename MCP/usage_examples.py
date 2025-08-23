#!/usr/bin/env python3
"""
HACKADEMIA MCP Usage Examples
Demonstrates how to use the MCP wrapper in other parts of the project
"""

# Import the wrapper
from hackademia_mcp_client import (
    create_mcp_client, 
    quick_security_scan, 
    quick_code_search, 
    quick_vulnerability_check,
    HackademiaMCPWrapper
)

def example_1_basic_usage():
    """Example 1: Basic usage with convenience functions"""
    print("📝 Example 1: Basic Usage")
    print("-" * 40)
    
    # Quick security scan
    security_results = quick_security_scan()
    print(f"🔍 Security Scan Results: {security_results[:150]}...")
    
    # Quick code search
    code_results = quick_code_search("react components")
    print(f"📱 React Components: {code_results[:150]}...")
    print()

def example_2_advanced_usage():
    """Example 2: Advanced usage with the wrapper class"""
    print("📝 Example 2: Advanced Usage")
    print("-" * 40)
    
    try:
        # Create client
        client = create_mcp_client()
        
        # Get repository structure
        structure = client.get_folder_structure("src")
        print(f"📁 Repository Structure: {client.get_content_from_result(structure)[:150]}...")
        
        # Search for API endpoints
        api_results = client.analyze_api_endpoints(limit=3)
        print(f"🌐 API Endpoints: {client.get_content_from_result(api_results)[:150]}...")
        
        # Search documentation
        docs = client.search_documentation("installation guide")
        print(f"📚 Documentation: {client.get_content_from_result(docs)[:150]}...")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_3_comprehensive_analysis():
    """Example 3: Comprehensive analysis"""
    print("📝 Example 3: Comprehensive Analysis")
    print("-" * 40)
    
    try:
        client = create_mcp_client()
        
        # Perform comprehensive analysis
        analysis = client.comprehensive_analysis()
        
        print("🔍 Analysis Results:")
        for category, result in analysis.items():
            content = client.get_content_from_result(result)
            status = "✅" if "Repository" in content else "⚠️"
            print(f"  {status} {category.replace('_', ' ').title()}: {len(content)} characters")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_4_targeted_searches():
    """Example 4: Targeted searches for specific use cases"""
    print("📝 Example 4: Targeted Searches")
    print("-" * 40)
    
    try:
        client = create_mcp_client()
        
        # Search for different types of code
        searches = [
            ("Authentication Functions", "login logout signin signup authentication"),
            ("Error Handling", "error exception try catch throw"),
            ("Database Queries", "query select insert update delete sql"),
            ("React Hooks", "useState useEffect useContext react hooks"),
            ("API Calls", "fetch axios api request http")
        ]
        
        for search_name, query in searches:
            result = client.search_code(query, limit=2)
            content = client.get_content_from_result(result)
            found = "✅ Found" if "Repository" in content else "❌ Not found"
            print(f"  {found} {search_name}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_5_integration_ready():
    """Example 5: How to integrate with other systems (GitHub Actions, Gemini AI, etc.)"""
    print("📝 Example 5: Integration Ready Functions")
    print("-" * 40)
    
    def analyze_pr_changes(file_changes: list):
        """Simulate analyzing PR changes"""
        try:
            client = create_mcp_client()
            
            print("🔄 Analyzing PR changes...")
            for file_path in file_changes:
                # Search for related code
                result = client.search_code(f"file:{file_path}")
                content = client.get_content_from_result(result)
                print(f"  📄 {file_path}: {'Found' if content else 'Not found'}")
            
            # Check for security issues
            security = client.analyze_security(limit=5)
            vulnerabilities = client.find_vulnerabilities(limit=5)
            
            print(f"  🔒 Security check: {'Issues found' if security.get('content') else 'Clean'}")
            print(f"  🚨 Vulnerability check: {'Issues found' if vulnerabilities.get('content') else 'Clean'}")
            
        except Exception as e:
            print(f"❌ PR Analysis failed: {e}")
    
    # Simulate PR with file changes
    pr_files = ["src/components/SignIn.tsx", "src/pages/Login.tsx"]
    analyze_pr_changes(pr_files)
    print()

def example_6_gemini_ai_integration():
    """Example 6: Prepare data for Gemini AI analysis"""
    print("📝 Example 6: Gemini AI Integration Ready")
    print("-" * 40)
    
    try:
        client = create_mcp_client()
        
        # Gather comprehensive data for AI analysis
        ai_analysis_data = {
            "repository_structure": client.get_folder_structure(),
            "security_functions": client.analyze_security(),
            "vulnerabilities": client.find_vulnerabilities(),
            "api_endpoints": client.analyze_api_endpoints(),
            "database_operations": client.analyze_database_operations()
        }
        
        # Format data for AI consumption
        formatted_data = {}
        for category, data in ai_analysis_data.items():
            content = client.get_content_from_result(data)
            formatted_data[category] = content[:500] + "..." if len(content) > 500 else content
        
        print("🤖 Data prepared for Gemini AI:")
        for category, content in formatted_data.items():
            print(f"  📊 {category.replace('_', ' ').title()}: {len(content)} chars ready")
        
        # This data can now be sent to Gemini AI for analysis
        return formatted_data
        
    except Exception as e:
        print(f"❌ AI Integration preparation failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 HACKADEMIA MCP - Usage Examples")
    print("=" * 60)
    
    # Run all examples
    example_1_basic_usage()
    example_2_advanced_usage()
    example_3_comprehensive_analysis()
    example_4_targeted_searches()
    example_5_integration_ready()
    
    # Prepare data for AI
    ai_data = example_6_gemini_ai_integration()
    
    print("✅ All examples completed!")
    print("\n🎯 Ready for integration with:")
    print("  • GitHub Actions workflows")
    print("  • Gemini AI for vulnerability analysis")
    print("  • LangGraph for multi-agent orchestration")
    print("  • Automated PR analysis and fixes")
