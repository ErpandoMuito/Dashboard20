#!/bin/bash

# Script para testar API do Dashboard Estoque v2

APP_URL="https://dashboard-estoque-v2.fly.dev"

echo "🧪 Testando API Dashboard Estoque v2..."
echo ""

# 1. Health Check
echo "1️⃣ Health Check:"
curl -s "$APP_URL/api/health" | jq .
echo ""

# 2. Debug Environment
echo "2️⃣ Variáveis de Ambiente:"
curl -s "$APP_URL/api/debug/env" | jq .
echo ""

# 3. Buscar Produto
echo "3️⃣ Buscando produto PH-510:"
RESPONSE=$(curl -s "$APP_URL/api/v2/estoque/produto/PH-510")
echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
echo ""

# 4. Teste de Entrada de Estoque (exemplo)
echo "4️⃣ Teste de Entrada de Estoque:"
echo "Para testar entrada de estoque, use:"
echo "curl -X POST '$APP_URL/api/v2/estoque/entrada' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"codigo_produto\": \"PH-510\", \"quantidade\": 10, \"observacoes\": \"Teste\"}'"
echo ""

# 5. Verificar página principal
echo "5️⃣ Verificando página principal:"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/")
echo "Status HTTP: $STATUS"
if [ "$STATUS" = "200" ]; then
    echo "✅ Página principal acessível"
else
    echo "❌ Erro ao acessar página principal"
fi
echo ""

# 6. Verificar página de estoque
echo "6️⃣ Verificando página de estoque:"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/estoque")
echo "Status HTTP: $STATUS"
if [ "$STATUS" = "200" ]; then
    echo "✅ Página de estoque acessível"
else
    echo "❌ Erro ao acessar página de estoque"
fi
echo ""

echo "✅ Testes concluídos!"
echo ""
echo "📝 Para ver logs em tempo real:"
echo "fly logs --app dashboard-estoque-v2"