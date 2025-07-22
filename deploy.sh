#!/bin/bash

echo "🚀 Iniciando deploy do Dashboard Estoque v2.0..."

# Verificar se o Fly CLI está instalado
if ! command -v fly &> /dev/null; then
    echo "❌ Fly CLI não encontrado. Instale com: curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Criar app se não existir
if ! fly status --app dashboard-estoque-v2 &> /dev/null; then
    echo "📦 Criando nova app no Fly.io..."
    fly launch --name dashboard-estoque-v2 --region gru --no-deploy
fi

# Configurar secrets
echo "🔐 Configurando secrets..."
fly secrets set \
    TINY_API_TOKEN=fe8abfe8be5255938b70cb7f671c723ab21af6e1102f6cd730a93228d78bc5bb \
    VALKEY_PUBLIC_URL=redis://default:AiXzAAIjcDEwMDk3OWZmODY0YjA0YTliOGJmOTVjMzFkZTU0YzFhMDAxMnAxMA@prepared-mutt-42394.upstash.io:6379 \
    --app dashboard-estoque-v2

# Deploy
echo "🚀 Fazendo deploy..."
fly deploy --app dashboard-estoque-v2

echo "✅ Deploy concluído!"
echo "🌐 Acesse em: https://dashboard-estoque-v2.fly.dev"