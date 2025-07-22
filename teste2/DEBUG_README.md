# 🔍 DASHBOARD DEBUG - LOGS SÃO VIDA!

Este é o projeto `/teste2` com foco TOTAL em debugging e visibilidade.

## 🚀 Como Executar

```bash
cd teste2
./run.sh
```

## 📋 O que este sistema faz?

### Backend (FastAPI)
- **LOGA TUDO**: Cada requisição, resposta, erro, variável
- **Salva logs em arquivo**: `debug.log` com todos os detalhes
- **Middleware de logging**: Captura TODAS as requisições HTTP
- **Tratamento de erros detalhado**: Stack trace completo

### Frontend (HTML/JS)
- **Console integrado**: Pressione o botão "Console" para ver logs
- **Logs em tempo real**: Aparecem na tela conforme acontecem
- **Métricas ao vivo**: Contadores de chamadas, erros, uptime
- **Testes com um clique**: Botões para testar cada componente

## 🛠️ Endpoints de Debug

### `/debug/env`
- Mostra TODAS as variáveis de ambiente
- Mascara senhas e tokens automaticamente
- Inclui informações do Python e diretório

### `/debug/redis`
- Testa conexão com Redis
- Mostra versão, memória, clientes conectados
- Faz teste de escrita/leitura
- Conta total de chaves

### `/debug/tiny`
- Testa API do Tiny ERP
- Mostra se token está configurado
- Faz chamada real para validar
- Exibe resposta completa

### `/debug/static`
- Lista todos os arquivos estáticos
- Mostra tamanho e data de modificação
- Útil para verificar deploy

### `/debug/logs`
- Retorna todos os logs de startup
- Histórico das últimas 100 chamadas API
- Inclui duração, status, headers

### `/debug/test-error`
- Gera erro proposital
- Mostra como erros são tratados
- Retorna stack trace completo

## 🎯 Interface de Debug

Acesse http://localhost:8000/static/index.html para:

1. **Painel de Controle**
   - Botão "TESTAR TUDO" executa todos os testes
   - Cada botão mostra logs em tempo real
   - Resultados aparecem formatados em JSON

2. **Status dos Serviços**
   - Indicadores visuais (verde/vermelho/amarelo)
   - Atualização automática a cada 5 segundos
   - Mostra API, Redis, Tiny

3. **Métricas em Tempo Real**
   - Contador de chamadas API
   - Logs de startup
   - Contador de erros
   - Uptime do sistema

4. **Console JavaScript**
   - Captura TODOS os console.log()
   - Mostra erros em vermelho
   - Warnings em amarelo
   - Timestamps em cada log

## 🔧 Arquivos de Log

### `debug.log`
- Criado automaticamente pelo backend
- Contém TODOS os logs do servidor
- Formato: timestamp | level | module | function:line | message

### Console do Browser
- Abra o DevTools (F12)
- Todos os logs são duplicados lá
- Útil para debug do frontend

## 📊 Monitoramento

### No Terminal
```bash
# Ver logs em tempo real
tail -f debug.log

# Filtrar apenas erros
grep ERROR debug.log

# Contar requisições
grep "REQUEST:" debug.log | wc -l
```

### No Browser
- Botão "Console" mostra logs capturados
- Seção "Logs em Tempo Real" atualiza sozinha
- JSON viewer mostra respostas formatadas

## 🚨 Debugging Tips

1. **Sempre verifique o console do browser**
   - Erros de JavaScript aparecem lá
   - Network tab mostra requisições

2. **Use o endpoint /debug/logs**
   - Mostra histórico completo
   - Inclui requisições que falharam

3. **Teste individual vs completo**
   - Use botões individuais para isolar problemas
   - "TESTAR TUDO" para visão geral

4. **Arquivo debug.log**
   - Mais detalhado que a interface
   - Inclui logs internos do Python

## 🔴 Se algo der errado

1. **Redis não conecta?**
   ```bash
   # Verificar se está rodando
   redis-cli ping
   
   # Iniciar manualmente
   redis-server
   ```

2. **Tiny API falha?**
   - Verifique o token em .env
   - Endpoint /debug/env mostra se está configurado

3. **Frontend não carrega?**
   - Verifique se backend está em http://localhost:8000
   - Olhe o console do browser para erros

## 💡 Filosofia: LOGS SÃO VIDA!

- Se não está logado, não aconteceu
- Mais logs = menos bugs
- Visibilidade total = debug fácil
- Erros devem gritar, não sussurrar

---

**LEMBRE-SE**: Este é um ambiente de DEBUG. Não use em produção!