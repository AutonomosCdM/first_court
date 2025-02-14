#!/bin/bash

# Setup script for Open Canvas integration

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Setting up Open Canvas...${NC}"

# 1. Update submodule
echo "Updating Open Canvas submodule..."
git submodule update --init --recursive vendor/open-canvas

# 2. Install dependencies
echo "Installing dependencies..."
cd vendor/open-canvas
yarn install

# 3. Build Open Canvas
echo "Building Open Canvas..."
yarn build

# 4. Link custom extensions
echo "Linking custom extensions..."
cd ../../
ln -sf $(pwd)/custom/agents vendor/open-canvas/apps/agents/src/custom
ln -sf $(pwd)/custom/integrations vendor/open-canvas/apps/agents/src/integrations
ln -sf $(pwd)/custom/extensions vendor/open-canvas/apps/agents/src/extensions

# 5. Setup environment
echo "Setting up environment..."
cp vendor/open-canvas/apps/agents/.env.example vendor/open-canvas/apps/agents/.env
cp vendor/open-canvas/apps/web/.env.example vendor/open-canvas/apps/web/.env

# 6. Configure API keys
echo "Configuring API keys..."
if [ -f ".env" ]; then
    source .env
    sed -i '' "s/DEEPSEEK_API_KEY=.*/DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY/" vendor/open-canvas/apps/agents/.env
    sed -i '' "s/LANGSMITH_API_KEY=.*/LANGSMITH_API_KEY=$LANGSMITH_API_KEY/" vendor/open-canvas/apps/agents/.env
fi

echo -e "${GREEN}Open Canvas setup complete!${NC}"
echo "You can now start the development server with: cd vendor/open-canvas && yarn dev"
