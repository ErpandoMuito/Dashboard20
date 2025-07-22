#!/usr/bin/env python3
"""
Teste com formato EXATO da documentação
"""
import httpx
from urllib.parse import urlencode
import asyncio

TOKEN = "fe8abfe8be5255938b70cb7f671c723ab21af6e1102f6cd730a93228d78bc5bb"
URL = "https://api.tiny.com.br/api2/produto.atualizar.estoque.php"

async def teste_formato_documentacao():
    """Usa o formato EXATO da documentação"""
    print("=== Teste Formato Documentação ===")
    
    # Formato EXATO da documentação
    estoque = '{"estoque":{"idProduto":"12345888","tipo":"E","data":"2017-03-27 13:03:00","quantidade":"7","precoUnitario":"25.78","observacoes":"observação do lançamento","deposito":"deposito central"}}'
    
    # Substituindo o ID pelo nosso
    estoque = estoque.replace('"12345888"', '"893434458"')
    estoque = estoque.replace('"quantidade":"7"', '"quantidade":"1"')
    estoque = estoque.replace('2017-03-27', '2025-07-22')
    
    print(f"Enviando: {estoque}")
    
    data = {
        "token": TOKEN,
        "estoque": estoque,
        "formato": "JSON"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            URL,
            content=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        import json
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

async def teste_sem_wrapper():
    """Teste sem o wrapper 'estoque'"""
    print("\n=== Teste sem wrapper ===")
    
    estoque = '{"idProduto":"893434458","tipo":"E","data":"2025-07-22 13:03:00","quantidade":"1","precoUnitario":"25.78","observacoes":"teste sem wrapper","deposito":"deposito central"}'
    
    print(f"Enviando: {estoque}")
    
    data = {
        "token": TOKEN,
        "estoque": estoque,
        "formato": "JSON"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            URL,
            content=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        import json
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

async def main():
    await teste_formato_documentacao()
    await asyncio.sleep(2)
    await teste_sem_wrapper()

if __name__ == "__main__":
    asyncio.run(main())