#!/bin/bash

# Ensure Firebase CLI is installed
if ! command -v firebase &> /dev/null
then
    echo "Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

# Login to Firebase (if not already logged in)
firebase login

# Initialize Firebase project
firebase init hosting firestore

# Set up Firebase App Distribution
echo "Configuring Firebase App Distribution..."
firebase appdistribution:distribute \
    --app $FIREBASE_APP_ID \
    --groups "internal-testers" \
    --release-notes "Automated preview build" \
    dist/index.html

# Print success message
echo "Firebase project initialization complete!"
