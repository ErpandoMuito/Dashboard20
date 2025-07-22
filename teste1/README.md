# Dashboard Minimalista - Controle de Estoque

Solução ultra simples. Apenas o essencial.

## O que faz

1. Busca produto por código
2. Mostra estoque atual
3. Permite entrada de estoque
4. Atualiza no Tiny

## Como rodar

```bash
# 1. Configure o token
cp .env.example .env
# Edite .env e adicione seu TINY_API_TOKEN

# 2. Execute
./run.sh
```

## Uso

1. Abra http://localhost:8000 no navegador
2. Digite o código do produto
3. Clique em "Buscar Produto"
4. Digite a quantidade para entrada
5. Clique em "Confirmar Entrada"

## Arquitetura

- **main.py**: API com 2 endpoints
- **index.html**: Interface web simples
- **Sem Redis**: Direto no Tiny
- **Sem cache**: Sempre dados atualizados
- **Sem complexidade**: Apenas o necessário

## Endpoints

- `GET /api/v2/estoque/produto/{codigo}` - Busca produto
- `POST /api/v2/estoque/entrada` - Entrada de estoque

Minimalista. Funcional. Sem firulas.