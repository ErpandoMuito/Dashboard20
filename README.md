# Dashboard de Gestão de Estoque

Sistema de gestão de estoque integrado com Tiny ERP, desenvolvido com Flask (backend) e React (frontend).

## 🚀 Acesso Rápido

**🔗 Sistema em produção: https://dashboard-estoque-v2.fly.dev/estoque**

## ✨ Funcionalidades

- 🔍 Buscar qualquer produto pelo código (ex: PH-510, PH-520)
- ➕ Adicionar quantidade específica ao estoque
- ➖ Remover quantidade específica do estoque
- 📝 Campo de descrição/observação para cada movimentação
- 🔄 Sincronização em tempo real com Tiny ERP
- 📊 Visualização de estoque por depósito

## 🛠️ Stack Tecnológica

- **Backend**: Flask (Python) - API simples e eficiente
- **Frontend**: React 18 - Interface moderna e responsiva
- **Cache**: Redis - Performance otimizada
- **Deploy**: Fly.io - Hospedagem confiável
- **CI/CD**: GitHub Actions - Deploy automático

## 📁 Estrutura do Projeto

```
/
├── flask-backend/        # Backend Flask
│   ├── app.py           # Aplicação principal
│   ├── app/             # Módulos da aplicação
│   │   ├── api/         # Endpoints
│   │   ├── core/        # Configurações
│   │   ├── models/      # Modelos de dados
│   │   └── services/    # Serviços (Tiny API, etc)
│   └── requirements.txt # Dependências Python
│
├── react-frontend/       # Frontend React
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   └── services/    # Integração com API
│   └── package.json     # Dependências Node.js
│
├── .github/workflows/    # GitHub Actions
│   └── deploy.yml       # Deploy automático
│
├── Dockerfile           # Imagem Docker
├── fly.toml            # Configuração Fly.io
└── docker-compose.yml  # Desenvolvimento local
```

## 🚀 Como Executar Localmente

### Opção 1: Docker Compose (Recomendado)

```bash
docker-compose up
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### Opção 2: Manualmente

**Backend:**
```bash
cd flask-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
cd react-frontend
npm install
npm start
```

## 🔧 Variáveis de Ambiente

Crie um arquivo `.env` no diretório `flask-backend/`:

```env
TINY_API_TOKEN=seu_token_aqui
VALKEY_PUBLIC_URL=redis://localhost:6379
SECRET_KEY=sua_chave_secreta
```

## 📦 Deploy

O deploy é feito automaticamente via GitHub Actions quando há push na branch `main`.

Para deploy manual:
```bash
fly deploy
```

## 🧪 Testes

Execute o script de teste:
```bash
python test_flask_app.py
```

## 📝 Uso do Sistema

1. Acesse https://dashboard-estoque-v2.fly.dev/estoque
2. Digite o código do produto (ex: PH-510)
3. Clique em "Buscar Produto"
4. Digite a quantidade desejada
5. Opcionalmente, adicione uma descrição
6. Clique em "Adicionar" ou "Remover"

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é privado e de uso exclusivo da empresa.

---

**Última atualização**: 22/07/2025