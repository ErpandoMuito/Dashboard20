# Dashboard Estoque v2.0

Sistema de entrada de estoque integrado com Tiny ERP, desenvolvido com React + FastAPI + Redis.

## 🌐 URLs de Produção

- **Aplicação**: https://dashboard-estoque-v2.fly.dev/estoque
- **API Docs**: https://dashboard-estoque-v2.fly.dev/docs
- **Health Check**: https://dashboard-estoque-v2.fly.dev/health

## 🚀 Comandos Rápidos (Makefile)

```bash
# Desenvolvimento
make dev          # Inicia backend e frontend
make backend-dev  # Apenas backend
make frontend-dev # Apenas frontend

# Testes
make test         # Executa testes (exceto E2E)

# Docker
make docker-up    # Sobe containers
make docker-down  # Para containers
make docker-logs  # Ver logs

# Deploy
make deploy       # Deploy para Fly.io
make logs        # Ver logs do Fly
make status      # Status da aplicação

# Setup inicial
make setup       # Instala dependências
```

## 🛠️ Stack Tecnológica

- **Frontend**: React 18
- **Backend**: FastAPI (Python 3.11)
- **Cache**: Redis
- **Deploy**: Fly.io (4GB RAM, região GRU)

## 📦 Instalação Local

### Docker Compose (Recomendado)

```bash
docker-compose up -d
```

Acesse:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🧪 Testes

Os testes estão configurados para rodar via npm/Makefile:

```bash
# Backend
cd backend
npm run test          # Todos exceto E2E
npm run test:unit     # Apenas unitários
npm run test:integration # Apenas integração
npm run test:coverage # Com relatório de cobertura
```

## 📚 Endpoints da API

### POST /api/v2/estoque/entrada
Realiza entrada de estoque

```json
{
  "codigo_produto": "PH-510",
  "quantidade": 100,
  "descricao": "Entrada de produção",
  "data": "2025-07-21T10:00:00",
  "deposito": "Geral"
}
```

### GET /api/v2/estoque/produto/{codigo}
Busca informações do produto com cache

### GET /api/v2/estoque/historico/{codigo}
Retorna histórico de movimentações

## 🔒 Variáveis de Ambiente

Criar arquivo `.env` no backend:

```env
TINY_API_TOKEN=seu_token_aqui
VALKEY_PUBLIC_URL=redis://...
```

## 📊 Monitoramento

- **Fly.io Dashboard**: https://fly.io/apps/dashboard-estoque-v2/monitoring
- **Logs**: `make logs` ou `fly logs -a dashboard-estoque-v2`
- **Métricas**: https://fly.io/apps/dashboard-estoque-v2/monitoring/metrics