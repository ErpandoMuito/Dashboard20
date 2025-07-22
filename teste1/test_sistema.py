#!/usr/bin/env python3
"""
Teste do sistema de estoque minimalista
"""
import httpx
import asyncio
import os
import json
from datetime import datetime

# URL da API (ajustar conforme necessário)
API_URL = os.getenv("API_URL", "http://localhost:8000")

async def test_health():
    """Testa se a API está rodando"""
    print("1. Testando health check...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/api/v2/health")
            data = response.json()
            print(f"   ✓ Status: {data['status']}")
            print(f"   ✓ Minimalista: {data['minimalista']}")
            return True
        except Exception as e:
            print(f"   ✗ Erro: {e}")
            return False

async def test_buscar_produto(codigo="PH-510"):
    """Testa busca de produto"""
    print(f"\n2. Buscando produto {codigo}...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/api/v2/estoque/produto/{codigo}")
            if response.status_code == 200:
                produto = response.json()
                print(f"   ✓ Nome: {produto['nome']}")
                print(f"   ✓ Estoque: {produto['estoque']} {produto['unidade']}")
                return produto
            else:
                print(f"   ✗ Erro {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"   ✗ Erro: {e}")
            return None

async def test_entrada_estoque(codigo="PH-510", quantidade=10):
    """Testa entrada de estoque"""
    print(f"\n3. Testando entrada de {quantidade} unidades...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/api/v2/estoque/entrada",
                json={
                    "codigo": codigo,
                    "quantidade": quantidade,
                    "observacao": f"Teste automático - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                }
            )
            if response.status_code == 200:
                resultado = response.json()
                print(f"   ✓ Estoque anterior: {resultado['estoque_anterior']}")
                print(f"   ✓ Estoque novo: {resultado['estoque_novo']}")
                return resultado
            else:
                print(f"   ✗ Erro {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"   ✗ Erro: {e}")
            return None

async def test_saida_estoque(codigo="PH-510", quantidade=5):
    """Testa saída de estoque"""
    print(f"\n4. Testando saída de {quantidade} unidades...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/api/v2/estoque/entrada",
                json={
                    "codigo": codigo,
                    "quantidade": -quantidade,  # Negativo para saída
                    "observacao": f"Saída teste - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                }
            )
            if response.status_code == 200:
                resultado = response.json()
                print(f"   ✓ Estoque anterior: {resultado['estoque_anterior']}")
                print(f"   ✓ Estoque novo: {resultado['estoque_novo']}")
                return resultado
            else:
                data = response.json()
                print(f"   ✗ Erro {response.status_code}: {data.get('detail', response.text)}")
                return None
        except Exception as e:
            print(f"   ✗ Erro: {e}")
            return None

async def test_saida_excessiva(codigo="PH-510"):
    """Testa tentativa de saída maior que o estoque"""
    print(f"\n5. Testando saída excessiva...")
    
    # Primeiro busca o produto para saber o estoque
    produto = await test_buscar_produto(codigo)
    if not produto:
        print("   ✗ Não foi possível buscar o produto")
        return
    
    quantidade_excessiva = int(produto['estoque']) + 100
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/api/v2/estoque/entrada",
                json={
                    "codigo": codigo,
                    "quantidade": -quantidade_excessiva,
                    "observacao": "Teste de saída excessiva"
                }
            )
            if response.status_code == 400:
                data = response.json()
                print(f"   ✓ Erro esperado: {data['detail']}")
                return True
            else:
                print(f"   ✗ Deveria retornar erro 400, mas retornou {response.status_code}")
                return False
        except Exception as e:
            print(f"   ✗ Erro inesperado: {e}")
            return False

async def main():
    """Executa todos os testes"""
    print("=== TESTE DO SISTEMA DE ESTOQUE ===")
    print(f"API URL: {API_URL}")
    print(f"Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 35)
    
    # Verifica se a API está rodando
    if not await test_health():
        print("\n✗ API não está respondendo. Verifique se o servidor está rodando.")
        return
    
    # Testa busca de produto
    produto = await test_buscar_produto()
    if not produto:
        print("\n✗ Não foi possível buscar o produto. Verifique o código e o token da API Tiny.")
        return
    
    # Testa entrada de estoque
    await test_entrada_estoque()
    
    # Testa saída de estoque
    await test_saida_estoque()
    
    # Testa validação de estoque negativo
    await test_saida_excessiva()
    
    print("\n=== TESTES CONCLUÍDOS ===")

if __name__ == "__main__":
    asyncio.run(main())