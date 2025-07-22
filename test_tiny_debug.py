#!/usr/bin/env python3
"""
Debug detalhado da API do Tiny
"""
import httpx
import json
from urllib.parse import urlencode
import asyncio

TINY_TOKEN = "fe8abfe8be5255938b70cb7f671c723ab21af6e1102f6cd730a93228d78bc5bb"

async def buscar_produto_detalhado():
    """Busca produto e mostra estrutura completa"""
    print("=== Buscando produto PH-510 ===")
    
    url = "https://api.tiny.com.br/api2/produtos.pesquisa.php"
    data = {
        "token": TINY_TOKEN,
        "pesquisa": "PH-510",
        "formato": "JSON"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            content=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        result = response.json()
        if result.get('retorno', {}).get('status') == 'OK':
            produtos = result['retorno'].get('produtos', [])
            if produtos:
                produto = produtos[0]['produto']
                print(f"Produto encontrado:")
                print(json.dumps(produto, indent=2, ensure_ascii=False))
                return produto
        
        return None

async def obter_produto_por_id(produto_id):
    """Obtém produto específico pelo ID"""
    print(f"\n=== Obtendo produto por ID: {produto_id} ===")
    
    url = "https://api.tiny.com.br/api2/produto.obter.php"
    data = {
        "token": TINY_TOKEN,
        "id": produto_id,
        "formato": "JSON"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            content=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        result = response.json()
        print(f"Resposta obter produto:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get('retorno', {}).get('status') == 'OK':
            return result['retorno'].get('produto')
        
        return None

async def testar_com_precounitario():
    """Testa com precoUnitario conforme documentação"""
    print("\n=== Teste com precoUnitario ===")
    
    estoque_data = {
        "idProduto": "893434458",
        "tipo": "E",
        "data": "2025-07-22 13:03:00",
        "quantidade": "1",
        "precoUnitario": "25.78",  # Adicionando preço unitário
        "observacoes": "Teste com preço unitário",
        "deposito": "deposito central"
    }
    
    data = {
        "token": TINY_TOKEN,
        "estoque": json.dumps(estoque_data),
        "formato": "JSON"
    }
    
    url = "https://api.tiny.com.br/api2/produto.atualizar.estoque.php"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            content=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

async def main():
    """Função principal de debug"""
    # 1. Buscar produto
    produto = await buscar_produto_detalhado()
    
    if produto:
        produto_id = produto.get('id')
        
        # 2. Obter produto por ID para confirmar
        await obter_produto_por_id(produto_id)
        
        # 3. Testar atualização com preço
        await testar_com_precounitario()

if __name__ == "__main__":
    asyncio.run(main())