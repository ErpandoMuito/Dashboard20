#!/bin/bash

# Script de deploy com correções para Dashboard Estoque v2

echo "🚀 Iniciando deploy com correções..."

# 1. Fazer build e deploy
echo "📦 Fazendo build e deploy..."
fly deploy --app dashboard-estoque-v2

# 2. Verificar status
echo "✅ Verificando status da aplicação..."
fly status --app dashboard-estoque-v2

# 3. Verificar variáveis de ambiente
echo "🔍 Verificando variáveis de ambiente..."
fly secrets list --app dashboard-estoque-v2

# 4. Testar endpoints
echo "🧪 Testando endpoints..."
APP_URL="https://dashboard-estoque-v2.fly.dev"

echo "- Health check:"
curl -s "$APP_URL/api/health" | jq .

echo "- Debug env:"
curl -s "$APP_URL/api/debug/env" | jq .

echo "- Página principal:"
curl -s -o /dev/null -w "%{http_code}" "$APP_URL/"

echo ""
echo "✅ Deploy concluído! Acesse: $APP_URL"
echo ""
echo "📝 Para verificar logs em tempo real:"
echo "fly logs --app dashboard-estoque-v2"