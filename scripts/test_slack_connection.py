import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def test_slack_connection():
    # Load environment variables
    load_dotenv()

    # Get the Slack Bot Token
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    
    if not slack_token:
        print("❌ Error: SLACK_BOT_TOKEN not found in environment variables")
        return False

    # Initialize the Slack client
    client = WebClient(token=slack_token)

    try:
        # Test authentication
        auth_test = client.auth_test()
        print("✅ Slack Authentication Successful!")
        print(f"   Bot User ID: {auth_test['user_id']}")
        print(f"   Bot Team: {auth_test['team']}")
        print(f"   Bot Name: {auth_test['user']}")
        return True

    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        return False

def send_test_message():
    """
    Send a test message to a Slack channel
    """
    # Load environment variables
    load_dotenv()

    # Get the Slack Bot Token
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    
    if not slack_token:
        print("❌ Error: SLACK_BOT_TOKEN not found in environment variables")
        return False

    # Initialize the Slack client
    client = WebClient(token=slack_token)

    try:
        # Send a test message
        print("\n📝 Sending test message...")
        response = client.chat_postMessage(
            channel="C08DM64374H",  # Channel ID from the URL
            text="🤖 ¡Hola! Soy el agente de comunicación de AgentCourt. Estoy probando mi conexión. 📜⚖️"
        )
        print("✅ Test message sent successfully!")
        print(f"   Channel: {response['channel']}")
        print(f"   Message timestamp: {response['ts']}")
        return True

    except SlackApiError as e:
        print(f"❌ Error sending message: {e.response['error']}")
        if 'missing_scope' in str(e):
            print("   💡 Tip: Make sure the bot has 'chat:write' permission")
        return False

def main():
    print("🔄 Testing Slack Connection...")
    if test_slack_connection():
        print("\n🚀 Connection test successful! Trying to send a message...")
        send_test_message()
    else:
        print("\n❌ Connection test failed. Please check your token and permissions.")

if __name__ == "__main__":
    main()
