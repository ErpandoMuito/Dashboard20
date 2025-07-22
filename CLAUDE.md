# Instruções para Claude - DashboardNext v2.0 (Nova Arquitetura)

Este documento contém instruções específicas para ajudar o Claude a trabalhar com o projeto DashboardNext em sua nova arquitetura.

## 📋 Contexto do Projeto

DashboardNext é um sistema empresarial integrado com Tiny ERP. O sistema gerencia notas fiscais, produtos, pedidos e analytics em tempo real.

### Nova Stack (v2.0)
- **Frontend**: React (Interface do usuário - dashboard)
- **Backend**: FastAPI (Python) - API rápida e moderna para processar dados
- **Banco/Cache**: Redis - Cache, filas, pub/sub
- **Integração**: Tiny ERP API

### Stack Anterior (v1.x) - DESCONTINUADA
- Frontend: Next.js 15.3.4, React 19, TypeScript
- Backend: API Routes do Next.js
- Deploy: Fly.io

## 🚨 Regras Críticas

### 1. NÃO Modificar Lógica de Semanas
A lógica de agrupamento por sextas-feiras é **fundamental** para o sistema. Qualquer alteração deve ser discutida antes:
- Arquivos: `/lib/semanas-por-sexta.ts`, `/lib/month-weeks.ts`
- Conceito: Todas as entregas são agrupadas pela sexta-feira da semana ISO

### 2. Formato de Datas
- **Exibição**: Sempre `dd/MM/yyyy` (formato brasileiro)
- **Interno**: ISO 8601 para ordenação
- **Semanas**: ISO week format `yyyy-'W'ww`

### 3. Redis/Upstash
- **Nunca use `keys()`**: Use `scan` com cursor
- **Chaves sempre com prefixo**: `nota:`, `pedido:`, `produto:codigo:`
- **IDs prefixados**: `ped_`, `req_`, `nota_`

### 4. Integração Tiny
- **Token**: Está em `.env` como `TINY_API_TOKEN`
- **Rate limit**: 60s entre requisições para evitar bloqueio
- **Formato**: Sempre `application/x-www-form-urlencoded`

## 🏗️ Nova Arquitetura (v2.0)

### Estrutura de Diretórios Proposta
```
/
├── frontend/              # React App
│   ├── src/
│   │   ├── components/   # Componentes React
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # Comunicação com API
│   │   └── utils/        # Utilitários
│   └── package.json
│
├── backend/               # FastAPI
│   ├── app/
│   │   ├── api/          # Endpoints
│   │   ├── core/         # Configurações
│   │   ├── models/       # Pydantic models
│   │   ├── services/     # Lógica de negócio
│   │   └── workers/      # Background tasks
│   ├── requirements.txt
│   └── main.py
│
└── docker-compose.yml     # Orquestração local
```

### Migração de Componentes-Chave

| v1.x (Next.js/TS) | v2.0 (React/FastAPI) | Observações |
|-------------------|---------------------|-------------|
| `/lib/tiny-api.ts` | `/backend/app/services/tiny_api.py` | Reescrever em Python |
| `/lib/abatimento.ts` | `/backend/app/services/abatimento.py` | Manter lógica FIFO |
| `/lib/semanas-por-sexta.ts` | `/backend/app/services/semanas.py` | **CRÍTICO**: Manter exata |
| `/components/*.tsx` | `/frontend/src/components/*.jsx` | Converter para React puro |
| API Routes | FastAPI endpoints | RESTful + WebSockets |

## 🛠️ Comandos Úteis (Nova Stack)

```bash
# Backend (FastAPI)
cd backend/
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (React)
cd frontend/
npm install
npm start

# Docker Compose (desenvolvimento)
docker-compose up -d

# Redis
redis-cli
```

### Endpoints FastAPI Principais
```python
# Exemplos de rotas
GET  /api/v2/notas          # Lista notas fiscais
POST /api/v2/notas/sync     # Sincroniza com Tiny
GET  /api/v2/pedidos        # Lista pedidos
POST /api/v2/pedidos/upload # Upload de PDF
GET  /api/v2/produtos       # Lista produtos
```

## 🐛 Bugs Conhecidos

1. **BUG:001**: Entregas de final de mês agrupadas no mês seguinte
   - Arquivo: `/lib/semanas-por-sexta.ts`
   - Status: Aguardando correção

2. **BUG:002**: Cálculo firm/forecast usa data ajustada
   - Arquivo: `/components/pedidos-table.tsx`
   - Status: Em análise

## 🔄 Fluxos Críticos

### Upload de Pedido
1. PDF é processado em `/api/pedidos/upload`
2. Parser identifica cliente (ex: VIBRACOUSTIC)
3. Salva em Redis com índices
4. Ajusta datas para sextas-feiras

### Sistema de Abatimento
1. Busca notas do produto
2. Ordena pedidos por data (FIFO)
3. Deduz quantidades das entregas
4. Mostra saldo restante

## ⚡ Performance

### Otimizações para v2.0
- **Frontend**: React com lazy loading e memoização
- **Backend**: FastAPI com async/await nativo
- **Cache**: Redis para resposta rápida
- **Workers**: Celery para tarefas em background

### Limites
- Redis: Configurar maxmemory-policy
- PDFs: Máximo 10MB para upload
- API Tiny: ~10.000 requisições/dia
- FastAPI: Connection pooling para Redis

## 🎨 Padrões de UI

### Cores das Semanas
- Semana 1: Azul (#3B82F6)
- Semana 2: Roxo (#8B5CF6) 
- Semana 3: Verde (#10B981)
- Semana 4: Amarelo (#F59E0B)
- Semana 5: Laranja (#F97316)
- Backlog: Vermelho (#EF4444)
- Forecast: Âmbar (#D97706)

### Ícones
- ✓ Saldo zerado (sucesso)
- ❗ Saldo negativo (erro)

## 📝 Convenções de Código

### Nomenclatura
- **React Components**: `PascalCase.jsx`
- **Python modules**: `snake_case.py`
- **Python classes**: `PascalCase`
- **Python functions**: `snake_case`
- **Constantes**: `UPPER_SNAKE_CASE`

### Tratamento de Erros (v2.0)

**FastAPI (Python)**
```python
from fastapi import HTTPException

try:
    # lógica...
except Exception as e:
    logger.error(f"Erro em {endpoint}: {e}", extra={"params": params})
    raise HTTPException(
        status_code=500,
        detail="Mensagem amigável para o usuário"
    )
```

**React (JavaScript)**
```javascript
try {
  const response = await fetch('/api/v2/endpoint')
  if (!response.ok) throw new Error('Falha na requisição')
  // continua...
} catch (error) {
  console.error('Erro:', error)
  toast.error('Erro ao carregar dados')
}
```

## 🔐 Segurança

- **Tokens**: Nunca hardcode, use variáveis de ambiente
- **Blacklist**: Empresas bloqueadas em `config:blacklist`
- **Auth**: Sistema básico de login (melhorar para JWT)

## 📊 Monitoramento (v2.0)

```bash
# Logs do FastAPI
docker logs backend_container -f

# Logs do React (desenvolvimento)
# Aparecem no console do navegador

# Redis Monitor
redis-cli monitor

# Python debugging
import pdb; pdb.set_trace()

# React debugging
console.log() ou React DevTools
```

## ⚠️ Avisos Importantes

1. **Sempre teste localmente** antes de fazer deploy
2. **Não modifique** a lógica de semanas sem discussão
3. **Cuidado com rate limits** da API Tiny
4. **Valide PDFs** antes de processar (máx 10MB)
5. **Use TodoWrite** para planejar tarefas complexas

## 🚀 Roadmap v2.0

### Fase 1 - Migração Core
- [ ] Setup inicial React + FastAPI + Redis
- [ ] Migrar lógica de semanas (CRÍTICO)
- [ ] Implementar autenticação JWT
- [ ] Criar endpoints básicos

### Fase 2 - Features
- [ ] Sistema de abatimento FIFO
- [ ] Upload e parser de PDFs
- [ ] Worker de sincronização (Celery)
- [ ] Dashboard interativo

### Fase 3 - Melhorias
- [ ] WebSockets para updates real-time
- [ ] Testes automatizados (pytest + Jest)
- [ ] CI/CD com GitHub Actions
- [ ] Deploy com Docker/Kubernetes

## 📞 Suporte

Para dúvidas sobre:
- **Lógica de negócio**: Ver DOCUMENTACAO.md
- **Deploy**: Verificar fly.toml e Dockerfile
- **Integração Tiny**: Consultar seção 5 da documentação

---

## 🔧 Tecnologias da Nova Stack

### Backend (Python/FastAPI)
```python
# requirements.txt principais
fastapi==0.104.1
uvicorn==0.24.0
redis==5.0.1
celery==5.3.4
pydantic==2.5.0
python-multipart==0.0.6  # Upload de arquivos
PyPDF2==3.0.1  # Parser de PDF
python-dateutil==2.8.2
httpx==0.25.1  # Cliente HTTP async
```

### Frontend (React)
```json
// package.json principais
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "axios": "^1.6.0",
  "react-query": "^3.39.0",
  "date-fns": "^2.30.0",
  "recharts": "^2.9.0",
  "react-table": "^7.8.0",
  "react-toastify": "^9.1.0"
}
```

### Docker Compose
```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - TINY_API_TOKEN=${TINY_API_TOKEN}
    depends_on:
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
```

---

**Última atualização**: 21/07/2025  
**Versão**: 2.0 (Nova Arquitetura)  
**Mantido para**: Claude AI Assistant