#!/bin/bash

echo "🧪 Testando API do Dashboard de Estoque"
echo ""

# URL base da API em produção
API_URL="https://dashboard-estoque-v2.fly.dev/teste1"

# Teste 1: Health check
echo "1. Testando health check..."
curl -s "$API_URL/api/v2/health" | python3 -m json.tool
echo ""

# Teste 2: Buscar produto
echo "2. Buscando produto PH-510..."
curl -s "$API_URL/api/v2/estoque/produto/PH-510" | python3 -m json.tool
echo ""

# Teste 3: Entrada de estoque (exemplo)
echo "3. Exemplo de entrada de estoque (POST):"
echo "curl -X POST '$API_URL/api/v2/estoque/entrada' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"codigo\": \"PH-510\", \"quantidade\": 10, \"observacao\": \"Teste\"}'"
echo ""

echo "✅ Testes concluídos!"