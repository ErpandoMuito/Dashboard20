#!/bin/bash

# Script minimalista para rodar o sistema

echo "🚀 Dashboard Minimalista - Controle de Estoque"
echo ""

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado"
    exit 1
fi

# Instala dependências se necessário
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Verifica token
if [ -z "$TINY_API_TOKEN" ]; then
    if [ -f ".env" ]; then
        export $(cat .env | xargs)
    else
        echo "⚠️  Token não configurado. Copie .env.example para .env e adicione seu token"
    fi
fi

# Inicia servidor
echo ""
echo "✅ Servidor rodando em:"
echo "   API: http://localhost:8000"
echo "   UI:  http://localhost:8000/index.html"
echo ""
echo "📝 Endpoints disponíveis:"
echo "   GET  /api/v2/estoque/produto/{codigo}"
echo "   POST /api/v2/estoque/entrada"
echo ""

# Inicia o servidor com arquivos estáticos configurados corretamente
python3 server.py