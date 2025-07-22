# Dashboard Estoque - Frontend React

Interface simples para gerenciamento de estoque do produto PH-510.

## Instalação

1. Instalar dependências:
```bash
npm install
```

2. Configurar API (opcional):
```bash
# Por padrão conecta em http://localhost:8000
# Para mudar, criar arquivo .env:
echo "REACT_APP_API_URL=http://seu-backend:8000" > .env
```

3. Executar:
```bash
npm start
```

## Funcionalidades

- Visualizar estoque atual do PH-510
- Adicionar +1 unidade
- Remover -1 unidade
- Atualizar dados em tempo real

## Build para produção

```bash
npm run build
```

Os arquivos estarão na pasta `build/`.