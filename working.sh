#!/bin/bash

# ============================================
# Tanlov AI - Barcha xizmatlarni ishga tushirish
# ============================================

set -e

# Ranglar
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Loyiha papkasi
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}       TANLOV AI - Xizmatlar Boshqaruvi     ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Funksiyalar
cleanup() {
    echo -e "\n${YELLOW}Xizmatlarni to'xtatish...${NC}"
    pkill -f "manage.py runserver" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    echo -e "${GREEN}Barcha xizmatlar to'xtatildi${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

start_backend() {
    echo -e "${YELLOW}[1/3] Backend serverini ishga tushirish...${NC}"
    
    # Proxy o'zgaruvchilarni o'chirish (agar bor bo'lsa)
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
    
    # Eski jarayonlarni to'xtatish
    pkill -f "manage.py runserver" 2>/dev/null || true
    sleep 1
    
    # Virtual environment aktivatsiya
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}Virtual environment topilmadi! Yaratish...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    fi
    
    # Migratsiyalarni tekshirish
    python manage.py migrate --check 2>/dev/null || python manage.py migrate
    
    # Backend ishga tushirish
    nohup python manage.py runserver 0.0.0.0:8000 > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Server tayyor bo'lguncha kutish
    echo -e "${YELLOW}  Server yuklanmoqda...${NC}"
    for i in {1..15}; do
        if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend ishlayapti: http://localhost:8000${NC}"
            return 0
        fi
        sleep 1
        echo -ne "${YELLOW}  Kutilmoqda... ${i}s${NC}\r"
    done
    
    # 15 sekunddan keyin ham ishlamasa
    echo -e "${RED}✗ Backend 15 sekund ichida ishga tushmadi${NC}"
    echo -e "${YELLOW}Log:${NC}"
    cat logs/backend.log | tail -10
    echo ""
    echo -e "${YELLOW}Lekin jarayon davom etmoqda, frontendni ishga tushiramiz...${NC}"
}

start_frontend() {
    echo -e "${YELLOW}[2/3] Frontend serverini ishga tushirish...${NC}"
    
    # Eski jarayonlarni to'xtatish
    pkill -f "vite" 2>/dev/null || true
    sleep 1
    
    cd frontend
    
    # Node modules tekshirish
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Node modules o'rnatilmoqda...${NC}"
        npm install
    fi
    
    # Frontend ishga tushirish
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    cd ..
    
    sleep 5
    
    # Port aniqlash
    FRONTEND_PORT=$(grep -oP 'localhost:\K[0-9]+' logs/frontend.log 2>/dev/null | head -1)
    
    if [ -n "$FRONTEND_PORT" ]; then
        echo -e "${GREEN}✓ Frontend ishlayapti: http://localhost:${FRONTEND_PORT}${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend port aniqlanmadi, logni tekshiring${NC}"
    fi
}

check_services() {
    echo -e "${YELLOW}[3/3] Xizmatlarni tekshirish...${NC}"
    echo ""
    
    # Backend
    if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
        HEALTH=$(curl -s http://localhost:8000/api/health/)
        echo -e "${GREEN}✓ Backend API:    http://localhost:8000${NC}"
        echo -e "  Status: $HEALTH"
    else
        echo -e "${RED}✗ Backend API:    Ishlamayapti${NC}"
    fi
    
    # Frontend port topish
    FRONTEND_PORT=$(grep -oP 'localhost:\K[0-9]+' logs/frontend.log 2>/dev/null | head -1)
    if [ -n "$FRONTEND_PORT" ] && curl -s "http://localhost:${FRONTEND_PORT}" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend:       http://localhost:${FRONTEND_PORT}${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend:       Port aniqlanmadi${NC}"
    fi
    
    # OpenAI
    if grep -q "OPENAI_API_KEY" .env 2>/dev/null; then
        echo -e "${GREEN}✓ OpenAI:         Sozlangan (.env)${NC}"
    else
        echo -e "${RED}✗ OpenAI:         .env faylida OPENAI_API_KEY yo'q${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${GREEN}Tayyor! Quyidagi manzillardan foydalaning:${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
    echo -e "  📊 Dashboard:     http://localhost:${FRONTEND_PORT:-5175}"
    echo -e "  🔬 Tahlil:        http://localhost:${FRONTEND_PORT:-5175}/analysis"
    echo -e "  📚 API Docs:      http://localhost:8000/api/docs/"
    echo -e "  ❤️  Health:       http://localhost:8000/api/health/"
    echo ""
    echo -e "${YELLOW}To'xtatish uchun: Ctrl+C${NC}"
    echo ""
}

show_logs() {
    echo -e "${BLUE}Loglarni ko'rish...${NC}"
    tail -f logs/backend.log logs/frontend.log
}

# Logs papkasini yaratish
mkdir -p logs

# Asosiy ishga tushirish
case "${1:-start}" in
    start)
        start_backend
        start_frontend
        check_services
        # Loglarni ko'rsatish
        show_logs
        ;;
    stop)
        cleanup
        ;;
    restart)
        cleanup
        sleep 2
        start_backend
        start_frontend
        check_services
        show_logs
        ;;
    status)
        check_services
        ;;
    backend)
        start_backend
        tail -f logs/backend.log
        ;;
    frontend)
        start_frontend
        tail -f logs/frontend.log
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Foydalanish: $0 {start|stop|restart|status|backend|frontend|logs}"
        echo ""
        echo "  start    - Barcha xizmatlarni ishga tushirish"
        echo "  stop     - Barcha xizmatlarni to'xtatish"
        echo "  restart  - Qayta ishga tushirish"
        echo "  status   - Xizmatlar holatini ko'rish"
        echo "  backend  - Faqat backend"
        echo "  frontend - Faqat frontend"
        echo "  logs     - Loglarni ko'rish"
        exit 1
        ;;
esac
