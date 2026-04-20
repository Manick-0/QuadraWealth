#!/bin/bash
# ═══════════════════════════════════════════════════
# QuadraWealth — Single Command Launcher
# Start both FastAPI backend and Streamlit frontend
# ═══════════════════════════════════════════════════

set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ╔═══════════════════════════════════════════╗"
echo "  ║       💎 QuadraWealth Launcher            ║"
echo "  ║   Multi-Mode Asset & Capital Manager      ║"
echo "  ╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${YELLOW}📦 Checking dependencies...${NC}"
pip3 install -q -r "$SCRIPT_DIR/requirements.txt"

echo -e ""
echo -e "${GREEN}🚀 Starting FastAPI backend on port 8000...${NC}"
cd "$SCRIPT_DIR"
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

sleep 3

echo -e "${GREEN}🎨 Starting Streamlit frontend on port 8501...${NC}"
python3 -m streamlit run frontend/app.py --server.port 8501 --server.headless true &
FRONTEND_PID=$!

echo ""
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ QuadraWealth is running!${NC}"
echo ""
echo -e "  📊 Dashboard:  ${CYAN}http://localhost:8501${NC}"
echo -e "  🔌 API Docs:   ${CYAN}http://localhost:8000/docs${NC}"
echo -e "  ❤️  Health:     ${CYAN}http://localhost:8000/health${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"

# Trap Ctrl+C to kill both
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down QuadraWealth...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}👋 Goodbye!${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
