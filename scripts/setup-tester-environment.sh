#!/bin/bash

# Ensure the script is run interactively
if [[ ! -t 0 ]]; then
    echo "This script must be run interactively. Please run with: npm run testers:setup"
    exit 1
fi

# Function to check CLI installations
check_and_install_cli() {
    # GitHub CLI
    if ! command -v gh &> /dev/null; then
        echo "GitHub CLI not found. Installing..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install gh
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt install gh
        else
            echo "Unsupported OS. Please install GitHub CLI manually."
            exit 1
        fi
    fi

    # Firebase CLI
    if ! command -v firebase &> /dev/null; then
        echo "Firebase CLI not found. Installing..."
        npm install -g firebase-tools
    fi
}

# Function to authenticate
authenticate() {
    echo "Authenticating with GitHub..."
    gh auth login

    echo "Authenticating with Firebase..."
    firebase login --reauth
}

# Function to get project details
get_project_details() {
    read -p "Enter Firebase Project ID: " FIREBASE_PROJECT_ID
    read -p "Enter Firebase App ID: " FIREBASE_APP_ID
    read -p "Enter tester group name (e.g., internal-testers): " TESTER_GROUP

    # Validate inputs
    if [[ -z "$FIREBASE_PROJECT_ID" || -z "$FIREBASE_APP_ID" || -z "$TESTER_GROUP" ]]; then
        echo "Error: All fields are required"
        exit 1
    fi

    export FIREBASE_PROJECT_ID
    export FIREBASE_APP_ID
    export TESTER_GROUP
}

# Function to set up GitHub secrets
setup_github_secrets() {
    # Generate Firebase service account
    echo "Generating Firebase service account..."
    firebase apps:sdkconfig WEB "$FIREBASE_APP_ID" > firebase-service-account.json

    # Base64 encode the service account for GitHub secrets
    BASE64_SERVICE_ACCOUNT=$(base64 firebase-service-account.json)

    # Get current repository
    REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

    # Set GitHub secrets
    echo "Setting up GitHub secrets for $REPO..."

    # Firebase Service Account
    gh secret set FIREBASE_SERVICE_ACCOUNT_FIRST_COURT \
        --body "$BASE64_SERVICE_ACCOUNT" \
        --repo "$REPO"

    # Firebase Token (generate a new token)
    FIREBASE_TOKEN=$(firebase login:ci)
    gh secret set FIREBASE_TOKEN \
        --body "$FIREBASE_TOKEN" \
        --repo "$REPO"

    # Firebase App ID
    gh secret set FIREBASE_APP_ID \
        --body "$FIREBASE_APP_ID" \
        --repo "$REPO"

    # Clean up service account file
    rm firebase-service-account.json
}

# Function to configure Firebase App Distribution
configure_app_distribution() {
    # Verify Firebase authentication
    echo "Verifying Firebase authentication..."
    firebase projects:list > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Firebase authentication failed. Please log in again."
        firebase login --reauth
    fi

    # Set the active project
    firebase use "$FIREBASE_PROJECT_ID"

    # Create tester group with explicit error handling
    echo "Configuring Firebase App Distribution..."
    firebase appdistribution:groups:create "$TESTER_GROUP" || true

    # Prompt for tester emails
    read -p "Enter tester emails (comma-separated): " TESTER_EMAILS
    IFS=',' read -ra EMAILS <<< "$TESTER_EMAILS"

    for email in "${EMAILS[@]}"; do
        # Trim whitespace
        email=$(echo "$email" | xargs)
        echo "Adding tester: $email"
        firebase appdistribution:testers:add \
            --emails "$email" \
            --groups "$TESTER_GROUP" || echo "Failed to add tester: $email"
    done
}

# Error handling function
handle_error() {
    echo "An error occurred during the setup process."
    echo "Please check your internet connection and credentials."
    exit 1
}

# Main script execution
main() {
    # Trap errors
    trap handle_error ERR

    echo "First Court - Tester Environment Setup"
    echo "====================================="

    # Check and install CLIs
    check_and_install_cli

    # Authenticate
    authenticate

    # Get project details
    get_project_details

    # Set up GitHub secrets
    setup_github_secrets

    # Configure App Distribution
    configure_app_distribution

    echo "Tester environment setup complete!"
    echo "Tester Group: $TESTER_GROUP"
    echo "Testers added: ${EMAILS[*]}"
}

# Run the main script
main
