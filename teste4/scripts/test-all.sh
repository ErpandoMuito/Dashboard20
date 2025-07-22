#!/bin/bash

# Script para testar todos os componentes do DashboardNext v2.0

echo "🧪 Testando DashboardNext v2.0 - Teste 4"
echo "======================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para testar endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=$3
    
    echo -n "Testing $name... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✓ OK${NC} (Status: $status)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected: $expected_status, Got: $status)"
        return 1
    fi
}

# Verificar se os serviços estão rodando
echo "1. Verificando containers Docker..."
echo "-----------------------------------"
docker-compose ps
echo ""

# Testar endpoints do Backend
echo "2. Testando Backend API..."
echo "--------------------------"
test_endpoint "Root endpoint" "http://localhost:8000/" 200
test_endpoint "Health check" "http://localhost:8000/api/v1/health" 200
test_endpoint "API Docs" "http://localhost:8000/api/v1/docs" 200
test_endpoint "ReDoc" "http://localhost:8000/api/v1/redoc" 200
echo ""

# Testar Redis
echo "3. Testando Redis..."
echo "--------------------"
echo -n "Redis PING... "
if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Testar PostgreSQL
echo "4. Testando PostgreSQL..."
echo "-------------------------"
echo -n "PostgreSQL connection... "
if docker-compose exec -T postgres pg_isready -U postgres | grep -q "accepting connections"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Testar Frontend
echo "5. Testando Frontend..."
echo "-----------------------"
test_endpoint "Frontend" "http://localhost:3000" 200
echo ""

# Testar Celery
echo "6. Testando Celery..."
echo "---------------------"
echo -n "Celery workers... "
if docker-compose exec -T celery celery -A app.workers.celery_app inspect active >/dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi

echo -n "Flower monitoring... "
test_endpoint "Flower" "http://localhost:5555" 200
echo ""

# Executar testes unitários do backend
echo "7. Executando testes unitários..."
echo "---------------------------------"
if docker-compose exec -T backend pytest -v --tb=short; then
    echo -e "${GREEN}✓ Testes passaram${NC}"
else
    echo -e "${RED}✗ Alguns testes falharam${NC}"
fi
echo ""

# Resumo
echo "======================================="
echo "Resumo dos Testes"
echo "======================================="
echo ""
echo -e "${YELLOW}Dica:${NC} Se algum teste falhou, verifique os logs com:"
echo "  docker-compose logs [nome-do-servico]"
echo ""
echo "Para logs em tempo real:"
echo "  docker-compose logs -f"
echo ""