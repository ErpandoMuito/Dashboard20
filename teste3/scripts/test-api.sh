#!/bin/bash

# Script de teste da API
# Testa todos os endpoints principais

API_URL="http://localhost:8000"
echo "🧪 Testando API em $API_URL"
echo "================================"

# Função para fazer request e mostrar resultado
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    echo -n "Testing $method $endpoint... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$API_URL$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo "✅ OK ($http_code)"
        if [ "$VERBOSE" = "1" ]; then
            echo "$body" | jq '.' 2>/dev/null || echo "$body"
        fi
    else
        echo "❌ FAIL ($http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    fi
    echo ""
}

# Health checks
echo "🏥 Health Checks"
echo "----------------"
test_endpoint "GET" "/health"
test_endpoint "GET" "/health/detailed"

# Notas endpoints
echo "📄 Notas Fiscais"
echo "----------------"
test_endpoint "GET" "/api/v2/notas"
test_endpoint "GET" "/api/v2/notas?data_inicial=01/01/2024&data_final=31/12/2024"

# Produtos endpoints
echo "📦 Produtos"
echo "-----------"
test_endpoint "GET" "/api/v2/produtos"
test_endpoint "GET" "/api/v2/produtos/buscar?nome=teste"

# Pedidos endpoints
echo "📋 Pedidos"
echo "----------"
test_endpoint "GET" "/api/v2/pedidos"

echo "================================"
echo "✅ Testes concluídos!"
echo ""
echo "💡 Dica: Use VERBOSE=1 $0 para ver as respostas completas"