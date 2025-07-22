#!/usr/bin/env python3
"""
Lista produtos para verificar formato de IDs
"""
import httpx
import json
from urllib.parse import urlencode
import asyncio

TINY_TOKEN = "fe8abfe8be5255938b70cb7f671c723ab21af6e1102f6cd730a93228d78bc5bb"

async def listar_produtos():
    """Lista produtos"""
    print("=== Listando produtos ===")
    
    url = "https://api.tiny.com.br/api2/produtos.pesquisa.php"
    data = {
        "token": TINY_TOKEN,
        "formato": "JSON",
        "pagina": "1"
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
            print(f"Total de produtos: {len(produtos)}")
            
            # Mostrar primeiros 5 produtos
            for i, prod in enumerate(produtos[:5]):
                p = prod['produto']
                print(f"\n{i+1}. {p.get('nome')}")
                print(f"   ID: {p.get('id')} (tipo: {type(p.get('id'))})")
                print(f"   Código: {p.get('codigo')}")
                
            # Procurar PH-510
            for prod in produtos:
                p = prod['produto']
                if p.get('codigo') == 'PH-510':
                    print(f"\n=== PRODUTO PH-510 ENCONTRADO ===")
                    print(json.dumps(p, indent=2, ensure_ascii=False))
                    break

async def testar_obter_saldo():
    """Testa obter saldo de diversos produtos"""
    print("\n\n=== Testando obter saldo ===")
    
    # IDs para testar
    ids_teste = ["893434458", "123", "1", "999999999"]
    
    url = "https://api.tiny.com.br/api2/produto.obter.estoque.php"
    
    async with httpx.AsyncClient() as client:
        for id_produto in ids_teste:
            print(f"\nTestando ID: {id_produto}")
            
            data = {
                "token": TINY_TOKEN,
                "id": id_produto,
                "formato": "JSON"
            }
            
            response = await client.post(
                url,
                content=urlencode(data),
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            result = response.json()
            if result.get('retorno', {}).get('status') == 'OK':
                print(f"✓ Sucesso - Saldo: {result['retorno'].get('produto', {}).get('saldo')}")
            else:
                print(f"✗ Erro: {result}")

async def main():
    await listar_produtos()
    await testar_obter_saldo()

if __name__ == "__main__":
    asyncio.run(main())