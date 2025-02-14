#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Setting up Open Canvas integration...${NC}"

# 1. Clone Open Canvas if not exists
if [ ! -d "open-canvas" ]; then
    echo -e "${BLUE}Cloning Open Canvas...${NC}"
    git clone https://github.com/langchain-ai/open-canvas.git
    cd open-canvas
    yarn install
else
    echo -e "${GREEN}Open Canvas already exists${NC}"
    cd open-canvas
    yarn install
fi

# 2. Copy environment files
echo -e "${BLUE}Setting up environment files...${NC}"
cp apps/web/.env.example apps/web/.env
cp apps/agents/.env.example apps/agents/.env

# 3. Create our custom directories
echo -e "${BLUE}Creating custom directories...${NC}"
cd ..
mkdir -p src/canvas/{adapters,actions}

# 4. Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
yarn add @supabase/supabase-js
yarn add @langchain/core
yarn add @langchain/openai

echo -e "${GREEN}Setup complete!${NC}"
echo -e "Next steps:"
echo -e "1. Configure Supabase in apps/web/.env"
echo -e "2. Configure DeepSeek models in apps/agents/.env"
echo -e "3. Run yarn dev in open-canvas/apps/web"
