#!/bin/bash

echo "Configurando variáveis de ambiente no Fly.io..."

# Você precisa substituir estes valores pelos reais
# Para criar um Redis no Upstash: https://upstash.com/

# Exemplo de configuração:
# fly secrets set REDIS_URL="redis://default:YOUR_PASSWORD@YOUR_HOST.upstash.io:6379" --app dashboard-estoque-v2
# fly secrets set TINY_API_TOKEN="seu_token_tiny_aqui" --app dashboard-estoque-v2

echo "Para configurar, execute:"
echo ""
echo "1. Crie uma conta no Upstash (https://upstash.com)"
echo "2. Crie um banco Redis"
echo "3. Copie a URL de conexão"
echo "4. Execute:"
echo ""
echo 'fly secrets set REDIS_URL="sua_url_redis_aqui" --app dashboard-estoque-v2'
echo 'fly secrets set TINY_API_TOKEN="seu_token_tiny_aqui" --app dashboard-estoque-v2'
echo ""
echo "5. Verifique com:"
echo "fly secrets list --app dashboard-estoque-v2"