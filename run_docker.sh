#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Video Chat Application with Docker...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create necessary directories
mkdir -p videos

# Function to handle cleanup
cleanup() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Build and start the containers
echo -e "${BLUE}🏗️  Building and starting containers...${NC}"
docker-compose up --build

# The script will keep running until Ctrl+C is pressed
# The cleanup function will be called automatically 