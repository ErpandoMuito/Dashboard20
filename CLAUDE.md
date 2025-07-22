# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📋 Project Overview

DashboardNovo is an enterprise inventory management system integrated with Tiny ERP, specifically designed for managing product stock levels (e.g., PH-510, PH-520).

### Current Architecture (v2.0 - Production)
- **Backend**: Flask 3.0.0 (Python) - REST API
- **Frontend**: React 18.2.0 - Single-page application
- **Cache**: Redis 5.0.1 - High-performance caching
- **Deployment**: Fly.io (GRU region)
- **CI/CD**: GitHub Actions

## 🛠️ Essential Commands

### Development
```bash
# Start both backend and frontend
make dev

# Backend only (Flask with auto-reload)
cd flask-backend && python app.py

# Frontend only (React development server)
cd react-frontend && npm start

# Run backend tests
make backend-test
# or
cd flask-backend && pytest -v

# Docker development
make docker-up      # Start all services
make docker-down    # Stop services
make docker-logs    # View logs
```

### Deployment
```bash
# Deploy to Fly.io
make deploy
# or
fly deploy --app dashboard-estoque-v2

# View production logs
make logs
# or
fly logs -a dashboard-estoque-v2

# Check deployment status
fly status -a dashboard-estoque-v2
```

## 🏗️ High-Level Architecture

### Directory Structure
```
/
├── flask-backend/          # Flask API backend
│   ├── app/
│   │   ├── api/           # API blueprints (estoque.py)
│   │   ├── core/          # Core utilities (redis_client.py, config.py)
│   │   ├── models/        # Data models
│   │   └── services/      # Business logic (tiny_api.py)
│   ├── tests/             # Pytest test suite
│   └── requirements.txt   # Python dependencies
│
├── react-frontend/         # React frontend
│   ├── src/
│   │   ├── components/    # React components (GestaoEstoque.js)
│   │   └── services/      # API client (api.js)
│   └── package.json       # Node dependencies
│
├── Dockerfile             # Multi-stage build (Flask + React)
├── docker-compose.yml     # Local development orchestration
├── fly.toml              # Fly.io deployment configuration
└── .github/workflows/     # GitHub Actions CI/CD
```

### Key API Endpoints
```
GET  /api/health           # Health check
GET  /api/estoque/produtos # List products with stock
POST /api/estoque/ajustar  # Adjust stock (+1/-1)
POST /api/estoque/sync     # Sync with Tiny ERP (cached 5min)
```

### Data Flow
1. **Frontend** (React) → Makes API calls to backend
2. **Backend** (Flask) → Checks Redis cache first
3. **Redis** → Returns cached data if available (5min TTL)
4. **Tiny API** → Fetched only if cache miss
5. **Response** → Formatted and returned to frontend

## 🚨 Critical Rules

### 1. Redis Best Practices
- **Never use `keys()`** - Use `scan` with cursor
- **Key prefixes**: Always use prefixes like `produto:`, `estoque:`
- **TTL**: Default cache TTL is 5 minutes (300 seconds)

### 2. Tiny API Integration
- **Token**: Stored in environment variable `TINY_API_TOKEN`
- **Format**: Always use `application/x-www-form-urlencoded`
- **Caching**: All Tiny API responses are cached for 5 minutes
- **Error Handling**: Gracefully handle API failures with cached fallbacks

### 3. Stock Management
- **Products**: Currently supports PH-510, PH-520, etc.
- **Adjustments**: Only +1 or -1 increments allowed
- **Sync**: Manual sync button respects 5-minute cache

## 🐛 Known Issues

1. **Legacy Code**: Multiple test directories (teste1-5) need cleanup
2. **CORS**: Currently allows all origins in production (security concern)
3. **Documentation**: Some files still reference old FastAPI/Next.js stack

## ⚡ Performance Considerations

- **Redis Caching**: 5-minute TTL on all Tiny API responses
- **Single Container**: Flask serves both API and static React build
- **Auto-scaling**: Fly.io configured with min 1 machine
- **Health Checks**: Regular health checks ensure uptime

## 🔐 Security Notes

- **Environment Variables**: All sensitive data in .env files
- **CORS**: Configure for production domain only
- **API Token**: Never commit Tiny API token to repository

## 📝 Code Conventions

### Python (Flask Backend)
- **Files**: `snake_case.py`
- **Functions**: `snake_case()`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`

### JavaScript (React Frontend)
- **Components**: `PascalCase.js`
- **Functions**: `camelCase()`
- **API calls**: Use axios with proper error handling

### Error Handling
```python
# Flask backend
try:
    result = tiny_api.get_product_stock(product_code)
    return jsonify(result), 200
except Exception as e:
    logger.error(f"Error getting stock: {str(e)}")
    return jsonify({"error": "Failed to get stock"}), 500
```

```javascript
// React frontend
try {
  const response = await api.get('/api/estoque/produtos');
  setProducts(response.data);
} catch (error) {
  console.error('Error:', error);
  toast.error('Erro ao carregar produtos');
}
```

## 🚀 Production Details

- **URL**: https://dashboard-estoque-v2.fly.dev/estoque
- **Region**: GRU (São Paulo)
- **Port**: 8000
- **Health Check**: GET /api/health

---

**Last Updated**: January 2025  
**Version**: 2.0 (Flask + React)  
**Purpose**: Guide for Claude AI Assistant