# Deploy do Dashboard Estoque v2.0

## 🚀 Deploy Automático no Fly.io

O sistema está configurado para deploy automático através do GitHub Actions.

### Pré-requisitos

1. **Repositório no GitHub** com os arquivos do projeto
2. **Secret FLY_API_TOKEN** configurado no GitHub
3. **App criado no Fly.io** com nome `dashboard-estoque-v2`

### Como Fazer Deploy

1. **Commit e Push**:
```bash
git add .
git commit -m "sua mensagem"
git push origin main
```

2. O GitHub Actions irá automaticamente:
   - Fazer build do frontend React
   - Fazer build do backend FastAPI
   - Deploy no Fly.io
   - Verificar health check

### URLs em Produção

- **Dashboard**: https://dashboard-estoque-v2.fly.dev/estoque
- **API Health**: https://dashboard-estoque-v2.fly.dev/api/health
- **API Docs**: https://dashboard-estoque-v2.fly.dev/docs

### Endpoints da API

#### Gestão de Estoque
- `POST /api/v2/estoque/entrada` - Adicionar estoque
- `POST /api/v2/estoque/saida` - Remover estoque  
- `GET /api/v2/estoque/produto/{codigo}` - Buscar produto

#### Cache de Produtos
- `POST /api/v2/estoque/cache/popular` - Popular cache PH
- `GET /api/v2/estoque/cache/produtos` - Listar produtos cacheados
- `DELETE /api/v2/estoque/cache` - Limpar cache

### Configuração do Fly.io

Se ainda não tiver o app criado:

```bash
fly launch --name dashboard-estoque-v2 --region gru
fly secrets set TINY_API_TOKEN=seu_token_aqui
fly secrets set VALKEY_PUBLIC_URL=redis://...
```

### Troubleshooting

#### Deploy falhou
- Verifique os logs: `fly logs -a dashboard-estoque-v2`
- Verifique secrets: `fly secrets list -a dashboard-estoque-v2`

#### Página não carrega
- Verifique se o frontend foi buildado corretamente
- Verifique o main.py está servindo arquivos estáticos

#### API não responde
- Verifique health: https://dashboard-estoque-v2.fly.dev/api/health
- Verifique logs do backend