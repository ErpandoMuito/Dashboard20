#!/bin/bash

echo "=== Configurando Fly.io para Dashboard Estoque v2 ==="

# Verificar se flyctl está instalado
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl não encontrado. Instale em: https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

# Login no Fly (se necessário)
if ! flyctl auth whoami &> /dev/null; then
    echo "📝 Fazendo login no Fly.io..."
    flyctl auth login
fi

# Verificar se o app existe
if flyctl apps list | grep -q "dashboard-estoque-v2"; then
    echo "✅ App dashboard-estoque-v2 já existe"
else
    echo "📦 Criando app dashboard-estoque-v2..."
    flyctl apps create dashboard-estoque-v2 --org personal
fi

# Configurar secrets
echo ""
echo "🔐 Configurando secrets..."
echo "Digite o token do Tiny API:"
read -s TINY_TOKEN
flyctl secrets set TINY_API_TOKEN="$TINY_TOKEN" -a dashboard-estoque-v2

echo ""
echo "Digite a URL do Redis/Valkey (ou deixe em branco para usar local):"
read REDIS_URL
if [ -n "$REDIS_URL" ]; then
    flyctl secrets set VALKEY_PUBLIC_URL="$REDIS_URL" -a dashboard-estoque-v2
fi

echo ""
echo "✅ Configuração concluída!"
echo ""
echo "Para fazer deploy manual:"
echo "  flyctl deploy -a dashboard-estoque-v2"
echo ""
echo "Para ver logs:"
echo "  flyctl logs -a dashboard-estoque-v2"