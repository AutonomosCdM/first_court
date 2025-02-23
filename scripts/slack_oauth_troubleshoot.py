"""
Slack OAuth Troubleshooting Script

This script helps diagnose and resolve OAuth configuration issues.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def validate_slack_credentials():
    """
    Validate and diagnose Slack OAuth credentials.
    """
    print("🔍 Slack OAuth Credential Validation")
    print("===================================")

    # Retrieve credentials
    client_id = os.getenv('SLACK_CLIENT_ID')
    client_secret = os.getenv('SLACK_CLIENT_SECRET')
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    
    # Detailed validation
    print("\n1. Credential Presence Check:")
    credentials_valid = True
    
    if not client_id:
        print("   ❌ SLACK_CLIENT_ID is missing")
        credentials_valid = False
    else:
        print(f"   ✅ Client ID: {client_id}")
        print(f"   Length: {len(client_id)} characters")
        
        # Validate client ID format
        if '.' in client_id or not client_id.isalnum():
            print("   ❌ Invalid Client ID format")
            print("   Recommended: Alphanumeric string without special characters")
            credentials_valid = False
    
    if not client_secret:
        print("   ❌ SLACK_CLIENT_SECRET is missing")
        credentials_valid = False
    else:
        print(f"   ✅ Client Secret present (length: {len(client_secret)})")
    
    if not bot_token:
        print("   ❌ SLACK_BOT_TOKEN is missing")
        credentials_valid = False
    else:
        print(f"   ✅ Bot Token present (length: {len(bot_token)})")
    
    if not credentials_valid:
        return False

    # Verify OAuth configuration
    try:
        # Test OAuth token validation
        response = requests.post(
            'https://slack.com/api/auth.test',
            headers={
                'Authorization': f'Bearer {bot_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print("\n2. OAuth Token Validation:")
                print("   ✅ Token is valid")
                print(f"   User: {data.get('user')}")
                print(f"   Team: {data.get('team')}")
                
                # Check token scopes
                scopes_response = requests.post(
                    'https://slack.com/api/apps.permissions.info',
                    headers={
                        'Authorization': f'Bearer {bot_token}',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    timeout=10
                )
                
                if scopes_response.status_code == 200:
                    scopes_data = scopes_response.json()
                    if scopes_data.get('ok'):
                        bot_scopes = scopes_data.get('info', {}).get('bot_scopes', [])
                        print("\n3. Bot Token Scopes:")
                        print("   Configured Scopes:")
                        for scope in bot_scopes:
                            print(f"   - {scope}")
                    else:
                        print("\n3. Bot Token Scopes:")
                        print(f"   ❌ Unable to retrieve scopes: {scopes_data.get('error', 'Unknown error')}")
                else:
                    print("\n3. Bot Token Scopes:")
                    print(f"   ❌ Error retrieving scopes: HTTP {scopes_response.status_code}")
            else:
                print("\n2. OAuth Token Validation:")
                print(f"   ❌ Token Validation Failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print("\n2. OAuth Token Validation:")
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
    
    except requests.RequestException as e:
        print("\n2. OAuth Token Validation:")
        print(f"   ❌ Network Error: {e}")
        return False

    return True

def recommend_fixes():
    """
    Provide recommendations for potential OAuth configuration issues.
    """
    print("\n🛠️ Recommended Fixes:")
    print("-------------------")
    print("1. Verify Slack App Configuration:")
    print("   - Go to https://api.slack.com/apps")
    print("   - Select your app")
    print("   - Check 'App Credentials' section")
    
    print("\n2. Client ID Troubleshooting:")
    print("   - Ensure Client ID is a clean numeric/alphanumeric string")
    print("   - Remove any periods or additional identifiers")
    
    print("\n3. OAuth Flow Checklist:")
    print("   - Confirm Redirect URI is correctly configured")
    print("   - Verify requested scopes")
    print("   - Reinstall app in workspace if needed")

def main():
    print("🚀 Slack OAuth Troubleshooter")
    print("============================")
    
    if validate_slack_credentials():
        print("\n✅ Basic credential validation passed")
    else:
        print("\n❌ Credential validation failed")
    
    recommend_fixes()

if __name__ == '__main__':
    main()
