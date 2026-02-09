#!/bin/bash

# STL Auto - Start All Services Script

echo "🚀 Starting STL Auto Platform..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if PostgreSQL is running
echo -e "${YELLOW}Checking PostgreSQL...${NC}"
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  PostgreSQL is not running on port 5432${NC}"
    echo "Please start PostgreSQL first:"
    echo "  brew services start postgresql@14"
    echo ""
    echo "Or update the DATABASE_URL in backend/.env"
    echo ""
fi

# Start Backend
echo -e "${BLUE}Starting Backend (Port 8000)...${NC}"
cd backend
python3 -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start Frontend
# echo -e "${BLUE}Starting Frontend (Port 3000)...${NC}"
# cd frontend
# npm run dev &
# FRONTEND_PID=$!
# cd ..

# Wait a bit
# sleep 2

# Start Admin
echo -e "${BLUE}Starting Admin Panel (Port 3001)...${NC}"
cd admin
npm run dev -- --port 3001 &
ADMIN_PID=$!
cd ..

echo ""
echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo "📍 Services:"
echo "  - Backend API:    http://localhost:8000"
echo "  - API Docs:       http://localhost:8000/docs"
echo "  - Frontend:       http://localhost:3000"
echo "  - Admin Panel:    http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping all services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    kill $ADMIN_PID 2>/dev/null
    echo -e "${GREEN}All services stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for all processes
wait
