#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Video Chat Application with Docker...${NC}"

# Function to check if Docker daemon is running
check_docker_daemon() {
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon is not running. Please start Docker Desktop first.${NC}"
        exit 1
    fi
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed.${NC}"
    echo -e "${YELLOW}Please install Docker from: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# Check if Docker Compose is available (either as plugin or standalone)
if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available.${NC}"
    echo -e "${YELLOW}Please install Docker Compose or update Docker to include the compose plugin.${NC}"
    exit 1
fi

# Determine which compose command to use
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo -e "${GREEN}✅ Using: $COMPOSE_CMD${NC}"

# Check if Docker daemon is running
check_docker_daemon

# Create necessary directories
echo -e "${BLUE}📁 Creating necessary directories...${NC}"
mkdir -p videos

# Stop any existing containers
echo -e "${BLUE}🛑 Stopping any existing containers...${NC}"
$COMPOSE_CMD down 2>/dev/null || true

# Function to handle cleanup
cleanup() {
    echo -e "\n${BLUE}🧹 Cleaning up...${NC}"
    $COMPOSE_CMD down
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Build and start the containers
echo -e "${BLUE}🏗️  Building and starting containers...${NC}"
echo -e "${YELLOW}This may take a few minutes on first run...${NC}"

if $COMPOSE_CMD up --build; then
    echo -e "${GREEN}✅ Application started successfully!${NC}"
else
    echo -e "${RED}❌ Failed to start the application. Check the logs above for errors.${NC}"
    exit 1
fi

# Show access information
echo -e "\n${GREEN}🎉 Video Chat Application is running!${NC}"
echo -e "${GREEN}📱 Frontend: http://localhost:8501${NC}"
echo -e "${GREEN}🔧 Backend API: http://localhost:8000${NC}"
echo -e "${GREEN}📚 API Documentation: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the application${NC}"

# Keep the script running
wait 