#!/bin/bash

# Script para iniciar o DashboardNext v2.0 - Teste 4

echo "🚀 Iniciando DashboardNext v2.0 - Teste 4..."

# Verifica se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Criar arquivos .env se não existirem
if [ ! -f "./backend/.env" ]; then
    echo "📝 Criando arquivo .env para backend..."
    cp ./backend/.env.example ./backend/.env
    echo "⚠️  Por favor, edite ./backend/.env com suas configurações (especialmente TINY_API_TOKEN)"
fi

if [ ! -f "./frontend/.env" ]; then
    echo "📝 Criando arquivo .env para frontend..."
    cp ./frontend/.env.example ./frontend/.env
fi

# Para containers antigos se existirem
echo "🛑 Parando containers antigos..."
docker-compose down

# Remove volumes antigos para limpar cache (opcional)
# echo "🧹 Limpando volumes antigos..."
# docker-compose down -v

# Constrói as imagens
echo "🏗️  Construindo imagens Docker..."
docker-compose build

# Inicia os serviços
echo "▶️  Iniciando serviços..."
docker-compose up -d

# Aguarda os serviços iniciarem
echo "⏳ Aguardando serviços iniciarem..."
sleep 15

# Verifica status dos containers
echo "📊 Status dos containers:"
docker-compose ps

# Verifica health do backend
echo ""
echo "🏥 Verificando saúde dos serviços..."
curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend está saudável"
    # Mostra detalhes do health check
    curl -s http://localhost:8000/api/v1/health | python -m json.tool 2>/dev/null || echo "   (Detalhes não disponíveis)"
else
    echo "❌ Backend não está respondendo"
    echo "   Verifique os logs: docker-compose logs backend"
fi

echo ""
echo "✅ DashboardNext v2.0 - Teste 4 iniciado!"
echo ""
echo "🌐 Acesse:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/api/v1/docs"
echo "   - ReDoc: http://localhost:8000/api/v1/redoc"
echo "   - Flower (Celery): http://localhost:5555"
echo ""
echo "📌 Comandos úteis:"
echo "   - Ver todos os logs: docker-compose logs -f"
echo "   - Ver logs específicos: docker-compose logs -f [backend|frontend|redis|postgres|celery|flower]"
echo "   - Parar tudo: docker-compose down"
echo "   - Reiniciar serviço: docker-compose restart [serviço]"
echo "   - Executar testes backend: docker-compose exec backend pytest"
echo ""