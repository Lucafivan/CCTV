#!/bin/bash

# Safety Monitoring System - Startup Script
# This script starts both backend and frontend services

set -e

echo "🚀 Starting Safety Monitoring System..."
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo -e "${YELLOW}📦 Starting Backend...${NC}"
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    pip install -r requirements.txt
    touch venv/.installed
fi

# Start backend server
echo -e "${GREEN}✅ Backend starting on http://localhost:8000${NC}"
python app.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend to be ready...${NC}"
sleep 3

# Check if backend is running
if ! ps -p $BACKEND_PID > /dev/null; then
    echo -e "${RED}❌ Backend failed to start. Check logs/backend.log${NC}"
    exit 1
fi

cd ..

# Start Frontend
echo -e "${YELLOW}📦 Starting Frontend...${NC}"
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Start frontend dev server
echo -e "${GREEN}✅ Frontend starting on http://localhost:5173${NC}"
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# Print status
echo ""
echo "========================================"
echo -e "${GREEN}✅ All services started successfully!${NC}"
echo ""
echo "📍 Access points:"
echo "   - Dashboard:  http://localhost:5173"
echo "   - Backend:    http://localhost:8000"
echo "   - API Docs:   http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   - Backend:    logs/backend.log"
echo "   - Frontend:   logs/frontend.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================"

# Keep script running
wait $BACKEND_PID $FRONTEND_PID