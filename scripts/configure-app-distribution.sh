#!/bin/bash

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null
then
    echo "Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

# Ensure user is logged in
firebase login

# Prompt for tester group details
read -p "Enter group name (e.g., internal-testers): " GROUP_NAME
read -p "Enter tester emails (comma-separated): " TESTER_EMAILS

# Convert comma-separated emails to array
IFS=',' read -ra EMAILS <<< "$TESTER_EMAILS"

# Add testers to the group
for email in "${EMAILS[@]}"; do
    # Trim whitespace
    email=$(echo "$email" | xargs)
    echo "Adding tester: $email to group: $GROUP_NAME"
    firebase appdistribution:testers:add \
        --emails "$email" \
        --groups "$GROUP_NAME"
done

echo "Tester group '$GROUP_NAME' configured successfully!"
echo "Added testers:"
printf '%s\n' "${EMAILS[@]}"
