"""
Slack OAuth Setup Script for AgentCourt

This script helps set up OAuth 2.0 authentication for the Slack integration.
"""

import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs
from dotenv import load_dotenv
import webbrowser
import requests
import json
import ssl

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv('SLACK_CLIENT_ID')
CLIENT_SECRET = os.getenv('SLACK_CLIENT_SECRET')
PORT = 3000

# Required scopes for the application
REQUIRED_SCOPES = [
    'chat:write',
    'app_mentions:read',
    'im:read',
    'im:history',
    'groups:read',
    'mpim:write',
    'mpim:write.topic',
    'channels:read',
    'users:read'
]

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle the OAuth callback from Slack."""
        if self.path.startswith('/oauth/callback'):
            # Parse the query parameters
            query_components = parse_qs(self.path.split('?')[1])
            
            # Get the temporary code
            code = query_components.get('code', [None])[0]
            
            if code:
                # Exchange the code for an access token
                token_response = self.exchange_code_for_token(code)
                
                if token_response.get('ok'):
                    # Save the tokens to .env file
                    self.save_tokens(token_response)
                    self.send_success_response()
                else:
                    self.send_error_response(token_response.get('error', 'Unknown error'))
            else:
                self.send_error_response('No code received')
        else:
            self.send_response(404)
            self.end_headers()

    def exchange_code_for_token(self, code):
        """Exchange the temporary code for an access token."""
        response = requests.post(
            'https://slack.com/api/oauth.v2.access',
            data={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'code': code,
                'redirect_uri': f'http://localhost:{PORT}/oauth/callback'
            }
        )
        return response.json()

    def save_tokens(self, token_response):
        """Save the tokens to .env file."""
        bot_token = token_response.get('access_token')
        
        # Read existing .env content
        env_content = {}
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        env_content[key] = value

        # Update tokens
        env_content['SLACK_BOT_TOKEN'] = bot_token
        
        # Write back to .env
        with open('.env', 'w') as f:
            for key, value in env_content.items():
                f.write(f'{key}={value}\n')

    def send_success_response(self):
        """Send a success response to the browser."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        success_message = """
        <html>
            <body style="text-align: center; font-family: Arial, sans-serif; margin-top: 50px;">
                <h1 style="color: #2eb67d;">✅ Slack Integration Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
            </body>
        </html>
        """
        self.wfile.write(success_message.encode())

    def send_error_response(self, error):
        """Send an error response to the browser."""
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        error_message = f"""
        <html>
            <body style="text-align: center; font-family: Arial, sans-serif; margin-top: 50px;">
                <h1 style="color: #e01e5a;">❌ Error</h1>
                <p>{error}</p>
                <p>Please check the terminal for more information.</p>
            </body>
        </html>
        """
        self.wfile.write(error_message.encode())

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Error: SLACK_CLIENT_ID and SLACK_CLIENT_SECRET must be set in .env file")
        sys.exit(1)

    # Use a local development redirect URI
    redirect_uri = f'http://localhost:{PORT}/oauth/callback'
    
    # Construct the OAuth URL
    params = {
        'client_id': CLIENT_ID,
        'scope': ','.join(REQUIRED_SCOPES),
        'redirect_uri': redirect_uri
    }
    
    auth_url = f'https://slack.com/oauth/v2/authorize?{urlencode(params)}'
    
    print("🚀 Starting Slack OAuth Setup")
    print("============================")
    print("1. Slack Authorization Required")
    print("\nℹ️  Please follow these steps:")
    print("   a) Open the following URL in your browser:")
    print(f"      {auth_url}")
    print("   b) Authorize the 'secretario' app")
    print("   c) After authorization, you'll be redirected")
    print("\n2. Redirect URI Configuration")
    print(f"   Ensure '{redirect_uri}' is added in Slack App Settings")
    print("   Go to: https://api.slack.com/apps")
    print(f"   Select app 'secretario'")
    print("   Navigate to 'OAuth & Permissions'")
    print("   Add Redirect URL in 'Redirect URLs' section")

    # Open the browser
    webbrowser.open(auth_url)

    # Start the local server to handle the callback
    from http.server import HTTPServer
    server = HTTPServer(('localhost', PORT), OAuthHandler)
    print(f"\n3. Waiting for OAuth callback on port {PORT}...")
    print("   (Press Ctrl+C to cancel)")
    
    try:
        server.handle_request()
        print("\n✅ Setup complete! You can now close this script.")
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
