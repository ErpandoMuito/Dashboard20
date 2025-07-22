# DashboardNext v2.0 - Teste 4 (Integração Completa)

Sistema empresarial integrado com Tiny ERP, desenvolvido com foco em **integração perfeita** entre todas as camadas.

## 🚀 Stack Tecnológica

### Backend
- **FastAPI** - Framework web moderno e rápido
- **Pydantic** - Validação de dados com type hints
- **Redis** - Cache e pub/sub
- **PostgreSQL** - Banco de dados principal
- **Celery** - Processamento assíncrono
- **Structlog** - Logging estruturado

### Frontend
- **React 18** - Interface reativa
- **React Query** - Gerenciamento de estado do servidor
- **React Router** - Roteamento
- **Tailwind CSS** - Estilização utility-first
- **React Hot Toast** - Notificações elegantes
- **React Error Boundary** - Tratamento de erros

### DevOps
- **Docker Compose** - Orquestração local
- **GitHub Actions** - CI/CD pipeline
- **Prometheus** - Métricas (preparado)
- **Trivy** - Scan de segurança

## 📋 Features Implementadas

### 1. Backend Robusto
- ✅ API RESTful com documentação automática (Swagger/ReDoc)
- ✅ Validação de dados com Pydantic
- ✅ Middleware de logging estruturado
- ✅ Rate limiting configurável
- ✅ Health checks detalhados
- ✅ Background tasks com Celery
- ✅ Error handling centralizado

### 2. Frontend Moderno
- ✅ Hooks customizados para API
- ✅ Loading states com skeletons
- ✅ Error boundaries para recuperação
- ✅ Toast notifications funcionais
- ✅ Layout responsivo com Tailwind
- ✅ React Query DevTools

### 3. DevOps Correto
- ✅ Docker Compose completo
- ✅ Variáveis de ambiente documentadas
- ✅ CI/CD com GitHub Actions
- ✅ Health checks em todos os serviços
- ✅ Volumes para persistência
- ✅ Networks isoladas

## 🛠️ Instalação e Execução

### Pré-requisitos
- Docker e Docker Compose
- Node.js 18+ (desenvolvimento)
- Python 3.11+ (desenvolvimento)

### Configuração Rápida

1. **Clone o repositório**
```bash
cd teste4
```

2. **Configure as variáveis de ambiente**
```bash
# Backend
cp backend/.env.example backend/.env
# Edite backend/.env com suas configurações

# Frontend
cp frontend/.env.example frontend/.env
# Edite frontend/.env se necessário
```

3. **Inicie com Docker Compose**
```bash
docker-compose up -d
```

4. **Acesse os serviços**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs
- Flower (Celery): http://localhost:5555

### Desenvolvimento Local

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## 📚 Documentação da API

A documentação completa da API está disponível em:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### Endpoints Principais

```http
# Health
GET /api/v1/health
GET /api/v1/health/detailed

# Notas Fiscais
GET    /api/v1/notas
POST   /api/v1/notas
GET    /api/v1/notas/{id}
PATCH  /api/v1/notas/{id}
DELETE /api/v1/notas/{id}
POST   /api/v1/notas/sync

# Pedidos (em desenvolvimento)
GET    /api/v1/pedidos
POST   /api/v1/pedidos/upload

# Produtos (em desenvolvimento)
GET    /api/v1/produtos
GET    /api/v1/produtos/{codigo}/abatimento
```

## 🔧 Configuração

### Variáveis de Ambiente

#### Backend (.env)
```env
# Aplicação
APP_NAME=DashboardNext
DEBUG=True
ENVIRONMENT=development

# Segurança
SECRET_KEY=your-secret-key

# Redis
REDIS_URL=redis://localhost:6379/0

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dashboard_next

# Tiny ERP
TINY_API_TOKEN=seu-token-tiny

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
```

## 🧪 Testes

### Backend
```bash
cd backend
pytest -v --cov=app
```

### Frontend
```bash
cd frontend
npm test
```

### CI/CD
Os testes são executados automaticamente no GitHub Actions em cada push/PR.

## 📊 Monitoramento

### Logs
- Backend: Structlog com formato JSON
- Frontend: Console do navegador + React Query DevTools

### Métricas
- Preparado para Prometheus (porta 9090)
- Health checks em `/api/v1/health`

### Celery
- Monitor Flower: http://localhost:5555
- Filas: Redis queues

## 🔒 Segurança

- ✅ CORS configurado
- ✅ Rate limiting
- ✅ Validação de entrada com Pydantic
- ✅ Secrets em variáveis de ambiente
- ✅ Scan de vulnerabilidades com Trivy
- ✅ Usuário não-root no Docker

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT.

---

**Desenvolvido com foco em integração perfeita** 🚀