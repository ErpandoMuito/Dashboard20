#!/usr/bin/env python3
"""
Teste sem campo depósito
"""
import httpx
from urllib.parse import urlencode
import asyncio
import json

TOKEN = "fe8abfe8be5255938b70cb7f671c723ab21af6e1102f6cd730a93228d78bc5bb"
URL = "https://api.tiny.com.br/api2/produto.atualizar.estoque.php"

async def teste_sem_deposito():
    """Teste sem campo depósito"""
    print("=== Teste SEM depósito ===")
    
    estoque_obj = {
        "estoque": {
            "idProduto": "893434458",
            "tipo": "E",
            "data": "2025-07-22 13:03:00",
            "quantidade": "1",
            "precoUnitario": "25.78",
            "observacoes": "Adicionando 1 unidade ao PH-510"
        }
    }
    
    estoque_json = json.dumps(estoque_obj)
    print(f"Enviando: {estoque_json}")
    
    data = {
        "token": TOKEN,
        "estoque": estoque_json,
        "formato": "JSON"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            URL,
            content=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # Se sucesso, buscar estoque atualizado
        if result.get('retorno', {}).get('status') == 'OK':
            print("\n✅ SUCESSO! Verificando novo saldo...")
            
            # Buscar estoque
            url_estoque = "https://api.tiny.com.br/api2/produto.obter.estoque.php"
            data_estoque = {
                "token": TOKEN,
                "id": "893434458",
                "formato": "JSON"
            }
            
            resp_estoque = await client.post(
                url_estoque,
                content=urlencode(data_estoque),
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            estoque_result = resp_estoque.json()
            if estoque_result.get('retorno', {}).get('status') == 'OK':
                novo_saldo = estoque_result['retorno']['produto']['saldo']
                print(f"Novo saldo: {novo_saldo} unidades")

if __name__ == "__main__":
    asyncio.run(teste_sem_deposito())