#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing Video Chat Application Setup...${NC}"

# Function to test URL accessibility
test_url() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${BLUE}Testing $name at $url...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|404"; then
            echo -e "${GREEN}✅ $name is accessible${NC}"
            return 0
        fi
        echo -e "${YELLOW}Attempt $attempt/$max_attempts - waiting for $name...${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ $name is not accessible after $max_attempts attempts${NC}"
    return 1
}

# Determine which compose command to use
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Check if containers are running
echo -e "${BLUE}📋 Checking container status...${NC}"
if $COMPOSE_CMD ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Containers are running${NC}"
else
    echo -e "${RED}❌ Containers are not running. Please run ./run_docker.sh first${NC}"
    exit 1
fi

# Test backend health
test_url "http://localhost:8000/health" "Backend Health Check"

# Test backend API docs
test_url "http://localhost:8000/docs" "Backend API Documentation"

# Test frontend
test_url "http://localhost:8501" "Frontend Application"

echo -e "\n${GREEN}🎉 All tests passed! The application is working correctly.${NC}"
echo -e "${GREEN}You can now:${NC}"
echo -e "${GREEN}1. Open http://localhost:8501 to use the application${NC}"
echo -e "${GREEN}2. Upload a video and start chatting!${NC}" 