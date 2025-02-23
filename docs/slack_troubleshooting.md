# Slack Integration Troubleshooting Guide for AgentCourt

## Common Scope-Related Issues

### Missing Scopes
If you encounter a "missing_scope" error, ensure the following scopes are added:

1. Communication Scopes
- `chat:write`: Send messages
- `app_mentions:read`: Read app mentions
- `im:read`: Access direct message info
- `im:history`: Read direct message history
- `groups:read`: View private channel info
- `mpim:write`: Start group direct messages
- `mpim:write.topic`: Modify group message topics

## Troubleshooting Steps
1. Verify Bot Token Permissions
   - Go to https://api.slack.com/apps
   - Select your AgentCourt app
   - Navigate to "OAuth & Permissions"
   - Check "Bot Token Scopes" section

2. Add Missing Scopes
   - Click "Add an OAuth Scope"
   - Add each missing scope individually
   - Re-install the app to workspace if needed

3. Regenerate Bot Token
   - If persistent issues occur
   - Go to "OAuth & Permissions"
   - Click "Reinstall App" or generate new token

## Debugging Checklist
- Verify .env file contains correct bot token
- Ensure bot is added to required channels
- Check network connectivity
- Validate Slack API credentials

## Common Error Messages
- `missing_scope`: Bot lacks required permissions
- `not_in_channel`: Bot not added to specified channel
- `invalid_token`: Token is expired or incorrect

## Support
For additional help, consult:
- Slack API Documentation
- AgentCourt Slack Integration Support
