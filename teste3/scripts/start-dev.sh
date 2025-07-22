#!/bin/bash

# Script para iniciar ambiente de desenvolvimento
echo "🚀 Iniciando Dashboard v2.0 em modo desenvolvimento"
echo "=================================================="

# Verifica Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale o Docker."
    exit 1
fi

# Verifica Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Por favor, instale o Docker Compose."
    exit 1
fi

# Para containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Constrói imagens
echo "🔨 Construindo imagens..."
docker-compose build

# Inicia serviços
echo "🚀 Iniciando serviços..."
docker-compose up -d

# Aguarda serviços ficarem prontos
echo "⏳ Aguardando serviços..."
sleep 5

# Verifica saúde dos serviços
echo "🏥 Verificando saúde dos serviços..."
./test-api.sh

echo ""
echo "✅ Dashboard v2.0 iniciado com sucesso!"
echo ""
echo "📍 URLs:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Metrics: http://localhost:8000/metrics"
echo ""
echo "📝 Comandos úteis:"
echo "   - Ver logs: docker-compose logs -f"
echo "   - Parar: docker-compose down"
echo "   - Reiniciar: docker-compose restart"
echo ""