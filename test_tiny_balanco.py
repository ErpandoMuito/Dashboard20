#!/usr/bin/env python3
"""
Teste com tipo Balanço
"""
import httpx
import json
from urllib.parse import urlencode
import asyncio

TINY_TOKEN = "fe8abfe8be5255938b70cb7f671c723ab21af6e1102f6cd730a93228d78bc5bb"

async def testar_balanco():
    """Testa com tipo B (Balanço)"""
    print("=== Teste tipo Balanço ===")
    
    # Primeiro obter estoque atual
    url_estoque = "https://api.tiny.com.br/api2/produto.obter.estoque.php"
    data_estoque = {
        "token": TINY_TOKEN,
        "id": "893434458",
        "formato": "JSON"
    }
    
    async with httpx.AsyncClient() as client:
        # Obter saldo atual
        response = await client.post(
            url_estoque,
            content=urlencode(data_estoque),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        result = response.json()
        saldo_atual = 0
        
        if result.get('retorno', {}).get('status') == 'OK':
            saldo_str = result['retorno'].get('produto', {}).get('saldo', '0')
            saldo_atual = int(float(saldo_str))
            print(f"Saldo atual: {saldo_atual}")
        
        # Tentar balanço
        novo_saldo = saldo_atual + 1
        
        estoque_data = {
            "idProduto": "893434458",
            "tipo": "B",  # Balanço
            "quantidade": str(novo_saldo),  # No balanço, quantidade é o saldo final
            "observacoes": f"Balanço - ajuste de {saldo_atual} para {novo_saldo}"
        }
        
        data = {
            "token": TINY_TOKEN,
            "estoque": json.dumps(estoque_data),
            "formato": "JSON"
        }
        
        url = "https://api.tiny.com.br/api2/produto.atualizar.estoque.php"
        
        response = await client.post(
            url,
            content=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

async def testar_sem_deposito():
    """Testa sem especificar depósito"""
    print("\n=== Teste sem depósito ===")
    
    estoque_data = {
        "idProduto": "893434458",
        "tipo": "E",
        "quantidade": "1",
        "observacoes": "Teste sem depósito"
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

async def listar_depositos():
    """Lista depósitos disponíveis"""
    print("\n=== Listando depósitos ===")
    
    url = "https://api.tiny.com.br/api2/depositos.pesquisa.php"
    data = {
        "token": TINY_TOKEN,
        "formato": "JSON"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            content=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        try:
            result = response.json()
            if result.get('retorno', {}).get('status') == 'OK':
                depositos = result['retorno'].get('depositos', [])
                for dep in depositos:
                    print(f"Depósito: {dep.get('deposito', {})}")
            else:
                print(f"Erro ao listar depósitos: {result}")
        except Exception as e:
            print(f"Erro: {e}")
            print(f"Resposta: {response.text}")

async def main():
    """Função principal"""
    # await listar_depositos()
    # await asyncio.sleep(2)
    await testar_balanco()
    await asyncio.sleep(2)
    await testar_sem_deposito()

if __name__ == "__main__":
    asyncio.run(main())