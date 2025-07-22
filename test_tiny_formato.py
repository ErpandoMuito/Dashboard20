#!/usr/bin/env python3
"""
Teste de diferentes formatos para API do Tiny
"""
import httpx
import json
from urllib.parse import urlencode
import asyncio

TINY_TOKEN = "fe8abfe8be5255938b70cb7f671c723ab21af6e1102f6cd730a93228d78bc5bb"
TINY_URL = "https://api.tiny.com.br/api2/produto.atualizar.estoque.php"
PRODUTO_ID = "893434458"

async def testar_formato_1():
    """Formato com JSON serializado"""
    print("=== Teste Formato 1: JSON serializado ===")
    
    estoque_data = {
        "idProduto": PRODUTO_ID,
        "tipo": "E",
        "data": "2025-07-22 13:03:00",
        "quantidade": "1",
        "deposito": "deposito central",
        "observacoes": "Teste formato 1"
    }
    
    data = {
        "token": TINY_TOKEN,
        "estoque": json.dumps(estoque_data),
        "formato": "JSON"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TINY_URL,
            content=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
async def testar_formato_2():
    """Formato com XML"""
    print("\n=== Teste Formato 2: XML ===")
    
    estoque_xml = f"""<estoque>
    <idProduto>{PRODUTO_ID}</idProduto>
    <tipo>E</tipo>
    <data>2025-07-22 13:03:00</data>
    <quantidade>1</quantidade>
    <deposito>deposito central</deposito>
    <observacoes>Teste formato 2 XML</observacoes>
</estoque>"""
    
    data = {
        "token": TINY_TOKEN,
        "estoque": estoque_xml,
        "formato": "JSON"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TINY_URL,
            content=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

async def testar_formato_3():
    """Formato simples com ID direto"""
    print("\n=== Teste Formato 3: ID direto ===")
    
    estoque_data = {
        "id": PRODUTO_ID,  # Tentar 'id' ao invés de 'idProduto'
        "tipo": "E",
        "quantidade": "1",
        "deposito": "Geral",
        "observacoes": "Teste formato 3"
    }
    
    data = {
        "token": TINY_TOKEN,
        "estoque": json.dumps(estoque_data),
        "formato": "JSON"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TINY_URL,
            content=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

async def main():
    """Testa diferentes formatos"""
    await testar_formato_1()
    await asyncio.sleep(2)
    await testar_formato_2()
    await asyncio.sleep(2)
    await testar_formato_3()

if __name__ == "__main__":
    asyncio.run(main())