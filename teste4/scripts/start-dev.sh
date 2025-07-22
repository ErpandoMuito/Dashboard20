#!/bin/bash
# Development startup script

echo "🚀 Starting DashboardNext Development Environment..."

# Check if .env files exist
if [ ! -f backend/.env ]; then
    echo "⚠️  Creating backend/.env from example..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env with your configuration"
fi

if [ ! -f frontend/.env ]; then
    echo "⚠️  Creating frontend/.env from example..."
    cp frontend/.env.example frontend/.env
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health
echo "🏥 Checking service health..."
curl -s http://localhost:8000/api/v1/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

# Show URLs
echo ""
echo "🎉 DashboardNext is ready!"
echo ""
echo "📍 Access points:"
echo "   Frontend:    http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs:    http://localhost:8000/api/v1/docs"
echo "   Flower:      http://localhost:5555"
echo ""
echo "📊 Logs:"
echo "   docker-compose logs -f backend"
echo "   docker-compose logs -f frontend"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"
echo ""