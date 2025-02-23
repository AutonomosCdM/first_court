"""
Slack Integration Setup Script for AgentCourt

This script helps configure and validate the Slack integration for the AgentCourt system.
"""

import os
import sys
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def validate_slack_credentials():
    """
    Validate Slack credentials from environment variables.
    """
    required_env_vars = [
        'SLACK_BOT_TOKEN', 
        'SLACK_SIGNING_SECRET', 
        'SLACK_VERIFICATION_TOKEN'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    return True

def test_slack_connection():
    """
    Test connection to Slack and basic API functionality.
    """
    REQUIRED_SCOPES = {
        'chat:write': lambda client, channel: client.chat_postMessage(
            channel=channel, 
            text="🤖 AgentCourt Slack Integration Test"
        ),
        'app_mentions:read': lambda client, channel: None,  # Requires event subscription
        'im:read': lambda client, channel: client.conversations_list(types="im", limit=1),
        'im:history': lambda client, channel: client.conversations_history(channel=channel, limit=1),
        'groups:read': lambda client, channel: client.conversations_list(types="private_channel", limit=1),
        'mpim:write': lambda client, channel: client.conversations_open(users=['U08DM5AGKQR']),
        'mpim:write.topic': lambda client, channel: None  # No direct test available
    }
    
    try:
        client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
        
        # Test authentication
        auth_test = client.auth_test()
        print(f"✅ Slack Authentication Successful")
        print(f"   Bot User ID: {auth_test['user_id']}")
        print(f"   Team Name: {auth_test['team']}")
        
        # Attempt to perform actions that require specific scopes
        try:
            # Get a test channel
            test_channel = client.conversations_list(limit=1)['channels'][0]['id']
            
            # Check each required scope
            missing_scopes = []
            for scope, test_func in REQUIRED_SCOPES.items():
                try:
                    test_func(client, test_channel)
                    print(f"✅ Scope '{scope}' verified")
                except SlackApiError as e:
                    print(f"❌ Scope '{scope}' failed: {e.response['error']}")
                    missing_scopes.append((scope, e.response['error']))
            
            # If any scopes are missing, return False
            if missing_scopes:
                print("\n❌ Missing or Insufficient Scopes:")
                for scope, error in missing_scopes:
                    print(f"   - {scope}: {error}")
                return False
            
            # List channels
            channels_response = client.conversations_list(limit=10)
            print("\n📋 Available Channels:")
            for channel in channels_response['channels'][:5]:
                print(f"   - #{channel['name']} (ID: {channel['id']})")
            
            return True
        
        except SlackApiError as scope_error:
            print(f"\n❌ Scope Verification Failed: {scope_error.response['error']}")
            return False
    
    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def configure_slack_app():
    """
    Guide user through Slack app configuration steps.
    """
    print("\n🤖 AgentCourt Slack App Configuration Guide")
    print("-------------------------------------------")
    print("1. Go to https://api.slack.com/apps")
    print("2. Click 'Create New App'")
    print("3. Choose 'From scratch'")
    print("4. Name your app 'AgentCourt'")
    print("5. Select your workspace")
    print("\nRequired App Configurations:")
    print("-------------------------------------------")
    print("A. Bot Token Scopes (OAuth & Permissions):")
    print("   - chat:write")
    print("   - channels:read")
    print("   - groups:read")
    print("   - im:read")
    print("   - mpim:read")
    
    print("\nB. Event Subscriptions:")
    print("   - Enable Events")
    print("   - Subscribe to bot events:")
    print("     * message.channels")
    print("     * message.groups")
    print("     * message.im")
    print("     * message.mpim")

def main():
    """
    Main script execution.
    """
    # Load environment variables
    load_dotenv()
    
    print("🚀 AgentCourt Slack Integration Setup")
    print("=====================================")
    
    # Validate credentials
    if not validate_slack_credentials():
        print("\n❌ Please set the required environment variables in .env file.")
        sys.exit(1)
    
    # Test Slack connection
    if test_slack_connection():
        print("\n✅ Slack Connection Successful!")
    else:
        print("\n❌ Slack Connection Failed. Please check your credentials.")
        sys.exit(1)
    
    # Configuration guide
    configure_slack_app()

if __name__ == '__main__':
    main()
