# Sistema de Debug - DashboardNext v2.0

## Visão Geral

Este é um sistema de debug completo para o DashboardNext, com logging extensivo e interface web interativa. O sistema foi projetado com o lema "LOGS SÃO VIDA!" para facilitar a identificação e resolução de problemas.

## Características

- **Backend FastAPI** com logging detalhado
- **Interface Web** interativa para visualização de logs e testes
- **Endpoints de Debug** para verificar status de todos os serviços
- **Rotação de Logs** automática para evitar problemas de espaço
- **Testes Automatizados** com script Python colorido

## Arquitetura

```
teste2/
├── backend.py          # Servidor FastAPI com endpoints de debug
├── static/
│   └── index.html     # Interface web interativa
├── test_debug.py      # Script de teste do sistema
├── requirements.txt   # Dependências Python
├── run.sh            # Script para iniciar o servidor
├── README.md         # Este arquivo
└── DEBUG_README.md   # Documentação técnica detalhada
```

## Correções Implementadas

### 1. Bug na Atualização de Métricas
- **Problema**: O frontend tentava acessar `logs.total_calls` mas o backend retornava `total_api_calls`
- **Solução**: Atualizado o código JavaScript para usar os nomes corretos dos campos

### 2. Carregamento de Variáveis de Ambiente
- **Problema**: O backend não verificava se o arquivo `.env` existia
- **Solução**: Adicionada verificação e tratamento de erro para carregamento do `.env`

### 3. Verificação de Servidor no Script de Teste
- **Problema**: O script de teste não verificava se o servidor estava rodando
- **Solução**: Adicionada função `check_server_running()` antes de executar os testes

### 4. Limites de Memória
- **Melhoria**: Mantidos limites razoáveis para logs em memória (1000 para startup, 500 para API)

## Como Usar

### 1. Instalação Rápida

```bash
# No diretório raiz do projeto
./teste2
```

Este comando executará automaticamente:
- Verificação de dependências
- Inicialização do Redis (se necessário)
- Instalação de pacotes Python
- Inicialização do servidor
- Execução de testes automatizados

### 2. Inicialização Manual

```bash
cd dashboard-v2/teste2
./run.sh
```

### 3. Execução de Testes

```bash
cd dashboard-v2/teste2
python3 test_debug.py
```

### 4. Acesso à Interface Web

Após iniciar o servidor, acesse:
- Interface Debug: http://localhost:8000/static/index.html
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## Endpoints de Debug

### `/debug/env`
Mostra todas as variáveis de ambiente (com máscaras para senhas)

### `/debug/redis`
Testa conexão com Redis e mostra informações

### `/debug/tiny`
Testa conexão com API Tiny

### `/debug/static`
Lista arquivos estáticos disponíveis

### `/debug/logs`
Retorna logs de startup e histórico de chamadas

### `/debug/test-error`
Endpoint para testar tratamento de erros

## Recursos da Interface Web

- **Painel de Controle**: Botões para executar testes
- **Status dos Serviços**: Indicadores visuais em tempo real
- **Métricas**: Contadores de chamadas, logs e erros
- **Logs em Tempo Real**: Visualização de logs conforme são gerados
- **Console JavaScript**: Toggle para ver logs do browser

## Configuração

### Arquivo `.env`

Crie um arquivo `.env` com:

```env
# Redis
REDIS_URL=redis://localhost:6379

# Tiny API
TINY_API_TOKEN=seu_token_aqui
```

### Requisitos

- Python 3.8+
- Redis
- pip

### Dependências Python

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
redis==5.0.1
httpx==0.25.1
python-multipart==0.0.6
python-dotenv==1.0.0
```

## Monitoramento

### Logs em Tempo Real

```bash
# Ver logs do servidor
tail -f dashboard-v2/teste2/debug.log

# Ver logs do Redis
redis-cli MONITOR
```

### Métricas

A interface web mostra:
- Total de chamadas API
- Total de logs de startup
- Contagem de erros
- Uptime do sistema

## Troubleshooting

### Redis não conecta
1. Verifique se o Redis está instalado: `redis-cli --version`
2. Inicie o Redis: `redis-server --daemonize yes`
3. Teste conexão: `redis-cli ping`

### Porta 8000 em uso
1. Encontre o processo: `lsof -i :8000`
2. Mate o processo: `kill -9 <PID>`
3. Ou mude a porta no `backend.py`

### Módulos Python não encontrados
1. Ative o ambiente virtual: `source venv/bin/activate`
2. Reinstale dependências: `pip install -r requirements.txt`

## Desenvolvimento

### Adicionando Novos Endpoints

```python
@app.get("/debug/novo-endpoint")
async def debug_novo():
    logger.info("Novo endpoint chamado")
    return {"status": "ok"}
```

### Adicionando Logs

```python
# Use a função log_and_store para logs que aparecem na UI
log_and_store("Mensagem importante", "INFO")

# Use logger para logs apenas no arquivo
logger.debug("Detalhe técnico")
```

## Performance

- Logs são rotacionados automaticamente (máx 10MB)
- Limites de memória para evitar vazamentos
- Debounce nos botões da interface para evitar spam
- Timeout de 30s nas requisições HTTP

## Segurança

- Senhas e tokens são mascarados nos logs
- CORS configurado (ajustar para produção)
- Validação de entrada em todos os endpoints

---

**Lembre-se**: LOGS SÃO VIDA! 🔍