#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Video Chat Application Locally...${NC}"

# Create necessary directories
mkdir -p videos

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Verify virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

# Set PYTHONPATH
export PYTHONPATH="$PWD:$PYTHONPATH"

# Install requirements
echo -e "${BLUE}📥 Installing requirements...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Verify critical packages are installed
echo -e "${BLUE}🔍 Verifying installations...${NC}"
python3 -c "import cv2; import streamlit; import uvicorn; print('✅ All required packages are installed')" || {
    echo -e "${RED}❌ Some packages are missing. Please run setup.sh first${NC}"
    exit 1
}

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Stop any local PostgreSQL services
echo -e "${BLUE}🛑 Stopping local PostgreSQL services...${NC}"
brew services stop postgresql@14 2>/dev/null || true
brew services stop postgresql 2>/dev/null || true

# Clean up any existing containers
echo -e "${BLUE}🧹 Cleaning up existing containers...${NC}"
docker stop videochat-db 2>/dev/null || true
docker rm videochat-db 2>/dev/null || true

# Start PostgreSQL with pgvector
echo -e "${BLUE}🐘 Starting PostgreSQL with pgvector...${NC}"
docker run -d \
    --name videochat-db \
    -e POSTGRES_DB=videochat \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -p 5432:5432 \
    ankane/pgvector:latest

# Wait for PostgreSQL to be ready
echo -e "${BLUE}⏳ Waiting for PostgreSQL to be ready...${NC}"
sleep 5

# Start the backend using the virtual environment's Python
echo -e "${BLUE}🌐 Starting FastAPI backend...${NC}"
$VIRTUAL_ENV/bin/python start_backend.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
sleep 10

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start. Check the logs above for errors.${NC}"
    docker stop videochat-db
    docker rm videochat-db
    exit 1
fi

# Test backend connectivity
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; then
    echo -e "${GREEN}✅ Backend is running and accessible${NC}"
else
    echo -e "${RED}❌ Backend is not accessible${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    docker stop videochat-db
    docker rm videochat-db
    exit 1
fi

# Start the frontend using the virtual environment's Python
echo -e "${BLUE}🎨 Starting Streamlit frontend...${NC}"
$VIRTUAL_ENV/bin/streamlit run src/frontend/app.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!

echo -e "${GREEN}✅ Application is running!${NC}"
echo -e "${GREEN}🌐 Frontend: http://localhost:8501${NC}"
echo -e "${GREEN}🔧 Backend API: http://localhost:8000${NC}"
echo -e "${GREEN}📚 API Documentation: http://localhost:8000/docs${NC}"

# Function to handle cleanup
cleanup() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    docker stop videochat-db
    docker rm videochat-db
    deactivate
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Keep script running
wait 