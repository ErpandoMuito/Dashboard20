#!/bin/bash

# Defina a URL base da sua API
BASE_URL="https://dashboard-estoque-v2.fly.dev"

# Código do produto para o teste
CODIGO_PRODUTO="PH-510"

echo "Iniciando teste de fluxo de estoque para o produto: $CODIGO_PRODUTO"
echo "URL da API: $BASE_URL"

# 1. Consultar estoque inicial
echo "\n--- 1. Consultando estoque inicial de $CODIGO_PRODUTO ---"
curl -s -X GET "$BASE_URL/api/v2/estoque/produto/$CODIGO_PRODUTO" | python3 -m json.tool
echo "\n"

# 2. Adicionar 1 unidade ao estoque
echo "--- 2. Adicionando 1 unidade ao estoque de $CODIGO_PRODUTO ---"
curl -s -X POST "$BASE_URL/api/v2/estoque/entrada" \
-H "Content-Type: application/json" \
-d '{
  "codigo_produto": "'"$CODIGO_PRODUTO"'",
  "quantidade": 1,
  "descricao": "Teste de adicao de estoque"
}' | python3 -m json.tool
echo "\n"

# 3. Consultar estoque após adição
echo "--- 3. Consultando estoque de $CODIGO_PRODUTO apos adicao ---"
curl -s -X GET "$BASE_URL/api/v2/estoque/produto/$CODIGO_PRODUTO" | python3 -m json.tool
echo "\n"

# 4. Remover 1 unidade do estoque
echo "--- 4. Removendo 1 unidade do estoque de $CODIGO_PRODUTO ---"
curl -s -X POST "$BASE_URL/api/v2/estoque/saida" \
-H "Content-Type: application/json" \
-d '{
  "codigo_produto": "'"$CODIGO_PRODUTO"'",
  "quantidade": 1,
  "descricao": "Teste de remocao de estoque"
}' | python3 -m json.tool
echo "\n"

# 5. Consultar estoque final
echo "--- 5. Consultando estoque final de $CODIGO_PRODUTO ---"
curl -s -X GET "$BASE_URL/api/v2/estoque/produto/$CODIGO_PRODUTO" | python3 -m json.tool
echo "\n"

echo "Teste de fluxo de estoque concluído."
