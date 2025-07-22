#!/bin/bash

# 🚀 SCRIPT HACKER - INICIA TUDO COM 1 COMANDO!

echo "🔥 INICIANDO SISTEMA HACKER..."

# HACK 1: Verifica/instala dependências automaticamente
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    exit 1
fi

# HACK 2: Cria venv se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# HACK 3: Ativa venv
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# HACK 4: Instala deps sem perguntar
echo "📥 Instalando dependências..."
pip install -q fastapi uvicorn redis httpx python-multipart websockets PyPDF2

# HACK 5: Tenta iniciar Redis (se tiver)
if command -v redis-server &> /dev/null; then
    echo "🔴 Iniciando Redis..."
    redis-server --daemonize yes 2>/dev/null || echo "⚠️  Redis já rodando ou não disponível"
else
    echo "⚠️  Redis não instalado - usando cache em memória"
fi

# HACK 6: Mata processo anterior na porta 8000
echo "🔪 Limpando porta 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# HACK 7: Inicia servidor com output colorido
echo ""
echo "🚀 SERVIDOR RODANDO!"
echo "📍 Dashboard: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""

# HACK 8: Inicia com reload automático
python3 server_hack.py