"""
Azure DevOps Personal Access Token (PAT) Setup Helper
=====================================================
This script helps you set up your PAT token for Azure DevOps API access.

What is a PAT?
- Personal Access Token - a secure way to authenticate with Azure DevOps APIs
- Alternative to using username/password
- Can be scoped to specific permissions (we only need Test Plans read access)

Usage: python setup_pat.py
"""

import os
import getpass
import subprocess

def create_pat_guide():
    """Show step-by-step guide to create PAT token"""
    print("📋 How to Create Azure DevOps Personal Access Token (PAT)")
    print("=" * 60)
    print()
    print("1. 🌐 Go to Azure DevOps in your browser:")
    print("   https://dev.azure.com/tr-corp-tax")
    print()
    print("2. 👤 Click on your profile picture (top right)")
    print("   Select 'Personal access tokens'")
    print()
    print("3. ➕ Click '+ New Token'")
    print()
    print("4. 📝 Fill in the details:")
    print("   Name: 'Test Case Extraction Script'")
    print("   Organization: tr-corp-tax")
    print("   Expiration: 30 days (or as required)")
    print()
    print("5. 🔐 Set Scopes:")
    print("   Select 'Custom defined'")
    print("   Check: 'Test Plans (read)'")
    print("   (This gives read access to test plans, suites, and test cases)")
    print()
    print("6. ✅ Click 'Create'")
    print()
    print("7. 📋 Copy the token immediately!")
    print("   ⚠️  You won't be able to see it again!")
    print()
    print("=" * 60)

def set_environment_variable():
    """Help user set the PAT token as environment variable"""
    print("\n🔧 Setting Up Environment Variable")
    print("=" * 40)
    
    # Check if already set
    existing_pat = os.environ.get('AZURE_DEVOPS_PAT')
    if existing_pat:
        print(f"✅ AZURE_DEVOPS_PAT already set (length: {len(existing_pat)})")
        choice = input("Do you want to update it? (y/n): ").lower()
        if choice != 'y':
            return True
    
    print("\nPlease paste your PAT token:")
    print("(Note: The token won't be visible as you type - this is normal)")
    pat_token = getpass.getpass("PAT Token: ")
    
    if not pat_token or len(pat_token) < 10:
        print("❌ Invalid token. PAT tokens are usually 52 characters long.")
        return False
    
    # Try to set environment variable for current session
    os.environ['AZURE_DEVOPS_PAT'] = pat_token
    
    print(f"✅ Environment variable set for current session (length: {len(pat_token)})")
    
    # Show how to make it permanent
    print("\n📌 To make this permanent:")
    print("Windows (Command Prompt):")
    print(f"   setx AZURE_DEVOPS_PAT \"{pat_token}\"")
    print()
    print("Windows (PowerShell):")
    print(f"   [Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', '{pat_token}', 'User')")
    print()
    print("⚠️  You'll need to restart your terminal/IDE after setting it permanently")
    
    return True

def test_pat_token():
    """Quick test of the PAT token"""
    print("\n🧪 Testing PAT Token")
    print("=" * 30)
    
    pat_token = os.environ.get('AZURE_DEVOPS_PAT')
    if not pat_token:
        print("❌ AZURE_DEVOPS_PAT not set")
        return False
    
    try:
        import requests
        import base64
        
        # Test basic connection
        credentials = f":{pat_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
        
        url = "https://dev.azure.com/tr-corp-tax/_apis/projects/OnesourceGCR"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            project_data = response.json()
            print(f"✅ PAT token works!")
            print(f"   Connected to project: {project_data.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ PAT token test failed: HTTP {response.status_code}")
            return False
            
    except ImportError:
        print("⚠️  Cannot test PAT token - 'requests' library not installed")
        print("   Run: pip install requests")
        return False
    except Exception as e:
        print(f"❌ PAT token test failed: {e}")
        return False

def main():
    """Main setup process"""
    print("🚀 Azure DevOps PAT Setup Helper")
    print("=" * 40)
    
    # Check if PAT is already configured
    existing_pat = os.environ.get('AZURE_DEVOPS_PAT')
    if existing_pat:
        print(f"✅ PAT token already configured (length: {len(existing_pat)})")
        if test_pat_token():
            print("\n🎉 Setup complete! You can run the extraction script:")
            print("   python extract_test_cases.py")
            return
    
    # Show PAT creation guide
    create_pat_guide()
    
    # Wait for user to create PAT
    input("\nPress Enter after you've created your PAT token...")
    
    # Set up environment variable
    if set_environment_variable():
        # Test the token
        if test_pat_token():
            print("\n🎉 Setup complete! You can now run:")
            print("   python diagnose_api.py    (to test your setup)")
            print("   python extract_test_cases.py    (to extract all test cases)")
        else:
            print("\n❌ Setup incomplete - PAT token test failed")
    else:
        print("\n❌ Setup incomplete - failed to set PAT token")

if __name__ == "__main__":
    main()
