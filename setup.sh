#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Setting up Video Chat Application...${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check and install Homebrew if not present
if ! command_exists brew; then
    echo -e "${YELLOW}🍺 Installing Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Python if not present
if ! command_exists python3; then
    echo -e "${YELLOW}🐍 Installing Python 3...${NC}"
    brew install python@3.9
fi

# Install Docker if not present
if ! command_exists docker; then
    echo -e "${YELLOW}🐳 Installing Docker...${NC}"
    brew install --cask docker
    echo -e "${YELLOW}⚠️  Please open Docker Desktop and complete the installation${NC}"
    echo -e "${YELLOW}   Press Enter when Docker is installed and running...${NC}"
    read
fi

# Install PostgreSQL if not present
if ! command_exists psql; then
    echo -e "${YELLOW}🐘 Installing PostgreSQL...${NC}"
    brew install postgresql@14
    brew services start postgresql@14
fi

# Create and activate virtual environment
echo -e "${BLUE}📦 Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}📥 Upgrading pip...${NC}"
pip install --upgrade pip

# Install system dependencies for OpenCV
echo -e "${BLUE}📦 Installing system dependencies...${NC}"
brew install ffmpeg
brew install opencv

# Install Python requirements
echo -e "${BLUE}📥 Installing Python requirements...${NC}"
pip install -r requirements.txt

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p videos

echo -e "${GREEN}✅ Setup complete!${NC}"
echo -e "${GREEN}You can now run the application using:${NC}"
echo -e "${GREEN}1. For local development: ./run_local.sh${NC}"
echo -e "${GREEN}2. For Docker deployment: ./run_docker.sh${NC}"

# Make scripts executable
chmod +x run_local.sh run_docker.sh 