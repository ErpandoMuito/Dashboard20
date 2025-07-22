#!/bin/bash

echo "=== Iniciando Dashboard Estoque v2.0 ==="
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para encerrar processos ao sair
cleanup() {
    echo -e "\n${YELLOW}Encerrando serviços...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Verificar se estamos no diretório correto
if [ ! -f "backend/main.py" ]; then
    echo "❌ Erro: Execute este script no diretório dashboard-v2"
    exit 1
fi

# Iniciar Backend
echo -e "${BLUE}1. Iniciando Backend (FastAPI)...${NC}"
cd backend
python3 -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Aguardar backend iniciar
echo -e "${YELLOW}   Aguardando backend iniciar...${NC}"
sleep 3

# Verificar se backend está rodando
curl -s http://localhost:8000/api/health > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✓ Backend rodando em http://localhost:8000${NC}"
else
    echo -e "❌ Erro ao iniciar backend"
    exit 1
fi

# Iniciar Frontend
echo -e "\n${BLUE}2. Iniciando Frontend (React)...${NC}"
cd frontend

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}   Instalando dependências do frontend...${NC}"
    npm install
fi

# Iniciar React
BROWSER=none npm start &
FRONTEND_PID=$!
cd ..

# Aguardar frontend iniciar
echo -e "${YELLOW}   Aguardando frontend iniciar...${NC}"
sleep 5

echo -e "\n${GREEN}=== Serviços Iniciados ===${NC}"
echo -e "${GREEN}✓ Backend:${NC} http://localhost:8000"
echo -e "${GREEN}✓ Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}✓ API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Pressione Ctrl+C para encerrar todos os serviços${NC}"
echo ""

# Manter script rodando
wait