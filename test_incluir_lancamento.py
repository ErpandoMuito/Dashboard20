#!/usr/bin/env python3
"""
Teste usando lancamento.estoque.incluir ao invés de produto.atualizar.estoque
"""
import httpx
import json
from urllib.parse import urlencode
import asyncio
from datetime import datetime

TINY_TOKEN = "fe8abfe8be5255938b70cb7f671c723ab21af6e1102f6cd730a93228d78bc5bb"

async def incluir_lancamento_estoque():
    """Tenta incluir lançamento de estoque"""
    print("=== Teste lancamento.estoque.incluir ===")
    
    lancamento_data = {
        "id_produto": "893434458",
        "tipo": "E",  # Entrada
        "quantidade": "1",
        "observacoes": "Teste de lançamento de estoque",
        "data": datetime.now().strftime("%d/%m/%Y"),
        "hora": datetime.now().strftime("%H:%M")
    }
    
    data = {
        "token": TINY_TOKEN,
        "lancamento": json.dumps(lancamento_data),
        "formato": "JSON"
    }
    
    url = "https://api.tiny.com.br/api2/lancamento.estoque.incluir.php"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            content=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        try:
            result = response.json()
            print(f"Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except:
            print(f"Resposta texto: {response.text}")

async def testar_xml_format():
    """Testa formato XML puro"""
    print("\n=== Teste XML Format ===")
    
    estoque_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<estoque>
    <idProduto>893434458</idProduto>
    <tipo>E</tipo>
    <data>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</data>
    <quantidade>1</quantidade>
    <precoUnitario>25.78</precoUnitario>
    <observacoes>Teste XML</observacoes>
    <deposito>deposito central</deposito>
</estoque>"""
    
    data = {
        "token": TINY_TOKEN,
        "estoque": estoque_xml.strip(),
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
        result = response.json()
        print(f"Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")

async def buscar_config_api():
    """Busca configurações da conta"""
    print("\n=== Verificando configurações ===")
    
    urls_config = [
        "conta.obter.php",
        "info.obter.php"
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint in urls_config:
            print(f"\nTestando {endpoint}...")
            
            data = {
                "token": TINY_TOKEN,
                "formato": "JSON"
            }
            
            url = f"https://api.tiny.com.br/api2/{endpoint}"
            
            try:
                response = await client.post(
                    url,
                    content=urlencode(data),
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if result.get('retorno', {}).get('status') == 'OK':
                            print(f"✓ Sucesso em {endpoint}")
                            # Procurar informações sobre estoque
                            info = json.dumps(result, indent=2, ensure_ascii=False)
                            if 'estoque' in info.lower():
                                print("Encontrada configuração de estoque:")
                                print(info[:500] + "...")
                    except:
                        pass
            except Exception as e:
                print(f"Erro em {endpoint}: {e}")

async def main():
    """Função principal"""
    await incluir_lancamento_estoque()
    await asyncio.sleep(2)
    await testar_xml_format()
    await asyncio.sleep(2)
    await buscar_config_api()

if __name__ == "__main__":
    asyncio.run(main())