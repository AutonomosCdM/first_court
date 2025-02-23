# Slack App Configuration for AgentCourt

## Bot User Token

- Token: `xoxb-8435959058327-8489545509665-hNBhJl5vWvnuGc4KxgWkOgUP`

## Requested Bot Token Scopes

### Communication Scopes

- `chat:write`: Send messages as @secretary
- `app_mentions:read`: View messages that directly mention @secretary
- `im:read`: View basic information about direct messages
- `im:history`: View messages in direct messages
- `groups:read`: View basic information about private channels
- `mpim:write`: Start group direct messages
- `mpim:write.topic`: Set description in group direct messages

## Recommended Security Practices

1. Rotate bot token periodically
2. Limit scopes to minimum required functionality
3. Use environment variables for token management
4. Implement token revocation procedures

## Integration Approach

- Primary communication channel: Secretary agent
- Logging and monitoring through dedicated Slack channels

## Slack App Configuration Steps

1. Create a new Slack App at <https://api.slack.com/apps>
2. Configure Bot Token Scopes
3. Install App to Workspace
4. Copy Bot User OAuth Token
5. Set up Event Subscriptions (optional)

## Troubleshooting

- Verify bot is added to required channels
- Check token permissions
- Ensure network connectivity
- Monitor Slack API rate limits
