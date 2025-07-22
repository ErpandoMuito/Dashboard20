# GitHub Actions - Dashboard v2

## 🔐 Secrets Necessários

Configure no GitHub → Settings → Secrets:

1. **TINY_API_TOKEN** - Token da API do Tiny ERP
2. **FLY_API_TOKEN** - Token do Fly.io (obter com `fly auth token`)

## 📋 Workflows Disponíveis

### 1. Testes Automatizados (`test.yml`)
- **Trigger**: Push em main/develop ou Pull Request
- **Jobs**:
  - Backend tests com coverage
  - Frontend build validation
  - Docker build test
- **Executado automaticamente**

### 2. Deploy Automático (`deploy.yml`)
- **Trigger**: Push na branch main
- **Jobs**:
  - Executa todos os testes primeiro
  - Deploy para Fly.io se testes passarem
  - Health check após deploy
- **Deploy apenas em main**

### 3. Testes E2E Manual (`e2e-manual.yml`)
- **Trigger**: Manual (workflow_dispatch)
- **Opções**:
  - `smoke`: Testes rápidos
  - `single`: Um teste específico
  - `full`: Suite completa
- **Use com cuidado - altera dados no Tiny**

### 4. CodeQL Security (`codeql.yml`)
- **Trigger**: Push/PR em main + semanal
- **Análise**: JavaScript e Python
- **Identifica vulnerabilidades**

## 🚀 Como Configurar

```bash
# 1. Obter token do Fly.io
fly auth token

# 2. No GitHub:
# Settings → Secrets → New repository secret
# - Name: FLY_API_TOKEN
# - Value: [colar token]

# 3. Adicionar TINY_API_TOKEN também
# - Name: TINY_API_TOKEN  
# - Value: [seu token tiny]
```

## 🔄 Dependabot

Atualização automática semanal de:
- Dependências Python (backend)
- Dependências npm (frontend)
- GitHub Actions

## 📊 Badges

Adicione ao README principal:

```markdown
![Tests](https://github.com/seu-usuario/dashboard-v2/actions/workflows/test.yml/badge.svg)
![Deploy](https://github.com/seu-usuario/dashboard-v2/actions/workflows/deploy.yml/badge.svg)
```