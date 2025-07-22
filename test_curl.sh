#!/bin/bash

TOKEN="fe8abfe8be5255938b70cb7f671c723ab21af6e1102f6cd730a93228d78bc5bb"
URL="https://api.tiny.com.br/api2/produto.atualizar.estoque.php"

# Teste 1: JSON com ID como número
echo "=== Teste 1: JSON com ID número ==="
ESTOQUE_JSON='{"idProduto":893434458,"tipo":"E","quantidade":1.00,"data":"2025-07-22 13:03:00","precoUnitario":25.78,"observacoes":"Teste cURL","deposito":"deposito central"}'

curl -X POST "$URL" \
  -d "token=$TOKEN" \
  -d "estoque=$ESTOQUE_JSON" \
  -d "formato=JSON" | jq .

echo -e "\n\n=== Teste 2: XML ==="
ESTOQUE_XML='<estoque><idProduto>893434458</idProduto><tipo>E</tipo><quantidade>1</quantidade><data>2025-07-22 13:03:00</data><precoUnitario>25.78</precoUnitario><observacoes>Teste XML</observacoes><deposito>deposito central</deposito></estoque>'

curl -X POST "$URL" \
  -d "token=$TOKEN" \
  -d "estoque=$ESTOQUE_XML" \
  -d "formato=JSON" | jq .