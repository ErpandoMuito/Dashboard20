# 🛠️ Correções Aplicadas - Dashboard Estoque v2

## Problemas Identificados e Resolvidos

### 1. ❌ Erro Redis/Upstash
**Problema**: "Error -2 connecting to prepared-mutt-42394.upstash.io:6379. Name or service not known"

**Correção aplicada em** `backend/app/core/redis_client.py`:
- Adicionado suporte SSL para Upstash
- Adicionado teste de conexão com ping
- Melhor tratamento de erros

### 2. ❌ Erro API Tiny
**Problema**: "404 Not Found for url 'https://api.tiny.com.br/api2/produto.alterar.estoque.php'"

**Correções aplicadas em** `backend/app/services/tiny_api.py`:
- Endpoint correto: `produto.atualizar.estoque.php` (não `alterar`)
- Estrutura de dados corrigida: usa objeto `estoque` com `idProduto`
- Serialização JSON do objeto estoque

### 3. ❌ Arquivos estáticos não encontrados
**Problema**: CSS e JS retornando 404

**Correção aplicada em** `backend/main.py`:
- Mapeamento correto das rotas `/css` e `/js`
- Ajuste para estrutura `static/static/` do React build

## 📋 Comandos para Configurar Variáveis no Fly.io

```bash
# Verificar variáveis atuais
fly secrets list --app dashboard-estoque-v2

# Se VALKEY_PUBLIC_URL estiver com problema, obter nova URL:
fly redis create  # Criar novo Redis se necessário

# Ou usar Upstash:
# 1. Criar conta em upstash.com
# 2. Criar database Redis
# 3. Copiar Redis URL (com rediss://)

# Configurar variáveis
fly secrets set VALKEY_PUBLIC_URL="rediss://default:senha@endpoint.upstash.io:porta" --app dashboard-estoque-v2
fly secrets set TINY_API_TOKEN="seu_token_tiny" --app dashboard-estoque-v2
```

## 🔧 Variáveis de Ambiente Necessárias

1. **VALKEY_PUBLIC_URL** ou **REDIS_URL**
   - Formato: `redis://host:porta` ou `rediss://user:pass@host:porta`
   - Para Upstash: usar URL com `rediss://` (SSL)

2. **TINY_API_TOKEN**
   - Token de API do Tiny ERP
   - Obter em: Tiny > Configurações > API

## 📁 Arquivos Modificados

1. `/backend/app/core/redis_client.py` - Conexão Redis com SSL
2. `/backend/app/services/tiny_api.py` - Endpoint e estrutura corrigidos
3. `/backend/main.py` - Rotas estáticas e debug endpoint
4. `.env.example` - Template de variáveis (novo)
5. `deploy-fix.sh` - Script de deploy com testes (novo)
6. `FIXES.md` - Esta documentação (novo)

## 🚀 Deploy com Correções

```bash
# Na pasta dashboard-v2/
./deploy-fix.sh
```

## 🧪 Testar Correções

1. **Verificar variáveis**:
   ```bash
   curl https://dashboard-estoque-v2.fly.dev/api/debug/env
   ```

2. **Testar busca de produto**:
   - Acessar https://dashboard-estoque-v2.fly.dev/estoque
   - Digitar código do produto (ex: PH-510)
   - Deve buscar sem erro

3. **Testar entrada de estoque**:
   - Preencher quantidade
   - Clicar em "Adicionar ao Estoque"
   - Deve atualizar no Tiny

## ⚠️ Importante

- O endpoint `/api/debug/env` deve ser removido em produção
- Verificar logs com: `fly logs --app dashboard-estoque-v2`
- Para SSH no container: `fly ssh console --app dashboard-estoque-v2`

## 📞 Suporte

Se persistirem erros após aplicar estas correções:
1. Verificar logs detalhados
2. Confirmar URLs do Redis/Upstash
3. Validar token Tiny na plataforma