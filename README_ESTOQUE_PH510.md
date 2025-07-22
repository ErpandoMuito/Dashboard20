# Dashboard Estoque v2.0 - Ajuste de Estoque PH-510

Sistema completo para adicionar e remover estoque do produto PH-510 usando React + FastAPI + Tiny API.

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.8+
- Node.js 14+
- npm

### 2. Instalar Dependências

#### Backend (Python/FastAPI)
```bash
cd backend
pip3 install -r requirements.txt
```

#### Frontend (React)
```bash
cd frontend
npm install
```

### 3. Iniciar os Serviços

Use o script automatizado:
```bash
./start-services.sh
```

Ou manualmente:

#### Terminal 1 - Backend
```bash
cd backend
python3 -m uvicorn main:app --reload --port 8000
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm start
```

## 📱 Acessar o Sistema

- **Dashboard**: http://localhost:3000/estoque
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 🧪 Testar a API

### Teste Automatizado
```bash
python3 test_api_estoque.py
```

### Teste Manual com cURL

#### Buscar informações do PH-510
```bash
curl http://localhost:8000/api/v2/estoque/produto/PH-510
```

#### Adicionar 1 unidade
```bash
curl -X POST http://localhost:8000/api/v2/estoque/entrada \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_produto": "PH-510",
    "quantidade": 1,
    "descricao": "Teste manual",
    "deposito": "FUNDIÇÃO"
  }'
```

#### Remover 1 unidade
```bash
curl -X POST http://localhost:8000/api/v2/estoque/saida \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_produto": "PH-510",
    "quantidade": 1,
    "descricao": "Teste manual",
    "deposito": "FUNDIÇÃO"
  }'
```

## 🎯 Funcionalidades

### Interface Web (React)
- Exibe informações do produto PH-510 em tempo real
- Botão "Adicionar 1" - adiciona 1 unidade ao estoque
- Botão "Remover 1" - remove 1 unidade do estoque
- Atualização automática do saldo após cada operação
- Notificações de sucesso/erro

### API (FastAPI)
- `GET /api/v2/estoque/produto/{codigo}` - Busca informações do produto
- `POST /api/v2/estoque/entrada` - Adiciona unidades ao estoque
- `POST /api/v2/estoque/saida` - Remove unidades do estoque

### Integração Tiny ERP
- Todas as operações são sincronizadas em tempo real com o Tiny ERP
- ID do produto PH-510 no Tiny: 893434458
- Depósito padrão: FUNDIÇÃO

## 📊 Informações do Produto

- **Código**: PH-510
- **Nome**: REB0778310
- **ID Tiny**: 893434458
- **Unidade**: Peça
- **Saldo atual**: Exibido em tempo real na interface

## 🐛 Troubleshooting

### API não conecta
- Verifique se o backend está rodando na porta 8000
- Confirme que o arquivo `.env` existe em `/backend/.env`

### Produto não encontrado
- Verifique se o token do Tiny está correto no `.env`
- Confirme que o produto PH-510 existe no Tiny

### Erro ao alterar estoque
- Verifique se o depósito "FUNDIÇÃO" existe no Tiny
- Confirme que o usuário tem permissão para alterar estoque

## 🔧 Configuração

### Variáveis de Ambiente (backend/.env)
```env
TINY_API_TOKEN=seu_token_aqui
VALKEY_PUBLIC_URL=redis://localhost:6379
```

## 📝 Logs

- Backend: Terminal onde está rodando o uvicorn
- Frontend: Console do navegador (F12)
- API Requests: Aba Network do navegador

---

**Desenvolvido com React + FastAPI + Tiny API**