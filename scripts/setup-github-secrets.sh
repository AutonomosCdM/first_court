#!/bin/bash

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null
then
    echo "GitHub CLI (gh) not found. Please install it first."
    echo "You can install it via:"
    echo "- macOS (Homebrew): brew install gh"
    echo "- Windows: winget install --id GitHub.cli"
    echo "- Linux: See https://github.com/cli/cli#installation"
    exit 1
fi

# Prompt for Firebase credentials
read -p "Enter Firebase Service Account JSON (base64 encoded): " FIREBASE_SERVICE_ACCOUNT
read -p "Enter Firebase Token: " FIREBASE_TOKEN
read -p "Enter Firebase App ID: " FIREBASE_APP_ID

# Validate inputs
if [ -z "$FIREBASE_SERVICE_ACCOUNT" ] || [ -z "$FIREBASE_TOKEN" ] || [ -z "$FIREBASE_APP_ID" ]; then
    echo "Error: All fields are required"
    exit 1
fi

# Set GitHub secrets
echo "Setting up GitHub secrets..."

# Firebase Service Account (base64 encoded JSON)
gh secret set FIREBASE_SERVICE_ACCOUNT_FIRST_COURT \
    --body "$FIREBASE_SERVICE_ACCOUNT" \
    --repo $(git config --get remote.origin.url | sed 's/https:\/\/github.com\///')

# Firebase CLI Token
gh secret set FIREBASE_TOKEN \
    --body "$FIREBASE_TOKEN" \
    --repo $(git config --get remote.origin.url | sed 's/https:\/\/github.com\///')

# Firebase App ID for Distribution
gh secret set FIREBASE_APP_ID \
    --body "$FIREBASE_APP_ID" \
    --repo $(git config --get remote.origin.url | sed 's/https:\/\/github.com\///')

echo "GitHub secrets have been set up successfully!"
echo ""
echo "Next steps:"
echo "1. Verify the secrets in your GitHub repository settings"
echo "2. Ensure your GitHub Actions workflows can access these secrets"
