#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# GitHub CLI must be installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI is not installed. Please install it first."
    exit 1
fi

echo -e "${BLUE}Setting up GitHub Secrets...${NC}"

# LangSmith
gh secret set LANGCHAIN_API_KEY --body "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"
gh secret set LANGCHAIN_PROJECT --body "first_court_judicial"

# DeepSeek
gh secret set DEEPSEEK_LEGAL_API_KEY --body "sk-210d87e76faf4d89b34c8821f5b8de96"
gh secret set DEEPSEEK_DOCS_API_KEY --body "sk-9f73e9f5a5ba43fdb505deefd94315df"
gh secret set DEEPSEEK_ADMIN_API_KEY --body "sk-6f8c1e1c703a4aeaad8c0235068d9522"

# Supabase
gh secret set SUPABASE_URL --body "https://kosorbiqjnkvlhgfazdr.supabase.co"
gh secret set SUPABASE_ANON_KEY --body "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtvc29yYmlxam5rdmxoZ2ZhemRyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk1NjQyOTUsImV4cCI6MjA1NTE0MDI5NX0.PVCtrkSofTgsFg0E0tN0wx_kNlIQqmYdaoRgT1mFMq0"

echo -e "${GREEN}Secrets configured successfully!${NC}"
echo -e "Next steps:"
echo -e "1. Update .gitignore to ensure no .env files are committed"
echo -e "2. Remove any existing .env files from git history"
echo -e "3. Push the GitHub Actions workflow"
