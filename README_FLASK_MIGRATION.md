# Migração para Flask + React

## ✅ O que foi feito

### 1. Backend Flask criado em `/flask-backend/`
- ✅ Estrutura organizada com blueprints
- ✅ Integração com Redis (mesma lógica do FastAPI)
- ✅ Integração com Tiny API (totalmente funcional)
- ✅ Endpoints para gerenciar estoque:
  - `GET /api/v2/estoque/produto/{codigo}` - Buscar produto
  - `POST /api/v2/estoque/ajustar` - Ajuste genérico
  - `POST /api/v2/estoque/ph510/adicionar` - Adicionar +1 ao PH-510
  - `POST /api/v2/estoque/ph510/remover` - Remover -1 do PH-510

### 2. Frontend React criado em `/react-frontend/`
- ✅ Interface simples e limpa
- ✅ Componente GestaoEstoque para o PH-510
- ✅ Botões para adicionar/remover estoque
- ✅ Atualização em tempo real
- ✅ Notificações toast para feedback

### 3. Infraestrutura
- ✅ Docker Compose configurado
- ✅ Dockerfile para ambos os serviços
- ✅ Script de teste automatizado

## 🚀 Como executar

### Opção 1: Docker Compose (recomendado)
```bash
# Na raiz do projeto
docker-compose up
```
- Backend Flask: http://localhost:8000
- Frontend React: http://localhost:3000

### Opção 2: Manualmente

**Backend Flask:**
```bash
cd flask-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python app.py
```

**Frontend React:**
```bash
cd react-frontend
npm install
npm start
```

## 🧪 Como testar

1. Execute o script de teste:
```bash
python test_flask_app.py
```

2. Ou teste manualmente:
   - Acesse http://localhost:3000
   - Clique em "Adicionar +1" para aumentar estoque
   - Clique em "Remover -1" para diminuir estoque
   - Clique em "Atualizar Dados" para sincronizar

## 📊 Vantagens do Flask sobre FastAPI

1. **Mais simples** - Menos complexidade, menos abstrações
2. **Mais maduro** - Existe há mais tempo, mais estável
3. **Melhor documentação** - Mais exemplos e tutoriais
4. **Menos dependências** - Não precisa de Pydantic, async/await é opcional
5. **Debug mais fácil** - Erros mais claros e diretos

## 🔄 Próximos passos

1. Migrar outras funcionalidades (notas, pedidos, etc.)
2. Adicionar autenticação JWT
3. Implementar WebSockets para updates em tempo real
4. Adicionar testes automatizados
5. Configurar CI/CD

## ⚠️ Notas importantes

- O arquivo `.env` foi copiado do projeto FastAPI
- Redis continua funcionando da mesma forma
- A integração com Tiny API está 100% funcional
- O cache de produtos funciona por 5 minutos

## 🗑️ Limpeza (opcional)

Para remover o código FastAPI antigo após validar que Flask funciona:
```bash
# CUIDADO: Só execute após ter certeza!
rm -rf dashboard-v2/backend/
rm -rf teste1/ teste2/ teste3/ teste4/ teste5/
```