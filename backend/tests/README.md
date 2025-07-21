# 🧪 Testes Automatizados - Dashboard Estoque v2.0

## 📋 Visão Geral

Esta suíte de testes garante a qualidade e confiabilidade do sistema de entrada de estoque, com especial atenção para **não deixar dados residuais no Tiny ERP**.

## 🏗️ Estrutura dos Testes

```
tests/
├── unit/           # Testes unitários (rápidos, sem dependências)
├── integration/    # Testes de integração (API + Redis mock)
├── e2e/            # Testes end-to-end (API real do Tiny)
├── fixtures/       # Dados de teste compartilhados
└── conftest.py     # Configurações e fixtures globais
```

## 🚀 Como Executar

### Instalação das Dependências
```bash
cd backend
pip install -r requirements-test.txt
```

### Executar Todos os Testes (exceto E2E)
```bash
pytest -v
# ou
./tests/run_tests.sh
```

### Executar por Categoria

#### 🔬 Testes Unitários
```bash
pytest -m unit -v
# ou
./tests/run_tests.sh unit
```

#### 🔗 Testes de Integração
```bash
pytest -m integration -v
# ou
./tests/run_tests.sh integration
```

#### 🌐 Testes E2E (CUIDADO!)
```bash
# Requer confirmação - altera dados reais no Tiny
RUN_E2E_TESTS=true pytest -m e2e -v
# ou
./tests/run_tests.sh e2e
```

### 📊 Relatório de Cobertura
```bash
./tests/run_tests.sh coverage
# Abre: htmlcov/index.html
```

## ⚠️ Testes E2E - Segurança

Os testes E2E implementam um **sistema de reversão automática**:

1. **TinyTestManager**: Gerencia todas as alterações
2. **Registro de operações**: Cada entrada é registrada
3. **Reversão automática**: Ao final, faz saídas equivalentes
4. **Produto de teste**: Usa produto específico (PH-999)

### Exemplo de Uso Seguro:
```python
async with TinyTestManager() as manager:
    # Faz entrada de 100 unidades
    await manager.entrada_estoque("PH-999", 100)
    
    # Testes...
    
    # Ao sair do contexto, automaticamente faz saída de 100 unidades
```

## 🔧 Fixtures Principais

### `mock_tiny_client`
Mock completo da API Tiny para testes sem acesso real.

### `tiny_test_manager`
Manager para testes E2E com reversão automática.

### `test_client`
Cliente HTTP assíncrono para testar endpoints.

### `redis_client`
Cliente Redis isolado para testes (usa DB 15).

## 📝 Convenções

1. **Sempre use mocks** para testes unitários e integração
2. **Produto PH-999** exclusivo para testes E2E
3. **Quantidades pequenas** nos testes E2E (max 50)
4. **Descrições identificadas** como "Teste automatizado"
5. **Limpeza garantida** via context managers

## 🎯 Metas de Cobertura

- **Unitários**: 90%+ de cobertura
- **Integração**: Todos os endpoints
- **E2E**: Fluxos críticos apenas

## 🚨 Troubleshooting

### "Produto não encontrado" nos testes E2E
Certifique-se que o produto PH-999 existe no Tiny.

### Testes E2E não executam
Defina a variável: `export RUN_E2E_TESTS=true`

### Redis connection refused
Inicie o Redis local: `redis-server`

### Reversão falhou
Verifique manualmente no Tiny e ajuste via interface se necessário.

## 🔄 CI/CD

Para integração contínua, use:
```yaml
- name: Run tests
  run: |
    pytest -v -m "not e2e" --cov=app
```

**Nunca execute testes E2E em CI/CD automático!**